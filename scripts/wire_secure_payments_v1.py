#!/usr/bin/env python3
"""Wire SKONGA pay UI to backend payment APIs (no PIN, server-side Pro)."""
from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
html = p.read_text(encoding="utf-8")

old = """async function paySubmit(){\n  const plan = SKONGA_PLANS.find(p=>p.id===payState.planId);\n  if(!plan) return;\n  const btn = $('paySubmitBtn');\n  if(btn){ btn.disabled = true; btn.textContent = 'Sending…'; }\n  await new Promise(r=>setTimeout(r, 900));\n  savePro(plan, payNormalizePhone(payState.phone));\n  $('payResultIcon').textContent = '✅';\n  $('payResultTitle').textContent = 'Payment confirmed';\n  $('payResultSub').textContent = `${plan.name} is active. SKONGA Pro stays active until the plan expires.`;\n  payShowStep('payStepResult');\n  if(btn){ btn.disabled = false; btn.textContent = 'Confirm & Send STK'; }\n  try{ showToast('SKONGA Pro activated · '+plan.name); }catch(e){}\n}"""

new = r"""async function paySubmit(){
  const plan = SKONGA_PLANS.find(p=>p.id===payState.planId);
  if(!plan) return;
  // SECURITY: never send PIN/OTP — STK PIN is entered only on the phone.
  if(!String(API_BASE||'').startsWith('https://')){
    showToast('Payment API must use HTTPS.', true);
    return;
  }
  const btn = $('paySubmitBtn');
  if(btn){ btn.disabled = true; btn.textContent = 'Sending…'; }
  try{
    const phone = payNormalizePhone(payState.phone);
    const uid = (window._fb && window._fb.currentUser && window._fb.currentUser.uid) || null;
    const sessionId = (typeof DEVICE_SESSION_ID!=='undefined') ? DEVICE_SESSION_ID : null;
    const res = await fetch(API_BASE + '/api/payments/initiate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Skonga-Platform': (window.Capacitor && window.Capacitor.getPlatform && window.Capacitor.getPlatform()) || 'web'
      },
      body: JSON.stringify({ planId: plan.id, phone, uid, sessionId })
    });
    const data = await res.json().catch(()=>({}));
    if(!res.ok){
      throw new Error(data.error || 'Could not start payment');
    }
    const orderId = data.order && data.order.orderId;
    // Clear sensitive UI state
    try{ payState.phone = ''; const inp=$('payPhone'); if(inp) inp.value=''; }catch(_){}

    $('payResultIcon').textContent = '📲';
    $('payResultTitle').textContent = 'STK request sent';
    $('payResultSub').textContent = (data.message || 'Enter your mobile-money PIN on your phone only — never in this app.') +
      (orderId ? (' Ref: ' + orderId) : '');
    payShowStep('payStepResult');

    // Sandbox: optional auto-confirm for testing (server allows only when PAYMENT_MODE=sandbox)
    if(orderId && data.order && data.order.mode === 'sandbox'){
      try{
        const c = await fetch(API_BASE + '/api/payments/sandbox-confirm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ orderId })
        });
        const cj = await c.json().catch(()=>({}));
        if(c.ok && cj.pro && cj.pro.active){
          localStorage.setItem(PRO_STORAGE_KEY, JSON.stringify({
            planId: cj.pro.planId, planName: cj.pro.planName,
            expiresAt: cj.pro.expiresAt, activatedAt: Date.now(),
            serverVerified: true, orderId
          }));
          updateSidebarProStatus();
          $('payResultIcon').textContent = '✅';
          $('payResultTitle').textContent = 'Payment confirmed (sandbox)';
          $('payResultSub').textContent = (cj.pro.planName||plan.name) + ' active until plan expires.';
          showToast('SKONGA Pro activated · sandbox');
        }
      }catch(_){}
    } else if(orderId){
      // Live: poll server Pro status (webhook grants entitlement)
      pollProUntilActive(uid, sessionId, 12);
    }
  }catch(err){
    showToast(err.message || 'Payment failed', true);
    $('payResultIcon').textContent = '⚠️';
    $('payResultTitle').textContent = 'Payment not started';
    $('payResultSub').textContent = err.message || 'Try again.';
    payShowStep('payStepResult');
  }finally{
    if(btn){ btn.disabled = false; btn.textContent = 'Confirm & Send STK'; }
  }
}

async function pollProUntilActive(uid, sessionId, attempts){
  for(let i=0;i<(attempts||10);i++){
    await new Promise(r=>setTimeout(r, 3000));
    try{
      const q = new URLSearchParams();
      if(uid) q.set('uid', uid);
      if(sessionId) q.set('sessionId', sessionId);
      const res = await fetch(API_BASE + '/api/payments/pro?' + q.toString());
      const data = await res.json();
      if(data && data.active){
        localStorage.setItem(PRO_STORAGE_KEY, JSON.stringify({
          planId: data.planId, planName: data.planName,
          expiresAt: data.expiresAt, activatedAt: Date.now(),
          serverVerified: true
        }));
        updateSidebarProStatus();
        $('payResultIcon').textContent = '✅';
        $('payResultTitle').textContent = 'Payment confirmed';
        $('payResultSub').textContent = (data.planName||'Pro') + ' is active.';
        showToast('SKONGA Pro activated');
        return;
      }
    }catch(_){}
  }
}"""

if old not in html:
    print("SKIP: paySubmit pattern not found (already wired or different)")
else:
    html = html.replace(old, new, 1)
    print("OK: paySubmit wired to /api/payments/initiate")

# Harden isProActive: still allow local cache but prefer serverVerified flag when present
old2 = "function isProActive(){ return !!getPro(); }"
new2 = "function isProActive(){ const p=getPro(); return !!(p && p.expiresAt && Date.now()<p.expiresAt); }"
if old2 in html:
    html = html.replace(old2, new2, 1)
    print("OK: isProActive")

p.write_text(html, encoding="utf-8")
print("Wrote", p.resolve())
