/* Paris Comedy — SVG Caricature Portraits
   Consistent style: circular frame, gradient bg, stylized features
   Each comic gets a unique but cohesive portrait */

const PORTRAITS = {
    'seb': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-seb" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#1a0f2e"/><stop offset="100%" style="stop-color:#2d1b69"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-seb)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#f4d0a0"/>
        <rect x="75" y="120" width="50" height="45" rx="10" fill="#2c2c54"/>
        <circle cx="87" cy="78" r="5" fill="#333"/><circle cx="113" cy="78" r="5" fill="#333"/>
        <path d="M90,95 Q100,105 110,95" fill="none" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M65,68 Q100,50 135,68" fill="none" stroke="#4a3728" stroke-width="8" stroke-linecap="round"/>
        <rect x="78" y="70" width="44" height="16" rx="8" fill="none" stroke="#666" stroke-width="1.5"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">🗽 THE PIONEER</text>
    </svg>`,

    'paul': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-paul" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#0f1a2e"/><stop offset="100%" style="stop-color:#1b3d69"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-paul)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#f0c8a0"/>
        <rect x="72" y="120" width="56" height="45" rx="10" fill="#1a1a2e"/>
        <circle cx="88" cy="78" r="4.5" fill="#333"/><circle cx="112" cy="78" r="4.5" fill="#333"/>
        <path d="M88,96 Q100,108 112,96" fill="none" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M68,60 Q100,48 132,60" fill="#8b6914" stroke="none"/>
        <path d="M65,65 Q100,55 135,65" fill="#a07818" stroke="none"/>
        <rect x="70" y="76" width="20" height="5" rx="2" fill="#333" transform="rotate(-5 80 78)"/>
        <rect x="110" y="76" width="20" height="5" rx="2" fill="#333" transform="rotate(5 120 78)"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">🇬🇧 THE BREAKOUT</text>
    </svg>`,

    'sarah': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-sarah" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#2e0f1a"/><stop offset="100%" style="stop-color:#691b3d"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-sarah)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#f4d0b0"/>
        <rect x="72" y="120" width="56" height="45" rx="10" fill="#4a1942"/>
        <circle cx="88" cy="78" r="4.5" fill="#333"/><circle cx="112" cy="78" r="4.5" fill="#333"/>
        <path d="M87,96 Q100,106 113,96" fill="none" stroke="#c44" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M55,70 Q65,45 85,55 Q100,40 115,55 Q135,45 145,70" fill="#8b4513" stroke="none"/>
        <path d="M55,70 Q60,80 70,85" fill="#8b4513" stroke="none"/>
        <path d="M145,70 Q140,80 130,85" fill="#8b4513" stroke="none"/>
        <circle cx="88" cy="78" r="6" fill="none" stroke="#333" stroke-width="1"/>
        <circle cx="112" cy="78" r="6" fill="none" stroke="#333" stroke-width="1"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">👑 THE QUEEN</text>
    </svg>`,

    'robert': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-rob" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#2e1a0f"/><stop offset="100%" style="stop-color:#694a1b"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-rob)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#f0c8a0"/>
        <rect x="72" y="120" width="56" height="45" rx="10" fill="#1a2e1a"/>
        <circle cx="88" cy="78" r="5" fill="#333"/><circle cx="112" cy="78" r="5" fill="#333"/>
        <path d="M85,96 Q100,110 115,96" fill="none" stroke="#333" stroke-width="3" stroke-linecap="round"/>
        <path d="M60,58 Q80,45 100,50 Q120,45 140,58" fill="#999" stroke="none"/>
        <path d="M60,62 Q80,50 100,54 Q120,50 140,62" fill="#aaa" stroke="none"/>
        <path d="M80,98 Q100,106 120,98" fill="#999" stroke="none" opacity="0.5"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">🍟 THE FOUNDER</text>
    </svg>`,

    'tamer': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-tam" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#1a2e0f"/><stop offset="100%" style="stop-color:#3d691b"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-tam)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#d4a870"/>
        <rect x="72" y="120" width="56" height="45" rx="10" fill="#2e2e1a"/>
        <circle cx="88" cy="78" r="5" fill="#222"/><circle cx="112" cy="78" r="5" fill="#222"/>
        <path d="M88,96 Q100,107 112,96" fill="none" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M65,55 Q100,42 135,55" fill="#1a1a1a" stroke="none"/>
        <path d="M65,60 Q100,48 135,60" fill="#222" stroke="none"/>
        <path d="M82,100 Q100,112 118,100" fill="#333" stroke="none" opacity="0.4"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">🌍 NY TO PARIS</text>
    </svg>`,

    'gad': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-gad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#0f2e2e"/><stop offset="100%" style="stop-color:#1b6960"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-gad)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#d4a870"/>
        <rect x="72" y="120" width="56" height="45" rx="10" fill="#1a1a2e"/>
        <circle cx="88" cy="78" r="4.5" fill="#222"/><circle cx="112" cy="78" r="4.5" fill="#222"/>
        <path d="M90,95 Q100,104 110,95" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round"/>
        <path d="M68,55 Q100,40 132,55" fill="#1a1a1a" stroke="none"/>
        <path d="M68,60 Q100,46 132,60" fill="#2a2a2a" stroke="none"/>
        <path d="M75,74 Q82,70 88,74" fill="none" stroke="#333" stroke-width="1.5"/>
        <path d="M112,74 Q118,70 125,74" fill="none" stroke="#333" stroke-width="1.5"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">🌉 THE BRIDGE</text>
    </svg>`,

    'noman': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-nom" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#2e0f2e"/><stop offset="100%" style="stop-color:#5b1b69"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-nom)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#d4a870"/>
        <rect x="72" y="120" width="56" height="45" rx="10" fill="#2e1a2e"/>
        <circle cx="88" cy="78" r="5" fill="#222"/><circle cx="112" cy="78" r="5" fill="#222"/>
        <path d="M86,96 Q100,108 114,96" fill="none" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M65,55 Q100,38 135,55" fill="#111" stroke="none"/>
        <path d="M65,62 Q100,48 135,62" fill="#1a1a1a" stroke="none"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">🇫🇷 FRENCH STAR</text>
    </svg>`,

    'tania': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="bg-tan" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#2e1a2e"/><stop offset="100%" style="stop-color:#691b55"/></linearGradient></defs>
        <circle cx="100" cy="100" r="96" fill="url(#bg-tan)" stroke="#ff3366" stroke-width="3"/>
        <circle cx="100" cy="85" r="40" fill="#f4d0b0"/>
        <rect x="72" y="120" width="56" height="45" rx="10" fill="#2e1a42"/>
        <circle cx="88" cy="78" r="4" fill="#333"/><circle cx="112" cy="78" r="4" fill="#333"/>
        <path d="M88,95 Q100,104 112,95" fill="none" stroke="#c44" stroke-width="2" stroke-linecap="round"/>
        <path d="M55,65 Q70,40 90,50 Q100,38 110,50 Q130,40 145,65" fill="#4a2a14" stroke="none"/>
        <path d="M55,65 Q58,78 65,85" fill="#4a2a14" stroke="none"/>
        <path d="M145,65 Q142,78 135,85" fill="#4a2a14" stroke="none"/>
        <text x="100" y="185" text-anchor="middle" fill="#ff3366" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700">✨ RISING STAR</text>
    </svg>`
};

/* Render portraits into player cards */
function renderPortraits() {
    document.querySelectorAll('.player-card').forEach(card => {
        const avatar = card.querySelector('.player-avatar');
        const name = card.querySelector('.player-name')?.textContent?.toLowerCase() || '';
        let portraitKey = null;

        if (name.includes('sebastian') || name.includes('seb')) portraitKey = 'seb';
        else if (name.includes('paul')) portraitKey = 'paul';
        else if (name.includes('sarah')) portraitKey = 'sarah';
        else if (name.includes('robert')) portraitKey = 'robert';
        else if (name.includes('tamer')) portraitKey = 'tamer';
        else if (name.includes('gad')) portraitKey = 'gad';
        else if (name.includes('noman')) portraitKey = 'noman';
        else if (name.includes('tania')) portraitKey = 'tania';

        if (portraitKey && PORTRAITS[portraitKey] && avatar) {
            avatar.innerHTML = PORTRAITS[portraitKey];
            avatar.style.fontSize = '1rem';
            avatar.style.width = '120px';
            avatar.style.height = '120px';
            avatar.style.margin = '0 auto 16px';
        }
    });
}
