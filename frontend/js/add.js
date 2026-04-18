// frontend/js/add.js — quick add (expense / income / friend) (recovered; mirrors index.html inline script)

var _selCat = 'Food',
  _ftype = 'pay';

document.querySelectorAll('.mode-tab').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.mode-tab').forEach(function (b) {
      b.classList.remove('active');
    });
    btn.classList.add('active');
    document.querySelectorAll('.add-block').forEach(function (b) {
      b.style.display = 'none';
    });
    document.getElementById('add-' + btn.dataset.mode).style.display = 'block';
  });
});

document.querySelectorAll('.cp-btn').forEach(function (btn) {
  btn.addEventListener('click', function () {
    _selCat = btn.dataset.cat;
    document.querySelectorAll('.cp-btn').forEach(function (b) {
      b.classList.remove('active');
    });
    btn.classList.add('active');
  });
});

document.querySelectorAll('[data-ftype]').forEach(function (btn) {
  btn.addEventListener('click', function () {
    _ftype = btn.dataset.ftype;
    document.querySelectorAll('[data-ftype]').forEach(function (b) {
      b.classList.remove('active', 'pay', 'receive');
    });
    btn.classList.add('active', btn.dataset.ftype);
  });
});

document.getElementById('exp-submit').addEventListener('click', async function () {
  var a = parseFloat(document.getElementById('exp-amt').value),
    d = document.getElementById('exp-desc').value.trim();
  if (!a || a <= 0) {
    toast('Enter valid amount', 'error');
    return;
  }
  this.textContent = 'Adding...';
  this.disabled = true;
  var res = await API.transactions.add({
    type: 'expense',
    amount: a,
    category: _selCat,
    description: d || _selCat,
    date: new Date().toISOString().slice(0, 10),
  });
  this.textContent = 'Add Expense';
  this.disabled = false;
  if (res.data.success) {
    toast('-' + fmt(a) + ' added ✓', 'success');
    document.getElementById('exp-amt').value = '';
    document.getElementById('exp-desc').value = '';
    document.getElementById('exp-amt').focus();
  } else toast(res.data.error || 'Error', 'error');
});

document.getElementById('inc-submit').addEventListener('click', async function () {
  var a = parseFloat(document.getElementById('inc-amt').value),
    d = document.getElementById('inc-desc').value.trim();
  if (!a || a <= 0) {
    toast('Enter valid amount', 'error');
    return;
  }
  this.textContent = 'Adding...';
  this.disabled = true;
  var res = await API.transactions.add({
    type: 'income',
    amount: a,
    category: 'Income',
    description: d || 'Income received',
    date: new Date().toISOString().slice(0, 10),
  });
  this.textContent = 'Add Income';
  this.disabled = false;
  if (res.data.success) {
    toast('+' + fmt(a) + ' received ✓', 'success');
    document.getElementById('inc-amt').value = '';
    document.getElementById('inc-desc').value = '';
  } else toast(res.data.error || 'Error', 'error');
});

document.getElementById('fr-submit').addEventListener('click', async function () {
  var name = document.getElementById('fr-name').value.trim(),
    a = parseFloat(document.getElementById('fr-amt').value),
    d = document.getElementById('fr-desc').value.trim();
  if (!name) {
    toast('Enter friend name', 'error');
    return;
  }
  if (!a || a <= 0) {
    toast('Enter valid amount', 'error');
    return;
  }
  this.textContent = 'Adding...';
  this.disabled = true;
  var res = await API.friends.add({
    friend_name: name,
    amount: a,
    type: _ftype,
    description: d,
    date: new Date().toISOString().slice(0, 10),
  });
  this.textContent = 'Add Entry';
  this.disabled = false;
  if (res.data.success) {
    toast((_ftype === 'pay' ? 'You owe' : 'You get') + ' ' + fmt(a) + ' from ' + name, 'success');
    document.getElementById('fr-name').value = '';
    document.getElementById('fr-amt').value = '';
    document.getElementById('fr-desc').value = '';
  } else toast(res.data.error || 'Error', 'error');
});

document.getElementById('exp-amt').addEventListener('keydown', function (e) {
  if (e.key === 'Enter') document.getElementById('exp-desc').focus();
});
document.getElementById('exp-desc').addEventListener('keydown', function (e) {
  if (e.key === 'Enter') document.getElementById('exp-submit').click();
});
document.getElementById('inc-amt').addEventListener('keydown', function (e) {
  if (e.key === 'Enter') document.getElementById('inc-submit').click();
});
