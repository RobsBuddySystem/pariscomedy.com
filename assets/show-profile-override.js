// Public show page override: fetches /api/show/{slug}/public-profile and
// overlays published owner data (tagline, description, ticket_url, dates,
// lineup, links). Static HTML remains the fallback if API fails.
// Never displays owner_email, RSVP emails, CRM data, or private lineup notes.
(function(){
  console.log('[show-profile-override] script started');
  function deriveSlug() {
    if (window.SHOW_SLUG) return String(window.SHOW_SLUG).trim();
    const m = location.pathname.match(/\/shows\/([a-z0-9-]+)\.html$/i);
    return m ? m[1] : '';
  }
  const slug = deriveSlug();
  if (!slug) return;
  const safeText = s => (s == null) ? '' : String(s).replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'})[c]);
  const safeUrl = s => {
    if (!s) return '';
    try { const u = new URL(s); return (u.protocol === 'http:' || u.protocol === 'https:') ? u.href : ''; }
    catch(_) { return ''; }
  };
  const fmtDate = iso => {
    if (!iso) return '';
    const [y,m,d] = iso.split('-').map(Number);
    const dt = new Date(Date.UTC(y, m-1, d));
    return dt.toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric', timeZone:'UTC' });
  };

  console.log('[show-profile-override] slug=' + slug);
  async function load() {
    console.log('[show-profile-override] load() starting');
    let apiBase = 'https://api.pariscomedy.com';
    try { const c = await fetch('/api-config.json').then(r=>r.json()); if (c && c.api) apiBase = c.api; } catch(_) {}
    let data;
    try {
      const r = await fetch(apiBase + '/api/show/' + encodeURIComponent(slug) + '/public-profile');
      if (!r.ok) return; // keep static fallback
      data = await r.json();
    } catch(_) { return; } // keep static fallback
    if (!data) return;
    const profile = data.profile || null;
    const dates = data.dates || [];
    const lineup = data.lineup || [];

    if (profile) {
      // Tagline (lead)
      if (profile.tagline) {
        const lead = document.querySelector('.lead');
        if (lead) lead.textContent = profile.tagline;
      }
      // Description: insert/replace right after lead
      if (profile.description) {
        let desc = document.getElementById('pp-description-block');
        if (!desc) {
          desc = document.createElement('p');
          desc.id = 'pp-description-block';
          desc.style.cssText = 'margin:14px 0;color:#ddd;line-height:1.55';
          const lead = document.querySelector('.lead');
          if (lead && lead.parentNode) lead.parentNode.insertBefore(desc, lead.nextSibling);
        }
        desc.textContent = profile.description;
      }
      // Ticket URL: override primary CTA only if ticket_url valid
      const tu = safeUrl(profile.ticket_url);
      if (tu) {
        const primary = document.querySelector('.cta-btn.cta-primary');
        if (primary) {
          primary.href = '/r.html?kind=show&id=' + encodeURIComponent(slug) + '&url=' + encodeURIComponent(tu);
          primary.textContent = 'Get tickets →';
        }
      }
      // Links (instagram / website)
      const ig = safeUrl(profile.instagram), ws = safeUrl(profile.website);
      if (ig || ws) {
        let links = document.getElementById('pp-links-block');
        if (!links) {
          links = document.createElement('div');
          links.id = 'pp-links-block';
          links.style.cssText = 'margin:14px 0;font-size:13px;color:#9cf';
          const cta = document.querySelector('.cta-row');
          if (cta && cta.parentNode) cta.parentNode.insertBefore(links, cta);
        }
        links.innerHTML = '';
        if (ig) links.innerHTML += '<a href="'+ig+'" target="_blank" rel="noopener" style="margin-right:14px">Instagram ↗</a>';
        if (ws) links.innerHTML += '<a href="'+ws+'" target="_blank" rel="noopener">Website ↗</a>';
      }
    }

    // Dates: only render if API returned at least one future scheduled/sold_out date.
    // Otherwise leave the static-generated list alone.
    if (dates.length) {
      const list = document.querySelector('.upcoming-list');
      if (list) {
        list.innerHTML = dates.map(d => {
          const dateLabel = safeText(fmtDate(d.show_date));
          const time = d.start_time ? ' · ' + safeText(d.start_time) : '';
          if (d.status === 'sold_out') {
            return '<li>' + dateLabel + time + ' · <span style="color:#fc6">SOLD OUT</span></li>';
          }
          const tu = safeUrl(d.ticket_url);
          if (tu) {
            return '<li>' + dateLabel + time + ' · <a href="/r.html?kind=show&amp;id=' +
              encodeURIComponent(slug) + '-' + d.show_date.replace(/-/g,'') +
              '&amp;url=' + encodeURIComponent(tu) +
              '" target="_blank" rel="noopener sponsored">Tickets →</a></li>';
          }
          return '<li>' + dateLabel + time + '</li>';
        }).join('');
      }
    }

    // Lineup: render a new section only if there are published items.
    if (lineup.length) {
      let li = document.getElementById('pp-lineup-block');
      if (!li) {
        li = document.createElement('div');
        li.id = 'pp-lineup-block';
        const h = document.createElement('h2'); h.textContent = 'Lineup'; li.appendChild(h);
        const ul = document.createElement('ul'); ul.className = 'upcoming-list'; li.appendChild(ul);
        const cta = document.querySelector('.cta-row');
        if (cta && cta.parentNode) cta.parentNode.insertBefore(li, cta);
      }
      const ul = li.querySelector('ul');
      ul.innerHTML = lineup.map(c => {
        const name = safeText(c.comic_name || '');
        if (c.comic_slug) {
          return '<li><a href="/comics/' + encodeURIComponent(c.comic_slug) + '.html">' + name + '</a></li>';
        }
        return '<li>' + name + '</li>';
      }).join('');
    }
  }
  load();
})();
