#!/usr/bin/env python3
"""Fix Pro Continue (Android WebView) + add Light/Dark/Auto in Settings."""
from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
html = p.read_text(encoding="utf-8")
n = 0

# ── 1) Theme UI in Settings (logic already exists: applyTheme / setThemeSeg) ──
THEME_UI = '''
      <div class="setting-row">
        <div class="setting-label">
          <div class="setting-icon si-purple"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/></svg></div>
          <div><div>Theme</div><div class="setting-desc">Light, Dark, or match system</div></div>
        </div>
        <div class="seg-ctrl" id="themeSeg">
          <button type="button" class="seg-btn active" data-val="dark" onclick="setThemeSeg(this)">Dark</button>
          <button type="button" class="seg-btn" data-val="light" onclick="setThemeSeg(this)">Light</button>
          <button type="button" class="seg-btn" data-val="auto" onclick="setThemeSeg(this)">Auto</button>
        </div>
      </div>
'''

if 'id="themeSeg"' not in html:
    anchor = '''      <div class="setting-row">
        <div class="setting-label">
          <div class="setting-icon si-cyan"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/></svg></div>
          <div><div>Response Style</div><div class="setting-desc">Response style</div></div>
        </div>
        <div class="seg-ctrl" id="styleSeg">'''
    if anchor in html:
        html = html.replace(anchor, THEME_UI + "\n" + anchor, 1)
        n += 1
        print("OK: Theme Dark/Light/Auto in Settings")
    else:
        print("SKIP: styleSeg anchor not found")
else:
    print("OK: themeSeg already in HTML")

# ── 2) Inline handlers on phone input (WebView-reliable) ──
OLD_INPUT = '<input type="tel" id="payPhone" placeholder="0742 000 000" maxlength="13" autocomplete="tel" inputmode="tel"/>'
NEW_INPUT = (
    '<input type="tel" id="payPhone" placeholder="0742 000 000" maxlength="13" '
    'autocomplete="tel" inputmode="tel" '
    'oninput="payOnPhoneInput()" onkeyup="payOnPhoneInput()" '
    'onchange="payOnPhoneInput()" onblur="payOnPhoneInput()"/>'
)
if OLD_INPUT in html:
    html = html.replace(OLD_INPUT, NEW_INPUT, 1)
    n += 1
    print("OK: inline phone handlers")
elif "oninput=\"payOnPhoneInput()\"" in html:
    print("OK: inline handlers already")
else:
    print("SKIP: payPhone input")

# ── 3) Harder enable/disable of Continue + live read from input ──
OLD_ON = '''  // Continue depends on FORMAT validity, not operator name
  if(next) next.disabled = !valid;
}'''
NEW_ON = '''  // Continue depends on FORMAT validity, not operator name
  if(next){
    if(valid){
      next.disabled = false;
      next.removeAttribute('disabled');
      next.setAttribute('aria-disabled','false');
    } else {
      next.disabled = true;
      next.setAttribute('disabled','disabled');
      next.setAttribute('aria-disabled','true');
    }
  }
}
'''
if OLD_ON in html:
    html = html.replace(OLD_ON, NEW_ON, 1)
    n += 1
    print("OK: removeAttribute disabled")
else:
    print("SKIP: disabled toggle")

OLD_GO = '''function payGoConfirm(){
  const plan = SKONGA_PLANS.find(p=>p.id===payState.planId);
  if(!plan || !payIsValidTzMobile(payState.phone)) return;
  if(!payState.network) payState.network = payDetectNetwork(payState.phone) || 'Mobile money';
'''
NEW_GO = '''function payGoConfirm(){
  // Always re-read field (Android may not have fired input yet)
  try{
    const el = document.getElementById('payPhone');
    if(el){ payState.phone = String(el.value||'').trim(); payOnPhoneInput(); }
  }catch(e){}
  const plan = SKONGA_PLANS.find(p=>p.id===payState.planId);
  if(!plan){ showToast('Choose a plan first.', true); return; }
  if(!payIsValidTzMobile(payState.phone)){ showToast('Enter a valid TZ mobile number.', true); return; }
  if(!payState.network) payState.network = payDetectNetwork(payState.phone) || 'Mobile money';
'''
if OLD_GO in html:
    html = html.replace(OLD_GO, NEW_GO, 1)
    n += 1
    print("OK: payGoConfirm live read")
else:
    print("SKIP: payGoConfirm")

# Continue button: also allow touch via explicit type + ensure not pointer-events none
OLD_BTN = '<button type="button" class="pay-btn pay-btn-primary" id="payNextFromPhone" disabled onclick="payGoConfirm()">Continue</button>'
NEW_BTN = '<button type="button" class="pay-btn pay-btn-primary" id="payNextFromPhone" disabled onclick="payGoConfirm()" ontouchend="event.preventDefault();payGoConfirm()">Continue</button>'
if OLD_BTN in html:
    html = html.replace(OLD_BTN, NEW_BTN, 1)
    n += 1
    print("OK: touchend on Continue")

# Light-mode polish for pay sheet if missing
if '[data-theme="light"] .pay-btn-primary' not in html:
    css = '''
[data-theme="light"] .pay-sheet{background:var(--bg-card);color:var(--text-primary)}
[data-theme="light"] .pay-btn-primary:disabled{opacity:.45}
'''
    html = html.replace('</style>', css + '</style>', 1)
    n += 1
    print("OK: light pay CSS")

p.write_text(html, encoding="utf-8")
print(f"Done replacements={n} → {p.resolve()}")
