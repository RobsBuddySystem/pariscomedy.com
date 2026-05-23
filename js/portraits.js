/* Paris Comedy — Montmartre-Style SVG Caricature Portraits
   Hand-drawn feel: expressive features, warm shading, personality in every line
   Consistent artist style across all 8 portraits */

const PORTRAITS = {

    /* ═══════════════════════════════════════════════════════
       SEBASTIAN MARX — 🗽 THE PIONEER
       New Yorker, ~47, Jewish-American, curly hair, glasses,
       warm approachable smile, friendly eyes
       ═══════════════════════════════════════════════════════ */
    'seb': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-seb" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#3d2352"/>
                <stop offset="100%" stop-color="#1a0f2e"/>
            </radialGradient>
            <radialGradient id="skin-seb" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#f5d4a8"/>
                <stop offset="60%" stop-color="#e8be8a"/>
                <stop offset="100%" stop-color="#d4a06a"/>
            </radialGradient>
            <radialGradient id="glow-seb" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-seb" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <!-- Frame -->
        <circle cx="100" cy="100" r="97" fill="url(#glow-seb)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-seb)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Neck & Shoulders -->
        <path d="M80,135 L75,155 Q50,165 35,170 L165,170 Q150,165 125,155 L120,135" fill="#2c2c54" filter="url(#shadow-seb)"/>
        <path d="M83,130 L80,142 Q100,150 120,142 L117,130" fill="url(#skin-seb)"/>
        <!-- Collar detail -->
        <path d="M80,142 Q90,148 100,150 Q110,148 120,142 L118,148 Q100,155 82,148 Z" fill="#3a3a6a"/>
        <path d="M96,142 L100,155 L104,142" fill="#2c2c54" stroke="#4a4a7a" stroke-width="0.5"/>
        <!-- Head shape — slightly elongated, warm -->
        <ellipse cx="100" cy="90" rx="42" ry="48" fill="url(#skin-seb)" filter="url(#shadow-seb)"/>
        <!-- Ear left -->
        <ellipse cx="58" cy="92" rx="7" ry="10" fill="#e8be8a" stroke="#d4a06a" stroke-width="0.8"/>
        <ellipse cx="59" cy="92" rx="3" ry="5" fill="#d4a06a"/>
        <!-- Ear right -->
        <ellipse cx="142" cy="92" rx="7" ry="10" fill="#e8be8a" stroke="#d4a06a" stroke-width="0.8"/>
        <ellipse cx="141" cy="92" rx="3" ry="5" fill="#d4a06a"/>
        <!-- Cheek shadow -->
        <ellipse cx="75" cy="100" rx="12" ry="8" fill="#d4a06a" opacity="0.3"/>
        <ellipse cx="125" cy="100" rx="12" ry="8" fill="#d4a06a" opacity="0.3"/>
        <!-- Nose — friendly, slightly rounded -->
        <path d="M98,82 Q96,90 92,100 Q96,103 100,104 Q104,103 108,100 Q104,90 102,82" fill="#daa06d" opacity="0.6"/>
        <path d="M93,100 Q96,104 100,105 Q104,104 107,100" fill="none" stroke="#c4905d" stroke-width="1" stroke-linecap="round"/>
        <!-- Nostrils -->
        <ellipse cx="95" cy="101" rx="2.5" ry="1.5" fill="#c4905d" opacity="0.5"/>
        <ellipse cx="105" cy="101" rx="2.5" ry="1.5" fill="#c4905d" opacity="0.5"/>
        <!-- Mouth — big warm open smile -->
        <path d="M82,112 Q91,122 100,123 Q109,122 118,112" fill="#c0392b" stroke="#a0301f" stroke-width="1"/>
        <path d="M84,112 Q92,115 100,116 Q108,115 116,112" fill="#fff" opacity="0.9"/>
        <path d="M86,116 Q93,120 100,121 Q107,120 114,116" fill="#a0302080"/>
        <!-- Laugh lines -->
        <path d="M78,105 Q80,112 82,118" fill="none" stroke="#c49060" stroke-width="0.8" opacity="0.5"/>
        <path d="M122,105 Q120,112 118,118" fill="none" stroke="#c49060" stroke-width="0.8" opacity="0.5"/>
        <!-- Glasses — round, intellectual -->
        <circle cx="84" cy="82" r="14" fill="none" stroke="#555" stroke-width="2"/>
        <circle cx="116" cy="82" r="14" fill="none" stroke="#555" stroke-width="2"/>
        <path d="M98,82 L102,82" stroke="#555" stroke-width="2"/>
        <path d="M70,80 L58,78" stroke="#555" stroke-width="1.8"/>
        <path d="M130,80 L142,78" stroke="#555" stroke-width="1.8"/>
        <!-- Lens reflection -->
        <ellipse cx="79" cy="78" rx="3" ry="2" fill="#ffffff20" transform="rotate(-20 79 78)"/>
        <ellipse cx="111" cy="78" rx="3" ry="2" fill="#ffffff20" transform="rotate(-20 111 78)"/>
        <!-- Eyes behind glasses — warm, kind -->
        <ellipse cx="84" cy="83" rx="6" ry="5" fill="#fff"/>
        <ellipse cx="116" cy="83" rx="6" ry="5" fill="#fff"/>
        <circle cx="85" cy="83" r="3.5" fill="#5a4020"/>
        <circle cx="117" cy="83" r="3.5" fill="#5a4020"/>
        <circle cx="85" cy="83" r="2" fill="#1a1008"/>
        <circle cx="117" cy="83" r="2" fill="#1a1008"/>
        <circle cx="86.5" cy="81.5" r="1" fill="#fff" opacity="0.8"/>
        <circle cx="118.5" cy="81.5" r="1" fill="#fff" opacity="0.8"/>
        <!-- Eyebrows — expressive, raised slightly -->
        <path d="M72,70 Q78,64 90,66 Q94,67 96,68" fill="none" stroke="#4a3020" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M128,70 Q122,64 110,66 Q106,67 104,68" fill="none" stroke="#4a3020" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Curly/wavy hair — layered texture -->
        <path d="M58,72 Q55,55 65,42 Q75,30 90,28 Q100,26 110,28 Q125,30 135,42 Q145,55 142,72" fill="#5a3d20"/>
        <path d="M60,68 Q58,52 68,40 Q78,30 95,28 Q105,27 115,30 Q128,35 138,48 Q144,58 140,68" fill="#6a4d2a"/>
        <!-- Curl details -->
        <path d="M62,65 Q58,58 64,50 Q68,44 72,42" fill="none" stroke="#7a5d3a" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M68,60 Q65,52 70,46 Q75,40 80,38" fill="none" stroke="#7a5d3a" stroke-width="2" stroke-linecap="round"/>
        <path d="M138,65 Q142,58 136,50 Q132,44 128,42" fill="none" stroke="#7a5d3a" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M132,60 Q135,52 130,46 Q125,40 120,38" fill="none" stroke="#7a5d3a" stroke-width="2" stroke-linecap="round"/>
        <path d="M80,34 Q85,28 95,27 Q100,26 105,27 Q115,28 120,34" fill="none" stroke="#7a5d3a" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M75,38 Q82,30 100,28 Q118,30 125,38" fill="none" stroke="#8a6d4a" stroke-width="1.5" stroke-linecap="round"/>
        <!-- Forehead lines — character -->
        <path d="M80,58 Q90,56 100,57 Q110,56 120,58" fill="none" stroke="#d4a06a" stroke-width="0.6" opacity="0.4"/>
        <path d="M82,62 Q92,60 100,61 Q108,60 118,62" fill="none" stroke="#d4a06a" stroke-width="0.5" opacity="0.3"/>
        <!-- Title -->
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">🗽 THE PIONEER</text>
    </svg>`,

    /* ═══════════════════════════════════════════════════════
       PAUL TAYLOR — 🇬🇧 THE BREAKOUT
       British, born 1986, clean-cut brown hair, strong jaw,
       confident smirk, sharp features, dapper
       ═══════════════════════════════════════════════════════ */
    'paul': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-paul" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#1e3050"/>
                <stop offset="100%" stop-color="#0f1a2e"/>
            </radialGradient>
            <radialGradient id="skin-paul" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#f2d0a8"/>
                <stop offset="60%" stop-color="#e4b88a"/>
                <stop offset="100%" stop-color="#d09a6a"/>
            </radialGradient>
            <radialGradient id="glow-paul" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-paul" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="100" cy="100" r="97" fill="url(#glow-paul)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-paul)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Neck & Shoulders — sharp suit -->
        <path d="M82,136 L76,155 Q52,165 38,170 L162,170 Q148,165 124,155 L118,136" fill="#1a1a2e" filter="url(#shadow-paul)"/>
        <path d="M85,132 L82,144 Q100,150 118,144 L115,132" fill="url(#skin-paul)"/>
        <!-- Suit collar — sharp -->
        <path d="M76,155 L88,144 L100,155 L112,144 L124,155" fill="none" stroke="#2a2a4e" stroke-width="1.5"/>
        <path d="M88,144 L100,155 L112,144" fill="#1a1a2e"/>
        <path d="M96,144 L100,160 L104,144" fill="#fff" opacity="0.15"/>
        <!-- Tie hint -->
        <rect x="97" y="148" width="6" height="12" rx="1" fill="#8b2252"/>
        <!-- Head — angular jaw, strong -->
        <path d="M60,85 Q58,55 75,42 Q90,32 100,30 Q110,32 125,42 Q142,55 140,85 Q138,108 125,120 Q112,130 100,132 Q88,130 75,120 Q62,108 60,85 Z" fill="url(#skin-paul)" filter="url(#shadow-paul)"/>
        <!-- Jaw definition -->
        <path d="M68,105 Q75,118 88,126 Q100,132 112,126 Q125,118 132,105" fill="none" stroke="#c49060" stroke-width="0.8" opacity="0.4"/>
        <!-- Ears -->
        <ellipse cx="60" cy="88" rx="6" ry="10" fill="#e4b88a" stroke="#d09a6a" stroke-width="0.8"/>
        <ellipse cx="140" cy="88" rx="6" ry="10" fill="#e4b88a" stroke="#d09a6a" stroke-width="0.8"/>
        <!-- Cheekbone highlight -->
        <ellipse cx="78" cy="95" rx="8" ry="4" fill="#f5d8b0" opacity="0.3"/>
        <ellipse cx="122" cy="95" rx="8" ry="4" fill="#f5d8b0" opacity="0.3"/>
        <!-- Nose — sharp, angular -->
        <path d="M99,78 Q97,88 94,98 Q97,101 100,102 Q103,101 106,98 Q103,88 101,78" fill="#d4a06d" opacity="0.5"/>
        <path d="M95,98 Q97,102 100,103 Q103,102 105,98" fill="none" stroke="#c4905d" stroke-width="0.8" stroke-linecap="round"/>
        <!-- Eyes — confident, slightly narrowed -->
        <ellipse cx="83" cy="80" rx="8" ry="5.5" fill="#fff"/>
        <ellipse cx="117" cy="80" rx="8" ry="5.5" fill="#fff"/>
        <!-- Upper eyelid — creates the confident look -->
        <path d="M75,78 Q83,75 91,78" fill="url(#skin-paul)" stroke="none"/>
        <path d="M109,78 Q117,75 125,78" fill="url(#skin-paul)" stroke="none"/>
        <circle cx="84" cy="80" r="3.5" fill="#3a6030"/>
        <circle cx="118" cy="80" r="3.5" fill="#3a6030"/>
        <circle cx="84" cy="80" r="2" fill="#1a2010"/>
        <circle cx="118" cy="80" r="2" fill="#1a2010"/>
        <circle cx="85.5" cy="79" r="1" fill="#fff" opacity="0.8"/>
        <circle cx="119.5" cy="79" r="1" fill="#fff" opacity="0.8"/>
        <!-- Eyebrows — strong, defined -->
        <path d="M73,72 Q78,68 86,69 Q90,70 92,71" fill="none" stroke="#4a3520" stroke-width="2.8" stroke-linecap="round"/>
        <path d="M127,72 Q122,68 114,69 Q110,70 108,71" fill="none" stroke="#4a3520" stroke-width="2.8" stroke-linecap="round"/>
        <!-- Mouth — confident smirk, one side up -->
        <path d="M86,112 Q93,116 100,115 Q110,114 116,108" fill="none" stroke="#a0392b" stroke-width="2" stroke-linecap="round"/>
        <path d="M88,112 Q93,114 100,114 Q108,113 114,110" fill="#c0392b" opacity="0.6"/>
        <!-- Dimple -->
        <path d="M117,108 Q119,110 118,112" fill="none" stroke="#c49060" stroke-width="0.6" opacity="0.5"/>
        <!-- Hair — neat, styled, brown -->
        <path d="M60,78 Q58,55 70,42 Q82,32 100,30 Q118,32 130,42 Q142,55 140,78 L138,72 Q136,55 126,44 Q114,35 100,34 Q86,35 74,44 Q64,55 62,72 Z" fill="#4a3018"/>
        <path d="M62,72 Q60,58 70,46 Q80,36 100,34 Q120,36 130,46 Q140,58 138,72" fill="#5a3d22"/>
        <!-- Hair texture — swept to side -->
        <path d="M65,68 Q70,50 85,40 Q95,35 100,34" fill="none" stroke="#6a4d2a" stroke-width="2" stroke-linecap="round"/>
        <path d="M70,64 Q76,48 90,40 Q98,36 105,35" fill="none" stroke="#6a4d2a" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M75,60 Q82,48 95,42 Q105,38 115,38" fill="none" stroke="#6a4d2a" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M135,68 Q132,52 122,42 Q112,36 105,35" fill="none" stroke="#6a4d2a" stroke-width="1.5" stroke-linecap="round"/>
        <!-- Part line -->
        <path d="M80,38 Q85,34 95,33" fill="none" stroke="#3a2010" stroke-width="1" opacity="0.5"/>
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">🇬🇧 THE BREAKOUT</text>
    </svg>`,

    /* ═══════════════════════════════════════════════════════
       SARAH DONNELLY — 👑 THE QUEEN
       American woman, warm expressive eyes, brown hair,
       confident stage presence, big smile
       ═══════════════════════════════════════════════════════ */
    'sarah': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-sarah" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#4a1535"/>
                <stop offset="100%" stop-color="#2e0f1a"/>
            </radialGradient>
            <radialGradient id="skin-sarah" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#f8dcc0"/>
                <stop offset="60%" stop-color="#f0c8a0"/>
                <stop offset="100%" stop-color="#daa878"/>
            </radialGradient>
            <radialGradient id="glow-sarah" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-sarah" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="100" cy="100" r="97" fill="url(#glow-sarah)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-sarah)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Hair flowing behind — establishes the frame -->
        <path d="M48,75 Q45,55 55,40 Q70,22 100,20 Q130,22 145,40 Q155,55 152,75 Q154,95 150,115 Q148,130 140,145 L135,155 Q120,165 110,168 L90,168 Q80,165 65,155 L60,145 Q52,130 50,115 Q46,95 48,75 Z" fill="#5a3018"/>
        <path d="M50,75 Q48,58 58,44 Q72,28 100,25 Q128,28 142,44 Q152,58 150,75 Q152,92 148,110 Q145,125 138,140 L132,150 Q118,160 108,162 L92,162 Q82,160 68,150 L62,140 Q55,125 52,110 Q48,92 50,75 Z" fill="#6a3d22"/>
        <!-- Hair texture flowing -->
        <path d="M55,70 Q52,50 62,38 Q75,25 100,22" fill="none" stroke="#7a4d2a" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M60,80 Q56,55 68,42 Q82,30 100,26" fill="none" stroke="#7a4d2a" stroke-width="2" stroke-linecap="round"/>
        <path d="M145,70 Q148,50 138,38 Q125,25 100,22" fill="none" stroke="#7a4d2a" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M140,80 Q144,55 132,42 Q118,30 100,26" fill="none" stroke="#7a4d2a" stroke-width="2" stroke-linecap="round"/>
        <path d="M50,100 Q48,115 55,135 Q60,145 65,152" fill="none" stroke="#7a4d2a" stroke-width="2" stroke-linecap="round"/>
        <path d="M150,100 Q152,115 145,135 Q140,145 135,152" fill="none" stroke="#7a4d2a" stroke-width="2" stroke-linecap="round"/>
        <!-- Neck & Shoulders -->
        <path d="M84,132 L78,150 Q58,160 42,166 L158,166 Q142,160 122,150 L116,132" fill="#4a1942" filter="url(#shadow-sarah)"/>
        <path d="M86,128 L84,140 Q100,146 116,140 L114,128" fill="url(#skin-sarah)"/>
        <!-- Neckline — elegant V -->
        <path d="M78,150 Q88,146 100,152 Q112,146 122,150" fill="none" stroke="#5a2952" stroke-width="1"/>
        <!-- Head — softer, rounder -->
        <ellipse cx="100" cy="88" rx="40" ry="45" fill="url(#skin-sarah)" filter="url(#shadow-sarah)"/>
        <!-- Ears (partially hidden by hair) -->
        <ellipse cx="62" cy="90" rx="4" ry="8" fill="#f0c8a0"/>
        <ellipse cx="138" cy="90" rx="4" ry="8" fill="#f0c8a0"/>
        <!-- Cheek glow — warmth -->
        <ellipse cx="76" cy="100" rx="10" ry="6" fill="#e8a090" opacity="0.25"/>
        <ellipse cx="124" cy="100" rx="10" ry="6" fill="#e8a090" opacity="0.25"/>
        <!-- Nose — gentle, feminine -->
        <path d="M99,80 Q97,88 95,96 Q97,99 100,100 Q103,99 105,96 Q103,88 101,80" fill="#daa078" opacity="0.4"/>
        <path d="M96,96 Q98,100 100,101 Q102,100 104,96" fill="none" stroke="#c4905d" stroke-width="0.7" stroke-linecap="round"/>
        <!-- Eyes — big, expressive, queen energy -->
        <ellipse cx="82" cy="80" rx="9" ry="7" fill="#fff"/>
        <ellipse cx="118" cy="80" rx="9" ry="7" fill="#fff"/>
        <!-- Eyelashes — thick, defining -->
        <path d="M73,78 Q78,73 82,73 Q86,73 91,78" fill="none" stroke="#2a1510" stroke-width="2" stroke-linecap="round"/>
        <path d="M109,78 Q114,73 118,73 Q122,73 127,78" fill="none" stroke="#2a1510" stroke-width="2" stroke-linecap="round"/>
        <!-- Lower lash hint -->
        <path d="M76,84 Q82,87 88,84" fill="none" stroke="#2a1510" stroke-width="0.5" opacity="0.4"/>
        <path d="M112,84 Q118,87 124,84" fill="none" stroke="#2a1510" stroke-width="0.5" opacity="0.4"/>
        <circle cx="83" cy="80" r="4" fill="#4a7040"/>
        <circle cx="119" cy="80" r="4" fill="#4a7040"/>
        <circle cx="83" cy="80" r="2.2" fill="#1a2a10"/>
        <circle cx="119" cy="80" r="2.2" fill="#1a2a10"/>
        <circle cx="84.5" cy="78.5" r="1.2" fill="#fff" opacity="0.85"/>
        <circle cx="120.5" cy="78.5" r="1.2" fill="#fff" opacity="0.85"/>
        <!-- Eyebrows — arched, expressive -->
        <path d="M72,70 Q78,64 85,66 Q89,67 92,69" fill="none" stroke="#4a3020" stroke-width="2" stroke-linecap="round"/>
        <path d="M128,70 Q122,64 115,66 Q111,67 108,69" fill="none" stroke="#4a3020" stroke-width="2" stroke-linecap="round"/>
        <!-- Mouth — confident, warm, showing teeth -->
        <path d="M82,108 Q90,118 100,119 Q110,118 118,108" fill="#c0392b" stroke="#a0301f" stroke-width="1"/>
        <path d="M84,108 Q90,112 100,113 Q110,112 116,108" fill="#fff" opacity="0.9"/>
        <path d="M86,114 Q93,118 100,118 Q107,118 114,114" fill="#a0302080"/>
        <!-- Lips — fuller, defined -->
        <path d="M88,106 Q94,104 100,105 Q106,104 112,106" fill="#d04838" opacity="0.6"/>
        <!-- Smile lines -->
        <path d="M78,102 Q80,108 82,114" fill="none" stroke="#c49060" stroke-width="0.6" opacity="0.4"/>
        <path d="M122,102 Q120,108 118,114" fill="none" stroke="#c49060" stroke-width="0.6" opacity="0.4"/>
        <!-- Hair over forehead — soft bangs -->
        <path d="M62,68 Q65,50 78,38 Q90,30 100,28 Q110,30 122,38 Q135,50 138,68" fill="#6a3d22"/>
        <path d="M65,65 Q68,48 82,38 Q92,32 100,30 Q108,32 118,38 Q132,48 135,65" fill="#7a4d2a" opacity="0.6"/>
        <path d="M68,62 Q75,45 90,36" fill="none" stroke="#8a5d3a" stroke-width="2" stroke-linecap="round"/>
        <path d="M132,62 Q125,45 110,36" fill="none" stroke="#8a5d3a" stroke-width="2" stroke-linecap="round"/>
        <!-- Earrings hint -->
        <circle cx="62" cy="100" r="2" fill="#ffd700" opacity="0.7"/>
        <circle cx="138" cy="100" r="2" fill="#ffd700" opacity="0.7"/>
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">👑 THE QUEEN</text>
    </svg>`,

    /* ═══════════════════════════════════════════════════════
       ROBERT LE RICAIN — 🍟 THE FOUNDER
       American, curly gray/silver hair, salt-and-pepper beard,
       warm open smile, fit build, the host
       ═══════════════════════════════════════════════════════ */
    'robert': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-rob" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#4a3518"/>
                <stop offset="100%" stop-color="#2e1a0f"/>
            </radialGradient>
            <radialGradient id="skin-rob" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#f5d4a8"/>
                <stop offset="60%" stop-color="#e8be8a"/>
                <stop offset="100%" stop-color="#d4a06a"/>
            </radialGradient>
            <radialGradient id="glow-rob" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-rob" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="100" cy="100" r="97" fill="url(#glow-rob)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-rob)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Neck & Shoulders — casual -->
        <path d="M80,138 L74,156 Q52,165 38,170 L162,170 Q148,165 126,156 L120,138" fill="#2a4a2a" filter="url(#shadow-rob)"/>
        <path d="M83,132 L80,145 Q100,152 120,145 L117,132" fill="url(#skin-rob)"/>
        <!-- T-shirt collar — relaxed -->
        <path d="M80,145 Q90,148 100,149 Q110,148 120,145 Q115,150 100,152 Q85,150 80,145 Z" fill="#224422"/>
        <!-- Head — warm, slightly round -->
        <path d="M60,86 Q58,58 72,44 Q86,32 100,30 Q114,32 128,44 Q142,58 140,86 Q138,108 128,118 Q115,130 100,132 Q85,130 72,118 Q62,108 60,86 Z" fill="url(#skin-rob)" filter="url(#shadow-rob)"/>
        <!-- Ears -->
        <ellipse cx="59" cy="90" rx="7" ry="10" fill="#e8be8a" stroke="#d4a06a" stroke-width="0.8"/>
        <ellipse cx="60" cy="90" rx="3" ry="5" fill="#d4a06a"/>
        <ellipse cx="141" cy="90" rx="7" ry="10" fill="#e8be8a" stroke="#d4a06a" stroke-width="0.8"/>
        <ellipse cx="140" cy="90" rx="3" ry="5" fill="#d4a06a"/>
        <!-- Cheek warmth -->
        <ellipse cx="75" cy="100" rx="10" ry="6" fill="#e8a090" opacity="0.2"/>
        <ellipse cx="125" cy="100" rx="10" ry="6" fill="#e8a090" opacity="0.2"/>
        <!-- Beard — salt and pepper, textured -->
        <path d="M68,104 Q70,120 80,128 Q90,135 100,136 Q110,135 120,128 Q130,120 132,104" fill="#888"/>
        <path d="M70,106 Q72,118 82,126 Q92,132 100,133 Q108,132 118,126 Q128,118 130,106" fill="#999"/>
        <!-- Beard texture — mixed gray/dark strokes -->
        <path d="M74,108 Q76,118 84,125" fill="none" stroke="#777" stroke-width="1" stroke-linecap="round"/>
        <path d="M78,106 Q80,115 86,122" fill="none" stroke="#aaa" stroke-width="0.8" stroke-linecap="round"/>
        <path d="M84,105 Q86,114 90,120" fill="none" stroke="#666" stroke-width="1" stroke-linecap="round"/>
        <path d="M126,108 Q124,118 116,125" fill="none" stroke="#777" stroke-width="1" stroke-linecap="round"/>
        <path d="M122,106 Q120,115 114,122" fill="none" stroke="#aaa" stroke-width="0.8" stroke-linecap="round"/>
        <path d="M116,105 Q114,114 110,120" fill="none" stroke="#666" stroke-width="1" stroke-linecap="round"/>
        <path d="M96,108 Q98,118 100,124" fill="none" stroke="#bbb" stroke-width="0.8" stroke-linecap="round"/>
        <path d="M104,108 Q102,118 100,124" fill="none" stroke="#777" stroke-width="0.8" stroke-linecap="round"/>
        <!-- Mustache -->
        <path d="M86,104 Q93,108 100,106 Q107,108 114,104" fill="#888" stroke="#777" stroke-width="0.5"/>
        <!-- Nose — friendly -->
        <path d="M98,80 Q96,88 93,98 Q96,101 100,102 Q104,101 107,98 Q104,88 102,80" fill="#daa06d" opacity="0.5"/>
        <path d="M94,98 Q97,102 100,103 Q103,102 106,98" fill="none" stroke="#c4905d" stroke-width="0.8" stroke-linecap="round"/>
        <!-- Mouth — big warm open smile visible through beard -->
        <path d="M84,110 Q92,120 100,121 Q108,120 116,110" fill="#c0392b" stroke="#a0301f" stroke-width="0.8"/>
        <path d="M86,110 Q92,114 100,115 Q108,114 114,110" fill="#fff" opacity="0.85"/>
        <!-- Eyes — warm, kind, crinkled from smiling -->
        <ellipse cx="83" cy="80" rx="8" ry="6" fill="#fff"/>
        <ellipse cx="117" cy="80" rx="8" ry="6" fill="#fff"/>
        <circle cx="84" cy="80" r="3.8" fill="#4a6030"/>
        <circle cx="118" cy="80" r="3.8" fill="#4a6030"/>
        <circle cx="84" cy="80" r="2" fill="#1a2010"/>
        <circle cx="118" cy="80" r="2" fill="#1a2010"/>
        <circle cx="85.5" cy="78.5" r="1.1" fill="#fff" opacity="0.8"/>
        <circle cx="119.5" cy="78.5" r="1.1" fill="#fff" opacity="0.8"/>
        <!-- Crow's feet — smile lines at eyes -->
        <path d="M72,77 Q70,75 68,73" fill="none" stroke="#c49060" stroke-width="0.6" opacity="0.5"/>
        <path d="M72,80 Q69,80 67,79" fill="none" stroke="#c49060" stroke-width="0.6" opacity="0.5"/>
        <path d="M128,77 Q130,75 132,73" fill="none" stroke="#c49060" stroke-width="0.6" opacity="0.5"/>
        <path d="M128,80 Q131,80 133,79" fill="none" stroke="#c49060" stroke-width="0.6" opacity="0.5"/>
        <!-- Eyebrows — expressive, slightly raised -->
        <path d="M72,70 Q78,65 86,67 Q90,68 93,70" fill="none" stroke="#888" stroke-width="2.2" stroke-linecap="round"/>
        <path d="M128,70 Q122,65 114,67 Q110,68 107,70" fill="none" stroke="#888" stroke-width="2.2" stroke-linecap="round"/>
        <!-- Curly gray/silver hair — wild, textured -->
        <path d="M56,76 Q52,52 65,38 Q80,25 100,22 Q120,25 135,38 Q148,52 144,76" fill="#999"/>
        <path d="M58,72 Q55,50 68,38 Q82,27 100,25 Q118,27 132,38 Q145,50 142,72" fill="#aaa"/>
        <!-- Curl details — silver -->
        <path d="M60,70 Q56,58 62,48 Q68,40 75,36" fill="none" stroke="#bbb" stroke-width="3" stroke-linecap="round"/>
        <path d="M66,64 Q62,52 68,44 Q74,38 82,34" fill="none" stroke="#ccc" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M140,70 Q144,58 138,48 Q132,40 125,36" fill="none" stroke="#bbb" stroke-width="3" stroke-linecap="round"/>
        <path d="M134,64 Q138,52 132,44 Q126,38 118,34" fill="none" stroke="#ccc" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M78,30 Q88,22 100,22 Q112,22 122,30" fill="none" stroke="#bbb" stroke-width="3" stroke-linecap="round"/>
        <path d="M85,28 Q95,24 100,24 Q105,24 115,28" fill="none" stroke="#ddd" stroke-width="2" stroke-linecap="round"/>
        <!-- More curls for volume -->
        <path d="M58,68 Q55,62 60,56" fill="none" stroke="#ddd" stroke-width="2" stroke-linecap="round"/>
        <path d="M142,68 Q145,62 140,56" fill="none" stroke="#ddd" stroke-width="2" stroke-linecap="round"/>
        <!-- Forehead lines -->
        <path d="M78,56 Q90,53 100,54 Q110,53 122,56" fill="none" stroke="#d4a06a" stroke-width="0.5" opacity="0.4"/>
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">🍟 THE FOUNDER</text>
    </svg>`,

    /* ═══════════════════════════════════════════════════════
       TAMER KATTAN — 🌍 NY TO PARIS
       Middle Eastern heritage, NY-based, dark hair,
       expressive face, big personality, animated
       ═══════════════════════════════════════════════════════ */
    'tamer': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-tam" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#2a4518"/>
                <stop offset="100%" stop-color="#1a2e0f"/>
            </radialGradient>
            <radialGradient id="skin-tam" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#e8c49a"/>
                <stop offset="60%" stop-color="#d4a878"/>
                <stop offset="100%" stop-color="#c09060"/>
            </radialGradient>
            <radialGradient id="glow-tam" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-tam" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="100" cy="100" r="97" fill="url(#glow-tam)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-tam)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Neck & Shoulders — expressive pose, slightly turned -->
        <path d="M78,136 L72,155 Q50,165 36,170 L164,170 Q150,165 128,155 L122,136" fill="#2e2e1a" filter="url(#shadow-tam)"/>
        <path d="M82,130 L78,144 Q100,150 122,144 L118,130" fill="url(#skin-tam)"/>
        <!-- Shirt collar — open, casual NYC -->
        <path d="M78,144 Q88,148 94,150 L100,156 L106,150 Q112,148 122,144" fill="#2e2e1a"/>
        <path d="M88,144 L94,150 L100,156 L106,150 L112,144" fill="none" stroke="#3e3e2a" stroke-width="1"/>
        <!-- Head — animated, slightly tilted -->
        <g transform="rotate(-3 100 88)">
        <path d="M58,86 Q56,56 70,42 Q86,30 100,28 Q114,30 130,42 Q144,56 142,86 Q140,110 128,120 Q114,132 100,134 Q86,132 72,120 Q60,110 58,86 Z" fill="url(#skin-tam)" filter="url(#shadow-tam)"/>
        <!-- Ears -->
        <ellipse cx="58" cy="88" rx="7" ry="11" fill="#d4a878" stroke="#c09060" stroke-width="0.8"/>
        <ellipse cx="59" cy="88" rx="3" ry="5.5" fill="#c09060"/>
        <ellipse cx="142" cy="88" rx="7" ry="11" fill="#d4a878" stroke="#c09060" stroke-width="0.8"/>
        <ellipse cx="141" cy="88" rx="3" ry="5.5" fill="#c09060"/>
        <!-- Five o'clock shadow -->
        <path d="M70,104 Q72,120 82,128 Q92,134 100,135 Q108,134 118,128 Q128,120 130,104" fill="#c09060" opacity="0.2"/>
        <!-- Nose — prominent, character -->
        <path d="M98,78 Q95,88 91,98 Q94,102 100,104 Q106,102 109,98 Q105,88 102,78" fill="#c49068" opacity="0.5"/>
        <path d="M92,98 Q96,103 100,105 Q104,103 108,98" fill="none" stroke="#b08058" stroke-width="1" stroke-linecap="round"/>
        <ellipse cx="95" cy="100" rx="2.5" ry="1.5" fill="#b08058" opacity="0.4"/>
        <ellipse cx="105" cy="100" rx="2.5" ry="1.5" fill="#b08058" opacity="0.4"/>
        <!-- Eyes — BIG, expressive, animated -->
        <ellipse cx="82" cy="80" rx="10" ry="7" fill="#fff"/>
        <ellipse cx="118" cy="80" rx="10" ry="7" fill="#fff"/>
        <circle cx="83" cy="80" r="4.5" fill="#3a2810"/>
        <circle cx="119" cy="80" r="4.5" fill="#3a2810"/>
        <circle cx="83" cy="80" r="2.5" fill="#1a1008"/>
        <circle cx="119" cy="80" r="2.5" fill="#1a1008"/>
        <circle cx="85" cy="78" r="1.3" fill="#fff" opacity="0.85"/>
        <circle cx="121" cy="78" r="1.3" fill="#fff" opacity="0.85"/>
        <!-- Lower eyelid — adds warmth -->
        <path d="M74,84 Q82,88 90,84" fill="none" stroke="#c09060" stroke-width="0.6" opacity="0.4"/>
        <path d="M110,84 Q118,88 126,84" fill="none" stroke="#c09060" stroke-width="0.6" opacity="0.4"/>
        <!-- Eyebrows — thick, very expressive, one raised -->
        <path d="M70,68 Q76,62 84,64 Q89,66 92,68" fill="none" stroke="#1a1008" stroke-width="3.2" stroke-linecap="round"/>
        <path d="M130,72 Q124,66 116,68 Q111,69 108,71" fill="none" stroke="#1a1008" stroke-width="3" stroke-linecap="round"/>
        <!-- Mouth — big animated grin, mid-joke -->
        <path d="M80,110 Q90,124 100,125 Q110,124 120,110" fill="#c0392b" stroke="#a0301f" stroke-width="1"/>
        <path d="M82,110 Q90,116 100,117 Q110,116 118,110" fill="#fff" opacity="0.9"/>
        <path d="M84,117 Q92,122 100,123 Q108,122 116,117" fill="#a03020" opacity="0.5"/>
        <!-- Tongue hint — mid-laugh -->
        <ellipse cx="100" cy="120" rx="6" ry="3" fill="#d05040" opacity="0.5"/>
        <!-- Laugh lines — deep -->
        <path d="M74,100 Q76,108 80,116" fill="none" stroke="#b08058" stroke-width="0.8" opacity="0.5"/>
        <path d="M126,100 Q124,108 120,116" fill="none" stroke="#b08058" stroke-width="0.8" opacity="0.5"/>
        <!-- Hair — thick, dark, full -->
        <path d="M56,78 Q52,50 68,36 Q84,24 100,22 Q116,24 132,36 Q148,50 144,78" fill="#1a1008"/>
        <path d="M58,74 Q55,48 70,36 Q86,26 100,24 Q114,26 130,36 Q145,48 142,74" fill="#2a1a10"/>
        <!-- Hair texture -->
        <path d="M62,68 Q58,50 72,38 Q85,28 100,26" fill="none" stroke="#3a2818" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M68,62 Q65,48 78,38 Q90,30 100,28" fill="none" stroke="#3a2818" stroke-width="2" stroke-linecap="round"/>
        <path d="M138,68 Q142,50 128,38 Q115,28 100,26" fill="none" stroke="#3a2818" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M132,62 Q135,48 122,38 Q110,30 100,28" fill="none" stroke="#3a2818" stroke-width="2" stroke-linecap="round"/>
        <path d="M80,28 Q90,22 100,22 Q110,22 120,28" fill="none" stroke="#3a2818" stroke-width="2.5" stroke-linecap="round"/>
        </g>
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">🌍 NY TO PARIS</text>
    </svg>`,

    /* ═══════════════════════════════════════════════════════
       GAD ELMALEH — 🌉 THE BRIDGE
       Moroccan-French, slim face, distinctive nose,
       warm eyes, elegant, France's biggest comic
       ═══════════════════════════════════════════════════════ */
    'gad': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-gad" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#1e4040"/>
                <stop offset="100%" stop-color="#0f2e2e"/>
            </radialGradient>
            <radialGradient id="skin-gad" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#e8c49a"/>
                <stop offset="60%" stop-color="#d4a878"/>
                <stop offset="100%" stop-color="#c09060"/>
            </radialGradient>
            <radialGradient id="glow-gad" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-gad" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="100" cy="100" r="97" fill="url(#glow-gad)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-gad)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Neck & Shoulders — elegant, slim -->
        <path d="M84,140 L80,156 Q60,165 45,170 L155,170 Q140,165 120,156 L116,140" fill="#1a1a2e" filter="url(#shadow-gad)"/>
        <path d="M86,134 L84,146 Q100,152 116,146 L114,134" fill="url(#skin-gad)"/>
        <!-- Elegant jacket collar -->
        <path d="M80,156 L90,146 L100,152 L110,146 L120,156" fill="#1a1a2e" stroke="#2a2a3e" stroke-width="0.8"/>
        <path d="M90,146 L100,152 L110,146" fill="#111128"/>
        <!-- Pocket square hint -->
        <path d="M120,156 L122,152 L125,156" fill="#8b4060" opacity="0.6"/>
        <!-- Head — slim, elongated, elegant -->
        <path d="M64,84 Q62,55 74,42 Q86,30 100,28 Q114,30 126,42 Q138,55 136,84 Q134,112 124,124 Q112,136 100,138 Q88,136 76,124 Q66,112 64,84 Z" fill="url(#skin-gad)" filter="url(#shadow-gad)"/>
        <!-- Slim jaw definition -->
        <path d="M72,110 Q78,122 88,130 Q100,138 112,130 Q122,122 128,110" fill="none" stroke="#b08058" stroke-width="0.6" opacity="0.3"/>
        <!-- Ears -->
        <ellipse cx="63" cy="88" rx="6" ry="10" fill="#d4a878" stroke="#c09060" stroke-width="0.7"/>
        <ellipse cx="137" cy="88" rx="6" ry="10" fill="#d4a878" stroke="#c09060" stroke-width="0.7"/>
        <!-- Cheekbone shadow — high, defined -->
        <path d="M70,92 Q76,96 80,100" fill="none" stroke="#b08058" stroke-width="0.8" opacity="0.3"/>
        <path d="M130,92 Q124,96 120,100" fill="none" stroke="#b08058" stroke-width="0.8" opacity="0.3"/>
        <!-- Nose — distinctive, longer, elegant -->
        <path d="M98,76 Q95,86 92,96 Q90,100 88,102 Q92,106 100,108 Q108,106 112,102 Q110,100 108,96 Q105,86 102,76" fill="#c49068" opacity="0.45"/>
        <path d="M90,102 Q94,107 100,108 Q106,107 110,102" fill="none" stroke="#b08058" stroke-width="1" stroke-linecap="round"/>
        <!-- Nose bridge highlight -->
        <path d="M99,78 L99,94" fill="none" stroke="#e0c0a0" stroke-width="0.8" opacity="0.3"/>
        <!-- Eyes — warm, deep-set, knowing -->
        <ellipse cx="83" cy="80" rx="8" ry="5.5" fill="#fff"/>
        <ellipse cx="117" cy="80" rx="8" ry="5.5" fill="#fff"/>
        <!-- Deeper eye socket -->
        <path d="M75,78 Q83,74 91,78" fill="#c09060" opacity="0.2"/>
        <path d="M109,78 Q117,74 125,78" fill="#c09060" opacity="0.2"/>
        <circle cx="84" cy="80" r="3.5" fill="#3a2810"/>
        <circle cx="118" cy="80" r="3.5" fill="#3a2810"/>
        <circle cx="84" cy="80" r="2" fill="#1a1008"/>
        <circle cx="118" cy="80" r="2" fill="#1a1008"/>
        <circle cx="85.5" cy="78.5" r="1" fill="#fff" opacity="0.8"/>
        <circle cx="119.5" cy="78.5" r="1" fill="#fff" opacity="0.8"/>
        <!-- Eyebrows — distinctive, expressive -->
        <path d="M73,72 Q78,66 85,68 Q89,69 92,71" fill="none" stroke="#2a1a10" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M127,72 Q122,66 115,68 Q111,69 108,71" fill="none" stroke="#2a1a10" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Mouth — subtle warm smile, knowing -->
        <path d="M86,114 Q93,120 100,121 Q107,120 114,114" fill="#b83425" stroke="#982818" stroke-width="0.8"/>
        <path d="M88,114 Q93,117 100,118 Q107,117 112,114" fill="#fff" opacity="0.7"/>
        <!-- Under-lip shadow -->
        <path d="M90,122 Q100,126 110,122" fill="#b08058" opacity="0.2"/>
        <!-- Smile creases -->
        <path d="M80,106 Q82,112 86,118" fill="none" stroke="#b08058" stroke-width="0.6" opacity="0.4"/>
        <path d="M120,106 Q118,112 114,118" fill="none" stroke="#b08058" stroke-width="0.6" opacity="0.4"/>
        <!-- Hair — neat dark, slightly receding, distinguished -->
        <path d="M64,78 Q62,52 74,40 Q86,30 100,28 Q114,30 126,40 Q138,52 136,78 L134,70 Q132,52 124,42 Q112,33 100,32 Q88,33 76,42 Q68,52 66,70 Z" fill="#1a1008"/>
        <path d="M66,70 Q65,50 76,40 Q88,32 100,30 Q112,32 124,40 Q135,50 134,70" fill="#2a1a10"/>
        <!-- Hair texture -->
        <path d="M70,65 Q72,48 84,38 Q95,32 100,30" fill="none" stroke="#3a2818" stroke-width="2" stroke-linecap="round"/>
        <path d="M76,60 Q80,46 90,38 Q98,34 105,32" fill="none" stroke="#3a2818" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M130,65 Q128,48 116,38 Q105,32 100,30" fill="none" stroke="#3a2818" stroke-width="2" stroke-linecap="round"/>
        <!-- Gray at temples — distinguished -->
        <path d="M66,72 Q65,65 68,58" fill="none" stroke="#888" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M134,72 Q135,65 132,58" fill="none" stroke="#888" stroke-width="1.5" stroke-linecap="round"/>
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">🌉 THE BRIDGE</text>
    </svg>`,

    /* ═══════════════════════════════════════════════════════
       NOMAN HOSNI — 🇫🇷 FRENCH STAR
       French, North African heritage, charismatic,
       big smile, energetic, commanding presence
       ═══════════════════════════════════════════════════════ */
    'noman': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-nom" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#402050"/>
                <stop offset="100%" stop-color="#2e0f2e"/>
            </radialGradient>
            <radialGradient id="skin-nom" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#deb88a"/>
                <stop offset="60%" stop-color="#c8a070"/>
                <stop offset="100%" stop-color="#b08858"/>
            </radialGradient>
            <radialGradient id="glow-nom" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-nom" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="100" cy="100" r="97" fill="url(#glow-nom)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-nom)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Neck & Shoulders — broad, energetic -->
        <path d="M78,134 L70,154 Q48,164 34,170 L166,170 Q152,164 130,154 L122,134" fill="#2e1a2e" filter="url(#shadow-nom)"/>
        <path d="M82,128 L78,142 Q100,148 122,142 L118,128" fill="url(#skin-nom)"/>
        <!-- Casual collar -->
        <path d="M78,142 Q88,146 100,148 Q112,146 122,142 Q118,148 100,150 Q82,148 78,142 Z" fill="#3e2a3e"/>
        <!-- Head — round, charismatic -->
        <path d="M58,86 Q56,56 70,42 Q86,28 100,26 Q114,28 130,42 Q144,56 142,86 Q140,112 128,122 Q114,134 100,136 Q86,134 72,122 Q60,112 58,86 Z" fill="url(#skin-nom)" filter="url(#shadow-nom)"/>
        <!-- Ears -->
        <ellipse cx="58" cy="88" rx="7" ry="10" fill="#c8a070" stroke="#b08858" stroke-width="0.8"/>
        <ellipse cx="59" cy="88" rx="3" ry="5" fill="#b08858"/>
        <ellipse cx="142" cy="88" rx="7" ry="10" fill="#c8a070" stroke="#b08858" stroke-width="0.8"/>
        <ellipse cx="141" cy="88" rx="3" ry="5" fill="#b08858"/>
        <!-- Stubble hint -->
        <path d="M70,106 Q72,120 82,128 Q92,134 100,136 Q108,134 118,128 Q128,120 130,106" fill="#b08858" opacity="0.15"/>
        <!-- Cheek warmth -->
        <ellipse cx="76" cy="100" rx="10" ry="6" fill="#c08060" opacity="0.2"/>
        <ellipse cx="124" cy="100" rx="10" ry="6" fill="#c08060" opacity="0.2"/>
        <!-- Nose -->
        <path d="M98,80 Q95,88 92,98 Q95,102 100,104 Q105,102 108,98 Q105,88 102,80" fill="#b8906a" opacity="0.5"/>
        <path d="M93,98 Q96,103 100,105 Q104,103 107,98" fill="none" stroke="#a8805a" stroke-width="0.9" stroke-linecap="round"/>
        <!-- Eyes — bright, energetic, wide -->
        <ellipse cx="82" cy="80" rx="9" ry="7" fill="#fff"/>
        <ellipse cx="118" cy="80" rx="9" ry="7" fill="#fff"/>
        <circle cx="83" cy="80" r="4.2" fill="#3a2810"/>
        <circle cx="119" cy="80" r="4.2" fill="#3a2810"/>
        <circle cx="83" cy="80" r="2.3" fill="#1a1008"/>
        <circle cx="119" cy="80" r="2.3" fill="#1a1008"/>
        <circle cx="85" cy="78" r="1.2" fill="#fff" opacity="0.85"/>
        <circle cx="121" cy="78" r="1.2" fill="#fff" opacity="0.85"/>
        <!-- Eyebrows — thick, animated -->
        <path d="M70,68 Q76,62 85,64 Q90,66 93,68" fill="none" stroke="#1a1008" stroke-width="3" stroke-linecap="round"/>
        <path d="M130,68 Q124,62 115,64 Q110,66 107,68" fill="none" stroke="#1a1008" stroke-width="3" stroke-linecap="round"/>
        <!-- Mouth — HUGE charismatic grin -->
        <path d="M76,108 Q88,126 100,127 Q112,126 124,108" fill="#c0392b" stroke="#a0301f" stroke-width="1.2"/>
        <path d="M78,108 Q88,116 100,117 Q112,116 122,108" fill="#fff" opacity="0.9"/>
        <path d="M80,117 Q90,124 100,125 Q110,124 120,117" fill="#a03020" opacity="0.5"/>
        <!-- Teeth detail -->
        <line x1="92" y1="108" x2="92" y2="116" stroke="#e8e8e8" stroke-width="0.4"/>
        <line x1="100" y1="108" x2="100" y2="117" stroke="#e8e8e8" stroke-width="0.4"/>
        <line x1="108" y1="108" x2="108" y2="116" stroke="#e8e8e8" stroke-width="0.4"/>
        <!-- Deep laugh lines -->
        <path d="M72,98 Q74,108 76,116" fill="none" stroke="#a8805a" stroke-width="1" opacity="0.5"/>
        <path d="M128,98 Q126,108 124,116" fill="none" stroke="#a8805a" stroke-width="1" opacity="0.5"/>
        <!-- Hair — short, dark, neat -->
        <path d="M58,80 Q55,52 70,38 Q86,25 100,23 Q114,25 130,38 Q145,52 142,80 L140,72 Q138,52 126,40 Q114,30 100,28 Q86,30 74,40 Q62,52 60,72 Z" fill="#1a0e08"/>
        <path d="M60,72 Q58,50 72,38 Q86,28 100,26 Q114,28 128,38 Q142,50 140,72" fill="#2a1810"/>
        <!-- Hair texture — short cropped -->
        <path d="M65,66 Q68,48 80,38 Q92,30 100,28" fill="none" stroke="#3a2818" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M135,66 Q132,48 120,38 Q108,30 100,28" fill="none" stroke="#3a2818" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M75,55 Q82,42 95,34 Q100,32 105,34 Q118,42 125,55" fill="none" stroke="#3a2818" stroke-width="2" stroke-linecap="round"/>
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">🇫🇷 FRENCH STAR</text>
    </svg>`,

    /* ═══════════════════════════════════════════════════════
       TANIA DUTEL — ✨ RISING STAR
       French woman, young, brown hair, bright eyes,
       sharp wit visible in expression, contemporary
       ═══════════════════════════════════════════════════════ */
    'tania': `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bg-tan" cx="50%" cy="45%" r="55%">
                <stop offset="0%" stop-color="#451540"/>
                <stop offset="100%" stop-color="#2e0f28"/>
            </radialGradient>
            <radialGradient id="skin-tan" cx="45%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#fae0c8"/>
                <stop offset="60%" stop-color="#f0ccaa"/>
                <stop offset="100%" stop-color="#dab48a"/>
            </radialGradient>
            <radialGradient id="glow-tan" cx="50%" cy="50%" r="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="100%" stop-color="#ff336640"/>
            </radialGradient>
            <filter id="shadow-tan" x="-10%" y="-10%" width="120%" height="130%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dy="3" result="shadow"/>
                <feFlood flood-color="#00000040"/>
                <feComposite in2="shadow" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <circle cx="100" cy="100" r="97" fill="url(#glow-tan)"/>
        <circle cx="100" cy="100" r="95" fill="url(#bg-tan)" stroke="#ff3366" stroke-width="2.5"/>
        <!-- Hair behind — long, flowing brown -->
        <path d="M46,78 Q42,52 55,36 Q72,18 100,16 Q128,18 145,36 Q158,52 154,78 Q156,100 152,125 Q148,145 140,158 L132,166 Q115,172 108,172 L92,172 Q85,172 68,166 L60,158 Q52,145 48,125 Q44,100 46,78 Z" fill="#4a2a14"/>
        <path d="M48,78 Q45,55 58,40 Q74,22 100,20 Q126,22 142,40 Q155,55 152,78 Q154,98 150,120 Q146,140 138,154 L130,162 Q114,168 106,168 L94,168 Q86,168 70,162 L62,154 Q54,140 50,120 Q46,98 48,78 Z" fill="#5a3820"/>
        <!-- Hair texture flowing -->
        <path d="M52,72 Q50,50 62,36 Q78,22 100,18" fill="none" stroke="#6a4828" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M56,82 Q52,55 66,40 Q82,26 100,22" fill="none" stroke="#6a4828" stroke-width="2" stroke-linecap="round"/>
        <path d="M148,72 Q150,50 138,36 Q122,22 100,18" fill="none" stroke="#6a4828" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M144,82 Q148,55 134,40 Q118,26 100,22" fill="none" stroke="#6a4828" stroke-width="2" stroke-linecap="round"/>
        <path d="M48,110 Q46,130 55,148 Q60,155 65,160" fill="none" stroke="#6a4828" stroke-width="2" stroke-linecap="round"/>
        <path d="M152,110 Q154,130 145,148 Q140,155 135,160" fill="none" stroke="#6a4828" stroke-width="2" stroke-linecap="round"/>
        <path d="M50,95 Q48,115 52,135" fill="none" stroke="#7a5838" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M150,95 Q152,115 148,135" fill="none" stroke="#7a5838" stroke-width="1.5" stroke-linecap="round"/>
        <!-- Neck & Shoulders -->
        <path d="M84,134 L78,152 Q60,162 44,168 L156,168 Q140,162 122,152 L116,134" fill="#3a1838" filter="url(#shadow-tan)"/>
        <path d="M86,128 L84,142 Q100,148 116,142 L114,128" fill="url(#skin-tan)"/>
        <!-- Top neckline — contemporary -->
        <path d="M78,152 Q88,148 100,150 Q112,148 122,152 Q116,156 100,158 Q84,156 78,152 Z" fill="#4a2848"/>
        <!-- Head — youthful, slightly round -->
        <ellipse cx="100" cy="88" rx="38" ry="44" fill="url(#skin-tan)" filter="url(#shadow-tan)"/>
        <!-- Ears (partially covered) -->
        <ellipse cx="64" cy="90" rx="4" ry="8" fill="#f0ccaa"/>
        <ellipse cx="136" cy="90" rx="4" ry="8" fill="#f0ccaa"/>
        <!-- Cheek glow -->
        <ellipse cx="78" cy="98" rx="8" ry="5" fill="#e8a090" opacity="0.25"/>
        <ellipse cx="122" cy="98" rx="8" ry="5" fill="#e8a090" opacity="0.25"/>
        <!-- Nose — small, cute -->
        <path d="M99,80 Q97,86 95,94 Q97,97 100,98 Q103,97 105,94 Q103,86 101,80" fill="#daa078" opacity="0.35"/>
        <path d="M96,94 Q98,98 100,99 Q102,98 104,94" fill="none" stroke="#c4905d" stroke-width="0.7" stroke-linecap="round"/>
        <!-- Eyes — bright, sharp, alert -->
        <ellipse cx="83" cy="80" rx="9" ry="6.5" fill="#fff"/>
        <ellipse cx="117" cy="80" rx="9" ry="6.5" fill="#fff"/>
        <!-- Upper eyelid — subtle cat-eye -->
        <path d="M74,78 Q83,74 92,78" fill="none" stroke="#2a1510" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M108,78 Q117,74 126,78" fill="none" stroke="#2a1510" stroke-width="1.8" stroke-linecap="round"/>
        <!-- Lower lash -->
        <path d="M76,84 Q83,87 90,84" fill="none" stroke="#2a1510" stroke-width="0.4" opacity="0.4"/>
        <path d="M110,84 Q117,87 124,84" fill="none" stroke="#2a1510" stroke-width="0.4" opacity="0.4"/>
        <circle cx="84" cy="80" r="4" fill="#4a6848"/>
        <circle cx="118" cy="80" r="4" fill="#4a6848"/>
        <circle cx="84" cy="80" r="2.2" fill="#1a2818"/>
        <circle cx="118" cy="80" r="2.2" fill="#1a2818"/>
        <circle cx="85.5" cy="78.5" r="1.2" fill="#fff" opacity="0.85"/>
        <circle cx="119.5" cy="78.5" r="1.2" fill="#fff" opacity="0.85"/>
        <!-- Eyebrows — defined, slightly arched, sharp -->
        <path d="M74,72 Q79,67 85,68 Q89,69 92,71" fill="none" stroke="#3a2818" stroke-width="2" stroke-linecap="round"/>
        <path d="M126,72 Q121,67 115,68 Q111,69 108,71" fill="none" stroke="#3a2818" stroke-width="2" stroke-linecap="round"/>
        <!-- Mouth — knowing half-smile, sharp wit -->
        <path d="M86,108 Q93,114 100,114 Q108,112 115,106" fill="#c04838" stroke="#a03828" stroke-width="0.8"/>
        <path d="M88,108 Q93,111 100,111 Q106,110 112,107" fill="#d8584a" opacity="0.5"/>
        <!-- Upper lip definition -->
        <path d="M90,106 Q95,104 100,105 Q105,104 110,106" fill="#c04838" opacity="0.4"/>
        <!-- Dimple — one side, adds character -->
        <path d="M116,106 Q118,108 117,110" fill="none" stroke="#c49060" stroke-width="0.5" opacity="0.5"/>
        <!-- Hair over forehead — side-swept bangs -->
        <path d="M60,72 Q58,48 72,34 Q86,22 100,20 Q114,22 128,34 Q142,48 140,72" fill="#5a3820"/>
        <path d="M62,68 Q60,46 74,34 Q88,24 100,22 Q112,24 126,34 Q140,46 138,68" fill="#6a4828"/>
        <!-- Side-swept bang detail -->
        <path d="M65,66 Q62,45 76,34 Q90,24 100,22" fill="none" stroke="#7a5838" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M70,62 Q68,44 80,34 Q92,26 102,24" fill="none" stroke="#7a5838" stroke-width="2" stroke-linecap="round"/>
        <path d="M136,66 Q138,45 124,34 Q110,24 100,22" fill="none" stroke="#7a5838" stroke-width="2" stroke-linecap="round"/>
        <!-- Swept fringe -->
        <path d="M75,58 Q80,42 95,32 Q100,30 108,32" fill="none" stroke="#8a6840" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M80,54 Q86,42 98,34 Q105,32 112,34" fill="none" stroke="#8a6840" stroke-width="1.5" stroke-linecap="round"/>
        <!-- Earring hint -->
        <circle cx="136" cy="98" r="1.5" fill="#ffd700" opacity="0.5"/>
        <text x="100" y="186" text-anchor="middle" fill="#ff3366" font-family="'Space Grotesk',sans-serif" font-size="11" font-weight="700">✨ RISING STAR</text>
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
