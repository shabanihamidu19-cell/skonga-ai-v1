#!/usr/bin/env python3
"""Fix panel X buttons + Android back (close sheet instead of exiting app)."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
path = root / "www" / "index.html"
pkg = root / "package.json"

if not path.exists():
    sys.exit(f"Missing {path}")

text = path.read_text(encoding="utf-8")

if 'id="payClose"' in text and 'onclick="closeSkongaPay()"' not in text:
    text = re.sub(r'(<button[^>]*id="payClose"[^>]*)>', r'\1 onclick="closeSkongaPay()">', text, count=1)
if 'id="legalClose"' in text and 'onclick="closeLegalModal()"' not in text:
    text = re.sub(r'(<button[^>]*id="legalClose"[^>]*)>', r'\1 onclick="closeLegalModal()">', text, count=1)
if 'id="settingsClose"' in text and 'onclick="closeSettings()"' not in text:
    text = re.sub(r'(<button[^>]*id="settingsClose"[^>]*)>', r'\1 onclick="closeSettings()">', text, count=1)
if 'id="profileClose"' in text and 'onclick="closeProfile()"' not in text:
    text = re.sub(r'(<button[^>]*id="profileClose"[^>]*)>', r'\1 onclick="closeProfile()">', text, count=1)

old_back = """    const sheets = ['profileSheet','settingsSheet'];
    for(const id of sheets){
      const el = document.getElementById(id);
      if(el && !el.classList.contains('hidden')){
        if(id === 'profileSheet') closeProfile?.();
        else if(id === 'settingsSheet') closeSettings?.();
        return;
      }
    }"""

new_back = """    const sheets = ['paySheet','legalSheet','profileSheet','settingsSheet'];
    for(const id of sheets){
      const el = document.getElementById(id);
      if(el && !el.classList.contains('hidden')){
        if(id === 'paySheet'){ if(typeof closeSkongaPay==='function') closeSkongaPay(); else el.classList.add('hidden'); }
        else if(id === 'legalSheet'){ if(typeof closeLegalModal==='function') closeLegalModal(); else el.classList.add('hidden'); }
        else if(id === 'profileSheet'){ if(typeof closeProfile==='function') closeProfile(); else el.classList.add('hidden'); }
        else if(id === 'settingsSheet'){ if(typeof closeSettings==='function') closeSettings(); else el.classList.add('hidden'); }
        return;
      }
    }
    const sb = document.getElementById('sidebar');
    if(sb && sb.classList.contains('open')){ if(typeof closeSidebar==='function') closeSidebar(); else sb.classList.remove('open'); return; }"""

if old_back in text:
    text = text.replace(old_back, new_back, 1)
    print("back handler updated")

if "window.closeSkongaPay = closeSkongaPay" not in text:
    text = text.replace(
        """function closeSkongaPay(){\n  $('paySheet').classList.add('hidden');\n}""",
        """function closeSkongaPay(){\n  const el = document.getElementById('paySheet');\n  if(el) el.classList.add('hidden');\n}\nwindow.closeSkongaPay = closeSkongaPay;\n""",
    )

if "PANELS_CLOSE_FIX" not in text:
    inject = r'''
/* PANELS_CLOSE_FIX */
(function(){
  function bindCloses(){
    const pairs = [
      ['payClose','closeSkongaPay'],
      ['legalClose','closeLegalModal'],
      ['settingsClose','closeSettings'],
      ['profileClose','closeProfile']
    ];
    pairs.forEach(([id, name])=>{
      const el = document.getElementById(id);
      const fn = window[name];
      if(!el || typeof fn!=='function') return;
      el.onclick = function(e){ try{e.preventDefault();e.stopPropagation();}catch(_){} fn(); };
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', bindCloses);
  else bindCloses();
  setTimeout(bindCloses, 0);
  setTimeout(bindCloses, 400);
})();
'''
    idx = text.rfind("</script>")
    if idx != -1:
        text = text[:idx] + inject + "\n" + text[idx:]
        print("PANELS_CLOSE_FIX injected")

path.write_text(text, encoding="utf-8")
print("OK", path.stat().st_size)

if pkg.exists():
    pj = pkg.read_text(encoding="utf-8")
    if "@capacitor/app" not in pj:
        pj = pj.replace(
            '"@capacitor/android": "^6.2.1",',
            '"@capacitor/android": "^6.2.1",\n    "@capacitor/app": "^6.0.2",',
        )
        pkg.write_text(pj, encoding="utf-8")
        print("Added @capacitor/app")
