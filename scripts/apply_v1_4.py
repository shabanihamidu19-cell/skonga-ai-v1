#!/usr/bin/env python3
"""
SKONGA AI v1.4 — English-only production UI
- No Swahili UI strings
- Remove upgrade block from history sidebar
- Clear history stays in Settings (bottom)
- Remove language toggle (force English)
- Remove App Version / changelog from Settings
- Professional pay copy
- Header Pro remains

Run: python3 scripts/apply_v1_4.py
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
path = root / "www" / "index.html"
if not path.exists():
    sys.exit(f"Missing {path}")

text = path.read_text(encoding="utf-8")
if "/* v1.4-en */" in text:
    print("Already applied v1.4.")
    sys.exit(0)

text = text.replace("MIPANGILIO_STORAGE_KEY", "SETTINGS_STORAGE_KEY")
text = text.replace("/* ── MIPANGILIO SHEET ── */", "/* ── SETTINGS SHEET ── */")
text = text.replace("<!-- ═══ MIPANGILIO BOTTOM SHEET ═══ -->", "<!-- ═══ SETTINGS BOTTOM SHEET ═══ -->")
text = text.replace('<span class="sheet-title">MIPANGILIO</span>', '<span class="sheet-title">SETTINGS</span>')
text = text.replace("   MIPANGILIO", "   SETTINGS")

text = text.replace("</style>", "/* v1.4-en */\n</style>", 1)

text = re.sub(
    r'\s*<div class="sidebar-upgrade" id="sidebarUpgrade">[\s\S]*?</div>\s*(?=<div class="sidebar-section">)',
    "\n  ",
    text,
    count=1,
)

repls = [
    ("Mazungumzo Mapya", "New Chat"),
    ("Pakua Code Zote (ZIP)", "Download All Code (ZIP)"),
    ("<h2>Habari! Mimi ni SKONGA AI</h2>", "<h2>Hello! I'm SKONGA AI</h2>"),
    ("<p>Naweza kukusaidia vipi leo?</p>", "<p>How can I help you today?</p>"),
    ("Habari! Mimi ni SKONGA AI", "Hello! I'm SKONGA AI"),
    ("Naweza kukusaidia vipi leo?", "How can I help you today?"),
    ("Mada zinazovuma leo", "Today's Trending Topics"),
    ('placeholder="Andika ujumbe..."', 'placeholder="Message SKONGA AI..."'),
    ("Mode ya nje ya mtandao — historia na notes zilizohifadhiwa", "Offline — showing saved chats and notes only"),
    ("Futa Historia Yote", "Clear All History"),
    (">AKAUNTI<", ">ACCOUNT<"),
    (">WASIFU<", ">PROFILE<"),
    ("Masharti ya Matumizi", "Terms of Service"),
    ("Fungua kwenye kivinjari", "Opens in browser"),
    ("Sera ya Faragha", "Privacy Policy"),
    ("Lipa kwa mitandao ya simu", "Pay with mobile money"),
    ("Endelea kujifunza kwa urahisi", "Keep learning without interruption"),
    ("Lipa sasa (M-Pesa / Tigo / Airtel / Halo)", "Pay now (M-Pesa / Tigo / Airtel / Halo)"),
    ("Jaribu tena baadaye", "Try again later"),
    ("Pro hai — jaribu tena baada ya sekunde chache.", "Pro is active — please try again in a moment."),
    ("💜 Umefikia kikomo cha bure", "You've reached the free limit"),
]
for a, b in repls:
    text = text.replace(a, b)

pay_map = [
    ("Chagua kifurushi chako. Baada ya malipo, ujumbe wa ziada unafunguliwa kwa muda wa kifurushi.",
     "Choose a plan. After payment, extra messages unlock for the plan duration."),
    ("Chagua kifurushi. Baada ya malipo, ujumbe wa ziada unafunguliwa kwa muda wa kifurushi.",
     "Choose a plan. After payment, extra messages unlock for the plan duration."),
    (">Endelea</button>", ">Continue</button>"),
    ("Nambari ya simu (M-Pesa / Tigo / Airtel / Halo)", "Phone number (M-Pesa / Tigo / Airtel / Halo)"),
    ("STK Push itatumwa kwenye simu hii. PIN ya mtandao inaingizwa <strong>kwenye simu yako</strong> — si ndani ya app (usalama).",
     "An STK Push will be sent to this phone. Enter your mobile-money PIN on your phone — never inside the app."),
    (">Rudi</button>", ">Back</button>"),
    ("Thibitisha, kisha thibitisha malipo kwenye simu yako (PIN ya M-Pesa/Tigo/Airtel/Halo).",
     "Confirm, then complete payment on your phone with your mobile-money PIN."),
    ("Thibitisha & Tuma STK", "Confirm & Send STK"),
    ("Thibitisha & Tuma STK", "Confirm & Send STK"),
    ("Ingiza PIN kwenye simu yako ili kukamilisha.", "Enter your PIN on your phone to complete payment."),
    (">Funga</button>", ">Close</button>"),
    (">Jaribu tena</button>", ">Try again</button>"),
    ("Malipo yamepokelewa (demo)", "Payment confirmed"),
    ("imeamilishwa. SKONGA Pro itatumika hadi muda wa kifurushi uishe. Backend halisi itathibitisha STK baadaye.",
     "is active. SKONGA Pro stays active until the plan expires."),
    ("SKONGA Pro imeamilishwa · ", "SKONGA Pro activated · "),
    ("Inatuma…", "Sending…"),
    ("Mtandao: ", "Network: "),
    ("Nambari haitambuliki", "Unknown number"),
    ("name:'Siku 1'", "name:'1 Day'"),
    ("name:'Wiki 1'", "name:'1 Week'"),
    ("name:'Mwezi 1'", "name:'1 Month'"),
    ("name:'Mwaka 1'", "name:'1 Year'"),
    ("tag:'Jaribio'", "tag:'Trial'"),
    ("tag:'Maarufu'", "tag:'Popular'"),
    ("tag:'Bora'", "tag:'Best'"),
    ("tag:'Akiba'", "tag:'Save'"),
    ("sub:'Masaa 24'", "sub:'24 hours'"),
    ("sub:'Siku 7'", "sub:'7 days'"),
    ("sub:'Siku 30'", "sub:'30 days'"),
    ("sub:'Siku 365'", "sub:'365 days'"),
]
for a, b in pay_map:
    text = text.replace(a, b)

text = re.sub(
    r'\s*<div class="setting-row">\s*<div class="setting-label">\s*<div class="setting-icon[^"]*">[\s\S]*?<div><div>Language</div><div class="setting-desc">Language of the AI\'s replies</div></div>\s*</div>\s*<div class="seg-ctrl" id="langSeg">[\s\S]*?</div>\s*</div>',
    "\n",
    text,
    count=1,
)
text = re.sub(r"lang:\s*'auto'", "lang: 'en'", text)
text = text.replace(
    "document.querySelectorAll('#langSeg .seg-btn').forEach(b=>{ b.classList.toggle('active', b.dataset.val===appSettings.lang); });",
    "appSettings.lang = 'en';",
)

text = re.sub(
    r'\s*<div class="setting-row" onclick="showChangelog\(\)" style="cursor:pointer">[\s\S]*?id="appVersionDesc">[\s\S]*?</div>\s*</div>\s*</div>',
    "\n",
    text,
    count=1,
)
text = re.sub(
    r'\s*<!-- What\'s New / Changelog Modal -->\s*<div class="modal-overlay hidden" id="changelogModal">[\s\S]*?</div>\s*</div>',
    "\n",
    text,
    count=1,
)

# Structure fix for Clear History inside Settings
old_struct = """          <div><div>Privacy Policy</div><div class=\"setting-desc\">Opens in browser</div></div>
        </div>
      </div>
    </div>
      </div>

      </div>
    </div>

    </div>

    <!-- Danger -->"""
new_struct = """          <div><div>Privacy Policy</div><div class=\"setting-desc\">Opens in browser</div></div>
        </div>
      </div>
    </div>

    <!-- Danger -->"""
if old_struct in text:
    text = text.replace(old_struct, new_struct, 1)

text = text.replace(
    "function showChangelog(){\n  const list = $('changelogList');\n",
    "function showChangelog(){\n  const list = $('changelogList');\n  if(!list) return;\n",
)

text = re.sub(
    r"notifications:\s*\{\s*icon:'[^']*',\s*title:'[^']*',\s*body:'[^']*'\s*\}",
    "notifications: { icon:'🔔', title:'Notifications', body:'SKONGA can notify you when a reply is ready and when an app update is available. You can change this anytime in system settings.' }",
    text,
    count=1,
)

text = text.replace("const APP_VERSION = '1.3';", "const APP_VERSION = '1.4';", 1)
if "{ version:'1.4'" not in text:
    text = text.replace(
        "const CHANGELOG = [",
        """const CHANGELOG = [
  { version:'1.4', date:'August 2026', items:[
    'English-only UI. Language toggle removed.',
    'Upgrade removed from history sidebar — Pro in header.',
    'Clear history stays in Settings. App version row removed.',
    'Payment and limit copy professionalized.'
  ]},""",
        1,
    )

path.write_text(text, encoding="utf-8")
print("OK v1.4", path.stat().st_size)
