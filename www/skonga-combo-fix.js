/* Force offline-first combinations so UI never stays on Loading… */
(function () {
  function apply() {
    var list = (window.SKONGA_TAHASUSI_FALLBACK || []).slice();
    if (!list.length) return;

    function paintGrid(container) {
      if (!container) return;
      var groups = {};
      list.forEach(function (c) {
        var cat = c.categoryNameEn || c.categoryNameSw || 'Other';
        if (!groups[cat]) groups[cat] = [];
        groups[cat].push(c);
      });
      var html = '';
      Object.keys(groups).forEach(function (cat) {
        html += '<div class="ob-cat">' + cat.replace(/</g, '') + '</div><div class="ob-grid">';
        groups[cat].forEach(function (c) {
          var sub = (c.subjects || []).join(', ');
          html +=
            '<button type="button" class="ob-cell" data-code="' +
            String(c.code).replace(/"/g, '') +
            '" title="' +
            (c.code + ' — ' + sub).replace(/"/g, '"') +
            '">' +
            String(c.code).replace(/</g, '') +
            '</button>';
        });
        html += '</div>';
      });
      container.innerHTML = html;
      container.querySelectorAll('.ob-cell').forEach(function (btn) {
        btn.addEventListener('click', function () {
          container.querySelectorAll('.ob-cell').forEach(function (b) {
            b.classList.toggle('selected', b === btn);
          });
          var code = btn.getAttribute('data-code') || '';
          var found = list.find(function (c) {
            return String(c.code).toUpperCase() === code.toUpperCase();
          });
          var tag = document.getElementById('obSelectedCombo');
          if (tag && found) {
            tag.innerHTML =
              '<strong>' + found.code + '</strong> — ' + (found.subjects || []).join(', ');
          }
          try {
            window.__skongaSelectedCombo = code;
            // Sync with onboard selectedCombo if same page
            var levelBtn = document.querySelector('#obLevelGrid .ob-cell.selected');
            // Store into extras on Continue is handled by onboard; also patch save
          } catch (e) {}
        });
      });
    }

    function fillSelect(sel) {
      if (!sel || !sel.options) return;
      if (sel.options.length > 2) return; // already filled
      var groups = {};
      list.forEach(function (c) {
        var cat = c.categoryNameEn || 'Other';
        if (!groups[cat]) groups[cat] = [];
        groups[cat].push(c);
      });
      var html = '<option value="">Optional — skip if unsure</option>';
      Object.keys(groups).forEach(function (cat) {
        html += '<optgroup label="' + cat.replace(/"/g, '') + '">';
        groups[cat].forEach(function (c) {
          html +=
            '<option value="' +
            c.code +
            '">' +
            c.code +
            ' — ' +
            (c.subjects || []).join(', ') +
            '</option>';
        });
        html += '</optgroup>';
      });
      sel.innerHTML = html;
    }

    function tryPaint() {
      var grid = document.getElementById('obComboGrid');
      if (grid && /Loading/i.test(grid.textContent || '')) {
        paintGrid(grid);
      }
      fillSelect(document.getElementById('regTahasusi'));
      fillSelect(document.getElementById('studyTahasusiSelect'));
    }

    tryPaint();
    var n = 0;
    var t = setInterval(function () {
      n++;
      tryPaint();
      if (n > 50) clearInterval(t);
    }, 300);

    try {
      var obs = new MutationObserver(function () {
        tryPaint();
      });
      obs.observe(document.body, { childList: true, subtree: true });
    } catch (e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', apply);
  } else {
    apply();
  }
  setTimeout(apply, 400);
  setTimeout(apply, 1200);
  setTimeout(apply, 3000);
})();
