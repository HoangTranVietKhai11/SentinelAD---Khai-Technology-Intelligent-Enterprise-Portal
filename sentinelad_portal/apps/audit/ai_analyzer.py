import os
import json
import requests
from datetime import datetime, timedelta
from django.conf import settings
from groq import Groq


def analyze_logs(log_file_path=None):
    """Original log-only analysis - reads local audit log file."""
    if not log_file_path:
        log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'sentinelad_audit.log')
        
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            # Read last 100 lines
            lines = f.readlines()
            recent_logs = lines[-100:] if len(lines) > 100 else lines
    except Exception as e:
        return f"Error reading log file: {str(e)}"
        
    log_content = "".join(recent_logs)
    
    prompt = f"""
Bạn là một Chuyên gia Phân tích An ninh mạng (Security Analyst) cấp cao.
Dưới đây là các bản ghi nhật ký hoạt động (Audit Logs) mới nhất từ hệ thống SentinelAD Enterprise Portal.
Hãy phân tích các log này để tìm kiếm:
1. Các hành vi đăng nhập bất thường (ví dụ: đăng nhập sai nhiều lần từ một user).
2. Các hoạt động tạo, sửa, xóa tài nguyên đáng ngờ.
3. Bất kỳ rủi ro bảo mật tiềm ẩn nào khác.

Nếu phát hiện bất thường, hãy trình bày báo cáo bằng tiếng Việt, định dạng Markdown rõ ràng, bao gồm:
- **Tóm tắt sự cố**
- **Chi tiết hành vi**
- **Đánh giá mức độ nghiêm trọng (Low/Medium/High/Critical)**
- **Khuyến nghị khắc phục**

Nếu hệ thống hoàn toàn bình thường, hãy trả lời ngắn gọn: "Hệ thống hiện tại an toàn, không phát hiện dấu hiệu bất thường trong 100 log gần nhất."

Dữ liệu log:
```json
{log_content}
```
"""

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-20b",
            temperature=0.3,
            max_tokens=2048,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error connecting to Groq API: {str(e)}"


class GrafanaAIAnalyzer:
    """
    Advanced AI Analyzer that queries Grafana for Prometheus metrics and Loki logs,
    then combines with local audit data for comprehensive security analysis.
    """

    def __init__(self):
        self.grafana_url = getattr(settings, 'GRAFANA_URL', 'http://127.0.0.1:3000')
        self.token = getattr(settings, 'GRAFANA_SERVICE_ACCOUNT_TOKEN', '')
        self.prometheus_uid = getattr(settings, 'PROMETHEUS_DATASOURCE_UID', '')
        self.loki_uid = getattr(settings, 'LOKI_DATASOURCE_UID', '')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _grafana_request(self, endpoint, method='GET', data=None, params=None):
        """Make a request to Grafana API."""
        url = f"{self.grafana_url}{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, headers=self.headers, params=params, timeout=15)
            else:
                resp = requests.post(url, headers=self.headers, json=data, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {'error': 'Cannot connect to Grafana. Is it running?'}
        except requests.exceptions.Timeout:
            return {'error': 'Grafana request timed out'}
        except Exception as e:
            return {'error': str(e)}

    def check_grafana_connection(self):
        """Check if Grafana is reachable and token is valid."""
        result = self._grafana_request('/api/health')
        if 'error' in result:
            return False, result['error']
        return True, 'Connected'

    def query_prometheus(self, expr, start=None, end=None, step=60):
        """Query Prometheus via Grafana's datasource proxy API."""
        if not start:
            start = datetime.utcnow() - timedelta(hours=1)
        if not end:
            end = datetime.utcnow()

        start_ts = int(start.timestamp())
        end_ts = int(end.timestamp())

        endpoint = f"/api/datasources/proxy/uid/{self.prometheus_uid}/api/v1/query_range"
        params = {
            'query': expr,
            'start': start_ts,
            'end': end_ts,
            'step': step,
        }
        return self._grafana_request(endpoint, params=params)

    def query_prometheus_instant(self, expr):
        """Instant query to Prometheus via Grafana."""
        endpoint = f"/api/datasources/proxy/uid/{self.prometheus_uid}/api/v1/query"
        params = {'query': expr}
        return self._grafana_request(endpoint, params=params)

    def query_loki(self, query, limit=100, start=None, end=None):
        """Query Loki logs via Grafana's datasource proxy API."""
        if not start:
            start = datetime.utcnow() - timedelta(hours=24)
        if not end:
            end = datetime.utcnow()

        start_ns = int(start.timestamp() * 1e9)
        end_ns = int(end.timestamp() * 1e9)

        endpoint = f"/api/datasources/proxy/uid/{self.loki_uid}/loki/api/v1/query_range"
        params = {
            'query': query,
            'start': start_ns,
            'end': end_ns,
            'limit': limit,
        }
        return self._grafana_request(endpoint, params=params)

    def get_infrastructure_metrics(self):
        """Gather key infrastructure metrics from DC-01 via Prometheus."""
        metrics = {}

        # CPU Usage
        cpu_result = self.query_prometheus_instant(
            '100 - (avg(rate(windows_cpu_time_total{mode="idle",instance=~"192.168.101.10.*"}[5m])) * 100)'
        )
        metrics['cpu_usage'] = self._extract_value(cpu_result)

        # Memory Usage
        mem_result = self.query_prometheus_instant(
            '100 - (windows_os_physical_memory_free_bytes{instance=~"192.168.101.10.*"} / windows_cs_physical_memory_bytes{instance=~"192.168.101.10.*"} * 100)'
        )
        metrics['memory_usage'] = self._extract_value(mem_result)

        # Disk Usage (C: drive)
        disk_result = self.query_prometheus_instant(
            '100 - (windows_logical_disk_free_bytes{volume="C:",instance=~"192.168.101.10.*"} / windows_logical_disk_size_bytes{volume="C:",instance=~"192.168.101.10.*"} * 100)'
        )
        metrics['disk_usage_c'] = self._extract_value(disk_result)

        # System Uptime
        uptime_result = self.query_prometheus_instant(
            'windows_system_system_up_time{instance=~"192.168.101.10.*"}'
        )
        metrics['uptime_seconds'] = self._extract_value(uptime_result)

        # Network Traffic (bytes/sec)
        net_in = self.query_prometheus_instant(
            'rate(windows_net_bytes_received_total{instance=~"192.168.101.10.*"}[5m])'
        )
        net_out = self.query_prometheus_instant(
            'rate(windows_net_bytes_sent_total{instance=~"192.168.101.10.*"}[5m])'
        )
        metrics['network_in_bps'] = self._extract_value(net_in)
        metrics['network_out_bps'] = self._extract_value(net_out)

        # Critical AD Services
        services_query = (
            'windows_service_state{instance=~"192.168.101.10.*",'
            'name=~"dns|ntds|kdc|netlogon|dhcpserver|w32time|lanmanserver|samss",'
            'state="running"}'
        )
        services_result = self.query_prometheus_instant(services_query)
        metrics['ad_services'] = self._extract_services(services_result)

        # Process count
        proc_result = self.query_prometheus_instant(
            'windows_os_processes{instance=~"192.168.101.10.*"}'
        )
        metrics['processes'] = self._extract_value(proc_result)

        # Context switches per second
        ctx_result = self.query_prometheus_instant(
            'rate(windows_system_context_switches_total{instance=~"192.168.101.10.*"}[5m])'
        )
        metrics['context_switches_per_sec'] = self._extract_value(ctx_result)

        return metrics

    def get_security_logs(self, hours=24):
        """Get security-relevant logs from Loki."""
        logs = {}

        # All audit logs
        all_logs = self.query_loki('{job="sentinelad_audit"}', limit=200,
                                   start=datetime.utcnow() - timedelta(hours=hours))
        logs['all_events'] = self._extract_loki_entries(all_logs)

        # Login-related events
        login_logs = self.query_loki('{job="sentinelad_audit"} |~ "(?i)login"', limit=100,
                                     start=datetime.utcnow() - timedelta(hours=hours))
        logs['login_events'] = self._extract_loki_entries(login_logs)

        # Failed login attempts
        failed_logs = self.query_loki('{job="sentinelad_audit"} |~ "(?i)(fail|error|denied)"', limit=100,
                                      start=datetime.utcnow() - timedelta(hours=hours))
        logs['failed_events'] = self._extract_loki_entries(failed_logs)

        # Delete operations (potentially destructive)
        delete_logs = self.query_loki('{job="sentinelad_audit"} |~ "(?i)delete"', limit=50,
                                      start=datetime.utcnow() - timedelta(hours=hours))
        logs['delete_events'] = self._extract_loki_entries(delete_logs)

        return logs

    def get_local_audit_logs(self):
        """Read local audit log file as fallback/supplement."""
        log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'sentinelad_audit.log')
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[-100:] if len(lines) > 100 else lines
        except Exception:
            return []

    def full_system_analysis(self):
        """
        Perform a comprehensive system analysis combining:
        1. Prometheus infrastructure metrics (DC-01)
        2. Loki security logs
        3. Local audit logs
        Send all data to Groq AI for analysis.
        """
        # Gather all data
        connection_ok, conn_msg = self.check_grafana_connection()

        infra_metrics = {}
        security_logs = {}
        grafana_status = 'disconnected'

        if connection_ok:
            grafana_status = 'connected'
            infra_metrics = self.get_infrastructure_metrics()
            security_logs = self.get_security_logs(hours=24)

        local_logs = self.get_local_audit_logs()
        local_log_content = "".join(local_logs) if local_logs else "No local logs available."

        # Format data for AI
        infra_summary = self._format_infra_metrics(infra_metrics)
        security_summary = self._format_security_logs(security_logs)

        prompt = f"""
Bạn là một **Chuyên gia Phân tích An ninh mạng và Giám sát Hạ tầng cấp cao** cho hệ thống SentinelAD Enterprise Portal.
Dưới đây là dữ liệu TOÀN DIỆN từ 3 nguồn khác nhau. Hãy phân tích và đưa ra báo cáo bảo mật.

## NGUỒN 1: Infrastructure Metrics (Prometheus → DC-01: 192.168.101.10)
Grafana Connection: **{grafana_status}**
```
{infra_summary}
```

## NGUỒN 2: Security Logs (Loki → SentinelAD Audit)
```
{security_summary}
```

## NGUỒN 3: Local Audit Logs (100 dòng gần nhất)
```json
{local_log_content[:3000]}
```

---

Hãy trình bày **BÁO CÁO TOÀN DIỆN** bằng tiếng Việt, định dạng Markdown, bao gồm:

### 📊 1. TÌNH TRẠNG HẠ TẦNG (Infrastructure Health)
- CPU, RAM, Disk, Network của DC-01
- Trạng thái các dịch vụ Active Directory quan trọng (DNS, NTDS, KDC, Netlogon, DHCP)
- Đánh giá: Bình thường / Cảnh báo / Nguy hiểm

### 🔒 2. PHÂN TÍCH BẢO MẬT (Security Analysis)
- Đăng nhập thành công / thất bại (tìm brute-force pattern)
- Hoạt động tạo/sửa/xóa tài nguyên đáng ngờ
- IP bất thường
- Đánh giá mức độ nghiêm trọng: Low / Medium / High / Critical

### 🛡️ 3. KHUYẾN NGHỊ (Recommendations)
- Đề xuất khắc phục ngay (nếu có vấn đề)
- Đề xuất cải thiện bảo mật dài hạn
- Đề xuất giám sát thêm

### 📈 4. TỔNG QUAN HỆ THỐNG
- Overall System Health Score: X/100
- Tóm tắt 1 câu về trạng thái hệ thống
"""

        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior cybersecurity analyst and infrastructure monitoring expert. "
                                   "Respond in Vietnamese with clear Markdown formatting. Be specific and actionable.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=4096,
            )
            return {
                'analysis': chat_completion.choices[0].message.content,
                'grafana_status': grafana_status,
                'metrics_snapshot': infra_metrics,
                'log_counts': {
                    'total_events': len(security_logs.get('all_events', [])),
                    'login_events': len(security_logs.get('login_events', [])),
                    'failed_events': len(security_logs.get('failed_events', [])),
                    'delete_events': len(security_logs.get('delete_events', [])),
                    'local_logs': len(local_logs),
                },
            }
        except Exception as e:
            return {
                'analysis': f"Error connecting to Groq API: {str(e)}",
                'grafana_status': grafana_status,
                'metrics_snapshot': infra_metrics,
                'log_counts': {},
            }

    def _extract_value(self, prom_result):
        """Extract a single numeric value from Prometheus query result."""
        try:
            if 'error' in prom_result:
                return None
            data = prom_result.get('data', {}).get('result', [])
            if data:
                value = data[0].get('value', [None, None])
                return round(float(value[1]), 2) if value[1] else None
        except (IndexError, TypeError, ValueError):
            pass
        return None

    def _extract_services(self, prom_result):
        """Extract service status from Prometheus query result."""
        services = {}
        try:
            if 'error' in prom_result:
                return services
            data = prom_result.get('data', {}).get('result', [])
            for item in data:
                name = item.get('metric', {}).get('name', 'unknown')
                value = item.get('value', [None, '0'])
                services[name] = 'running' if value[1] == '1' else 'stopped'
        except Exception:
            pass
        return services

    def _extract_loki_entries(self, loki_result):
        """Extract log entries from Loki query result."""
        entries = []
        try:
            if 'error' in loki_result:
                return entries
            data = loki_result.get('data', {}).get('result', [])
            for stream in data:
                for ts, line in stream.get('values', []):
                    entries.append(line)
        except Exception:
            pass
        return entries

    def _format_infra_metrics(self, metrics):
        """Format infrastructure metrics as a readable string."""
        if not metrics:
            return "No infrastructure metrics available (Grafana disconnected or Prometheus unavailable)."

        lines = []
        if metrics.get('cpu_usage') is not None:
            lines.append(f"CPU Usage: {metrics['cpu_usage']}%")
        if metrics.get('memory_usage') is not None:
            lines.append(f"Memory Usage: {metrics['memory_usage']}%")
        if metrics.get('disk_usage_c') is not None:
            lines.append(f"Disk C: Usage: {metrics['disk_usage_c']}%")
        if metrics.get('uptime_seconds') is not None:
            uptime_days = round(metrics['uptime_seconds'] / 86400, 1)
            lines.append(f"System Uptime: {uptime_days} days")
        if metrics.get('network_in_bps') is not None:
            lines.append(f"Network In: {round(metrics['network_in_bps'] / 1024, 2)} KB/s")
        if metrics.get('network_out_bps') is not None:
            lines.append(f"Network Out: {round(metrics['network_out_bps'] / 1024, 2)} KB/s")
        if metrics.get('processes') is not None:
            lines.append(f"Running Processes: {int(metrics['processes'])}")
        if metrics.get('context_switches_per_sec') is not None:
            lines.append(f"Context Switches/sec: {round(metrics['context_switches_per_sec'], 0)}")

        ad_services = metrics.get('ad_services', {})
        if ad_services:
            lines.append("\nActive Directory Services:")
            for svc, status in ad_services.items():
                icon = "✅" if status == "running" else "❌"
                lines.append(f"  {icon} {svc}: {status}")

        return "\n".join(lines) if lines else "No metrics data available."

    def _format_security_logs(self, logs):
        """Format security logs as a readable summary."""
        if not logs:
            return "No security logs available (Loki disconnected or no data)."

        lines = []
        lines.append(f"Total Events (24h): {len(logs.get('all_events', []))}")
        lines.append(f"Login Events: {len(logs.get('login_events', []))}")
        lines.append(f"Failed/Error Events: {len(logs.get('failed_events', []))}")
        lines.append(f"Delete Operations: {len(logs.get('delete_events', []))}")

        # Show sample of recent events
        all_events = logs.get('all_events', [])
        if all_events:
            lines.append(f"\nRecent Events (last {min(20, len(all_events))}):")
            for event in all_events[:20]:
                lines.append(f"  - {event[:200]}")

        return "\n".join(lines)
