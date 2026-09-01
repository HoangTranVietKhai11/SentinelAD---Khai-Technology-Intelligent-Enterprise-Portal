import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from apps.employees.models import Department, Employee
from apps.authentication.backends import _get_role, ROLE_MAP
from ldap3 import Server, Connection, ALL, SIMPLE, SUBTREE
from datetime import date


class Command(BaseCommand):
    help = 'Đồng bộ hóa 100% dữ liệu thực từ Active Directory DC-01 (192.168.101.10)'

    def handle(self, *args, **options):
        if sys.platform == 'win32':
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

        self.stdout.write(self.style.NOTICE("Connecting to DC-01 Active Directory (192.168.101.10)..."))
        ad = settings.AD_CONFIG

        try:
            server = Server(ad['SERVER'], port=ad['PORT'], get_info=ALL)
            admin_upn = f"Administrator@{ad['DOMAIN']}"
            conn = Connection(
                server,
                user=admin_upn,
                password=ad['BIND_PASSWORD'],
                authentication=SIMPLE,
                auto_bind=True
            )
            self.stdout.write(self.style.SUCCESS("[OK] Connected to Active Directory successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[FAIL] Could not connect to AD: {e}"))
            return

        # ── 1. Sync Organizational Units (Phòng ban) ─────────────────────────
        self.stdout.write(self.style.NOTICE("\n[1/3] Syncing Organizational Units (OUs)..."))
        conn.search(
            search_base=ad['BASE_DN'],
            search_filter='(objectClass=organizationalUnit)',
            search_scope=SUBTREE,
            attributes=['ou', 'description', 'distinguishedName']
        )

        dept_map = {}
        ignored_ous = ['Domain Controllers', 'Servers', 'Workstations']

        for entry in conn.entries:
            ou_name = str(entry.ou)
            if ou_name in ignored_ous or ou_name == 'Company':
                continue

            desc = str(entry.description) if hasattr(entry, 'description') and entry.description else f"Phòng {ou_name}"
            dept, created = Department.objects.get_or_create(
                name=ou_name,
                defaults={'description': desc}
            )
            dept_map[ou_name] = dept
            status_text = "Created" if created else "Updated"
            self.stdout.write(f"  - OU: {ou_name} ({status_text})")

        # ── 2. Sync Real Users from AD ───────────────────────────────────────
        self.stdout.write(self.style.NOTICE("\n[2/3] Syncing Real Users from Active Directory..."))
        conn.search(
            search_base=ad['BASE_DN'],
            search_filter='(&(objectClass=user)(!(objectClass=computer)))',
            search_scope=SUBTREE,
            attributes=[
                'sAMAccountName', 'displayName', 'givenName', 'sn',
                'mail', 'department', 'title', 'telephoneNumber',
                'memberOf', 'userAccountControl', 'distinguishedName'
            ]
        )

        synced_count = 0
        emp_code_idx = 1

        for entry in conn.entries:
            username = str(entry.sAMAccountName)

            # Skip internal system accounts
            if username.startswith(('$', 'krbtgt', 'Guest', 'DefaultAccount', 'WDAGUtilityAccount')):
                continue

            display_name = str(entry.displayName) if hasattr(entry, 'displayName') and entry.displayName else username
            first_name = str(entry.givenName) if hasattr(entry, 'givenName') and entry.givenName else ''
            last_name = str(entry.sn) if hasattr(entry, 'sn') and entry.sn else ''
            if not first_name and not last_name:
                parts = display_name.split(' ', 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''

            email = str(entry.mail) if hasattr(entry, 'mail') and entry.mail else f"{username}@{ad['DOMAIN']}"
            ad_dept_name = str(entry.department) if hasattr(entry, 'department') and entry.department else ''
            title = str(entry.title) if hasattr(entry, 'title') and entry.title else ''
            phone = str(entry.telephoneNumber) if hasattr(entry, 'telephoneNumber') and entry.telephoneNumber else ''

            # Extract groups
            member_of = list(entry.memberOf) if hasattr(entry, 'memberOf') else []
            groups = [cn.split(',')[0].replace('CN=', '') for cn in member_of]
            role = _get_role(groups)

            # Check account enabled
            uac = int(str(entry.userAccountControl)) if hasattr(entry, 'userAccountControl') and entry.userAccountControl else 512
            is_disabled = bool(uac & 2)

            # Match department from OU if not explicitly set
            dn_str = str(entry.distinguishedName)
            if not ad_dept_name:
                for ou_key in dept_map.keys():
                    if f"OU={ou_key}" in dn_str:
                        ad_dept_name = ou_key
                        break

            target_dept = dept_map.get(ad_dept_name)

            # 1. Update / Create Django User
            user, u_created = User.objects.get_or_create(username=username)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.is_active = not is_disabled
            user.is_staff = role == 'administrator' or username.lower() == 'administrator'
            user.is_superuser = role == 'administrator' or username.lower() == 'administrator'
            user.save()

            # 2. Update / Create UserProfile
            profile, p_created = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.department = ad_dept_name
            profile.title = title or role.replace('_', ' ').title()
            profile.ad_groups = ','.join(groups)
            profile.save()

            # 3. Update / Create Employee record (exclude raw Administrator from staff list)
            if username.lower() != 'administrator':
                emp_id = f"NV{emp_code_idx:03d}"
                emp_code_idx += 1

                emp, e_created = Employee.objects.get_or_create(
                    email=email,
                    defaults={'employee_id': emp_id, 'full_name': display_name}
                )
                emp.full_name = display_name
                emp.department = target_dept
                emp.position = title or profile.title
                emp.phone = phone or '0901234567'
                emp.status = 'inactive' if is_disabled else 'active'
                if not emp.hire_date:
                    emp.hire_date = date(2023, 1, 15)
                emp.save()

            synced_count += 1
            self.stdout.write(f"  - User: {username:<15} | {display_name:<20} | Role: {role:<15} | Dept: {ad_dept_name}")

        conn.unbind()

        # ── 3. Summary ───────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(f"\n[3/3] Done! Synchronized {synced_count} real AD accounts directly from DC-01."))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Server DC-01  : 192.168.101.10 (khai.local)")
        self.stdout.write(f"  AD Users      : {User.objects.count()}")
        self.stdout.write(f"  Departments   : {Department.objects.count()}")
        self.stdout.write(f"  Employees     : {Employee.objects.count()}")
        self.stdout.write("=" * 60)
