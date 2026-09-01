from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import AuditLog


@login_required
def audit_list(request):
    try:
        role = request.user.userprofile.role
    except Exception:
        role = 'employee'
    if role != 'administrator':
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    query = request.GET.get('q', '')
    action_filter = request.GET.get('action', '')
    logs = AuditLog.objects.select_related('user').all()
    if query:
        logs = logs.filter(Q(username__icontains=query) | Q(resource_name__icontains=query) |
                           Q(description__icontains=query) | Q(source_ip__icontains=query))
    if action_filter:
        logs = logs.filter(action=action_filter)
    return render(request, 'audit/audit_list.html', {
        'page_title': 'Audit Logs',
        'logs': logs[:500],
        'action_choices': AuditLog.ACTION_CHOICES,
        'query': query, 'action_filter': action_filter,
    })


@login_required
def ai_analysis(request):
    try:
        role = request.user.userprofile.role
    except Exception:
        role = 'employee'
    if role != 'administrator':
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    analysis_result = None
    analysis_mode = None
    grafana_status = None
    metrics_snapshot = None
    log_counts = None

    # Check Grafana connection status for UI
    from .ai_analyzer import GrafanaAIAnalyzer
    analyzer = GrafanaAIAnalyzer()
    connected, conn_msg = analyzer.check_grafana_connection()
    grafana_status = 'connected' if connected else 'disconnected'

    if request.method == 'POST':
        analysis_mode = request.POST.get('mode', 'logs')
        import markdown

        if analysis_mode == 'full':
            # Full System Analysis: Prometheus + Loki + Local Logs
            result = analyzer.full_system_analysis()
            analysis_result = markdown.markdown(
                result['analysis'],
                extensions=['tables', 'fenced_code']
            )
            metrics_snapshot = result.get('metrics_snapshot', {})
            log_counts = result.get('log_counts', {})
            grafana_status = result.get('grafana_status', grafana_status)
        else:
            # Audit Logs Only (original behavior)
            from .ai_analyzer import analyze_logs
            raw_markdown = analyze_logs()
            analysis_result = markdown.markdown(raw_markdown)

    return render(request, 'audit/ai_analysis.html', {
        'analysis_result': analysis_result,
        'analysis_mode': analysis_mode,
        'grafana_status': grafana_status,
        'metrics_snapshot': metrics_snapshot,
        'log_counts': log_counts,
    })

