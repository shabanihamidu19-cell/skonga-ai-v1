#!/usr/bin/env python3
"""Inject userId (Firebase uid) into chat API body."""
from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
html = p.read_text(encoding="utf-8")

old = """body: JSON.stringify({
        message: text,
        lang: appSettings.lang,
        style: appSettings.style,
        userName: appSettings.userName,
        identityQuestionCount,
        history: conversationMemory.slice(0, -1),
        sessionId: DEVICE_SESSION_ID,
        notifyOnComplete: appSettings.notificationsEnabled && isNativeApp,
        formHint: getStudentFormHint(),
      })"""

new = """body: JSON.stringify({
        message: text,
        lang: appSettings.lang,
        style: appSettings.style,
        userName: appSettings.userName,
        identityQuestionCount,
        history: conversationMemory.slice(0, -1),
        sessionId: DEVICE_SESSION_ID,
        notifyOnComplete: appSettings.notificationsEnabled && isNativeApp,
        formHint: getStudentFormHint(),
        // Usage quota: Firebase uid → AI backend → auth-content-service
        userId: (window._fb && window._fb.currentUser && window._fb.currentUser.uid) || null,
      })"""

if old not in html:
    print("SKIP: chat body pattern not found (already wired?)")
else:
    html = html.replace(old, new, 1)
    print("OK: chat userId wired")

# Handle 403 QUOTA_EXCEEDED with clearer message (optional soft touch)
old2 = """if(!res.ok){
      let errMsg='Tatizo la server limetokea';
      try{ const errData=await res.json(); if(errData.error) errMsg=errData.error; }catch(_){}
      throw new Error(errMsg);
    }"""

new2 = """if(!res.ok){
      let errMsg='Tatizo la server limetokea';
      try{
        const errData=await res.json();
        if(errData.code==='QUOTA_EXCEEDED'){
          errMsg=errData.error||'Daily free limit reached. Upgrade to Pro.';
          try{ if(typeof openPaySheet==='function') openPaySheet(); }catch(_){}
        } else if(errData.error) errMsg=errData.error;
      }catch(_){}
      throw new Error(errMsg);
    }"""

if old2 in html:
    html = html.replace(old2, new2, 1)
    print("OK: QUOTA_EXCEEDED handling")
else:
    print("SKIP: error handler pattern")

p.write_text(html, encoding="utf-8")
print("Wrote", p.resolve())
