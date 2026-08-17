#!/usr/bin/env python3
"""Apply clickable SKONGA Library citations + chat scroll fix to www/index.html (skonga-ai-v1)."""
from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
if not p.exists():
    print("FAIL: not found:", p)
    sys.exit(1)
html = p.read_text(encoding="utf-8")
n = 0

def rep(old, new, label):
    global html, n
    if old not in html:
        print("SKIP:", label)
        return
    html = html.replace(old, new)
    n += 1
    print("OK:", label)

rep(
"""#chat-area{flex:1;overflow-y:auto;padding:20px 14px 10px;display:flex;flex-direction:column;gap:14px;scroll-behavior:smooth}
#chat-area::-webkit-scrollbar{width:3px}
#chat-area::-webkit-scrollbar-thumb{background:var(--purple-mid);border-radius:10px}""",
"""#chat-area{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:20px 14px 10px;display:flex;flex-direction:column;gap:14px;scroll-behavior:smooth;-webkit-overflow-scrolling:touch;touch-action:pan-y;overscroll-behavior:contain}
#chat-area::-webkit-scrollbar{width:5px}
#chat-area::-webkit-scrollbar-thumb{background:var(--purple-mid);border-radius:10px}
#chat-area .bubble .md-content{max-width:100%}
#chat-area .bubble .md-content pre{max-height:280px;overflow:auto;-webkit-overflow-scrolling:touch}""",
"chat-scroll",
)

rep(
".source-card{flex-shrink:0;width:148px;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:11px;padding:9px 10px;cursor:pointer;transition:background .15s,border-color .15s}",
".source-card{flex-shrink:0;width:148px;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:11px;padding:9px 10px;cursor:pointer;transition:background .15s,border-color .15s;text-align:left;font:inherit;color:inherit;display:block;text-decoration:none}",
"source-card-css",
)

if ".source-icon.curriculum{" not in html:
    rep(
        ".source-icon.tamisemi{background:#dc2626}",
        """.source-icon.tamisemi{background:#dc2626}
.source-icon.curriculum{background:linear-gradient(135deg,#7c3aed,#a855f7)}
.source-card.curriculum-card{border-color:rgba(124,58,237,.35)}
.source-card.curriculum-card:hover{border-color:var(--purple-main)}""",
        "curriculum-css",
    )

old_build = """function buildSourcesHtml(sources){
  if(!sources || !sources.length) return '';
  const iconMap={google:'G',wikipedia:'W',necta:'N',tamisemi:'T'};
  const cards=sources.map(s=>{
    const kind=(s.kind||'google').toLowerCase();
    const initial=iconMap[kind]||'?';
    return `<a class=\"source-card\" href=\"${s.url||'#'}\" target=\"_blank\" rel=\"noopener noreferrer\">
      <div class=\"source-card-top\"><span class=\"source-icon ${kind}\">${initial}</span><span class=\"source-domain\">${escapeHtml(s.domain||kind)}</span></div>
      <div class=\"source-title\">${escapeHtml(s.title||'Chanzo')}</div>
    </a>`;
  }).join('');
  return `<div class=\"sources-block\"><div class=\"sources-label\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\"><circle cx=\"11\" cy=\"11\" r=\"8\"/><line x1=\"21\" y1=\"21\" x2=\"16.65\" y2=\"16.65\"/></svg>Vyanzo</div><div class=\"sources-scroll\">${cards}</div></div>`;
}"""

new_build = r"""function buildSourcesHtml(sources){
  if(!sources || !sources.length) return '';
  const iconMap={google:'G',wikipedia:'W',necta:'N',tamisemi:'T',curriculum:'S'};
  const cards=sources.map((s,i)=>{
    const kind=(s.kind|| (s.domain==='SKONGA Library' ? 'curriculum' : 'google')).toLowerCase();
    const initial=iconMap[kind]|| (kind==='curriculum' ? 'S' : '?');
    const isCurriculum = kind==='curriculum' || (s.domain||'').toLowerCase().includes('skonga');
    const title = s.title || s.title_en || s.title_sw || 'Chanzo';
    const meta = [s.subject_name || s.subject, s.form_id ? ('Form '+s.form_id) : (s.form ? ('Form '+s.form) : ''), s.difficulty].filter(Boolean).join(' · ');
    if(isCurriculum){
      const payload = encodeURIComponent(JSON.stringify({
        title, subject: s.subject_name || s.subject || 'SKONGA Library',
        form: s.form_id || s.form || '', difficulty: s.difficulty || '',
        topic_id: s.topic_id || ''
      }));
      return `<button type=\"button\" class=\"source-card curriculum-card\" data-curriculum=\"${payload}\" onclick=\"openCurriculumSource(this)\">
      <div class=\"source-card-top\"><span class=\"source-icon curriculum\">${initial}</span><span class=\"source-domain\">SKONGA Library</span></div>
      <div class=\"source-title\">${escapeHtml(title)}</div>
      ${meta ? `<div class=\"source-domain\" style=\"margin-top:4px;text-transform:none\">${escapeHtml(meta)}</div>` : ''}
    </button>`;
    }
    const href = (s.url && s.url !== '#') ? s.url : '';
    if(!href){
      return `<div class=\"source-card\" style=\"cursor:default\">
      <div class=\"source-card-top\"><span class=\"source-icon ${kind}\">${initial}</span><span class=\"source-domain\">${escapeHtml(s.domain||kind)}</span></div>
      <div class=\"source-title\">${escapeHtml(title)}</div>
    </div>`;
    }
    return `<a class=\"source-card\" href=\"${href}\" target=\"_blank\" rel=\"noopener noreferrer\">
      <div class=\"source-card-top\"><span class=\"source-icon ${kind}\">${initial}</span><span class=\"source-domain\">${escapeHtml(s.domain||kind)}</span></div>
      <div class=\"source-title\">${escapeHtml(title)}</div>
    </a>`;
  }).join('');
  return `<div class=\"sources-block\"><div class=\"sources-label\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\"><circle cx=\"11\" cy=\"11\" r=\"8\"/><line x1=\"21\" y1=\"21\" x2=\"16.65\" y2=\"16.65\"/></svg>Vyanzo</div><div class=\"sources-scroll\">${cards}</div></div>`;
}

function openCurriculumSource(el){
  try{
    const d = JSON.parse(decodeURIComponent(el.getAttribute('data-curriculum')||'{}'));
    if(typeof showToast==='function'){
      showToast((d.title||'SKONGA Library') + (d.subject ? ' · '+d.subject : '') + (d.form ? ' · Form '+d.form : ''), false);
    }
    let panel = document.getElementById('curriculum-detail');
    if(!panel){
      panel = document.createElement('div');
      panel.id = 'curriculum-detail';
      panel.style.cssText = 'position:fixed;left:50%;bottom:90px;transform:translateX(-50%);width:min(92vw,400px);background:var(--bg-elevated);border:1px solid var(--border);border-radius:16px;padding:16px;z-index:80;box-shadow:0 12px 40px rgba(0,0,0,.5)';
      document.body.appendChild(panel);
    }
    panel.innerHTML = `<div style=\"display:flex;justify-content:space-between;align-items:flex-start;gap:12px\">
      <div>
        <div style=\"font-size:.7rem;color:var(--purple-light);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px\">SKONGA Library</div>
        <div style=\"font-size:.95rem;font-weight:600;color:var(--text-primary);line-height:1.35\">${escapeHtml(d.title||'Mada')}</div>
        <div style=\"font-size:.78rem;color:var(--text-secondary);margin-top:8px;line-height:1.5\">
          ${d.subject?escapeHtml(d.subject):''}${d.form?' · Form '+escapeHtml(String(d.form)):''}${d.difficulty?' · '+escapeHtml(d.difficulty):''}
        </div>
        <div style=\"font-size:.72rem;color:var(--text-muted);margin-top:10px\">Mada hii inatoka kwenye mtaala wa TIE (SKONGA Library).</div>
      </div>
      <button type=\"button\" onclick=\"document.getElementById('curriculum-detail').remove()\" style=\"border:none;background:var(--bg-card);color:var(--text-secondary);width:32px;height:32px;border-radius:8px;cursor:pointer;flex-shrink:0\">✕</button>
    </div>`;
    setTimeout(()=>{ try{ panel.remove(); }catch(_){} }, 8000);
  }catch(err){ console.warn(err); }
}"""

rep(old_build, new_build, "buildSourcesHtml")

old_map = """const citeSources = (data.citations||[]).map(c => ({
      title: c.title_sw || c.title_en || c.topic_id,
      url: '#',
      domain: 'SKONGA Library',
      kind: 'curriculum'
    }));"""
new_map = """const citeSources = (data.citations||[]).map(c => ({
      title: c.title_sw || c.title_en || c.title || c.topic_id,
      title_en: c.title_en || c.title,
      title_sw: c.title_sw || c.title,
      url: (c.url && c.url !== '#') ? c.url : '',
      domain: 'SKONGA Library',
      kind: 'curriculum',
      subject_name: c.subject_name || c.subject || '',
      form_id: c.form_id || c.form || '',
      difficulty: c.difficulty || '',
      topic_id: c.topic_id || ''
    }));"""
if old_map in html:
    c = html.count(old_map)
    html = html.replace(old_map, new_map)
    n += c
    print("OK: citeSources (indent4) x", c)

old_map2 = """      const citeSources = (data.citations||[]).map(c => ({
        title: c.title_sw || c.title_en || c.topic_id,
        url: '#',
        domain: 'SKONGA Library',
        kind: 'curriculum'
      }));"""
new_map2 = """      const citeSources = (data.citations||[]).map(c => ({
        title: c.title_sw || c.title_en || c.title || c.topic_id,
        title_en: c.title_en || c.title,
        title_sw: c.title_sw || c.title,
        url: (c.url && c.url !== '#') ? c.url : '',
        domain: 'SKONGA Library',
        kind: 'curriculum',
        subject_name: c.subject_name || c.subject || '',
        form_id: c.form_id || c.form || '',
        difficulty: c.difficulty || '',
        topic_id: c.topic_id || ''
      }));"""
if old_map2 in html:
    c = html.count(old_map2)
    html = html.replace(old_map2, new_map2)
    n += c
    print("OK: citeSources (indent6) x", c)

p.write_text(html, encoding="utf-8")
print("---")
print("Total replacements:", n)
print("Wrote", p.resolve())
if "openCurriculumSource" not in html:
    print("WARN: openCurriculumSource missing — check buildSourcesHtml")
else:
    print("VERIFY: openCurriculumSource present")
