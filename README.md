# SentinelAD - Khai Technology Enterprise Portal & Infrastructure Monitoring

Dự án xây dựng **Cổng thông tin nội bộ (Intranet Portal)** cho công ty công nghệ Khai Technology kết hợp **Quản trị định danh tập trung qua Active Directory (Windows Server 2022)** và **Hệ thống giám sát an toàn hạ tầng (Prometheus, Grafana, Loki, AI Log Analyzer, Telegram Alerts)**.

---

## 📸 Hình ảnh minh chứng hoàn thành (Demo Screenshots)

### 1. Trang chủ Cổng thông tin (Dashboard)
Trang tổng quan với banner chào mừng nhân viên, lịch họp sắp tới trong ngày, feed tin tức công ty, danh sách nhân sự mới và biểu đồ phân bổ tài sản.

![Dashboard](docs/screenshots/dashboard.png)

---

### 2. Quản lý Lịch họp & Điểm danh RSVP (`/meetings/`)
Hỗ trợ tạo lịch họp theo phòng ban, lọc theo ngày/tuần, đặt địa điểm (Google Meet, Zoom, Phòng họp) và cho phép nhân viên bấm xác nhận tham dự (RSVP).

![Lịch họp](docs/screenshots/meetings.png)

---

### 3. Thông báo lương bảo mật (`/payroll/`)
Phân quyền bảo mật: nhân viên chỉ xem được phiếu lương của chính mình, chỉ Admin/HR mới có quyền tạo và quản lý bảng lương toàn công ty.

![Thông báo lương](docs/screenshots/payroll.png)

---

### 4. Bảng tin nội bộ & Chào đón nhân sự mới (`/announcements/`)
Đăng tải tin tức công ty, chính sách, sự kiện team building và bài viết chào mừng nhân viên mới gia nhập với tính năng ghim bài quan trọng.

![Bảng tin nội bộ](docs/screenshots/announcements.png)

---

### 5. Danh mục Nhân viên đồng bộ trực tiếp từ Active Directory (`/employees/`)
Dữ liệu nhân sự được đồng bộ 2 chiều trực tiếp từ máy chủ Domain Controller (`DC-01: 192.168.101.10`) qua giao thức LDAP. Có nút bấm "Đồng bộ từ DC-01" 1-click.

![Quản lý nhân viên](docs/screenshots/employees.png)

---

## 🏗️ Sơ đồ kiến trúc & Luồng hoạt động

```
[ Điện thoại / Laptop nhân viên ]
       │
       ├── (Trong cty): Wi-Fi / LAN nội bộ (DNS -> 192.168.101.10)
       └── (Từ xa):     Remote Access VPN (IKEv2 / IPsec)
       │
       ▼
[ Web Server Django - http://intranet.khai.local ] (192.168.101.7)
       │
       ├── 1. Xác thực người dùng (Live LDAP Port 389) ──────┐
       ├── 2. Tự động tạo OU & User trên AD khi thêm mới ────┤
       ├── 3. Giám sát & Quét log sự kiện (Event Logs) ──────┤
       │                                                     ▼
       │                                      [ Windows Server 2022 DC-01 ]
       │                                             (192.168.101.10)
       │                                      - Active Directory (khai.local)
       │                                      - DNS Server & DHCP Server
       │                                      - Routing & Remote Access (VPN)
       │
       ├── 4. Phân tích an ninh (AI Analyzer - Llama 3.1 qua Groq API)
       ├── 5. Cảnh báo xâm nhập thời gian thực qua Telegram Bot
       └── 6. Đẩy Metrics & Logs vào Docker Stack (Prometheus + Loki + Grafana)
```

---

## ⚙️ Các tính năng đã hoàn thiện

### 1. Cổng thông tin nội bộ (Khai Technology Portal)
* **Trang chủ (Dashboard):** Giao diện Dark-mode hiện đại, hiển thị lời chào theo tài khoản, đếm số cuộc họp hôm nay, thông báo lương chưa xem, feed tin tức.
* **Lịch họp (Meetings):** Tạo lịch họp Standup, Họp Team, Review, All Hands; hỗ trợ RSVP cho người tham gia.
* **Thông báo (Announcements):** Phân loại danh mục (Nhân viên mới, Cập nhật công ty, Sự kiện, Chính sách); hỗ trợ ghim bài lên đầu.
* **Bảng lương (Payroll):** Xem chi tiết phiếu lương cá nhân, tính toán tự động lương thực lãnh, bảo mật phân quyền nghiêm ngặt.
* **Yêu cầu hỗ trợ (IT Helpdesk Tickets):** Gửi yêu cầu hỗ trợ kỹ thuật nội bộ, phân loại theo mức độ ưu tiên.
* **Quản lý thiết bị (IT Assets):** Quản lý máy chủ, laptop, switch, firewall, theo dõi thời hạn bảo hành.

### 2. Tích hợp Active Directory (DC-01 `khai.local`)
* **Xác thực Live LDAP:** Đăng nhập trực tiếp bằng tài khoản Active Directory thật (hỗ trợ định dạng `username`, `khai\username`, `username@khai.local`).
* **Đồng bộ 2 chiều (Two-Way Sync):** Thao tác thêm/sửa/xóa nhân viên trên Web sẽ tự động gọi LDAP tạo/vô hiệu hóa User và OU tương ứng trên Windows Server 2022.
* **Lệnh đồng bộ 1-click:** Lệnh `python manage.py sync_ad` hoặc bấm nút trên web để kéo toàn bộ User/OU từ DC-01 về web trong vài giây.
* **Phân quyền vai trò (RBAC Mapping):**
  * `Domain Admins` / `IT_Admin` → Quản trị viên (Toàn quyền).
  * `HR_Manager` → Trưởng phòng nhân sự (Quản lý nhân viên, tạo phiếu lương).
  * `Finance_Manager` → Quản lý tài chính.
  * `Sales_Manager` → Quản lý kinh doanh.
  * `Department_User` → Nhân viên tiêu chuẩn.

### 3. Giám sát an toàn hạ tầng & Cảnh báo
* **Audit Logging:** Ghi nhận toàn bộ sự kiện đăng nhập thành công/thất bại, IP truy cập và lịch sử chỉnh sửa dữ liệu.
* **AI Security Analyzer:** Kết nối mô hình Llama 3.1 để đọc log đăng nhập, phát hiện hành vi dò quét mật khẩu (Event 4625 / Brute-force).
* **Telegram Bot Alerts:** Tự động gửi thông báo khẩn cấp về điện thoại của Quản trị viên khi phát hiện sự cố bảo mật.
* **Cụm Docker Observability:**
  * **Prometheus:** Thu thập metrics tài nguyên máy chủ qua Windows Exporter.
  * **Grafana:** Trực quan hóa dashboard giám sát CPU, RAM, Disk, Network.
  * **Loki & Promtail:** Thu thập và tìm kiếm log tập trung.
* **Remote Access VPN:** Cấu hình VPN Server (IKEv2 / IPsec) trên Windows Server 2022 để quản trị viên kết nối an toàn từ xa khi đi công tác.

---

## 🚀 Hướng dẫn cài đặt & Chạy dự án

### 1. Chuẩn bị môi trường
* Python 3.10 trở lên
* Docker & Docker Compose (nếu chạy cụm giám sát)
* Máy chủ Windows Server 2022 đã cấu hình AD DS (`khai.local`)

### 2. Cài đặt Web Portal
```bash
# 1. Clone repository
git clone https://github.com/HoangTranVietKhai11/SentinelAD---Khai-Technology-Intelligent-Enterprise-Portal.git
cd "SentinelAD---Khai-Technology-Intelligent-Enterprise-Portal"

# 2. Cài đặt thư viện
cd sentinelad_portal
pip install -r requirements.txt

# 3. Tạo file cấu hình môi trường .env (dựa theo .env.example)
cp ../.env.example .env

# 4. Chạy migration
python manage.py migrate

# 5. Đồng bộ dữ liệu thực tế từ Active Directory DC-01
python manage.py sync_ad

# 6. Khởi động Web Server
python manage.py runserver 0.0.0.0:80
```

### 3. Khởi động Cụm Giám sát (Monitoring)
```bash
cd ../monitoring
docker compose up -d
```

### 4. Địa chỉ truy cập
* **Web Portal nội bộ:** `http://intranet.khai.local` (hoặc `http://localhost`)
* **Grafana Monitoring:** `http://localhost:3000` (User: `admin` / Pass: `admin`)
* **Prometheus Metrics:** `http://localhost:9090`

---

## 👤 Thông tin tác giả

* **Họ và tên:** Hoàng Trần Việt Khải
* **Dự án:** SentinelAD - Khai Technology Enterprise Portal
* **Domain nội bộ:** `khai.local` · Máy chủ: `DC-01 (192.168.101.10)`
