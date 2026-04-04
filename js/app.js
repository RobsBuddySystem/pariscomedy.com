/* Paris Comedy — Main App */
document.addEventListener('DOMContentLoaded', () => {
    initLanguage();
    initNav();
    initPage();
    initParticles();
    initScrollAnimations();
    initEasterEggs();
});

/* ─── Language Switcher ─── */
let currentLang = localStorage.getItem('pc-lang') || 'en';

function initLanguage() {
    const switcher = document.getElementById('langSwitcher');
    if (!switcher) return;
    switcher.querySelectorAll('[data-lang]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLang);
        btn.addEventListener('click', () => {
            currentLang = btn.dataset.lang;
            localStorage.setItem('pc-lang', currentLang);
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
        renderFeaturedShows(); renderCalendar(); renderQuote(); renderTestimonials();
    }
    if (page === 'shows') { renderAllShows(); renderOtherShows(); initFilters(); }
    if (page === 'venues') { renderVenueMap(); renderVenueCards(); }
    if (page === 'history') { renderTimeline(); renderKeyPlayers(); renderNotableVisitors(); }
}

/* ─── Shows ─── */
function renderShowCard(show) {
    const venue = VENUES.find(v => v.id === show.venue);
    const typeLabel = show.type === 'standup' ? t('filters.standup') : t('filters.openmic');
    return `<article class="show-card" data-type="${show.type}">
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
                <span class="show-card-price">${show.price}</span>
                <a href="${show.bookingUrl}" target="_blank" rel="noopener" class="show-card-link">🎟️ Reserve Your Spot →</a>
            </div>
        </div>
    </article>`;
}

function renderFeaturedShows() {
    const grid = document.getElementById('featuredShowsGrid');
    if (!grid) return;
    let shows = [...SHOWS];
    if (currentLang === 'fr') {
        // French page: Velvet Bar brand shows first (the venue name, not FFCN brand)
        shows.sort((a,b) => {
            if (a.id === 'velvet-comedy') return -1;
            if (b.id === 'velvet-comedy') return 1;
            if (a.id === 'velvet-openmic') return -1;
            if (b.id === 'velvet-openmic') return 1;
            if (a.id === 'ffcn') return -1;
            if (b.id === 'ffcn') return 1;
            return 0;
        });
        grid.innerHTML = shows.map(renderShowCard).join('');
    } else {
        // All other languages: FFCN first (the English/international brand), then featured
        shows.sort((a,b) => {
            if (a.id === 'ffcn') return -1;
            if (b.id === 'ffcn') return 1;
            if (a.featured && !b.featured) return -1;
            if (!a.featured && b.featured) return 1;
            return 0;
        });
        grid.innerHTML = shows.filter(s => s.featured).map(renderShowCard).join('');
    }
}

function renderAllShows(filter = 'all') {
    const grid = document.getElementById('showsGrid');
    if (!grid) return;
    const filtered = filter === 'all' ? SHOWS : SHOWS.filter(s => s.type === filter);
    grid.innerHTML = filtered.map(renderShowCard).join('');
}

function renderOtherShows() {
    const container = document.getElementById('otherShowsList');
    if (!container || typeof OTHER_SHOWS === 'undefined') return;
    container.innerHTML = OTHER_SHOWS.map(show => `
        <div class="other-show-card${!show.paid ? ' placeholder-card' : ''}">
            <div class="other-show-name">${show.emoji || '🎤'} ${show.name}</div>
            <div class="other-show-venue">📍 ${show.venueName} · ${show.day}${show.time ? ' · '+show.time : ''}</div>
            <div class="other-show-desc">${show.description}</div>
            ${show.paid && show.bookingUrl ? `<a href="${show.bookingUrl}" target="_blank" rel="noopener" class="show-card-link" style="display:inline-block;margin-top:8px;">🎟️ Reserve Your Spot →</a>` : '<div class="other-show-cta"><span class="placeholder-badge">📋 Not yet listed</span> <a href="book.html" class="other-show-link">Get listed for €1/month →</a></div>'}
        </div>
    `).join('');
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
            tooltip.innerHTML = dayEvents.map(e => `<div>${e.emoji} <strong>${e.shortName}</strong> · ${e.time} · ${e.venue}</div>`).join('');
            cell.appendChild(tooltip);
            setTimeout(() => tooltip.remove(), 4000);
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
        return `<div class="venue-card venue-card-featured">
            <div class="venue-card-badge-top">⭐ Featured Venue</div>
            <div class="venue-card-name">${i+1}. ${venue.name}</div>
            <div class="venue-card-addr">📍 ${venue.address}</div>
            <div class="venue-card-metro">🚇 ${venue.metro || ''}</div>
            <div class="venue-card-desc">${venue.description || ''}</div>
            <div class="venue-card-shows">${showsAtVenue.map(s=>`<span class="venue-show-tag">${s.emoji} ${s.shortName} — ${s.day} ${s.time}</span>`).join('')}</div>
        </div>`;
    }).join('');
    
    if (others.length) {
        html += `<div style="grid-column:1/-1;margin-top:32px;"><h3 style="font-family:var(--font-display);font-size:1.3rem;margin-bottom:8px;color:var(--text-dim);">Other Comedy Venues in Paris</h3><p style="color:var(--text-muted);font-size:0.9rem;margin-bottom:20px;">These venues host English-language comedy. Want your show featured with full booking? <a href="book.html">Get listed →</a></p></div>`;
        html += others.map((venue, i) => {
            const otherHere = (typeof OTHER_SHOWS !== 'undefined') ? OTHER_SHOWS.filter(s => s.venueName === venue.name) : [];
            return `<div class="venue-card venue-card-placeholder">
                <div class="venue-card-name">${listed.length + i + 1}. ${venue.name}</div>
                <div class="venue-card-addr">📍 ${venue.address}</div>
                <div class="venue-card-metro">🚇 ${venue.metro || ''}</div>
                <div class="venue-card-desc">${venue.description || ''}</div>
                <div class="venue-card-shows">${otherHere.map(s=>`<span class="venue-show-tag">${s.emoji} ${s.name} — ${s.day}</span>`).join('') || '<span style="color:var(--text-muted);font-size:0.82rem">Shows not yet listed — <a href="book.html">claim this listing</a></span>'}</div>
            </div>`;
        }).join('');
    }
    container.innerHTML = html;
}

/* ─── History ─── */
function renderTimeline() {
    const container = document.getElementById('timelineContainer');
    if (!container || typeof TIMELINE === 'undefined') return;
    container.innerHTML = TIMELINE.map((item, i) => `
        <div class="timeline-item ${i % 2 === 0 ? 'left' : 'right'}">
            <div class="timeline-marker"></div>
            <div class="timeline-content">
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
    container.innerHTML = KEY_PLAYERS.map(player => `
        <div class="player-card">
            <div class="player-avatar">${player.emoji}</div>
            <h3 class="player-name">${player.name}</h3>
            <span class="player-title">${player.title}</span>
            <p class="player-bio">${currentLang === 'fr' ? (player.bioFr||player.bio) : currentLang === 'es' ? (player.bioEs||player.bio) : player.bio}</p>
        </div>
    `).join('');
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

/* ─── Testimonials ─── */
function renderTestimonials() {
    const container = document.getElementById('testimonialsGrid');
    if (!container || typeof TESTIMONIALS === 'undefined') return;
    container.innerHTML = TESTIMONIALS.map(t => `
        <div class="testimonial-card">
            <p class="testimonial-text">"${t.text}"</p>
            <div class="testimonial-author">
                <span class="testimonial-name">${t.author}</span>
                <span class="testimonial-source">${t.source}</span>
            </div>
        </div>
    `).join('');
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
        if (show.day === today) {
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
            if (show.day === today) {
                tonightShows.push({
                    name: show.name, shortName: show.name, time: show.time, emoji: show.emoji,
                    venue: show.venueName || '', lang: 'en', priority: show.paid ? 2 : 3,
                    bookingUrl: show.paid ? show.bookingUrl : null, ours: false
                });
            }
        });
    }

    // French fallback shows (if no English shows today)
    if (typeof FRENCH_SHOWS !== 'undefined') {
        FRENCH_SHOWS.forEach(show => {
            if (show.day === today) {
                tonightShows.push({
                    name: show.name, shortName: show.name, time: show.time, emoji: show.emoji || '🇫🇷',
                    venue: show.venueName || '', lang: 'fr', priority: 4,
                    bookingUrl: show.paid ? show.bookingUrl : null, ours: false
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

    // Shows tonight!
    const langLabel = tonightShows[0].lang === 'fr' ? '🇫🇷' : '🇬🇧';
    const tonightLabel = ({'fr':'Ce soir à Paris','es':'Esta noche en París','de':'Heute Abend in Paris','ja':'今夜パリで','zh':'今晚在巴黎','ko':'오늘 밤 파리에서'})[currentLang] || 'Tonight in Paris';

    const showList = tonightShows.map(s => {
        const link = s.bookingUrl
            ? `<a href="${s.bookingUrl}" target="_blank" rel="noopener" class="tonight-show-link">${s.emoji} <strong>${s.shortName || s.name}</strong> ${s.time} @ ${s.venue} ${s.ours ? '🎟️' : ''}</a>`
            : `<span class="tonight-show-nolink">${s.emoji} <strong>${s.shortName || s.name}</strong> ${s.time} @ ${s.venue}</span>`;
        return link;
    }).join('<span class="tonight-sep">·</span>');

    container.innerHTML = `
        <div class="tonight-banner tonight-banner-live">
            <span class="tonight-pulse"></span>
            <span class="tonight-label">${langLabel} ${tonightLabel}</span>
            <div class="tonight-shows">${showList}</div>
        </div>`;
}

/* ─── Section Reordering ─── */
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

/* ─── Newsletter form (placeholder) ─── */
document.addEventListener('submit', e => {
    if (e.target.id === 'newsletterForm') {
        e.preventDefault();
        const email = e.target.querySelector('input[type="email"]');
        if (email && email.value) {
            e.target.innerHTML = '<p class="newsletter-success">🎉 You\'re in! Watch your inbox for show alerts.</p>';
        }
    }
    if (e.target.id === 'contactForm') {
        e.preventDefault();
        e.target.innerHTML = '<p class="newsletter-success">🎉 Message sent! We\'ll get back to you soon.</p>';
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
