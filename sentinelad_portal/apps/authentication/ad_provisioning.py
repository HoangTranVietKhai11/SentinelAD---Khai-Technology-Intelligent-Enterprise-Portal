import logging
from django.conf import settings
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SUBTREE

logger = logging.getLogger('sentinelad.audit')

def _get_admin_connection():
    """Return an active connection to AD using Administrator credentials."""
    if getattr(settings, 'LDAP_MOCK_MODE', True):
        return None
        
    ad = settings.AD_CONFIG
    server = Server(ad['SERVER'], port=ad['PORT'], get_info=ALL)
    admin_upn = f"Administrator@{ad['DOMAIN']}"
    conn = Connection(
        server,
        user=admin_upn,
        password=ad['BIND_PASSWORD'],
        auto_bind=True
    )
    return conn

def create_ad_ou(department_name):
    """Create an Organizational Unit under BASE_DN."""
    conn = _get_admin_connection()
    if not conn:
        logger.info(f"Mock Mode: Skipped creating AD OU for {department_name}")
        return True, "Mock Mode: Skipped AD Sync"
        
    ad = settings.AD_CONFIG
    ou_dn = f"OU={department_name},{ad['BASE_DN']}"
    
    try:
        # Check if OU already exists
        conn.search(ad['BASE_DN'], f"(ou={department_name})", search_scope=SUBTREE)
        if conn.entries:
            return True, f"OU {department_name} already exists in AD."

        attributes = {
            'objectClass': ['top', 'organizationalUnit'],
            'description': f'Department {department_name} created via Portal'
        }
        success = conn.add(ou_dn, attributes=attributes)
        
        if success:
            logger.info(f"AD Provisioning: Created OU {department_name}")
            return True, "Successfully created AD OU."
        else:
            err = conn.result.get('description', 'Unknown error')
            logger.error(f"AD Provisioning Error creating OU {department_name}: {err}")
            return False, f"AD Error: {err}"
    except Exception as e:
        logger.error(f"AD Provisioning Exception (OU {department_name}): {e}")
        return False, str(e)
    finally:
        conn.unbind()

def create_ad_user(username, first_name, last_name, display_name, email, dept_name):
    """Create a User under the specified Department OU."""
    conn = _get_admin_connection()
    if not conn:
        logger.info(f"Mock Mode: Skipped creating AD user {username}")
        return True, "Mock Mode: Skipped AD Sync"
        
    ad = settings.AD_CONFIG
    user_dn = f"CN={display_name},OU={dept_name},{ad['BASE_DN']}"
    
    try:
        # Check if user already exists
        conn.search(ad['BASE_DN'], f"(sAMAccountName={username})", search_scope=SUBTREE)
        if conn.entries:
            return True, f"User {username} already exists in AD."

        attributes = {
            'sAMAccountName': username,
            'userPrincipalName': f"{username}@{ad['DOMAIN']}",
            'givenName': first_name,
            'sn': last_name,
            'displayName': display_name,
            'mail': email,
            'department': dept_name,
            # AD requirement: user must have a password before being enabled.
            # Without LDAPS, we cannot set password, so we create it as Disabled (514)
            'userAccountControl': 514, 
        }
        success = conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], attributes)
        
        if success:
            logger.info(f"AD Provisioning: Created User {username} in {dept_name}")
            return True, "Successfully created AD User (Disabled - Password must be reset by admin)."
        else:
            err = conn.result.get('description', 'Unknown error')
            logger.error(f"AD Provisioning Error creating user {username}: {err}")
            return False, f"AD Error: {err}"
    except Exception as e:
        logger.error(f"AD Provisioning Exception (User {username}): {e}")
        return False, str(e)
    finally:
        conn.unbind()

def disable_ad_user(username):
    """Disable a User in AD by setting userAccountControl to 514 (Disabled)."""
    conn = _get_admin_connection()
    if not conn:
        logger.info(f"Mock Mode: Skipped disabling AD user {username}")
        return True, "Mock Mode: Skipped AD Sync"
        
    ad = settings.AD_CONFIG
    
    try:
        # Find user's DN
        conn.search(ad['BASE_DN'], f"(sAMAccountName={username})", search_scope=SUBTREE, attributes=['userAccountControl'])
        if not conn.entries:
            return False, f"User {username} not found in AD."
            
        entry = conn.entries[0]
        user_dn = str(entry.distinguishedName)
        current_uac = int(str(entry.userAccountControl)) if hasattr(entry, 'userAccountControl') else 512
        
        # Bitwise OR with 2 to set ACCOUNTDISABLE
        new_uac = current_uac | 2
        
        success = conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [str(new_uac)])]})
        
        if success:
            logger.info(f"AD Provisioning: Disabled User {username}")
            return True, "Successfully disabled AD User."
        else:
            err = conn.result.get('description', 'Unknown error')
            logger.error(f"AD Provisioning Error disabling user {username}: {err}")
            return False, f"AD Error: {err}"
    except Exception as e:
        logger.error(f"AD Provisioning Exception (Disable {username}): {e}")
        return False, str(e)
    finally:
        conn.unbind()

def enable_ad_user(username):
    """Enable a User in AD by clearing the ACCOUNTDISABLE flag."""
    conn = _get_admin_connection()
    if not conn:
        logger.info(f"Mock Mode: Skipped enabling AD user {username}")
        return True, "Mock Mode: Skipped AD Sync"
        
    ad = settings.AD_CONFIG
    
    try:
        conn.search(ad['BASE_DN'], f"(sAMAccountName={username})", search_scope=SUBTREE, attributes=['userAccountControl'])
        if not conn.entries:
            return False, f"User {username} not found in AD."
            
        entry = conn.entries[0]
        user_dn = str(entry.distinguishedName)
        current_uac = int(str(entry.userAccountControl)) if hasattr(entry, 'userAccountControl') else 514
        
        # Bitwise AND with ~2 to clear ACCOUNTDISABLE
        new_uac = current_uac & ~2
        
        success = conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [str(new_uac)])]})
        
        if success:
            logger.info(f"AD Provisioning: Enabled User {username}")
            return True, "Successfully enabled AD User."
        else:
            err = conn.result.get('description', 'Unknown error')
            logger.error(f"AD Error enabling user {username}: {err}")
            return False, f"AD Error: {err}"
    except Exception as e:
        logger.error(f"AD Exception (Enable {username}): {e}")
        return False, str(e)
    finally:
        conn.unbind()

def delete_ad_user(username):
    """Delete a User from AD."""
    conn = _get_admin_connection()
    if not conn:
        logger.info(f"Mock Mode: Skipped deleting AD user {username}")
        return True, "Mock Mode: Skipped AD Sync"
        
    ad = settings.AD_CONFIG
    
    try:
        conn.search(ad['BASE_DN'], f"(sAMAccountName={username})", search_scope=SUBTREE)
        if not conn.entries:
            return False, f"User {username} not found in AD."
            
        entry = conn.entries[0]
        user_dn = str(entry.distinguishedName)
        
        success = conn.delete(user_dn)
        
        if success:
            logger.info(f"AD Provisioning: Deleted User {username}")
            return True, "Successfully deleted AD User."
        else:
            err = conn.result.get('description', 'Unknown error')
            logger.error(f"AD Error deleting user {username}: {err}")
            return False, f"AD Error: {err}"
    except Exception as e:
        logger.error(f"AD Exception (Delete {username}): {e}")
        return False, str(e)
    finally:
        conn.unbind()

def reset_ad_password(username, new_password):
    """Reset a User's password in AD. Requires LDAPS."""
    conn = _get_admin_connection()
    if not conn:
        logger.info(f"Mock Mode: Skipped reset password for {username}")
        return True, "Mock Mode: Skipped AD Sync"
        
    ad = settings.AD_CONFIG
    
    try:
        conn.search(ad['BASE_DN'], f"(sAMAccountName={username})", search_scope=SUBTREE)
        if not conn.entries:
            return False, f"User {username} not found in AD."
            
        entry = conn.entries[0]
        user_dn = str(entry.distinguishedName)
        
        # Using ldap3 modify_password extended operation
        success = conn.extend.microsoft.modify_password(user_dn, new_password)
        
        if success:
            logger.info(f"AD Provisioning: Reset password for {username}")
            return True, "Successfully reset password."
        else:
            err = conn.result.get('description', 'Unknown error')
            logger.error(f"AD Error resetting password for {username}: {err}")
            return False, f"AD Error: {err} (Note: LDAPS is usually required to change passwords)"
    except Exception as e:
        logger.error(f"AD Exception (Reset Password {username}): {e}")
        return False, f"{e}. Ensure LDAPS (port 636) is configured."
    finally:
        conn.unbind()

