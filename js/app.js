/* Paris Comedy — Main App */
document.addEventListener('DOMContentLoaded', () => {
    initLanguage();
    initNav();
    initPage();
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
    if (page === 'home') { renderFeaturedShows(); renderCalendar(); renderQuote(); renderTestimonials(); }
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
            <p class="show-card-time">🕐 Every ${show.day} at ${show.time}</p>
            <p class="show-card-desc">${currentLang === 'fr' ? (show.descFr||show.description) : currentLang === 'es' ? (show.descEs||show.description) : show.description}</p>
            <div class="show-card-footer">
                <span class="show-card-price">${show.price}</span>
                <a href="${show.bookingUrl}" target="_blank" rel="noopener" class="show-card-link">🎟️ Book →</a>
            </div>
        </div>
    </article>`;
}

function renderFeaturedShows() {
    const grid = document.getElementById('featuredShowsGrid');
    if (!grid) return;
    grid.innerHTML = SHOWS.filter(s => s.featured).map(renderShowCard).join('');
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
        <div class="other-show-card">
            <div class="other-show-name">${show.name}</div>
            <div class="other-show-venue">📍 ${show.venue} · ${show.day}</div>
            <div class="other-show-desc">${show.description}</div>
            ${show.url ? `<a href="${show.url}" target="_blank" rel="noopener" class="other-show-link">Visit →</a>` : ''}
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
        html += `<div class="cal-day${isToday?' today':''}" data-day="${day}">
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
        const showsAtVenue = SHOWS.filter(s => s.venue === venue.id);
        return `<div class="venue-pin" style="left:${venue.mapX}%;top:${venue.mapY}%;">
            <span>${i+1}</span>
            <div class="venue-pin-tooltip"><strong>${venue.name}</strong><br>${venue.neighborhood}<br>${showsAtVenue.map(s=>`${s.emoji} ${s.shortName} · ${s.day}`).join('<br>')}</div>
        </div>`;
    }).join('');
}

function renderVenueCards() {
    const container = document.getElementById('venuesList');
    if (!container) return;
    container.innerHTML = VENUES.map((venue, i) => {
        const showsAtVenue = SHOWS.filter(s => s.venue === venue.id);
        return `<div class="venue-card">
            <div class="venue-card-name">${i+1}. ${venue.name}</div>
            <div class="venue-card-addr">📍 ${venue.address}</div>
            <div class="venue-card-metro">🚇 ${venue.metro || ''}</div>
            <div class="venue-card-desc">${venue.description || ''}</div>
            <div class="venue-card-shows">${showsAtVenue.map(s=>`<span class="venue-show-tag">${s.emoji} ${s.shortName} — ${s.day} ${s.time}</span>`).join('')}</div>
        </div>`;
    }).join('');
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
