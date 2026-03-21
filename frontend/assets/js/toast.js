(function () {
  var DURATION = 3500;
  var LABELS   = { success: 'Listo', error: 'Error', warning: 'Atención' };
  var ICONS = {
    success: '<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    error:   '<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    warning: '<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 3v6.5M8 12v.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
  };
  var CLOSE_ICON = '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';

  function getContainer() {
    var c = document.getElementById('_toast_container');
    if (!c) {
      c = document.createElement('div');
      c.id = '_toast_container';
      c.className = 'toast-container';
      document.body.appendChild(c);
    }
    return c;
  }

  window.showToast = function (message, type, duration) {
    type     = type     || 'success';
    duration = duration || DURATION;
    if (type === 'danger') type = 'error';
    if (type === 'info')   type = 'warning';
    if (type !== 'success' && type !== 'error' && type !== 'warning') type = 'error';

    var container = getContainer();
    var el = document.createElement('div');
    el.className = 'toast-item toast-' + type;
    el.innerHTML =
      '<div class="toast-icon">' + ICONS[type] + '</div>' +
      '<div class="toast-body">' +
        '<div class="toast-title">' + LABELS[type] + '</div>' +
        '<div class="toast-msg">' + String(message).replace(/</g, '&lt;') + '</div>' +
      '</div>' +
      '<button class="toast-close" aria-label="Cerrar">' + CLOSE_ICON + '</button>' +
      '<div class="toast-progress" style="animation-duration:' + duration + 'ms"></div>';
    container.appendChild(el);

    function dismiss() {
      el.classList.add('toast-out');
      el.addEventListener('animationend', function () { el.remove(); }, { once: true });
    }
    var timer = setTimeout(dismiss, duration);
    el.querySelector('.toast-close').addEventListener('click', function () {
      clearTimeout(timer);
      dismiss();
    });
  };
})();
