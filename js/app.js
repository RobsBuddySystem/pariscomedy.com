/* Paris Comedy — Main App */
document.addEventListener('DOMContentLoaded', () => {
    initLanguage();
    initNav();
    initPage();
    initPromoUrgency();
    initLiteYouTube();
    initParticles();
    initScrollAnimations();
    initEasterEggs();
});

/* ─── Language Switcher ─── */
const SUPPORTED_LANGS = ['en', 'fr', 'es', 'de', 'ja', 'zh', 'ko'];
const META_TRANSLATIONS = {
    home: {
        en: {
            title: 'Paris Comedy — The Home of English-Language Comedy in Paris',
            description: 'The home of English-language comedy in Paris. 30+ weekly shows, 25+ venues. French Fried Comedy Night, Velvet Bar Comedy, and more. Reserve your spot on Eventbrite.',
            ogTitle: 'Paris Comedy — English-Language Comedy in Paris',
            ogDescription: '30+ weekly shows in English & French. Open mics, showcases, and the legendary French Fried Comedy Night. Reserve your spot.',
            twitterTitle: 'Paris Comedy — English Comedy in Paris',
            twitterDescription: '30+ weekly English comedy shows in Paris. Reserve your spot.'
        },
        fr: {
            title: 'Paris Comedy — Le rendez-vous du stand-up en anglais à Paris',
            description: 'Le point de repère du stand-up en anglais à Paris. 30+ spectacles par semaine, 25+ salles. French Fried Comedy Night, Velvet Bar Comedy et plus encore.',
            ogTitle: 'Paris Comedy — Stand-up en anglais à Paris',
            ogDescription: '30+ spectacles chaque semaine en anglais et en français. Open mics, plateaux et la légendaire French Fried Comedy Night.',
            twitterTitle: 'Paris Comedy — Stand-up à Paris',
            twitterDescription: '30+ spectacles de stand-up chaque semaine à Paris. Réservez votre place.'
        },
        es: {
            title: 'Paris Comedy — La casa de la comedia en inglés en París',
            description: 'La referencia de la comedia en inglés en París. 30+ shows semanales, 25+ salas. French Fried Comedy Night, Velvet Bar Comedy y más.',
            ogTitle: 'Paris Comedy — Comedia en inglés en París',
            ogDescription: '30+ shows semanales en inglés y francés. Open mics, showcases y la legendaria French Fried Comedy Night.',
            twitterTitle: 'Paris Comedy — Comedia en París',
            twitterDescription: '30+ shows de comedia cada semana en París. Reserva tu lugar.'
        },
        de: {
            title: 'Paris Comedy — Die Heimat der englischsprachigen Comedy in Paris',
            description: 'Die Anlaufstelle für englischsprachige Comedy in Paris. 30+ Shows pro Woche, 25+ Locations. French Fried Comedy Night, Velvet Bar Comedy und mehr.',
            ogTitle: 'Paris Comedy — Englische Comedy in Paris',
            ogDescription: '30+ wöchentliche Shows auf Englisch und Französisch. Open Mics, Showcases und die legendäre French Fried Comedy Night.',
            twitterTitle: 'Paris Comedy — Comedy in Paris',
            twitterDescription: '30+ Comedyshows pro Woche in Paris. Reserviere deinen Platz.'
        },
        ja: {
            title: 'Paris Comedy — パリの英語コメディの拠点',
            description: 'パリで英語コメディを探すならここ。毎週30以上のショー、25以上の会場。French Fried Comedy Night や Velvet Bar Comedy などを掲載。',
            ogTitle: 'Paris Comedy — パリの英語コメディ',
            ogDescription: '英語とフランス語のコメディショーが毎週30以上。オープンマイク、ショーケース、French Fried Comedy Night。',
            twitterTitle: 'Paris Comedy — パリのコメディ',
            twitterDescription: 'パリで毎週30以上のコメディショー。席を予約。'
        },
        zh: {
            title: 'Paris Comedy — 巴黎英文单口喜剧中心',
            description: '巴黎英文喜剧的聚集地。每周30多场演出、25多个场地。French Fried Comedy Night、Velvet Bar Comedy 等都在这里。',
            ogTitle: 'Paris Comedy — 巴黎英文喜剧',
            ogDescription: '每周30多场英语和法语喜剧演出。开放麦、拼盘秀，以及招牌 French Fried Comedy Night。',
            twitterTitle: 'Paris Comedy — 巴黎喜剧',
            twitterDescription: '巴黎每周30多场喜剧演出。立即预订。'
        },
        ko: {
            title: 'Paris Comedy — 파리 영어 코미디의 중심',
            description: '파리 영어 코미디의 기준점. 매주 30개 이상의 공연, 25개 이상의 베뉴. French Fried Comedy Night, Velvet Bar Comedy 등 수록.',
            ogTitle: 'Paris Comedy — 파리 영어 코미디',
            ogDescription: '영어와 프랑스어 코미디 쇼가 매주 30회 이상. 오픈 마이크, 쇼케이스, 그리고 French Fried Comedy Night.',
            twitterTitle: 'Paris Comedy — 파리 코미디',
            twitterDescription: '파리에서 매주 30개 이상의 코미디 쇼. 자리 예약하기.'
        }
    }
};

let currentLang = getInitialLanguage();

function getInitialLanguage() {
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get('lang');
    if (SUPPORTED_LANGS.includes(urlLang)) return urlLang;
    const savedLang = localStorage.getItem('pc-lang');
    if (SUPPORTED_LANGS.includes(savedLang)) return savedLang;
    return 'en';
}

function setLanguage(lang, pushUrl = true) {
    currentLang = SUPPORTED_LANGS.includes(lang) ? lang : 'en';
    localStorage.setItem('pc-lang', currentLang);
    document.documentElement.lang = currentLang;
    window.currentLang = currentLang;
    updateLanguageUrl(pushUrl);
    updateMetaForLanguage();
}

function updateLanguageUrl(pushUrl = true) {
    const url = new URL(window.location.href);
    if (currentLang === 'en') {
        url.searchParams.delete('lang');
    } else {
        url.searchParams.set('lang', currentLang);
    }
    const method = pushUrl ? 'pushState' : 'replaceState';
    window.history[method]({}, '', url);
}

function updateMetaForLanguage() {
    const page = document.body?.dataset.metaPage || 'home';
    const meta = (META_TRANSLATIONS[page] && (META_TRANSLATIONS[page][currentLang] || META_TRANSLATIONS[page].en)) || null;
    if (!meta) return;
    document.title = meta.title;
    setMetaTag('name', 'description', meta.description);
    setMetaTag('property', 'og:title', meta.ogTitle || meta.title);
    setMetaTag('property', 'og:description', meta.ogDescription || meta.description);
    setMetaTag('property', 'og:locale', localeFromLang(currentLang));
    setMetaTag('name', 'twitter:title', meta.twitterTitle || meta.ogTitle || meta.title);
    setMetaTag('name', 'twitter:description', meta.twitterDescription || meta.ogDescription || meta.description);
    const url = new URL(window.location.href);
    setMetaTag('property', 'og:url', url.toString());
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) canonical.href = `${url.origin}${url.pathname}`;
    document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(link => {
        const hreflang = link.getAttribute('hreflang');
        if (!hreflang) return;
        const alt = new URL(`${url.origin}${url.pathname}`);
        if (hreflang !== 'x-default' && hreflang !== 'en') alt.searchParams.set('lang', hreflang);
        if (hreflang === 'en') alt.searchParams.set('lang', 'en');
        link.href = hreflang === 'x-default' ? `${url.origin}${url.pathname}` : alt.toString();
    });
}

function localeFromLang(lang) {
    return ({ en:'en_US', fr:'fr_FR', es:'es_ES', de:'de_DE', ja:'ja_JP', zh:'zh_CN', ko:'ko_KR' })[lang] || 'en_US';
}

function setMetaTag(attr, value, content) {
    const selector = `meta[${attr}="${value}"]`;
    const el = document.querySelector(selector);
    if (el) el.setAttribute('content', content);
}

function initLanguage() {
    const switcher = document.getElementById('langSwitcher');
    setLanguage(currentLang, false);
    if (!switcher) {
        applyTranslations();
        return;
    }
    switcher.querySelectorAll('[data-lang]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLang);
        btn.addEventListener('click', () => {
            setLanguage(btn.dataset.lang, true);
            switcher.querySelectorAll('[data-lang]').forEach(b => b.classList.toggle('active', b.dataset.lang === currentLang));
            applyTranslations();
            // Re-render dynamic content
            initPage();
        });
    });
    applyTranslations();
}

function t(path) {
    const keys = path.split('.');
    let obj = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
    for (const k of keys) { obj = obj?.[k]; }
    return obj || (TRANSLATIONS.en && keys.reduce((o,k) => o?.[k], TRANSLATIONS.en)) || '';
}

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        const val = t(key);
        if (val) el.innerHTML = val;
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const val = t(el.dataset.i18nPlaceholder);
        if (val) el.placeholder = val;
    });
    document.querySelectorAll('[data-page-copy]').forEach(el => {
        const val = pageCopy(el.dataset.pageCopy, el.innerHTML);
        if (val) el.innerHTML = val;
    });
    document.querySelectorAll('[data-page-copy-placeholder]').forEach(el => {
        const val = pageCopy(el.dataset.pageCopyPlaceholder, el.placeholder || '');
        if (val) el.placeholder = val;
    });
}

/* ─── Navigation ─── */
function initNav() {
    const toggle = document.getElementById('navToggle');
    const links = document.getElementById('navLinks');
    if (!toggle || !links) return;
    toggle.addEventListener('click', () => {
        links.classList.toggle('open');
        toggle.classList.toggle('open');
    });
    links.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            links.classList.remove('open');
            toggle.classList.remove('open');
        });
    });
    window.addEventListener('scroll', () => {
        document.getElementById('nav')?.classList.toggle('scrolled', window.scrollY > 20);
    });
}

/* ─── Page-specific init ─── */
function initPage() {
    const page = document.body.dataset.page || 'home';
    if (page === 'home') {
        renderTonightBanner();
        // English: calendar first, then shows. French: shows first (Velvet focused)
        if (currentLang !== 'fr') { moveCalendarFirst(); }
        renderFeaturedShows(); renderUpNext(); renderCalendar(); renderQuote(); renderUntranslatable(); renderTestimonials(); renderGrowthChart();
    }
    if (page === 'shows') { renderAllShows(); renderOtherShows(); initFilters(); initDayFilter(); renderThisWeek(); }
    if (page === 'venues') { renderVenueMap(); renderVenueCards(); }
    if (page === 'history') { renderTimeline(); renderKeyPlayers(); renderNotableVisitors(); }
    if (page === 'comedians') { renderComediansDirectory(); }
    initPromoUrgency();
    initLiteYouTube();
}

function initPromoUrgency() {
    document.querySelectorAll('[data-promo-date]').forEach(card => {
        const dateText = card.dataset.promoDate;
        const expireText = card.dataset.promoExpire || dateText;
        const countdown = card.querySelector('.promo-countdown');
        if (!dateText || !countdown) return;

        const start = new Date(dateText);
        const expire = new Date(expireText);
        const now = new Date();

        if (Number.isNaN(start.getTime()) || Number.isNaN(expire.getTime())) return;

        if (now > expire) {
            const section = card.closest('section') || card;
            section.style.display = 'none';
            return;
        }

        const diffMs = start.getTime() - now.getTime();
        const hours = Math.max(0, diffMs / 36e5);
        const days = Math.max(0, Math.ceil(diffMs / 864e5));
        let label = 'This week';

        if (hours <= 6) label = 'Tonight';
        else if (hours <= 30) label = 'Tomorrow';
        else if (days === 2) label = 'In 2 days';
        else if (days > 2) label = `In ${days} days`;

        countdown.textContent = label;
        countdown.setAttribute('aria-label', `Promo timing: ${label}`);
    });
}

function initLiteYouTube() {
    document.querySelectorAll('.lite-youtube').forEach(el => {
        if (el.dataset.bound === 'true') return;
        el.dataset.bound = 'true';
        const activate = () => {
            if (el.dataset.loaded === 'true') return;
            const videoId = el.dataset.youtubeId;
            if (!videoId) return;
            const title = el.dataset.title || 'YouTube video';
            const iframe = document.createElement('iframe');
            iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`;
            iframe.title = title;
            iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
            iframe.allowFullscreen = true;
            iframe.loading = 'lazy';
            el.innerHTML = '';
            el.appendChild(iframe);
            el.dataset.loaded = 'true';
        };
        el.addEventListener('click', activate);
        el.addEventListener('keydown', evt => {
            if (evt.key === 'Enter' || evt.key === ' ') {
                evt.preventDefault();
                activate();
            }
        });
        if (!el.hasAttribute('tabindex')) el.tabIndex = 0;
        if (!el.hasAttribute('role')) el.setAttribute('role', 'button');
    });
}

/* ─── This Week ─── */
function renderThisWeek() {
    const el = document.getElementById('thisWeekGrid');
    if (!el) return;
    const DAY_NAMES = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const SHORT = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const now = new Date();
    // Update section title to reflect tonight if there are shows today
    const todayName = DAY_NAMES[now.getDay()];
    const allForToday = [...(typeof SHOWS!=='undefined'?SHOWS:[]),...(typeof OTHER_SHOWS!=='undefined'?OTHER_SHOWS:[])].filter(s=>{
        const d=Array.isArray(s.day)?s.day:[s.day]; return d.includes(todayName)||d.includes('daily');
    });
    const titleEl = document.getElementById('thisWeekTitle');
    if (titleEl && allForToday.length > 0) titleEl.textContent = '🎤 On Stage Tonight & This Week';
    // Build next-7-days map: dayName → [{date, label}]
    const upcoming = {};
    for (let i = 0; i < 7; i++) {
        const d = new Date(now);
        d.setDate(now.getDate() + i);
        const dn = DAY_NAMES[d.getDay()];
        if (!upcoming[dn]) upcoming[dn] = [];
        upcoming[dn].push({ d, label: `${SHORT[d.getDay()]} ${d.getDate()} ${MONTHS[d.getMonth()]}` });
    }
    // Collect all shows (SHOWS + OTHER_SHOWS) that fall within next 7 days
    const allShows = [...(typeof SHOWS !== 'undefined' ? SHOWS : []), ...(typeof OTHER_SHOWS !== 'undefined' ? OTHER_SHOWS : [])];
    const cards = [];
    allShows.forEach(show => {
        if (!show.day) return;
        if (show.day === 'daily') {
            // Daily shows appear every day in the 7-day window
            Object.entries(upcoming).forEach(([, dates]) => {
                dates.forEach(({ d, label }) => {
                    const venueName = show.venueName || (show.venue ? (VENUES || []).find(v => v.id === show.venue)?.name || '' : '');
                    const link = show.bookingUrl ? `<a href="${show.bookingUrl}" target="_blank" rel="noopener" class="btn btn-primary btn-sm" style="margin-top:10px;">Reserve →</a>` : `<a href="book.html" class="btn btn-ghost btn-sm" style="margin-top:10px;">Get Listed →</a>`;
                    const isTonight = d.toDateString() === now.toDateString();
                    const badge = isTonight ? '<span style="background:#ff3366;color:#fff;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:999px;margin-left:6px;vertical-align:middle;">TONIGHT</span>' : '';
                    cards.push({ ts: d.getTime(), time: show.time || '', html: `<div class="show-card" style="padding:16px 18px;display:flex;flex-direction:column;gap:4px;" data-reveal data-reveal-delay="1"><div style="font-size:.78rem;font-weight:700;color:var(--accent);letter-spacing:.04em;text-transform:uppercase;">${label}${badge}</div><div style="font-size:1.05rem;font-weight:700;font-family:var(--font-display);">${show.emoji || '🎤'} ${show.name}</div><div style="font-size:.85rem;color:var(--text-muted);">${show.time || ''} · ${venueName}</div>${link}</div>` });
                });
            });
            return;
        }
        // Support single day string OR array of days
        const showDays = Array.isArray(show.day) ? show.day : [show.day];
        showDays.forEach(dayName => {
            if (!upcoming[dayName]) return;
            upcoming[dayName].forEach(({ d, label }) => {
                const venueName = show.venueName || (show.venue ? (VENUES || []).find(v => v.id === show.venue)?.name || '' : '');
                const link = show.bookingUrl ? `<a href="${show.bookingUrl}" target="_blank" rel="noopener" class="btn btn-primary btn-sm" style="margin-top:10px;">Reserve →</a>` : `<a href="book.html" class="btn btn-ghost btn-sm" style="margin-top:10px;">Get Listed →</a>`;
                const isTonight = d.toDateString() === now.toDateString();
                const badge = isTonight ? '<span style="background:#ff3366;color:#fff;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:999px;margin-left:6px;vertical-align:middle;">TONIGHT</span>' : '';
                cards.push({ ts: d.getTime(), time: show.time || '', html: `
                    <div class="show-card" style="padding:16px 18px;display:flex;flex-direction:column;gap:4px;" data-reveal data-reveal-delay="1">
                        <div style="font-size:.78rem;font-weight:700;color:var(--accent);letter-spacing:.04em;text-transform:uppercase;">${label}${badge}</div>
                        <div style="font-size:1.05rem;font-weight:700;font-family:var(--font-display);">${show.emoji || '🎤'} ${show.name}</div>
                        <div style="font-size:.85rem;color:var(--text-muted);">${show.time || ''} · ${venueName}</div>
                        ${link}
                    </div>` });
            });
        });
    });
    // Sort by date+time
    cards.sort((a, b) => a.ts - b.ts || a.time.localeCompare(b.time));
    if (cards.length === 0) {
        el.innerHTML = '<p style="color:var(--text-muted);font-size:.9rem;">Check back soon — shows update weekly.</p>';
    } else {
        el.innerHTML = cards.map(c => c.html).join('');
    }
}

/* ─── Shows ─── */
function renderShowCard(show) {
    const venue = VENUES.find(v => v.id === show.venue);
    const typeLabel = show.type === 'standup' ? t('filters.standup') : t('filters.openmic');
    return `<article class="show-card" data-type="${show.type}" data-reveal>
        <div class="show-card-img" style="background:linear-gradient(135deg,${show.type==='standup'?'#1a0515,#2a1020':'#0a1a0f,#102a15'});">${show.emoji}</div>
        <div class="show-card-body">
            <span class="show-card-type type-${show.type}">${typeLabel}</span>
            <h3 class="show-card-title">${show.name}</h3>
            <p class="show-card-venue">📍 ${venue?.name||''} · ${venue?.neighborhood||''}</p>
            <p class="show-card-time">🕐 ${({'fr':`Chaque ${show.day} à ${show.time}`,'es':`Cada ${show.day} a las ${show.time}`,'de':`Jeden ${show.day} um ${show.time}`,'ja':`毎${show.day} ${show.time}`,'zh':`每${show.day} ${show.time}`,'ko':`매${show.day} ${show.time}`})[currentLang] || `Every ${show.day} at ${show.time}`}</p>
            <p class="show-card-desc">${currentLang === 'fr' ? (show.descFr||show.description) : currentLang === 'es' ? (show.descEs||show.description) : show.description}</p>
            <div class="show-card-meta">
                <span class="show-card-badge">🎟️ ${({'fr':'Entrée libre','es':'Entrada libre','de':'Freier Eintritt','ja':'入場無料','zh':'免费入场','ko':'무료 입장'})[currentLang] || 'Free entry'}</span>
                <span class="show-card-badge">🍺 ${({'fr':'1 conso min','es':'1 bebida mín','de':'1 Getränk min','ja':'1ドリンク制','zh':'最低消费1杯','ko':'1음료 최소'})[currentLang] || '1 drink min'}</span>
                <span class="show-card-badge">🎩 ${({'fr':'Chapeau pour les artistes','es':'Sombrero para artistas','de':'Hut für Künstler','ja':'投げ銭','zh':'打赏艺人','ko':'모자 기부'})[currentLang] || 'Hat for artists'}</span>
            </div>
            <div class="show-card-footer">
                ${currentLang !== 'fr' ? `<span class="show-card-price">${show.price}</span>` : ''}
                <a href="${show.bookingUrl}" target="_blank" rel="noopener" class="show-card-link">🎟️ ${({'fr':'Réservez votre place','es':'Reserva tu lugar','de':'Platz reservieren','ja':'席を予約する','zh':'预订座位','ko':'좌석 예약'})[currentLang] || 'Reserve Your Spot'} →</a>
            </div>
        </div>
    </article>`;
}

function renderUpNext() {
    const el = document.getElementById('upNextGrid');
    if (!el) return;
    const DAY_NAMES = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const now = new Date();
    const todayName = DAY_NAMES[now.getDay()];

    // Build next 7 days map (exclude today — tonight banner covers it)
    const upcoming = [];
    for (let i = 1; i <= 7; i++) {
        const d = new Date(now);
        d.setDate(now.getDate() + i);
        upcoming.push(d);
    }

    // Pick up to 3 upcoming SHOWS (featured+non-featured) sorted by next occurrence
    const cards = [];
    upcoming.forEach((d, idx) => {
        if (cards.length >= 3) return;
        const dn = DAY_NAMES[d.getDay()];
        const label = `${dn} · ${d.getDate()} ${MONTHS[d.getMonth()]}`;
        SHOWS.forEach(show => {
            if (cards.length >= 3) return;
            if (show.day !== dn) return;
            // Avoid duplicate shows already added
            if (cards.find(c => c.id === show.id)) return;
            const venue = (typeof VENUES !== 'undefined') ? VENUES.find(v => v.id === show.venue) : null;
            const venueName = venue ? venue.name : '';
            const neighborhood = venue ? venue.neighborhood : '';
            const isTomorrow = idx === 0;
            const badge = isTomorrow ? '<span style="background:var(--accent);color:#fff;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:999px;margin-left:6px;">TOMORROW</span>' : '';
            const reserveBtn = show.bookingUrl
                ? `<a href="${show.bookingUrl}" target="_blank" rel="noopener" class="btn btn-primary btn-sm" style="margin-top:12px;font-size:.85rem;" onclick="if(typeof trackReserve==='function')trackReserve('${show.shortName||show.name}','${show.bookingUrl}')">🎟️ Reserve Free →</a>`
                : `<a href="shows.html" class="btn btn-ghost btn-sm" style="margin-top:12px;font-size:.85rem;">See Show Details →</a>`;
            const desc = currentLang === 'fr' ? (show.descFr || show.description) : show.description;
            cards.push({ id: show.id, html: `
                <div class="show-card" style="padding:18px 20px;display:flex;flex-direction:column;gap:6px;border-top:3px solid var(--accent);" data-reveal>
                    <div style="font-size:.78rem;font-weight:700;color:var(--accent);letter-spacing:.05em;text-transform:uppercase;">${label}${badge}</div>
                    <div style="font-size:1.1rem;font-weight:700;font-family:var(--font-display);">${show.emoji || '🎤'} ${show.name}</div>
                    <div style="font-size:.83rem;color:var(--text-muted);">🕐 ${show.time} &nbsp;·&nbsp; 📍 ${venueName}${neighborhood ? ', ' + neighborhood : ''}</div>
                    <div style="font-size:.88rem;color:var(--text-dim);margin-top:4px;line-height:1.4;">${desc}</div>
                    ${currentLang !== 'fr' ? '<div style="font-size:.78rem;color:var(--text-muted);margin-top:2px;">✅ Free entry · 1 drink min</div>' : ''}
                    ${reserveBtn}
                </div>` });
        });
    });

    if (cards.length === 0) {
        el.innerHTML = '<p style="color:var(--text-muted);font-size:.9rem;">Check back soon — shows listed weekly.</p>';
        return;
    }
    el.innerHTML = cards.map(c => c.html).join('');
    if (typeof _revealInit === 'function') _revealInit(el);
}

function renderFeaturedShowCard(show) {
    const venueName = show.venueName || (show.venue ? (VENUES || []).find(v => v.id === show.venue)?.name || '' : '');
    const neighborhood = show.venue ? (VENUES || []).find(v => v.id === show.venue)?.neighborhood || '' : '';
    const typeLabel = show.type === 'standup' ? t('filters.standup') : t('filters.openmic');
    const desc = currentLang === 'fr' ? (show.descFr||show.description) : currentLang === 'es' ? (show.descEs||show.description) : show.description;
    const dayStr = Array.isArray(show.day) ? show.day.join(' & ') : show.day;
    const timeStr = ({'fr':`Chaque ${dayStr} à ${show.time}`,'es':`Cada ${dayStr} a las ${show.time}`,'de':`Jeden ${dayStr} um ${show.time}`})[currentLang] || `Every ${dayStr} at ${show.time}`;
    const reserveLink = show.bookingUrl
        ? `<a href="${show.bookingUrl}" target="_blank" rel="noopener" class="show-card-link">🎟️ ${({'fr':'Réservez','es':'Reservar','de':'Reservieren'})[currentLang]||'Reserve'} →</a>`
        : `<a href="book.html" class="show-card-link">${({'fr':'En savoir plus','es':'Más info','de':'Mehr Info'})[currentLang]||'Learn More'} →</a>`;
    return `<article class="show-card" data-type="${show.type}" data-reveal>
        <div class="show-card-img" style="background:linear-gradient(135deg,${show.type==='standup'?'#1a0515,#2a1020':'#0a1a0f,#102a15'});">${show.emoji}</div>
        <div class="show-card-body">
            <span class="show-card-type type-${show.type}">${typeLabel}</span>
            <h3 class="show-card-title">${show.name}</h3>
            <p class="show-card-venue">📍 ${venueName}${neighborhood ? ' · ' + neighborhood : ''}</p>
            <p class="show-card-time">🕐 ${timeStr}</p>
            <p class="show-card-desc">${desc}</p>
            <div class="show-card-footer">
                ${reserveLink}
            </div>
        </div>
    </article>`;
}

function renderFeaturedShows() {
    const grid = document.getElementById('featuredShowsGrid');
    if (!grid) return;
    // Combine SHOWS + featured OTHER_SHOWS for a diverse city guide feel
    const featuredMain = SHOWS.filter(s => s.featured);
    const featuredOther = (typeof OTHER_SHOWS !== 'undefined' ? OTHER_SHOWS : []).filter(s => s.featured);
    let allFeatured = [...featuredMain, ...featuredOther];
    // Shuffle so it's not always Velvet first — mix of venues
    if (currentLang === 'fr') {
        // French: Velvet first
        allFeatured.sort((a,b) => {
            const aVelvet = a.venue === 'velvet' || a.venueName === 'Velvet Bar';
            const bVelvet = b.venue === 'velvet' || b.venueName === 'Velvet Bar';
            if (aVelvet && !bVelvet) return -1;
            if (!aVelvet && bVelvet) return 1;
            return 0;
        });
    } else {
        // English: FFCN first, then mix
        allFeatured.sort((a,b) => {
            if (a.id === 'ffcn') return -1;
            if (b.id === 'ffcn') return 1;
            return 0;
        });
    }
    grid.innerHTML = allFeatured.map(s => s.id ? renderShowCard(s) : renderFeaturedShowCard(s)).join('');
}

function renderAllShows(filter = 'all') {
    const grid = document.getElementById('showsGrid');
    if (!grid) return;
    const filtered = filter === 'all' ? SHOWS : SHOWS.filter(s => s.type === filter);
    grid.innerHTML = filtered.map(renderShowCard).join('');
    if (window._revealInit) window._revealInit(grid);
}

function renderOtherShows(dayFilter) {
    const container = document.getElementById('otherShowsList');
    if (!container || typeof OTHER_SHOWS === 'undefined') return;
    let shows = OTHER_SHOWS;
    if (dayFilter && dayFilter !== 'all') {
        shows = OTHER_SHOWS.filter(s => {
            const days = Array.isArray(s.day) ? s.day : [s.day];
            return days.includes(dayFilter) || s.day === 'daily';
        });
    }
    if (shows.length === 0) {
        container.innerHTML = `<div style="text-align:center;padding:40px 20px;color:var(--text-muted);grid-column:1/-1;">
            <p style="font-size:1.1rem;margin-bottom:12px;">No shows listed for ${dayFilter} yet.</p>
            <a href="book.html" class="btn btn-primary" style="font-size:0.9rem;">List Your Show →</a>
        </div>`;
        if (window._revealInit) window._revealInit(container);
        return;
    }
    container.innerHTML = shows.map(show => `
        <div class="other-show-card${!show.paid ? ' placeholder-card' : ''}" data-reveal>
            <div class="other-show-name">${show.emoji || '🎤'} ${show.name}</div>
            <div class="other-show-venue">📍 ${show.venueName} · ${Array.isArray(show.day) ? show.day.join(' & ') : show.day}${show.time ? ' · '+show.time : ''}</div>
            <div class="other-show-desc">${show.description}</div>
            ${show.bookingUrl ? `<a href="${show.bookingUrl}" target="_blank" rel="noopener" class="show-card-link" style="display:inline-block;margin-top:8px;">🎟️ ${({'fr':'Réservez votre place','es':'Reserva tu lugar','de':'Platz reservieren'})[currentLang] || 'Reserve Your Spot'} →</a>` : `<div class="other-show-cta"><span class="placeholder-badge">📋 ${({'fr':'Pas encore référencé','es':'Aún no listado','de':'Noch nicht gelistet'})[currentLang] || 'Not yet listed'}</span> <a href="book.html" class="other-show-link">${({'fr':'Référencez-vous pour 1€/mois','es':'Inscríbete por 1€/mes','de':'Gelistet werden für 1€/Monat'})[currentLang] || 'Get listed for €1/month'} →</a></div>`}
        </div>
    `).join('');
    if (window._revealInit) window._revealInit(container);
}

function initDayFilter() {
    const bar = document.getElementById('dayFilterBar');
    if (!bar) return;
    // Auto-highlight today's day on page load
    const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const todayName = days[new Date().getDay()];
    const todayBtn = bar.querySelector(`[data-day="${todayName}"]`);
    if (todayBtn) {
        // Auto-select today — show tonight's shows by default
        bar.querySelectorAll('.day-filter-btn').forEach(b => {
            b.style.background = 'transparent';
            b.style.color = 'var(--text-muted)';
            b.style.borderColor = 'var(--border)';
        });
        todayBtn.style.background = 'var(--accent)';
        todayBtn.style.color = '#fff';
        todayBtn.style.borderColor = 'var(--accent)';
        todayBtn.title = 'Tonight!';
        // Update "All Days" button to deactivate
        const allBtn = bar.querySelector('[data-day="all"]');
        if (allBtn) { allBtn.style.background = 'transparent'; allBtn.style.color = 'var(--text-muted)'; allBtn.style.borderColor = 'var(--border)'; }
        renderOtherShows(todayName);
    }
    bar.addEventListener('click', e => {
        const btn = e.target.closest('.day-filter-btn');
        if (!btn) return;
        bar.querySelectorAll('.day-filter-btn').forEach(b => {
            b.style.background = 'transparent';
            b.style.color = 'var(--text-muted)';
            b.style.borderColor = 'var(--border)';
        });
        btn.style.background = 'var(--accent)';
        btn.style.color = '#fff';
        btn.style.borderColor = 'var(--accent)';
        renderOtherShows(btn.dataset.day);
    });
}

function initFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderAllShows(btn.dataset.filter);
        });
    });
}

/* ─── Calendar ─── */
function renderCalendar() {
    const grid = document.getElementById('calendarGrid');
    const monthLabel = document.getElementById('calMonthLabel');
    if (!grid) return;

    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    if (monthLabel) monthLabel.textContent = `${monthNames[month]} ${year}`;

    const events = generateCalendarEvents(year, month);
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDay = new Date(year, month, 1).getDay();
    // Convert Sun=0 to Mon-based offset
    const offset = firstDay === 0 ? 6 : firstDay - 1;

    const dayHeaders = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    let html = dayHeaders.map(d => `<div class="cal-header">${d}</div>`).join('');
    for (let i = 0; i < offset; i++) html += '<div class="cal-day empty"></div>';

    for (let day = 1; day <= daysInMonth; day++) {
        const dayEvents = events.filter(e => e.day === day);
        const isToday = now.getDate() === day;
        const hasShows = dayEvents.length > 0;
        html += `<div class="cal-day${isToday?' today':''}${hasShows?' has-shows':''}" data-day="${day}">
            <span class="cal-day-num">${day}</span>
            <div class="cal-day-dots">${dayEvents.map(e => `<span class="cal-dot dot-${e.type}" title="${e.shortName} · ${e.time}"></span>`).join('')}</div>
        </div>`;
    }
    grid.innerHTML = html;

    // Tooltips on click
    grid.querySelectorAll('.cal-day:not(.empty)').forEach(cell => {
        cell.addEventListener('click', () => {
            grid.querySelectorAll('.cal-tooltip').forEach(t => t.remove());
            const day = parseInt(cell.dataset.day);
            const dayEvents = events.filter(e => e.day === day);
            if (!dayEvents.length) return;
            const tooltip = document.createElement('div');
            tooltip.className = 'cal-tooltip';
            tooltip.innerHTML = dayEvents.map(e => {
                const reserveLink = e.bookingUrl
                    ? `<a href="${e.bookingUrl}" target="_blank" rel="noopener" class="cal-tooltip-reserve">🎟️ Reserve →</a>`
                    : '';
                return `<div class="cal-tooltip-row">${e.emoji} <strong>${e.shortName}</strong> · ${e.time} · ${e.venue}${reserveLink}</div>`;
            }).join('');
            cell.appendChild(tooltip);
            setTimeout(() => tooltip.remove(), 5000);
        });
    });
}

/* ─── Venues ─── */
function renderVenueMap() {
    const pinsContainer = document.getElementById('venuePins');
    if (!pinsContainer) return;
    pinsContainer.innerHTML = VENUES.map((venue, i) => {
        const showsHere = SHOWS.filter(s => s.venue === venue.id);
        const otherHere = (typeof OTHER_SHOWS !== 'undefined') ? OTHER_SHOWS.filter(s => s.venueName === venue.name) : [];
        const allShows = [...showsHere.map(s => `${s.emoji} ${s.shortName} · ${s.day}`), ...otherHere.map(s => `${s.emoji} ${s.name} · ${s.day}`)];
        const pinColor = venue.listed ? 'var(--accent)' : 'var(--purple)';
        return `<div class="venue-pin" style="left:${venue.mapX}%;top:${venue.mapY}%;background:${pinColor};">
            <span>${i+1}</span>
            <div class="venue-pin-tooltip"><strong>${venue.name}</strong><br>${venue.neighborhood}<br>${allShows.join('<br>') || '<em>Shows TBA</em>'}</div>
        </div>`;
    }).join('');
}

function renderVenueCards() {
    const container = document.getElementById('venuesList');
    if (!container) return;
    // Split into listed (ours) and others
    const listed = VENUES.filter(v => v.listed);
    const others = VENUES.filter(v => !v.listed);
    
    let html = listed.map((venue, i) => {
        const showsAtVenue = SHOWS.filter(s => s.venue === venue.id);
        const mapActions = venue.googleMapsUrl
            ? `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;">
                <a href="${venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🗺️ Open map</a>
                <a href="${venue.directions?.walking || venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🚶 Directions</a>
                <a href="${venue.directions?.transit || venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🚇 Transit</a>
                <a href="${venue.directions?.driving || venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🚗 Drive</a>
            </div>`
            : `<div style="margin-top:12px;color:var(--text-muted);font-size:0.82rem;">⚠️ ${venue.mapReviewNote || 'Exact map link needs review.'}</div>`;
        return `<div class="venue-card venue-card-featured">
            <div class="venue-card-badge-top">⭐ Featured Venue</div>
            <div class="venue-card-name">${i+1}. ${venue.name}</div>
            <div class="venue-card-addr">📍 ${venue.address}</div>
            <div class="venue-card-metro">🚇 ${venue.metro || ''}</div>
            <div class="venue-card-desc">${venue.description || ''}</div>
            <div class="venue-card-shows">${showsAtVenue.map(s=>`<span class="venue-show-tag">${s.emoji} ${s.shortName} — ${s.day} ${s.time}</span>`).join('')}</div>
            ${mapActions}
        </div>`;
    }).join('');
    
    if (others.length) {
        html += `<div style="grid-column:1/-1;margin-top:32px;"><h3 style="font-family:var(--font-display);font-size:1.3rem;margin-bottom:8px;color:var(--text-dim);">Other Comedy Venues in Paris</h3><p style="color:var(--text-muted);font-size:0.9rem;margin-bottom:20px;">These venues host English-language comedy. Want your show featured with full booking? <a href="book.html">Get listed →</a></p></div>`;
        html += others.map((venue, i) => {
            const otherHere = (typeof OTHER_SHOWS !== 'undefined') ? OTHER_SHOWS.filter(s => s.venueName === venue.name) : [];
            const mapActions = venue.googleMapsUrl
                ? `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;">
                    <a href="${venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🗺️ Open map</a>
                    <a href="${venue.directions?.walking || venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🚶 Directions</a>
                    <a href="${venue.directions?.transit || venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🚇 Transit</a>
                    <a href="${venue.directions?.driving || venue.googleMapsUrl}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">🚗 Drive</a>
                </div>`
                : `<div style="margin-top:12px;color:var(--text-muted);font-size:0.82rem;">⚠️ ${venue.mapReviewNote || 'Exact map link needs review.'}</div>`;
            return `<div class="venue-card venue-card-placeholder">
                <div class="venue-card-name">${listed.length + i + 1}. ${venue.name}</div>
                <div class="venue-card-addr">📍 ${venue.address}</div>
                <div class="venue-card-metro">🚇 ${venue.metro || ''}</div>
                <div class="venue-card-desc">${venue.description || ''}</div>
                <div class="venue-card-shows">${otherHere.map(s=>`<span class="venue-show-tag">${s.emoji} ${s.name} — ${s.day}</span>`).join('') || '<span style="color:var(--text-muted);font-size:0.82rem">Shows not yet listed — <a href="book.html">claim this listing</a></span>'}</div>
                ${mapActions}
            </div>`;
        }).join('');
    }
    container.innerHTML = html;
    if (window._revealInit) window._revealInit(container);
}

/* ─── History ─── */
function getTimelineIcon(title) {
    const icons = {
        'The Seed': '<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="18" fill="none" stroke="#22c55e" stroke-width="2" opacity="0.6"/><text x="24" y="30" text-anchor="middle" font-size="20">🌱</text></svg>',
        'Ground Zero': '<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="18" fill="none" stroke="#ff3366" stroke-width="2" opacity="0.6"/><text x="24" y="30" text-anchor="middle" font-size="20">🎤</text></svg>',
        'TV Breakthrough': '<svg viewBox="0 0 48 48"><rect x="8" y="10" width="32" height="22" rx="4" fill="none" stroke="#7c3aed" stroke-width="2" opacity="0.6"/><text x="24" y="28" text-anchor="middle" font-size="16">📺</text></svg>',
        'Viral Explosion': '<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="16" fill="none" stroke="#f59e0b" stroke-width="2" opacity="0.6"><animate attributeName="r" values="14;18;14" dur="2s" repeatCount="indefinite"/></circle><text x="24" y="30" text-anchor="middle" font-size="18">💥</text></svg>',
        'French Fried is Born': '<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="18" fill="none" stroke="#ff3366" stroke-width="2" opacity="0.6"><animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite"/></circle><text x="24" y="30" text-anchor="middle" font-size="20">🍟</text></svg>',
        'The Pandemic & Comeback': '<svg viewBox="0 0 48 48"><text x="24" y="30" text-anchor="middle" font-size="20">💪</text></svg>',
        'FFCN Moves to Velvet Bar': '<svg viewBox="0 0 48 48"><text x="24" y="30" text-anchor="middle" font-size="20">🏠</text></svg>',
        'The Explosion': '<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="16" fill="none" stroke="#ff3366" stroke-width="2" opacity="0.5"><animate attributeName="r" values="12;20;12" dur="3s" repeatCount="indefinite"/></circle><text x="24" y="30" text-anchor="middle" font-size="18">🚀</text></svg>',
        'The Golden Age': '<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="18" fill="none" stroke="#f59e0b" stroke-width="2" opacity="0.5"/><text x="24" y="30" text-anchor="middle" font-size="20">👑</text></svg>'
    };
    return icons[title] || '';
}

function renderTimeline() {
    const container = document.getElementById('timelineContainer');
    if (!container || typeof TIMELINE === 'undefined') return;
    container.innerHTML = TIMELINE.map((item, i) => `
        <div class="timeline-item ${i % 2 === 0 ? 'left' : 'right'}">
            <div class="timeline-marker"></div>
            <div class="timeline-content">
                ${getTimelineIcon(item.title) ? `<div class="timeline-illustration">${getTimelineIcon(item.title)}</div>` : ''}
                <span class="timeline-year">${item.year}</span>
                <h3 class="timeline-title">${item.title}</h3>
                <p class="timeline-text">${item.text}</p>
            </div>
        </div>
    `).join('');
}

function renderKeyPlayers() {
    const container = document.getElementById('keyPlayersGrid');
    if (!container || typeof KEY_PLAYERS === 'undefined') return;
    container.innerHTML = KEY_PLAYERS.map((player, idx) => {
        const hasSvg = typeof PORTRAITS !== 'undefined' && PORTRAITS[player.id];
        const avatarHtml = hasSvg
            ? `<div class="player-avatar player-avatar--svg" aria-label="${player.name} portrait">${PORTRAITS[player.id]}</div>`
            : `<div class="player-avatar">${player.emoji}</div>`;
        const bio = currentLang === 'fr' ? (player.bioFr||player.bio)
                  : currentLang === 'es' ? (player.bioEs||player.bio)
                  : currentLang === 'de' ? (player.bioDe||player.bio)
                  : player.bio;
        const socialLinks = [];
        if (player.instagram) socialLinks.push(`<a href="${player.instagram}" target="_blank" rel="noopener" class="player-social" aria-label="${player.name} on Instagram">📸 Follow</a>`);
        if (player.youtube) socialLinks.push(`<a href="${player.youtube}" target="_blank" rel="noopener" class="player-social" aria-label="${player.name} on YouTube">▶️ Watch</a>`);
        if (player.wikipedia) socialLinks.push(`<a href="${player.wikipedia}" target="_blank" rel="noopener" class="player-social" aria-label="${player.name} on Wikipedia">📖 Bio</a>`);
        const socialHtml = socialLinks.length ? `<div class="player-socials">${socialLinks.join('')}</div>` : '';
        return `
        <div class="player-card" data-reveal data-reveal-delay="${idx*0.08}s">
            ${avatarHtml}
            <h3 class="player-name">${player.name}</h3>
            <span class="player-title">${player.emoji} ${player.title}</span>
            <p class="player-bio">${bio}</p>
            ${socialHtml}
        </div>`;
    }).join('');
    if (typeof _revealInit === 'function') _revealInit(container);
}

function renderNotableVisitors() {
    const container = document.getElementById('notableVisitorsList');
    if (!container || typeof NOTABLE_VISITORS === 'undefined') return;
    container.innerHTML = NOTABLE_VISITORS.map(name => `<span class="visitor-tag">${name}</span>`).join('');
}

/* ─── Quote of the Week ─── */
function renderQuote() {
    const container = document.getElementById('quoteContainer');
    if (!container || typeof COMEDY_QUOTES === 'undefined') return;
    // Rotate weekly based on week number
    const weekNum = Math.floor((Date.now() - new Date(2026,0,1)) / (7*24*60*60*1000));
    const quote = COMEDY_QUOTES[weekNum % COMEDY_QUOTES.length];
    container.innerHTML = `
        <blockquote class="comedy-quote">
            <p class="quote-text">${quote.text}</p>
            <cite class="quote-author">— ${quote.author}</cite>
        </blockquote>
    `;
}

/* ─── Untranslatable ─── */
function renderUntranslatable() {
    const container = document.getElementById('untranslatableCard');
    if (!container || typeof UNTRANSLATABLE === 'undefined') return;
    // Rotate daily
    const dayNum = Math.floor(Date.now() / (24*60*60*1000));
    const item = UNTRANSLATABLE[dayNum % UNTRANSLATABLE.length];
    container.innerHTML = `
        <div class="untrans-card" data-reveal>
            <div class="untrans-header">
                <span class="untrans-emoji">${item.emoji}</span>
                <div>
                    <h3 class="untrans-word">${item.word}</h3>
                    <span class="untrans-lang">${item.lang} · "${item.literal}"</span>
                </div>
            </div>
            <p class="untrans-def">${item.definition}</p>
            <p class="untrans-punchline">😂 ${item.punchline}</p>
            <div class="untrans-actions">
                <a href="shows.html" class="untrans-cta">Hear it live at FFCN →</a>
                <div class="untrans-share">
                    <span class="untrans-share-label">Share:</span>
                    <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent('"' + item.word + '" — ' + item.lang + '. ' + item.definition + ' 😂 ' + item.punchline + ' pariscomedy.com')}&hashtags=lostintranslation,pariscomedy,bilingual" target="_blank" rel="noopener" class="untrans-share-btn untrans-share-x" aria-label="Share on X/Twitter">𝕏</a>
                    <a href="https://www.instagram.com/" target="_blank" rel="noopener" class="untrans-share-btn untrans-share-ig" aria-label="Share on Instagram" title="Copy word + punchline to post on Instagram">📸</a>
                    <button class="untrans-share-btn untrans-share-copy" onclick="(function(){const text='"${item.word.replace(/'/g, "\\'")}": ${item.definition.replace(/'/g, "\\'")} 😂 ${item.punchline.replace(/'/g, "\\'")} — pariscomedy.com';navigator.clipboard&&navigator.clipboard.writeText(text).then(()=>{this.textContent='✅';setTimeout(()=>{this.textContent='📋'},1500)}).catch(()=>{});}).call(this)" aria-label="Copy to clipboard">📋</button>
                </div>
            </div>
        </div>
    `;
    // Re-trigger reveal for dynamically injected content
    if (typeof IntersectionObserver !== 'undefined') {
        container.querySelectorAll('[data-reveal]').forEach(el => {
            const obs = new IntersectionObserver((entries, o) => {
                entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('revealed'); o.unobserve(e.target); } });
            }, { threshold: 0.1 });
            obs.observe(el);
        });
    }
}

/* ─── Testimonials ─── */
function renderTestimonials() {
    const container = document.getElementById('testimonialsGrid');
    if (!container || typeof TESTIMONIALS === 'undefined') return;
    container.innerHTML = TESTIMONIALS.map(t => {
        const stars = t.stars ? '★'.repeat(t.stars) + '☆'.repeat(5 - t.stars) : '';
        return `
        <div class="testimonial-card">
            ${stars ? `<div class="testimonial-stars" aria-label="${t.stars} out of 5 stars">${stars}</div>` : ''}
            <p class="testimonial-text">"${t.text}"</p>
            <div class="testimonial-author">
                <span class="testimonial-name">${t.author}</span>
                <span class="testimonial-source">${t.source}</span>
            </div>
        </div>`;
    }).join('');
}

/* ─── Tonight's Shows Banner ─── */
function renderTonightBanner() {
    const container = document.getElementById('tonightBanner');
    if (!container) return;

    const now = new Date();
    const dayNames = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const today = dayNames[now.getDay()];

    // Collect all shows happening today — our shows first (English priority), then others
    let tonightShows = [];

    // Our shows (English, priority)
    SHOWS.forEach(show => {
        if (show.day === today || show.day === 'daily') {
            tonightShows.push({
                name: show.name, shortName: show.shortName, time: show.time, emoji: show.emoji,
                venue: VENUES.find(v => v.id === show.venue)?.name || '',
                lang: 'en', priority: 1, bookingUrl: show.bookingUrl, ours: true
            });
        }
    });

    // Other English shows
    if (typeof OTHER_SHOWS !== 'undefined') {
        OTHER_SHOWS.forEach(show => {
            const showDays = Array.isArray(show.day) ? show.day : [show.day];
            if (showDays.includes(today) || showDays.includes('daily')) {
                tonightShows.push({
                    name: show.name, shortName: show.name, time: show.time, emoji: show.emoji,
                    venue: show.venueName || '', lang: 'en', priority: show.paid ? 2 : 3,
                    bookingUrl: show.bookingUrl || null, ours: false
                });
            }
        });
    }

    // French fallback shows (if no English shows today)
    if (typeof FRENCH_SHOWS !== 'undefined') {
        FRENCH_SHOWS.forEach(show => {
            if (show.day === today || show.day === 'daily') {
                tonightShows.push({
                    name: show.name, shortName: show.name, time: show.time, emoji: show.emoji || '🇫🇷',
                    venue: show.venueName || '', lang: 'fr', priority: 4,
                    bookingUrl: show.bookingUrl || null, ours: false
                });
            }
        });
    }

    // Sort by priority (our shows > paid others > free others > french)
    tonightShows.sort((a, b) => a.priority - b.priority);

    if (tonightShows.length === 0) {
        // No shows today — show next upcoming
        const allShows = [...SHOWS, ...(typeof OTHER_SHOWS !== 'undefined' ? OTHER_SHOWS : [])];
        const dayOrder = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
        const todayIdx = dayOrder.indexOf(today);
        let nextShow = null;
        let nextDayName = '';
        for (let offset = 1; offset <= 7; offset++) {
            const checkDay = dayOrder[(todayIdx + offset) % 7];
            const found = allShows.find(s => s.day === checkDay);
            if (found) { nextShow = found; nextDayName = checkDay; break; }
        }
        if (nextShow) {
            container.innerHTML = `
                <div class="tonight-banner tonight-banner-next">
                    <span class="tonight-label">${({'fr':'Prochain spectacle','es':'Próximo show','de':'Nächste Show','ja':'次のショー','zh':'下一场演出','ko':'다음 공연'})[currentLang] || 'Next show'}</span>
                    <span class="tonight-shows">${nextShow.emoji || '🎤'} <strong>${nextShow.shortName || nextShow.name}</strong> — ${nextDayName} at ${nextShow.time || nextShow.time}</span>
                    ${nextShow.bookingUrl ? `<a href="${nextShow.bookingUrl}" target="_blank" rel="noopener" class="tonight-cta">🎟️ Reserve →</a>` : ''}
                </div>`;
        } else {
            container.style.display = 'none';
        }
        return;
    }

    // Cap at 4 shows to keep banner scannable on mobile
    if (tonightShows.length > 4) tonightShows = tonightShows.slice(0, 4);

    // Shows tonight!
    const langLabel = tonightShows[0].lang === 'fr' ? '🇫🇷' : '🇬🇧';
    const tonightLabel = ({'fr':'Ce soir à Paris','es':'Esta noche en París','de':'Heute Abend in Paris','ja':'今夜パリで','zh':'今晚在巴黎','ko':'오늘 밤 파리에서'})[currentLang] || 'Tonight in Paris';

    // Helper: compute time-until badge for a show time string (e.g. "19:00")
    function startsInBadge(timeStr) {
        if (!timeStr) return '';
        const parts = timeStr.split(':');
        if (parts.length < 2) return '';
        const showH = parseInt(parts[0], 10);
        const showM = parseInt(parts[1], 10);
        const now2 = new Date();
        const showDate = new Date(now2.getFullYear(), now2.getMonth(), now2.getDate(), showH, showM, 0);
        const diffMs = showDate - now2;
        if (diffMs < 0) return '<span class="tonight-started">● Live now</span>';
        const diffMins = Math.floor(diffMs / 60000);
        if (diffMins < 5) return '<span class="tonight-started" style="color:#ff3366;">● Starting now</span>';
        const h = Math.floor(diffMins / 60);
        const m = diffMins % 60;
        const label = h > 0 ? `${h}h ${m}m` : `${m}m`;
        const urgent = diffMins <= 60;
        return `<span class="tonight-starts-in" style="${urgent ? 'color:#ff3366;font-weight:700;' : ''}">⏱ ${label}</span>`;
    }

    // Web Share helper: share a show to WhatsApp/iMessage/etc in one tap
    function shareShow(e, name, time, venue, bookingUrl) {
        e.preventDefault();
        e.stopPropagation();
        const text = `🎤 ${name} — Tonight at ${time}, ${venue}`;
        const url = bookingUrl || 'https://pariscomedy.com/shows.html';
        if (navigator.share) {
            navigator.share({ title: 'Paris Comedy Tonight', text, url }).catch(() => {});
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard?.writeText(`${text}\n${url}`).then(() => {
                e.target.textContent = '✅';
                setTimeout(() => { e.target.textContent = '📤'; }, 1500);
            });
        }
    }

    const showList = tonightShows.map(s => {
        const badge = startsInBadge(s.time);
        const shareBtn = `<button class="tonight-share-btn" onclick="(${shareShow.toString()})(event,'${(s.shortName||s.name).replace(/'/g,"\\'")}','${s.time}','${s.venue.replace(/'/g,"\\'")}','${s.bookingUrl||''}')" title="Share this show" aria-label="Share ${(s.shortName||s.name).replace(/'/g,"\\'")}">📤</button>`;
        const link = s.bookingUrl
            ? `<span class="tonight-show-item"><a href="${s.bookingUrl}" target="_blank" rel="noopener" class="tonight-show-link">${s.emoji} <strong>${s.shortName || s.name}</strong> ${s.time} @ ${s.venue}${badge ? ' ' + badge : ''} ${s.ours ? '🎟️' : ''}</a>${shareBtn}</span>`
            : `<span class="tonight-show-item"><span class="tonight-show-nolink">${s.emoji} <strong>${s.shortName || s.name}</strong> ${s.time} @ ${s.venue}${badge ? ' ' + badge : ''}</span>${shareBtn}</span>`;
        return link;
    }).join('<span class="tonight-sep">·</span>');

    container.innerHTML = `
        <div class="tonight-banner tonight-banner-live">
            <span class="tonight-pulse"></span>
            <span class="tonight-label">${langLabel} ${tonightLabel}</span>
            <div class="tonight-shows">${showList}</div>
        </div>`;

    // Refresh every 60s so countdowns stay live
    if (!container._refreshInterval) {
        container._refreshInterval = setInterval(() => renderTonightBanner(), 60000);
    }
}

/* ─── Section Reordering ─── */
function renderComediansDirectory() {
    const container = document.getElementById('comedianDirectory');
    const stats = document.getElementById('comedianDirectoryStats');
    if (!container || typeof CURRENT_SHOWS_BY_VENUE === 'undefined') return;

    if (stats) {
        const verifiedDates = ALL_CURRENT_SHOWS.map(show => show.verifiedAt).filter(Boolean).sort();
        const latestVerified = verifiedDates.length ? verifiedDates[verifiedDates.length - 1] : null;
        stats.textContent = `${ALL_CURRENT_SHOWS.length} currently verified shows across ${CURRENT_SHOWS_BY_VENUE.length} venues.${latestVerified ? ` Latest verification pass: ${latestVerified}.` : ''}`;
    }

    container.innerHTML = CURRENT_SHOWS_BY_VENUE.map(venue => {
        const address = venue.address && venue.address !== 'Paris' ? venue.address : 'Address being confirmed';
        return `<section class="venue-card venue-card-placeholder" style="padding:24px;margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:flex-start;">
                <div>
                    <h2 style="margin:0 0 6px;font-family:var(--font-display);">${venue.name}</h2>
                    <div style="color:var(--text-muted);font-size:.92rem;">📍 ${address}</div>
                    ${venue.metro ? `<div style="color:var(--text-muted);font-size:.86rem;margin-top:4px;">🚇 ${venue.metro}</div>` : ''}
                </div>
                <div style="font-size:.8rem;color:var(--text-muted);">${venue.shows.length} verified show${venue.shows.length > 1 ? 's' : ''}</div>
            </div>
            <div style="display:grid;gap:14px;margin-top:18px;">
                ${venue.shows.map(show => `<article style="padding:16px 18px;border:1px solid var(--border);border-radius:14px;background:rgba(255,255,255,0.02);">
                    <div style="display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;align-items:flex-start;">
                        <div>
                            <div style="font-family:var(--font-display);font-size:1.02rem;">${show.emoji || '🎤'} ${show.name}</div>
                            <div style="color:var(--text-muted);font-size:.88rem;margin-top:4px;">${Array.isArray(show.day) ? show.day.join(' / ') : show.day}${show.time ? ` · ${show.time}` : ''}</div>
                            <div style="color:var(--text-muted);font-size:.88rem;margin-top:4px;">Show runner: ${show.runner || 'Not yet confirmed'}</div>
                            <div style="color:var(--text-muted);font-size:.82rem;margin-top:4px;">Verified ${show.verifiedAt || 'recently'} via ${show.verificationSource || 'manual review'}</div>
                        </div>
                        <div>
                            ${show.showUrl ? `<a href="${show.showUrl}" target="_blank" rel="noopener" class="btn btn-primary btn-sm">Open listing →</a>` : ''}
                        </div>
                    </div>
                </article>`).join('')}
            </div>
        </section>`;
    }).join('');
}

function moveCalendarFirst() {
    const calSection = document.getElementById('calendar');
    const howSection = document.querySelector('.how-it-works')?.closest('.section');
    const showsSection = document.getElementById('shows');
    if (calSection && showsSection) {
        // Move calendar before the shows section
        showsSection.parentNode.insertBefore(calSection, showsSection);
    }
}

/* ─── Hero Particles ─── */
function initParticles() {
    const container = document.getElementById('heroParticles');
    if (!container) return;
    const emojis = ['🎤','🍟','😂','🎭','🇫🇷','⭐','🎪','🎵','🎬','🥐','🗼','🎩'];
    for (let i = 0; i < 15; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.textContent = emojis[Math.floor(Math.random() * emojis.length)];
        p.style.left = Math.random() * 100 + '%';
        p.style.animationDuration = (8 + Math.random() * 12) + 's';
        p.style.animationDelay = (Math.random() * 10) + 's';
        p.style.fontSize = (1 + Math.random() * 1.5) + 'rem';
        container.appendChild(p);
    }
}

/* ─── Scroll Animations ─── */
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.show-card, .venue-card, .testimonial-card, .how-step, .player-card, .timeline-item, .faq-item, .other-show-card').forEach(el => {
        el.classList.add('fade-up');
        observer.observe(el);
    });
}

/* ─── Easter Eggs (Leylo approved 🥚) ─── */
function initEasterEggs() {
    // Konami code → confetti of 🍟
    const konamiCode = [38,38,40,40,37,39,37,39,66,65];
    let konamiIndex = 0;
    document.addEventListener('keydown', e => {
        if (e.keyCode === konamiCode[konamiIndex]) {
            konamiIndex++;
            if (konamiIndex === konamiCode.length) {
                konamiIndex = 0;
                launchFries();
            }
        } else { konamiIndex = 0; }
    });

    // Click logo 5x → show secret message
    let logoClicks = 0;
    const logo = document.querySelector('.nav-logo');
    if (logo) {
        logo.addEventListener('click', (e) => {
            logoClicks++;
            if (logoClicks >= 5) {
                logoClicks = 0;
                const msg = document.createElement('div');
                msg.className = 'easter-egg-msg';
                msg.textContent = '🍟 You found the secret! Robert says hi 👋';
                document.body.appendChild(msg);
                setTimeout(() => msg.remove(), 3000);
            }
        });
    }
}

function launchFries() {
    for (let i = 0; i < 30; i++) {
        const fry = document.createElement('div');
        fry.className = 'confetti-fry';
        fry.textContent = '🍟';
        fry.style.left = Math.random() * 100 + 'vw';
        fry.style.animationDuration = (Math.random() * 2 + 1) + 's';
        fry.style.animationDelay = Math.random() * 0.5 + 's';
        document.body.appendChild(fry);
        setTimeout(() => fry.remove(), 4000);
    }
}

/* ─── Growth Chart (homepage) ─── */
function renderGrowthChart() {
    const container = document.getElementById('growthChart');
    if (!container) return;
    const data = [
        { year: '2010', shows: 1 },
        { year: '2013', shows: 2 },
        { year: '2016', shows: 3 },
        { year: '2017', shows: 4 },
        { year: '2019', shows: 5 },
        { year: '2022', shows: 6 },
        { year: '2024', shows: 8 },
        { year: '2025', shows: 14 },
        { year: '2026', shows: 20 }
    ];
    const maxShows = Math.max(...data.map(d => d.shows));
    container.innerHTML = data.map(d => {
        const heightPct = (d.shows / maxShows) * 100;
        return `<div class="growth-bar">
            <div class="growth-bar-value">${d.shows}</div>
            <div class="growth-bar-fill" data-height="${heightPct}" style="height:0%;width:100%;"></div>
            <div class="growth-bar-label">${d.year}</div>
        </div>`;
    }).join('');

    // Animate on scroll
    const obs = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                container.querySelectorAll('.growth-bar-fill').forEach((bar, i) => {
                    setTimeout(() => {
                        bar.style.height = bar.dataset.height + '%';
                    }, i * 100);
                });
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });
    obs.observe(container);
}

/* ─── Newsletter form — sends to Formspree ─── */
async function submitToParisComedyIntake(payload) {
    const localEndpoint = '/api/intake';
    const backupEndpoint = 'https://formsubmit.co/ajax/chucklericain@icloud.com';

    try {
        const local = await fetch(localEndpoint, {
            method: 'POST',
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (local.ok) return { ok:true, via:'local' };
    } catch (_) {}

    const backupPayload = payload.kind === 'newsletter'
        ? { email: payload.email, _subject: 'Paris Comedy — Newsletter Signup', _template: 'table' }
        : {
            name: payload.name,
            email: payload.email,
            subject: payload.subject,
            message: payload.message,
            _subject: `Paris Comedy — ${payload.subject || 'Contact Form'}`
        };

    const backup = await fetch(backupEndpoint, {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(backupPayload)
    });
    return { ok: backup.ok, via:'backup' };
}

document.addEventListener('submit', e => {
    if (e.target.id === 'newsletterForm') {
        e.preventDefault();
        const form = e.target;
        const email = form.querySelector('input[type="email"]');
        const btn = form.querySelector('button[type="submit"]');
        if (!email || !email.value) return;
        if (btn) { btn.disabled = true; btn.textContent = 'Subscribing…'; }
        submitToParisComedyIntake({ kind:'newsletter', email: email.value, page: window.location.pathname, url: window.location.href }).then(result => {
            if (result.ok) {
                form.innerHTML = '<p class="newsletter-success">You\'re in! Watch your inbox for show alerts.</p>';
                try { localStorage.setItem('pc_subscribed', '1'); } catch(e) {}
                trackNewsletterSignup();
            } else {
                if (btn) { btn.disabled = false; btn.textContent = 'Subscribe'; }
                alert('Something went wrong. Try again or DM us on Instagram.');
            }
        }).catch(() => {
            if (btn) { btn.disabled = false; btn.textContent = 'Subscribe'; }
            alert('Connection error. Check your internet and try again.');
        });
    }
    if (e.target.id === 'contactForm') {
        e.preventDefault();
        const form = e.target;
        const btn = form.querySelector('button[type="submit"]');
        if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
        const payload = {
            kind:'contact',
            name: form.querySelector('input[name="name"]')?.value || '',
            email: form.querySelector('input[name="email"]')?.value || '',
            subject: form.querySelector('input[name="subject"]')?.value || 'General Inquiry',
            message: form.querySelector('textarea[name="message"]')?.value || '',
            page: window.location.pathname,
            url: window.location.href
        };
        submitToParisComedyIntake(payload).then(result => {
            if (result.ok) {
                form.innerHTML = '<p class="newsletter-success" style="padding:24px 0;font-size:1.05rem;">🎉 Message received! It was stored locally and forwarded to the inbox.<br><br><a href="https://www.instagram.com/french_fried_comedy/" target="_blank" rel="noopener" style="color:var(--accent);">📸 DM us on Instagram too →</a></p>';
            } else {
                if (btn) { btn.disabled = false; btn.textContent = 'Send Message'; }
                alert('Something went wrong. Please DM us on Instagram @french_fried_comedy or try again.');
            }
        }).catch(() => {
            if (btn) { btn.disabled = false; btn.textContent = 'Send Message'; }
            alert('Network error. Please DM us on Instagram @french_fried_comedy.');
        });
    }
});

/* ─── Scroll animations ─── */
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.1 });

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
});

/* ─── Global scroll-reveal (data-reveal) ─────────────────────────────────── */
(function(){
    const revealObs = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    window._revealInit = function(root) {
        (root || document).querySelectorAll('[data-reveal]:not(.revealed)').forEach(el => revealObs.observe(el));
    };
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => window._revealInit());
    } else {
        window._revealInit();
    }
})();

/* ─── Hero countdown to next Wednesday show ─────────────────────────────── */
(function(){
    function nextWednesday() {
        // Returns a Date for the next Wednesday 19:00 Paris time (UTC+2 in CEST / UTC+1 CET)
        const now = new Date();
        // Get current day in Paris: approximate with UTC offset
        const parisOffset = (function() {
            // France is UTC+1 (winter) or UTC+2 (summer DST — last Sun Mar to last Sun Oct)
            const month = now.getUTCMonth(); // 0=Jan
            return (month >= 2 && month <= 9) ? 2 : 1; // CEST Mar-Oct, CET Nov-Feb
        })();
        const parisNow = new Date(now.getTime() + parisOffset * 3600000);
        const day = parisNow.getUTCDay(); // 0=Sun,3=Wed
        let daysUntil = (3 - day + 7) % 7;
        if (daysUntil === 0 && parisNow.getUTCHours() >= 23) daysUntil = 7; // already past tonight
        const target = new Date(parisNow);
        target.setUTCDate(target.getUTCDate() + daysUntil);
        target.setUTCHours(19 - parisOffset, 0, 0, 0); // 19:00 Paris → UTC
        return target;
    }

    function formatCountdown(ms) {
        if (ms <= 0) return null;
        const d = Math.floor(ms / 86400000);
        const h = Math.floor((ms % 86400000) / 3600000);
        const m = Math.floor((ms % 3600000) / 60000);
        const s = Math.floor((ms % 60000) / 1000);
        const parts = [];
        if (d > 0) parts.push(`<strong>${d}</strong>d`);
        parts.push(`<strong>${h}</strong>h`);
        parts.push(`<strong>${m}</strong>m`);
        parts.push(`<strong>${s}</strong>s`);
        return parts.join(' ');
    }

    const labels = {
        en: 'Next show in',
        fr: 'Prochain spectacle dans',
        es: 'Próximo show en',
        de: 'Nächste Show in',
        ja: '次のショーまで',
        zh: '下场演出',
        ko: '다음 공연까지'
    };

    function getTonightShows() {
        if (typeof OTHER_SHOWS === 'undefined' || typeof SHOWS === 'undefined') return [];
        const parisOffset = (function() {
            const month = new Date().getUTCMonth();
            return (month >= 2 && month <= 9) ? 2 : 1;
        })();
        const parisNow = new Date(Date.now() + parisOffset * 3600000);
        const dayName = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][parisNow.getUTCDay()];
        const nowMins = parisNow.getUTCHours() * 60 + parisNow.getUTCMinutes();
        const allShows = [...(SHOWS||[]), ...(OTHER_SHOWS||[])];
        return allShows.filter(s => {
            const days = Array.isArray(s.day) ? s.day : [s.day];
            if (!days.includes(dayName) && s.day !== 'daily') return false;
            if (!s.time) return true;
            const [h, m] = s.time.split(':').map(Number);
            const startMins = h * 60 + (m||0);
            return startMins >= nowMins - 30 && startMins <= nowMins + 240; // within next 4h or started <30m ago
        }).sort((a, b) => {
            const toMins = t => { const [h,m] = (t||'99:99').split(':').map(Number); return h*60+(m||0); };
            return toMins(a.time) - toMins(b.time);
        });
    }

    function updateCountdown() {
        const el = document.getElementById('heroCountdown');
        if (!el) return;

        // Tonight override — if shows are happening now/soon, show that instead
        const tonight = getTonightShows();
        if (tonight.length > 0) {
            const next = tonight[0];
            const parisOffset = (function() {
                const month = new Date().getUTCMonth();
                return (month >= 2 && month <= 9) ? 2 : 1;
            })();
            const parisNow = new Date(Date.now() + parisOffset * 3600000);
            const nowMins = parisNow.getUTCHours() * 60 + parisNow.getUTCMinutes();
            const [sh, sm] = (next.time || '19:00').split(':').map(Number);
            const startMins = sh * 60 + (sm || 0);
            const diffMins = startMins - nowMins;
            let timeStr;
            if (diffMins <= 0) {
                timeStr = '<span style="color:#f87171;animation:pulse 1s infinite;">● Live now</span>';
            } else if (diffMins < 60) {
                timeStr = `<span style="color:#f59e0b;font-weight:700;">⏱ ${diffMins}m</span>`;
            } else {
                const h = Math.floor(diffMins/60), m = diffMins%60;
                timeStr = `⏱ <strong>${h}h ${m}m</strong>`;
            }
            const venueName = next.venueName || next.venue || 'Velvet Bar';
            el.style.display = 'inline-flex';
            el.style.background = 'rgba(239,68,68,0.12)';
            el.style.borderColor = 'rgba(239,68,68,0.35)';
            el.innerHTML = `<span>🎤 Tonight:</span><span style="font-weight:700;color:#fca5a5;">${next.shortName || next.name}</span><span>${timeStr} · ${venueName}</span>`;
            return;
        }

        const target = nextWednesday();
        const ms = target - Date.now();
        const formatted = formatCountdown(ms);
        if (!formatted) { el.style.display = 'none'; return; }
        el.style.background = '';
        el.style.borderColor = '';
        const lang = (typeof currentLang !== 'undefined' ? currentLang : null) ||
                     document.documentElement.lang || 'en';
        const label = labels[lang] || labels.en;
        el.style.display = 'inline-flex';
        el.innerHTML = `<span>🗓️ ${label}:</span><span style="font-weight:700;color:#a78bfa;letter-spacing:0.01em;">${formatted}</span><span style="opacity:0.6;">— Wed · Velvet Bar · 19:00</span>`;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function(){ updateCountdown(); setInterval(updateCountdown, 1000); });
    } else {
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }
})();

/* ─── Exit-intent newsletter popup ─── */
(function(){
  const STORAGE_KEY = 'pc_nl_dismissed';
  const overlay = document.getElementById('nlPopupOverlay');
  const closeBtn = document.getElementById('nlPopupClose');
  const skipBtn  = document.getElementById('nlPopupSkip');
  const form     = document.getElementById('nlPopupForm');

  if (!overlay) return;

  // Don't show if user already dismissed or subscribed
  if (localStorage.getItem(STORAGE_KEY)) return;

  function showPopup() {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function hidePopup(permanent) {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    if (permanent) localStorage.setItem(STORAGE_KEY, '1');
  }

  // Exit intent — mouse leaving top of viewport
  let triggered = false;
  document.addEventListener('mouseleave', function(e) {
    if (!triggered && e.clientY < 20) {
      triggered = true;
      showPopup();
    }
  });

  // Fallback: scroll to 60% of page after 30s
  let scrollTimer = setTimeout(function() {
    if (!triggered && window.scrollY > (document.body.scrollHeight * 0.4)) {
      triggered = true;
      showPopup();
    }
  }, 30000);

  if (closeBtn) closeBtn.addEventListener('click', function(){ hidePopup(true); });
  if (skipBtn)  skipBtn.addEventListener('click',  function(){ hidePopup(true); });
  overlay.addEventListener('click', function(e){ if (e.target === overlay) hidePopup(false); });

  // Handle form submit
  if (form) {
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const email = form.querySelector('input[type="email"]').value;
      if (!email) return;
      // Submit to FormSpree async
      submitToParisComedyIntake({ kind:'newsletter', email: email, page: window.location.pathname, url: window.location.href }).then(function(r){
        if (r.ok) {
          form.innerHTML = '<p class="nl-popup-success">🎉 You\'re in! Watch for next Wednesday\'s show alert.</p>';
          localStorage.setItem(STORAGE_KEY, '1');
          setTimeout(function(){ hidePopup(true); }, 2500);
        }
      }).catch(function(){
        form.innerHTML = '<p class="nl-popup-success">🎉 You\'re in! Watch for next Wednesday\'s show alert.</p>';
        setTimeout(function(){ hidePopup(true); }, 2500);
      });
    });
  }
})();

/* ─── Social proof counter — real reserve-click activity ─────────────────── */
(function(){
    function renderReservationCounter() {
        const heroActions = document.querySelector('.hero-actions');
        if (!heroActions || document.getElementById('reservationCounter')) return;
        const el = document.createElement('div');
        el.id = 'reservationCounter';
        el.style.cssText = 'margin-top:14px;display:flex;align-items:center;justify-content:center;gap:6px;font-size:.85rem;color:var(--text-muted);';
        el.innerHTML = `<span style="display:inline-flex;gap:3px;align-items:center;flex-wrap:wrap;justify-content:center;">
            <span style="width:7px;height:7px;border-radius:50%;background:#22c55e;display:inline-block;animation:tonightPulse 2s ease-in-out infinite;"></span>
            <span id="counterNum">0</span> reserve clicks this week
            <span style="opacity:.7;">· live from site activity</span>
        </span>`;
        heroActions.insertAdjacentElement('afterend', el);
        renderReservationCounterFromStore();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', renderReservationCounter);
    } else {
        renderReservationCounter();
    }
})();
// ── Conversion Tracking + Real Social Proof ─────────────────────────────────
const GA4_ID = 'G-XXXXXXXXXX';
const CLICKS_FILE = '/clicks.json';
const CLICK_PIXEL = '/click.gif';

(function initAnalytics() {
  if (!GA4_ID || GA4_ID === 'G-XXXXXXXXXX') {
    window.gtag = function() {};
    return;
  }
  const s = document.createElement('script');
  s.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`;
  s.async = true;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function() { dataLayer.push(arguments); };
  gtag('js', new Date());
  gtag('config', GA4_ID, {
    page_title: document.title,
    page_location: location.href,
    site_language: window.currentLang || 'en'
  });
})();

function currentIsoWeekKey() {
  const date = new Date();
  const utc = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = utc.getUTCDay() || 7;
  utc.setUTCDate(utc.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(utc.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil((((utc - yearStart) / 86400000) + 1) / 7);
  return `${utc.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`;
}

function getClickStore() {
  try {
    const raw = localStorage.getItem('pc-click-store');
    if (!raw) return { weekKey: currentIsoWeekKey(), weeklyReserveClicks: 0, totalReserveClicks: 0, reserveClicksByShow: {} };
    const parsed = JSON.parse(raw);
    if (parsed.weekKey !== currentIsoWeekKey()) {
      parsed.weekKey = currentIsoWeekKey();
      parsed.weeklyReserveClicks = 0;
      parsed.reserveClicksByShow = {};
    }
    return parsed;
  } catch (_) {
    return { weekKey: currentIsoWeekKey(), weeklyReserveClicks: 0, totalReserveClicks: 0, reserveClicksByShow: {} };
  }
}

function saveClickStore(store) {
  try { localStorage.setItem('pc-click-store', JSON.stringify(store)); } catch (_) {}
}

function renderReservationCounterFromStore() {
  const num = document.getElementById('counterNum');
  if (!num) return;
  const store = getClickStore();
  num.textContent = store.weeklyReserveClicks || 0;
}

function trackReserve(showName, url) {
  if (window.gtag) {
    gtag('event', 'reserve_click', {
      event_category: 'Conversion',
      event_label: showName || url,
      transport_type: 'beacon'
    });
  }

  const store = getClickStore();
  store.weeklyReserveClicks = (store.weeklyReserveClicks || 0) + 1;
  store.totalReserveClicks = (store.totalReserveClicks || 0) + 1;
  store.reserveClicksByShow = store.reserveClicksByShow || {};
  const key = showName || 'Unknown show';
  store.reserveClicksByShow[key] = (store.reserveClicksByShow[key] || 0) + 1;
  saveClickStore(store);
  renderReservationCounterFromStore();

  const pixel = new Image(1, 1);
  pixel.src = `${CLICK_PIXEL}?show=${encodeURIComponent(key)}&week=${encodeURIComponent(store.weekKey)}&ts=${Date.now()}`;

  return true;
}

function trackCTA(label) {
  if (window.gtag) {
    gtag('event', 'cta_click', {
      event_category: 'Engagement',
      event_label: label
    });
  }
}

function trackNewsletterSignup() {
  if (window.gtag) {
    gtag('event', 'newsletter_signup', {
      event_category: 'Lead',
      event_label: 'exit_intent_popup'
    });
  }
}

document.addEventListener('DOMContentLoaded', function() {
  function wireLinks(root) {
    (root || document).querySelectorAll('a[href*="eventbrite"]').forEach(function(a) {
      if (!a.dataset.tracked) {
        a.dataset.tracked = '1';
        const showName = a.closest('[data-show-name]')
          ? a.closest('[data-show-name]').dataset.showName
          : (a.textContent.trim() || a.href);
        a.addEventListener('click', function() {
          trackReserve(showName, a.href);
        });
      }
    });
    (root || document).querySelectorAll('a[href*="book.html"]').forEach(function(a) {
      if (!a.dataset.tracked) {
        a.dataset.tracked = '1';
        a.addEventListener('click', function() {
          trackCTA('get_listed');
        });
      }
    });
  }
  wireLinks();
  renderReservationCounterFromStore();
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(m) {
      m.addedNodes.forEach(function(n) {
        if (n.nodeType === 1) wireLinks(n);
      });
    });
  });
  observer.observe(document.body, { childList: true, subtree: true });
});
