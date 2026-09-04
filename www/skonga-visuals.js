/**
 * skonga-visuals.js
 * Shows images/diagrams from Live Search sources next to the AI reply.
 * Loaded by update-check.js — no need to rebuild index.html for this feature.
 *
 * Expects backend /api/chat-search to return:
 *   sources[].image  and/or  visuals: [{ imageUrl, caption, sourceUrl, sourceTitle, domain }]
 */
(function () {
  'use strict';

  var lastVisuals = [];

  function injectCSS() {
    if (document.getElementById('skonga-visuals-css')) return;
    var style = document.createElement('style');
    style.id = 'skonga-visuals-css';
    style.textContent = [
      '.visuals-block{margin-top:12px}',
      '.visuals-label{display:flex;align-items:center;gap:6px;font-size:.72rem;color:var(--text-muted);margin-bottom:8px;font-weight:600;letter-spacing:.02em}',
      '.visuals-label svg{width:14px;height:14px;flex-shrink:0}',
      '.visuals-scroll{display:flex;gap:10px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px;scroll-snap-type:x mandatory}',
      '.visuals-scroll::-webkit-scrollbar{height:4px}',
      '.visuals-scroll::-webkit-scrollbar-thumb{background:var(--purple-mid);border-radius:4px}',
      '.visual-card{flex-shrink:0;width:160px;scroll-snap-align:start;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:12px;overflow:hidden;cursor:pointer;text-decoration:none;color:inherit;display:block;transition:border-color .15s,transform .15s}',
      '.visual-card:active{transform:scale(.98)}',
      '.visual-card:hover{border-color:var(--purple-mid)}',
      '.visual-card img{width:100%;height:110px;object-fit:cover;display:block;background:var(--bg-primary)}',
      '.visual-card-meta{padding:8px 9px}',
      '.visual-card-caption{font-size:.72rem;line-height:1.35;color:var(--text-primary);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}',
      '.visual-card-domain{font-size:.65rem;color:var(--text-muted);margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
      '.source-card-thumb{width:100%;height:72px;object-fit:cover;border-radius:8px;margin-bottom:6px;background:var(--bg-primary);display:block}',
      '.visual-lightbox{position:fixed;inset:0;z-index:120;background:rgba(0,0,0,.85);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:16px;animation:fadeUp .2s ease}',
      '.visual-lightbox img{max-width:100%;max-height:75vh;border-radius:12px;object-fit:contain}',
      '.visual-lightbox-bar{margin-top:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;justify-content:center}',
      '.visual-lightbox a,.visual-lightbox button{font-size:.8rem;padding:8px 14px;border-radius:10px;border:1px solid var(--border);background:var(--bg-elevated);color:var(--text-primary);cursor:pointer;text-decoration:none}',
    ].join('');
    document.head.appendChild(style);
  }

  function esc(s) {
    if (typeof escapeHtml === 'function') return escapeHtml(String(s || ''));
    return String(s || '')
      .replace(/&/g, '&')
      .replace(/</g, '<')
      .replace(/>/g, '>')
      .replace(/"/g, '"');
  }

  function collectVisuals(sources, extraVisuals) {
    var out = [];
    var seen = {};
    function push(v) {
      if (!v || !v.imageUrl) return;
      if (seen[v.imageUrl]) return;
      seen[v.imageUrl] = true;
      out.push(v);
    }
    (extraVisuals || []).forEach(function (v) {
      push({
        imageUrl: v.imageUrl || v.url || v.image,
        caption: v.caption || v.sourceTitle || v.title || 'Visual',
        sourceUrl: v.sourceUrl || v.url || '',
        sourceTitle: v.sourceTitle || v.title || '',
        domain: v.domain || '',
      });
    });
    (sources || []).forEach(function (s) {
      if (!s || !s.image) return;
      push({
        imageUrl: s.image,
        caption: s.title || s.title_en || 'Visual',
        sourceUrl: s.url || '',
        sourceTitle: s.title || '',
        domain: s.domain || '',
      });
    });
    return out.slice(0, 6);
  }

  function buildVisualsHtml(visuals) {
    if (!visuals || !visuals.length) return '';
    var cards = visuals
      .map(function (v, i) {
        var caption = esc(v.caption || 'Visual');
        var domain = esc(v.domain || '');
        var src = esc(v.imageUrl);
        var href = v.sourceUrl && v.sourceUrl !== '#' ? esc(v.sourceUrl) : '';
        return (
          '<button type="button" class="visual-card" data-v-idx="' +
          i +
          '">' +
          '<img src="' +
          src +
          '" alt="' +
          caption +
          '" loading="lazy" onerror="this.closest(\'.visual-card\').style.display=\'none\'"/>' +
          '<div class="visual-card-meta">' +
          '<div class="visual-card-caption">' +
          caption +
          '</div>' +
          (domain ? '<div class="visual-card-domain">' + domain + '</div>' : '') +
          '</div></button>'
        );
      })
      .join('');
    return (
      '<div class="visuals-block">' +
      '<div class="visuals-label">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>' +
      'Picha / Dicharts kutoka sources' +
      '</div>' +
      '<div class="visuals-scroll" data-visuals="1">' +
      cards +
      '</div></div>'
    );
  }

  function openLightbox(v) {
    var existing = document.getElementById('skonga-visual-lightbox');
    if (existing) existing.remove();
    var box = document.createElement('div');
    box.id = 'skonga-visual-lightbox';
    box.className = 'visual-lightbox';
    box.innerHTML =
      '<img src="' +
      esc(v.imageUrl) +
      '" alt=""/>' +
      '<div class="visual-lightbox-bar">' +
      (v.sourceUrl
        ? '<a href="' + esc(v.sourceUrl) + '" target="_blank" rel="noopener noreferrer">Fungua source</a>'
        : '') +
      '<button type="button" id="skonga-lb-close">Funga</button>' +
      '</div>';
    document.body.appendChild(box);
    function close() {
      try {
        box.remove();
      } catch (e) {}
    }
    box.addEventListener('click', function (e) {
      if (e.target === box) close();
    });
    var btn = document.getElementById('skonga-lb-close');
    if (btn) btn.addEventListener('click', close);
  }

  function bindVisualClicks(root, visuals) {
    if (!root || !visuals) return;
    root.querySelectorAll('.visual-card').forEach(function (el) {
      el.addEventListener('click', function () {
        var idx = parseInt(el.getAttribute('data-v-idx') || '0', 10);
        var v = visuals[idx];
        if (v) openLightbox(v);
      });
    });
  }

  function enhanceBuildSourcesHtml() {
    if (typeof buildSourcesHtml !== 'function') return;
    var original = buildSourcesHtml;
    window.buildSourcesHtml = function (sources) {
      var html = original(sources);
      // Add thumbnail on source cards that have image
      if (!sources || !sources.length) return html;
      try {
        // Rebuild with thumbs for non-curriculum cards that have image
        // Keep original structure; inject thumbs via post-process string is fragile.
        // Instead append visuals block separately in streamMessage wrapper.
      } catch (e) {}
      return html;
    };
    // Also expose original for safety
    window.__buildSourcesHtmlOriginal = original;
  }

  function enhanceStreamMessage() {
    if (typeof streamMessage !== 'function') return;
    var original = streamMessage;
    window.streamMessage = function (fullText, onDone, sources, graphData, practiceQ) {
      var visuals = collectVisuals(sources, lastVisuals);
      // Clear one-shot visuals after consume
      lastVisuals = [];

      var wrappedDone = function () {
        try {
          // After original finalize, find the last bot bubble and inject visuals if missing
          var rows = document.querySelectorAll('#chat-area .msg-row.bot');
          var last = rows[rows.length - 1];
          if (last && visuals.length) {
            var content = last.querySelector('.md-content') || last.querySelector('.bubble');
            if (content && !content.querySelector('.visuals-block')) {
              content.insertAdjacentHTML('beforeend', buildVisualsHtml(visuals));
              bindVisualClicks(content, visuals);
            }
          }
        } catch (e) {}
        if (typeof onDone === 'function') onDone();
      };

      // Prefer injecting inside finalize: wrap by calling original with enhanced onDone
      // But original finalize already ran sources — so we inject after via MutationObserver briefly
      var result = original.call(this, fullText, wrappedDone, sources, graphData, practiceQ);

      // Also try immediate inject after short delay (streaming may still run)
      if (visuals.length) {
        var tries = 0;
        var timer = setInterval(function () {
          tries++;
          try {
            var rows = document.querySelectorAll('#chat-area .msg-row.bot');
            var last = rows[rows.length - 1];
            if (!last) return;
            var content = last.querySelector('.md-content') || last.querySelector('.bubble');
            if (!content) return;
            // Wait until streaming finished (no ai-cursor)
            if (last.querySelector('.ai-cursor') && tries < 40) return;
            if (!content.querySelector('.visuals-block')) {
              content.insertAdjacentHTML('beforeend', buildVisualsHtml(visuals));
              bindVisualClicks(content, visuals);
            }
            clearInterval(timer);
          } catch (e) {
            if (tries > 40) clearInterval(timer);
          }
          if (tries > 40) clearInterval(timer);
        }, 200);
      }

      return result;
    };
  }

  function interceptChatSearchFetch() {
    if (typeof window.fetch !== 'function') return;
    var origFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
      var url = typeof input === 'string' ? input : input && input.url ? input.url : '';
      var p = origFetch(input, init);
      if (url && url.indexOf('/api/chat-search') !== -1) {
        return p.then(function (res) {
          try {
            var clone = res.clone();
            clone.json().then(function (data) {
              if (data && Array.isArray(data.visuals) && data.visuals.length) {
                lastVisuals = data.visuals;
              } else if (data && Array.isArray(data.sources)) {
                lastVisuals = collectVisuals(data.sources, []);
              }
            }).catch(function () {});
          } catch (e) {}
          return res;
        });
      }
      return p;
    };
  }

  function boot() {
    injectCSS();
    interceptChatSearchFetch();
    // Retry briefly in case streamMessage is defined later
    var n = 0;
    var t = setInterval(function () {
      n++;
      if (typeof streamMessage === 'function') {
        enhanceStreamMessage();
        enhanceBuildSourcesHtml();
        clearInterval(t);
      }
      if (n > 50) clearInterval(t);
    }, 200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window.SKONGA_VISUALS = {
    setLastVisuals: function (v) {
      lastVisuals = v || [];
    },
    buildVisualsHtml: buildVisualsHtml,
  };
})();
