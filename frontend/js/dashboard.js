// frontend/js/dashboard.js — dashboard month view (recovered; mirrors index.html inline script)

async function loadDashboard() {
  var res = await API.transactions.dashboard(currentMonth);
  if (!res.ok) return;
  var d = res.data;
  document.getElementById('dash-month-lbl').textContent = monthLabel(currentMonth);
  document.getElementById('d-income').textContent = fmt(d.total_income);
  document.getElementById('d-expense').textContent = fmt(d.total_expense);
  document.getElementById('d-balance').textContent = fmt(d.balance);
  document.getElementById('d-balance').className = 'stat-box-val ' + (d.balance >= 0 ? 'purple' : 'red');
  document.getElementById('d-days').textContent = d.days_left + 'd';
  document.getElementById('hero-safe').textContent = fmt(d.safe_daily_spend);
  document.getElementById('hero-sub').textContent = 'for ' + d.days_left + ' days remaining';
  var avg = d.days_left > 0 ? d.total_expense / Math.max(1, new Date().getDate()) : 0;
  var msg = spendMsg(d.safe_daily_spend, avg);
  var badge = document.getElementById('hero-badge');
  badge.textContent = msg.text;
  badge.className = 'hero-badge ' + msg.cls;
  if (d.friend_totals) {
    document.getElementById('d-to-receive').textContent = fmt(d.friend_totals.total_to_receive);
    document.getElementById('d-to-pay').textContent = fmt(d.friend_totals.total_to_pay);
  }
  var cats = [
    { k: 'Food', i: '🍔' },
    { k: 'Travel', i: '🚌' },
    { k: 'Fun', i: '🎮' },
    { k: 'Other', i: '📦' },
  ];
  document.getElementById('dash-cats').innerHTML = cats
    .map(function (c) {
      return (
        '<div class="cat-chip"><div class="cat-chip-icon">' +
        c.i +
        '</div><div><div class="cat-chip-name">' +
        c.k +
        '</div><div class="cat-chip-amt">' +
        fmt((d.categories && d.categories[c.k]) || 0) +
        '</div></div></div>'
      );
    })
    .join('');
  var rc = d.recent_transactions;
  if (!rc || !rc.length) {
    document.getElementById('dash-recent').innerHTML =
      '<div class="empty-state"><div class="empty-state-icon">📭</div><p>No transactions yet<br>Tap + to add one</p></div>';
    return;
  }
  document.getElementById('dash-recent').innerHTML = rc
    .map(function (tx) {
      var cls = tx.type === 'income' ? 'income' : tx.category.toLowerCase();
      return (
        '<div class="tx-row"><div class="tx-row-icon ' +
        cls +
        '">' +
        getCatIcon(tx.category, tx.type) +
        '</div><div class="tx-row-body"><div class="tx-row-desc">' +
        (tx.description || tx.category) +
        '</div><div class="tx-row-meta">' +
        tx.category +
        ' · ' +
        fmtDate(tx.date) +
        '</div></div><div class="tx-row-amount ' +
        tx.type +
        '">' +
        (tx.type === 'income' ? '+' : '-') +
        fmt(tx.amount) +
        '</div></div>'
      );
    })
    .join('');
}

document.getElementById('dash-prev').addEventListener('click', function () {
  currentMonth = shiftMonth(currentMonth, -1);
  loadDashboard();
});
document.getElementById('dash-next').addEventListener('click', function () {
  var n = shiftMonth(currentMonth, 1);
  if (n <= new Date().toISOString().slice(0, 7)) {
    currentMonth = n;
    loadDashboard();
  }
});
