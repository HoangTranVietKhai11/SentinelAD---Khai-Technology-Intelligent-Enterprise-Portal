"""
SentinelAD Authentication Backend
Supports LDAP (Active Directory khai.local) with Mock mode for development.
Login formats accepted: khai\\username, username@khai.local, or plain username
"""
import logging
import json
import datetime
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger('sentinelad.audit')

# Mock AD users for development (when LDAP_MOCK_MODE=True)
MOCK_AD_USERS = {
    'khai.it': {
        'password': 'Admin@123456',
        'display_name': 'Khai IT Admin',
        'email': 'khai.it@khai.local',
        'groups': ['IT_Admin', 'Department_User'],
        'department': 'IT',
        'title': 'IT Administrator',
    },
    'an.hr': {
        'password': 'Admin@123456',
        'display_name': 'An HR Manager',
        'email': 'an.hr@khai.local',
        'groups': ['HR_Manager', 'Department_User'],
        'department': 'HR',
        'title': 'HR Manager',
    },
    'minh.finance': {
        'password': 'Admin@123456',
        'display_name': 'Minh Finance Manager',
        'email': 'minh.finance@khai.local',
        'groups': ['Finance_Manager', 'Department_User'],
        'department': 'Finance',
        'title': 'Finance Manager',
    },
    'hung.sales': {
        'password': 'Admin@123456',
        'display_name': 'Hung Sales Manager',
        'email': 'hung.sales@khai.local',
        'groups': ['Sales_Manager', 'Department_User'],
        'department': 'Sales',
        'title': 'Sales Manager',
    },
}

ROLE_MAP = {
    'Domain Admins': 'administrator',
    'Administrators': 'administrator',
    'IT_Admin': 'administrator',
    'Helpdesk': 'helpdesk',
    'HR_Manager': 'hr_manager',
    'Finance_Manager': 'finance_manager',
    'Sales_Manager': 'sales_manager',
    'Department_User': 'employee',
}


def _parse_username(raw_username):
    """Parse khai\\user, user@khai.local, or plain user → plain username."""
    username = raw_username.strip()
    if '\\' in username:
        username = username.split('\\', 1)[1]
    elif '@' in username:
        username = username.split('@', 1)[0]
    return username.lower()


def _get_role(groups):
    """Determine highest-privilege role from AD groups."""
    priority = ['Domain Admins', 'Administrators', 'IT_Admin', 'Helpdesk', 'HR_Manager', 'Finance_Manager', 'Sales_Manager', 'Department_User']
    for g in priority:
        if g in groups:
            return ROLE_MAP[g]
    return 'employee'


def _audit_log(username, action, success, ip='unknown', extra=None):
    """Write structured audit log entry for Loki/Grafana ingestion."""
    record = {
        "user": username,
        "action": action,
        "success": success,
        "source_ip": ip,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if extra:
        record.update(extra)
    logger.info(json.dumps(record))


class SentinelADBackend(ModelBackend):
    """
    Custom authentication backend for Active Directory khai.local.
    - LDAP_MOCK_MODE=True: Uses local mock users (development)
    - LDAP_MOCK_MODE=False: Connects to DC-01 (192.168.101.10) via LDAP3
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        raw_username = username
        username = _parse_username(username)
        source_ip = request.META.get('REMOTE_ADDR', 'unknown') if request else 'unknown'

        if getattr(settings, 'LDAP_MOCK_MODE', True):
            return self._mock_authenticate(username, password, source_ip, raw_username)
        else:
            return self._ldap_authenticate(username, password, source_ip, raw_username)

    def _mock_authenticate(self, username, password, source_ip, raw_username):
        """Authenticate against mock user database (development mode)."""
        if username not in MOCK_AD_USERS:
            _audit_log(username, 'LOGIN_FAILURE', False, source_ip,
                       {'reason': 'User not found in mock AD', 'raw_username': raw_username})
            return None

        mock_user = MOCK_AD_USERS[username]
        if mock_user['password'] != password:
            _audit_log(username, 'LOGIN_FAILURE', False, source_ip,
                       {'reason': 'Invalid password'})
            return None

        user = self._get_or_create_user(username, mock_user)
        _audit_log(username, 'LOGIN_SUCCESS', True, source_ip,
                   {'role': user.profile_role if hasattr(user, 'profile_role') else 'unknown',
                    'mode': 'mock'})
        return user

    def _ldap_authenticate(self, username, password, source_ip, raw_username):
        """
        Authenticate against Active Directory DC-01 via LDAP3.
        Uses SIMPLE bind with UPN (user@khai.local) to avoid NTLM/MD4 hash
        issues with Python 3.13 + OpenSSL 3.x which disables MD4 by default.
        """
        try:
            from ldap3 import Server, Connection, ALL, SIMPLE, ANONYMOUS
            ad = settings.AD_CONFIG

            # Step 1: Bind with admin account (SIMPLE bind, no NTLM needed)
            server = Server(ad['SERVER'], port=ad['PORT'], get_info=ALL)
            admin_upn = f"Administrator@{ad['DOMAIN']}"
            admin_conn = Connection(
                server,
                user=admin_upn,
                password=ad['BIND_PASSWORD'],
                authentication=SIMPLE,
                auto_bind=True
            )

            # Step 2: Search for the user's DN by sAMAccountName
            search_filter = f"(sAMAccountName={username})"
            admin_conn.search(
                search_base=ad['BASE_DN'],
                search_filter=search_filter,
                attributes=['distinguishedName', 'displayName', 'mail',
                            'memberOf', 'department', 'title', 'userAccountControl']
            )

            if not admin_conn.entries:
                _audit_log(username, 'LOGIN_FAILURE', False, source_ip,
                           {'reason': 'User not found in AD', 'mode': 'ldap'})
                admin_conn.unbind()
                return None

            entry = admin_conn.entries[0]
            user_dn = str(entry.distinguishedName)

            # Check if account is enabled (userAccountControl bit 2 = ACCOUNTDISABLE)
            uac = int(str(entry.userAccountControl)) if hasattr(entry, 'userAccountControl') else 0
            if uac & 2:
                _audit_log(username, 'LOGIN_FAILURE', False, source_ip,
                           {'reason': 'Account disabled in AD', 'mode': 'ldap'})
                admin_conn.unbind()
                return None

            # Step 3: Bind as the user to verify password (SIMPLE bind with DN)
            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=SIMPLE,
                auto_bind=False
            )
            if not user_conn.bind():
                _audit_log(username, 'LOGIN_FAILURE', False, source_ip,
                           {'reason': 'Invalid password', 'mode': 'ldap'})
                admin_conn.unbind()
                return None

            # Step 4: Extract group membership from admin search result
            member_of = list(entry.memberOf) if hasattr(entry, 'memberOf') else []
            groups = [cn.split(',')[0].replace('CN=', '') for cn in member_of]

            user_info = {
                'display_name': str(entry.displayName) if hasattr(entry, 'displayName') else username,
                'email': str(entry.mail) if hasattr(entry, 'mail') else f"{username}@{ad['DOMAIN']}",
                'groups': groups,
                'department': str(entry.department) if hasattr(entry, 'department') else '',
                'title': str(entry.title) if hasattr(entry, 'title') else '',
            }

            user = self._get_or_create_user(username, user_info)
            _audit_log(username, 'LOGIN_SUCCESS', True, source_ip,
                       {'groups': groups, 'role': user._ad_role, 'mode': 'ldap'})
            user_conn.unbind()
            admin_conn.unbind()
            return user

        except Exception as e:
            _audit_log(username, 'LOGIN_FAILURE', False, source_ip,
                       {'reason': str(e), 'mode': 'ldap'})
            return None

    def _get_or_create_user(self, username, user_info):
        """Create or update Django User from AD data, assign role in session."""
        groups = user_info.get('groups', [])
        role = _get_role(groups)
        display_name = user_info.get('display_name', username)
        name_parts = display_name.split(' ', 1)

        user, created = User.objects.get_or_create(username=username)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = user_info.get('email', f"{username}@khai.local")
        user.is_active = True
        user.is_staff = role == 'administrator'
        user.is_superuser = role == 'administrator'

        # Store role and extra info on user object temporarily
        user._ad_role = role
        user._ad_groups = groups
        user._ad_department = user_info.get('department', '')
        user.save()

        # Store in profile if exists
        try:
            profile = user.userprofile
            profile.role = role
            profile.department = user_info.get('department', '')
            profile.title = user_info.get('title', '')
            profile.ad_groups = ','.join(groups)
            profile.save()
        except Exception:
            pass

        return user
