/**
 * skonga-profile-tahasusi.js
 * Study profile UI (English) + Form 1–6 + optional A-Level Combination.
 * Expected career fields stay on backend only — never shown to students.
 */
(function () {
  'use strict';

  var EXTRAS_KEY = 'skonga_user_extras';
  var API =
    (typeof API_BASE !== 'undefined' && API_BASE) ||
    'https://skonga-backend-v2.onrender.com';

  var LEVEL_LABELS = {
    form1: 'Form 1',
    form2: 'Form 2',
    form3: 'Form 3',
    form4: 'Form 4 (NECTA)',
    form5: 'Form 5',
    form6: 'Form 6 (ACSEE)',
    primary7: 'Standard 7 (PSLE)',
  };

  var combosCache = null;

  function getExtras() {
    try {
      return JSON.parse(localStorage.getItem(EXTRAS_KEY) || '{}') || {};
    } catch (e) {
      return {};
    }
  }

  function saveExtras(patch) {
    var cur = getExtras();
    Object.assign(cur, patch || {});
    try {
      localStorage.setItem(EXTRAS_KEY, JSON.stringify(cur));
    } catch (e) {}
    return cur;
  }

  function formNumberFromLevel(level) {
    var m = String(level || '').match(/form\s*([1-6])/i);
    return m ? Number(m[1]) : null;
  }

  function getProfilePayload() {
    var extras = getExtras();
    var level = extras.level || '';
    if (!level && typeof currentUser !== 'undefined' && currentUser && currentUser.level) {
      level = currentUser.level;
    }
    var formLevel = formNumberFromLevel(level);
    return {
      formLevel: formLevel,
      formHint: formLevel,
      combinationCode: extras.combinationCode || '',
      preferredSubjects: Array.isArray(extras.preferredSubjects)
        ? extras.preferredSubjects
        : [],
      level: level,
      levelLabel: extras.levelLabel || LEVEL_LABELS[level] || '',
    };
  }

  window.SKONGA_PROFILE = {
    get: getProfilePayload,
    getExtras: getExtras,
    save: saveExtras,
  };

  function injectCSS() {
    if (document.getElementById('skonga-tahasusi-css')) return;
    var s = document.createElement('style');
    s.id = 'skonga-tahasusi-css';
    s.textContent = [
      /* Professional study card */
      '.study-profile-box{margin:16px 0;border-radius:16px;overflow:hidden;',
      'border:1px solid rgba(168,85,247,.35);',
      'background:linear-gradient(165deg,rgba(124,58,237,.14) 0%,rgba(15,12,28,.92) 45%,rgba(6,182,212,.06) 100%);',
      'box-shadow:0 8px 28px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.06)}',
      '.study-profile-tabs{display:flex;border-bottom:1px solid rgba(168,85,247,.25)}',
      '.study-tab{flex:1;padding:12px 10px;border:none;background:transparent;',
      'font-family:var(--font-b);font-size:.78rem;font-weight:600;color:var(--text-muted);',
      'cursor:pointer;letter-spacing:.03em;position:relative;transition:color .2s,background .2s}',
      '.study-tab.active{color:#e9d5ff;background:rgba(124,58,237,.18)}',
      '.study-tab.active::after{content:"";position:absolute;left:12%;right:12%;bottom:0;',
      'height:3px;border-radius:3px 3px 0 0;',
      'background:linear-gradient(90deg,#7c3aed,#c084fc,#22d3ee)}',
      '.study-tab-body{padding:14px 14px 16px}',
      '.study-profile-box .field{margin-bottom:12px}',
      '.study-profile-box .field label{display:block;font-size:.72rem;color:var(--text-muted);',
      'margin-bottom:6px;letter-spacing:.02em}',
      '.study-profile-box select{width:100%;background:rgba(0,0,0,.28);',
      'border:1.5px solid rgba(168,85,247,.3);border-radius:12px;padding:12px 14px;',
      'font-family:var(--font-b);font-size:.88rem;color:var(--text-primary);outline:none;',
      'appearance:none;cursor:pointer;',
      'background-image:url("data:image/svg+xml,%3Csvg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23c084fc\' stroke-width=\'2\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpolyline points=\'6 9 12 15 18 9\'/%3E%3C/svg%3E");',
      'background-repeat:no-repeat;background-position:right 12px center;background-size:16px;padding-right:36px}',
      '.study-profile-box select:focus{border-color:#a855f7;box-shadow:0 0 0 3px rgba(168,85,247,.2)}',
      '#tahasusiWrap{display:none;margin-top:4px;padding-top:12px;',
      'border-top:1px dashed rgba(168,85,247,.25);animation:studySlide .25s ease}',
      '#tahasusiWrap.show{display:block}',
      '@keyframes studySlide{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}',
      '.combo-optional{font-size:.68rem;color:var(--cyan);margin:0 0 8px;font-weight:500}',
      '.combo-subjects{font-size:.75rem;color:var(--text-secondary);line-height:1.4;margin-top:8px;',
      'padding:8px 10px;border-radius:10px;background:rgba(34,211,238,.08);',
      'border:1px solid rgba(34,211,238,.2)}',
      '.study-save-btn{width:100%;margin-top:6px;padding:12px;border:none;border-radius:12px;',
      'background:linear-gradient(135deg,#7c3aed,#a855f7 50%,#06b6d4);color:#fff;',
      'font-family:var(--font-b);font-size:.88rem;font-weight:600;cursor:pointer;',
      'box-shadow:0 4px 16px rgba(124,58,237,.35)}',
      '.study-save-btn:active{opacity:.9;transform:scale(.98)}',
    ].join('');
    document.head.appendChild(s);
  }

  function cleanLevelSelect(sel) {
    if (!sel) return;
    Array.from(sel.options).forEach(function (opt) {
      if (String(opt.value).toLowerCase() === 'university') opt.remove();
    });
  }

  function loadCombinations() {
    if (combosCache) return Promise.resolve(combosCache);
    return fetch(API + '/api/tahasusi', { credentials: 'omit' })
      .then(function (r) {
        if (!r.ok) throw new Error('tahasusi http ' + r.status);
        return r.json();
      })
      .then(function (data) {
        combosCache = data.combinations || [];
        return combosCache;
      })
      .catch(function () {
        combosCache = [];
        return combosCache;
      });
  }

  function fillTahasusiSelect(selectEl, selectedCode) {
    if (!selectEl) return;
    var groups = {};
    (combosCache || []).forEach(function (c) {
      var cat = c.categoryNameEn || c.categoryNameSw || 'Other';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(c);
    });
    var html = '<option value="">Optional — skip if unsure</option>';
    Object.keys(groups).forEach(function (cat) {
      html += '<optgroup label="' + cat.replace(/"/g, '') + '">';
      groups[cat].forEach(function (c) {
        var label = c.code + ' — ' + (c.subjects || []).join(', ');
        var sel =
          selectedCode &&
          String(selectedCode).toUpperCase() === String(c.code).toUpperCase()
            ? ' selected'
            : '';
        html += '<option value="' + c.code + '"' + sel + '>' + label + '</option>';
      });
      html += '</optgroup>';
    });
    selectEl.innerHTML = html;
  }

  /** Subjects only — never show expected career fields to students */
  function updateComboSubjects(code, metaId) {
    var meta = document.getElementById(metaId || 'comboSubjects');
    if (!meta) return;
    if (!code) {
      meta.innerHTML = '';
      meta.style.display = 'none';
      return;
    }
    var found = (combosCache || []).find(function (c) {
      return String(c.code).toUpperCase() === String(code).toUpperCase();
    });
    if (!found) {
      meta.innerHTML = '';
      meta.style.display = 'none';
      return;
    }
    meta.style.display = 'block';
    meta.innerHTML =
      '<strong style="color:var(--text-primary)">Subjects:</strong> ' +
      (found.subjects || []).join(', ');
  }

  function toggleTahasusiVisibility(levelVal) {
    var wrap = document.getElementById('tahasusiWrap');
    if (!wrap) return;
    var n = formNumberFromLevel(levelVal);
    if (n === 5 || n === 6) {
      wrap.classList.add('show');
      // Auto-focus combination select when panel opens
      setTimeout(function () {
        var tah = document.getElementById('studyTahasusiSelect');
        if (tah) {
          try {
            tah.focus();
          } catch (e) {}
        }
      }, 80);
    } else {
      wrap.classList.remove('show');
    }
  }

  function buildStudyProfileUI() {
    var profileView = document.getElementById('profileView');
    if (!profileView) return;

    // Rebuild if already exists so copy stays English after updates
    var existing = document.getElementById('studyProfileBox');
    if (existing) existing.remove();

    var box = document.createElement('div');
    box.className = 'study-profile-box';
    box.id = 'studyProfileBox';
    box.innerHTML =
      '<div class="study-profile-tabs">' +
      '<button type="button" class="study-tab active" data-tab="level">Class level</button>' +
      '<button type="button" class="study-tab" data-tab="combo" id="studyTabCombo">Combination</button>' +
      '</div>' +
      '<div class="study-tab-body">' +
      '<div class="field">' +
      '<label>Your class / form</label>' +
      '<select id="studyLevelSelect">' +
      '<option value="">Select your form...</option>' +
      '<option value="primary7">Standard 7 (PSLE)</option>' +
      '<option value="form1">Form 1</option>' +
      '<option value="form2">Form 2</option>' +
      '<option value="form3">Form 3</option>' +
      '<option value="form4">Form 4 (NECTA)</option>' +
      '<option value="form5">Form 5</option>' +
      '<option value="form6">Form 6 (ACSEE)</option>' +
      '</select></div>' +
      '<div id="tahasusiWrap">' +
      '<p class="combo-optional">Recommended for Form 5–6 · optional</p>' +
      '<div class="field">' +
      '<label>What is your Combination?</label>' +
      '<select id="studyTahasusiSelect"><option value="">Loading...</option></select>' +
      '<div class="combo-subjects" id="comboSubjects" style="display:none"></div>' +
      '</div></div>' +
      '<button type="button" class="study-save-btn" id="studyProfileSave">Save study profile</button>' +
      '</div>';

    var logout = profileView.querySelector('.logout-btn');
    if (logout) profileView.insertBefore(box, logout);
    else profileView.appendChild(box);

    var extras = getExtras();
    var levelSel = document.getElementById('studyLevelSelect');
    var tahSel = document.getElementById('studyTahasusiSelect');
    var tabCombo = document.getElementById('studyTabCombo');

    if (levelSel && extras.level) levelSel.value = extras.level;
    toggleTahasusiVisibility(extras.level || '');

    // Tab highlight: when Form 5/6, switch active visual to Combination tab
    function syncTabs(levelVal) {
      var n = formNumberFromLevel(levelVal);
      box.querySelectorAll('.study-tab').forEach(function (t) {
        var isCombo = t.getAttribute('data-tab') === 'combo';
        t.classList.toggle('active', n === 5 || n === 6 ? isCombo : !isCombo);
      });
    }
    syncTabs(extras.level || '');

    box.querySelectorAll('.study-tab').forEach(function (t) {
      t.addEventListener('click', function () {
        box.querySelectorAll('.study-tab').forEach(function (x) {
          x.classList.remove('active');
        });
        t.classList.add('active');
        if (t.getAttribute('data-tab') === 'combo') {
          var n = formNumberFromLevel(levelSel.value);
          if (n === 5 || n === 6) {
            document.getElementById('tahasusiWrap').classList.add('show');
            if (tahSel) tahSel.focus();
          } else if (typeof showToast === 'function') {
            showToast('Select Form 5 or 6 first to set a combination.');
          }
        }
      });
    });

    levelSel.addEventListener('change', function () {
      toggleTahasusiVisibility(levelSel.value);
      syncTabs(levelSel.value);
    });

    loadCombinations().then(function () {
      fillTahasusiSelect(tahSel, extras.combinationCode || '');
      updateComboSubjects(extras.combinationCode || '');
    });

    if (tahSel) {
      tahSel.addEventListener('change', function () {
        updateComboSubjects(tahSel.value);
      });
    }

    document.getElementById('studyProfileSave').addEventListener('click', function () {
      var level = levelSel.value || '';
      var code = (tahSel && tahSel.value) || '';
      var formN = formNumberFromLevel(level);
      // Combination is optional — no hard block
      if (formN && formN < 5) code = '';

      var subjects = [];
      var found = (combosCache || []).find(function (c) {
        return String(c.code).toUpperCase() === String(code).toUpperCase();
      });
      if (found) subjects = found.subjects || [];

      saveExtras({
        level: level,
        levelLabel: LEVEL_LABELS[level] || level || '—',
        combinationCode: code,
        preferredSubjects: subjects,
      });

      try {
        if (typeof currentUser !== 'undefined' && currentUser) {
          currentUser.level = level;
          currentUser.levelLabel = LEVEL_LABELS[level] || level;
        }
      } catch (e) {}

      var pl = document.getElementById('profileLevel');
      if (pl) {
        pl.textContent =
          (LEVEL_LABELS[level] || level || '—') + (code ? ' · ' + code : '');
      }

      if (typeof showToast === 'function') showToast('Study profile saved.');
      try {
        refreshSuggestedTopics();
      } catch (e) {}
    });
  }

  function enhanceRegisterForm() {
    var reg = document.getElementById('regLevel');
    cleanLevelSelect(reg);
    if (!reg) return;

    if (!document.getElementById('regTahasusiWrap')) {
      var field = reg.closest('.field');
      if (field && field.parentNode) {
        var wrap = document.createElement('div');
        wrap.className = 'field';
        wrap.id = 'regTahasusiWrap';
        wrap.style.display = 'none';
        wrap.innerHTML =
          '<label>What is your Combination? <span style="color:var(--cyan);font-weight:500">(optional)</span></label>' +
          '<select id="regTahasusi"><option value="">Optional — skip if unsure</option></select>';
        field.parentNode.insertBefore(wrap, field.nextSibling);

        loadCombinations().then(function () {
          fillTahasusiSelect(document.getElementById('regTahasusi'), '');
        });

        reg.addEventListener('change', function () {
          var n = formNumberFromLevel(reg.value);
          wrap.style.display = n === 5 || n === 6 ? 'block' : 'none';
        });
      }
    }

    var origRegister = window.handleRegister;
    if (typeof origRegister === 'function' && !origRegister._tahPatched) {
      window.handleRegister = function () {
        try {
          var level = (document.getElementById('regLevel') || {}).value || '';
          var code = (document.getElementById('regTahasusi') || {}).value || '';
          var subjects = [];
          var found = (combosCache || []).find(function (c) {
            return String(c.code).toUpperCase() === String(code).toUpperCase();
          });
          if (found) subjects = found.subjects || [];
          saveExtras({
            level: level,
            levelLabel: LEVEL_LABELS[level] || level || '—',
            combinationCode: formNumberFromLevel(level) >= 5 ? code : '',
            preferredSubjects: subjects,
          });
        } catch (e) {}
        return origRegister.apply(this, arguments);
      };
      window.handleRegister._tahPatched = true;
    }
  }

  function interceptChatFetch() {
    if (typeof window.fetch !== 'function') return;
    var orig = window.fetch.bind(window);
    window.fetch = function (input, init) {
      var url = typeof input === 'string' ? input : input && input.url ? input.url : '';
      var isChat =
        url &&
        (url.indexOf('/api/chat') !== -1 || url.indexOf('/api/chat-search') !== -1) &&
        url.indexOf('/api/chat-title') === -1;

      if (isChat && init && init.body && typeof init.body === 'string') {
        try {
          var body = JSON.parse(init.body);
          var p = getProfilePayload();
          if (p.formLevel != null) {
            body.formLevel = p.formLevel;
            body.formHint = p.formLevel;
          }
          if (p.combinationCode) body.combinationCode = p.combinationCode;
          if (p.preferredSubjects && p.preferredSubjects.length) {
            body.preferredSubjects = p.preferredSubjects;
          }
          init = Object.assign({}, init, { body: JSON.stringify(body) });
        } catch (e) {}
      }
      return orig(input, init);
    };
  }

  function relabelTrending() {
    document.querySelectorAll('.trending-label').forEach(function (el) {
      if (el.textContent && /trending/i.test(el.textContent)) {
        el.innerHTML = el.innerHTML.replace(
          /Today's Trending Topics|Trending Topics/i,
          'Suggested Topics'
        );
      }
    });
  }

  function subjectMatch(cardSubject, allowed) {
    if (!allowed || !allowed.length) return true;
    var s = String(cardSubject || '').toLowerCase();
    return allowed.some(function (a) {
      var x = String(a).toLowerCase();
      return s.indexOf(x) !== -1 || x.indexOf(s) !== -1;
    });
  }

  function refreshSuggestedTopics() {
    relabelTrending();
    var p = getProfilePayload();
    var allowed = p.preferredSubjects || [];
    if (!allowed.length) return;
    if (
      typeof trendingCardsData !== 'undefined' &&
      Array.isArray(trendingCardsData) &&
      trendingCardsData.length
    ) {
      var filtered = trendingCardsData.filter(function (c) {
        return subjectMatch(c.subject, allowed);
      });
      if (filtered.length && typeof renderTrendingCards === 'function') {
        renderTrendingCards(filtered);
      }
    }
  }

  function patchTrendingRenderer() {
    if (typeof renderTrendingCards !== 'function' || renderTrendingCards._tahPatched) return;
    var orig = renderTrendingCards;
    window.renderTrendingCards = function (cards) {
      relabelTrending();
      var p = getProfilePayload();
      var allowed = p.preferredSubjects || [];
      var list = cards || [];
      if (allowed.length) {
        var filtered = list.filter(function (c) {
          return subjectMatch(c.subject, allowed);
        });
        if (filtered.length) list = filtered;
      }
      return orig(list);
    };
    window.renderTrendingCards._tahPatched = true;
  }

  function enhanceProfileLevelDisplay() {
    try {
      var extras = getExtras();
      var pl = document.getElementById('profileLevel');
      if (pl && extras.level) {
        pl.textContent =
          (extras.levelLabel || LEVEL_LABELS[extras.level] || extras.level) +
          (extras.combinationCode ? ' · ' + extras.combinationCode : '');
      }
    } catch (e) {}
  }

  function patchUpdateProfileView() {
    if (typeof updateProfileView !== 'function' || updateProfileView._tahPatched) return;
    var orig = updateProfileView;
    window.updateProfileView = function () {
      var r = orig.apply(this, arguments);
      try {
        buildStudyProfileUI();
        enhanceProfileLevelDisplay();
      } catch (e) {}
      return r;
    };
    window.updateProfileView._tahPatched = true;
  }

  function boot() {
    injectCSS();
    interceptChatFetch();
    enhanceRegisterForm();
    patchUpdateProfileView();
    patchTrendingRenderer();
    relabelTrending();
    enhanceProfileLevelDisplay();

    var n = 0;
    var t = setInterval(function () {
      n++;
      patchUpdateProfileView();
      patchTrendingRenderer();
      enhanceRegisterForm();
      if (n > 40) clearInterval(t);
    }, 250);

    loadCombinations();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
