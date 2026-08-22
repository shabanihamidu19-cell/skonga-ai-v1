#!/usr/bin/env python3
"""Chat history long-press Rename/Delete + show-password on auth."""
from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
html = p.read_text(encoding="utf-8")
n = 0

# ── CSS for hist actions + password eye ──
CSS = """
.hist-item{ -webkit-user-select:none; user-select:none; }
.hist-menu{
  position:absolute; right:6px; top:36px; z-index:40;
  background:var(--bg-card); border:1px solid var(--border);
  border-radius:12px; min-width:140px; padding:6px;
  box-shadow:0 8px 24px rgba(0,0,0,.35);
}
.hist-menu button{
  display:block; width:100%; text-align:left; background:transparent;
  border:none; color:var(--text-primary); font:inherit; font-size:.82rem;
  padding:10px 12px; border-radius:8px; cursor:pointer;
}
.hist-menu button:hover{ background:rgba(124,58,237,.12); }
.hist-menu button.danger{ color:#f43f5e; }
.field-pass-wrap{ position:relative; }
.field-pass-wrap input{ width:100%; padding-right:44px; }
.pass-toggle{
  position:absolute; right:8px; top:50%; transform:translateY(-50%);
  background:transparent; border:none; color:var(--text-muted);
  font-size:.75rem; cursor:pointer; padding:6px 8px;
}
.pass-toggle:hover{ color:var(--purple-light); }
"""

if ".hist-menu{" not in html:
    html = html.replace("</style>", CSS + "\n</style>", 1)
    n += 1
    print("OK: CSS")

# ── Password fields with show toggle ──
OLD_LOGIN_PASS = '''          <div class="field">
            <label>Password</label>
            <input type="password" id="loginPass" placeholder="••••••••"/>
          </div>'''
NEW_LOGIN_PASS = '''          <div class="field">
            <label>Password</label>
            <div class="field-pass-wrap">
              <input type="password" id="loginPass" placeholder="••••••••" autocomplete="current-password"/>
              <button type="button" class="pass-toggle" id="loginPassToggle" onclick="togglePasswordVisibility('loginPass',this)" aria-label="Show password">Show</button>
            </div>
          </div>'''
if OLD_LOGIN_PASS in html:
    html = html.replace(OLD_LOGIN_PASS, NEW_LOGIN_PASS, 1)
    n += 1
    print("OK: login show password")

OLD_REG_PASS = '''          <div class="field">
            <label>Password</label>
            <input type="password" id="regPass" placeholder="At least 6 characters"/>
          </div>'''
NEW_REG_PASS = '''          <div class="field">
            <label>Password</label>
            <div class="field-pass-wrap">
              <input type="password" id="regPass" placeholder="At least 6 characters" autocomplete="new-password"/>
              <button type="button" class="pass-toggle" id="regPassToggle" onclick="togglePasswordVisibility('regPass',this)" aria-label="Show password">Show</button>
            </div>
          </div>'''
if OLD_REG_PASS in html:
    html = html.replace(OLD_REG_PASS, NEW_REG_PASS, 1)
    n += 1
    print("OK: register show password")

# ── togglePasswordVisibility helper (near handleLogin) ──
if "function togglePasswordVisibility" not in html:
    helper = '''
function togglePasswordVisibility(inputId, btn){
  const inp = document.getElementById(inputId);
  if(!inp) return;
  const show = inp.type === 'password';
  inp.type = show ? 'text' : 'password';
  if(btn) btn.textContent = show ? 'Hide' : 'Show';
}
'''
    html = html.replace("function handleLogin(){", helper + "\nfunction handleLogin(){", 1)
    n += 1
    print("OK: togglePasswordVisibility")

# ── replace renderHistList with long-press menu ──
OLD_RENDER = '''function renderHistList(){
  const list = $('chatHistList');
  list.innerHTML = '';
  if(!chatSessions.length){
    list.innerHTML = '<div style="padding:16px;font-size:.8rem;color:var(--text-muted);text-align:center">No chats yet</div>';
    return;
  }
  chatSessions.slice().reverse().forEach(s=>{
    const item = document.createElement('div');
    item.className = 'hist-item' + (s.id===activeChatId?' active-chat':'');
    item.innerHTML = `
      <div class="hist-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
      <div class="hist-info">
        <div class="hist-title">${s.title}</div>
        <div class="hist-preview">${s.preview}</div>
        <div class="hist-time">${s.time}</div>
      </div>`;
    item.onclick = ()=>{ loadSession(s.id); closeSidebar(); };
    list.appendChild(item);
  });
}'''

NEW_RENDER = r'''function closeHistMenus(){
  document.querySelectorAll('.hist-menu').forEach(m=>m.remove());
}
function renameChatSession(id){
  const s = chatSessions.find(x=>x.id===id);
  if(!s) return;
  const next = prompt('Rename chat', s.title || '');
  if(next===null) return;
  const t = String(next).trim().slice(0,80);
  if(!t) return;
  s.title = t;
  s.aiTitled = true;
  persistSessions();
  renderHistList();
}
function deleteChatSession(id){
  const s = chatSessions.find(x=>x.id===id);
  if(!s) return;
  if(!confirm('Delete this chat?\n\n"'+(s.title||'Chat')+'"')) return;
  chatSessions = chatSessions.filter(x=>x.id!==id);
  if(activeChatId===id){
    activeChatId = null;
    conversationMemory = [];
    try{
      const area = $('chat-area');
      if(area) area.innerHTML = '';
      if(typeof showWelcome==='function') showWelcome();
      else if(typeof startNewChat==='function') startNewChat();
    }catch(e){}
  }
  persistSessions();
  renderHistList();
}
function attachHistLongPress(item, sessionId){
  let timer = null;
  let moved = false;
  const openMenu = (e)=>{
    if(e){ e.preventDefault(); e.stopPropagation(); }
    closeHistMenus();
    const menu = document.createElement('div');
    menu.className = 'hist-menu';
    menu.innerHTML = `
      <button type="button" data-act="rename">Rename</button>
      <button type="button" class="danger" data-act="delete">Delete</button>`;
    menu.addEventListener('click', ev=>{
      ev.stopPropagation();
      const act = ev.target && ev.target.getAttribute('data-act');
      closeHistMenus();
      if(act==='rename') renameChatSession(sessionId);
      if(act==='delete') deleteChatSession(sessionId);
    });
    item.appendChild(menu);
  };
  item.addEventListener('contextmenu', openMenu);
  item.addEventListener('touchstart', e=>{
    moved = false;
    timer = setTimeout(()=>openMenu(e), 480);
  }, {passive:true});
  item.addEventListener('touchmove', ()=>{ moved = true; if(timer){ clearTimeout(timer); timer=null; } }, {passive:true});
  item.addEventListener('touchend', ()=>{ if(timer){ clearTimeout(timer); timer=null; } });
  item.addEventListener('touchcancel', ()=>{ if(timer){ clearTimeout(timer); timer=null; } });
}
function renderHistList(){
  const list = $('chatHistList');
  if(!list) return;
  closeHistMenus();
  list.innerHTML = '';
  if(!chatSessions.length){
    list.innerHTML = '<div style="padding:16px;font-size:.8rem;color:var(--text-muted);text-align:center">No chats yet</div>';
    return;
  }
  chatSessions.slice().reverse().forEach(s=>{
    const item = document.createElement('div');
    item.className = 'hist-item' + (s.id===activeChatId?' active-chat':'');
    const title = (typeof escapeHtml==='function' ? escapeHtml(s.title||'Chat') : String(s.title||'Chat'));
    const preview = (typeof escapeHtml==='function' ? escapeHtml(s.preview||'') : String(s.preview||''));
    const time = (typeof escapeHtml==='function' ? escapeHtml(s.time||'') : String(s.time||''));
    item.innerHTML = `
      <div class="hist-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
      <div class="hist-info">
        <div class="hist-title">${title}</div>
        <div class="hist-preview">${preview}</div>
        <div class="hist-time">${time}</div>
      </div>`;
    item.onclick = (e)=>{
      if(e.target.closest && e.target.closest('.hist-menu')) return;
      closeHistMenus();
      loadSession(s.id);
      closeSidebar();
    };
    attachHistLongPress(item, s.id);
    list.appendChild(item);
  });
}'''

if "function renameChatSession" not in html and OLD_RENDER in html:
    html = html.replace(OLD_RENDER, NEW_RENDER, 1)
    n += 1
    print("OK: hist long-press rename/delete")
elif "function renameChatSession" in html:
    print("OK: hist menu already present")
else:
    print("SKIP: renderHistList pattern mismatch — check manually")

# Close menus on sidebar overlay click if possible
if "closeHistMenus" in html and "document.addEventListener('click', closeHistMenus)" not in html:
    html = html.replace(
        "function closeSidebar(){\n  $('sidebar').classList.remove('open');\n  $('overlay').classList.remove('open');\n}",
        "function closeSidebar(){\n  try{ closeHistMenus(); }catch(e){}\n  $('sidebar').classList.remove('open');\n  $('overlay').classList.remove('open');\n}\n", 
        1,
    )
    n += 1

p.write_text(html, encoding="utf-8")
print(f"Done replacements={n} → {p.resolve()}")
