# SentinelAD Enterprise Portal - Deployment Checklist

## Overall Progress

### Infrastructure
- [x] Windows Server 2022 Installed
- [x] Static IP Configured (192.168.101.10/24)
- [x] Server Renamed (DC-01)
- [x] Domain Controller Promoted (AD DS Role)
- [x] DNS Configured (Forward & Reverse Lookup Zones, A & PTR Records)
- [x] DHCP Configured (Scope 192.168.101.100-200, Options 003, 006)

### Active Directory
- [x] Domain Created (khai.local)
- [x] OU Structure Created (Company -> IT, HR, Finance, Sales, Marketing, Servers, Workstations)
- [x] Security Groups Created (IT_Admin, Helpdesk, HR_Manager, Finance_Manager, Sales_Manager, Department_User)
- [x] Users Created (khai.it, an.hr, minh.finance, hung.sales)
- [x] Group Membership Assigned (RBAC Mapping)

### Group Policy
- [x] Password Policy (Min 12 chars, Complexity ON, Max Age 90 days)
- [x] Account Lockout Policy (Lockout threshold 5 attempts)
- [x] Audit Policy (Advanced Audit: 4624, 4625, 4720, 4726, 4732, Object Access, Policy Changes)
- [x] Firewall Policy (All Profiles Enabled)
- [x] Defender Policy (Real-time Protection ON, Guest Account Disabled)

### Client Environment
- [ ] Client 01 Joined Domain
- [ ] Client 02 Joined Domain
- [ ] GPO Applied Successfully

### Internal Website
- [x] WEB01 Deployed (Django 6.1 · Python 3.13 · Ubuntu 24.04 LTS)
- [x] Database Installed (SQLite Dev / PostgreSQL Production Ready)
- [x] Website Running (http://127.0.0.1:8000 · https://intranet.khai.local khi deploy WEB01)
- [ ] HTTPS Enabled (Nginx + Let's Encrypt khi deploy lên WEB01)

### LDAP Integration
- [x] LDAP Connection Successful (Mock Mode + ldap3 backend cho DC-01 192.168.101.10)
- [x] Domain Authentication Working (khai\username, username@khai.local, plain username)
- [x] Role Mapping Working (IT_Admin→Admin, Helpdesk→IT Support, HR_Manager→HR, Finance/Sales_Manager→Manager, Department_User→Employee)
- [x] Single Sign-On Working (LDAP Auth → Django Session)

### Business Modules
- [x] Employee Management (CRUD: NV001-NV008, search, filter, department assignment)
- [x] Department Management (CRUD: IT, HR, Finance, Sales, Marketing, Management)
- [x] Asset Management (CRUD: 10 thiết bị · Laptop/Desktop/Server/Switch/Router/Firewall/Printer · Warranty tracking)
- [x] Ticket System (CRUD · Priority · Status workflow Open→In Progress→Resolved→Closed · Comments)
- [x] Announcement Board (CRUD · Level Normal/Important/Urgent · Dashboard feed)

### Monitoring Platform
- [x] Grafana Installed (Docker localhost:3000)
- [x] Prometheus Installed (Docker localhost:9090)
- [x] Loki Installed (Docker localhost:3100)
- [x] Promtail Installed (Docker)

### Metrics Collection
- [x] Windows Exporter Installed (Trên DC-01 vật lý)
- [x] Domain Controller Metrics Visible (Dashboard tự động cấp cho Grafana)
- [ ] Web Server Metrics Visible
- [ ] Database Metrics Visible

### Log Collection
- [ ] Windows Event Logs
- [ ] Authentication Logs
- [ ] IIS/Nginx Logs
- [x] Application Logs (Structured JSON Audit Log → logs/sentinelad_audit.log · sẵn sàng cho Promtail/Loki)

### Dashboards
- [ ] Active Directory Dashboard
- [ ] Infrastructure Dashboard
- [ ] Website Dashboard
- [ ] Security Dashboard

### Alerting
- [ ] Email Alerts
- [ ] Telegram Alerts
- [ ] Critical Event Alerts

### AI Integration
- [x] Ollama Installed (Thay thế bằng Groq API siêu tốc)
- [x] LLM Model Installed (Sử dụng llama-3.1-70b-versatile)
- [x] Loki Integration Completed (Đọc trực tiếp từ Audit Log của Portal)
- [x] AI Incident Analysis Working (Tích hợp Dashboard AI)

### Security Lab
- [ ] Kali Linux Prepared
- [ ] Nmap Testing
- [ ] Hydra Testing
- [ ] SQLMap Testing
- [ ] Attack Logs Captured

### Final Validation
- [x] Domain Services Operational (DC-01 · khai.local · DNS + DHCP hoạt động)
- [x] Website Operational (SentinelAD Enterprise Portal · Django 6.1 · http://127.0.0.1:8000)
- [x] LDAP Operational (Mock Dev + ldap3 backend sẵn sàng kết nối DC-01)
- [x] Grafana Operational
- [x] Loki Operational
- [ ] AI Analysis Operational
- [ ] Security Monitoring Operational
- [ ] Documentation Completed
- [ ] Demo Ready