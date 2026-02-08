const API_BASE = "http://localhost:8000";

// Este JS se usa dentro de /admin/
// Necesitas el puente: frontend/admin/auth.html -> ../auth_admin.html
const LOGIN_REDIRECT = "./auth.html";

function getToken() {
  return localStorage.getItem("access_token");
}

function authHeaders() {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  let data = null;
  try { data = await res.json(); } catch (_) {}
  if (!res.ok) {
    const msg = data ? JSON.stringify(data) : res.statusText;
    throw new Error(msg);
  }
  return data;
}

function isAdmin(me) {
  return (
    me?.user_type === "admin" ||
    me?.user_type === "staff" ||
    me?.is_staff === true ||
    me?.is_superuser === true
  );
}

function initialsFromName(name) {
  if (!name) return "A";
  const parts = name.trim().split(/\s+/);
  const a = parts[0]?.[0] || "A";
  const b = parts[1]?.[0] || "";
  return (a + b).toUpperCase();
}

function renderDemoOrders() {
  const demo = [
    { id: "#192541", customer: "Esther Howard", type: "Shipping", status: "Paid", product: "Aceite + Filtro", total: 3127.00, date: "Jun 19" },
    { id: "#192540", customer: "David Miller", type: "Pickup", status: "Paid", product: "Filtro aire", total: 58.00, date: "Jun 18" },
    { id: "#192539", customer: "James Moore", type: "Shipping", status: "Pending", product: "Aceite 15W-40", total: 152.80, date: "Jun 18" },
    { id: "#192538", customer: "Robert Anderson", type: "Shipping", status: "Paid", product: "Accesorios", total: 85.20, date: "Jun 17" },
    { id: "#192537", customer: "Jessica Martinez", type: "Pickup", status: "Cancelled", product: "Filtro aceite", total: 0.00, date: "Jun 17" },
  ];

  const tbody = document.getElementById("ordersTbody");
  if (!tbody) return;

  tbody.innerHTML = "";

  for (const o of demo) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input class="form-check-input" type="checkbox"></td>
      <td class="fw-semibold">${o.id}</td>
      <td>${o.customer}</td>
      <td>${o.type}</td>
      <td>
        <span class="badge ${o.status === "Paid" ? "text-bg-success" : o.status === "Pending" ? "text-bg-warning" : "text-bg-secondary"}">
          ${o.status}
        </span>
      </td>
      <td>${o.product}</td>
      <td class="text-end">$ ${o.total.toFixed(2)}</td>
      <td>${o.date}</td>
      <td class="text-end">⋯</td>
    `;
    tbody.appendChild(tr);
  }
}

async function init() {
  const token = getToken();
  if (!token) {
    window.location.href = LOGIN_REDIRECT;
    return;
  }

  try {
    const me = await fetchJSON(`${API_BASE}/api/auth/me/`, { headers: authHeaders() });

    if (!isAdmin(me)) {
      window.location.href = LOGIN_REDIRECT;
      return;
    }

    const displayName = me?.full_name || me?.username || me?.email || "Admin";

    const elName = document.getElementById("userName");
    const elRole = document.getElementById("userRole");
    const elInit = document.getElementById("userInitials");

    if (elName) elName.textContent = displayName;
    if (elRole) elRole.textContent = me?.user_type || (me?.is_superuser ? "admin" : "staff");
    if (elInit) elInit.textContent = initialsFromName(displayName);

    renderDemoOrders();
  } catch (_) {
    window.location.href = LOGIN_REDIRECT;
    return;
  }

  const btn = document.getElementById("btnLogout");
  if (btn) {
    btn.addEventListener("click", async () => {
      try {
        await fetchJSON(`${API_BASE}/api/auth/logout/`, { method: "POST", headers: authHeaders() });
      } catch (_) {}

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = LOGIN_REDIRECT;
    });
  }
}

init();
