#!/usr/bin/env python3
"""
SKONGA AI v1.3 — stability + UX:
  - Fix Profile (headerAvatar null crash)
  - Pro button in header (top-right)
  - Swahili user-facing copy
  - Terms/Privacy open external browser (not in-app)
  - Hide trending skeleton when backend fails
  - Lighter animations / less jank
  - Sheets position:fixed so Clear History never leaks
  - Safe event wiring for Profile/Settings

Run: python3 scripts/apply_v1_3.py
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
path = root / "www" / "index.html"
if not path.exists():
    sys.exit(f"Missing {path}")

text = path.read_text(encoding="utf-8")
if "/* v1.3-stable */" in text:
    print("Already applied v1.3.")
    sys.exit(0)

css_extra = """
/* v1.3-stable */
.sheet-overlay{
  position:fixed!important;inset:0!important;left:0;right:0;top:0;bottom:0;
  max-width:430px;margin:0 auto;z-index:200!important;
}
.sheet-overlay.hidden{display:none!important;pointer-events:none!important}
.danger-row{position:relative;z-index:1}
.hbtn-pro{
  height:34px;padding:0 12px;border-radius:10px;border:1px solid rgba(168,85,247,.4);
  background:linear-gradient(135deg,rgba(124,58,237,.35),rgba(192,132,252,.15));
  color:var(--purple-light);font-size:.72rem;font-weight:600;cursor:pointer;
  font-family:var(--font-b);white-space:nowrap
}
.hbtn-pro:active{opacity:.85}
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}
}
.trending-section.is-empty{display:none!important}
"""
if "/* v1.3-stable */" not in text:
    text = text.replace("</style>", css_extra + "\n</style>", 1)

old_h = """  <div style=\"width:40px\"></div>
</header>"""
new_h = """  <button type=\"button\" class=\"hbtn-pro\" id=\"headerProBtn\" onclick=\"openSkongaPay()\" aria-label=\"SKONGA Pro\">Pro</button>
</header>"""
if old_h in text:
    text = text.replace(old_h, new_h, 1)
else:
    text = re.sub(
        r'<div style=\"width:40px\"></div>\s*</header>',
        '<button type=\"button\" class=\"hbtn-pro\" id=\"headerProBtn\" onclick=\"openSkongaPay()\" aria-label=\"SKONGA Pro\">Pro</button>\n</header>',
        text,
        count=1,
    )

text = text.replace(
    "<h2>Hello! I'm SKONGA AI</h2>\n      <p>How can I help you today?</p>",
    "<h2>Habari! Mimi ni SKONGA AI</h2>\n      <p>Naweza kukusaidia vipi leo?</p>",
)
text = text.replace("Today's Trending Topics", "Mada zinazovuma leo")
text = text.replace(
    "Offline Mode — showing saved chats & notes only",
    "Mode ya nje ya mtandao — historia na notes zilizohifadhiwa",
)
text = text.replace(
    'placeholder=\"Message SKONGA AI...\"',
    'placeholder=\"Andika ujumbe...\"',
)
text = text.replace("Hello! I'm SKONGA AI", "Habari! Mimi ni SKONGA AI")
text = text.replace("How can I help you today?", "Naweza kukusaidia vipi leo?")

text = text.replace("onclick=\"openLegalModal('terms')\"", "onclick=\"openExternalLegal('terms')\"")
text = text.replace("onclick=\"openLegalModal('privacy')\"", "onclick=\"openExternalLegal('privacy')\"")
text = text.replace(
    "<div><div>Terms of Service</div><div class=\"setting-desc\">Sheria na masharti ya matumizi</div></div>",
    "<div><div>Masharti ya Matumizi</div><div class=\"setting-desc\">Fungua kwenye kivinjari</div></div>",
)
text = text.replace(
    "<div><div>Privacy Policy</div><div class=\"setting-desc\">Jinsi tunavyotunza data yako</div></div>",
    "<div><div>Sera ya Faragha</div><div class=\"setting-desc\">Fungua kwenye kivinjari</div></div>",
)

text = text.replace(
    "$('headerAvatar').textContent = initials;",
    "const _ha=$('headerAvatar'); if(_ha) _ha.textContent = initials;",
)
text = re.sub(
    r"\$\('headerAvatar'\)\.innerHTML\s*=",
    "if($('headerAvatar')) $('headerAvatar').innerHTML=",
    text,
)

text = text.replace(
    "console.warn('[Trending] Backend unavailable — hiding carousel:', err.message||err);",
    "console.warn('[Trending] Backend unavailable — hiding carousel:', err.message||err);\n"
    "    const sec=document.getElementById('trendingSection'); if(sec) sec.classList.add('is-empty');",
)

js_extra = r'''
/* v1.3 helpers */
const EXTERNAL_LEGAL = {
  terms: 'https://skonga-ai.web.app/terms',
  privacy: 'https://skonga-ai.web.app/privacy'
};
async function openExternalLegal(kind){
  const url = EXTERNAL_LEGAL[kind] || EXTERNAL_LEGAL.terms;
  try{
    if(window.Capacitor?.Plugins?.Browser?.open){
      await window.Capacitor.Plugins.Browser.open({ url });
      return;
    }
  }catch(e){}
  try{ window.open(url, '_blank'); }catch(e){ location.href = url; }
}
(function(){
  function safeOpenProfile(e){
    try{ if(e) e.preventDefault(); }catch(_){}
    try{ closeSidebar(); }catch(_){}
    try{
      if(typeof updateProfileView==='function') updateProfileView();
      const sheet=$('profileSheet');
      if(sheet) sheet.classList.remove('hidden');
    }catch(err){ console.error('openProfile', err); try{ showToast('Profile haikufunguka. Jaribu tena.', true);}catch(_){} }
  }
  function safeOpenSettings(e){
    try{ if(e) e.preventDefault(); }catch(_){}
    try{ closeSidebar(); }catch(_){}
    try{
      const sheet=$('settingsSheet');
      if(sheet) sheet.classList.remove('hidden');
    }catch(err){ console.error('openSettings', err); }
  }
  window.openProfile = safeOpenProfile;
  window.openSettings = safeOpenSettings;
  const pb=$('sidebarProfileBtn'); if(pb){ pb.onclick=null; pb.addEventListener('click', safeOpenProfile); }
  const sb=$('sidebarSettingsBtn'); if(sb){ sb.onclick=null; sb.addEventListener('click', safeOpenSettings); }
  setTimeout(function(){
    const vp=document.getElementById('trendingViewport');
    const sec=document.getElementById('trendingSection');
    if(vp && sec && vp.querySelector('.trending-skeleton') && !vp.querySelector('.trending-card')){
      sec.classList.add('is-empty');
    }
  }, 4000);
})();
'''

if "EXTERNAL_LEGAL" not in text:
    idx = text.rfind("</script>")
    if idx != -1:
        text = text[:idx] + "\n" + js_extra + "\n" + text[idx:]

text = text.replace("SETTINGS", "MIPANGILIO")
text = text.replace(">ACCOUNT<", ">AKAUNTI<")
text = text.replace(">PROFILE<", ">WASIFU<")
text = text.replace("Clear All History", "Futa Historia Yote")
text = text.replace("New Chat", "Mazungumzo Mapya")
text = text.replace("Download All Code (ZIP)", "Pakua Code Zote (ZIP)")

text = text.replace("const APP_VERSION = '1.2';", "const APP_VERSION = '1.3';", 1)
if "{ version:'1.3'" not in text:
    text = text.replace(
        "const CHANGELOG = [",
        """const CHANGELOG = [
  { version:'1.3', date:'August 2026', items:[
    'Pro button kwenye header; Profile/Settings zimeimarishwa.',
    'Lugha ya UI (Kiswahili) kwa sehemu kuu.',
    'Terms/Privacy zinafunguka kwenye kivinjari.',
    'Trending haibaki skeleton; sheets fixed.'
  ]},""",
        1,
    )

path.write_text(text, encoding="utf-8")
checks = {
    "v1.3-stable": "/* v1.3-stable */" in text,
    "headerProBtn": "headerProBtn" in text,
    "EXTERNAL_LEGAL": "EXTERNAL_LEGAL" in text,
    "APP 1.3": "APP_VERSION = '1.3'" in text,
}
for k, v in checks.items():
    print(("OK" if v else "FAIL"), k)
print("Done.")
