"""Audit Middleware - Automatically logs all authentication and navigation events."""
import json
import logging
import datetime
from .models import AuditLog
from .telegram import send_telegram_alert

logger = logging.getLogger('sentinelad.audit')


def log_action(user, action, resource_type='', resource_id='', resource_name='',
               description='', source_ip='', user_agent=''):
    """Helper function to create an AuditLog entry and write to log file."""
    username = user.username if user and user.is_authenticated else 'anonymous'

    # DB record
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        resource_name=resource_name,
        description=description,
        source_ip=source_ip or None,
        user_agent=user_agent[:300] if user_agent else '',
    )

    # JSON log for Loki
    record = {
        "user": username,
        "action": action,
        "resource_type": resource_type,
        "resource_id": str(resource_id),
        "resource_name": resource_name,
        "description": description,
        "source_ip": source_ip,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    logger.info(json.dumps(record, ensure_ascii=False))

    # Telegram Real-time Alert for dangerous actions
    dangerous_actions = ['LOGIN_FAILURE', 'DELETE', 'UNAUTHORIZED_ACCESS']
    if action in dangerous_actions:
        emoji = "🚨" if action == 'LOGIN_FAILURE' else "🛑" if action == 'DELETE' else "⚠️"
        msg = (
            f"{emoji} <b>Cảnh báo Bảo mật SentinelAD</b>\n"
            f"<b>Hành động:</b> {action}\n"
            f"<b>Người dùng:</b> {username}\n"
            f"<b>Tài nguyên:</b> {resource_type} ({resource_name})\n"
            f"<b>Chi tiết:</b> {description}\n"
            f"<b>IP Nguồn:</b> {source_ip}"
        )
        send_telegram_alert(msg)


class AuditMiddleware:
    """Middleware for capturing authentication events from Django signals."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
