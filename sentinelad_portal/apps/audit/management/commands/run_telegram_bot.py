import time
import requests
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.audit.models import AuditLog
from apps.employees.models import Department, Employee
from apps.authentication.ad_provisioning import (
    create_ad_ou, create_ad_user, disable_ad_user, 
    enable_ad_user, delete_ad_user, reset_ad_password
)

logger = logging.getLogger('sentinelad.app')

class Command(BaseCommand):
    help = 'Chạy tiến trình Telegram Bot ngầm để nhận lệnh điều khiển'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        authorized_chat_id = str(getattr(settings, 'TELEGRAM_CHAT_ID', ''))

        if not token or not authorized_chat_id:
            self.stdout.write(self.style.ERROR("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in settings."))
            return

        self.stdout.write(self.style.SUCCESS(f"Started listening to Telegram commands from CHAT_ID: {authorized_chat_id}"))

        url = f"https://api.telegram.org/bot{token}/getUpdates"
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"

        offset = None

        while True:
            try:
                params = {'timeout': 30, 'offset': offset}
                response = requests.get(url, params=params, timeout=35)
                
                if not response.ok:
                    time.sleep(5)
                    continue
                
                data = response.json()
                for update in data.get('result', []):
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        msg = update['message']
                        chat_id = str(msg.get('chat', {}).get('id'))
                        text = msg.get('text', '').strip()

                        # Authorization check
                        if chat_id != authorized_chat_id:
                            self.stdout.write(self.style.WARNING(f"Blocked unauthorized attempt from chat_id {chat_id}: {text}"))
                            continue

                        # Command Processing
                        if text:
                            self.process_command(text, chat_id, send_url)
                            
            except requests.exceptions.RequestException:
                # Tránh in log quá nhiều khi mất kết nối mạng
                time.sleep(5)
            except Exception as e:
                logger.error(f"Telegram Bot error: {e}")
                time.sleep(5)

    def process_command(self, text, chat_id, send_url):
        parts = text.split()
        cmd = parts[0].lower()
        reply = ""

        if cmd == '/help' or cmd == '/start':
            reply = (
                "🤖 <b>SentinelAD Control Center</b>\n\n"
                "Danh sách các lệnh hỗ trợ:\n"
                "🔹 /help - Xem hướng dẫn này\n"
                "🔹 /status - Kiểm tra trạng thái hệ thống\n"
                "🔹 /logs - Xem 5 sự kiện bảo mật gần nhất\n"
                "🔹 /add_ou &lt;name&gt; - Thêm phòng ban mới\n"
                "🔹 /add_user &lt;email&gt; &lt;fullname&gt; [ou] - Thêm nhân viên\n"
                "🔹 /lock_user &lt;username&gt; - Khóa tài khoản AD\n"
                "🔹 /unlock_user &lt;username&gt; - Mở khóa tài khoản AD\n"
                "🔹 /reset_password &lt;username&gt; &lt;new_pass&gt; - Đổi mật khẩu\n"
                "🔹 /delete_user &lt;username&gt; - Xóa nhân viên\n"
                "🔹 /list_users [ou] - Xem danh sách nhân viên"
            )
        elif cmd == '/status':
            log_count = AuditLog.objects.count()
            reply = (
                "🟢 <b>Trạng thái Hệ thống: BÌNH THƯỜNG</b>\n"
                "Tất cả các dịch vụ đang hoạt động tốt.\n\n"
                f"📊 <b>Tổng số bản ghi Audit:</b> {log_count}"
            )
        elif cmd == '/logs':
            recent_logs = AuditLog.objects.order_by('-timestamp')[:5]
            if recent_logs:
                reply = "📝 <b>5 Sự kiện Bảo mật gần nhất:</b>\n"
                for log in recent_logs:
                    time_str = log.timestamp.strftime("%H:%M %d/%m")
                    emoji = "🚨" if log.action == "LOGIN_FAILURE" else "🛑" if log.action == "DELETE" else "✅"
                    reply += f"{emoji} [{time_str}] {log.username} - {log.action}\n"
            else:
                reply = "📝 Chưa có sự kiện bảo mật nào."
        elif cmd == '/lock_user':
            if len(parts) > 1:
                username = parts[1]
                ad_ok, ad_msg = disable_ad_user(username)
                if ad_ok:
                    # Update DB as well
                    Employee.objects.filter(employee_id=username).update(status='inactive')
                    reply = f"🔒 Đã <b>khóa thành công</b> tài khoản <code>{username}</code> trên Active Directory."
                else:
                    reply = f"⚠️ Lỗi khi khóa tài khoản: {ad_msg}"
            else:
                reply = "⚠️ Lỗi cú pháp. Vui lòng sử dụng:\n<code>/lock_user &lt;username&gt;</code>"

        elif cmd == '/unlock_user':
            if len(parts) > 1:
                username = parts[1]
                ad_ok, ad_msg = enable_ad_user(username)
                if ad_ok:
                    Employee.objects.filter(employee_id=username).update(status='active')
                    reply = f"🔓 Đã <b>mở khóa thành công</b> tài khoản <code>{username}</code> trên Active Directory."
                else:
                    reply = f"⚠️ Lỗi khi mở khóa: {ad_msg}"
            else:
                reply = "⚠️ Lỗi cú pháp. Vui lòng sử dụng:\n<code>/unlock_user &lt;username&gt;</code>"

        elif cmd == '/reset_password':
            if len(parts) >= 3:
                username = parts[1]
                new_pass = ' '.join(parts[2:])
                ad_ok, ad_msg = reset_ad_password(username, new_pass)
                if ad_ok:
                    reply = f"🔑 Đã <b>đặt lại mật khẩu</b> cho tài khoản <code>{username}</code> thành công."
                else:
                    reply = f"⚠️ Lỗi khi đổi mật khẩu: {ad_msg}"
            else:
                reply = "⚠️ Lỗi cú pháp. Vui lòng sử dụng:\n<code>/reset_password &lt;username&gt; &lt;mật_khẩu_mới&gt;</code>"

        elif cmd == '/delete_user':
            if len(parts) > 1:
                username = parts[1]
                ad_ok, ad_msg = delete_ad_user(username)
                if ad_ok:
                    Employee.objects.filter(employee_id=username).delete()
                    reply = f"🗑️ Đã <b>xóa vĩnh viễn</b> tài khoản <code>{username}</code> khỏi hệ thống và AD."
                else:
                    reply = f"⚠️ Lỗi khi xóa tài khoản: {ad_msg}"
            else:
                reply = "⚠️ Lỗi cú pháp. Vui lòng sử dụng:\n<code>/delete_user &lt;username&gt;</code>"

        elif cmd == '/list_users':
            dept_name = ' '.join(parts[1:]) if len(parts) > 1 else None
            
            if dept_name:
                users = Employee.objects.filter(department__name__icontains=dept_name)
                header = f"👥 <b>Danh sách nhân viên phòng {dept_name}:</b>\n\n"
            else:
                users = Employee.objects.all()[:20]
                header = f"👥 <b>Danh sách nhân viên (20 người đầu tiên):</b>\n\n"
                
            if users.exists():
                reply = header
                for u in users:
                    icon = "🟢" if u.status == 'active' else "🔴"
                    dept = u.department.name if u.department else "N/A"
                    reply += f"{icon} <code>{u.employee_id}</code> - {u.full_name} ({dept})\n"
            else:
                reply = "📝 Không tìm thấy nhân viên nào."

        elif cmd == '/add_ou':
            if len(parts) > 1:
                name = ' '.join(parts[1:])
                # Create in Database
                dept, created = Department.objects.get_or_create(name=name)
                # Sync to AD
                ad_ok, ad_msg = create_ad_ou(name)
                
                if ad_ok:
                    reply = f"✅ Đã tạo phòng ban <b>{name}</b> thành công trên Web & Active Directory."
                else:
                    reply = f"⚠️ Đã tạo phòng ban <b>{name}</b> trên Web, nhưng AD báo lỗi: {ad_msg}"
            else:
                reply = "⚠️ Lỗi cú pháp. Vui lòng sử dụng:\n<code>/add_ou &lt;Tên_Phòng_Ban&gt;</code>"

        elif cmd == '/add_user':
            if len(parts) >= 3:
                email = parts[1]
                rest = ' '.join(parts[2:])
                
                dept_name = "Company"
                full_name = rest
                
                # Simple parsing logic to extract OU if it matches an existing department at the end of the string
                all_depts = Department.objects.values_list('name', flat=True)
                for d in all_depts:
                    if rest.endswith(d):
                        dept_name = d
                        full_name = rest[:-len(d)].strip()
                        break
                
                if not full_name:
                    full_name = rest
                
                username = email.split('@')[0] if '@' in email else email
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Save to Database
                dept = Department.objects.filter(name=dept_name).first()
                emp = Employee.objects.create(
                    employee_id=username,
                    full_name=full_name,
                    email=email,
                    department=dept,
                    position='Staff',
                    status='active'
                )
                
                # Sync to AD
                ad_ok, ad_msg = create_ad_user(username, first_name, last_name, full_name, email, dept_name)
                
                if ad_ok:
                    reply = f"✅ Đã tạo user <b>{full_name}</b> ({email}) thuộc OU <b>{dept_name}</b> thành công trên Web & AD."
                else:
                    reply = f"⚠️ Đã tạo user <b>{full_name}</b> trên Web, nhưng AD báo lỗi: {ad_msg}"
            else:
                reply = "⚠️ Lỗi cú pháp. Vui lòng sử dụng:\n<code>/add_user &lt;email&gt; &lt;họ_tên_đầy_đủ&gt; [Tên_OU_nếu_có]</code>\nVD: /add_user john@khai.local John Doe IT"
                
        else:
            reply = "❓ Lệnh không hợp lệ. Gõ /help để xem danh sách lệnh."

        # Gửi trả lời
        payload = {
            "chat_id": chat_id,
            "text": reply,
            "parse_mode": "HTML"
        }
        try:
            requests.post(send_url, json=payload, timeout=5)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to reply: {e}"))
