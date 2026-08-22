#!/usr/bin/env python3
"""Expand LIVE_INFO_KEYWORDS + shouldSearch for web intents."""
from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
html = p.read_text(encoding="utf-8")

OLD = '''const LIVE_INFO_KEYWORDS = [
  "latest","today","currently","current news","breaking","update on","recent",
  "this week","this year","score","match result","election result","weather",
  "forecast","temperature today","exchange rate","stock price","news about",
  "who is the current","who is the president","prime minister","who won","live","right now",
  "tafuta","tafuteni","chunguza mtandao","habari za leo","habari mpya","habari za hivi punde",
  "matokeo ya","necta","tamisemi","tie.go.tz","matokeo ya mtihani","matokeo ya kidato",
  "matokeo ya darasa","hali ya hewa","bei ya","kiwango cha ubadilishaji","soko la fedha",
  "uchaguzi","rais wa sasa","waziri mkuu wa sasa","mchezo wa leo","matokeo ya mchezo",
  "ripoti mpya","habari za sasa","sasa hivi kuna","nani ni","who is"
];'''

NEW = '''const LIVE_INFO_KEYWORDS = [
  "latest","today","currently","current news","breaking","update on","recent",
  "this week","this year","score","match result","election result","weather",
  "forecast","temperature today","exchange rate","stock price","news about",
  "who is the current","who is the president","prime minister","who won","live","right now",
  "tafuta","tafuteni","chunguza mtandao","habari za leo","habari mpya","habari za hivi punde",
  "matokeo ya","necta","tamisemi","tie.go.tz","matokeo ya mtihani","matokeo ya kidato",
  "matokeo ya darasa","hali ya hewa","bei ya","kiwango cha ubadilishaji","soko la fedha",
  "uchaguzi","rais wa sasa","waziri mkuu wa sasa","mchezo wa leo","matokeo ya mchezo",
  "ripoti mpya","habari za sasa","sasa hivi kuna","nani ni","who is",
  "from net","from the net","from internet","from the internet","on the internet",
  "search the web","search online","google","kutoka mtandao","kutoka net",
  "what is new","what's new","whats new","nini kipya","news","current events","trending"
];'''

if OLD not in html:
    print("SKIP: LIVE_INFO_KEYWORDS block not found exactly")
else:
    html = html.replace(OLD, NEW, 1)
    print("OK: LIVE_INFO_KEYWORDS")

OLD_FN = '''function shouldSearch(message){
  if(!message || typeof message!=='string') return false;
  const text = message.trim();
  if(!text) return false;
  if(GREETING_ONLY_RE.test(text)) return false;
  if(PURE_MATH_RE.test(text) && text.length<=20) return false;
  const lower = text.toLowerCase();
  const hasFutureYear = /\\b(202[6-9]|20[3-9]\\d)\\b/.test(lower);
  const isQuestionish = /[?]|nini|nani|vipi|lini|wapi|what|when|where|which|who|how/.test(lower);
  if(hasFutureYear && isQuestionish) return true;
  return LIVE_INFO_KEYWORDS.some(kw=>lower.includes(kw));
}'''

NEW_FN = '''function shouldSearch(message){
  if(!message || typeof message!=='string') return false;
  const text = message.trim();
  if(!text) return false;
  if(GREETING_ONLY_RE.test(text)) return false;
  if(PURE_MATH_RE.test(text) && text.length<=20) return false;
  const lower = text.toLowerCase();
  if(/\\bfrom\\s+(the\\s+)?(net|internet|web)\\b/.test(lower)) return true;
  if(/\\b(search|find)\\s+(online|the\\s+web|on\\s+the\\s+web)\\b/.test(lower)) return true;
  if(/\\bwhat'?s?\\s+new\\b/.test(lower) || /\\bnini\\s+kipya\\b/.test(lower)) return true;
  const hasFutureYear = /\\b(202[6-9]|20[3-9]\\d)\\b/.test(lower);
  const isQuestionish = /[?]|nini|nani|vipi|lini|wapi|what|when|where|which|who|how/.test(lower);
  if(hasFutureYear && isQuestionish) return true;
  return LIVE_INFO_KEYWORDS.some(kw=>lower.includes(kw));
}'''

# The file uses single-escaped regex in JS - match without python double escape issues
old_fn_real = """function shouldSearch(message){
  if(!message || typeof message!=='string') return false;
  const text = message.trim();
  if(!text) return false;
  if(GREETING_ONLY_RE.test(text)) return false;
  if(PURE_MATH_RE.test(text) && text.length<=20) return false;
  const lower = text.toLowerCase();
  const hasFutureYear = /\\b(202[6-9]|20[3-9]\\d)\\b/.test(lower);
  const isQuestionish = /[?]|nini|nani|vipi|lini|wapi|what|when|where|which|who|how/.test(lower);
  if(hasFutureYear && isQuestionish) return true;
  return LIVE_INFO_KEYWORDS.some(kw=>lower.includes(kw));
}"""

# Read actual from file between function shouldSearch and needsReasoning
import re
m = re.search(r"function shouldSearch\(message\)\{[\s\S]*?\n\}\nfunction needsReasoning", html)
if m and "from\\s+(the\\s+)?(net|internet|web)" not in m.group(0):
    new_block = '''function shouldSearch(message){
  if(!message || typeof message!=='string') return false;
  const text = message.trim();
  if(!text) return false;
  if(GREETING_ONLY_RE.test(text)) return false;
  if(PURE_MATH_RE.test(text) && text.length<=20) return false;
  const lower = text.toLowerCase();
  if(/\\bfrom\\s+(the\\s+)?(net|internet|web)\\b/.test(lower)) return true;
  if(/\\b(search|find)\\s+(online|the\\s+web|on\\s+the\\s+web)\\b/.test(lower)) return true;
  if(/\\bwhat'?s?\\s+new\\b/.test(lower) || /\\bnini\\s+kipya\\b/.test(lower)) return true;
  const hasFutureYear = /\\b(202[6-9]|20[3-9]\\d)\\b/.test(lower);
  const isQuestionish = /[?]|nini|nani|vipi|lini|wapi|what|when|where|which|who|how/.test(lower);
  if(hasFutureYear && isQuestionish) return true;
  return LIVE_INFO_KEYWORDS.some(kw=>lower.includes(kw));
}
function needsReasoning'''
    html = html[:m.start()] + new_block + html[m.end()-len("function needsReasoning"):]
    print("OK: shouldSearch function")
elif m and "from\\s+(the\\s+)?(net|internet|web)" in m.group(0):
    print("OK: shouldSearch already patched")
else:
    print("SKIP: shouldSearch not found")

p.write_text(html, encoding="utf-8")
print("Wrote", p)
