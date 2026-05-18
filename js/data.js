/* Paris Comedy — Data Layer */
/* All show data in one place — easy to update */

const UTM = '?utm_source=pariscomedy&utm_medium=website';

const VENUES = [
    { id:'velvet', name:'Velvet Bar', address:'43 Rue Saint-Honoré, 75001 Paris', neighborhood:'Les Halles (1er)', lat:48.8607768, lng:2.3454208, mapX:50, mapY:42, listed:true, description:'A cocktail bar in the 1er, Les Halles, 160m from Châtelet. Hosts the French Fried Comedy Night Wednesday stack — three back-to-back English/bilingual shows on the same stage. Free entry, drink purchase mandatory.', metro:'Châtelet (M1/M4/M7/M11/M14)', website:'https://velvet-bar.fr/', source:'velvet-bar.fr/contact + Eventbrite event 1977106148713 — verified 2026-05-18' },
    { id:'paname', name:'Paname Art Café', address:'2bis Quai de la Loire, 75019 Paris', neighborhood:'Canal Saint-Martin (19th)', lat:48.8844, lng:2.3728, mapX:72, mapY:18, listed:false, description:'A legendary venue overlooking Canal Saint-Martin where French Fried Comedy Night was born in 2013. Kept here as a historical comedy landmark, not as a current featured English listing on this site.', metro:'Jaurès (M2/M5/M7bis)' },
    { id:'green-mic', name:'Green Mic Paris', address:'32 Rue Muller, 75018 Paris', neighborhood:'Montmartre (18th)', lat:48.8867, lng:2.3431, mapX:42, mapY:15, listed:false, description:'A rising fixture on the English comedy scene. Green Mic hosts regular English stand-up nights in Montmartre and central Paris — casual, fun, and growing fast.', metro:'Anvers (M2) · Abbesses (M12)' },
    { id:'bikini-bottom', name:'Le Bikini Bottom', address:'Paris', neighborhood:'Paris', lat:48.8600, lng:2.3500, mapX:52, mapY:45, listed:false, description:'Le Bikini Bottom hosts Millennial Meltdown — a weekly Wednesday English stand-up night with a young, expat-friendly crowd.', metro:'' },
    { id:'les-marquises', name:'Les Marquises', address:'Paris', neighborhood:'Paris', lat:48.8650, lng:2.3700, mapX:70, mapY:38, listed:false, description:'A neighborhood bar hosting Green Light Comedy every Tuesday at 20:15 — English stand-up with a local flavor.', metro:'' },
    { id:'englishman', name:'The Englishman Cocktail Club', address:'Paris', neighborhood:'Paris', lat:48.8700, lng:2.3300, mapX:42, mapY:32, listed:false, description:'Part cocktail bar, part comedy room. The Englishman Comedy Night runs every Thursday — English humour in a very French city.', metro:'' },
    { id:'theatre-bo', name:'Théâtre BO Saint-Martin', address:'19 Boulevard Saint-Martin, 75003 Paris', neighborhood:'République (3rd)', lat:48.8680, lng:2.3540, mapX:58, mapY:35, listed:true, description:'Professional comedy theatre near République. Home of "Oh My God She\'s Parisian!" (Julie Coulon) — Friday and Saturday nights at 20:15. Sarah Donnelly\'s regular stage.', metro:'République (M3/M5/M8/M9/M11)' },
    { id:'le-noddi', name:'Le Noddi', address:'16 Rue Bernardins, 75005 Paris', neighborhood:'Latin Quarter (5th)', lat:48.8513, lng:2.3527, mapX:53, mapY:56, listed:false, description:'Funny Women Paris — English stand-up featuring women comedians every Tuesday at 20:30.', metro:'Maubert-Mutualité (M10)' },
    { id:'le-kibele', name:'Le Kibélé', address:'12 Rue de l\'Éperon, 75006 Paris', neighborhood:'Paris', lat:48.8750, lng:2.3450, mapX:48, mapY:25, listed:false, description:'The Open Mic Express — English stand-up open mic.', metro:'' },
    { id:'au-soleil', name:'Au Soleil de la Butte', address:'32 Rue Muller, 75018 Paris', neighborhood:'Montmartre (18th)', lat:48.8867, lng:2.3431, mapX:42, mapY:15, listed:false, description:'Green Mic Showcase venue in Montmartre — English stand-up every Friday at 20:30 with a classic Paris neighbourhood crowd.', metro:'Anvers (M2) · Abbesses (M12)' },
    { id:'les-cariatiades', name:'Les Cariatiades', address:'Paris', neighborhood:'Paris', lat:48.8690, lng:2.3480, mapX:50, mapY:33, listed:false, description:'Home of Comedy Crush — Wednesday night English stand-up at 20:30. A growing room on the Paris comedy circuit.', metro:'' },
    { id:'dissident-club', name:'The Dissident Club', address:'58 Rue Richer, 75009 Paris', neighborhood:'Faubourg-Montmartre (9th)', lat:48.8730, lng:2.3443, mapX:48, mapY:28, listed:false, description:'The Dissident Comedy Show — verified Wednesday English stand-up at 20:30 with an alternative, sharp comedy sensibility.', metro:'Grands Boulevards (M8/M9) · Cadet (M7)' },
    { id:'pomme-eve', name:'La Pomme d\'Eve', address:'1 Rue des Boulangers, 75005 Paris', neighborhood:'Latin Quarter', lat:48.8520, lng:2.3490, mapX:50, mapY:55, listed:false, description:'Latin Quarter venue currently carrying verified Wednesday Night Comedy (19:30) and Blast Off All Stars (Saturday 19:30) in the public reference layer.', metro:'Place Monge (M7)' },
    { id:'paris-humour', name:'Le Paris de l\'Humour', address:'Paris', neighborhood:'Paris', lat:48.8680, lng:2.3560, mapX:55, mapY:34, listed:false, description:'MANGO English Stand-Up — Wednesday nights at 19:45 with Randy J Dreams.', metro:'' },
    { id:'timbaud', name:'76 Rue Jean-Pierre Timbaud', address:'76 Rue Jean-Pierre Timbaud, 75011 Paris', neighborhood:'Oberkampf (11th)', lat:48.8644, lng:2.3748, mapX:73, mapY:42, listed:false, description:'English stand-up comedy on Thursday and Saturday nights at 18:30 — one of the more active English comedy spots in East Paris.', metro:'Parmentier (M3)' },
    { id:'chat-noir', name:'Chat Noir', address:'76 Rue Jean-Pierre Timbaud, 75011 Paris', neighborhood:'Oberkampf (11th)', lat:48.8644, lng:2.3748, mapX:73, mapY:42, listed:false, description:'Iconic 11th-arrondissement venue hosting Comedy Lab\'s recurring English stand-up shows on Thursdays and Saturdays.', metro:'Parmentier (M3)' },
    { id:'comedie-cafe', name:'Comédie Café', address:'Paris', neighborhood:'Paris', lat:48.8660, lng:2.3520, mapX:54, mapY:38, listed:false, description:'One of Paris\'s busiest comedy venues — home to South Comedy Club (Wed) and Smash Comedy Club. Multiple shows weekly.', metro:'' },
    { id:'fiap-paris', name:'FIAP Paris', address:'30 Rue Cabanis, 75014 Paris', neighborhood:'Montparnasse (14th)', lat:48.8330, lng:2.3330, mapX:38, mapY:65, listed:false, description:'FIAP Comedy Club every Thursday at 19:30 — popular with students and international crowds.', metro:'Glacière (M6)' },
    { id:'cafe-oscar', name:'Café Oscar', address:'155 Rue Montmartre, 75002 Paris', neighborhood:'Montorgueil / Bourse (2nd)', lat:48.8700, lng:2.3400, mapX:44, mapY:30, listed:false, description:'Home of Oscar Comedy Club — Sunday afternoon shows and one of the most frequent comedy programmes in Paris.', metro:'Grands Boulevards (M8/M9)' },
    { id:'poincon', name:'Poinçon Paris', address:'Paris', neighborhood:'Montparnasse', lat:48.8410, lng:2.3270, mapX:34, mapY:68, listed:false, description:'Kinto Comedy Club — English stand-up every Friday at 19:30. A rising venue on the Paris comedy circuit.', metro:'Montparnasse-Bienvenue (M4/M6/M12/M13)' },
    { id:'cesure', name:'Césure', address:'13 Rue Santeuil, 75005 Paris', neighborhood:'Latin Quarter (5th)', lat:48.8490, lng:2.3470, mapX:48, mapY:58, listed:false, description:'Greenwashing Comedy Club — English comedy with an eco-conscious angle. Thursday evenings.', metro:'Cardinal Lemoine (M10)' },
    { id:'cuba-compagnie', name:'Cuba Compagnie', address:'48 Bd Beaumarchais, 75011 Paris', neighborhood:'Bastille (11th)', lat:48.8566, lng:2.3668, mapX:67, mapY:52, listed:false, description:'Cuba Compagnie Comedy Club — English stand-up on Tuesday evenings at 19:30. 25+ upcoming dates. Established venue on Bd Beaumarchais.', metro:'Chemin Vert (M8)' },
    { id:'speechless', name:'Speechless', address:'45 Rue de Montreuil, 75011 Paris', neighborhood:'Nation / Alexandre Dumas (11th)', lat:48.8523, lng:2.3854, mapX:74, mapY:45, listed:false, description:'Home of Mic Drop Comedy Club — a verified Wednesday English stand-up room at 20:00.', metro:'Alexandre Dumas (M2) / Nation (M1/M2/M6/M9/RER A)' },
    { id:'bonne-nouvelle', name:'25 Bd de Bonne Nouvelle', address:'25 Bd de Bonne Nouvelle, 75002 Paris', neighborhood:'Grands Boulevards (2nd)', lat:48.8700, lng:2.3510, mapX:52, mapY:27, listed:false, description:'Broadway Comedy Club Paris — English and bilingual stand-up every evening at 19:00. One of the most active comedy venues in central Paris.', metro:'Bonne Nouvelle (M8/M9)' },
    { id:'fada-paris', name:'Fada Paris', address:'Paris', neighborhood:'Paris', lat:48.8690, lng:2.3600, mapX:61, mapY:35, listed:false, description:'LOFI Comedy Club — English stand-up every Tuesday at 19:00. Relaxed, intimate venue.', metro:'' },
    { id:'cafe-plage', name:'Le Café de la Plage', address:'Paris', neighborhood:'Charonne (11th)', lat:48.8530, lng:2.3820, mapX:78, mapY:54, listed:false, description:'Home of Charonne Comedy Club — English stand-up every Saturday at 19:30. East Paris venue with 20+ upcoming shows.', metro:'Charonne (M9)' },
    { id:'le-tlm', name:'Le TLM Paris', address:'105 Rue Curial, 75019 Paris', neighborhood:'Rosa Parks / 19th', lat:48.8610, lng:2.3470, mapX:47, mapY:44, listed:false, description:'Sparkle Comedy Club — English stand-up every Thursday at 21:00. Late-night Paris comedy.', metro:'Rosa Parks (RER E) / Corentin Cariou (M7)' },
    { id:'cotte23', name:'Cotte 23', address:'23 Rue de la Mare, 75020 Paris', neighborhood:'Belleville (20th)', lat:48.8693, lng:2.3817, mapX:72, mapY:35, listed:false, description:'Rocket Comedy Club — English stand-up every Tuesday at 19:00. A lively Belleville bar with a growing comedy scene.', metro:'Ménilmontant (M2)' },
    { id:'coquin', name:'Le Coquin', address:'Paris', neighborhood:'Paris', lat:48.8650, lng:2.3550, mapX:54, mapY:40, listed:false, description:'Kiss Comedy Club — Wednesday night English comedy in an intimate Parisian bar. Regular shows at 20:00.', metro:'' },
    { id:'toloache', name:'Toloache', address:'Paris', neighborhood:'Marais / 3rd', lat:48.8600, lng:2.3590, mapX:58, mapY:46, listed:false, description:'Kuhl Comedy Open Mic — English stand-up open mic every Tuesday at 19:30. A friendly room for new voices and regulars.', metro:'Temple (M3)' }
].map(venue => {
    const hasExactAddress = /\b75\d{3}\b/.test(venue.address || '');
    const mapQuery = hasExactAddress ? encodeURIComponent(`${venue.name}, ${venue.address}`) : '';
    return {
        ...venue,
        hasExactAddress,
        googleMapsUrl: hasExactAddress ? `https://www.google.com/maps/search/?api=1&query=${mapQuery}` : '',
        directions: hasExactAddress ? {
            walking: `https://www.google.com/maps/dir/?api=1&destination=${mapQuery}&travelmode=walking`,
            transit: `https://www.google.com/maps/dir/?api=1&destination=${mapQuery}&travelmode=transit`,
            driving: `https://www.google.com/maps/dir/?api=1&destination=${mapQuery}&travelmode=driving`
        } : null,
        mapReviewNote: hasExactAddress ? '' : 'Exact Google Maps link still needs manual verification for this venue.'
    };
});

const SHOWS = [
    { id:'velvet-openmic', name:'Velvet Bar Comedy — Open Mic', shortName:'Open Mic', venue:'velvet', type:'openmic', day:'Wednesday', time:'19:00', price:'Free', emoji:'🎙️',
      description:'Sign up, step up, make them laugh. All levels welcome — the best open mic at Velvet Bar (43 Rue Saint-Honoré, 75001, near Châtelet).',
      descFr:'Inscrivez-vous, montez sur scène, faites-les rire. Tous niveaux bienvenus.',
      descEs:'Inscríbete, sube al escenario, hazlos reír. Todos los niveles son bienvenidos.',
      bookingUrl:'https://www.eventbrite.com/e/velvet-bar-comedy-open-mic-stand-up-comedy-a-paris-tickets-1977106148713' + UTM, featured:false },
    { id:'velvet-comedy', name:'Velvet Bar Comedy — Le meilleur du stand-up', shortName:'Comedy Night', venue:'velvet', type:'standup', day:'Wednesday', time:'20:30', price:'Free', emoji:'🎭',
      description:'Curated showcase — the best comics in Paris on one stage. Bilingual, unpredictable, unforgettable.',
      descFr:'Showcase soigné — les meilleurs humoristes de Paris sur une même scène. Bilingue, imprévisible, inoubliable.',
      descEs:'Showcase curado — los mejores cómicos de París en un escenario. Bilingüe, impredecible, inolvidable.',
      bookingUrl:'https://www.eventbrite.com/e/velvet-bar-comedy-le-meilleur-du-stand-up-a-paris-tickets-1825871804719' + UTM, featured:true },
    { id:'ffcn', name:'French Fried Comedy Night', shortName:'FFCN', venue:'velvet', type:'standup', day:'Wednesday', time:'22:00', price:'Free', emoji:'🍟',
      description:'THE bilingual comedy show. American & French comics, English & French jokes, same night. The show that started it all.',
      descFr:'LE spectacle de comédie bilingue. Humoristes américains et français, blagues en anglais et en français, le même soir.',
      descEs:'EL show de comedia bilingüe. Cómicos americanos y franceses, chistes en inglés y francés, la misma noche.',
      bookingUrl:'https://www.eventbrite.com/e/french-fried-comedy-night-tickets-603182383747' + UTM, featured:true },
    /* Paname removed from our shows — not our venue */
];

/* Public current-show directory — only shows with verified activity inside the last 6 months stay in this layer. */
const SIX_MONTHS_MS = 183 * 24 * 60 * 60 * 1000;
const CURRENT_SHOWS_CUTOFF = new Date('2025-10-06T00:00:00+02:00');

const OTHER_SHOWS_RAW = [
    { id:'kuhl-open-mic', name:'Kuhl Comedy Open Mic', venue:'toloache', venueName:'Toloache', address:'Paris', day:'Tuesday', time:'19:30', type:'openmic', emoji:'🎙️',
      description:'English stand-up open mic at Toloache every Tuesday at 19:30. Run by Kuhl Comedy — a friendly room for new voices and regulars alike.',
      descFr:'Scène ouverte de stand-up en anglais chez Toloache chaque mardi à 19h30. Une salle conviviale pour les nouveaux comme pour les habitués.',
      bookingUrl:'https://www.eventbrite.fr/e/stand-up-open-mic-in-english-by-kuhl-comedy-tickets-1760885549079', paid:false,
      runner:'Kuhl Comedy', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/stand-up-open-mic-in-english-by-kuhl-comedy-tickets-1760885549079' },
    { id:'green-light', name:'Green Light Comedy', venue:'les-marquises', venueName:'Les Marquises', address:'Paris', day:'Tuesday', time:'20:15', type:'standup', emoji:'🟢',
      description:'English stand-up every Tuesday at 20:15 at Les Marquises — one of the most consistent comedy nights on the Paris circuit.',
      descFr:'Stand-up en anglais chaque mardi à 20h15 aux Marquises — l’une des soirées les plus régulières du circuit parisien.',
      bookingUrl:'https://www.eventbrite.fr/e/standup-comedy-in-english-green-light-in-paris-tickets-927454971787', paid:false,
      runner:'Green Light Comedy', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/standup-comedy-in-english-green-light-in-paris-tickets-927454971787' },
    { id:'cuba-compagnie', name:'Cuba Compagnie Comedy Club', venue:'cuba-compagnie', venueName:'Cuba Compagnie', address:'48 Bd Beaumarchais, 75011 Paris', day:'Tuesday', time:'19:30', type:'standup', emoji:'🎺',
      description:'Tuesday evening English stand-up at Cuba Compagnie with a reliable recurring run and an established room near Bastille.',
      descFr:'Stand-up en anglais le mardi soir chez Cuba Compagnie, dans une salle bien installée près de Bastille.',
      bookingUrl:'https://www.eventbrite.fr/e/cuba-compagnie-comedy-club-tickets-1254791257429', paid:false,
      runner:'Cuba Compagnie Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/cuba-compagnie-comedy-club-tickets-1254791257429' },
    { id:'funny-women', name:'Funny Women Paris', venue:'le-noddi', venueName:'Le Noddi', address:'16 Rue Bernardins, 75005 Paris', day:'Tuesday', time:'20:30', type:'standup', emoji:'👩🎤',
      description:'All-women English stand-up lineup at Le Noddi every Tuesday, with doors at 20:00 and showtime at 20:30.',
      descFr:'Plateau 100 % féminin de stand-up en anglais au Noddi chaque mardi, ouverture des portes à 20h00 et début du spectacle à 20h30.',
      bookingUrl:'https://www.eventbrite.fr/e/english-stand-up-comedy-in-paris-funny-women-tickets-295960655287', paid:false,
      runner:'Coucou Comedy', verificationSource:'Eventbrite', verifiedAt:'2026-04-08', showUrl:'https://www.eventbrite.fr/e/english-stand-up-comedy-in-paris-funny-women-tickets-295960655287' },
    { id:'rocket', name:'Rocket Comedy Club', venue:'cotte23', venueName:'Cotte 23', address:'23 Rue de la Mare, 75020 Paris', day:'Tuesday', time:'19:00', type:'standup', emoji:'🚀',
      description:'Rocket Comedy Club runs every Tuesday with a bilingual-friendly crowd and a growing foothold in Belleville.',
      descFr:'Rocket Comedy Club a lieu chaque mardi avec un public bilingue et une vraie présence à Belleville.',
      bookingUrl:'https://www.eventbrite.fr/e/rocket-comedy-club-tickets-1001216875627', paid:false,
      runner:'Rocket Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/rocket-comedy-club-tickets-1001216875627' },
    { id:'lofi', name:'LOFI Comedy Club', venue:'fada-paris', venueName:'Fada Paris', address:'Paris', day:'Tuesday', time:'19:00', type:'standup', emoji:'🎵',
      description:'Laid-back Tuesday English comedy at Fada Paris with a growing regular crowd.',
      descFr:'Soirée comédie en anglais détendue le mardi chez Fada Paris, avec un public fidèle en croissance.',
      bookingUrl:'https://www.eventbrite.com/e/lofi-comedy-club-2-tickets-1982107345427', paid:false,
      runner:'LOFI Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.com/e/lofi-comedy-club-2-tickets-1982107345427' },
    { id:'comedy-crush', name:'Comedy Crush Wednesday Show', venue:'les-cariatiades', venueName:'Les Cariatiades', address:'Paris', day:'Wednesday', time:'20:30', type:'standup', emoji:'💥',
      description:'Packed Wednesday showcase with strong crowd energy and a dependable recurring listing.',
      descFr:'Showcase du mercredi, souvent bien rempli, avec une vraie énergie de salle.',
      bookingUrl:'https://www.eventbrite.fr/e/comedy-crushs-wednesday-show-tickets-1982356098454', paid:false,
      runner:'Comedy Crush', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/comedy-crushs-wednesday-show-tickets-1982356098454' },
    { id:'millennial-meltdown', name:'Millennial Meltdown', venue:'bikini-bottom', venueName:'Le Bikini Bottom', address:'49 Rue de Lappe, 75011 Paris', day:'Wednesday', time:'20:00', type:'standup', emoji:'🫠',
      description:'A recurring Wednesday English stand-up night in Bastille from Kuhl Comedy, built around sharp modern-life material and an expat-friendly crowd.',
      descFr:'Soirée régulière de stand-up en anglais le mercredi à Bastille, signée Kuhl Comedy, avec un public expat et des thèmes très contemporains.',
      bookingUrl:'https://www.eventbrite.fr/e/billets-english-comedy-show-millennial-meltdown-paris-stand-up-night-1984665294321', paid:false,
      runner:'Kuhl Comedy', verificationSource:'Eventbrite', verifiedAt:'2026-04-08', showUrl:'https://www.eventbrite.fr/e/billets-english-comedy-show-millennial-meltdown-paris-stand-up-night-1984665294321' },
    { id:'dissident', name:'The Dissident Comedy Show', venue:'dissident-club', venueName:'The Dissident Club', address:'58 Rue Richer, 75009 Paris', day:'Wednesday', time:'20:30', type:'standup', emoji:'🎷',
      description:'Alternative English stand-up every Wednesday at The Dissident Club, hosted by Maddie Storm, with a live multi-date Eventbrite listing and a verified central-Paris address.',
      descFr:'Stand-up en anglais chaque mercredi au Dissident Club, animé par Maddie Storm, avec une adresse vérifiée dans le centre de Paris et une vraie récurrence Eventbrite.',
      bookingUrl:'https://www.eventbrite.fr/e/the-dissident-comedy-show-tickets-1985334998424', paid:false,
      runner:'Maddie Storm', verificationSource:'Eventbrite', verifiedAt:'2026-04-06', showUrl:'https://www.eventbrite.fr/e/the-dissident-comedy-show-tickets-1985334998424' },
    { id:'mic-drop', name:'Mic Drop Comedy Club', venue:'speechless', venueName:'Speechless', address:'45 Rue de Montreuil, 75011 Paris', day:'Wednesday', time:'20:00', type:'standup', emoji:'🎤',
      description:'Wednesday stand-up at Speechless with a direct live Eventbrite listing confirmed for 8 April 2026.',
      descFr:'Stand-up du mercredi chez Speechless, avec une fiche Eventbrite en direct confirmée pour le 8 avril 2026.',
      bookingUrl:'https://www.eventbrite.com/e/mic-drop-comedy-club-tickets-1982353596972', paid:false,
      runner:'Mic Drop Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-08', showUrl:'https://www.eventbrite.com/e/mic-drop-comedy-club-tickets-1982353596972' },
    { id:'mango', name:'MANGO English Stand-Up', venue:'paris-humour', venueName:'Le Paris de l\'Humour', address:'Paris', day:'Wednesday', time:'19:45', type:'standup', emoji:'🥭',
      description:'Wednesday English stand-up at Le Paris de l’Humour with Randy J Dreams.',
      descFr:'Stand-up en anglais le mercredi au Paris de l’Humour avec Randy J Dreams.',
      bookingUrl:'https://www.eventbrite.ca/e/mango-english-stand-up-comedy-in-paris-randy-j-dreams-tickets-1984868292494', paid:false,
      runner:'Randy J Dreams', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.ca/e/mango-english-stand-up-comedy-in-paris-randy-j-dreams-tickets-1984868292494' },
    { id:'wednesday-night-comedy', name:'Wednesday Night Comedy', venue:'pomme-eve', venueName:'La Pomme d\'Eve', address:'1 Rue des Boulangers, 75005 Paris', day:'Wednesday', time:'19:30', type:'standup', emoji:'🌙',
      description:'Reliable mid-week English comedy in the Latin Quarter at La Pomme d’Eve.',
      descFr:'Soirée comédie en anglais fiable en milieu de semaine à La Pomme d’Eve, dans le Quartier Latin.',
      bookingUrl:'https://www.eventbrite.fr/e/english-standup-wednesday-night-comedy-tickets-1750646975229', paid:false,
      runner:'Wednesday Night Comedy', verificationSource:'Eventbrite', verifiedAt:'2026-04-08', showUrl:'https://www.eventbrite.fr/e/english-standup-wednesday-night-comedy-tickets-1750646975229' },
    { id:'kiss-comedy', name:'Kiss Comedy Club', venue:'coquin', venueName:'Le Coquin', address:'Paris', day:'Wednesday', time:'20:00', type:'standup', emoji:'💋',
      description:'Midweek English and bilingual comedy in an intimate Paris bar.',
      descFr:'Comédie anglaise et bilingue en milieu de semaine dans un bar parisien intimiste.',
      bookingUrl:'https://www.eventbrite.fr/e/kiss-comedy-club-tickets-1935245083139', paid:false,
      runner:'Kiss Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/kiss-comedy-club-tickets-1935245083139' },
    { id:'south-comedy', name:'South Comedy Club', venue:'comedie-cafe', venueName:'Comédie Café', address:'Paris', day:'Wednesday', time:'20:00', type:'standup', emoji:'☀️',
      description:'One of the busiest English comedy rooms in Paris with a deep recurring calendar.',
      descFr:'L’une des salles de comédie en anglais les plus actives de Paris, avec un calendrier dense.',
      bookingUrl:'https://www.eventbrite.fr/e/billets-south-comedy-club-1716456721259', paid:false,
      runner:'South Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/billets-south-comedy-club-1716456721259' },
    { id:'theatre-bo-julie', name:'Oh My God She\'s Parisian! — Julie Coulon', venue:'theatre-bo', venueName:'Théâtre BO Saint-Martin', address:'19 Boulevard Saint-Martin, 75003 Paris', day:['Friday','Saturday'], time:'20:15', type:'standup', emoji:'🎭', featured:true,
      description:'A polished English-language solo show on a professional theatre stage Friday and Saturday nights.',
      descFr:'Un solo-show en anglais sur une vraie scène de théâtre, les vendredis et samedis soirs.',
      bookingUrl:'https://www.eventbrite.fr/e/the-comedy-in-english-by-a-french-girl-that-will-make-you-love-paris-tickets-1764207685679', paid:false,
      runner:'Julie Coulon', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/the-comedy-in-english-by-a-french-girl-that-will-make-you-love-paris-tickets-1764207685679' },
    { id:'fiap', name:'FIAP Comedy Club', venue:'fiap-paris', venueName:'FIAP Paris', address:'30 Rue Cabanis, 75014 Paris', day:'Thursday', time:'19:30', type:'standup', emoji:'🎭',
      description:'Thursday English stand-up at FIAP Paris, strong with students and international crowds.',
      descFr:'Stand-up en anglais le jeudi au FIAP Paris, très apprécié des étudiants et publics internationaux.',
      bookingUrl:'https://www.eventbrite.fr/e/fiap-comedy-club-tickets-1986207987558', paid:false,
      runner:'FIAP Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/fiap-comedy-club-tickets-1986207987558' },
    { id:'englishman-night', name:'The Englishman Comedy Night', venue:'englishman', venueName:'The Englishman Cocktail Club', address:'Paris', day:'Thursday', time:'20:00', type:'standup', emoji:'🇬🇧',
      description:'English-language comedy night in a cocktail-club setting.',
      descFr:'Soirée de comédie en anglais dans un cocktail club parisien.',
      bookingUrl:'https://www.eventbrite.com/e/the-englishman-comedy-night-tickets-1982274965784', paid:false,
      runner:'The Englishman Comedy Night', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.com/e/the-englishman-comedy-night-tickets-1982274965784' },
    { id:'greenwashing', name:'Greenwashing Comedy Club', venue:'cesure', venueName:'Césure', address:'Paris', day:'Thursday', time:'20:00', type:'standup', emoji:'🌱',
      description:'English comedy with an eco-conscious angle on Thursday evenings.',
      descFr:'Comédie en anglais avec un angle écolo, le jeudi soir.',
      bookingUrl:'https://www.eventbrite.fr/e/greenwashing-comedy-club-a-cesure-tickets-1984380900692' + UTM, paid:false,
      runner:'Greenwashing Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/greenwashing-comedy-club-a-cesure-tickets-1984380900692' },
    { id:'sparkle', name:'Sparkle Comedy Club', venue:'le-tlm', venueName:'Le TLM Paris', address:'Paris', day:'Thursday', time:'21:00', type:'standup', emoji:'✨',
      description:'Late Thursday English comedy in Paris.',
      descFr:'Comédie en anglais en fin de soirée le jeudi à Paris.',
      bookingUrl:'https://www.eventbrite.fr/e/sparkle-comedy-club-tickets-1985497313914', paid:false,
      runner:'Sparkle Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/sparkle-comedy-club-tickets-1985497313914' },
    { id:'comedy-lab-chat-noir', name:'Comedy Lab', venue:'chat-noir', venueName:'Chat Noir', address:'76 Rue Jean-Pierre Timbaud, 75011 Paris', day:['Thursday','Saturday'], time:'20:00', type:'standup', emoji:'🧪',
      description:'Recurring English stand-up at Chat Noir every Thursday plus early and late Saturday shows. Strong tourist fit, central 11th-arrondissement location, and a live multi-date Eventbrite listing.',
      descFr:'Plateau régulier de stand-up en anglais au Chat Noir chaque jeudi, avec deux horaires le samedi. Bon fit touristes/expats, dans le 11e, avec une vraie fiche Eventbrite multi-dates.',
      bookingUrl:'https://www.eventbrite.com/e/english-stand-up-comedy-in-paris-thursday-saturday-night-shows-tickets-77709323679', paid:false,
      runner:'Comedy Lab', verificationSource:'Eventbrite', verifiedAt:'2026-04-09', showUrl:'https://www.eventbrite.com/e/english-stand-up-comedy-in-paris-thursday-saturday-night-shows-tickets-77709323679' },
    { id:'green-mic-showcase', name:'Green Mic Showcase', venue:'au-soleil', venueName:'Au Soleil de la Butte', address:'32 Rue Muller, 75018 Paris', day:'Friday', time:'20:30', type:'standup', emoji:'🎙️', featured:true,
      description:'One of the sharpest Friday English showcase rooms in Montmartre, with doors at 20:15 and showtime at 20:30.',
      descFr:'L’un des meilleurs showcase anglophones du vendredi à Montmartre.',
      bookingUrl:'https://www.eventbrite.fr/e/billets-standup-comedy-in-english-green-mic-showcase-montmartre-573952757147', paid:false,
      runner:'Green Mic', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/billets-standup-comedy-in-english-green-mic-showcase-montmartre-573952757147' },
    { id:'coucou-friday', name:'English Stand-Up Comedy in Paris — Friday Night Show', venue:'pomme-eve', venueName:'La Pomme d\'Eve', address:'1 Rue Laplace, 75005 Paris', day:'Friday', time:'20:30', type:'standup', emoji:'🍎',
      description:'Weekly Friday English stand-up at La Pomme d\'Eve from Coucou Comedy, with doors at 20:00 and a pay-what-you-can exit model.',
      descFr:'Soirée hebdo de stand-up en anglais le vendredi à La Pomme d\'Eve par Coucou Comedy, avec ouverture des portes à 20h00 et participation libre à la sortie.',
      bookingUrl:'https://www.eventbrite.fr/e/english-stand-up-comedy-in-paris-friday-night-show-tickets-364336088047', paid:false,
      runner:'Coucou Comedy', verificationSource:'Eventbrite', verifiedAt:'2026-04-08', showUrl:'https://www.eventbrite.fr/e/english-stand-up-comedy-in-paris-friday-night-show-tickets-364336088047' },
    { id:'open-mic-express', name:'The Open Mic Express', venue:'le-kibele', venueName:'Le Kibélé', address:'12 Rue de l\'Éperon, 75006 Paris', day:'Friday', time:'19:00', type:'openmic', emoji:'🚂',
      description:'English open mic at Le Kibélé — drop in, sign up, perform.',
      descFr:'Scène ouverte anglophone au Kibélé — venez, inscrivez-vous, montez sur scène.',
      bookingUrl:'https://www.eventbrite.com/e/the-open-mic-express-english-stand-up-comedy-april-17-tickets-1985629550437', paid:false,
      runner:'The Open Mic Express', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.com/e/the-open-mic-express-english-stand-up-comedy-april-17-tickets-1985629550437' },
    { id:'kinto', name:'Kinto Comedy Club', venue:'poincon', venueName:'Poinçon Paris', address:'Paris', day:'Friday', time:'19:30', type:'standup', emoji:'🎯',
      description:'Friday English stand-up in one of Paris’s most atmospheric venues.',
      descFr:'Stand-up en anglais le vendredi dans l’un des lieux les plus atmosphériques de Paris.',
      bookingUrl:'https://www.eventbrite.fr/e/kinto-comedy-club-au-poincon-tickets-1981428458859', paid:false,
      runner:'Kinto Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/kinto-comedy-club-au-poincon-tickets-1981428458859' },
    { id:'smash', name:'Smash Comedy Club', venue:'comedie-cafe', venueName:'Comédie Café', address:'Paris', day:'Saturday', time:'19:00', type:'standup', emoji:'💥',
      description:'High-volume English comedy programme with frequent Saturday dates.',
      descFr:'Programme de comédie en anglais très actif, avec de nombreuses dates le samedi.',
      bookingUrl:'https://www.eventbrite.com/e/smash-comedy-club-tickets-1902240916789', paid:false,
      runner:'Smash Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.com/e/smash-comedy-club-tickets-1902240916789' },
    { id:'integrire', name:'IntégRire Comedy Night', venue:'le-kibele', venueName:'Le Kibélé', address:'12 Rue de l\'Éperon, 75006 Paris', day:'Saturday', time:'19:00', type:'standup', emoji:'🌍',
      description:'Multicultural Saturday night with English comedy and a diverse lineup.',
      descFr:'Soirée multiculturelle du samedi avec de la comédie en anglais et un plateau varié.',
      bookingUrl:'https://www.eventbrite.fr/e/integrire-comedy-night-3-tickets-1986334225138', paid:false,
      runner:'IntégRire', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/integrire-comedy-night-3-tickets-1986334225138' },
    { id:'blast-off', name:'Blast Off All Stars', venue:'pomme-eve', venueName:'La Pomme d\'Eve', address:'1 Rue des Boulangers, 75005 Paris', day:'Saturday', time:'19:30', type:'standup', emoji:'🚀',
      description:'Saturday all-star English showcase at La Pomme d’Eve.',
      descFr:'Showcase all-stars du samedi à La Pomme d’Eve.',
      bookingUrl:'https://www.eventbrite.com/e/blast-off-all-stars-english-stand-up-comedy-april-25-tickets-1986150988071', paid:false,
      runner:'Blast Off All Stars', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.com/e/blast-off-all-stars-english-stand-up-comedy-april-25-tickets-1986150988071' },
    { id:'charonne', name:'Charonne Comedy Club', venue:'cafe-plage', venueName:'Le Café de la Plage', address:'Paris', day:'Saturday', time:'19:30', type:'standup', emoji:'🏖️',
      description:'Consistent English comedy night in East Paris with a real recurring run.',
      descFr:'Soirée comédie en anglais régulière dans l’est parisien.',
      bookingUrl:'https://www.eventbrite.fr/e/charonne-comedy-club-tickets-1697805324429', paid:false,
      runner:'Charonne Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/charonne-comedy-club-tickets-1697805324429' },
    { id:'oscar', name:'Oscar Comedy Club', venue:'cafe-oscar', venueName:'Café Oscar', address:'Paris', day:'Sunday', time:'17:00', type:'standup', emoji:'🏆',
      description:'Sunday afternoon English and bilingual comedy at Café Oscar.',
      descFr:'Comédie anglaise et bilingue le dimanche après-midi au Café Oscar.',
      bookingUrl:'https://www.eventbrite.fr/e/oscar-comedy-club-tickets-1985916648154', paid:false,
      runner:'Oscar Comedy Club', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/oscar-comedy-club-tickets-1985916648154' },
    { id:'green-mic-sunday', name:'Green Mic Comedy Show', venueName:'Ma Cocotte du Faubourg', address:'5 Rue du Faubourg Montmartre, 75009 Paris', day:'Sunday', time:'19:30', type:'standup', emoji:'🌿',
      description:'Sunday English stand-up with a verified recurring run on Eventbrite. Doors at 19:00, show at 19:30.',
      descFr:'Soirée de stand-up en anglais le dimanche, avec une vraie récurrence vérifiée sur Eventbrite.',
      bookingUrl:'https://www.eventbrite.fr/e/green-mic-comedy-show-tickets-214634947907', paid:false,
      runner:'Green Mic', verificationSource:'Eventbrite', verifiedAt:'2026-04-05', showUrl:'https://www.eventbrite.fr/e/green-mic-comedy-show-tickets-214634947907' },

    { id:'broadway-comedy-club', name:'Broadway Comedy Club - Paris', venue:'bonne-nouvelle', venueName:'25 Bd de Bonne Nouvelle', address:'25 Bd de Bonne Nouvelle, 75002 Paris', day:'daily', time:'19:00', type:'standup', emoji:'🎬', paid:true,
      description:'Daily English and bilingual stand-up near Bonne Nouvelle with a high-volume schedule and one of the deepest recurring calendars in central Paris.',
      descFr:'Stand-up en anglais et bilingue tous les soirs près de Bonne Nouvelle, avec un calendrier très dense au cœur de Paris.',
      bookingUrl:'https://www.eventbrite.com/e/billets-broadway-comedy-club-paris-1978410990530',
      runner:'Broadway Comedy Club Paris', verificationSource:'Eventbrite', verifiedAt:'2026-04-09', showUrl:'https://www.eventbrite.com/e/billets-broadway-comedy-club-paris-1978410990530' },

    /* stale / not recent enough for public current layer */
    { id:'paname-archive', name:'Paname English Stand-Up', venueName:'Paname Art Café', day:'Tuesday', time:'17:30', type:'standup', emoji:'🎤', paid:false, bookingUrl:'https://www.billetreduc.com/recherche.htm?q=stand+up+paname+art+cafe', runner:'Paname Art Café', verificationSource:'BilletReduc', verifiedAt:'2025-07-01', archived:true }
];

const OTHER_SHOWS = OTHER_SHOWS_RAW.filter(show => {
    if (!show.verifiedAt) return false;
    return new Date(show.verifiedAt) >= CURRENT_SHOWS_CUTOFF && !show.archived;
});

const ALL_CURRENT_SHOWS = [...SHOWS, ...OTHER_SHOWS];
const CURRENT_SHOWS_BY_VENUE = VENUES.map(venue => ({
    ...venue,
    shows: ALL_CURRENT_SHOWS.filter(show => (show.venue && show.venue === venue.id) || show.venueName === venue.name)
})).filter(venue => venue.shows.length > 0);

const KEY_PLAYERS = [
    { id:'seb', name:'Sebastian Marx', title:'The Pioneer', emoji:'🗽',
      instagram:'https://www.instagram.com/sebastianmarxcomedy/',
      bio:'New Yorker who fell in love with a French woman and moved to Paris. Created "New York Comedy Night" at SoGymnase — the FIRST regular English stand-up show in Paris. Appeared on Jamel Comedy Club (Canal+), got a radio gig on RTL with Stéphane Bern, and later France Inter. He\'s the one who proved English-language comedy could work in Paris.',
      bioFr:'New-Yorkais tombé amoureux d\'une Française. Créateur de "New York Comedy Night" au SoGymnase — le PREMIER spectacle régulier de stand-up en anglais à Paris.',
      bioEs:'Neoyorquino que se enamoró de una francesa. Creó "New York Comedy Night" en SoGymnase — el PRIMER show regular de stand-up en inglés en París.' },
    { id:'paul', name:'Paul Taylor', title:'The Breakout', emoji:'🇬🇧',
      instagram:'https://www.instagram.com/paul_taylor_uk/',
      wikipedia:'https://en.wikipedia.org/wiki/Paul_Taylor_(comedian)',
      youtube:'https://www.youtube.com/@paultaylorcomedy',
      bio:'British comedian who moved to Paris in 2009 and got his start performing at French Fried Comedy Night, hosted by Robert Hoehn. His 2016 "La Bise" video — produced and directed by Robert — went viral with 3M+ views, leading Canal+ to give him "What The Fuck France," the first English-language show on French TV. His #Franglais, "So British", and "Bisoubye x" tours sold out across France. 1.5M+ followers across platforms.',
      bioFr:'Humoriste britannique installé à Paris depuis 2009. Sa vidéo "La Bise" est devenue virale en 2016. Canal+ lui a confié "What The Fuck France".',
      bioEs:'Comediante británico que se mudó a París en 2009. Su video "La Bise" se volvió viral en 2016 con más de 3M de vistas.' },
    { id:'sarah', name:'Sarah Donnelly', title:'The Queen', emoji:'👑',
      instagram:'https://www.instagram.com/sarahdonnellycomedian/',
      bio:'American comedian who\'s been in Paris 12+ years. She opened for Jerry Seinfeld, toured with Gad Elmaleh, and regularly performs at Théâtre BO Saint-Martin. Her special "The Only American in Paris" is on YouTube. A pillar of the Paris English comedy scene.',
      bioFr:'Humoriste américaine installée à Paris depuis plus de 12 ans. Elle a fait la première partie de Jerry Seinfeld et tourné avec Gad Elmaleh.',
      bioEs:'Comediante estadounidense en París desde hace más de 12 años. Abrió para Jerry Seinfeld y giró con Gad Elmaleh.' },
    { id:'robert', name:'Robert Hoehn', title:'Early Builder', emoji:'🍟',
      instagram:'https://www.instagram.com/Robertlericain/',
      bio:'American bilingual comedian and one of the early builders of the Paris English-language comedy scene. He launched French Fried Comedy Night in 2013 at Paname Art Café, helped give Paul Taylor one of his first regular stages, and produced and directed "La Bise" — the viral video that helped map the scene for a wider audience. He belongs in the timeline and listings as a key historical reference point.',
      bioFr:'Humoriste américain bilingue qui a fondé French Fried Comedy Night en 2013 au Paname Art Café — le plus ancien spectacle de stand-up en anglais encore en activité à Paris. Il a donné à Paul Taylor sa première scène régulière et a produit et réalisé \"La Bise\". Maintenant au Velvet Bar (43 Rue Saint-Honoré, 1er) chaque mercredi.',
      bioEs:'Comediante estadounidense bilingüe y uno de los primeros constructores de la escena anglófona en París. Lanzó French Fried Comedy Night en 2013 en Paname Art Café, dio a Paul Taylor uno de sus primeros escenarios regulares y produjo/dirigió "La Bise". Aparece aquí como referencia histórica importante.' },
    { id:'tamer', name:'Tamer Kattan', title:'NY to Paris', emoji:'🌍',
      instagram:'https://www.instagram.com/tamerkat/',
      bio:'New York comedian who made Paris his second home. 159K+ followers on social media. Regular collaborator with Robert Hoehn and a favorite on the Paris English-language comedy circuit.',
      bioFr:'Humoriste new-yorkais qui a fait de Paris sa deuxième maison. Plus de 159K abonnés sur les réseaux sociaux.',
      bioEs:'Comediante neoyorquino que hizo de París su segundo hogar. Más de 159K seguidores en redes sociales.' },
    { id:'noman', name:'Noman Hosni', title:'French Star', emoji:'🇫🇷',
      instagram:'https://www.instagram.com/nomanhosni/',
      bio:'One of France\'s biggest comedy stars who bridges the French and English comedy worlds. Regular performer at English-language shows in Paris, proving that great comedy transcends language barriers.',
      bioFr:'L\'une des plus grandes stars de la comédie française qui fait le pont entre les mondes de l\'humour français et anglais.',
      bioEs:'Una de las mayores estrellas de la comedia francesa que conecta los mundos del humor francés e inglés.' },
    { id:'tania', name:'Tania Dutel', title:'Rising Star', emoji:'✨',
      instagram:'https://www.instagram.com/taniadutel/',
      bio:'French comedian who performs brilliantly in both French and English. Known for her sharp observational humor and fearless stage presence. A regular at English-language shows in Paris and proof that the scene is truly bilingual.',
      bioFr:'Humoriste française qui brille en français comme en anglais. Connue pour son humour d\'observation et sa présence scénique.',
      bioEs:'Comediante francesa que brilla en francés e inglés. Conocida por su humor observacional y presencia escénica.' },
    { id:'gad', name:'Gad Elmaleh', title:'The Bridge', emoji:'🌉',
      instagram:'https://www.instagram.com/gadelmaleh/',
      bio:'French comedy legend who crossed over to perform in English, doing sets in New York and appearing on major US platforms. He bridged French and American comedy, proving the two worlds could connect. Toured with Sarah Donnelly.',
      bioFr:'Légende de l\'humour français qui a traversé l\'Atlantique pour se produire en anglais à New York.',
      bioEs:'Leyenda de la comedia francesa que cruzó al inglés, actuando en Nueva York y plataformas estadounidenses.' }
];

const TIMELINE = [
    { year:'~2004', title:'The Seed', text:'Sebastian Marx arrives from New York, falls in love with a French woman, and moves to Toulouse. He doesn\'t know it yet, but he\'s about to change Paris comedy forever.' },
    { year:'2010', title:'Ground Zero', text:'Seb Marx starts doing stand-up in French in Paris. He creates "New York Comedy Night" at SoGymnase — the FIRST regular English stand-up show in the city. This is where it all begins.' },
    { year:'2012', title:'TV Breakthrough', text:'Seb appears on Jamel Comedy Club on Canal+ — massive national exposure. Gets a radio gig on RTL with Stéphane Bern. English-language comedy in Paris is suddenly visible.' },
    { year:'2013', title:'New Voices', text:'Paul Taylor (British, moved to Paris in 2009) starts doing stand-up. Same year, Seb Marx gets a France Inter radio slot. The scene is growing.' },
    { year:'~2014', title:'Sarah Arrives', text:'Sarah Donnelly, American comedian in Paris for years, builds her career. She\'ll go on to open for Jerry Seinfeld, tour with Gad Elmaleh, and become one of Paris\'s most respected English-language comics.' },
    { year:'2016', title:'Viral Explosion', text:'Paul Taylor\'s "La Bise" video — goes viral with 3M+ views. Canal+ gives Taylor "What The Fuck France," the first English-language show on French TV. English comedy in Paris goes from underground to mainstream, with French Fried as one of the key launchpads.' },
    { year:'2016–2019', title:'The Franglais Era', text:'Paul Taylor\'s #Franglais tour sells out venues across France. French Fried Comedy Night launches at Paname Art Café, then moves to Velvet Bar — becoming the weekly Wednesday institution.' },
    { year:'2013', title:'French Fried is Born', text:'French Fried Comedy Night launches at Paname Art Café — the bilingual comedy show that would become the longest-running English stand-up night in Paris. A young Paul Taylor is among the early comics to perform there. The scene now has a weekly home.' },
    { year:'2020–2023', title:'The Pandemic & Comeback', text:'Like every live venue, Paris comedy takes a hit. But the scene bounces back stronger. French Fried Comedy Night survives and evolves.' },
    { year:'~2024', title:'FFCN Moves to Velvet Bar', text:'French Fried Comedy Night moves to Velvet Bar (43 Rue Saint-Honoré, 75001 Paris, near Châtelet) — a more intimate venue in central Paris that becomes the new home of Wednesday night comedy. Now the oldest continuously running English stand-up comedy show in Paris.' },
    { year:'2019–2024', title:'The Growth', text:'Paul Taylor\'s "So British" and "Bisoubye x" tours continue selling out. Sarah Donnelly releases "The Only American in Paris" special on YouTube. More English comedy nights keep appearing.' },
    { year:'2024–2025', title:'The Explosion', text:'The scene explodes. Multiple weekly English shows across Paris. What started as one guy from New York at SoGymnase grows into a citywide discovery engine for tourists, expats, and locals — and sets up the verified 30-show, 23-venue scene Paris has today.' },
    { year:'2026', title:'The Golden Age', text:'{showCount} verified weekly English-language shows across {venueCount} current venues. Wednesday nights at Velvet Bar anchor the scene with a three-show stack: open mic, showcase, and the flagship bilingual French Fried Comedy Night. From one guy with a mic at Paname in 2013 to a full discovery engine with paid listings, bilingual headliners, and tourists actively booking comedy in Paris — the scene has become one of Europe\'s strongest English-language live-comedy hubs.' }
];

/* Untranslatable words — bilingual comedy content, rotates on each visit */
const UNTRANSLATABLE = [
    { word:'Dépaysement', lang:'French', emoji:'🌍',
      literal:'De-countrified',
      definition:'The disorientation you feel when you\'re in a foreign country — not homesickness exactly, just the sense that your normal rules no longer apply.',
      punchline:'Americans in Paris experience this when they realize the waiter isn\'t being rude. That\'s just his face.' },
    { word:'Flâner', lang:'French', emoji:'🚶',
      literal:'To stroll without purpose',
      definition:'To wander the city with no destination, no phone out, observing everything. A respected pastime. A lifestyle, actually.',
      punchline:'In America we have a word for this too. It\'s "lost."' },
    { word:'Corny', lang:'English', emoji:'🌽',
      literal:'Like corn. (Unhelpful.)',
      definition:'Embarrassingly sentimental or old-fashioned in a way that is somehow both sincere and cringeworthy at the same time.',
      punchline:'The closest French word is *ringard*, which means dated. But *corny* is not dated — it\'s timeless. It\'s a Tim McGraw song at a wedding. It\'s *forever.*' },
    { word:'Ringard', lang:'French', emoji:'🧥',
      literal:'Outdated / passé',
      definition:'A thing, joke, style, or person that feels old-fashioned in a deeply uncool way. Not nostalgic-cool. Just... expired.',
      punchline:'People say it translates to *corny*, but that\'s incomplete. *Corny* can still be lovable. *Ringard* is when the room votes to move on.' },
    { word:'La Bise', lang:'French', emoji:'💋',
      literal:'The kiss',
      definition:'The obligatory cheek-kiss greeting between acquaintances, colleagues, strangers, and people you\'ve met once at a party three years ago.',
      punchline:'One kiss? Two? Three? Four? It depends on the region. Nobody tells you the rules. You just lean in and hope for the best.' },
    { word:'Awkward', lang:'English', emoji:'😬',
      literal:'Clumsy. (Also unhelpful.)',
      definition:'The specific social discomfort of a situation that is uncomfortable but not embarrassing enough to warrant leaving — you just have to sit in it.',
      punchline:'The French word is *gêné*, meaning embarrassed. But awkward is pre-embarrassed. It\'s the loading screen before embarrassment.' },
    { word:'Gêné', lang:'French', emoji:'🫣',
      literal:'Embarrassed / self-conscious',
      definition:'That feeling when you suddenly become very aware of yourself in a social moment — your hands, your face, your whole existence.',
      punchline:'It gets translated as *awkward*, but that misses the sequence: awkward is before impact. *Gêné* is after impact.' },
    { word:'Terroir', lang:'French', emoji:'🍷',
      literal:'Earth / soil',
      definition:'The complete natural environment in which a wine is produced — soil, climate, geography — and its specific taste as a result. Used for wine, coffee, cheese.',
      punchline:'Americans use this word now too, mostly wrong, mostly about craft beer.' },
    { word:'Serendipity', lang:'English', emoji:'✨',
      literal:'A made-up word from a Persian fairy tale (really)',
      definition:'A happy accident. Finding something wonderful without looking for it.',
      punchline:'The French have *par hasard* — "by chance" — which is technically accurate and completely kills the magic.' },
    { word:'Déguster', lang:'French', emoji:'🍽️',
      literal:'To taste / to savour',
      definition:'To eat or drink something slowly and with full attention, appreciating every element. Not just eating. *Experiencing.*',
      punchline:'The English equivalent is "eating slowly," which sounds like a medical symptom.' },
    { word:'Whatever', lang:'English', emoji:'🤷',
      literal:'Literally: what ever. (Still unhelpful.)',
      definition:'A declaration of total indifference — dismissing a topic, a person, or an entire conversation with a single word. It ends debates. It ends relationships. It ends decades.',
      punchline:'French people are *never* indifferent. They have strong opinions about everything, including having no opinion. *Whatever* has no French equivalent — because the French always care.' }
];

const COMEDY_QUOTES = [
    { text:'"The French think Americans are funny. Americans think the French are funny. I\'m here to prove them both right."', author:'Robert Hoehn' },
    { text:'"I moved to Paris for love. I stayed for the comedy."', author:'Sebastian Marx' },
    { text:'"La bise... how many? Two? Three? Four? Nobody knows. Not even the French."', author:'Paul Taylor' },
    { text:'"If you can make a French person laugh, you can do anything."', author:'Anonymous Paris Comic' },
    { text:'"Paris is the only city where your set can bomb in two languages simultaneously."', author:'FFCN Wisdom' },
    { text:'"Comedy is the universal language. Well, comedy and miming. But miming doesn\'t sell tickets."', author:'Paris Comedy' },
    { text:'"Best pancake of my life… still only second best day in France. First was learning my name means boobies."', author:'Robert Hoehn' },
    { text:'"People ask me if I\'m more American or more French now. The answer depends on whether the waiter just brought me the wrong order."', author:'Robert Hoehn' },
    { text:'"My brain now thinks in both French and English at the same time. The result is neither language — just a kind of anxious fog with a baguette in it."', author:'Robert Hoehn' },
    { text:'"There\'s no good French word for \'corny.\' Ringard is close but it\'s more dated. Corny is... corny. You know?"', author:'Paris Comedy Scene' },
    { text:'"The French word for awkward is gêné — which means embarrassed. But awkward is not embarrassed. Awkward is when the embarrassment hasn\'t landed yet."', author:'FFCN Wisdom' }
];

const TESTIMONIALS = [
    { text:'Best Wednesday night in Paris. Three shows, zero regrets.', author:'Laura M.', source:'Google Reviews', stars:5 },
    { text:'I didn\'t know I needed bilingual comedy in my life until FFCN. Now I\'m addicted.', author:'Thomas K.', source:'Eventbrite', stars:5 },
    { text:'Brought my French friends who barely speak English. They laughed harder than me.', author:'Mike R.', source:'TripAdvisor', stars:5 },
    { text:'The open mic is genuinely good — not just \"open mic good.\" Real talent every week.', author:'Sophie L.', source:'Google Reviews', stars:5 },
    { text:'Paname on a Tuesday is the cheat code for having a great week.', author:'David P.', source:'Instagram', stars:5 },
    { text:'We were only in Paris for 4 days. This was the highlight. Absolutely packed room, incredible energy.', author:'James & Clara', source:'TripAdvisor', stars:5 },
    { text:'I\'ve lived in Paris for 6 years and I don\'t know why it took me this long to find FFCN. Now it\'s every Wednesday.', author:'Nadia F.', source:'Google Reviews', stars:5 },
    { text:'Booked the team for our company evening — 40 people, mixed French/English. Everyone was in tears laughing. Will do it again.', author:'Olivier B.', source:'Email', stars:5 },
    { text:'Got on the open mic on a whim. Robert runs the tightest room in Paris. You can feel the respect for the craft.', author:'Kenji M.', source:'Instagram', stars:5 }
];

/* French shows — fallback for days with no English comedy. These are NOT our shows. */
const FRENCH_SHOWS = [
    { name:'Velvet Bar Comedy (FR)', venueName:'Velvet Bar', day:'Thursday', time:'20:30', emoji:'🇫🇷', description:'Stand-up en français au Velvet Bar.', paid:false },
    { name:'Paname Comedy (FR)', venueName:'Paname Art Café', day:'Monday', time:'20:00', emoji:'🇫🇷', description:'Scène ouverte et showcase au Paname.', paid:false },
    { name:'Jamel Comedy Club', venueName:'Jamel Comedy Club', day:'Saturday', time:'21:00', emoji:'🇫🇷', description:'Le plus célèbre comedy club de Paris.', paid:false },
    { name:'Le Point Virgule', venueName:'Le Point Virgule', day:'Friday', time:'20:00', emoji:'🇫🇷', description:'One-man shows et stand-up au cœur du Marais.', paid:false },
    { name:'Comedy Club Paris', venueName:'Comedy Club Paris', day:'Sunday', time:'20:00', emoji:'🇫🇷', description:'Stand-up en français le dimanche soir.', paid:false }
];

const NOTABLE_VISITORS = [
    'Dave Chappelle', 'Trevor Noah', 'Hannah Gadsby', 'Nish Kumar', 'Katherine Ryan',
    'Eddie Izzard', 'Russell Peters', 'Vir Das', 'Daniel Sloss', 'Phil Wang'
];

/* Translations */
const TRANSLATIONS = {
    en: {
        nav: { home:'Home', shows:'Shows', calendar:'Calendar', history:'History', venues:'Venues', book:'Book a Show', about:'About' },
        hero: { info:'🎟️ Reserve your spot · 🍺 One drink minimum · 🎩 Pass the hat for the performers', tag:'🇫🇷 Bilingual comedy every week in Paris', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'The Home of English-Language Comedy in Paris', desc:'Live stand-up in French & English. Open mics, showcases, and the legendary French Fried Comedy Night. Every week across Paris.', cta:'🎟️ Reserve Your Spot', browse:'Browse Shows' },
        stats: { shows:'{showCount}', showsLabel:'Weekly Shows', venues:'{venueCount}', venuesLabel:'Venues', bilingual:'FR+EN', bilingualLabel:'Bilingual', est:'~2010', estLabel:'Est.' },
        sections: { featuredShows:'This Week\'s Shows', allShows:'All Shows', showsSub:'Stand-up, open mics — every week at venues across Paris', calendar:'Calendar', calendarSub:'Tap a day to see what\'s on', venues:'Venue Map', venuesSub:'Where the comedy happens in Paris', bookShow:'Book a Show', bookCTA:'Book a Private Show', newsletter:'Get Show Alerts', newsletterSub:'Weekly email with upcoming shows. No spam, just laughs.', subscribe:'Subscribe', quoteTitle:'Comedy Quote of the Week', videoTitle:'Latest Clips', supportTitle:'Support the Scene', testimonials:'What People Say' },
        filters: { all:'All', standup:'Stand-Up', openmic:'Open Mic' },
        footer: { copyright:'© 2026 Paris Comedy · Made with 🍟 in Paris', tagline:'The Home of English-Language Comedy in Paris. Est. ~2010.', contact:'Contact', legal:'Legal', privacy:'Privacy', terms:'Terms', pages:'Pages', comedians:'For Comedians', contactForm:'Contact form' },
        book: { perform:'Want to Perform?', performDesc:'Got 5 minutes of material and zero fear? Email us to get on a show. We run open mics every Wednesday — all levels welcome.', corporate:'Book a Comedian', corporateDesc:'Corporate events, private parties, festivals, team-building — we\'ll match you with the perfect comic. Bilingual performers available.', list:'List Your Show', listDesc:'Running an English comedy night in Paris? Get featured on pariscomedy.com for €1/month.', contact:'Get in Touch', name:'Your Name', email:'Email', message:'Message', send:'Send Message' },
        about: { title:'About Paris Comedy', what:'What is this?', team:'Who runs this?', teamDesc:'Paris Comedy is run by a team of comedy lovers who believe English-language comedy in Paris deserves a proper home on the internet.', contactUs:'Contact Us' },
        history: { title:'The History of English Comedy in Paris', intro:'From one New Yorker with a dream to {showCount} verified weekly shows — how Paris became one of Europe\'s greatest English-language comedy cities.', keyPlayers:'Key Players', notableVisitors:'Notable Visitors', visitorsIntro:'International comedians who\'ve performed on Paris stages:', stages:'Stages of Growth' }
    },
    fr: {
        nav: { home:'Accueil', shows:'Spectacles', calendar:'Calendrier', history:'Histoire', venues:'Salles', book:'Réserver un spectacle', about:'À propos' },
        hero: { info:'🎟️ Réservez votre place · 🍺 Une consommation minimum · 🎩 Le chapeau pour les artistes', tag:'🇫🇷 Stand-up bilingue chaque semaine à Paris', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'Le guide du stand-up anglophone à Paris', desc:'Stand-up en français et en anglais. Open mics, plateaux et la légendaire French Fried Comedy Night. Chaque semaine à Paris.', cta:'🎟️ Réserver votre place', browse:'Voir les spectacles' },
        stats: { shows:'{showCount}', showsLabel:'Spectacles/sem', venues:'{venueCount}', venuesLabel:'Salles', bilingual:'FR+EN', bilingualLabel:'Bilingue', est:'~2010', estLabel:'Depuis' },
        sections: { featuredShows:'À l\'Affiche Cette Semaine', allShows:'Tous les Spectacles', showsSub:'Stand-up, scènes ouvertes — chaque semaine dans les salles de Paris', calendar:'Calendrier', calendarSub:'Cliquez sur un jour pour voir le programme', venues:'Carte des Salles', venuesSub:'Où se passe la comédie à Paris', bookShow:'Réserver un Spectacle', bookCTA:'Réserver un Spectacle Privé', newsletter:'Recevez les Alertes', newsletterSub:'Un email hebdo avec les prochains spectacles. Pas de spam, que des rires.', subscribe:'S\'abonner', quoteTitle:'Citation de la Semaine', videoTitle:'Derniers Clips', supportTitle:'Soutenez la Scène', testimonials:'Ce Qu\'on Dit' },
        filters: { all:'Tout', standup:'Stand-Up', openmic:'Scène Ouverte' },
        footer: { copyright:'© 2026 Paris Comedy · Fait à Paris', tagline:'Le guide du stand-up anglophone à Paris. Depuis ~2010.', contact:'Contact', legal:'Mentions légales', privacy:'Confidentialité', terms:'CGU', pages:'Pages', comedians:'Pour les humoristes', contactForm:'Formulaire de contact' },
        book: { perform:'Vous Voulez Monter sur Scène ?', performDesc:'Vous avez 5 minutes de matériel et zéro peur ? Écrivez-nous pour être programmé. Nous organisons des scènes ouvertes chaque mercredi — tous niveaux bienvenus.', corporate:'Engager un Humoriste', corporateDesc:'Événements d\'entreprise, soirées privées, festivals, team-building — on vous trouve le comique parfait. Artistes bilingues disponibles.', list:'Référencer Votre Spectacle', listDesc:'Vous organisez un spectacle de comédie en anglais à Paris ? Apparaissez sur pariscomedy.com pour 1€/mois.', contact:'Contactez-nous', name:'Votre Nom', email:'Email', message:'Message', send:'Envoyer' },
        about: { title:'À Propos de Paris Comedy', what:'C\'est quoi ?', team:'Qui gère ça ?', teamDesc:'Paris Comedy est géré par une équipe de passionnés de comédie qui pensent que l\'humour anglophone à Paris mérite une vraie maison sur internet.', contactUs:'Nous Contacter' },
        history: { title:'L\'Histoire de la Comédie Anglaise à Paris', intro:'D\'un New-Yorkais avec un rêve à {showCount} spectacles hebdomadaires vérifiés — comment Paris est devenue l\'une des grandes capitales européennes de la comédie en anglais.', keyPlayers:'Les Acteurs Clés', notableVisitors:'Visiteurs Notables', visitorsIntro:'Humoristes internationaux qui se sont produits sur les scènes parisiennes :', stages:'Étapes de la scène' }
    },
    es: {
        nav: { home:'Inicio', shows:'Shows', calendar:'Calendario', history:'Historia', venues:'Locales', book:'Reservar', about:'Acerca de' },
        hero: { info:'🎟️ Reserva tu lugar · 🍺 Una consumición mínima · 🎩 El sombrero para los artistas', tag:'🇫🇷 Comedia bilingüe cada semana en París', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'El Hogar de la Comedia en Inglés en París', desc:'Stand-up en francés e inglés. Micros abiertos, showcases y la legendaria French Fried Comedy Night. Cada semana en París.', cta:'🎟️ Reserva Tu Lugar', browse:'Ver Shows' },

        stats: { shows:'{showCount}', showsLabel:'Shows/sem', venues:'{venueCount}', venuesLabel:'Locales', bilingual:'FR+EN', bilingualLabel:'Bilingüe', est:'~2010', estLabel:'Desde' },
        sections: { featuredShows:'Shows de Esta Semana', allShows:'Todos los Shows', showsSub:'Stand-up, micros abiertos — cada semana en locales de París', calendar:'Calendario', calendarSub:'Toca un día para ver la programación', venues:'Mapa de Locales', venuesSub:'Dónde pasa la comedia en París', bookShow:'Reservar un Show', bookCTA:'Reservar un Show Privado', newsletter:'Recibe Alertas', newsletterSub:'Email semanal con los próximos shows. Sin spam, solo risas.', subscribe:'Suscribirse', quoteTitle:'Frase de la Semana', videoTitle:'Últimos Clips', supportTitle:'Apoya la Escena', testimonials:'Lo Que Dicen' },
        filters: { all:'Todo', standup:'Stand-Up', openmic:'Micro Abierto' },
        footer: { copyright:'© 2026 Paris Comedy · Made with 🍟 in Paris', tagline:'El Hogar de la Comedia en Inglés en París. Desde ~2010.', contact:'Contacto', legal:'Legal', privacy:'Privacidad', terms:'Términos', pages:'Páginas', comedians:'Para cómicos', contactForm:'Formulario de contacto' },
        book: { perform:'¿Quieres Actuar?', performDesc:'¿Tienes 5 minutos de material y cero miedo? Escríbenos para subir al escenario. Organizamos open mics cada miércoles — todos los niveles son bienvenidos.', corporate:'Contrata un Comediante', corporateDesc:'Eventos corporativos, fiestas privadas, festivales, team-building — te encontramos al cómico perfecto. Artistas bilingües disponibles.', list:'Lista Tu Show', listDesc:'¿Organizas una noche de comedia en inglés en París? Aparece en pariscomedy.com por 1€/mes.', contact:'Contáctanos', name:'Tu Nombre', email:'Email', message:'Mensaje', send:'Enviar' },
        about: { title:'Sobre Paris Comedy', what:'¿Qué es esto?', team:'¿Quién lo gestiona?', teamDesc:'Paris Comedy está gestionado por un equipo de amantes de la comedia que creen que la comedia en inglés en París merece un hogar propio en internet.', contactUs:'Contáctanos' },
        history: { title:'La Historia de la Comedia en Inglés en París', intro:'De un neoyorquino con un sueño a {showCount} shows semanales verificados — cómo París se convirtió en una de las grandes ciudades europeas de la comedia en inglés.', keyPlayers:'Protagonistas', notableVisitors:'Visitantes Notables', visitorsIntro:'Comediantes internacionales que han actuado en escenarios de París:', stages:'Etapas del crecimiento' }
    },
    de: {
        nav: { home:'Startseite', shows:'Shows', calendar:'Kalender', history:'Geschichte', venues:'Veranstaltungsorte', book:'Show buchen', about:'Über uns' },
        hero: { info:'🎟️ Platz reservieren · 🍺 Ein Getränk Minimum · 🎩 Der Hut für die Künstler', tag:'🇫🇷 Zweisprachige Comedy jede Woche in Paris', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'Das Zuhause der englischsprachigen Comedy in Paris', desc:'Live-Stand-up auf Französisch & Englisch. Open Mics, Showcases und die legendäre French Fried Comedy Night. Jede Woche in Paris.', cta:'🎟️ Platz reservieren', browse:'Shows ansehen' },
        stats: { shows:'{showCount}', showsLabel:'Wöchentliche Shows', venues:'{venueCount}', venuesLabel:'Venues', bilingual:'FR+EN', bilingualLabel:'Zweisprachig', est:'~2010', estLabel:'Seit' },
        sections: { featuredShows:'Shows Diese Woche', allShows:'Alle Shows', showsSub:'Stand-up, Open Mics — jede Woche in Pariser Venues', calendar:'Kalender', calendarSub:'Tippen Sie auf einen Tag', venues:'Venue-Karte', venuesSub:'Wo die Comedy in Paris stattfindet', bookShow:'Show buchen', bookCTA:'Private Show buchen', newsletter:'Show-Benachrichtigungen', newsletterSub:'Wöchentliche E-Mail mit kommenden Shows. Kein Spam, nur Lacher.', subscribe:'Abonnieren', quoteTitle:'Comedy-Zitat der Woche', videoTitle:'Neueste Clips', supportTitle:'Die Szene unterstützen', testimonials:'Was die Leute sagen' },
        filters: { all:'Alle', standup:'Stand-Up', openmic:'Open Mic' },
        footer: { copyright:'© 2026 Paris Comedy · Made with 🍟 in Paris', tagline:'Das Zuhause der englischsprachigen Comedy in Paris. Seit ~2010.', contact:'Kontakt', legal:'Impressum', privacy:'Datenschutz', terms:'AGB', pages:'Seiten', comedians:'Für Comedians', contactForm:'Kontaktformular' },
        book: { perform:'Möchten Sie auftreten?', performDesc:'5 Minuten Material und keine Angst? Schreiben Sie uns, um in einer Show zu sein. Wir veranstalten jeden Mittwoch Open Mics — alle Niveaus willkommen.', corporate:'Einen Comedian buchen', corporateDesc:'Firmenveranstaltungen, Privatpartys, Festivals, Teambuilding — wir finden den perfekten Comedian. Zweisprachige Künstler verfügbar.', list:'Ihre Show eintragen', listDesc:'Organisieren Sie einen englischen Comedy-Abend in Paris? Für 1€/Monat auf pariscomedy.com erscheinen.', contact:'Kontakt aufnehmen', name:'Ihr Name', email:'E-Mail', message:'Nachricht', send:'Nachricht senden' },
        about: { title:'Über Paris Comedy', what:'Was ist das?', team:'Wer macht das?', teamDesc:'Paris Comedy wird von einem Team von Comedy-Liebhabern betrieben, die glauben, dass englischsprachige Comedy in Paris ein richtiges Zuhause im Internet verdient.', contactUs:'Kontaktieren Sie uns' },
        history: { title:'Die Geschichte der englischen Comedy in Paris', intro:'Von einem New Yorker mit einem Traum zu 30 verifizierten wöchentlichen Shows — wie Paris eine der größten englischsprachigen Comedy-Städte Europas wurde.', keyPlayers:'Schlüsselfiguren', notableVisitors:'Bekannte Besucher', visitorsIntro:'Internationale Comedians, die auf Pariser Bühnen aufgetreten sind:', stages:'Wachstumsphasen' }
    },
    ja: {
        nav: { home:'ホーム', shows:'ショー', calendar:'カレンダー', history:'歴史', venues:'会場', book:'ショーを予約', about:'概要' },
        hero: { info:'🎟️ 席を予約する · 🍺 ドリンク1杯必須 · 🎩 パフォーマーへのカンパ', tag:'🇫🇷 毎週パリでバイリンガルコメディ', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'パリの英語コメディの拠点', desc:'フランス語と英語のライブスタンドアップ。オープンマイク、ショーケース、伝説のFrench Fried Comedy Night。毎週パリで開催。', cta:'🎟️ 席を予約する', browse:'ショーを見る' },
        stats: { shows:'{showCount}', showsLabel:'毎週のショー', venues:'{venueCount}', venuesLabel:'会場', bilingual:'FR+EN', bilingualLabel:'バイリンガル', est:'~2010', estLabel:'創設' },
        sections: { featuredShows:'今週のショー', allShows:'全ショー', showsSub:'スタンドアップ、オープンマイク — 毎週パリの会場で', calendar:'カレンダー', calendarSub:'日付をタップして詳細を見る', venues:'会場マップ', venuesSub:'パリのコメディ会場', bookShow:'ショーを予約', bookCTA:'プライベートショーを予約', newsletter:'ショー通知を受け取る', newsletterSub:'毎週のショー情報メール。スパムなし、笑いだけ。', subscribe:'登録', quoteTitle:'今週のコメディ名言', videoTitle:'最新クリップ', supportTitle:'シーンを応援する', testimonials:'みんなの声' },
        filters: { all:'すべて', standup:'スタンドアップ', openmic:'オープンマイク' },
        footer: { copyright:'© 2026 Paris Comedy · Made with 🍟 in Paris', tagline:'パリの英語コメディの拠点。~2010年創設。', contact:'お問い合わせ', legal:'法的情報', privacy:'プライバシー', terms:'利用規約', pages:'ページ', comedians:'コメディアン向け', contactForm:'お問い合わせフォーム' },
        book: { perform:'出演したいですか？', performDesc:'5分のネタとゼロの恐怖心があれば、メールをください。毎週水曜日にオープンマイクを開催しています — レベル不問。', corporate:'コメディアンを予約', corporateDesc:'企業イベント、プライベートパーティー、フェスティバル、チームビルディング — ぴったりのコメディアンをお探しします。バイリンガルのパフォーマーも対応可能。', list:'ショーを掲載', listDesc:'パリで英語のコメディナイトを開催中？月1€でpariscomedy.comに掲載。', contact:'お問い合わせ', name:'お名前', email:'メール', message:'メッセージ', send:'送信' },
        about: { title:'Paris Comedyについて', what:'これは何ですか？', team:'誰が運営していますか？', teamDesc:'Paris Comedyは、パリの英語コメディがインターネット上の本格的な拠点にふさわしいと信じるコメディ愛好家のチームが運営しています。', contactUs:'お問い合わせ' },
        history: { title:'パリにおける英語コメディの歴史', intro:'夢を持つ一人のニューヨーカーから週{showCount}本の検証済みショーへ — パリがヨーロッパ最大級の英語コメディ都市の一つになるまで。', keyPlayers:'主要人物', notableVisitors:'著名な訪問者', visitorsIntro:'パリのステージで公演した国際的なコメディアン：', stages:'成長の段階' }
    },
    zh: {
        nav: { home:'首页', shows:'演出', calendar:'日历', history:'历史', venues:'场地', book:'预订演出', about:'关于' },
        hero: { info:'🎟️ 预订座位 · 🍺 最低消费一杯饮品 · 🎩 向演员打赏', tag:'🇫🇷 每周在巴黎的双语喜剧', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'巴黎英语喜剧之家', desc:'法语和英语现场脱口秀。开放麦、展演和传奇的French Fried Comedy Night。每周在巴黎举办。', cta:'🎟️ 预订座位', browse:'浏览演出' },
        stats: { shows:'{showCount}', showsLabel:'每周演出', venues:'{venueCount}', venuesLabel:'场地', bilingual:'FR+EN', bilingualLabel:'双语', est:'~2010', estLabel:'创立' },
        sections: { featuredShows:'本周演出', allShows:'所有演出', showsSub:'脱口秀、开放麦 — 每周在巴黎各场地', calendar:'日历', calendarSub:'点击日期查看详情', venues:'场地地图', venuesSub:'巴黎喜剧演出场地', bookShow:'预订演出', bookCTA:'预订私人演出', newsletter:'获取演出提醒', newsletterSub:'每周演出邮件。不发垃圾邮件，只有欢笑。', subscribe:'订阅', quoteTitle:'本周喜剧名言', videoTitle:'最新片段', supportTitle:'支持喜剧圈', testimonials:'观众评价' },
        filters: { all:'全部', standup:'脱口秀', openmic:'开放麦' },
        footer: { copyright:'© 2026 Paris Comedy · Made with 🍟 in Paris', tagline:'巴黎英语喜剧之家。创立于约 2010 年。', contact:'联系我们', legal:'法律信息', privacy:'隐私', terms:'条款', pages:'页面', comedians:'演员专区', contactForm:'联系表单' },
        book: { perform:'想上台表演？', performDesc:'有5分钟的段子并且毫无恐惧？发邮件给我们参加演出。我们每周三举办开放麦 — 欢迎所有水平。', corporate:'预约喜剧演员', corporateDesc:'企业活动、私人派对、节日演出、团建 — 我们为您匹配完美的喜剧演员。提供双语表演者。', list:'发布您的演出', listDesc:'在巴黎举办英语喜剧之夜？每月1欧元即可在pariscomedy.com上展示。', contact:'联系我们', name:'您的姓名', email:'电子邮件', message:'留言', send:'发送消息' },
        about: { title:'关于 Paris Comedy', what:'这是什么？', team:'谁在运营？', teamDesc:'Paris Comedy 由一群喜剧爱好者运营，他们相信巴黎的英语喜剧值得在互联网上拥有一个真正的家。', contactUs:'联系我们' },
        history: { title:'巴黎英语喜剧史', intro:'从一个有梦想的纽约人到每周{showCount}场已核实演出 — 巴黎如何成为欧洲最重要的英语喜剧城市之一。', keyPlayers:'关键人物', notableVisitors:'著名访客', visitorsIntro:'曾在巴黎舞台上表演的国际喜剧演员：', stages:'成长阶段' }
    },
    ko: {
        nav: { home:'홈', shows:'쇼', calendar:'캘린더', history:'역사', venues:'공연장', book:'쇼 예약', about:'소개' },
        hero: { info:'🎟️ 좌석 예약 · 🍺 1인 1음료 · 🎩 공연자 팁', tag:'🇫🇷 파리에서 매주 열리는 이중언어 코미디', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'파리 영어 코미디의 홈', desc:'프랑스어와 영어로 즐기는 라이브 스탠드업. 오픈 마이크, 쇼케이스, 그리고 전설적인 French Fried Comedy Night까지. 매주 파리에서 만나요.', cta:'🎟️ 좌석 예약', browse:'쇼 둘러보기' },
        stats: { shows:'{showCount}', showsLabel:'주간 쇼', venues:'{venueCount}', venuesLabel:'공연장', bilingual:'FR+EN', bilingualLabel:'이중언어', est:'~2010', estLabel:'시작' },
        sections: { featuredShows:'이번 주 추천 쇼', allShows:'전체 쇼', showsSub:'스탠드업과 오픈 마이크 — 매주 파리 곳곳에서', calendar:'캘린더', calendarSub:'날짜를 눌러 공연 확인', venues:'공연장 지도', venuesSub:'파리에서 코미디가 열리는 곳', bookShow:'쇼 예약', bookCTA:'프라이빗 쇼 문의', newsletter:'쇼 알림 받기', newsletterSub:'다가오는 쇼를 매주 이메일로 보내드립니다. 스팸 없이, 웃음만.', subscribe:'구독', quoteTitle:'이번 주 코미디 명언', videoTitle:'최신 클립', supportTitle:'씬 응원하기', testimonials:'관객 후기' },
        filters: { all:'전체', standup:'스탠드업', openmic:'오픈 마이크' },
        footer: { copyright:'© 2026 Paris Comedy · Made with 🍟 in Paris', tagline:'파리 영어 코미디의 홈. 약 2010년 시작.', contact:'문의', legal:'법적 고지', privacy:'개인정보', terms:'이용약관', pages:'페이지', comedians:'코미디언용', contactForm:'문의 폼' },
        book: { perform:'무대에 서고 싶나요?', performDesc:'5분 분량의 소재와 약간의 배짱만 있으면 됩니다. 공연 문의 메일을 보내세요. 우리는 매주 수요일 오픈 마이크를 엽니다 — 실력 무관 환영.', corporate:'코미디언 섭외', corporateDesc:'기업 행사, 프라이빗 파티, 페스티벌, 팀빌딩 — 행사에 맞는 코미디언을 연결해 드립니다. 이중언어 공연자도 가능합니다.', list:'당신의 쇼 등록', listDesc:'파리에서 영어 코미디 나이트를 운영하시나요? 월 1유로로 pariscomedy.com에 소개할 수 있습니다.', contact:'문의하기', name:'이름', email:'이메일', message:'메시지', send:'보내기' },
        about: { title:'Paris Comedy 소개', what:'이 사이트는?', team:'누가 운영하나요?', teamDesc:'Paris Comedy는 파리의 영어 코미디가 인터넷에서 제대로 된 집을 가져야 한다고 믿는 코미디 애호가들이 운영합니다.', contactUs:'문의하기' },
        history: { title:'파리 영어 코미디의 역사', intro:'꿈을 품은 한 뉴요커에서 출발해 주간 {showCount}개의 검증된 쇼까지 — 파리가 어떻게 유럽에서 가장 중요한 영어 코미디 도시 중 하나가 되었는지.', keyPlayers:'핵심 인물', notableVisitors:'주목할 방문자', visitorsIntro:'파리 무대에 섰던 국제 코미디언들:', stages:'성장의 단계' }
    },

};

const PAGE_COPY = {
  en: {
    header: { subtitle:'Perform, hire a comedian, or list your show on pariscomedy.com', title:'About Paris Comedy' },
    listing: { title:'List Your Show' },
    contact: { subtitle:'Fill in the form below or DM us on Instagram — we reply fast.' },
    faq: { title:'FAQ' },
    book: {
      listingIntro:'Running an English comedy night in Paris? Get featured on pariscomedy.com — the #1 guide to English comedy in Paris.',
      performCta:'📧 Get in Touch',
      corporateCta:'📧 Get a Quote',
      basic:{ title:'Basic Listing', feat1:'✅ Show name & description', feat2:'✅ Venue & schedule in calendar', feat3:'❌ No ticket link', cta:'Get Started' },
      pro:{ badge:'MOST POPULAR', title:'Pro Listing', feat1:'✅ Everything in Basic', feat2:'✅ Direct ticket/booking link', feat3:'✅ Solid card (not dashed)', feat4:'✅ Venue pin on map', feat5:'✅ We manage your email list', feat6:'✅ 1 mass email/week included', cta:'Get Pro' },
      full:{ title:'Full Service Booking', feat1:'✅ Everything in Pro', feat2:'✅ Full booking management', feat3:'✅ 1 mass email/week to YOUR list', feat4:'✅ Automated email campaigns', feat5:'✅ Show page on pariscomedy.com', feat6:'✅ Priority calendar placement', feat7:'✅ We build & send your promo emails', cta:'Go Full Service' },
      proof:{ badge:'📈 Why show-runners list here', heading:'Paris tourists and expats are already looking for comedy here.', p1:'Today\'s standup confirms booking-link health is at <strong>{bookingLinksVerified}</strong>. That means when someone lands on pariscomedy.com and clicks your show, they reach a live booking page — not a dead end. We built this site to turn discovery into reservations.', p2:'For organizers, that\'s the real pitch: high-intent traffic, clean links, and fast discovery for people searching <em>comedy in Paris tonight</em>, <em>English stand-up Paris</em>, or <em>what to do in Pigalle</em>.', stat1:'active booking links verified live', stat2:'to get your show discoverable on the guide', stat3:'bilingual positioning for tourists, expats, locals', quote:'"Wrong Language, Right Feeling" is already working as a conversion angle because it feels native to expat Paris. If your show has a clear vibe, we can package it that way too.', cta:'🚀 Get My Show Listed' },
      fringe:{ badge:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Edinburgh Fringe 2026 · Preview Season', heading:'Testing your hour before Edinburgh?<br>Paris is the perfect preview city.', desc:'Warm, bilingual, comedy-hungry crowds. FFCN has been running since 2013. We\'ll fill the room and run your promo — so you walk into Edinburgh having already worked the room.', feat1:'✅ Paris preview slot (Wed/Fri/Sat)', feat2:'✅ Eventbrite + pariscomedy.com listing', feat3:'✅ Email blast to our Paris audience', feat4:'✅ Instagram promo post included', feat5:'✅ Pro Listing €5/mo or Full Service €30/mo', cta:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Book My Preview Slot', secondary:'See the scene →' },
      sunday:{ badge:'🗓️ Sunday prime slots open now', heading:'Need a Sunday show in Paris?', desc:'Corporate brunch, private birthday, expat meetup, team offsite — we can place a bilingual comedian and handle promo/listing support so your room fills fast.', cta:'⚡ Reserve a Sunday Slot', response:'Response target: same day' },
      quickBrief:{ badge:'⚡ Fast brief starter', heading:'Don’t want to write from scratch? Pick the closest brief.', desc:'The fastest money is still private/corporate entertainment and open Sunday inventory. These buttons pre-fill the form so buyers can send a usable brief in one tap.', response:'Best for same-day quote requests', sunday:'🌞 Sunday private event', corporate:'🏢 Corporate / team event', listing:'📋 List a room or new show' },
      messagePlaceholder:'Tell us what you need...',
      formNote:'Corrections and new show suggestions are reviewed by Chuck, then added to the verified public directory once confirmed.',
      faq:{ q1:'How do I get on the open mic?', a1:'Show up to Velvet Bar on Wednesday at 19:00 and sign up. First come, first served. 5 minutes per comic.', q2:'How much does it cost to perform?', a2:'Nothing for performers. Reserve your spot, there\'s a one drink minimum, and we pass the hat at the end. We\'re in it for the laughs.', q3:'Do I need to speak French?', a3:'Nope. Our shows are in English (some are bilingual). French is a bonus, not a requirement.', q4:'Can I book a comedian for my corporate event?', a4:'Absolutely. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Book a comedian\'">Fill out the form above</a> with your event details and we\'ll match you with the right comic.', q5:'I run a comedy show in Paris. Can I get listed?', a5:'Yes! We want pariscomedy.com to be the complete guide to English comedy in Paris. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Get Listed\'">Use the form above</a> and Chuck will review the details before anything is added to the verified public directory.' }
    },
    venues: { subtitle:'23 verified comedy venues across Paris — where the laughs happen every week', mapTitle:'🗺️ Comedy Venue Map', mapSub:'23 verified English comedy spots across Paris — click any pin for show times', mapLegend:'🟣 = Featured venue with weekly shows · 🔵 = All English comedy spots', cardsTitle:'Comedy Venues in Paris', cardsSub:'Home of French Fried Comedy Night and 22 more verified English comedy spots across Paris', yourVenue:'🏠 <strong>Your venue here?</strong>', yourVenueSub:'If you host English-language comedy in Paris, we want to list you.', yourVenueCta:'Get Listed →', actions:{ map:'Open map', walk:'Directions', transit:'Transit', drive:'Drive', pending:'Exact map link needs review.' }, map:{ tba:'Shows TBA' }, other:{ title:'Other Comedy Venues in Paris', sub:'These venues host English-language comedy. Want your show featured with full booking?', cta:'Get listed', claim:'Shows not yet listed', claimCta:'claim this listing' } },
    history: { timeline:'The Timeline', introP1:'There\'s a running joke in Paris comedy: <em>"When did English stand-up start here?"</em> The answer is complicated — because for most of the 20th century, it didn\'t exist. France had its own comedy tradition. The chansonnier, the one-man show, the café-théâtre. Stand-up in the American or British sense? That was something you watched on Netflix, not something you did in a basement bar in Pigalle.', introP2:'And then a guy from New York showed up.', introP3:'This is the story of how English-language comedy in Paris went from literally nothing to one of the most vibrant live scenes in Europe — in about fifteen years.', keyPlayersSub:'The people who built the scene, one joke at a time', playerTitles:{ seb:'The Pioneer', paul:'The Breakout', sarah:'The Queen', robert:'Early Builder', tamer:'The Heavy Hitter' } },
    comedians: { nav:'For Comedians', contactNav:'Contact', title:'Paris comedy shows for comedians', subtitle:'A free reference + suggestion service. Only shows with verified recent activity stay on this page.', howTitle:'How this page works', howP1:'This is meant as a useful public reference, not a gatekeeping list. If a show has no verified activity in the last 6 months, it comes off the current directory until we can verify it again.', howP2:'If something is wrong, missing, or newly launched, send it through the Paris Comedy contact form. Chuck reviews corrections and new submissions; verified fixes get added to the public data layer, and uncertain items go into manual review instead of being guessed.', helper:'Grouped by venue · working links · show runner if known · updated from the public data layer · corrections reviewed by Chuck · paid listings available from €1', cta:'Send a correction / add a show →', footerBlurb:'Free reference page for comedians, crowds, and show runners.', pages:'Pages', needFix:'Need a fix?', sendUpdate:'Send an update', stats:'{shows} currently verified shows across {venues} venues.{latest}', addressPending:'Address being confirmed', verifiedCount:'{count} verified shows', runner:'Show runner', notConfirmed:'Not yet confirmed', verifiedVia:'Verified {date} via {source}', recently:'recently', manualReview:'manual review', openListing:'Open listing' },
    blog: { nav:'Blog', heroTag:'Comedy-only coverage for Paris', heroTitle:'The <span class="gradient-text">Paris Comedy Blog</span>', heroSub:'A practical editorial lane for people who want to find a show, understand the scene, or get on stage in Paris without digging through random posts and stale listings.', heroCta:'Browse the lane', heroShows:'See live shows', belongsTitle:'What belongs here', belongsSub:'Only comedy: shows, crowds, neighborhoods, scene context, and useful resources for performers.', audienceTag:'For audiences', audienceTitle:'Show Guides', audienceDesc:'Short guides like “best first comedy night in Paris,” neighborhood-by-neighborhood picks, or where to bring friends visiting for the weekend.', comicsTag:'For comedians', comicsTitle:'Comic Resources', comicsDesc:'Practical explainers on open mics, how rooms differ, what the Wednesday Velvet stack feels like, and how to navigate the English-language scene.', sceneTag:'Scene intel', sceneTitle:'Paris Scene Notes', sceneDesc:'Timely, audience-facing scene updates: busy weeks, venue clusters, seasonal crowd energy, and what kind of room each show attracts.', seedTitle:'Seeded first posts', seedSub:'Not a content dump — just a clean first shelf that matches the site.', workflowTitle:'Editorial workflow', workflowSub:'Small, practical, and brand-safe.', step1Title:'1. Pick a comedy question', step1Desc:'Choose something audiences or comics actually ask: where to go, what to expect, or how a room differs.', step2Title:'2. Anchor it to live pages', step2Desc:'Every post should point back to relevant show, venue, history, or comedian-resource pages already on the site.', step3Title:'3. Keep the tone local', step3Desc:'Funny, useful, and scene-aware. No internal ops talk, no system notes, no campaign jargon.', step4Title:'4. End with a real next step', step4Desc:'Reserve a show, browse a venue, or submit a correction — never a dead-end article.', explore:'Explore', forComics:'For comics', currentShows:'Current shows', getListed:'Get listed' }
  },
  fr: {
    header: { subtitle:'Montez sur scène, engagez un humoriste ou référencez votre spectacle sur pariscomedy.com', title:'À propos de Paris Comedy' },
    listing: { title:'Référencez Votre Spectacle' },
    contact: { subtitle:'Remplissez le formulaire ci-dessous ou envoyez-nous un DM sur Instagram — on répond vite.' },
    faq: { title:'FAQ' },
    book: {
      listingIntro:'Vous organisez une soirée comédie en anglais à Paris ? Apparaissez sur pariscomedy.com — le guide n°1 de la comédie anglophone à Paris.',
      performCta:'📧 Nous Contacter',
      corporateCta:'📧 Obtenir un Devis',
      basic:{ title:'Référencement de base', feat1:'✅ Nom et description du spectacle', feat2:'✅ Salle et horaire dans le calendrier', feat3:'❌ Pas de lien de réservation', cta:'Commencer' },
      pro:{ badge:'LE PLUS POPULAIRE', title:'Référencement Pro', feat1:'✅ Tout le Basic', feat2:'✅ Lien de réservation direct', feat3:'✅ Carte pleine (non tiretée)', feat4:'✅ Épingle de salle sur la carte', feat5:'✅ On gère votre liste email', feat6:'✅ 1 email de masse/semaine inclus', cta:'Passer en Pro' },
      full:{ title:'Service Complet de Réservation', feat1:'✅ Tout le Pro', feat2:'✅ Gestion complète des réservations', feat3:'✅ 1 email de masse/semaine à VOTRE liste', feat4:'✅ Campagnes email automatisées', feat5:'✅ Page spectacle sur pariscomedy.com', feat6:'✅ Priorité dans le calendrier', feat7:'✅ On crée et envoie vos emails promo', cta:'Service Complet' },
      proof:{ badge:'📈 Pourquoi les organisateurs nous rejoignent', heading:'Les touristes et expatriés à Paris cherchent déjà de la comédie ici.', p1:'Le contrôle d\'aujourd\'hui confirme que les liens de réservation sont au vert : <strong>{bookingLinksVerified}</strong>. Quand quelqu\'un arrive sur pariscomedy.com et clique sur votre spectacle, il atterrit sur une page de réservation active — pas un cul-de-sac. On a construit ce site pour transformer la découverte en réservation.', p2:'Pour les organisateurs, c\'est l\'argument clé : un trafic qualifié, des liens propres, et une découverte rapide pour les personnes qui cherchent <em>comédie à Paris ce soir</em>, <em>stand-up anglais Paris</em>, ou <em>quoi faire à Pigalle</em>.', stat1:'liens de réservation actifs vérifiés en direct', stat2:'pour rendre votre spectacle visible sur le guide', stat3:'positionnement bilingue pour touristes, expatriés, locaux', quote:'« Wrong Language, Right Feeling » fonctionne déjà comme angle de conversion parce que ça sonne juste pour les expatriés à Paris. Si votre spectacle a une ambiance claire, on peut le présenter de la même façon.', cta:'🚀 Référencer Mon Spectacle' },
      fringe:{ badge:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Edinburgh Fringe 2026 · Saison Préview', heading:'Vous testez votre heure avant Édimbourg ?<br>Paris est la ville préview idéale.', desc:'Un public chaleureux, bilingue, avide de comédie. FFCN tourne depuis 2013. On remplit la salle et gère votre promo — pour que vous arriviez à Édimbourg en ayant déjà rodé votre spectacle.', feat1:'✅ Créneau préview à Paris (Mer/Ven/Sam)', feat2:'✅ Référencement Eventbrite + pariscomedy.com', feat3:'✅ Envoi email à notre audience parisienne', feat4:'✅ Post promo Instagram inclus', feat5:'✅ Pro 5€/mois ou Service Complet 30€/mois', cta:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Réserver Mon Créneau Préview', secondary:'Voir la scène →' },
      sunday:{ badge:'🗓️ Créneaux du dimanche disponibles', heading:'Vous avez besoin d\'un spectacle dimanche à Paris ?', desc:'Brunch d\'entreprise, anniversaire privé, meetup d\'expatriés, team offsite — on peut placer un humoriste bilingue et gérer la promo et le référencement pour que votre salle se remplisse vite.', cta:'⚡ Réserver un Créneau Dimanche', response:'Réponse cible : même jour' },
      quickBrief:{ badge:'⚡ Brief rapide', heading:'Pas envie d’écrire depuis zéro ? Choisissez le brief le plus proche.', desc:'Les demandes les plus rapides à convertir restent le corporate/privé et l’inventaire du dimanche encore ouvert. Ces boutons préremplissent le formulaire pour envoyer un brief exploitable en un clic.', response:'Idéal pour les demandes de devis dans la journée', sunday:'🌞 Événement privé du dimanche', corporate:'🏢 Événement corporate / équipe', listing:'📋 Référencer une salle ou un nouveau spectacle' },
      messagePlaceholder:'Dites-nous ce dont vous avez besoin...',
      formNote:'Les corrections et les nouvelles suggestions de spectacles sont d\'abord examinées par Chuck, puis ajoutées au répertoire public vérifié une fois confirmées.',
      faq:{ q1:'Comment rejoindre le open mic ?', a1:'Présentez-vous au Velvet Bar le mercredi à 19h00 et inscrivez-vous. Premier arrivé, premier servi. 5 minutes par comédien.', q2:'Combien ça coûte de se produire ?', a2:'Rien pour les artistes. Réservez votre place, il y a un minimum d\'une consommation, et on fait passer le chapeau à la fin. On est là pour les rires.', q3:'Faut-il parler français ?', a3:'Non. Nos spectacles sont en anglais (certains sont bilingues). Le français est un plus, pas une obligation.', q4:'Puis-je réserver un comédien pour mon événement d\'entreprise ?', a4:'Absolument. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Book a comedian\'">Remplissez le formulaire ci-dessus</a> avec les détails de votre événement et on vous trouvera le bon comédien.', q5:'Je dirige un spectacle de comédie à Paris. Puis-je être référencé ?', a5:'Oui ! On veut que pariscomedy.com soit le guide complet de la comédie anglaise à Paris. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Get Listed\'">Utilisez le formulaire ci-dessus</a> et l\'équipe Paris Comedy examinera les détails avant tout ajout au répertoire public vérifié.' }
    },
    venues: { subtitle:'23 salles de stand-up vérifiées dans Paris — là où les rires se jouent chaque semaine', mapTitle:'🗺️ Carte des salles de stand-up', mapSub:'23 lieux de stand-up anglophone vérifiés à Paris — cliquez sur un point pour voir les horaires', mapLegend:'🟣 = salle mise en avant avec rendez-vous hebdomadaires · 🔵 = autres lieux de stand-up anglophone', cardsTitle:'Salles de stand-up à Paris', cardsSub:'Retrouvez French Fried Comedy Night et 22 autres lieux anglophones vérifiés à Paris', yourVenue:'🏠 <strong>Votre salle ici ?</strong>', yourVenueSub:'Si vous programmez du stand-up anglophone à Paris, on veut vous référencer.', yourVenueCta:'Être référencé →', actions:{ map:'Ouvrir la carte', walk:'À pied', transit:'Transports', drive:'Voiture', pending:'Le lien cartographique précis est encore en vérification.' }, map:{ tba:'Spectacles à venir' }, other:{ title:'Autres salles de stand-up à Paris', sub:'Ces lieux accueillent du stand-up en anglais. Vous voulez une fiche complète avec réservation ?', cta:'Être référencé', claim:'Spectacles pas encore référencés', claimCta:'revendiquer cette fiche' } },
    history: { timeline:'La chronologie', introP1:'Il y a une blague récurrente dans la scène comique parisienne : <em>« Quand est-ce que le stand-up en anglais a commencé ici ? »</em> La réponse est compliquée — parce que pendant la majeure partie du XXe siècle, il n’existait tout simplement pas. La France avait sa propre tradition comique : le chansonnier, le one-man-show, le café-théâtre. Le stand-up à l’américaine ou à la britannique ? C’était quelque chose qu’on regardait sur Netflix, pas qu’on jouait dans un sous-sol à Pigalle.', introP2:'Et puis un gars venu de New York est arrivé.', introP3:'Voici comment la comédie en anglais à Paris est passée de rien du tout à l’une des scènes live les plus vibrantes d’Europe — en une quinzaine d’années.', keyPlayersSub:'Les personnes qui ont construit la scène, vanne après vanne', playerTitles:{ seb:'Le pionnier', paul:'La révélation', sarah:'La reine', robert:'Bâtisseur historique', tamer:'Le poids lourd' } },
    comedians: { nav:'Pour les humoristes', contactNav:'Contact', title:'Les spectacles de stand-up à Paris pour les humoristes', subtitle:'Une page de référence gratuite avec suggestions. Seuls les spectacles récemment vérifiés restent ici.', howTitle:'Comment fonctionne cette page', howP1:'Cette page se veut utile au public, pas excluante. Si un spectacle n’a pas d’activité vérifiée depuis 6 mois, il sort du répertoire courant jusqu’à nouvelle vérification.', howP2:'Si quelque chose est faux, manque, ou vient d’être lancé, envoyez-le via le formulaire Paris Comedy. Chuck examine les corrections et nouvelles suggestions ; les corrections vérifiées rejoignent la base publique et les cas incertains passent en revue manuelle.', helper:'Classé par salle · liens actifs · organisateur si connu · mis à jour depuis les données publiques · corrections relues par Chuck · offres payantes dès 1 €', cta:'Envoyer une correction / ajouter un spectacle →', footerBlurb:'Page de référence gratuite pour les humoristes, le public et les organisateurs.', pages:'Pages', needFix:'Besoin d’une correction ?', sendUpdate:'Envoyer une mise à jour', stats:'{shows} spectacles actuellement vérifiés dans {venues} salles. Dernière vérification : {latest}.', addressPending:'Adresse en cours de confirmation', verifiedCount:'{count} spectacles vérifiés', runner:'Organisateur', notConfirmed:'Pas encore confirmé', verifiedVia:'Vérifié {date} via {source}', recently:'récemment', manualReview:'revue manuelle', openListing:'Ouvrir la fiche' },
    blog: { nav:'Blog', heroTag:'Couverture 100 % comédie à Paris', heroTitle:'Le <span class="gradient-text">blog Paris Comedy</span>', heroSub:'Un espace éditorial pratique pour celles et ceux qui veulent trouver un spectacle, comprendre la scène ou monter sur scène à Paris sans fouiller des posts aléatoires.', heroCta:'Parcourir le blog', heroShows:'Voir les spectacles', belongsTitle:'Ce qu’on publie ici', belongsSub:'Uniquement de la comédie : spectacles, public, quartiers, contexte de scène et ressources utiles pour les artistes.', audienceTag:'Pour le public', audienceTitle:'Guides spectacles', audienceDesc:'Des guides courts comme « meilleure première soirée stand-up à Paris », des sélections par quartier, ou où emmener des amis de passage.', comicsTag:'Pour les humoristes', comicsTitle:'Ressources humoristes', comicsDesc:'Des explications concrètes sur les open mics, les différences entre les salles, l’ambiance du bloc Velvet du mercredi et la scène anglophone.', sceneTag:'Infos scène', sceneTitle:'Notes sur la scène parisienne', sceneDesc:'Des mises à jour utiles côté public : semaines chargées, grappes de salles, énergie saisonnière et type de public selon chaque lieu.', seedTitle:'Premiers articles', seedSub:'Pas un déversement de contenu — juste une première étagère propre, alignée avec le site.', workflowTitle:'Workflow éditorial', workflowSub:'Petit, pratique et sûr pour la marque.', step1Title:'1. Partir d’une vraie question de comédie', step1Desc:'Choisir une question que le public ou les humoristes posent vraiment : où aller, à quoi s’attendre, ou comment une salle diffère.', step2Title:'2. L’ancrer aux pages en ligne', step2Desc:'Chaque article doit renvoyer vers une page spectacle, salle, histoire ou ressource humoriste déjà présente sur le site.', step3Title:'3. Garder un ton local', step3Desc:'Drôle, utile et conscient de la scène. Pas de jargon interne, pas de notes système, pas de discours marketing.', step4Title:'4. Finir sur une vraie prochaine étape', step4Desc:'Réserver un spectacle, voir une salle ou envoyer une correction — jamais un article sans suite.', explore:'Explorer', forComics:'Pour les humoristes', currentShows:'Spectacles actuels', getListed:'Être référencé' }
  },
  es: {
    header: { subtitle:'Actúa, contrata un comediante o lista tu show en pariscomedy.com', title:'Sobre Paris Comedy' },
    listing: { title:'Lista Tu Show' },
    contact: { subtitle:'Rellena el formulario o escríbenos por Instagram — respondemos rápido.' },
    faq: { title:'Preguntas frecuentes' },
    book: {
      listingIntro:'¿Organizas una noche de comedia en inglés en París? Aparece en pariscomedy.com — la guía #1 de la comedia en inglés en París.',
      performCta:'📧 Contáctanos',
      corporateCta:'📧 Obtener Presupuesto',
      basic:{ title:'Listado básico', feat1:'✅ Nombre y descripción del show', feat2:'✅ Local y horario en el calendario', feat3:'❌ Sin enlace de entradas', cta:'Empezar' },
      pro:{ badge:'MÁS POPULAR', title:'Listado Pro', feat1:'✅ Todo lo del Básico', feat2:'✅ Enlace directo de reservas', feat3:'✅ Tarjeta sólida (sin borde discontinuo)', feat4:'✅ Marcador de local en el mapa', feat5:'✅ Gestionamos tu lista de email', feat6:'✅ 1 email masivo/semana incluido', cta:'Obtener Pro' },
      full:{ title:'Reserva de Servicio Completo', feat1:'✅ Todo lo del Pro', feat2:'✅ Gestión completa de reservas', feat3:'✅ 1 email masivo/semana a TU lista', feat4:'✅ Campañas de email automatizadas', feat5:'✅ Página de show en pariscomedy.com', feat6:'✅ Posición prioritaria en el calendario', feat7:'✅ Creamos y enviamos tus emails promo', cta:'Ir a Servicio Completo' },
      proof:{ badge:'📈 Por qué los organizadores se listan aquí', heading:'Los turistas y expatriados en París ya buscan comedia aquí.', p1:'La verificación de hoy confirma que los enlaces de reserva funcionan: <strong>{bookingLinksVerified}</strong>. Cuando alguien llega a pariscomedy.com y hace clic en tu show, llega a una página de reserva real — no a un callejón sin salida. Este sitio existe para convertir los descubrimientos en reservas.', p2:'Para los organizadores, ese es el argumento clave: tráfico de alta intención, enlaces limpios y descubrimiento rápido para personas que buscan <em>comedia en París esta noche</em>, <em>stand-up en inglés París</em>, o <em>qué hacer en Pigalle</em>.', stat1:'enlaces de reserva activos verificados en vivo', stat2:'para que tu show aparezca en la guía', stat3:'posicionamiento bilingüe para turistas, expatriados, locales', quote:'"Wrong Language, Right Feeling" ya funciona como ángulo de conversión porque se siente nativo en el París expatriado. Si tu show tiene un vibe claro, podemos empaquetarlo así también.', cta:'🚀 Listar Mi Show' },
      fringe:{ badge:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Edinburgh Fringe 2026 · Temporada Preview', heading:'¿Probando tu hora antes de Edimburgo?<br>París es la ciudad de preview perfecta.', desc:'Públicos cálidos, bilingües y con ganas de reír. FFCN lleva funcionando desde 2013. Llenaremos la sala y gestionaremos tu promo — para que llegues a Edimburgo habiendo ya calentado la sala.', feat1:'✅ Slot de preview en París (Mié/Vie/Sáb)', feat2:'✅ Listado en Eventbrite + pariscomedy.com', feat3:'✅ Email masivo a nuestra audiencia parisina', feat4:'✅ Post promo de Instagram incluido', feat5:'✅ Pro €5/mes o Servicio Completo €30/mes', cta:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Reservar Mi Slot de Preview', secondary:'Ver la escena →' },
      sunday:{ badge:'🗓️ Slots de domingo disponibles ahora', heading:'¿Necesitas un show el domingo en París?', desc:'Brunch corporativo, cumpleaños privado, meetup de expatriados, team offsite — podemos colocar un comediante bilingüe y gestionar el soporte de promo/listado para que tu sala se llene rápido.', cta:'⚡ Reservar un Slot Domingo', response:'Objetivo de respuesta: mismo día' },
      quickBrief:{ badge:'⚡ Inicio rápido', heading:'¿No quieres escribir desde cero? Elige el brief más cercano.', desc:'Las oportunidades de conversión más rápidas siguen estando en eventos privados/corporativos y en el inventario abierto del domingo. Estos botones rellenan el formulario para enviar un brief útil en un toque.', response:'Ideal para pedir presupuesto el mismo día', sunday:'🌞 Evento privado en domingo', corporate:'🏢 Evento corporativo / de equipo', listing:'📋 Añadir sala o show nuevo' },
      messagePlaceholder:'Cuéntanos lo que necesitas...',
      formNote:'Las correcciones y nuevas sugerencias de shows son revisadas primero por el equipo de Paris Comedy, luego añadidas al directorio público verificado una vez confirmadas.',
      faq:{ q1:'¿Cómo me apunto al open mic?', a1:'Preséntate en Velvet Bar el miércoles a las 19:00 y apúntate. Primero en llegar, primero en actuar. 5 minutos por cómico.', q2:'¿Cuánto cuesta actuar?', a2:'Nada para los artistas. Reserva tu lugar, hay un mínimo de una consumición, y pasamos el sombrero al final. Estamos aquí por las risas.', q3:'¿Necesito hablar francés?', a3:'No. Nuestros shows son en inglés (algunos son bilingües). El francés es un plus, no un requisito.', q4:'¿Puedo contratar un comediante para mi evento corporativo?', a4:'Por supuesto. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Book a comedian\'">Rellena el formulario de arriba</a> con los detalles de tu evento y te encontraremos al cómico adecuado.', q5:'Dirijo un show de comedia en París. ¿Puedo aparecer en la lista?', a5:'¡Sí! Queremos que pariscomedy.com sea la guía completa de la comedia en inglés en París. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Get Listed\'">Usa el formulario de arriba</a> y el equipo de Paris Comedy revisará los detalles antes de añadir nada al directorio público verificado.' }
    },
    venues: { actions:{ map:'Abrir mapa', walk:'Cómo llegar', transit:'Transporte', drive:'En coche', pending:'El enlace exacto del mapa aún debe revisarse.' }, map:{ tba:'Shows por anunciar' }, other:{ title:'Otros locales de comedia en París', sub:'Estos locales programan comedia en inglés. ¿Quieres destacar tu show con reserva completa?', cta:'Aparecer en la lista', claim:'Shows aún no listados', claimCta:'reclamar esta ficha' } },
    history: { playerTitles:{ seb:'El pionero', paul:'La explosión', sarah:'La reina', robert:'Constructor histórico', tamer:'El peso pesado' } },
    comedians: { nav:'Para comediantes', contactNav:'Contacto', title:'Shows de comedia en París para comediantes', subtitle:'Una página de referencia gratuita con sugerencias. Solo permanecen aquí los shows con actividad reciente verificada.', howTitle:'Cómo funciona esta página', howP1:'Esta página quiere ser una referencia pública útil, no una lista excluyente. Si un show no tiene actividad verificada en los últimos 6 meses, sale del directorio actual hasta que podamos verificarlo de nuevo.', howP2:'Si algo está mal, falta, o acaba de lanzarse, envíalo mediante el formulario de contacto de Paris Comedy. Chuck revisa las correcciones y nuevas propuestas; las correcciones verificadas se incorporan a la base pública y los casos inciertos pasan a revisión manual.', helper:'Ordenado por sala · enlaces activos · responsable si se conoce · actualizado a partir de datos públicos · correcciones revisadas por Chuck · opciones de pago desde 1 €', cta:'Enviar una corrección / añadir un show →', footerBlurb:'Página de referencia gratuita para comediantes, público y organizadores.', pages:'Páginas', needFix:'¿Hace falta una corrección?', sendUpdate:'Enviar una actualización', stats:'{shows} shows verificados actualmente en {venues} locales. Última verificación: {latest}.', addressPending:'Dirección por confirmar', verifiedCount:'{count} shows verificados', runner:'Responsable del show', notConfirmed:'Aún sin confirmar', verifiedVia:'Verificado {date} vía {source}', recently:'recientemente', manualReview:'revisión manual', openListing:'Abrir ficha' }
  },
  de: {
    header: { subtitle:'Auftreten, einen Comedian buchen oder Ihre Show auf pariscomedy.com eintragen', title:'Über Paris Comedy' },
    listing: { title:'Ihre Show eintragen' },
    contact: { subtitle:'Füllen Sie das Formular aus oder schreiben Sie uns per Instagram — wir antworten schnell.' },
    faq: { title:'FAQ' },
    book: {
      listingIntro:'Veranstalten Sie einen englischen Comedy-Abend in Paris? Erscheinen Sie auf pariscomedy.com — dem Nr. 1-Guide für englischsprachige Comedy in Paris.',
      performCta:'📧 Kontakt aufnehmen',
      corporateCta:'📧 Angebot anfragen',
      basic:{ title:'Basiseintrag', feat1:'✅ Showname & Beschreibung', feat2:'✅ Venue & Termine im Kalender', feat3:'❌ Kein Ticket-Link', cta:'Jetzt starten' },
      pro:{ badge:'BELIEBTESTE WAHL', title:'Pro-Eintrag', feat1:'✅ Alles aus Basic', feat2:'✅ Direkter Ticket-/Buchungslink', feat3:'✅ Einfarbige Karte (kein gestrichelter Rahmen)', feat4:'✅ Venue-Pin auf der Karte', feat5:'✅ Wir verwalten Ihre E-Mail-Liste', feat6:'✅ 1 Massen-E-Mail/Woche inklusive', cta:'Pro holen' },
      full:{ title:'Full-Service-Buchung', feat1:'✅ Alles aus Pro', feat2:'✅ Vollständiges Buchungsmanagement', feat3:'✅ 1 Massen-E-Mail/Woche an IHRE Liste', feat4:'✅ Automatisierte E-Mail-Kampagnen', feat5:'✅ Show-Seite auf pariscomedy.com', feat6:'✅ Priorität im Kalender', feat7:'✅ Wir erstellen & versenden Ihre Promo-E-Mails', cta:'Full Service wählen' },
      proof:{ badge:'📈 Warum Show-Veranstalter hier listen', heading:'Touristen und Expats in Paris suchen hier bereits nach Comedy.', p1:'Die heutige Überprüfung bestätigt: Die Buchungslinks sind alle aktiv — <strong>{bookingLinksVerified}</strong>. Wenn jemand auf pariscomedy.com landet und auf Ihre Show klickt, landet er auf einer echten Buchungsseite — nicht in einer Sackgasse. Diese Website ist dafür gebaut, Entdeckungen in Reservierungen zu verwandeln.', p2:'Für Veranstalter ist das der entscheidende Pitch: gezielter Traffic, saubere Links und schnelle Auffindbarkeit für Menschen, die nach <em>Comedy in Paris heute Abend</em>, <em>Englischer Stand-up Paris</em> oder <em>Was tun in Pigalle</em> suchen.', stat1:'aktive Buchungslinks live verifiziert', stat2:'um Ihre Show im Guide auffindbar zu machen', stat3:'zweisprachige Positionierung für Touristen, Expats, Einheimische', quote:'"Wrong Language, Right Feeling" funktioniert bereits als Conversion-Winkel, weil es sich nativ für das Expat-Paris anfühlt. Wenn Ihre Show eine klare Stimmung hat, können wir sie auch so verpacken.', cta:'🚀 Meine Show eintragen' },
      fringe:{ badge:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Edinburgh Fringe 2026 · Preview-Saison', heading:'Proben Sie Ihre Stunde vor Edinburgh?<br>Paris ist die perfekte Vorschau-Stadt.', desc:'Warmes, zweisprachiges, komödienhungriges Publikum. FFCN läuft seit 2013. Wir füllen den Raum und übernehmen Ihr Promo — damit Sie in Edinburgh ankommen, nachdem Sie den Raum bereits bespielt haben.', feat1:'✅ Paris Preview-Slot (Mi/Fr/Sa)', feat2:'✅ Eventbrite + pariscomedy.com Listing', feat3:'✅ E-Mail-Blast an unser Pariser Publikum', feat4:'✅ Instagram-Promo-Post inklusive', feat5:'✅ Pro-Listing €5/Monat oder Full-Service €30/Monat', cta:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 Meinen Preview-Slot buchen', secondary:'Die Szene ansehen →' },
      sunday:{ badge:'🗓️ Prime-Slots am Sonntag jetzt verfügbar', heading:'Brauchen Sie eine Sonntags-Show in Paris?', desc:'Corporate-Brunch, privater Geburtstag, Expat-Meetup, Team-Offsite — wir können einen zweisprachigen Comedian platzieren und Promo-/Listing-Support übernehmen, damit Ihr Raum schnell voll wird.', cta:'⚡ Sonntags-Slot reservieren', response:'Antwort-Ziel: gleicher Tag' },
      quickBrief:{ badge:'⚡ Schnellstart-Brief', heading:'Keine Lust, bei null anzufangen? Wählen Sie den passendsten Brief.', desc:'Die schnellsten Conversion-Chancen liegen weiter bei Private-/Corporate-Events und offenem Sonntags-Inventar. Diese Buttons füllen das Formular vor, damit Käufer mit einem Klick ein brauchbares Briefing senden können.', response:'Ideal für Angebotsanfragen noch am selben Tag', sunday:'🌞 Privates Sonntags-Event', corporate:'🏢 Corporate- / Team-Event', listing:'📋 Venue oder neue Show eintragen' },
      messagePlaceholder:'Sagen Sie uns, was Sie brauchen...',
      formNote:'Korrekturen und neue Show-Vorschläge werden zunächst vom Paris Comedy-Team geprüft und dann nach Bestätigung in das verifizierte öffentliche Verzeichnis aufgenommen.',
      faq:{ q1:'Wie komme ich auf die Open Mic-Bühne?', a1:'Kommen Sie mittwochs um 19:00 Uhr in die Velvet Bar und melden Sie sich an. Wer zuerst kommt, mahlt zuerst. 5 Minuten pro Comic.', q2:'Was kostet es aufzutreten?', a2:'Nichts für Auftreter. Reservieren Sie Ihren Platz, es gibt ein Mindestgetränk, und am Ende geht der Hut rum. Wir machen das für die Lacher.', q3:'Muss ich Französisch sprechen?', a3:'Nein. Unsere Shows sind auf Englisch (einige sind zweisprachig). Französisch ist ein Bonus, keine Voraussetzung.', q4:'Kann ich einen Comedian für meine Unternehmensveranstaltung buchen?', a4:'Selbstverständlich. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Book a comedian\'">Füllen Sie das Formular oben aus</a> mit Ihren Veranstaltungsdetails und wir finden den richtigen Comedian für Sie.', q5:'Ich veranstalte eine Comedy-Show in Paris. Kann ich gelistet werden?', a5:'Ja! Wir möchten, dass pariscomedy.com der vollständige Leitfaden für englischsprachige Comedy in Paris ist. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Get Listed\'">Nutzen Sie das obige Formular</a> und das Paris Comedy-Team prüft die Details, bevor etwas in das verifizierte öffentliche Verzeichnis aufgenommen wird.' }
    },
    venues: { actions:{ map:'Karte öffnen', walk:'Route', transit:'ÖPNV', drive:'Auto', pending:'Der genaue Kartenlink muss noch geprüft werden.' }, map:{ tba:'Shows folgen' }, other:{ title:'Weitere Comedy-Locations in Paris', sub:'Diese Locations hosten englischsprachige Comedy. Möchten Sie Ihre Show mit voller Buchung hervorheben?', cta:'Eintragen', claim:'Shows noch nicht gelistet', claimCta:'diesen Eintrag übernehmen' } },
    history: { playerTitles:{ seb:'Der Pionier', paul:'Der Durchbruch', sarah:'Die Königin', robert:'Früher Szenebauer', tamer:'Das Schwergewicht' } },
    comedians: { stats:'{shows} aktuell verifizierte Shows in {venues} Locations. Letzte Verifizierung: {latest}.', addressPending:'Adresse wird bestätigt', verifiedCount:'{count} verifizierte Shows', runner:'Showrunner', notConfirmed:'Noch nicht bestätigt', verifiedVia:'Verifiziert {date} via {source}', recently:'kürzlich', manualReview:'manuelle Prüfung', openListing:'Eintrag öffnen' }
  },
  ja: {
    header: { subtitle:'出演する、コメディアンを予約する、または pariscomedy.com にショーを掲載する', title:'Paris Comedy について' },
    listing: { title:'ショーを掲載' },
    contact: { subtitle:'下記フォームにご記入いただくか、Instagramにてメッセージをお送りください — すぐにご返答します。' },
    faq: { title:'よくある質問' },
    book: {
      listingIntro:'パリで英語のコメディナイトを開催中？pariscomedy.com に掲載 — パリの英語コメディ第1位のガイド。',
      performCta:'📧 お問い合わせ',
      corporateCta:'📧 見積もり依頼',
      basic:{ title:'ベーシック掲載', feat1:'✅ ショー名と説明', feat2:'✅ 会場とスケジュールをカレンダーに掲載', feat3:'❌ チケットリンクなし', cta:'始める' },
      pro:{ badge:'最人気', title:'プロ掲載', feat1:'✅ ベーシックのすべて', feat2:'✅ チケット直接リンク', feat3:'✅ ソリッドカード（点線なし）', feat4:'✅ 地図に会場ピン表示', feat5:'✅ メールリスト管理あり', feat6:'✅ 週1回のマスメール含む', cta:'プロを始める' },
      full:{ title:'フルサービス予約', feat1:'✅ プロのすべて', feat2:'✅ 予約完全管理', feat3:'✅ あなたのリストに週1回マスメール', feat4:'✅ 自動メールキャンペーン', feat5:'✅ pariscomedy.com に専用ショーページ', feat6:'✅ カレンダー優先掲載', feat7:'✅ プロモメール作成・送信代行', cta:'フルサービスを始める' },
      proof:{ badge:'📈 主催者がここに掲載する理由', heading:'パリの観光客やエクスパットはすでにここでコメディを探しています。', p1:'本日の確認で予約リンクの状態が確認されました：<strong>{bookingLinksVerified}</strong>。pariscomedy.com に誰かが訪れてあなたのショーをクリックすると、有効な予約ページに到達します — 死んだリンクではありません。このサイトは発見を予約に変えるために作りました。', p2:'主催者の方へ、それが本当の提案です：高い購買意欲を持つトラフィック、クリーンなリンク、そして <em>今夜パリのコメディ</em>、<em>パリの英語スタンドアップ</em>、または <em>ピガールで何をする</em> を検索している人への速い発見。', stat1:'予約リンクがライブ確認済み', stat2:'ガイドにショーを掲載するために', stat3:'観光客・外国人・地元向けバイリンガル展開', quote:'「Wrong Language, Right Feeling」はすでにコンバージョンの切り口として機能しています。パリのエクスパットにとってネイティブに感じられるからです。あなたのショーに明確な雰囲気があれば、同じようにパッケージングできます。', cta:'🚀 ショーを掲載する' },
      fringe:{ badge:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 エディンバラ・フリンジ 2026 · プレビューシーズン', heading:'エディンバラ前に1時間をテストしますか？<br>パリは完璧なプレビュー都市です。', desc:'温かく、バイリンガルで、コメディに飢えた観客。FFCNは2013年から続いています。会場を満員にしてプロモも担当します — すでに場を温めた状態でエディンバラに臨めます。', feat1:'✅ パリ・プレビュースロット（水/金/土）', feat2:'✅ Eventbrite + pariscomedy.com 掲載', feat3:'✅ パリのオーディエンスへのメール一斉配信', feat4:'✅ Instagramプロモ投稿含む', feat5:'✅ プロ掲載 €5/月 またはフルサービス €30/月', cta:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 プレビュースロットを予約', secondary:'シーンを見る →' },
      sunday:{ badge:'🗓️ 日曜プライムスロット受付中', heading:'パリで日曜ショーが必要ですか？', desc:'企業ブランチ、プライベートバースデー、エクスパットミートアップ、チームオフサイト — バイリンガルのコメディアンを手配し、プロモ・掲載サポートを担当して会場を速く満員にします。', cta:'⚡ 日曜スロットを予約', response:'目標返答時間：当日中' },
      quickBrief:{ badge:'⚡ クイック依頼', heading:'最初から書きたくないですか？いちばん近い依頼を選んでください。', desc:'最も早く収益につながりやすいのは、企業・プライベート案件と、まだ空きのある日曜枠です。これらのボタンでフォームを事前入力し、1タップで実用的な依頼を送れます。', response:'当日見積もり依頼に最適', sunday:'🌞 日曜のプライベートイベント', corporate:'🏢 企業 / チームイベント', listing:'📋 会場または新規ショーを掲載' },
      messagePlaceholder:'ご要望をお聞かせください...',
      formNote:'修正と新しいショーの提案は、まずパリコメディチームが審査し、確認後に公開ディレクトリに追加されます。',
      faq:{ q1:'オープンマイクに参加するにはどうすればいいですか？', a1:'水曜日の19時にVelvet Barに来て登録してください。先着順です。1コメディアン5分。', q2:'出演するのにいくらかかりますか？', a2:'出演者は無料です。席を予約して、ドリンク1杯のミニマムがあり、最後に帽子を回します。笑いのためにやっています。', q3:'フランス語を話す必要がありますか？', a3:'いいえ。ショーは英語（一部バイリンガル）です。フランス語はボーナスであり、必須ではありません。', q4:'企業イベント用にコメディアンを予約できますか？', a4:'もちろんです。<a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Book a comedian\'">上記フォームに記入</a>してイベントの詳細をお送りください。最適なコメディアンをマッチングします。', q5:'パリでコメディショーを運営しています。掲載してもらえますか？', a5:'はい！pariscomedy.comをパリの英語コメディの完全ガイドにしたいと思っています。<a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Get Listed\'">上記フォームを使用</a>して、パリコメディチームが詳細を確認してから公開ディレクトリに追加します。' }
    },
    venues: { actions:{ map:'地図を開く', walk:'行き方', transit:'交通機関', drive:'車', pending:'正確な地図リンクは確認中です。' }, map:{ tba:'公演情報は後日' }, other:{ title:'パリのその他のコメディ会場', sub:'これらの会場でも英語コメディを開催しています。予約付きで掲載したいですか？', cta:'掲載する', claim:'まだ掲載されていない公演', claimCta:'この掲載を申請' } },
    history: { playerTitles:{ seb:'パイオニア', paul:'ブレイク役', sarah:'女王', robert:'初期の立役者', tamer:'大物' } },
    comedians: { stats:'現在確認済みの公演は{venues}会場で{shows}件。最新確認日: {latest}。', addressPending:'住所確認中', verifiedCount:'確認済み {count} 件', runner:'主催者', notConfirmed:'未確認', verifiedVia:'{source} により {date} に確認', recently:'最近', manualReview:'手動確認', openListing:'掲載を見る' }
  },
  zh: {
    header: { subtitle:'表演、预约喜剧演员，或在 pariscomedy.com 发布您的演出', title:'关于 Paris Comedy' },
    listing: { title:'发布您的演出' },
    contact: { subtitle:'填写下方表单，或在 Instagram 上发私信给我们 — 我们回复很快。' },
    faq: { title:'常见问题' },
    book: {
      listingIntro:'在巴黎举办英语喜剧之夜？立即在 pariscomedy.com 上发布 — 巴黎英语喜剧第一指南。',
      performCta:'📧 联系我们',
      corporateCta:'📧 获取报价',
      basic:{ title:'基础套餐', feat1:'✅ 演出名称和描述', feat2:'✅ 场地和时间表收录于日历', feat3:'❌ 无购票链接', cta:'立即开始' },
      pro:{ badge:'最受欢迎', title:'专业套餐', feat1:'✅ 基础套餐所有功能', feat2:'✅ 直接购票/预订链接', feat3:'✅ 实线边框卡片（非虚线）', feat4:'✅ 地图上标注场地', feat5:'✅ 我们管理您的邮件列表', feat6:'✅ 每周1封群发邮件已包含', cta:'升级专业版' },
      full:{ title:'全服务预订', feat1:'✅ 专业套餐所有功能', feat2:'✅ 完整预订管理', feat3:'✅ 每周1封群发邮件至您的列表', feat4:'✅ 自动邮件营销活动', feat5:'✅ pariscomedy.com 上的专属演出页面', feat6:'✅ 日历优先展示', feat7:'✅ 我们为您制作并发送推广邮件', cta:'选择全服务' },
      proof:{ badge:'📈 演出主理人在这里发布的原因', heading:'巴黎的游客和外籍人士已经在这里寻找喜剧演出。', p1:'今天的核验确认订票链接状态良好：<strong>{bookingLinksVerified}</strong>。当有人登陆 pariscomedy.com 并点击您的演出时，他们会进入一个有效的订票页面 — 而不是死链。我们建立这个网站，就是为了将发现转化为预订。', p2:'对于演出主理人来说，这才是真正的卖点：高意向流量、干净的链接，以及针对那些搜索 <em>今晚巴黎喜剧</em>、<em>巴黎英语单口</em> 或 <em>皮加勒去哪玩</em> 的人的快速发现。', stat1:'订票链接已在线验证', stat2:'让您的演出在指南上可被发现', stat3:'面向游客、外籍人士和本地居民的双语定位', quote:'"Wrong Language, Right Feeling" 已经作为转化角度发挥作用，因为它对巴黎的外籍人士感觉非常贴近。如果您的演出有清晰的风格，我们也可以这样为您打包推广。', cta:'🚀 发布我的演出' },
      fringe:{ badge:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 爱丁堡艺穗节 2026 · 预演季', heading:'在爱丁堡之前测试你的一小时？<br>巴黎是完美的预演城市。', desc:'热情洋溢、双语、渴望喜剧的观众。FFCN 自 2013 年起持续运营。我们会帮您填满场子并负责推广 — 让您带着已经磨砺过的节目走进爱丁堡。', feat1:'✅ 巴黎预演场次（周三/周五/周六）', feat2:'✅ Eventbrite + pariscomedy.com 收录', feat3:'✅ 向我们的巴黎受众发送邮件群发', feat4:'✅ 含 Instagram 推广帖子', feat5:'✅ 专业套餐 €5/月 或 全服务 €30/月', cta:'🏴󠁧󠁢󠁳󠁣󠁴󠁿 预订我的预演场次', secondary:'了解现场 →' },
      sunday:{ badge:'🗓️ 周日黄金时段现已开放', heading:'需要在巴黎安排周日演出？', desc:'企业早午宴、私人生日派对、外籍人士聚会、团队外出活动 — 我们可以安排一位双语喜剧演员，并提供推广/发布支持，让您的场地迅速坐满。', cta:'⚡ 预订周日时段', response:'目标回复：当天' },
      quickBrief:{ badge:'⚡ 快速需求模板', heading:'不想从零开始写？选择最接近的需求模板。', desc:'目前最快的转化机会仍然是企业/私人活动，以及还有空档的周日场次。这些按钮会预填表单，让买家一键发送可执行的需求。', response:'适合同日询价', sunday:'🌞 周日私人活动', corporate:'🏢 企业 / 团队活动', listing:'📋 收录场地或新演出' },
      messagePlaceholder:'请告诉我们您的需求...',
      formNote:'更正和新演出建议将由巴黎喜剧团队首先审核，确认后添加到经过验证的公共目录中。',
      faq:{ q1:'如何参加开放麦？', a1:'周三 19:00 到 Velvet Bar 报名。先到先得，每位喜剧演员 5 分钟。', q2:'表演需要多少费用？', a2:'演员免费。预留座位，最低消费一杯饮品，最后我们会传帽子募款。我们是为了笑声而来。', q3:'我需要会说法语吗？', a3:'不需要。我们的演出是英语（部分是双语）。会法语是加分项，不是必要条件。', q4:'我可以为企业活动预订喜剧演员吗？', a4:'当然。<a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Book a comedian\'">填写上面的表单</a>并提供活动详情，我们会为您匹配合适的喜剧演员。', q5:'我在巴黎经营喜剧演出。可以收录我吗？', a5:'当然！我们希望 pariscomedy.com 成为巴黎英语喜剧的完整指南。<a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Get Listed\'">使用上面的表单</a>，巴黎喜剧团队将在添加到已验证的公共目录之前审核详情。' }
    },
    venues: { actions:{ map:'打开地图', walk:'路线', transit:'公共交通', drive:'驾车', pending:'精确地图链接仍待核实。' }, map:{ tba:'演出待公布' }, other:{ title:'巴黎其他喜剧场地', sub:'这些场地也有英文喜剧演出。想让你的演出带完整订票入口上线吗？', cta:'申请收录', claim:'演出尚未收录', claimCta:'认领此条目' } },
    history: { playerTitles:{ seb:'先驱', paul:'破圈人物', sarah:'女王', robert:'早期建设者', tamer:'重磅人物' } },
    comedians: { stats:'目前共有 {venues} 个场地的 {shows} 场已验证演出。最近一次核验：{latest}。', addressPending:'地址待确认', verifiedCount:'已验证 {count} 场', runner:'主理人', notConfirmed:'尚未确认', verifiedVia:'于 {date} 通过 {source} 核验', recently:'最近', manualReview:'人工复核', openListing:'打开条目' }
  },
  ko: {
    header: { subtitle:'무대에 서고, 코미디언을 섭외하고, pariscomedy.com에 쇼를 등록하세요', title:'Paris Comedy 소개' },
    listing: { title:'쇼 등록하기' },
    contact: { subtitle:'아래 양식을 작성하거나 인스타그램 DM을 보내세요 — 빠르게 답장합니다.' },
    faq: { title:'자주 묻는 질문' },
    book: {
      listingIntro:'파리에서 영어 코미디 나이트를 운영하시나요? pariscomedy.com에 소개되세요 — 파리 영어 코미디 1위 가이드입니다.',
      performCta:'📧 문의하기',
      corporateCta:'📧 견적 받기',
      basic:{ title:'기본 등록', feat1:'✅ 쇼 이름과 설명', feat2:'✅ 공연장과 일정 캘린더 노출', feat3:'❌ 티켓 링크 없음', cta:'시작하기' },
      pro:{ badge:'가장 인기', title:'프로 등록', feat1:'✅ 기본 등록 전체 포함', feat2:'✅ 직접 티켓/예약 링크', feat3:'✅ 실선 카드 디자인', feat4:'✅ 지도에 공연장 핀 표시', feat5:'✅ 이메일 리스트 관리', feat6:'✅ 주 1회 대량 이메일 포함', cta:'프로 시작' },
      full:{ title:'풀서비스 예약', feat1:'✅ 프로 등록 전체 포함', feat2:'✅ 전체 예약 운영 관리', feat3:'✅ 당신의 리스트에 주 1회 대량 이메일', feat4:'✅ 자동 이메일 캠페인', feat5:'✅ pariscomedy.com 전용 쇼 페이지', feat6:'✅ 캘린더 우선 배치', feat7:'✅ 프로모 이메일 제작 및 발송', cta:'풀서비스 선택' },
      proof:{ badge:'📈 주최자가 여기 등록하는 이유', heading:'파리의 관광객과 외국인 거주자들은 이미 여기서 코미디를 찾고 있습니다.', p1:'오늘 점검 결과 예약 링크 상태는 양호합니다: <strong>{bookingLinksVerified}</strong>. 즉, 누군가 pariscomedy.com에 들어와 당신의 쇼를 클릭하면 죽은 링크가 아니라 실제 예약 페이지로 이동합니다. 이 사이트는 발견을 예약으로 바꾸기 위해 만들었습니다.', p2:'주최자에게 이게 핵심 가치입니다: 구매 의도가 높은 트래픽, 깔끔한 링크, 그리고 <em>오늘 밤 파리 코미디</em>, <em>파리 영어 스탠드업</em>, <em>피갈에서 뭐 하지</em>를 검색하는 사람들에게 빠르게 발견되는 것.', stat1:'라이브 검증된 활성 예약 링크', stat2:'가이드에서 당신의 쇼를 발견 가능하게', stat3:'관광객·외국인·현지인을 위한 이중언어 포지셔닝', quote:'“Wrong Language, Right Feeling”은 이미 전환 문구로 잘 작동합니다. 파리의 외국인 커뮤니티에 자연스럽게 들리기 때문이죠. 쇼에 뚜렷한 분위기가 있다면 그렇게 패키징할 수 있습니다.', cta:'🚀 내 쇼 등록하기' },
      fringe:{ badge:'🏴 에든버러 프린지 2026 · 프리뷰 시즌', heading:'에든버러 전에 한 시간 분량을 테스트하시나요?<br>파리는 완벽한 프리뷰 도시입니다.', desc:'따뜻하고, 이중언어이며, 코미디를 사랑하는 관객들. FFCN은 2013년부터 계속되어 왔습니다. 객석을 채우고 프로모션까지 맡아드리니, 이미 무대를 다져 놓은 상태로 에든버러에 들어갈 수 있습니다.', feat1:'✅ 파리 프리뷰 슬롯 (수/금/토)', feat2:'✅ Eventbrite + pariscomedy.com 등록', feat3:'✅ 파리 관객 대상 이메일 발송', feat4:'✅ 인스타그램 프로모 게시물 포함', feat5:'✅ 프로 등록 €5/월 또는 풀서비스 €30/월', cta:'🏴 프리뷰 슬롯 예약', secondary:'씬 보기 →' },
      sunday:{ badge:'🗓️ 일요일 주요 슬롯 오픈', heading:'파리에서 일요일 쇼가 필요하신가요?', desc:'기업 브런치, 프라이빗 생일 파티, 외국인 모임, 팀 오프사이트 — 이중언어 코미디언 섭외와 홍보/등록 지원으로 객석을 빠르게 채워드립니다.', cta:'⚡ 일요일 슬롯 예약', response:'목표 응답: 당일' },
      quickBrief:{ badge:'⚡ 빠른 브리프', heading:'처음부터 쓰기 싫다면 가장 가까운 브리프를 고르세요.', desc:'지금 가장 빨리 전환되는 건 여전히 기업/프라이빗 행사와 비어 있는 일요일 슬롯입니다. 이 버튼들은 폼을 미리 채워 한 번에 쓸 만한 요청을 보내게 해줍니다.', response:'당일 견적 요청에 적합', sunday:'🌞 일요일 프라이빗 이벤트', corporate:'🏢 기업 / 팀 이벤트', listing:'📋 공연장 또는 새 쇼 등록' },
      messagePlaceholder:'원하시는 내용을 알려주세요...',
      formNote:'수정 요청과 새 쇼 제안은 먼저 검토한 뒤, 확인되면 공개 디렉터리에 반영됩니다.',
      faq:{ q1:'오픈 마이크는 어떻게 신청하나요?', a1:'수요일 19:00에 Velvet Bar에 오셔서 이름을 올리세요. 선착순이며 1인당 5분입니다.', q2:'공연하려면 비용이 드나요?', a2:'공연자에게는 비용이 없습니다. 좌석을 예약하고, 1인 1음료가 있으며, 마지막에 팁 모자를 돌립니다. 우리는 웃음을 위해 합니다.', q3:'프랑스어를 해야 하나요?', a3:'아니요. 쇼는 영어로 진행되며 일부는 이중언어입니다. 프랑스어는 있으면 좋지만 필수는 아닙니다.', q4:'기업 행사에 코미디언을 섭외할 수 있나요?', a4:'물론입니다. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Book a comedian\'">위 양식을 작성</a>하고 행사 정보를 보내주시면 맞는 코미디언을 연결해 드립니다.', q5:'파리에서 코미디 쇼를 운영합니다. 등록할 수 있나요?', a5:'네. pariscomedy.com이 파리 영어 코미디의 완전한 가이드가 되길 원합니다. <a href="#contactForm" onclick="document.getElementById(\'contactSubject\').value=\'Get Listed\'">위 양식을 사용</a>하면 검토 후 공개 디렉터리에 반영합니다.' }
    },
    venues: { actions:{ map:'지도 열기', walk:'길찾기', transit:'대중교통', drive:'자동차', pending:'정확한 지도 링크는 아직 확인 중입니다.' }, map:{ tba:'공연 정보 예정' }, other:{ title:'파리의 다른 코미디 공연장', sub:'이 공연장들도 영어 코미디를 엽니다. 예약 링크까지 포함해 소개하고 싶으신가요?', cta:'등록하기', claim:'아직 등록되지 않은 쇼', claimCta:'이 항목 요청하기' } },
    history: { playerTitles:{ seb:'개척자', paul:'브레이크아웃 스타', sarah:'여왕', robert:'초기 구축자', tamer:'헤비히터' } },
    comedians: { nav:'코미디언용', contactNav:'문의', title:'코미디언을 위한 파리 코미디 쇼', subtitle:'무료 참고 + 제안 페이지입니다. 최근 활동이 검증된 쇼만 여기에 남습니다.', howTitle:'이 페이지가 작동하는 방식', howP1:'이 페이지는 배타적인 리스트가 아니라, 실제로 도움이 되는 공개 참고용 페이지입니다. 6개월 안에 검증 가능한 활동이 없으면 다시 확인될 때까지 현재 디렉터리에서 빠집니다.', howP2:'잘못된 정보, 누락된 정보, 새로 시작한 쇼가 있다면 Paris Comedy 문의 폼으로 보내주세요. Chuck이 수정과 새 제안을 검토하고, 확인된 내용만 공개 데이터 레이어에 반영합니다. 확실하지 않은 것은 추측하지 않고 수동 검토로 넘깁니다.', helper:'공연장별 정리 · 작동하는 링크 · 쇼 러너 정보(가능할 경우) · 공개 데이터 레이어 기반 업데이트 · Chuck 검토 · 유료 등록은 월 1€부터', cta:'수정 보내기 / 쇼 추가하기 →', footerBlurb:'코미디언, 관객, 쇼 러너를 위한 무료 참고 페이지.', pages:'페이지', needFix:'수정이 필요하신가요?', sendUpdate:'업데이트 보내기', stats:'현재 {venues}개 공연장에 {shows}개의 검증된 쇼가 있습니다. 최근 검증일: {latest}.', addressPending:'주소 확인 중', verifiedCount:'검증된 쇼 {count}개', runner:'쇼 러너', notConfirmed:'아직 확인되지 않음', verifiedVia:'{date}에 {source}를 통해 검증', recently:'최근', manualReview:'수동 검토', openListing:'항목 열기' }
  },

};

function mergeLocaleFallback(base, override) {
    if (Array.isArray(base)) return Array.isArray(override) ? override : base.slice();
    if (base && typeof base === 'object') {
        const out = {};
        const keys = new Set([
            ...Object.keys(base || {}),
            ...Object.keys((override && typeof override === 'object') ? override : {})
        ]);
        keys.forEach(key => {
            out[key] = mergeLocaleFallback(base?.[key], override?.[key]);
        });
        return out;
    }
    return override == null ? base : override;
}

['fr', 'es', 'de', 'ja', 'zh', 'ko'].forEach(lang => {
    TRANSLATIONS[lang] = mergeLocaleFallback(TRANSLATIONS.en, TRANSLATIONS[lang]);
    PAGE_COPY[lang] = mergeLocaleFallback(PAGE_COPY.en, PAGE_COPY[lang]);
});

/* Calendar helper — generates events for current month */
function generateCalendarEvents(year, month) {
    const events = [];
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const dayOfWeek = date.getDay(); // 0=Sun, 1=Mon, ..., 3=Wed
        SHOWS.forEach(show => {
            const showDayNum = { 'Sunday':0,'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5,'Saturday':6 }[show.day];
            if (dayOfWeek === showDayNum) {
                events.push({
                    day, showId:show.id, showName:show.name, shortName:show.shortName,
                    type:show.type, time:show.time, venue:VENUES.find(v=>v.id===show.venue)?.name||'', emoji:show.emoji,
                    bookingUrl: show.bookingUrl || null
                });
            }
        });
    }
    return events;
}
