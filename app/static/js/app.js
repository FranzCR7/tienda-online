/* app/static/js/app.js - JavaScript principal de TiendaOnline */

document.addEventListener('DOMContentLoaded', function () {

    // ── Auto-cerrar alertas tras 5 segundos ───────────────────────────────
    const alertas = document.querySelectorAll('.alert.alert-dismissible');
    alertas.forEach(alerta => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alerta);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // ── Actualizar badge del carrito ───────────────────────────────────────
    function actualizarBadgeCarrito() {
        const badge = document.getElementById('badge-carrito');
        if (!badge) return;

        fetch('/carrito/contar')
            .then(r => r.json())
            .then(data => {
                const total = data.total || 0;
                badge.textContent = total;
                badge.style.display = total > 0 ? 'inline' : 'none';
            })
            .catch(() => { badge.style.display = 'none'; });
    }

    actualizarBadgeCarrito();

    // ── Confirmación antes de eliminar ────────────────────────────────────
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm || '¿Estás seguro?')) {
                e.preventDefault();
            }
        });
    });

    // ── Tooltips Bootstrap ────────────────────────────────────────────────
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    // ── Inyectar año actual en el footer ──────────────────────────────────
    const yearEl = document.getElementById('year-actual');
    if (yearEl) yearEl.textContent = new Date().getFullYear();

});
