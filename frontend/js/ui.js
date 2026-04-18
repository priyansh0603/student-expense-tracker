// frontend/js/ui.js — Shared helpers

// ── Format ──
const fmt = amt => '₹' + Math.abs(Number(amt)).toLocaleString('en-IN', {minimumFractionDigits:0, maximumFractionDigits:2});
const fmtDate = s => { const d = new Date(s+'T00:00:00'); return d.toLocaleDateString('en-IN',{day:'numeric',month:'short'}); };
const monthLabel = s => { if(!s) return ''; const [y,m] = s.split('-'); return new Date(y,m-1,1).toLocaleDateString('en-IN',{month:'long',year:'numeric'}); };
const getInitials = n => n.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2);
const catIcon = {Food:'🍔',Travel:'🚌',Fun:'🎮',Other:'📦',Income:'💰'};
const getCatIcon = (cat,type) => type==='income' ? '💰' : (catIcon[cat]||'📦');

// ── Month math ──
let currentMonth = new Date().toISOString().slice(0,7);
const shiftMonth = (base, delta) => { const [y,m]=base.split('-').map(Number); const d=new Date(y,m-1+delta,1); return d.toISOString().slice(0,7); };

// ── Toast ──
function toast(msg, type, ms) {
  type = type||'info'; ms = ms||3000;
  let c = document.getElementById('toast-container');
  if(!c){ c=document.createElement('div'); c.id='toast-container'; document.body.appendChild(c); }
  const icons={success:'✓',error:'✕',info:'ℹ'};
  const t=document.createElement('div');
  t.className='toast '+type;
  t.innerHTML='<span>'+icons[type]+'</span><span>'+msg+'</span>';
  c.appendChild(t);
  setTimeout(function(){ t.style.opacity='0'; t.style.transform='translateY(-8px)'; setTimeout(function(){ t.remove(); },300); }, ms);
}

// ── Drawer ──
function openDrawer(id){
  var el=document.getElementById(id); if(el) el.classList.add('open');
  var ov=document.getElementById('overlay'); if(ov){ ov.classList.add('open'); ov.onclick=function(){closeDrawer(id);}; }
}
function closeDrawer(id){
  var el=document.getElementById(id); if(el) el.classList.remove('open');
  var ov=document.getElementById('overlay'); if(ov) ov.classList.remove('open');
}

// ── Page nav ──
function navigateTo(p) {
  document.querySelectorAll('.page').forEach(function(el){el.classList.remove('active');});
  document.querySelectorAll('.nav-btn[data-page]').forEach(function(el){el.classList.remove('active');});
  var pg=document.getElementById('page-'+p); if(pg) pg.classList.add('active');
  var nb=document.querySelector('.nav-btn[data-page="'+p+'"]'); if(nb) nb.classList.add('active');
  if(p==='dashboard') loadDashboard();
  else if(p==='receive')  loadReceive();
  else if(p==='pay')      loadPay();
  else if(p==='history')  loadHistory();
  else if(p==='settings') loadSettings();
}

// ── Safe-spend message ──
function spendMsg(safeDaily, avgSpend) {
  if(safeDaily<=0) return {text:'Over budget!', cls:'bad'};
  if(avgSpend > safeDaily*1.2) return {text:'Spending too fast', cls:'bad'};
  if(avgSpend > safeDaily*0.9) return {text:'Watch your spending', cls:'warn'};
  return {text:'Nice, you are on track!', cls:'good'};
}
