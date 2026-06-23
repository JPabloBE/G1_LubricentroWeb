(function () {
  const PHONE      = "+(506) 2443-6139";
  const PHONE_HREF = "tel:+50624436139";
  const MAPS_URL   = "https://maps.app.goo.gl/v2un81eScRmhvtA89";

  const QUESTIONS = [
    {
      label: "¿Cuál es el horario?",
      icon:  "bi-clock",
      answer: "Atendemos de <strong>lunes a sábado de 9:00 a 19:00 hrs</strong>. ¡Te esperamos cuando lo necesitás!"
    },
    {
      label: "¿Qué servicios realizan?",
      icon:  "bi-wrench-adjustable",
      answer: "Realizamos cambio de aceite y filtros, alineación y balanceo, diagnóstico computarizado, servicio de frenos, revisión general, cambio de correa de distribución, revisión de suspensión y <strong>mucho más</strong>."
    },
    {
      label: "¿Cómo agendo una cita?",
      icon:  "bi-calendar-plus",
      answer: "Podés agendar tu cita desde nuestro <strong>Portal Cliente</strong>: registrate o iniciá sesión, seleccioná tu vehículo, el servicio y el horario disponible. ¡Listo, así de fácil!"
    },
    {
      label: "¿Dónde están ubicados?",
      icon:  "bi-geo-alt",
      answer: "Estamos en <strong>Montecillos, Alajuela</strong>.",
      extra:  "maps"
    },
    {
      label: "¿Es necesario sacar una cita?",
      icon:  "bi-patch-question",
      answer: "¡No necesariamente! Podés venir directamente al taller. Sin embargo, sacar una cita tiene varias ventajas:<br><br>✅ Tu vehículo es atendido <strong>sin atrasos</strong>, con horario garantizado.<br>⭐ Tenés <strong>prioridad</strong> sobre los ingresos sin cita.<br>📱 Podés <strong>rastrear el estado de tu vehículo</strong> en tiempo real desde esta app.<br>🔔 Recibís <strong>notificaciones y mensajes del taller</strong> con actualizaciones.<br><br>¡Te recomendamos agendar para una mejor experiencia!"
    },
    {
      label: "Otros",
      icon:  "bi-chat-dots",
      answer: null
    }
  ];

  /* ── CSS ────────────────────────────────────────────────────── */
  const style = document.createElement("style");
  style.textContent = `
    .cw-bubble {
      position:        fixed;
      bottom:          24px;
      right:           24px;
      width:           58px;
      height:          58px;
      border-radius:   50%;
      background:      var(--accent-red, #e03e1a);
      border:          none;
      cursor:          pointer;
      display:         flex;
      align-items:     center;
      justify-content: center;
      box-shadow:      0 4px 20px rgba(224,62,26,.45);
      z-index:         9990;
      transition:      transform .2s, box-shadow .2s;
      padding:         0;
    }
    .cw-bubble:hover {
      transform:  scale(1.08);
      box-shadow: 0 6px 28px rgba(224,62,26,.6);
    }
    .cw-bubble svg { width: 30px; height: 30px; fill: #fff; flex-shrink: 0; }

    /* popup */
    .cw-popup {
      position:       fixed;
      bottom:         94px;
      right:          24px;
      width:          320px;
      display:        flex;
      flex-direction: column;
      background:     var(--bg-elevated, #1a1a2e);
      border:         1px solid var(--border-bright, rgba(255,255,255,.12));
      border-radius:  14px;
      box-shadow:     0 12px 40px rgba(0,0,0,.55);
      z-index:        9989;
      overflow:       hidden;
      transform-origin: bottom right;
      transform:      scale(.85);
      opacity:        0;
      pointer-events: none;
      transition:     transform .22s cubic-bezier(.34,1.56,.64,1), opacity .18s ease;
      max-height:     520px;
    }
    .cw-popup.cw-open {
      transform:      scale(1);
      opacity:        1;
      pointer-events: auto;
    }

    /* header */
    .cw-header {
      display:         flex;
      align-items:     center;
      gap:             10px;
      padding:         13px 14px 11px;
      background:      var(--accent-red, #e03e1a);
      flex-shrink:     0;
    }
    .cw-header-icon {
      width:           34px;
      height:          34px;
      border-radius:   50%;
      background:      rgba(255,255,255,.18);
      display:         flex;
      align-items:     center;
      justify-content: center;
      flex-shrink:     0;
    }
    .cw-header-icon svg { width: 20px; height: 20px; fill: #fff; }
    .cw-header-text   { flex: 1; min-width: 0; }
    .cw-header-title  {
      font-family:    var(--font-display, 'Barlow Condensed', sans-serif);
      font-size:      15px;
      font-weight:    800;
      text-transform: uppercase;
      letter-spacing: .06em;
      color:          #fff;
      line-height:    1;
    }
    .cw-header-sub { font-size: 11px; color: rgba(255,255,255,.75); margin-top: 2px; }
    .cw-close {
      background:  rgba(255,255,255,.15);
      border:      none;
      border-radius: 50%;
      width:       28px;
      height:      28px;
      display:     flex;
      align-items: center;
      justify-content: center;
      cursor:      pointer;
      color:       #fff;
      font-size:   14px;
      flex-shrink: 0;
      transition:  background .15s;
    }
    .cw-close:hover { background: rgba(255,255,255,.28); }

    /* messages area */
    .cw-messages {
      flex:       1;
      overflow-y: auto;
      padding:    14px 12px 8px;
      display:    flex;
      flex-direction: column;
      gap:        10px;
      scrollbar-width: thin;
      scrollbar-color: rgba(255,255,255,.1) transparent;
    }
    .cw-messages::-webkit-scrollbar { width: 4px; }
    .cw-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 4px; }

    /* message bubbles */
    .cw-row {
      display:   flex;
      gap:       7px;
      align-items: flex-end;
    }
    .cw-row.user { flex-direction: row-reverse; }

    .cw-avatar {
      width:         28px;
      height:        28px;
      border-radius: 50%;
      background:    var(--accent-red, #e03e1a);
      display:       flex;
      align-items:   center;
      justify-content: center;
      flex-shrink:   0;
    }
    .cw-avatar svg { width: 16px; height: 16px; fill: #fff; }

    .cw-bubble-msg {
      max-width:     75%;
      padding:       9px 12px;
      border-radius: 12px;
      font-size:     13px;
      line-height:   1.5;
      animation:     cwFadeUp .2s ease;
    }
    @keyframes cwFadeUp {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .cw-row.bot  .cw-bubble-msg {
      background:    var(--bg-surface, #252540);
      color:         var(--text-primary, #f1f5f9);
      border-bottom-left-radius: 3px;
    }
    .cw-row.user .cw-bubble-msg {
      background:    var(--accent-red, #e03e1a);
      color:         #fff;
      border-bottom-right-radius: 3px;
    }
    .cw-bubble-msg strong { color: inherit; font-weight: 700; }

    /* maps card */
    .cw-maps-btn {
      display:         flex;
      align-items:     center;
      gap:             6px;
      margin-top:      8px;
      padding:         7px 11px;
      background:      rgba(224,62,26,.15);
      border:          1px solid rgba(224,62,26,.35);
      border-radius:   7px;
      color:           var(--accent-red, #e03e1a);
      font-size:       12px;
      font-weight:     700;
      text-decoration: none;
      transition:      background .15s;
    }
    .cw-maps-btn:hover { background: rgba(224,62,26,.25); color: var(--accent-red, #e03e1a); }

    /* phone card in "otros" */
    .cw-phone-card {
      background:    var(--bg-surface, #252540);
      border:        1px solid var(--border-bright, rgba(255,255,255,.1));
      border-radius: 10px;
      padding:       12px;
      animation:     cwFadeUp .2s ease;
    }
    .cw-phone-badge {
      display:        inline-flex;
      align-items:    center;
      gap:            5px;
      background:     rgba(224,62,26,.12);
      border:         1px solid rgba(224,62,26,.3);
      border-radius:  20px;
      padding:        2px 9px;
      font-size:      10px;
      font-weight:    700;
      text-transform: uppercase;
      letter-spacing: .07em;
      color:          var(--accent-red, #e03e1a);
      margin-bottom:  8px;
    }
    .cw-phone-dot {
      width:         5px;
      height:        5px;
      border-radius: 50%;
      background:    var(--accent-red, #e03e1a);
      animation:     cw-pulse 1.6s ease-in-out infinite;
    }
    @keyframes cw-pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%      { opacity: .4; transform: scale(.7); }
    }
    .cw-phone-text {
      font-size:   12.5px;
      color:       var(--text-muted, #94a3b8);
      line-height: 1.5;
      margin-bottom: 10px;
    }
    .cw-phone-text strong { color: var(--text-primary, #f1f5f9); }
    .cw-phone-link {
      display:         flex;
      align-items:     center;
      justify-content: center;
      gap:             7px;
      width:           100%;
      padding:         10px;
      background:      var(--accent-red, #e03e1a);
      color:           #fff;
      border-radius:   7px;
      font-family:     var(--font-display, 'Barlow Condensed', sans-serif);
      font-size:       13px;
      font-weight:     800;
      text-transform:  uppercase;
      letter-spacing:  .06em;
      text-decoration: none;
      transition:      background .15s;
    }
    .cw-phone-link:hover { background: #c43518; color: #fff; }

    /* typing indicator */
    .cw-typing-row { display: flex; gap: 7px; align-items: flex-end; }
    .cw-typing-bubble {
      background:    var(--bg-surface, #252540);
      border-radius: 12px;
      border-bottom-left-radius: 3px;
      padding:       10px 14px;
      display:       flex;
      gap:           5px;
      align-items:   center;
    }
    .cw-dot {
      width:         7px;
      height:        7px;
      border-radius: 50%;
      background:    var(--text-muted, #94a3b8);
      animation:     cwBounce 1.1s ease-in-out infinite;
    }
    .cw-dot:nth-child(2) { animation-delay: .18s; }
    .cw-dot:nth-child(3) { animation-delay: .36s; }
    @keyframes cwBounce {
      0%, 60%, 100% { transform: translateY(0); }
      30%           { transform: translateY(-6px); }
    }

    /* question chips */
    .cw-chips {
      padding:         0 12px 12px;
      display:         flex;
      flex-direction:  column;
      gap:             6px;
      flex-shrink:     0;
    }
    .cw-chip {
      display:        flex;
      align-items:    center;
      gap:            8px;
      width:          100%;
      padding:        9px 12px;
      background:     var(--bg-surface, #252540);
      border:         1.5px solid var(--border-bright, rgba(255,255,255,.1));
      border-radius:  8px;
      color:          var(--text-primary, #f1f5f9);
      font-size:      12.5px;
      font-weight:    600;
      cursor:         pointer;
      text-align:     left;
      transition:     border-color .15s, background .15s;
    }
    .cw-chip:hover {
      border-color: var(--accent-red, #e03e1a);
      background:   rgba(224,62,26,.08);
    }
    .cw-chip i { color: var(--accent-red, #e03e1a); font-size: 13px; flex-shrink: 0; }
    .cw-chip.otros { color: var(--text-muted, #94a3b8); }

    /* back button */
    .cw-back {
      display:         flex;
      align-items:     center;
      justify-content: center;
      gap:             5px;
      margin:          0 12px 12px;
      width:           calc(100% - 24px);
      background:      transparent;
      border:          1.5px dashed var(--border-bright, rgba(255,255,255,.15));
      border-radius:   7px;
      color:           var(--text-muted, #94a3b8);
      font-size:       12px;
      font-weight:     600;
      padding:         9px 12px;
      cursor:          pointer;
      transition:      border-color .15s, color .15s;
      flex-shrink:     0;
      box-sizing:      border-box;
    }
    .cw-back:hover { border-color: var(--accent-red, #e03e1a); color: var(--text-primary, #f1f5f9); }

    /* mobile */
    @media (max-width: 480px) {
      .cw-bubble { bottom: 20px; right: 16px; width: 54px; height: 54px; }
      .cw-popup  { right: 12px; left: 12px; width: auto; bottom: 86px; max-height: 70vh; }
    }
  `;
  document.head.appendChild(style);

  /* ── SVG ────────────────────────────────────────────────────── */
  const SVG = `<svg viewBox="0 0 360.855 360.855" xmlns="http://www.w3.org/2000/svg"><g><path d="M180.428,197.204c24.125,0,80.846-29.034,80.846-98.603c0-9.704-0.236-19.078-1.036-27.935c-1.313-17.431-4.883-32.879-13.772-44.718C235.064,9.837,215.116,0,180.428,0c-34.682,0-54.629,9.833-66.031,25.939c-8.895,11.842-12.467,27.294-13.779,44.731c-0.799,8.856-1.035,18.229-1.035,27.932C99.582,168.17,156.303,197.204,180.428,197.204zM206.817,36.123c-2.354,5.951-3.534,8.927-5.89,14.877c-15.209-4.297-25.791-4.297-41,0c-2.355-5.95-3.535-8.926-5.891-14.877C173.057,30.365,187.799,30.366,206.817,36.123zM111.609,83.517c0.932,2.037,4.889,9.87,11.014,10.604c7.041,0.845,18.728-24.935,57.805-24.998c39.076,0.063,50.764,25.843,57.805,24.998c6.125-0.735,10.082-8.567,11.014-10.604c0.189,4.992,0.259,10.046,0.259,15.085c0,34.005-15.015,55.075-27.612,66.762c-15.871,14.727-33.493,20.072-41.465,20.072s-25.594-5.345-41.465-20.072c-12.598-11.687-27.612-32.757-27.612-66.762C111.351,93.563,111.42,88.509,111.609,83.517z"/><path d="M330.52,298.327c-4.128-25.664-12.624-58.724-29.668-70.472c-11.64-8.026-52.248-29.721-69.589-38.985l-0.293-0.156c-1.982-1.059-4.403-0.846-6.169,0.541c-9.084,7.131-19.034,11.937-29.574,14.284c-1.862,0.415-3.391,1.738-4.066,3.521l-10.733,28.291l-10.734-28.291c-0.675-1.783-2.203-3.106-4.066-3.521c-10.539-2.347-20.489-7.153-29.572-14.284c-1.77-1.388-4.189-1.6-6.171-0.541c-17.134,9.156-58.239,31.294-69.829,39.107c-19.621,13.217-28.199,61.052-29.72,70.507c-0.15,0.938-0.063,1.897,0.253,2.793c0.416,1.174,6.905,17.982,39.357,31.496c1.871-2.358,4.363-4.146,7.166-5.152c-3.482-1.236-6.504-3.659-8.437-6.911c-2.88-4.846-2.987-10.927-0.286-15.858c8.32-15.23,24.254-24.706,41.604-24.729c16.138,0,30.767,8.019,39.454,21.053h61.926c1.7-2.539,3.65-4.914,5.838-7.109c8.95-8.976,20.857-13.928,33.529-13.946h0.01h0.01c17.336,0,33.29,9.424,41.639,24.602c2.706,4.926,2.615,10.995-0.248,15.857c-1.922,3.253-4.936,5.684-8.414,6.931c2.852,1.01,5.383,2.825,7.268,5.224c32.369-13.507,38.848-30.284,39.264-31.456C330.584,300.224,330.671,299.264,330.52,298.327z"/><path d="M278.414,340.434h-0.004l-29.836,0.041c-0.529-1.256-1.545-4.744-1.555-13.065c-0.014-8.322,0.99-11.816,1.518-13.075l29.828-0.044c0.713-0.004,1.371-0.379,1.732-0.992c0.363-0.615,0.373-1.371,0.031-1.995c-5.885-10.698-17.115-17.342-29.369-17.342c-8.934,0.013-17.326,3.505-23.633,9.831c-3.25,3.258-5.73,7.074-7.383,11.225h-78.668c-4.939-12.315-16.992-21.053-31.082-21.053c-12.217,0.017-23.451,6.699-29.318,17.441c-0.342,0.624-0.328,1.383,0.035,1.994c0.363,0.611,1.021,0.984,1.732,0.984h0.002l29.836-0.047c0.531,1.256,1.545,4.744,1.555,13.068c0.014,8.323-0.99,11.815-1.518,13.072l-29.828,0.045c-0.711,0.001-1.369,0.379-1.732,0.99c-0.361,0.613-0.373,1.372-0.029,1.996c5.883,10.697,17.117,17.346,29.318,17.346h0.049c8.936-0.014,17.326-3.506,23.635-9.833c3.25-3.26,5.729-7.077,7.381-11.228h78.666c4.94,12.319,16.984,21.056,31.039,21.058c0,0,0.045,0,0.047,0c12.215-0.017,23.451-6.703,29.318-17.438c0.342-0.625,0.328-1.385-0.035-1.995C279.783,340.807,279.125,340.434,278.414,340.434z"/></g></svg>`;

  /* ── HTML ───────────────────────────────────────────────────── */
  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <button class="cw-bubble" id="cwBubble" aria-label="Asistente virtual">${SVG}</button>

    <div class="cw-popup" id="cwPopup" role="dialog" aria-label="Asistente virtual">
      <div class="cw-header">
        <div class="cw-header-icon">${SVG}</div>
        <div class="cw-header-text">
          <div class="cw-header-title">Asistente virtual</div>
          <div class="cw-header-sub">Lubricentro Montecillos</div>
        </div>
        <button class="cw-close" id="cwClose" aria-label="Cerrar">&#x2715;</button>
      </div>
      <div class="cw-messages" id="cwMessages"></div>
      <div id="cwFooter"></div>
    </div>
  `;
  document.body.appendChild(wrapper);

  /* ── State ──────────────────────────────────────────────────── */
  const messagesEl = document.getElementById("cwMessages");
  const footerEl   = document.getElementById("cwFooter");
  let   busy       = false;

  function scrollBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addRow(type, html) {
    const isUser = type === "user";
    const row = document.createElement("div");
    row.className = `cw-row ${type}`;
    if (!isUser) {
      row.innerHTML = `<div class="cw-avatar">${SVG}</div><div class="cw-bubble-msg">${html}</div>`;
    } else {
      row.innerHTML = `<div class="cw-bubble-msg">${html}</div>`;
    }
    messagesEl.appendChild(row);
    scrollBottom();
    return row;
  }

  function showTyping() {
    const row = document.createElement("div");
    row.className = "cw-typing-row";
    row.id = "cwTyping";
    row.innerHTML = `<div class="cw-avatar">${SVG}</div>
      <div class="cw-typing-bubble">
        <span class="cw-dot"></span>
        <span class="cw-dot"></span>
        <span class="cw-dot"></span>
      </div>`;
    messagesEl.appendChild(row);
    scrollBottom();
  }

  function removeTyping() {
    const t = document.getElementById("cwTyping");
    if (t) t.remove();
  }

  function renderChips() {
    footerEl.innerHTML = "";
    const chips = document.createElement("div");
    chips.className = "cw-chips";
    QUESTIONS.forEach((q, i) => {
      const btn = document.createElement("button");
      btn.className = "cw-chip" + (q.answer === null ? " otros" : "");
      btn.innerHTML = `<i class="bi ${q.icon}"></i>${q.label}`;
      btn.addEventListener("click", () => onChipClick(i));
      chips.appendChild(btn);
    });
    footerEl.appendChild(chips);
  }

  function renderBack() {
    footerEl.innerHTML = "";
    const back = document.createElement("button");
    back.className = "cw-back";
    back.innerHTML = `<i class="bi bi-arrow-left"></i> Hacer otra pregunta`;
    back.addEventListener("click", renderChips);
    footerEl.appendChild(back);
    scrollBottom();
  }

  async function onChipClick(idx) {
    if (busy) return;
    busy = true;
    const q = QUESTIONS[idx];

    // Quitar chips
    footerEl.innerHTML = "";

    // Burbuja del usuario
    addRow("user", q.label);

    // Typing
    await delay(350);
    showTyping();
    await delay(1100);
    removeTyping();

    if (q.answer === null) {
      // "Otros" → phone card
      const card = document.createElement("div");
      card.className = "cw-phone-card";
      card.innerHTML = `
        <div class="cw-phone-badge"><span class="cw-phone-dot"></span>Próximamente</div>
        <p class="cw-phone-text"><strong>¡Estamos trabajando en nuestro chat!</strong><br>
        Por el momento, para atención inmediata comunicate directamente con nosotros:</p>
        <a class="cw-phone-link" href="${PHONE_HREF}">
          <i class="bi bi-telephone-fill"></i> ${PHONE}
        </a>`;
      messagesEl.appendChild(card);
      scrollBottom();
    } else {
      let html = q.answer;
      if (q.extra === "maps") {
        html += `<br><a class="cw-maps-btn" href="${MAPS_URL}" target="_blank" rel="noopener">
          <i class="bi bi-map-fill"></i> Ver en Google Maps
        </a>`;
      }
      addRow("bot", html);
    }

    await delay(300);
    renderBack();
    busy = false;
  }

  function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

  /* ── Init chat ──────────────────────────────────────────────── */
  function initChat() {
    messagesEl.innerHTML = "";
    footerEl.innerHTML   = "";
    addRow("bot", "¡Hola! 👋 Soy el asistente de <strong>Lubricentro Montecillos</strong>. ¿En qué te puedo ayudar?");
    renderChips();
  }

  /* ── Controls ───────────────────────────────────────────────── */
  const bubble = document.getElementById("cwBubble");
  const popup  = document.getElementById("cwPopup");
  const close  = document.getElementById("cwClose");

  let initialized = false;

  function openPopup() {
    popup.classList.add("cw-open");
    bubble.setAttribute("aria-expanded", "true");
    if (!initialized) { initChat(); initialized = true; }
  }
  function closePopup() {
    popup.classList.remove("cw-open");
    bubble.setAttribute("aria-expanded", "false");
  }

  bubble.addEventListener("click", () => popup.classList.contains("cw-open") ? closePopup() : openPopup());
  close.addEventListener("click", closePopup);
  popup.addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("click", (e) => {
    if (!bubble.contains(e.target)) closePopup();
  });
})();
