#!/usr/bin/env python3
"""
SKONGA AI v1.2 — production UI:
  - In-app payment panel (plans + phone + confirm, neon dark, no page restart)
  - Plans: Siku 620 / Wiki 3500 / Mwezi 5000 / Mwaka 45000
  - Terms & Privacy real modals
  - Settings + Profile moved to bottom of history sidebar
  - Upgrade card at top of sidebar (after New Chat)
  - Pro subscription unlocks continued chat after free limit (client-side)
  - User-facing only (no backend/dev controls in pay UI)

Run from repo root:
  python3 scripts/apply_v1_2.py
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
path = root / "www" / "index.html"
if not path.exists():
    sys.exit(f"Missing {path}")

text = path.read_text(encoding="utf-8")
if "id=\"paySheet\"" in text and "SKONGA_PLANS" in text:
    print("Already applied v1.2.")
    sys.exit(0)

pay_css = """
/* ── PAY SHEET (in-app, no navigation restart) ── */
#paySheet .sheet{max-height:92vh}
.pay-step{display:none}
.pay-step.active{display:block}
.pay-plans{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0 16px}
.pay-plan{
  background:var(--bg-elevated);border:1.5px solid var(--border);border-radius:14px;
  padding:14px 12px;cursor:pointer;text-align:left;transition:border-color .15s,box-shadow .15s;position:relative
}
.pay-plan:hover{border-color:rgba(168,85,247,.45)}
.pay-plan.selected{border-color:var(--purple-light);box-shadow:0 0 0 1px rgba(168,85,247,.35),0 0 18px rgba(124,58,237,.2)}
.pay-plan-name{font-size:.88rem;font-weight:600;color:var(--text-primary);margin-bottom:4px}
.pay-plan-price{font-family:var(--font-brand);font-size:1.05rem;color:var(--purple-light);letter-spacing:.02em}
.pay-plan-tag{
  position:absolute;top:8px;right:8px;font-size:.62rem;font-weight:600;padding:2px 7px;border-radius:99px;
  background:rgba(124,58,237,.2);color:var(--purple-glow)
}
.pay-plan-sub{font-size:.68rem;color:var(--text-muted);margin-top:4px}
.pay-field{margin-bottom:14px}
.pay-field label{display:block;font-size:.72rem;color:var(--text-muted);margin-bottom:6px;letter-spacing:.04em}
.pay-field input{
  width:100%;background:var(--bg-elevated);border:1.5px solid var(--border);border-radius:12px;
  color:var(--text-primary);font-family:var(--font-b);font-size:.95rem;padding:12px 14px;outline:none
}
.pay-field input:focus{border-color:var(--purple-main)}
.pay-net-badge{font-size:.72rem;color:var(--green);margin-top:6px;min-height:18px}
.pay-actions{display:flex;gap:10px;margin-top:8px}
.pay-btn{
  flex:1;padding:13px;border:none;border-radius:12px;font-family:var(--font-b);font-size:.9rem;font-weight:600;cursor:pointer
}
.pay-btn-primary{background:linear-gradient(135deg,var(--purple-main),var(--purple-glow));color:#fff}
.pay-btn-primary:disabled{opacity:.4;cursor:not-allowed}
.pay-btn-ghost{background:var(--bg-elevated);color:var(--text-secondary);border:1px solid var(--border)}
.pay-summary{
  background:var(--bg-elevated);border:1px solid var(--border);border-radius:14px;padding:14px;margin-bottom:14px
}
.pay-summary .row{display:flex;justify-content:space-between;font-size:.82rem;padding:6px 0;color:var(--text-secondary)}
.pay-summary .row strong{color:var(--text-primary);font-weight:600}
.pay-hint{font-size:.72rem;color:var(--text-muted);line-height:1.45;margin:8px 0 4px}
.pay-result{text-align:center;padding:12px 8px}
.pay-result-icon{font-size:2.2rem;margin-bottom:8px}
.pay-result-title{font-size:1rem;font-weight:600;margin-bottom:6px}
.pay-result-sub{font-size:.8rem;color:var(--text-secondary);line-height:1.45}

.sidebar-footer{
  flex-shrink:0;display:flex;gap:8px;padding:10px 12px 14px;border-top:1px solid var(--border);
  background:var(--bg-secondary)
}
.sidebar-footer-btn{
  flex:1;display:flex;align-items:center;justify-content:center;gap:8px;
  padding:11px 10px;border-radius:12px;border:1px solid var(--border);
  background:var(--bg-elevated);color:var(--text-secondary);font-size:.78rem;font-weight:500;cursor:pointer
}
.sidebar-footer-btn:active{opacity:.85}
.sidebar-footer-btn svg{width:16px;height:16px;flex-shrink:0}
.sidebar-upgrade{margin:8px 10px 4px}

.legal-body{font-size:.8rem;color:var(--text-secondary);line-height:1.55;padding:4px 2px 20px;max-height:60vh;overflow-y:auto}
.legal-body h3{color:var(--text-primary);font-size:.88rem;margin:14px 0 6px}
.legal-body p{margin-bottom:8px}
"""

if "/* ── PAY SHEET" not in text:
    text = text.replace("</style>", pay_css + "\n</style>", 1)

old_header_btns = """  <div style=\"display:flex;gap:6px;align-items:center\">
    <button class=\"hbtn\" id=\"settingsBtn\" aria-label=\"Settings\">
      <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z\"/></svg>
    </button>
    <button class=\"hbtn\" id=\"profileBtn\" aria-label=\"Profile\" style=\"padding:0\">
      <div class=\"hbtn-avatar\" id=\"headerAvatar\">?</div>
    </button>
  </div>"""
new_header_btns = """  <div style=\"width:40px\"></div>"""
if old_header_btns in text:
    text = text.replace(old_header_btns, new_header_btns, 1)
else:
    text = re.sub(
        r'<button class=\"hbtn\" id=\"settingsBtn\"[^>]*>.*?</button>\s*',
        '',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<button class=\"hbtn\" id=\"profileBtn\"[^>]*>.*?</button>',
        '',
        text,
        count=1,
        flags=re.S,
    )

old_sidebar = """  <div class=\"sidebar-new\" id=\"exportCodeZipBtn\" style=\"border-bottom:1px solid var(--border)\">
    <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4\"/><polyline points=\"7 10 12 15 17 10\"/><line x1=\"12\" y1=\"15\" x2=\"12\" y2=\"3\"/></svg>
    Download All Code (ZIP)
  </div>
  <div class=\"sidebar-section\">Today</div>
  <div class=\"chat-hist-list\" id=\"chatHistList\"></div>
  <div class=\"sidebar-upgrade\" id=\"sidebarUpgrade\">
    <div class=\"sidebar-upgrade-title\">💜 SKONGA Pro</div>
    <p class=\"sidebar-upgrade-desc\">Umefikia kikomo? Lipa kwa M-Pesa, Tigo, Airtel au Halo — endelea bila kulazimishwa.</p>
    <button type=\"button\" class=\"sidebar-upgrade-btn\" onclick=\"openSkongaPay()\">Lipa sasa</button>
  </div>
</div>"""

new_sidebar = """  <div class=\"sidebar-new\" id=\"exportCodeZipBtn\" style=\"border-bottom:1px solid var(--border)\">
    <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4\"/><polyline points=\"7 10 12 15 17 10\"/><line x1=\"12\" y1=\"15\" x2=\"12\" y2=\"3\"/></svg>
    Download All Code (ZIP)
  </div>
  <div class=\"sidebar-upgrade\" id=\"sidebarUpgrade\">
    <div class=\"sidebar-upgrade-title\">💜 SKONGA Pro</div>
    <p class=\"sidebar-upgrade-desc\" id=\"sidebarProStatus\">Chagua kifurushi — lipa kwa M-Pesa, Tigo, Airtel au Halo.</p>
    <button type=\"button\" class=\"sidebar-upgrade-btn\" onclick=\"openSkongaPay()\">Angalia bei / Lipa</button>
  </div>
  <div class=\"sidebar-section\">Today</div>
  <div class=\"chat-hist-list\" id=\"chatHistList\"></div>
  <div class=\"sidebar-footer\">
    <button type=\"button\" class=\"sidebar-footer-btn\" id=\"sidebarProfileBtn\" onclick=\"openProfile();closeSidebar()\">
      <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>
      Profile
    </button>
    <button type=\"button\" class=\"sidebar-footer-btn\" id=\"sidebarSettingsBtn\" onclick=\"openSettings();closeSidebar()\">
      <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4\"/></svg>
      Settings
    </button>
  </div>
</div>"""

if old_sidebar in text:
    text = text.replace(old_sidebar, new_sidebar, 1)
else:
    print("WARN: exact sidebar block not found — trying partial")

if "Terms of Service not set up yet" in text:
    text = re.sub(
        r"<!-- ═══ TODO: Terms & Conditions[\s\S]*?Privacy Policy not set up yet — TODO\.'\)\" style=\"cursor:pointer\">[\s\S]*?</div>\s*</div>\s*</div>",
        """    <div class=\"settings-section\">
      <div class=\"settings-section-label\">About & Legal</div>
      <div class=\"setting-row\" onclick=\"openLegalModal('terms')\" style=\"cursor:pointer\">
        <div class=\"setting-label\">
          <div class=\"setting-icon si-purple\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\"><path d=\"M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z\"/><polyline points=\"14 2 14 8 20 8\"/></svg></div>
          <div><div>Terms of Service</div><div class=\"setting-desc\">Sheria na masharti ya matumizi</div></div>
        </div>
      </div>
      <div class=\"setting-row\" onclick=\"openLegalModal('privacy')\" style=\"cursor:pointer\">
        <div class=\"setting-label\">
          <div class=\"setting-icon si-purple\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\"><path d=\"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z\"/></svg></div>
          <div><div>Privacy Policy</div><div class=\"setting-desc\">Jinsi tunavyotunza data yako</div></div>
        </div>
      </div>
    </div>""",
        text,
        count=1,
    )

panels_html = r'''
<!-- ═══ PAY SHEET (in-app — no full-page restart) ═══ -->
<div class="sheet-overlay hidden" id="paySheet">
  <div class="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-hdr">
      <span class="sheet-title">💜 SKONGA PRO</span>
      <button class="sheet-close" id="payClose" aria-label="Funga"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="pay-step active" id="payStepPlans">
      <p class="pay-hint">Chagua kifurushi. Baada ya malipo, ujumbe wa ziada unafunguliwa kwa muda wa kifurushi.</p>
      <div class="pay-plans" id="payPlansGrid"></div>
      <div class="pay-actions">
        <button type="button" class="pay-btn pay-btn-primary" id="payNextFromPlans" disabled onclick="payGoPhone()">Endelea</button>
      </div>
    </div>
    <div class="pay-step" id="payStepPhone">
      <div class="pay-field">
        <label>Nambari ya simu (M-Pesa / Tigo / Airtel / Halo)</label>
        <input type="tel" id="payPhone" placeholder="0742 000 000" maxlength="13" autocomplete="tel" inputmode="tel"/>
        <div class="pay-net-badge" id="payNetBadge"></div>
      </div>
      <p class="pay-hint">STK Push itatumwa kwenye simu hii. PIN ya mtandao inaingizwa <strong>kwenye simu yako</strong> — si ndani ya app (usalama).</p>
      <div class="pay-actions">
        <button type="button" class="pay-btn pay-btn-ghost" onclick="payGoPlans()">Rudi</button>
        <button type="button" class="pay-btn pay-btn-primary" id="payNextFromPhone" disabled onclick="payGoConfirm()">Endelea</button>
      </div>
    </div>
    <div class="pay-step" id="payStepConfirm">
      <div class="pay-summary" id="paySummary"></div>
      <p class="pay-hint">Thibitisha, kisha thibitisha malipo kwenye simu yako (PIN ya M-Pesa/Tigo/Airtel/Halo).</p>
      <div class="pay-actions">
        <button type="button" class="pay-btn pay-btn-ghost" onclick="payGoPhone()">Rudi</button>
        <button type="button" class="pay-btn pay-btn-primary" id="paySubmitBtn" onclick="paySubmit()">Thibitisha & Tuma STK</button>
      </div>
    </div>
    <div class="pay-step" id="payStepResult">
      <div class="pay-result">
        <div class="pay-result-icon" id="payResultIcon">📲</div>
        <div class="pay-result-title" id="payResultTitle">STK imetumwa</div>
        <div class="pay-result-sub" id="payResultSub">Ingiza PIN kwenye simu yako ili kukamilisha.</div>
      </div>
      <div class="pay-actions">
        <button type="button" class="pay-btn pay-btn-ghost" onclick="closeSkongaPay()">Funga</button>
        <button type="button" class="pay-btn pay-btn-primary" onclick="payGoPlans()">Jaribu tena</button>
      </div>
    </div>
  </div>
</div>
<div class="sheet-overlay hidden" id="legalSheet">
  <div class="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-hdr">
      <span class="sheet-title" id="legalTitle">Masharti</span>
      <button class="sheet-close" id="legalClose" aria-label="Funga"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="legal-body" id="legalBody"></div>
  </div>
</div>
'''

if 'id="paySheet"' not in text:
    text = text.replace("</body>", panels_html + "\n</body>", 1)

pay_js = r'''
const SKONGA_PLANS = [
  { id:'day',   name:'Siku 1',  price:620,   days:1,   tag:'Jaribio',  sub:'Masaa 24' },
  { id:'week',  name:'Wiki 1',  price:3500,  days:7,   tag:'Maarufu',  sub:'Siku 7' },
  { id:'month', name:'Mwezi 1', price:5000,  days:30,  tag:'Bora',     sub:'Siku 30' },
  { id:'year',  name:'Mwaka 1', price:45000, days:365, tag:'Akiba',    sub:'Siku 365' },
];
const PRO_STORAGE_KEY = 'skonga_pro';
let payState = { planId:null, phone:'', network:null };

function getPro(){
  try{
    const p = JSON.parse(localStorage.getItem(PRO_STORAGE_KEY)||'null');
    if(!p || !p.expiresAt) return null;
    if(Date.now() >= p.expiresAt){ localStorage.removeItem(PRO_STORAGE_KEY); return null; }
    return p;
  }catch(e){ return null; }
}
function isProActive(){ return !!getPro(); }
function savePro(plan, phone){
  const expiresAt = Date.now() + (plan.days * 24 * 60 * 60 * 1000);
  localStorage.setItem(PRO_STORAGE_KEY, JSON.stringify({
    planId: plan.id, planName: plan.name, price: plan.price,
    phone, expiresAt, activatedAt: Date.now()
  }));
  updateSidebarProStatus();
}
function updateSidebarProStatus(){
  const el = $('sidebarProStatus');
  if(!el) return;
  const p = getPro();
  if(p){
    const left = Math.max(0, Math.ceil((p.expiresAt - Date.now())/86400000));
    el.textContent = `Pro hai · ${p.planName} · siku ${left} zimebaki`;
  } else {
    el.textContent = 'Chagua kifurushi — lipa kwa M-Pesa, Tigo, Airtel au Halo.';
  }
}

function openSkongaPay(){
  try{ closeSidebar(); }catch(e){}
  payState = { planId:null, phone:'', network:null };
  renderPayPlans();
  payShowStep('payStepPlans');
  const next = $('payNextFromPlans');
  if(next) next.disabled = true;
  $('paySheet').classList.remove('hidden');
}
function closeSkongaPay(){
  $('paySheet').classList.add('hidden');
}
function payShowStep(id){
  document.querySelectorAll('#paySheet .pay-step').forEach(s=>s.classList.remove('active'));
  const el = $(id);
  if(el) el.classList.add('active');
}
function renderPayPlans(){
  const grid = $('payPlansGrid');
  if(!grid) return;
  grid.innerHTML = SKONGA_PLANS.map(p=>`
    <button type="button" class="pay-plan${payState.planId===p.id?' selected':''}" data-plan="${p.id}" onclick="paySelectPlan('${p.id}')">
      <span class="pay-plan-tag">${p.tag}</span>
      <div class="pay-plan-name">${p.name}</div>
      <div class="pay-plan-price">TSh ${p.price.toLocaleString('sw')}</div>
      <div class="pay-plan-sub">${p.sub}</div>
    </button>
  `).join('');
}
function paySelectPlan(id){
  payState.planId = id;
  renderPayPlans();
  const btn = $('payNextFromPlans');
  if(btn) btn.disabled = false;
}
function payGoPlans(){ payShowStep('payStepPlans'); }
function payGoPhone(){
  if(!payState.planId) return;
  payShowStep('payStepPhone');
  const inp = $('payPhone');
  if(inp){ inp.focus(); payOnPhoneInput(); }
}
function payDetectNetwork(phone){
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
    badge.textContent = net ? `Mtandao: ${net} ✓` : (inp.value.length>=9 ? 'Nambari haitambuliki' : '');
    badge.style.color = net ? 'var(--green)' : 'var(--red)';
  }
  const ok = !!net && /^255\d{9}$/.test(payNormalizePhone(inp.value));
  if(next) next.disabled = !ok;
}
function payGoConfirm(){
  const plan = SKONGA_PLANS.find(p=>p.id===payState.planId);
  if(!plan || !payState.network) return;
  const sum = $('paySummary');
  if(sum){
    sum.innerHTML = `
      <div class="row"><span>Kifurushi</span><strong>${plan.name}</strong></div>
      <div class="row"><span>Bei</span><strong>TSh ${plan.price.toLocaleString('sw')}</strong></div>
      <div class="row"><span>Simu</span><strong>${payNormalizePhone(payState.phone)}</strong></div>
      <div class="row"><span>Mtandao</span><strong>${payState.network}</strong></div>`;
  }
  payShowStep('payStepConfirm');
}
async function paySubmit(){
  const plan = SKONGA_PLANS.find(p=>p.id===payState.planId);
  if(!plan) return;
  const btn = $('paySubmitBtn');
  if(btn){ btn.disabled = true; btn.textContent = 'Inatuma…'; }
  await new Promise(r=>setTimeout(r, 900));
  savePro(plan, payNormalizePhone(payState.phone));
  $('payResultIcon').textContent = '✅';
  $('payResultTitle').textContent = 'Malipo yamepokelewa (demo)';
  $('payResultSub').textContent = `${plan.name} imeamilishwa. SKONGA Pro itatumika hadi muda wa kifurushi uishe. Backend halisi itathibitisha STK baadaye.`;
  payShowStep('payStepResult');
  if(btn){ btn.disabled = false; btn.textContent = 'Thibitisha & Tuma STK'; }
  try{ showToast('SKONGA Pro imeamilishwa · '+plan.name); }catch(e){}
}

const LEGAL = {
  terms: {
    title: 'Masharti ya Matumizi',
    body: `<h3>1. Utangulizi</h3><p>Kwa kutumia SKONGA AI unakubali masharti haya. App hii ni msaidizi wa masomo — si badala ya mwalimu pale inapohitajika.</p><h3>2. Matumizi</h3><p>Usitumie app kwa udanganyifu au maudhui haramu chini ya sheria za Tanzania.</p><h3>3. Bure na Pro</h3><p>Kiwango cha bure kinaweza kuwa na kikomo. Pro inaongeza ufikiaji kwa muda uliolipiwa.</p><h3>4. Malipo</h3><p>Malipo: M-Pesa, Tigo, Airtel, Halo. PIN inaingizwa kwenye simu yako (STK), si ndani ya SKONGA.</p><h3>5. AI</h3><p>Majibu yanaweza kuwa na makosa — thibitisha taarifa muhimu.</p>`
  },
  privacy: {
    title: 'Sera ya Faragha',
    body: `<h3>1. Data</h3><p>Mazungumzo, mipangilio, na namba ya simu kwa malipo — si PIN.</p><h3>2. Matumizi</h3><p>Kutoa huduma na kuthibitisha malipo. Hatuziuzi data kwa watangazaji.</p><h3>3. Uhifadhi</h3><p>Baadhi ya data inahifadhiwa kwenye kifaa (localStorage).</p><h3>4. Haki</h3><p>Unaweza kufuta historia kwenye Settings.</p>`
  }
};
function openLegalModal(kind){
  const L = LEGAL[kind] || LEGAL.terms;
  $('legalTitle').textContent = L.title;
  $('legalBody').innerHTML = L.body;
  $('legalSheet').classList.remove('hidden');
}
function closeLegalModal(){ $('legalSheet').classList.add('hidden'); }

(function wirePayLegal(){
  const payClose = $('payClose');
  if(payClose) payClose.addEventListener('click', closeSkongaPay);
  const paySheet = $('paySheet');
  if(paySheet) paySheet.addEventListener('click', e=>{ if(e.target===paySheet) closeSkongaPay(); });
  const phone = $('payPhone');
  if(phone) phone.addEventListener('input', payOnPhoneInput);
  const legalClose = $('legalClose');
  if(legalClose) legalClose.addEventListener('click', closeLegalModal);
  const legalSheet = $('legalSheet');
  if(legalSheet) legalSheet.addEventListener('click', e=>{ if(e.target===legalSheet) closeLegalModal(); });
  updateSidebarProStatus();
})();
'''

if "function openSkongaPay()" in text:
    text = re.sub(
        r"function openSkongaPay\(\)\s*\{[^}]*\}",
        "function openSkongaPay(){ /* v1.2 impl below */ }",
        text,
        count=1,
    )

if "function showUpgradeCard" in text and "isProActive" not in text:
    text = text.replace(
        "function showUpgradeCard(originalText){",
        "function showUpgradeCard(originalText){\n  if(typeof isProActive==='function' && isProActive()){\n    try{ showToast('Pro hai — jaribu tena baada ya sekunde chache.'); }catch(e){}\n    return;\n  }",
        1,
    )

text = text.replace(
    "$('settingsBtn').addEventListener('click', openSettings);",
    "if($('settingsBtn')) $('settingsBtn').addEventListener('click', openSettings);",
)
text = text.replace(
    "$('profileBtn').addEventListener('click', openProfile);",
    "if($('profileBtn')) $('profileBtn').addEventListener('click', openProfile);",
)

if "SKONGA_PLANS" not in text:
    idx = text.rfind("</script>")
    if idx == -1:
        sys.exit("No </script> found")
    text = text[:idx] + "\n" + pay_js + "\n" + text[idx:]

text = text.replace("const APP_VERSION = '1.0';", "const APP_VERSION = '1.2';", 1)
if "v1.2" not in text[text.find("CHANGELOG"):text.find("CHANGELOG")+500]:
    text = text.replace(
        "const CHANGELOG = [",
        """const CHANGELOG = [
  { version:'1.2', date:'August 2026', items:[
    'SKONGA Pro plans: Siku 620, Wiki 3,500, Mwezi 5,000, Mwaka 45,000 — in-app pay panel.',
    'Terms of Service & Privacy Policy inside the app.',
    'Profile & Settings at bottom of history sidebar; Upgrade at top.',
    'Pro unlocks continued access after free limit (client-side until backend billing).'
  ]},""",
        1,
    )

path.write_text(text, encoding="utf-8")
checks = {
    "paySheet": 'id="paySheet"' in text,
    "SKONGA_PLANS": "SKONGA_PLANS" in text,
    "sidebar-footer": "sidebar-footer" in text,
    "openLegalModal": "openLegalModal" in text,
    "APP 1.2": "APP_VERSION = '1.2'" in text,
}
for k, v in checks.items():
    print(("OK" if v else "FAIL"), k)
print("Done.")
