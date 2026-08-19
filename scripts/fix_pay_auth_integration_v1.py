#!/usr/bin/env python3
"""
Fix Issue 1 (phone validation), Issue 2 (Pro Continue), Issue 3 (login email).
Apply: python3 scripts/fix_pay_auth_integration_v1.py www/index.html
"""
from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
html = p.read_text(encoding="utf-8")
n = 0

OLD_PHONE = r'''function payDetectNetwork(phone){
  let p = (phone||'').replace(/\s+/g,'').replace(/^\+/,'');
  if(p.startsWith('0')) p = '255'+p.slice(1);
  if(!p.startsWith('255')) p = '255'+p;
  const pre = p.slice(0,5);
  if(['25574','25575','25576'].includes(pre)) return 'M-Pesa';
  if(['25571','25565','25567'].includes(pre)) return 'Tigo Pesa';
  if(['25568','25569','25578'].includes(pre)) return 'Airtel Money';
  if(['25562'].includes(pre)) return 'HaloPesa';
  return null;
}
function payNormalizePhone(phone){
  let p = (phone||'').replace(/\s+/g,'').replace(/^\+/,'');
  if(p.startsWith('0')) p = '255'+p.slice(1);
  if(!p.startsWith('255')) p = '255'+p;
  return p;
}
function payOnPhoneInput(){
  const inp = $('payPhone');
  const badge = $('payNetBadge');
  const next = $('payNextFromPhone');
  if(!inp) return;
  const net = payDetectNetwork(inp.value);
  payState.network = net;
  payState.phone = inp.value.trim();
  if(badge){
    badge.textContent = net ? `Network: ${net} ✓` : (inp.value.length>=9 ? 'Unknown number' : '');
    badge.style.color = net ? 'var(--green)' : 'var(--red)';
  }
  const ok = !!net && /^255\d{9}$/.test(payNormalizePhone(inp.value));
  if(next) next.disabled = !ok;
}'''

NEW_PHONE = r'''/** Normalize TZ MSISDN → 255XXXXXXXXX (12 digits). */
function payNormalizePhone(phone){
  let p = String(phone||'').replace(/\s+/g,'').replace(/^\+/,'');
  if(p.startsWith('0')) p = '255'+p.slice(1);
  if(!p.startsWith('255') && /^[67]\d{8}$/.test(p)) p = '255'+p;
  if(!p.startsWith('255') && /^\d{9}$/.test(p)) p = '255'+p;
  return p;
}
/** Format validity only (Tanzania mobile: 255 + 9 digits starting 6 or 7). */
function payIsValidTzMobile(phone){
  return /^255[67]\d{8}$/.test(payNormalizePhone(phone));
}
/**
 * Operator label for UX only — NOT a gate for Continue / STK.
 * Prefix map is maintainable; unknown-but-valid numbers still pay.
 * (PSP routes STK by MSISDN; client does not need perfect MNO table.)
 */
const TZ_MM_PREFIX = {
  '25561': 'Yas',
  '25562': 'HaloPesa',
  '25563': 'Mobile',
  '25564': 'Mobile',
  '25565': 'Tigo Pesa',
  '25566': 'Yas',
  '25567': 'Tigo Pesa',
  '25568': 'Airtel Money',
  '25569': 'Airtel Money',
  '25571': 'Tigo Pesa',
  '25573': 'Mobile',
  '25574': 'M-Pesa',
  '25575': 'M-Pesa',
  '25576': 'M-Pesa',
  '25577': 'Zantel',
  '25578': 'Airtel Money',
  '25579': 'Mobile',
};
function payDetectNetwork(phone){
  if(!payIsValidTzMobile(phone)) return null;
  const p = payNormalizePhone(phone);
  const pre = p.slice(0,5);
  return TZ_MM_PREFIX[pre] || 'Mobile money';
}
function payOnPhoneInput(){
  const inp = document.getElementById('payPhone');
  const badge = document.getElementById('payNetBadge');
  const next = document.getElementById('payNextFromPhone');
  if(!inp) return;
  const raw = inp.value;
  const valid = payIsValidTzMobile(raw);
  const net = valid ? payDetectNetwork(raw) : null;
  payState.network = net;
  payState.phone = String(raw||'').trim();
  if(badge){
    if(!String(raw||'').replace(/\s+/g,'').length){
      badge.textContent = '';
    } else if(valid){
      badge.textContent = net ? ('Network: ' + net + ' ✓') : 'Valid TZ number ✓';
      badge.style.color = 'var(--green)';
    } else {
      badge.textContent = 'Enter a valid TZ mobile (e.g. 07XX XXX XXX)';
      badge.style.color = 'var(--red)';
    }
  }
  // Continue depends on FORMAT validity, not operator name
  if(next) next.disabled = !valid;
}'''

if OLD_PHONE in html:
    html = html.replace(OLD_PHONE, NEW_PHONE, 1)
    n += 1
    print('OK: phone validation + Continue gate')
else:
    print('SKIP: phone block (already patched or different)')

# payGoConfirm must not require known operator name — only valid MSISDN
OLD_CONFIRM = "if(!plan || !payState.network) return;"
NEW_CONFIRM = "if(!plan || !payIsValidTzMobile(payState.phone)) return;\n  if(!payState.network) payState.network = payDetectNetwork(payState.phone) || 'Mobile money';"
if OLD_CONFIRM in html:
    html = html.replace(OLD_CONFIRM, NEW_CONFIRM, 1)
    n += 1
    print('OK: payGoConfirm gate')
else:
    print('SKIP: payGoConfirm')

# Robust listeners: input + change + keyup (Android keyboards)
OLD_LIS = "if(phone) phone.addEventListener('input', payOnPhoneInput);"
NEW_LIS = """if(phone){
    ['input','change','keyup','blur','paste'].forEach(ev=>{
      phone.addEventListener(ev, ()=>{ try{ payOnPhoneInput(); }catch(e){} });
    });
  }"""
if OLD_LIS in html:
    html = html.replace(OLD_LIS, NEW_LIS, 1)
    n += 1
    print('OK: phone input listeners')
else:
    print('SKIP: listeners')

# Login: normalize email lowercase; keep password as typed (only strip ends)
OLD_LOGIN = """function handleLogin(){
  const email = ($('loginEmail')?.value||'').trim();
  const pass  = ($('loginPass')?.value||'').trim();"""
NEW_LOGIN = """function handleLogin(){
  const email = ($('loginEmail')?.value||'').trim().toLowerCase();
  const pass  = ($('loginPass')?.value||''); // do not alter password chars; backend trims only if needed"""
if OLD_LOGIN in html:
    html = html.replace(OLD_LOGIN, NEW_LOGIN, 1)
    n += 1
    print('OK: handleLogin email normalize')
else:
    print('SKIP: handleLogin')

OLD_REG = """function handleRegister(){
  const name  = ($('regName')?.value||'').trim();
  const email = ($('regEmail')?.value||'').trim();
  const pass  = ($('regPass')?.value||'').trim();"""
NEW_REG = """function handleRegister(){
  const name  = ($('regName')?.value||'').trim();
  const email = ($('regEmail')?.value||'').trim().toLowerCase();
  const pass  = ($('regPass')?.value||'');"""
if OLD_REG in html:
    html = html.replace(OLD_REG, NEW_REG, 1)
    n += 1
    print('OK: handleRegister email normalize')
else:
    print('SKIP: handleRegister')

# Auth module: always lowercase email in API body
OLD_SI = """async signIn(email, pass) {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: { email, password: pass },
    });"""
NEW_SI = """async signIn(email, pass) {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: { email: String(email||'').trim().toLowerCase(), password: String(pass||'') },
    });"""
if OLD_SI in html:
    html = html.replace(OLD_SI, NEW_SI, 1)
    n += 1
    print('OK: _fb.signIn normalize')
else:
    print('SKIP: _fb.signIn')

OLD_SU = """async signUp(name, email, pass) {
    const data = await api('/api/auth/signup', {
      method: 'POST',
      body: { email, password: pass, name },
    });"""
NEW_SU = """async signUp(name, email, pass) {
    const data = await api('/api/auth/signup', {
      method: 'POST',
      body: { email: String(email||'').trim().toLowerCase(), password: String(pass||''), name: String(name||'').trim() },
    });"""
if OLD_SU in html:
    html = html.replace(OLD_SU, NEW_SU, 1)
    n += 1
    print('OK: _fb.signUp normalize')
else:
    print('SKIP: _fb.signUp')

# Better login error: show server message when code unknown
OLD_ERR = "_authErr('loginErr', window._fb.err(e.code));"
NEW_ERR = "_authErr('loginErr', (window._fb.err(e.code) && e.code) ? window._fb.err(e.code) : (e.message || 'Login failed'));"
if OLD_ERR in html:
    html = html.replace(OLD_ERR, NEW_ERR, 1)
    n += 1
    print('OK: login error display')

p.write_text(html, encoding='utf-8')
print(f'Done. replacements={n} → {p.resolve()}')
