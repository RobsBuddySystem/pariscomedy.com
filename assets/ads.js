// pariscomedy.com affiliate ad slot renderer.
// Reads /data/ad_slots.json; if enabled, populates every
// <div data-ad-slot="<slot-name>"></div> placeholder on the current page.
// When disabled OR network ref is blank, renders nothing (slots stay invisible).
// One-command rollback: bash scripts/disable_affiliate_ads.sh.
(async function () {
  let cfg;
  try {
    cfg = await fetch('/data/ad_slots.json', {cache: 'no-store'}).then(r => r.json());
  } catch (_) {
    return; // No config → no ads.
  }
  if (!cfg || !cfg.enabled) return;

  const slots = document.querySelectorAll('[data-ad-slot]');
  if (!slots.length) return;

  function render(slotEl, slotName) {
    const slotCfg = (cfg.slots || {})[slotName];
    if (!slotCfg) return;
    const net = (cfg.networks || {})[slotCfg.network];
    if (!net || !net.ref) return; // No ref → no ad.

    const wrap = document.createElement('aside');
    wrap.className = 'pc-ad-slot pc-ad-' + (slotCfg.kind || 'default');
    wrap.setAttribute('data-network', slotCfg.network);
    wrap.style.cssText = 'border:1px solid #1e1e1e;border-radius:10px;padding:14px 16px;margin:18px 0;background:#0f0f0f;font-size:13px;line-height:1.5;color:#ccc;display:block';
    wrap.innerHTML = `
      <div style="font-size:11px;color:#666;letter-spacing:.04em;text-transform:uppercase;margin-bottom:6px">Sponsored · ${esc(net.label || '')}</div>
      <div style="font-weight:700;color:#f0f0f0;margin-bottom:4px">${esc(slotCfg.headline || '')}</div>
      <div style="margin-bottom:10px">${esc(slotCfg.body || '')}</div>
      <a href="${esc(buildHref(net, slotEl))}" target="_blank" rel="noopener sponsored" style="display:inline-block;padding:7px 12px;border-radius:7px;background:#1a1a1a;border:1px solid #333;color:#f5c518;text-decoration:none;font-weight:700;font-size:12px">View ${esc(net.label || 'offers')} →</a>
    `;
    slotEl.replaceWith(wrap);
  }

  function buildHref(net, slotEl) {
    // Allow per-instance target override via data-ad-target attribute, else
    // fall back to the network's signup_url (so clicks at least hit the
    // partner homepage with our ref).
    const target = slotEl.dataset.adTarget || net.signup_url || 'https://pariscomedy.com/';
    try {
      const u = new URL(target);
      if (net.ref_param && net.ref && !u.searchParams.has(net.ref_param)) {
        u.searchParams.set(net.ref_param, net.ref);
      }
      return u.toString();
    } catch (_) {
      return target;
    }
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c =>
      ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  slots.forEach(el => render(el, el.dataset.adSlot));
})();
