/* ═══════════════════════════════════════════════════════════════════
   FraudSentinel — main.js
   Fetches data from FastAPI backend and populates the dashboard.
   Falls back to mock data if the backend is unreachable.
   ═══════════════════════════════════════════════════════════════════ */

const API = 'http://localhost:8000/api';

// Chart.js global defaults for the dark theme
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.05)';
Chart.defaults.font.family = "'Plus Jakarta Sans', system-ui, sans-serif";

// Colour palette used by charts
const CHART_COLORS = [
  '#4e9de0', '#5cb85c', '#e89c2f', '#d9534f',
  '#5bc0de', '#9b59b6', '#1abc9c', '#e67e22',
];

// ── State ────────────────────────────────────────────────────────────────────
let fraudData   = [];
let chartBar    = null;
let chartDonut  = null;

// ── Helpers ──────────────────────────────────────────────────────────────────
const fmt = {
  currency: (n) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n),
  number:   (n) => new Intl.NumberFormat('en-US').format(n),
  pct:      (n) => `${n.toFixed(1)}%`,
  date:     (s) => s ? new Date(s).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '—',
};

async function safeFetch(endpoint) {
  try {
    const res = await fetch(`${API}/${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`[FraudSentinel] Could not reach ${endpoint}:`, err.message);
    return null;
  }
}

// ── DB Status Badge ───────────────────────────────────────────────────────────
function setDbStatus(live) {
  const dot  = document.getElementById('status-dot');
  const text = document.getElementById('db-status-text');
  if (live) {
    dot.className  = 'status-dot live';
    text.textContent = 'MongoDB Live';
  } else {
    dot.className  = 'status-dot mock';
    text.textContent = 'Mock Data';
  }
}

// ── KPI Cards ─────────────────────────────────────────────────────────────────
function renderKPIs(data) {
  document.getElementById('val-refund-loss').textContent  = fmt.currency(data.total_refund_loss);
  document.getElementById('val-total-returns').textContent = fmt.number(data.total_returns);
  document.getElementById('val-flagged').textContent       = fmt.number(data.flagged_accounts);
  document.getElementById('val-fraud-rate').textContent    = fmt.pct(data.fraud_rate_pct);
  document.getElementById('val-avg-refund').textContent    = fmt.currency(data.avg_refund_value);
  document.getElementById('val-high-risk').textContent     = fmt.number(data.high_risk_accounts);
}

function skeletonKPIs() {
  ['val-refund-loss','val-total-returns','val-flagged','val-fraud-rate','val-avg-refund','val-high-risk']
    .forEach(id => {
      const el = document.getElementById(id);
      el.textContent = '███████';
      el.classList.add('skeleton');
    });
}

function clearSkeletonKPIs() {
  ['val-refund-loss','val-total-returns','val-flagged','val-fraud-rate','val-avg-refund','val-high-risk']
    .forEach(id => document.getElementById(id).classList.remove('skeleton'));
}

// ── Bar Chart (returns by category) ──────────────────────────────────────────
function renderBarChart(categories) {
  const ctx = document.getElementById('category-chart').getContext('2d');
  const labels = categories.map(c => c.category);
  const values = categories.map(c => c.returns);

  if (chartBar) chartBar.destroy();

  chartBar = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Returns',
        data: values,
        backgroundColor: CHART_COLORS.map(c => c + '33'),
        borderColor:     CHART_COLORS,
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(37,37,38,0.97)',
          borderColor: '#3e3e42',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => ` ${fmt.number(ctx.parsed.y)} returns`,
          }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            font: { size: 11 },
            callback: (v) => fmt.number(v),
          }
        }
      }
    }
  });
}

// ── Donut Chart (refund loss share) ──────────────────────────────────────────
function renderDonutChart(categories) {
  const ctx = document.getElementById('donut-chart').getContext('2d');
  const labels = categories.map(c => c.category);
  const values = categories.map(c => c.refund_loss);
  const total  = values.reduce((a, b) => a + b, 0);

  if (chartDonut) chartDonut.destroy();

  chartDonut = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: CHART_COLORS.map(c => c + '55'),
        borderColor:     CHART_COLORS,
        borderWidth: 2,
        hoverOffset: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(37,37,38,0.97)',
          borderColor: '#3e3e42',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => {
              const pct = ((ctx.parsed / total) * 100).toFixed(1);
              return ` ${fmt.currency(ctx.parsed)} (${pct}%)`;
            }
          }
        }
      }
    }
  });

  // Custom legend
  const legend = document.getElementById('donut-legend');
  legend.innerHTML = categories.map((c, i) => `
    <div class="legend-item">
      <span class="legend-dot" style="background:${CHART_COLORS[i % CHART_COLORS.length]}"></span>
      <span>${c.category}</span>
    </div>
  `).join('');
}

// ── Category Rate Bars ────────────────────────────────────────────────────────
function renderRateBars(categories) {
  const maxRate = Math.max(...categories.map(c => c.return_rate));
  const container = document.getElementById('rate-bars');
  container.innerHTML = categories.map(c => `
    <div class="rate-row">
      <span class="rate-label" title="${c.category}">${c.category}</span>
      <div class="rate-bar-track">
        <div class="rate-bar-fill" data-pct="${(c.return_rate / maxRate) * 100}"></div>
      </div>
      <span class="rate-pct">${fmt.pct(c.return_rate)}</span>
    </div>
  `).join('');

  // Trigger animation after a tick
  requestAnimationFrame(() => {
    document.querySelectorAll('.rate-bar-fill').forEach(el => {
      el.style.width = el.dataset.pct + '%';
    });
  });
}

// ── Fraud Table ───────────────────────────────────────────────────────────────
function getRiskClass(level) {
  return level === 'High' ? 'high' : level === 'Medium' ? 'medium' : 'low';
}

function getRiskDot(level) {
  return level === 'High' ? '●' : level === 'Medium' ? '●' : '●';
}

function buildTableRow(row) {
  const rc   = getRiskClass(row.risk_level);
  const pct  = Math.min(row.risk_score, 100);

  return `
    <tr>
      <td>
        <div class="customer-cell">
          <span class="customer-name">${row.name}</span>
          <span class="customer-email">${row.email}</span>
        </div>
      </td>
      <td>${row.customer_id}</td>
      <td>${fmt.number(row.return_count)}</td>
      <td>${fmt.currency(row.total_refunds_claimed)}</td>
      <td>
        <div class="risk-score-bar">
          <div class="score-track">
            <div class="score-fill ${rc}" style="width:${pct}%"></div>
          </div>
          <span class="score-num">${row.risk_score}</span>
        </div>
      </td>
      <td>
        <span class="risk-badge ${rc}">
          ${getRiskDot(row.risk_level)} ${row.risk_level}
        </span>
      </td>
      <td>${fmt.date(row.flagged_on)}</td>
    </tr>
  `;
}

function renderTable(data) {
  fraudData = data;
  filterTable();
}

function filterTable() {
  const query      = document.getElementById('table-search').value.toLowerCase();
  const riskFilter = document.getElementById('risk-filter').value;

  const filtered = fraudData.filter(row => {
    const matchRisk   = riskFilter === 'all' || row.risk_level === riskFilter;
    const matchSearch = !query ||
      row.name.toLowerCase().includes(query) ||
      row.customer_id.toLowerCase().includes(query) ||
      row.email.toLowerCase().includes(query);
    return matchRisk && matchSearch;
  });

  const tbody = document.getElementById('fraud-tbody');
  tbody.innerHTML = filtered.length
    ? filtered.map(buildTableRow).join('')
    : '<tr><td colspan="7" style="text-align:center;color:var(--text-muted);padding:2rem;">No matching customers found.</td></tr>';

  document.getElementById('table-count').textContent =
    `Showing ${filtered.length} of ${fraudData.length} customers`;
}

// ── Timestamp ─────────────────────────────────────────────────────────────────
function updateTimestamp() {
  document.getElementById('last-updated').textContent =
    'Updated ' + new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// ── Main Load ─────────────────────────────────────────────────────────────────
async function loadDashboard() {
  // Show skeletons
  skeletonKPIs();

  // Fetch all three endpoints in parallel
  const [kpis, categories, fraud] = await Promise.all([
    safeFetch('kpis'),
    safeFetch('category-returns'),
    safeFetch('fraud-report'),
  ]);

  // Detect if backend is live (proxy: kpis returned and includes a known mock key pattern)
  // The backend itself signals via /api/kpis — we just check if data arrived
  const backendLive = kpis !== null;
  setDbStatus(backendLive);
  updateTimestamp();

  // KPIs
  clearSkeletonKPIs();
  if (kpis) renderKPIs(kpis);

  // Categories
  if (categories && categories.length) {
    renderBarChart(categories);
    renderDonutChart(categories);
    renderRateBars(categories);
  }

  // Fraud table
  if (fraud && fraud.length) {
    renderTable(fraud);
  }
}

// ── Event Listeners ───────────────────────────────────────────────────────────
document.getElementById('refresh-btn').addEventListener('click', () => {
  loadDashboard();
});

document.getElementById('table-search').addEventListener('input', filterTable);
document.getElementById('risk-filter').addEventListener('change', filterTable);

// ── SPA Tab Navigation ────────────────────────────────────────────────────────
const NAV_MAP = {
  'nav-overview':   'page-overview',
  'nav-fraud':      'page-fraud',
  'nav-categories': 'page-categories',
};

Object.entries(NAV_MAP).forEach(([navId, pageId]) => {
  document.getElementById(navId).addEventListener('click', (e) => {
    e.preventDefault();

    // Update active state on nav items
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    document.getElementById(navId).classList.add('active');

    // Hide all page sections, show the target one
    document.querySelectorAll('.page-section').forEach(sec => (sec.style.display = 'none'));
    document.getElementById(pageId).style.display = 'block';
  });
});

// ── Boot ─────────────────────────────────────────────────────────────────────
loadDashboard();
