// frontend/js/friends.js — receive / pay / friend flows (recovered; mirrors index.html inline script)

async function loadReceive() {
  var res = await API.friends.receive();
  if (!res.ok) return;
  document.getElementById('recv-total').textContent = fmt(res.data.total_to_receive);
  renderFL('recv-list', res.data.transactions, 'receive');
}

async function loadPay() {
  var res = await API.friends.pay();
  if (!res.ok) return;
  document.getElementById('pay-total').textContent = fmt(res.data.total_to_pay);
  renderFL('pay-list', res.data.transactions, 'pay');
}

function renderFL(cid, txs, type) {
  var c = document.getElementById(cid);
  if (!txs || !txs.length) {
    c.innerHTML =
      '<div class="empty-state"><div class="empty-state-icon">' +
      (type === 'receive' ? '🤝' : '💸') +
      '</div><p>No entries yet.<br>Tap + Add to create one.</p></div>';
    return;
  }
  var pend = txs.filter(function (t) {
    return t.status === 'pending';
  });
  var done = txs.filter(function (t) {
    return t.status === 'completed';
  });
  var html = '';
  if (pend.length)
    html +=
      '<div class="section-hd-title" style="margin:4px 0 10px">Pending (' +
      pend.length +
      ')</div>' +
      pend
        .map(function (t) {
          return fcCard(t, type);
        })
        .join('');
  if (done.length)
    html +=
      '<div class="section-hd-title" style="margin:16px 0 10px;color:var(--green)">Completed (' +
      done.length +
      ')</div>' +
      done
        .map(function (t) {
          return fcCard(t, type);
        })
        .join('');
  c.innerHTML = html;
  c.querySelectorAll('[data-fc-action]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      fcAction(btn.dataset.fcAction, parseInt(btn.dataset.fcId, 10), type);
    });
  });
}

function fcCard(t, type) {
  var pct = t.total_amount > 0 ? Math.min(100, (t.paid_amount / t.total_amount) * 100) : 0;
  var done = t.status === 'completed';
  var acts = done
    ? '<button class="btn btn-muted btn-sm" data-fc-action="delete" data-fc-id="' + t.id + '">🗑 Remove</button>'
    : type === 'receive'
      ? '<button class="btn btn-green btn-sm" data-fc-action="payment" data-fc-id="' +
        t.id +
        '">+ Received</button><button class="btn btn-primary btn-sm" data-fc-action="complete" data-fc-id="' +
        t.id +
        '">✓ Got All</button><button class="btn btn-muted btn-sm" data-fc-action="delete" data-fc-id="' +
        t.id +
        '">🗑</button>'
      : '<button class="btn btn-yellow btn-sm" data-fc-action="payment" data-fc-id="' +
        t.id +
        '">+ Paid</button><button class="btn btn-primary btn-sm" data-fc-action="complete" data-fc-id="' +
        t.id +
        '">✓ Paid All</button><button class="btn btn-muted btn-sm" data-fc-action="delete" data-fc-id="' +
        t.id +
        '">🗑</button>';
  return (
    '<div class="friend-card"><div class="fc-header"><div class="fc-who"><div class="fc-avatar">' +
    getInitials(t.friend_name) +
    '</div><div><div class="fc-name">' +
    t.friend_name +
    '</div><div class="fc-date">' +
    fmtDate(t.date) +
    '</div>' +
    (t.description ? '<div class="fc-desc">' + t.description + '</div>' : '') +
    '</div></div><span class="fc-status ' +
    t.status +
    '">' +
    t.status +
    '</span></div><div class="fc-amounts"><div class="fc-amt"><div class="fc-amt-label">Total</div><div class="fc-amt-val total">' +
    fmt(t.total_amount) +
    '</div></div><div class="fc-amt"><div class="fc-amt-label">' +
    (type === 'receive' ? 'Received' : 'Paid') +
    '</div><div class="fc-amt-val paid">' +
    fmt(t.paid_amount) +
    '</div></div><div class="fc-amt"><div class="fc-amt-label">Left</div><div class="fc-amt-val ' +
    (done ? 'done' : 'remaining') +
    '">' +
    (done ? '✓ Done' : fmt(t.remaining_amount)) +
    '</div></div></div><div class="fc-progress"><div class="fc-progress-fill" style="width:' +
    pct +
    '%"></div></div><div class="fc-actions">' +
    acts +
    '</div></div>'
  );
}

var _pendPayId = null,
  _pendPayType = null;

function fcAction(action, id, type) {
  if (action === 'complete') {
    API.friends.markComplete(id).then(function (r) {
      if (r.data.success) {
        toast('Marked complete!', 'success');
        if (type === 'receive') loadReceive();
        else loadPay();
      } else toast(r.data.error || 'Error', 'error');
    });
  } else if (action === 'payment') {
    _pendPayId = id;
    _pendPayType = type;
    document.getElementById('pay-drawer-title').textContent =
      type === 'receive' ? '💰 Record Money Received' : '💸 Record Payment Made';
    document.getElementById('pay-drawer-amt').value = '';
    openDrawer('pay-drawer');
    setTimeout(function () {
      document.getElementById('pay-drawer-amt').focus();
    }, 300);
  } else if (action === 'delete') {
    if (!confirm('Delete this entry?')) return;
    API.friends.delete(id).then(function () {
      toast('Removed', 'info');
      if (type === 'receive') loadReceive();
      else loadPay();
    });
  }
}

document.getElementById('pay-drawer-confirm').addEventListener('click', async function () {
  var a = parseFloat(document.getElementById('pay-drawer-amt').value);
  if (!a || a <= 0) {
    toast('Enter valid amount', 'error');
    return;
  }
  var res = await API.friends.addPayment(_pendPayId, a);
  if (res.data.success) {
    closeDrawer('pay-drawer');
    toast(
      res.data.status === 'completed'
        ? 'Fully settled! 🎉'
        : fmt(a) + ' recorded. Left: ' + fmt(res.data.remaining),
      'success'
    );
    if (_pendPayType === 'receive') loadReceive();
    else loadPay();
  } else toast(res.data.error || 'Error', 'error');
});

var _fdType = 'pay';

function openFriendDrawer(type) {
  _fdType = type;
  document.getElementById('friend-drawer-title').textContent =
    type === 'receive' ? '💰 Add: I Will Receive' : '💸 Add: I Need to Pay';
  document.getElementById('fd-name').value = '';
  document.getElementById('fd-amt').value = '';
  document.getElementById('fd-desc').value = '';
  openDrawer('friend-drawer');
  setTimeout(function () {
    document.getElementById('fd-name').focus();
  }, 300);
}

document.getElementById('fd-confirm').addEventListener('click', async function () {
  var name = document.getElementById('fd-name').value.trim(),
    amt = parseFloat(document.getElementById('fd-amt').value),
    desc = document.getElementById('fd-desc').value.trim();
  if (!name) {
    toast('Enter friend name', 'error');
    return;
  }
  if (!amt || amt <= 0) {
    toast('Enter valid amount', 'error');
    return;
  }
  var res = await API.friends.add({ friend_name: name, amount: amt, type: _fdType, description: desc });
  if (res.data.success) {
    closeDrawer('friend-drawer');
    toast('Added ' + fmt(amt) + ' for ' + name, 'success');
    if (_fdType === 'receive') loadReceive();
    else loadPay();
  } else toast(res.data.error || 'Error', 'error');
});
