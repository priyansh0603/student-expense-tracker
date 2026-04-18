// frontend/js/api.js — All API calls to Flask backend
var API = {
  _req: async function(method, path, body) {
    var opts = { method: method, headers: {'Content-Type':'application/json'}, credentials:'same-origin' };
    if (body) opts.body = JSON.stringify(body);
    var res = await fetch('/api' + path, opts);
    var data = await res.json().catch(function(){ return {}; });
    return { ok: res.ok, status: res.status, data: data };
  },
  auth: {
    status:              function()        { return API._req('GET',  '/auth/status'); },
    register:            function(u,p,q,a) { return API._req('POST', '/auth/register',         {username:u, password:p, security_question:q, security_answer:a}); },
    login:               function(u,p)     { return API._req('POST', '/auth/login',             {username:u, password:p}); },
    logout:              function()        { return API._req('POST', '/auth/logout'); },
    getSecurityQuestion: function(u)       { return API._req('POST', '/auth/security-question', {username:u}); },
    resetPassword:       function(u,a,np)  { return API._req('POST', '/auth/reset-password',    {username:u, security_answer:a, new_password:np}); },
    changePassword:      function(op,np)   { return API._req('POST', '/auth/change-password',   {old_password:op, new_password:np}); },
  },
  transactions: {
    dashboard: function(m)     { return API._req('GET',    '/transactions/dashboard'+(m?'?month='+m:'')); },
    list:      function(m,lim) {
      var q=[]; if(m) q.push('month='+m); if(lim) q.push('limit='+lim);
      return API._req('GET', '/transactions/'+(q.length?'?'+q.join('&'):''));
    },
    add:       function(d)     { return API._req('POST',   '/transactions/', d); },
    delete:    function(id)    { return API._req('DELETE', '/transactions/'+id); },
  },
  friends: {
    receive:     function(m)    { return API._req('GET',    '/friends/receive'+(m?'?month='+m:'')); },
    pay:         function(m)    { return API._req('GET',    '/friends/pay'+(m?'?month='+m:'')); },
    add:         function(d)    { return API._req('POST',   '/friends/', d); },
    addPayment:  function(id,a) { return API._req('POST',   '/friends/'+id+'/payment', {amount:a}); },
    markComplete:function(id)   { return API._req('POST',   '/friends/'+id+'/complete'); },
    update:      function(id,d) { return API._req('PUT',    '/friends/'+id, d); },
    delete:      function(id)   { return API._req('DELETE', '/friends/'+id); },
  },
  backup: {
    list:   function()  { return API._req('GET',  '/backup/'); },
    create: function(m) { return API._req('POST', '/backup/create', m?{month:m}:{}); },
  }
};
