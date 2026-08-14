#!/usr/bin/env python3
"""
Restore www/index.html from last known-good commit (14e341f / v1.4 full app),
then re-apply ONLY the safe UI improvements:
  - Theme selector (already in v1.4; ensure wired)
  - How should SKONGA call you? (preferred name)
  - Personalized welcome greeting
  - Safer Profile open (no headerAvatar crash)

Does NOT keep the truncated/broken shell from c7fd12b.
Run from repo root: python3 scripts/restore_and_keep_ui.py
"""
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"
GOOD_SHA = "14e341f"
GOOD_URL = f"https://raw.githubusercontent.com/shabanihamidu19-cell/skonga-ai-v1/{GOOD_SHA}/www/index.html"

print(f"Downloading good index from {GOOD_SHA}…")
try:
    with urllib.request.urlopen(GOOD_URL, timeout=60) as r:
        text = r.read().decode("utf-8")
except Exception as e:
    sys.exit(f"Download failed: {e}")

if len(text) < 100_000:
    sys.exit(f"Unexpected small file ({len(text)} bytes) — abort")

if "/* restore-keep-ui */" not in text:
    text = text.replace("</style>", "/* restore-keep-ui */\n.welcome-greeting{font-size:.95rem;font-weight:500;color:var(--purple-light);margin-top:4px}\n</style>", 1)

if 'id="userNameInput"' not in text:
    needle = """    <!-- Appearance -->
    <div class=\"settings-section\">
      <div class=\"settings-section-label\">Appearance</div>"""
    insert = """    <!-- Appearance -->
    <div class=\"settings-section\">
      <div class=\"settings-section-label\">Appearance</div>
      <div class=\"setting-row\">
        <div class=\"setting-label\">
          <div class=\"setting-icon si-purple\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\"><path d=\"M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg></div>
          <div><div>How should SKONGA call you?</div><div class=\"setting-desc\">Preferred name in greetings</div></div>
        </div>
      </div>
      <div style=\"padding:0 16px 12px\">
        <input type=\"text\" id=\"userNameInput\" placeholder=\"Your name\" maxlength=\"40\"
          style=\"width:100%;background:var(--bg-elevated);border:1.5px solid var(--border);border-radius:12px;color:var(--text-primary);font-family:var(--font-b);font-size:.9rem;padding:11px 14px;outline:none\"/>
      </div>"""
    if needle in text:
        text = text.replace(needle, insert, 1)
        print("Added preferred name field")
    else:
        print("WARN: Appearance section not found for name field")

if 'id="welcomeGreeting"' not in text:
    text = text.replace(
        """      <h2>Hello! I'm SKONGA AI</h2>
      <p>How can I help you today?</p>""",
        """      <h2>Hello! I'm SKONGA AI</h2>
      <div class=\"welcome-greeting\" id=\"welcomeGreeting\"></div>
      <p>How can I help you today?</p>""",
    )
    print("Added welcome greeting element")

if "function updateWelcomeGreeting" not in text:
    js = r'''
/* restore-keep-ui: greeting + preferred name + safe profile */
function getPreferredName(){
  try{
    if(window.appSettings && appSettings.userName) return appSettings.userName.trim();
    const ls = localStorage.getItem('skongaUserName');
    if(ls) return ls.trim();
    if(window.currentUser && currentUser.name) return String(currentUser.name).trim();
  }catch(e){}
  return '';
}
function updateWelcomeGreeting(){
  const el = document.getElementById('welcomeGreeting');
  if(!el) return;
  const name = getPreferredName();
  const greetings = ['Welcome back','Good to see you','Ready when you are','What is new'];
  const g = greetings[Math.floor(Math.random()*greetings.length)];
  el.textContent = name ? (g + ', ' + name) : g;
}
(function wirePreferredName(){
  const inp = document.getElementById('userNameInput');
  if(!inp) return;
  try{
    if(window.appSettings && appSettings.userName) inp.value = appSettings.userName;
    else {
      const ls = localStorage.getItem('skongaUserName');
      if(ls) inp.value = ls;
    }
  }catch(e){}
  inp.addEventListener('input', function(){
    const v = this.value.trim();
    try{
      if(window.appSettings){ appSettings.userName = v; if(typeof persistSettings==='function') persistSettings(); }
      localStorage.setItem('skongaUserName', v);
    }catch(e){}
    updateWelcomeGreeting();
  });
})();
(function safeProfileWire(){
  function safeOpenProfile(e){
    try{ if(e) e.preventDefault(); }catch(_){}
    try{ if(typeof closeSidebar==='function') closeSidebar(); }catch(_){}
    try{
      if(typeof updateProfileView==='function') updateProfileView();
      const sheet = document.getElementById('profileSheet');
      if(sheet) sheet.classList.remove('hidden');
    }catch(err){ console.error('openProfile', err); }
  }
  window.openProfile = safeOpenProfile;
  ['sidebarProfileBtn','profileBtn'].forEach(function(id){
    const el = document.getElementById(id);
    if(el){ el.onclick = null; el.addEventListener('click', safeOpenProfile); }
  });
})();
document.addEventListener('DOMContentLoaded', function(){ try{ updateWelcomeGreeting(); }catch(e){} });
try{ updateWelcomeGreeting(); }catch(e){}
'''
    idx = text.rfind("</script>")
    if idx != -1:
        text = text[:idx] + "\n" + js + "\n" + text[idx:]
        print("Added greeting/profile JS")

text = text.replace(
    "$('headerAvatar').textContent = initials;",
    "const _ha=$('headerAvatar'); if(_ha) _ha.textContent = initials;",
)

INDEX.parent.mkdir(parents=True, exist_ok=True)
INDEX.write_text(text, encoding="utf-8")
print(f"Wrote {INDEX} ({INDEX.stat().st_size} bytes)")
print("OK — full app restored + name/greeting/theme/profile kept")
