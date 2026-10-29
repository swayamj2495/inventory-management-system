// ============================================================
// Inventory Management System — Shared JS utilities
// ============================================================

// ── Constants ────────────────────────────────────────────────
const LOW_STOCK_THRESHOLD = 5;   // items with qty <= this are "low stock"

// ── Date formatting ──────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

// ── Status badges ─────────────────────────────────────────────
function statusBadge(status) {
  if (!status) return '<span class="badge badge-grey">—</span>';
  const s = status.toLowerCase();
  if (s === 'completed') return `<span class="badge badge-green">${status}</span>`;
  if (s === 'pending')   return `<span class="badge badge-amber">${status}</span>`;
  if (s === 'processing') return `<span class="badge badge-blue">${status}</span>`;
  if (s === 'cancelled') return `<span class="badge badge-red">${status}</span>`;
  return `<span class="badge badge-grey">${status}</span>`;
}

// ── Stock quantity display ────────────────────────────────────
function stockDisplay(qty) {
  if (qty === null || qty === undefined) return '—';
  if (qty <= 0)                  return `<span class="low-stock">0 (Out)</span>`;
  if (qty <= LOW_STOCK_THRESHOLD) return `<span class="low-stock">${qty}</span>`;
  if (qty <= LOW_STOCK_THRESHOLD * 2) return `<span class="warn-stock">${qty}</span>`;
  return qty;
}

// ── Notification helper ───────────────────────────────────────
function showNotification(el, message, type = 'success') {
  if (!el) return;
  el.className = `notification notification-${type} show`;
  const icons = {
    success: 'check-circle',
    error:   'alert-circle',
    warning: 'alert-triangle',
    info:    'info'
  };
  el.innerHTML = `<i data-lucide="${icons[type] || 'info'}"></i> ${message}`;
  lucide.createIcons({ nodes: [el] });
  // Auto-hide after 5s
  clearTimeout(el._hideTimer);
  el._hideTimer = setTimeout(() => {
    el.classList.remove('show');
  }, 5000);
}

// ── API helpers ───────────────────────────────────────────────
async function apiGet(url) {
  const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiPost(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(data)
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
  return body;
}

// ── Loading row helper ─────────────────────────────────────────
function loadingRow(colspan) {
  return `<tr class="state-row"><td colspan="${colspan}"><span class="spinner"></span> Loading…</td></tr>`;
}

function emptyRow(colspan, msg = 'No records found.') {
  return `<tr class="state-row"><td colspan="${colspan}">${msg}</td></tr>`;
}

function errorRow(colspan, msg = 'Failed to load data.') {
  return `<tr class="state-row"><td colspan="${colspan}" style="color:var(--red)">${msg}</td></tr>`;
}

