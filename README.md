# 🛡️ SentinelAD - Khai Technology Intelligent Enterprise Portal

> **Cổng Thông tin Nội bộ Doanh nghiệp, Quản trị Định danh Tập trung Active Directory & Giám sát An toàn Hạ tầng Tích hợp Trí tuệ Nhân tạo (AI).**

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Active Directory](https://img.shields.io/badge/Windows%20Server-2022%20AD%20DS-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Observability-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com/)
[![Loki](https://img.shields.io/badge/Grafana%20Loki-Log%20Aggregation-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)
[![Llama 3.1](https://img.shields.io/badge/AI%20Analyzer-Groq%20Llama%203.1-00ADD8?style=for-the-badge&logo=openai&logoColor=white)](https://groq.com)

---

## 📌 Giới thiệu tổng quan (Overview)

**SentinelAD (Khai Technology Enterprise Portal)** là giải pháp toàn diện kết hợp giữa **Cổng thông tin nội bộ (Intranet Portal)** cho doanh nghiệp công nghệ và **Hệ thống giám sát an toàn hạ tầng (Infrastructure Security Observability)**.

Hệ thống được thiết kế để tích hợp sâu với **Active Directory Domain Services (AD DS)** trên Windows Server 2022 (`khai.local`), cung cấp cơ chế xác thực tập trung, đồng bộ định danh hai chiều, phân quyền chặt chẽ theo vai trò (RBAC), quản trị nhân sự, tài sản, lịch họp, bảng lương bảo mật, cùng hệ thống cảnh báo xâm nhập thời gian thực và phân tích nhật ký bằng Trí tuệ Nhân tạo (AI).

---

## 🏛️ Kiến trúc hệ thống (System Architecture)

```
                       ┌────────────────────────────────────────────────────────┐
                       │                     CLIENT ACCESS                      │
                       │   - Corporate Wi-Fi / LAN Network                      │
                       │   - Remote Access VPN (IKEv2 / IPSec)                  │
                       └───────────────────────────┬────────────────────────────┘
                                                   │
                                     http://intranet.khai.local
                                                   │
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SENTINELAD / KHAI TECHNOLOGY PORTAL                                     │
│  ┌───────────────────────────┐ ┌───────────────────────────┐ ┌──────────────────────────────────────┐  │
│  │   Intranet Operations     │ │   Enterprise Identity     │ │   Security & AI Observability        │  │
│  │  - Dashboard & Timeline   │ │  - Active Directory Sync │ │  - Event Log Auditing (4624/4625)   │  │
│  │  - Lịch họp & RSVP        │ │  - Two-way Provisioning   │ │  - AI Security Incident Analyzer    │  │
│  │  - Bảng tin & Nhân viên mới│ │  - RBAC Role Mapping      │ │  - Real-time Telegram Bot Alert     │  │
│  │  - Phiếu lương bảo mật    │ │  - IT Asset Management    │ │  - Grafana & Prometheus Dashboards  │  │
│  │  - IT Helpdesk Tickets    │ │  - Employee & Dept OU     │ │  - Loki & Promtail Log Aggregator   │  │
│  └───────────────────────────┘ └───────────────────────────┘ └──────────────────────────────────────┘  │
└──────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                           │
                        LDAP (Port 389) / Windows Event Forwarding
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 WINDOWS SERVER 2022 DOMAIN CONTROLLER                                  │
│                                           DC-01 (192.168.101.10)                                       │
│   - Domain Name: khai.local                                                                            │
│   - Roles: Active Directory Domain Services (AD DS), DNS Server, DHCP Server, RRAS VPN Server          │
│   - OUs: OU=Company (IT, HR, Finance, Sales, Marketing, Telesale, Servers, Workstations)               │
│   - Security Groups: IT_Admin, HR_Manager, Finance_Manager, Sales_Manager, Helpdesk, Department_User   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Các tính năng chính (Key Features)

### 1. 🏢 Cổng Thông tin Doanh nghiệp (Enterprise Intranet)
* **Trang chủ & Banner thời gian thực:** Chào đón nhân viên, đếm cuộc họp trong ngày, cảnh báo phiếu lương mới.
* **Lịch họp thông minh (Meetings):** Tạo lịch họp (Standup, Review, All Hands...), đặt agenda, lọc theo ngày/tuần và tính năng **RSVP** xác nhận tham dự.
* **Thông báo & Chào đón nhân sự mới (Announcements):** Phân loại thông báo (Nhân viên mới, Cập nhật công ty, Sự kiện, Chính sách) kèm chức năng **Ghim bài (Pinned)**.
* **Phiếu lương bảo mật (Payroll):** Nhân viên chỉ xem được lương của chính mình. Tự động tính toán thực lãnh, lưu trữ lịch sử lương.
* **Hỗ trợ kỹ thuật (IT Helpdesk Tickets):** Tạo ticket yêu cầu hỗ trợ, phân quyền xử lý theo mức độ ưu tiên (Critical, High, Medium, Low).
* **Quản lý tài sản CNTT (IT Asset Tracking):** Quản lý máy chủ, thiết bị mạng, laptop, hạn bảo hành.

### 2. 🔐 Quản trị Định danh Active Directory (Identity & Access Management)
* **Live LDAP Authentication:** Xác thực trực tiếp với `192.168.101.10:389` qua tài khoản Active Directory thật.
* **Đồng bộ 2 chiều (Two-way Provisioning):** Tạo/Sửa/Xóa Nhân viên hoặc Phòng ban trên Web sẽ tự động kích hoạt tạo User và OU trên Active Directory trên Windows Server 2022.
* **Nút Đồng bộ 1-Click (`sync_ad`):** Quét toàn bộ cây OU và danh sách tài khoản từ máy chủ DC-01 về cơ sở dữ liệu Web ngay lập tức.
* **Phân quyền vai trò (RBAC):** Tự động ánh xạ từ Security Groups trong AD sang quyền hạn trên Web:
  * `IT_Admin` / `Domain Admins` → **Administrator** (Toàn quyền)
  * `HR_Manager` → **HR Manager** (Quản lý nhân sự, tạo phiếu lương)
  * `Finance_Manager` → **Finance Manager** (Quản lý tài chính)
  * `Sales_Manager` → **Sales Manager** (Quản trị kinh doanh)
  * `Department_User` → **Employee** (Nhân viên thông thường)

### 3. 🤖 Giám sát An toàn & Trí tuệ Nhân tạo (AI & Observability)
* **Nhật ký sự kiện (Audit Logging):** Ghi lại toàn bộ hành vi đăng nhập (thành công/thất bại), thao tác CRUD dữ liệu.
* **AI Security Analyzer:** Tích hợp mô hình AI Llama 3.1 phân tích phát hiện tấn công Brute-force (Event 4625), xâm nhập bất thường và đưa ra khuyến nghị phòng thủ.
* **Cảnh báo tức thì qua Telegram Bot:** Tự động gửi thông báo báo động khi có dấu hiệu tấn công hoặc lỗi hạ tầng về điện thoại Admin.
* **Hạ tầng Giám sát Full-Stack:**
  * **Prometheus:** Thu thập metrics tài nguyên máy chủ.
  * **Grafana:** Dashboard hiển thị trực quan tải CPU/RAM, Event Logs và Network.
  * **Loki & Promtail:** Tập trung và truy vấn log máy chủ thời gian thực.
* **VPN Remote Access (IKEv2 / L2TP):** Kết nối an toàn từ xa cho quản trị viên khi đi công tác.

---

## 🛠️ Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ |
| :--- | :--- |
| **Backend** | Python 3.13, Django 5.0+, SQLite / PostgreSQL |
| **Frontend** | HTML5, Vanilla CSS3 (Custom Dark/Tech Theme), Bootstrap 5, Chart.js |
| **Directory Services** | Microsoft Windows Server 2022 AD DS, LDAP3 |
| **AI Integration** | Groq API (Meta Llama 3.1 70B / 8B) |
| **Monitoring & Logs** | Docker, Prometheus, Grafana, Loki, Promtail, Windows Exporter |
| **Notifications** | Telegram Bot API (Python Telegram Bot) |
| **Remote Access** | Windows Server Routing and Remote Access (RRAS), IKEv2 / IPsec |

---

## 💻 Hướng dẫn cài đặt & Khởi chạy (Getting Started)

### 1. Yêu cầu hệ thống
* Python 3.10+
* Docker & Docker Compose (cho cụm Giám sát)
* Máy chủ Windows Server 2022 (Domain `khai.local`, IP `192.168.101.10`)

### 2. Cài đặt Cổng thông tin (Portal)
```bash
# Di chuyển vào thư mục portal
cd sentinelad_portal

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Chạy migrations cơ sở dữ liệu
python manage.py migrate

# Đồng bộ dữ liệu thực tế từ Active Directory DC-01
python manage.py sync_ad

# Khởi chạy máy chủ Web
python manage.py runserver 0.0.0.0:80
```

### 3. Khởi chạy Cụm Giám sát (Monitoring Stack)
```bash
# Di chuyển vào thư mục monitoring
cd monitoring

# Khởi động Prometheus, Loki, Promtail, Grafana
docker compose up -d
```

### 4. Truy cập dịch vụ
* **Cổng thông tin nội bộ:** `http://intranet.khai.local` (hoặc `http://localhost`)
* **Grafana Observability:** `http://grafana.khai.local:3000` (hoặc `http://localhost:3000`)
* **Prometheus Metrics:** `http://localhost:9090`

---

## 👥 Tác giả (Author)

* **Hoàng Trần Việt Khải** - *Lead Engineer & System Administrator*
* **Dự án:** *SentinelAD - Khai Technology Intelligent Enterprise Portal*
* **Tổ chức:** *Khai Technology (`khai.local`)*

---

*© 2026 Khai Technology. All rights reserved.*
