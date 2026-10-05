// Anima los saldos: <p class="aw-saldo-cliente" data-target="1234.50">
document.querySelectorAll('.aw-saldo-cliente').forEach(function (el) {
    var target = parseFloat(String(el.dataset.target).replace(',', '.')) || 0;
    var duration = 800, start = null;
    var fmt = function (n) { return '$' + n.toLocaleString('es-CL', { maximumFractionDigits: 0 }); };
    function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / duration, 1);
        el.textContent = fmt(target * p);
        if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
});
