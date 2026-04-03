document.addEventListener('DOMContentLoaded', () => {
    initNav(); renderShows(); renderCalendar(); renderVenues(); initFilters();
});

function initNav() {
    const toggle = document.getElementById('navToggle');
    const links = document.getElementById('navLinks');
    if (!toggle || !links) return;
    toggle.addEventListener('click', () => { links.classList.toggle('open'); toggle.classList.toggle('open'); });
    links.querySelectorAll('a').forEach(a => { a.addEventListener('click', () => { links.classList.remove('open'); toggle.classList.remove('open'); }); });
    window.addEventListener('scroll', () => { document.getElementById('nav')?.classList.toggle('scrolled', window.scrollY > 20); });
}

function renderShows(filter = 'all') {
    const grid = document.getElementById('showsGrid');
    if (!grid) return;
    const filtered = filter === 'all' ? SHOWS : SHOWS.filter(s => s.type === filter);
    grid.innerHTML = filtered.map(show => {
        const venue = VENUES.find(v => v.id === show.venue);
        const typeLabel = show.type === 'standup' ? 'Stand-Up' : 'Open Mic';
        return `<article class="show-card" data-type="${show.type}">
            <div class="show-card-img" style="background:linear-gradient(135deg,${show.type==='standup'?'#1a0515,#2a1020':'#0a1a0f,#102a15'});">${show.emoji}</div>
            <div class="show-card-body">
                <span class="show-card-type type-${show.type}">${typeLabel}</span>
                <h3 class="show-card-title">${show.name}</h3>
                <p class="show-card-venue">📍 ${venue?.name||''} · ${venue?.neighborhood||''}</p>
                <p class="show-card-time">🕐 Every ${show.day} at ${show.time}</p>
                <p class="show-card-desc">${show.description}</p>
                <div class="show-card-footer">
                    <span class="show-card-price">${show.price}</span>
                    <a href="${show.bookingUrl}" target="_blank" rel="noopener" class="show-card-link">🎟️ Book →</a>
                </div>
            </div>
        </article>`;
    }).join('');
}

function initFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderShows(btn.dataset.filter);
        });
    });
}

function renderCalendar() {
    const grid = document.getElementById('calendarGrid');
    if (!grid) return;
    const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    const firstDayOffset = 2; // April 2026 starts Wednesday
    let html = days.map(d => `<div class="cal-header">${d}</div>`).join('');
    for (let i = 0; i < firstDayOffset; i++) html += '<div class="cal-day empty"></div>';
    const today = new Date();
    const isCurrentMonth = today.getFullYear() === 2026 && today.getMonth() === 3;
    for (let day = 1; day <= 30; day++) {
        const dayEvents = APRIL_2026.filter(e => e.day === day);
        const isToday = isCurrentMonth && today.getDate() === day;
        html += `<div class="cal-day${isToday?' today':''}" data-day="${day}">
            <span class="cal-day-num">${day}</span>
            <div class="cal-day-dots">${dayEvents.map(e => `<span class="cal-dot dot-${e.type}" title="${e.shortName} · ${e.time}"></span>`).join('')}</div>
        </div>`;
    }
    grid.innerHTML = html;
    grid.querySelectorAll('.cal-day:not(.empty)').forEach(cell => {
        cell.addEventListener('click', () => {
            grid.querySelectorAll('.cal-tooltip').forEach(t => t.remove());
            const day = parseInt(cell.dataset.day);
            const dayEvents = APRIL_2026.filter(e => e.day === day);
            if (dayEvents.length === 0) return;
            const tooltip = document.createElement('div');
            tooltip.className = 'cal-tooltip';
            tooltip.innerHTML = dayEvents.map(e => `<div>${e.emoji} <strong>${e.shortName}</strong> · ${e.time} · ${e.venue}</div>`).join('');
            cell.appendChild(tooltip);
            setTimeout(() => tooltip.remove(), 3000);
        });
    });
}

function renderVenues() {
    const pinsContainer = document.getElementById('venuePins');
    const listContainer = document.getElementById('venuesList');
    if (!pinsContainer || !listContainer) return;
    pinsContainer.innerHTML = VENUES.map((venue, i) => {
        const showsAtVenue = SHOWS.filter(s => s.venue === venue.id);
        return `<div class="venue-pin" style="left:${venue.mapX}%;top:${venue.mapY}%;">
            <span>${i+1}</span>
            <div class="venue-pin-tooltip"><strong>${venue.name}</strong><br>${showsAtVenue.map(s=>`${s.emoji} ${s.shortName} · ${s.day}`).join('<br>')}</div>
        </div>`;
    }).join('');
    listContainer.innerHTML = VENUES.map((venue, i) => {
        const showsAtVenue = SHOWS.filter(s => s.venue === venue.id);
        return `<div class="venue-card">
            <div class="venue-card-name">${i+1}. ${venue.name}</div>
            <div class="venue-card-addr">📍 ${venue.address}</div>
            <div class="venue-card-shows">${showsAtVenue.map(s=>`${s.emoji} ${s.shortName} — ${s.day} ${s.time}`).join(' · ')}</div>
        </div>`;
    }).join('');
}
