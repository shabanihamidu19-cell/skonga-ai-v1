#!/usr/bin/env python3
"""Fix Profile sheet not opening (headerAvatar null crash). English toast."""
from pathlib import Path
import re
import sys

path = Path(__file__).resolve().parents[1] / "www" / "index.html"
if not path.exists():
    sys.exit(f"Missing {path}")

text = path.read_text(encoding="utf-8")

# 1) Unguarded headerAvatar in logged-out branch
text = text.replace(
    "$('profileSheetTitle').textContent='ACCOUNT';\n    $('headerAvatar').textContent='?';",
    "$('profileSheetTitle').textContent='ACCOUNT';\n    const _ha2=$('headerAvatar'); if(_ha2) _ha2.textContent='?';",
)
text = text.replace(
    "$('headerAvatar').textContent='?';",
    "const _ha2=$('headerAvatar'); if(_ha2) _ha2.textContent='?';",
)

# 2) openProfile: show sheet first, update view safely
old_open = """function openProfile(){\n  updateProfileView();\n  $('profileSheet').classList.remove('hidden');\n}"""
new_open = """function openProfile(){\n  const sheet = $('profileSheet');\n  if(!sheet){ try{ showToast('Profile unavailable.', true); }catch(e){} return; }\n  try{ updateProfileView(); }catch(err){ console.error('updateProfileView', err); }\n  sheet.classList.remove('hidden');\n}"""
if old_open in text:
    text = text.replace(old_open, new_open, 1)

# 3) Null-safe updateProfileView
new_upv = """function updateProfileView(){\n  if(currentUser){\n    if($('authView')) $('authView').style.display='none';\n    if($('profileView')) $('profileView').style.display='block';\n    if($('profileSheetTitle')) $('profileSheetTitle').textContent='PROFILE';\n\n    const initials = (currentUser.name||'?').trim().split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2) || '?';\n    const pa = $('profileAvatar');\n    if(pa){\n      if(currentUser.photo){\n        pa.innerHTML = `<img src="${currentUser.photo}" style="width:100%;height:100%;object-fit:cover;border-radius:50%" onerror="this.parentNode.textContent='${initials}'"/>`;\n      } else {\n        pa.textContent = initials;\n      }\n    }\n    const _ha=$('headerAvatar'); if(_ha) _ha.textContent = initials;\n\n    if($('profileName')) $('profileName').textContent  = currentUser.name || '';\n    if($('profileEmail')) $('profileEmail').textContent = currentUser.email || '';\n    if($('profileLevel')) $('profileLevel').textContent = currentUser.levelLabel || '\u2014';\n    if($('profileMethod')) $('profileMethod').textContent= currentUser.method === 'google' ? 'Google' : 'Email';\n    if($('statChats')) $('statChats').textContent    = (typeof chatSessions!=='undefined' ? chatSessions.length : 0);\n    if($('statNotes')) $('statNotes').textContent    = (typeof notes!=='undefined' ? notes.length : 0);\n    const days = Math.max(1, Math.floor((Date.now()-(currentUser.joinDate||Date.now()))/(86400000))+1);\n    if($('statDays')) $('statDays').textContent = days;\n  } else {\n    if($('authView')) $('authView').style.display='block';\n    if($('profileView')) $('profileView').style.display='none';\n    if($('profileSheetTitle')) $('profileSheetTitle').textContent='ACCOUNT';\n    const _ha2=$('headerAvatar'); if(_ha2) _ha2.textContent='?';\n  }\n}"""

if "function updateProfileView(){" in text:
    text2 = re.sub(
        r"function updateProfileView\(\)\{[\s\S]*?\n\}\n\nconst levelLabels",
        new_upv + "\n\nconst levelLabels",
        text,
        count=1,
    )
    if text2 != text:
        text = text2
        print("updateProfileView replaced")
    else:
        print("WARN: updateProfileView regex miss")

text = text.replace(
    "showToast('Profile haikufunguka. Jaribu tena.', true);",
    "showToast('Could not fully load profile.', true);",
)

safe = r'''
function safeOpenProfile(e){
  try{ if(e) e.preventDefault(); }catch(_){}
  try{ if(typeof closeSidebar==='function') closeSidebar(); }catch(_){}
  const sheet = document.getElementById('profileSheet') || (typeof $==='function' ? $('profileSheet') : null);
  if(!sheet){ try{ showToast('Profile unavailable.', true); }catch(_){} return; }
  try{ if(typeof updateProfileView==='function') updateProfileView(); }catch(err){ console.error('updateProfileView', err); }
  sheet.classList.remove('hidden');
}
window.openProfile = safeOpenProfile;
'''

if "PROFILE_FIX_V2" not in text:
    inject = "\n/* PROFILE_FIX_V2 */\n" + safe + '''
(function(){
  ['sidebarProfileBtn','profileBtn'].forEach(function(id){
    const el = document.getElementById(id);
    if(!el) return;
    el.onclick = null;
    el.addEventListener('click', function(ev){ safeOpenProfile(ev); });
  });
})();
'''
    idx = text.rfind("</script>")
    if idx != -1:
        text = text[:idx] + inject + "\n" + text[idx:]
        print("PROFILE_FIX_V2 injected")

path.write_text(text, encoding="utf-8")
print("OK", path.stat().st_size)
print("PROFILE_FIX_V2", "PROFILE_FIX_V2" in text)
