#!/usr/bin/env python3
"""Apply SKONGA v1.1 UI: sidebar upgrade + strip voice. Run from repo root: python3 scripts/apply_v1_1.py"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
path = root / "www" / "index.html"
if not path.exists():
    sys.exit(f"Missing {path}")
text = path.read_text(encoding="utf-8")
if "sidebar-upgrade" in text and "voiceBtn" not in text:
    print("Already applied.")
    sys.exit(0)

# --- CSS sidebar upgrade ---
anchor = ".chat-hist-list::-webkit-scrollbar-thumb{background:var(--purple-mid)}"
css = anchor + """
.sidebar-upgrade{flex-shrink:0;margin:8px 10px 14px;padding:14px;border-radius:14px;background:linear-gradient(135deg,rgba(124,58,237,.16),rgba(192,132,252,.08));border:1px solid rgba(168,85,247,.35)}
.sidebar-upgrade-title{font-size:.88rem;font-weight:600;color:var(--purple-light);margin-bottom:6px}
.sidebar-upgrade-desc{font-size:.72rem;color:var(--text-secondary);line-height:1.45;margin:0 0 10px}
.sidebar-upgrade-btn{width:100%;padding:10px 12px;border:none;border-radius:10px;background:linear-gradient(135deg,var(--purple-main),var(--purple-glow));color:#fff;font-family:var(--font-b);font-size:.82rem;font-weight:600;cursor:pointer}
.sidebar-upgrade-btn:active{opacity:.9;transform:scale(.98)}"""
if anchor in text and "sidebar-upgrade{" not in text:
    text = text.replace(anchor, css, 1)

# --- Sidebar HTML ---
old = """  <div class=\"sidebar-section\">Today</div>
  <div class=\"chat-hist-list\" id=\"chatHistList\"></div>
</div>"""
new = """  <div class=\"sidebar-section\">Today</div>
  <div class=\"chat-hist-list\" id=\"chatHistList\"></div>
  <div class=\"sidebar-upgrade\" id=\"sidebarUpgrade\">
    <div class=\"sidebar-upgrade-title\">💜 SKONGA Pro</div>
    <p class=\"sidebar-upgrade-desc\">Umefikia kikomo? Lipa kwa M-Pesa, Tigo, Airtel au Halo — endelea bila kulazimishwa.</p>
    <button type=\"button\" class=\"sidebar-upgrade-btn\" onclick=\"openSkongaPay()\">Lipa sasa</button>
  </div>
</div>"""
if old in text:
    text = text.replace(old, new, 1)

# Remove voice CSS
text = re.sub(r"/\* ── VOICE BUTTON ── \*/.*?\.voice-status\.show\{display:block\}\n\n?", "", text, count=1, flags=re.S)

# Remove voice button HTML
text = re.sub(r"\s*<button class=\"voice-btn\"[^>]*>.*?</button>\n?", "\n", text, count=1, flags=re.S)
text = re.sub(r"\s*<div class=\"voice-status\" id=\"voiceStatus\">[^<]*</div>\n?", "\n", text, count=1)

# Remove Voice settings section
text = re.sub(
    r"\s*<!-- Voice -->\s*<div class=\"settings-section\">.*?</div>\s*(?=\s*<!-- Data)",
    "\n\n    ",
    text,
    count=1,
    flags=re.S,
)

# Remove voice JS block
text = re.sub(
    r"/\* ═+\n   VOICE INPUT \(Speech-to-Text\).*?\$\('voiceBtn'\)\.addEventListener\('click', toggleVoice\);\n\n?",
    "",
    text,
    count=1,
    flags=re.S,
)
text = re.sub(r"\nfunction applyVoiceSetting\(\)\{[^}]+\}\n", "\n", text, count=1)
text = re.sub(r"\$\('autoSendToggle'\)\.addEventListener\('change', function\(\)\{[^}]+\}\);\n", "", text, count=1)
text = text.replace("  voice: false, // disabled by default — unreliable on many Android WebViews\n", "")
text = text.replace("  autoSend: true,\n", "")
text = text.replace("  $('voiceToggle').checked = appSettings.voice;\n", "")
text = text.replace("  $('autoSendToggle').checked = appSettings.autoSend;\n", "")
text = text.replace("  $('voiceBtn').style.display = appSettings.voice ? 'flex' : 'none';\n", "")
text = re.sub(r"\n  microphone: \{ icon:'🎙️', title:'Microphone access', body:.*? \},", "", text, count=1, flags=re.S)
text = text.replace("   VOICE INPUT                         — SpeechRecognition wiring\n", "")
text = text.replace(
    "    'Voice input off by default (unreliable on many Android WebViews); can be re-enabled in Settings if your device supports it.',\n",
    "    'Voice input removed (unreliable on Android WebView/APK).',\n",
)
old_pay = """function openSkongaPay(){
  // Navigate to the integrated mobile-money page
  try {
    if (window.Capacitor?.Plugins?.Browser) {
      // Prefer in-app browser if available; otherwise same-origin navigation
      window.location.href = './pay.html';
    } else {
      window.location.href = './pay.html';
    }
  } catch(e) {
    window.location.href = './pay.html';
  }
}"""
new_pay = """function openSkongaPay(){
  window.location.href = './pay.html';
}"""
if old_pay in text:
    text = text.replace(old_pay, new_pay, 1)

path.write_text(text, encoding="utf-8")
print("Applied. voiceBtn:", "voiceBtn" in text, "sidebar-upgrade:", "sidebar-upgrade" in text)
