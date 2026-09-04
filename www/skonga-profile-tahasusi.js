/**
 * skonga-profile-tahasusi.js
 * - Removes University from level picker
 * - Study profile: Form 1–6 + Tahasusi (Form 5–6)
 * - Saves to localStorage (skonga_user_extras)
 * - Injects formLevel + combinationCode into /api/chat and /api/chat-search
 * - Relabels Trending → Suggested Topics and filters by combination subjects
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
    primary7: 'Darasa la 7 (PSLE)',
  };

  var combosCache = null;
  var categoriesCache = null;

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

  /* ── CSS ── */
  function injectCSS() {
    if (document.getElementById('skonga-tahasusi-css')) return;
    var s = document.createElement('style');
    s.id = 'skonga-tahasusi-css';
    s.textContent = [
      '.study-profile-box{margin:14px 0;padding:14px;border-radius:14px;border:1px solid var(--border);background:rgba(124,58,237,.08)}',
      '.study-profile-box h4{margin:0 0 10px;font-size:.82rem;color:var(--purple-light);letter-spacing:.04em;text-transform:uppercase}',
      '.study-profile-box .field{margin-bottom:10px}',
      '.study-profile-box .field:last-child{margin-bottom:0}',
      '#tahasusiWrap{display:none}',
      '#tahasusiWrap.show{display:block}',
      '.combo-meta{font-size:.72rem;color:var(--text-secondary);line-height:1.45;margin-top:8px}',
      '.combo-meta strong{color:var(--text-primary)}',
      '.study-save-btn{width:100%;margin-top:10px;padding:11px;border:none;border-radius:11px;background:linear-gradient(135deg,var(--purple-main),var(--purple-mid));color:#fff;font-family:var(--font-b);font-size:.85rem;font-weight:600;cursor:pointer}',
      '.study-save-btn:active{opacity:.9}',
    ].join('');
    document.head.appendChild(s);
  }

  /* ── Remove University option ── */
  function cleanLevelSelect(sel) {
    if (!sel) return;
    Array.from(sel.options).forEach(function (opt) {
      if (String(opt.value).toLowerCase() === 'university') {
        opt.remove();
      }
    });
  }

  /* ── Load combinations from API ── */
  function loadCombinations() {
    if (combosCache) return Promise.resolve(combosCache);
    return fetch(API + '/api/tahasusi', { credentials: 'omit' })
      .then(function (r) {
        if (!r.ok) throw new Error('tahasusi http ' + r.status);
        return r.json();
      })
      .then(function (data) {
        combosCache = data.combinations || [];
        categoriesCache = data.categories || [];
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
      var cat = c.categoryNameSw || c.categoryNameEn || 'Nyingine';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(c);
    });
    var html = '<option value="">Chagua tahasusi yako...</option>';
    Object.keys(groups).forEach(function (cat) {
      html += '<optgroup label="' + cat.replace(/"/g, '') + '">';
      groups[cat].forEach(function (c) {
        var label = c.code + ' — ' + (c.subjects || []).join(', ');
        var sel = selectedCode && String(selectedCode).toUpperCase() === String(c.code).toUpperCase() ? ' selected' : '';
        html += '<option value="' + c.code + '"' + sel + '>' + label + '</option>';
      });
      html += '</optgroup>';
    });
    selectEl.innerHTML = html;
  }

  function updateComboMeta(code) {
    var meta = document.getElementById('comboMeta');
    if (!meta) return;
    if (!code) {
      meta.innerHTML = '';
      return;
    }
    var found = (combosCache || []).find(function (c) {
      return String(c.code).toUpperCase() === String(code).toUpperCase();
    });
    if (!found) {
      meta.innerHTML = '';
      return;
    }
    meta.innerHTML =
      '<strong>Masomo:</strong> ' +
      (found.subjects || []).join(', ') +
      '<br/><strong>Njia za kazi:</strong> ' +
      (found.fields || []).slice(0, 8).join(', ') +
      ((found.fields || []).length > 8 ? '…' : '');
  }

  function toggleTahasusiVisibility(levelVal) {
    var wrap = document.getElementById('tahasusiWrap');
    if (!wrap) return;
    var n = formNumberFromLevel(levelVal);
    if (n === 5 || n === 6) wrap.classList.add('show');
    else wrap.classList.remove('show');
  }

  function buildStudyProfileUI() {
    var profileView = document.getElementById('profileView');
    if (!profileView || document.getElementById('studyProfileBox')) return;

    var box = document.createElement('div');
    box.className = 'study-profile-box';
    box.id = 'studyProfileBox';
    box.innerHTML =
      '<h4>Wasifu wa masomo</h4>' +
      '<div class="field"><label>Darasa / Kidato</label>' +
      '<select id="studyLevelSelect">' +
      '<option value="">Chagua darasa...</option>' +
      '<option value="primary7">Darasa la 7 (PSLE)</option>' +
      '<option value="form1">Form 1</option>' +
      '<option value="form2">Form 2</option>' +
      '<option value="form3">Form 3</option>' +
      '<option value="form4">Form 4 (NECTA)</option>' +
      '<option value="form5">Form 5</option>' +
      '<option value="form6">Form 6 (ACSEE)</option>' +
      '</select></div>' +
      '<div class="field" id="tahasusiWrap">' +
      '<label>Tahasusi (Form 5–6)</label>' +
      '<select id="studyTahasusiSelect"><option value="">Inapakia...</option></select>' +
      '<div class="combo-meta" id="comboMeta"></div>' +
      '</div>' +
      '<button type="button" class="study-save-btn" id="studyProfileSave">Hifadhi wasifu</button>';

    var logout = profileView.querySelector('.logout-btn');
    if (logout) profileView.insertBefore(box, logout);
    else profileView.appendChild(box);

    var extras = getExtras();
    var levelSel = document.getElementById('studyLevelSelect');
    var tahSel = document.getElementById('studyTahasusiSelect');
    if (levelSel && extras.level) levelSel.value = extras.level;
    toggleTahasusiVisibility(extras.level || '');

    levelSel.addEventListener('change', function () {
      toggleTahasusiVisibility(levelSel.value);
    });

    loadCombinations().then(function () {
      fillTahasusiSelect(tahSel, extras.combinationCode || '');
      updateComboMeta(extras.combinationCode || '');
    });

    if (tahSel) {
      tahSel.addEventListener('change', function () {
        updateComboMeta(tahSel.value);
      });
    }

    document.getElementById('studyProfileSave').addEventListener('click', function () {
      var level = levelSel.value || '';
      var code = (tahSel && tahSel.value) || '';
      var formN = formNumberFromLevel(level);
      if ((formN === 5 || formN === 6) && !code) {
        if (typeof showToast === 'function') {
          showToast('Chagua tahasusi yako (Form 5/6).', true);
        }
        return;
      }
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
          (LEVEL_LABELS[level] || level || '—') +
          (code ? ' · ' + code : '');
      }

      if (typeof showToast === 'function') showToast('Wasifu wa masomo umehifadhiwa.');
      try {
        refreshSuggestedTopics();
      } catch (e) {}
    });
  }

  /* ── Register form: remove university + show tahasusi on form5/6 ── */
  function enhanceRegisterForm() {
    var reg = document.getElementById('regLevel');
    cleanLevelSelect(reg);
    if (!reg) return;

    // Insert tahasusi under regLevel if missing
    if (!document.getElementById('regTahasusiWrap')) {
      var field = reg.closest('.field');
      if (field && field.parentNode) {
        var wrap = document.createElement('div');
        wrap.className = 'field';
        wrap.id = 'regTahasusiWrap';
        wrap.style.display = 'none';
        wrap.innerHTML =
          '<label>Tahasusi (Form 5–6)</label>' +
          '<select id="regTahasusi"><option value="">Chagua tahasusi...</option></select>';
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

    // Patch handleRegister extras after submit — monkey via submit button path
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

  /* ── Inject profile into chat API bodies ── */
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

  /* ── Suggested topics (relabel + filter) ── */
  function relabelTrending() {
    document.querySelectorAll('.trending-label').forEach(function (el) {
      if (el.textContent && /trending/i.test(el.textContent)) {
        el.innerHTML = el.innerHTML.replace(/Today's Trending Topics|Trending Topics/i, 'Suggested Topics');
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

    // Filter currently rendered cards if possible
    if (typeof trendingCardsData !== 'undefined' && Array.isArray(trendingCardsData) && trendingCardsData.length) {
      var filtered = trendingCardsData.filter(function (c) {
        return subjectMatch(c.subject, allowed);
      });
      if (filtered.length && typeof renderTrendingCards === 'function') {
        renderTrendingCards(filtered);
      }
    }
  }

  // Patch renderTrendingCards to filter + relabel
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

  // Patch updateProfileView to rebuild study box
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

    // Retry patches if main script defines functions later
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
