/* SKONGA pay auto-unlock — every user after mobile money payment
 * Include before </body>: <script src="./pay-auto-unlock.js"></script>
 */
(function(){
  function saveProFromServer(pro, orderId){
    if(!pro || !pro.active || !pro.expiresAt) return false;
    var key = (typeof PRO_STORAGE_KEY!=='undefined') ? PRO_STORAGE_KEY : 'skonga_pro';
    try{
      localStorage.setItem(key, JSON.stringify({
        planId: pro.planId,
        planName: pro.planName,
        expiresAt: pro.expiresAt,
        activatedAt: Date.now(),
        serverVerified: true,
        orderId: orderId || pro.orderId || null
      }));
    }catch(e){}
    try{ if(typeof updateSidebarProStatus==='function') updateSidebarProStatus(); }catch(e){}
    try{ if(typeof renderPayPlans==='function') renderPayPlans(); }catch(e){}
    return true;
  }
  window.saveProFromServer = saveProFromServer;

  window.pollOrderUntilPaid = async function(orderId, uid, sessionId, attempts){
    var max = attempts || 40;
    var base = (typeof API_BASE!=='undefined') ? API_BASE : '';
    for(var i=0;i<max;i++){
      await new Promise(function(r){ setTimeout(r, 3000); });
      try{
        var q = new URLSearchParams();
        if(uid) q.set('uid', uid);
        if(sessionId) q.set('sessionId', sessionId);
        var res = await fetch(base + '/api/payments/status/' + encodeURIComponent(orderId) + '?' + q.toString());
        var data = await res.json().catch(function(){ return {}; });
        if(data.pro && data.pro.active && data.pro.expiresAt){
          saveProFromServer(data.pro, orderId);
          var icon=document.getElementById('payResultIcon'); if(icon) icon.textContent='\u2705';
          var title=document.getElementById('payResultTitle'); if(title) title.textContent='Malipo yamethibitishwa';
          var sub=document.getElementById('payResultSub');
          if(sub){
            var until = new Date(data.pro.expiresAt).toLocaleString('sw-TZ',{dateStyle:'medium',timeStyle:'short'});
            sub.textContent = (data.pro.planName||'Pro') + ' \u00b7 Active until ' + until;
          }
          try{ if(typeof showToast==='function') showToast('SKONGA Pro imefunguliwa'); }catch(e){}
          return true;
        }
        if(data.order && data.order.status==='failed'){
          var t=document.getElementById('payResultTitle'); if(t) t.textContent='Malipo yameshindikana';
          return false;
        }
      }catch(e){}
    }
    try{
      var res2 = await fetch(base + '/api/payments/sync', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ orderId: orderId, sessionId: sessionId, uid: uid })
      });
      var data2 = await res2.json().catch(function(){ return {}; });
      if(data2.pro && data2.pro.active){
        saveProFromServer(data2.pro, orderId);
        var icon2=document.getElementById('payResultIcon'); if(icon2) icon2.textContent='\u2705';
        var title2=document.getElementById('payResultTitle'); if(title2) title2.textContent='Malipo yamethibitishwa';
        try{ if(typeof showToast==='function') showToast('SKONGA Pro imefunguliwa'); }catch(e){}
        return true;
      }
    }catch(e){}
    return false;
  };

  function installPatches(){
    if(typeof pollProUntilActive==='function' && !window.__skongaPayPatched){
      window.__skongaPayPatched = true;
      var orig = pollProUntilActive;
      window.pollProUntilActive = async function(uid, sessionId, attempts){
        try{
          var last = localStorage.getItem('skonga_last_order_id');
          if(last && typeof pollOrderUntilPaid==='function'){
            pollOrderUntilPaid(last, uid, sessionId, attempts||40);
          }
        }catch(e){}
        return orig(uid, sessionId, attempts);
      };
    }
    if(typeof paySubmit==='function' && !window.__skongaPaySubmitPatched){
      window.__skongaPaySubmitPatched = true;
      var origSubmit = paySubmit;
      window.paySubmit = async function(){
        var result = await origSubmit.apply(this, arguments);
        try{
          var sub = document.getElementById('payResultSub');
          var m = sub && sub.textContent && sub.textContent.match(/Ref:\s*([A-Za-z0-9]+)/);
          if(m) localStorage.setItem('skonga_last_order_id', m[1]);
        }catch(e){}
        return result;
      };
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(installPatches, 0); });
  else setTimeout(installPatches, 0);
  setTimeout(installPatches, 500);
  setTimeout(installPatches, 2000);
})();
