// SentinelAD Enterprise Portal - Main JavaScript
// Auto-dismiss messages after 5s
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert-sentinel').forEach(function (el) {
        setTimeout(function () {
            el.style.opacity = '0';
            el.style.transition = 'opacity 0.5s';
            setTimeout(function () { el.remove(); }, 500);
        }, 5000);
    });

    // Mark active nav link
    const path = window.location.pathname;
    document.querySelectorAll('.nav-link-sidebar').forEach(function (link) {
        if (link.getAttribute('href') && path.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/') {
            link.classList.add('active');
        }
    });
});
