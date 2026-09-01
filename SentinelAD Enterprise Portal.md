# SentinelAD Enterprise Portal
## Internal Website Requirements Specification

Version: 1.0

---

# 1. Project Overview

## Purpose

Xây dựng cổng thông tin nội bộ doanh nghiệp tích hợp với Active Directory nhằm quản lý nhân viên, phòng ban, tài sản CNTT và hỗ trợ giám sát hạ tầng.

Website sẽ sử dụng LDAP Authentication để xác thực người dùng từ Domain Controller.

Domain:

khai.local

Website URL:

https://intranet.khai.local

---

# 2. Business Goals

Mục tiêu của hệ thống:

- Quản lý nhân viên nội bộ
- Quản lý phòng ban
- Quản lý tài sản CNTT
- Quản lý ticket hỗ trợ kỹ thuật
- Đồng bộ đăng nhập với Active Directory
- Ghi nhận Audit Log
- Cung cấp dữ liệu cho Grafana Monitoring

---

# 3. System Architecture

## Active Directory

Domain Controller:

DC-01

Domain:

khai.local

Authentication Method:

LDAP

---

## Web Server

Hostname:

WEB01

Operating System:

Ubuntu Server 24.04 LTS

IP Address:

192.168.101.20

---

## Database Server

Database:

PostgreSQL

Database Name:

sentinelad

---

# 4. Technology Stack

## Backend

Framework:

Django

Language:

Python 3.12

Reason:

- LDAP hỗ trợ tốt
- Bảo mật tốt
- Nhiều package doanh nghiệp

---

## Frontend

- HTML
- Bootstrap 5
- JavaScript

---

## Database

PostgreSQL

---

## Authentication

LDAP Authentication

Active Directory Integration

---

# 5. User Roles

## Administrator

Quyền:

- Toàn quyền hệ thống
- Quản lý người dùng
- Quản lý phòng ban
- Quản lý tài sản
- Xem Audit Log
- Quản lý Ticket

AD Group:

IT_Admin

---

## HR Manager

Quyền:

- Quản lý nhân viên
- Xem phòng ban

AD Group:

HR_Manager

---

## Employee

Quyền:

- Xem hồ sơ cá nhân
- Tạo ticket
- Xem thông báo

AD Group:

Department_User

---

# 6. Modules

## Dashboard

Hiển thị:

- Tổng nhân viên
- Tổng phòng ban
- Tổng tài sản
- Ticket đang mở
- Ticket đã xử lý

---

## Employee Management

### Chức năng

- Thêm nhân viên
- Sửa nhân viên
- Xóa nhân viên
- Tìm kiếm nhân viên

### Fields

Employee ID

Full Name

Email

Department

Position

Phone

Hire Date

Status

---

## Department Management

### Chức năng

- Thêm phòng ban
- Sửa phòng ban
- Xóa phòng ban

### Fields

Department Name

Manager

Description

---

## Asset Management

### Chức năng

- Quản lý thiết bị CNTT

### Asset Types

Laptop

Desktop

Printer

Switch

Router

Firewall

Server

---

### Fields

Asset Tag

Asset Name

Asset Type

Serial Number

Assigned User

Purchase Date

Warranty Date

Status

---

## Ticket System

### Chức năng

- Tạo ticket
- Phân công ticket
- Đóng ticket

### Priority

Low

Medium

High

Critical

### Status

Open

In Progress

Resolved

Closed

---

## Announcement Board

### Chức năng

- Đăng thông báo
- Chỉnh sửa thông báo
- Xóa thông báo

---

# 7. Authentication Requirements

## Login Method

LDAP Authentication

No Local User Account

---

## Login Flow

User

↓

Website

↓

LDAP Query

↓

Domain Controller

↓

Authentication Result

---

## Login Format

khai\\username

Ví dụ:

khai\\khai.it

---

# 8. Authorization Requirements

Role Mapping:

IT_Admin → Administrator

HR_Manager → HR Manager

Department_User → Employee

---

# 9. Audit Logging

Hệ thống phải ghi nhận:

- Login Success
- Login Failure
- Create User
- Update User
- Delete User
- Create Ticket
- Update Ticket
- Delete Ticket

Fields:

User

Action

Timestamp

Source IP

---

# 10. Database Schema

## Departments

DepartmentID

DepartmentName

Description

CreatedAt

---

## Employees

EmployeeID

FullName

Email

DepartmentID

Position

Phone

Status

CreatedAt

---

## Assets

AssetID

AssetTag

AssetName

AssetType

AssignedTo

Status

CreatedAt

---

## Tickets

TicketID

Title

Description

Priority

Status

CreatedBy

AssignedTo

CreatedAt

---

## Announcements

AnnouncementID

Title

Content

CreatedBy

CreatedAt

---

## AuditLogs

AuditID

User

Action

SourceIP

Timestamp

---

# 11. Monitoring Integration

Website phải xuất log để Grafana và Loki thu thập.

Các log cần ghi:

- Login Success
- Login Failure
- Ticket Creation
- Asset Assignment
- CRUD Operations

---

# 12. Security Requirements

- HTTPS Only
- CSRF Protection
- XSS Protection
- SQL Injection Protection
- Session Timeout
- Role-Based Access Control

---

# 13. Future Integrations

Phase 2:

- Grafana Dashboard
- Loki Log Collection
- AI Incident Analysis

Phase 3:

- Telegram Notifications
- Email Notifications
- Asset Lifecycle Tracking

---

# 14. Acceptance Criteria

Hệ thống được xem là hoàn thành khi:

- LDAP Login hoạt động
- RBAC hoạt động (IT_Admin, Helpdesk, HR_Manager, Finance_Manager, Sales_Manager, Department_User)
- CRUD nhân viên hoạt động
- CRUD phòng ban hoạt động
- CRUD tài sản hoạt động
- Ticket System hoạt động
- Audit Log hoạt động
- PostgreSQL hoạt động
- Website truy cập bằng https://intranet.khai.local
- Sẵn sàng tích hợp Grafana