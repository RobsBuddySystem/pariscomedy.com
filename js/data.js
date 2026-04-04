/* Paris Comedy — Data Layer */
/* All show data in one place — easy to update (Betty approved ✓) */

const UTM = '?utm_source=pariscomedy&utm_medium=website';

const VENUES = [
    { id:'velvet', name:'Velvet Bar', address:'39 Rue de Douai, 75009 Paris', neighborhood:'Pigalle (9th)', lat:48.8821, lng:2.3349, mapX:38, mapY:35, listed:true, description:'An intimate basement bar in the heart of Pigalle. Three comedy shows every Wednesday — the epicenter of English-language comedy in Paris.', metro:'Pigalle (M2/M12)' },
    { id:'paname', name:'Paname Art Café', address:'2bis Quai de la Loire, 75019 Paris', neighborhood:'Canal Saint-Martin (19th)', lat:48.8844, lng:2.3728, mapX:72, mapY:18, listed:false, description:'A legendary venue overlooking Canal Saint-Martin. Live comedy, music, and art in one of Paris\'s most creative spaces.', metro:'Jaurès (M2/M5/M7bis)' },
    { id:'bikini-bottom', name:'Le Bikini Bottom', address:'Paris', neighborhood:'Paris', lat:48.8600, lng:2.3500, mapX:52, mapY:45, listed:false, description:'Weekly English comedy show venue.', metro:'' },
    { id:'les-marquises', name:'Les Marquises', address:'Paris', neighborhood:'Paris', lat:48.8650, lng:2.3700, mapX:70, mapY:38, listed:false, description:'Home of Green Light Comedy — standup in English every Tuesday.', metro:'' },
    { id:'englishman', name:'The Englishman Cocktail Club', address:'Paris', neighborhood:'Paris', lat:48.8700, lng:2.3300, mapX:42, mapY:32, listed:false, description:'English comedy night every Thursday.', metro:'' },
    { id:'theatre-bo', name:'Théâtre BO Saint-Martin', address:'19 Boulevard Saint-Martin, 75003 Paris', neighborhood:'République (3rd)', lat:48.8680, lng:2.3540, mapX:58, mapY:35, listed:false, description:'English-language comedy specials and touring acts. Sarah Donnelly\'s home stage.', metro:'République (M3/M5/M8/M9/M11)' },
    { id:'le-noddi', name:'Le Noddi', address:'Paris', neighborhood:'Paris', lat:48.8550, lng:2.3600, mapX:60, mapY:50, listed:false, description:'Funny Women Paris — English stand-up featuring women comedians.', metro:'' },
    { id:'le-kibele', name:'Le Kibélé', address:'Paris', neighborhood:'Paris', lat:48.8750, lng:2.3450, mapX:48, mapY:25, listed:false, description:'The Open Mic Express — English stand-up open mic.', metro:'' }
];

const SHOWS = [
    { id:'velvet-openmic', name:'Velvet Bar Comedy — Open Mic', shortName:'Open Mic', venue:'velvet', type:'openmic', day:'Wednesday', time:'19:00', price:'Free', emoji:'🎙️',
      description:'Sign up, step up, make them laugh. All levels welcome — the best open mic in Pigalle.',
      descFr:'Inscrivez-vous, montez sur scène, faites-les rire. Tous niveaux bienvenus.',
      descEs:'Inscríbete, sube al escenario, hazlos reír. Todos los niveles son bienvenidos.',
      bookingUrl:'https://www.eventbrite.com/e/velvet-bar-comedy-open-mic-stand-up-comedy-a-paris-tickets-1977106148713' + UTM, featured:false },
    { id:'velvet-comedy', name:'Velvet Bar Comedy — Le meilleur du stand-up', shortName:'Comedy Night', venue:'velvet', type:'standup', day:'Wednesday', time:'20:30', price:'Free', emoji:'🎭',
      description:'Curated showcase — the best comics in Paris on one stage. Bilingual, unpredictable, unforgettable.',
      descFr:'Showcase curé — les meilleurs humoristes de Paris sur une même scène. Bilingue, imprévisible, inoubliable.',
      descEs:'Showcase curado — los mejores cómicos de París en un escenario. Bilingüe, impredecible, inolvidable.',
      bookingUrl:'https://www.eventbrite.com/e/velvet-bar-comedy-le-meilleur-du-stand-up-a-paris-tickets-1825871804719' + UTM, featured:true },
    { id:'ffcn', name:'French Fried Comedy Night', shortName:'FFCN', venue:'velvet', type:'standup', day:'Wednesday', time:'22:00', price:'Free', emoji:'🍟',
      description:'THE bilingual comedy show. American & French comics, English & French jokes, same night. The show that started it all.',
      descFr:'LE spectacle de comédie bilingue. Humoristes américains et français, blagues en anglais et en français, le même soir.',
      descEs:'EL show de comedia bilingüe. Cómicos americanos y franceses, chistes en inglés y francés, la misma noche.',
      bookingUrl:'https://www.eventbrite.com/e/french-fried-comedy-night-tickets-603182383747' + UTM, featured:true },
    /* Paname removed from our shows — not our venue */
];

/* Other shows — verified active on Eventbrite as of April 2026. No ticket links unless they pay. */
const OTHER_SHOWS = [
    { name:'Millennial Meltdown', venueName:'Le Bikini Bottom', day:'Wednesday', time:'20:00', type:'standup', emoji:'🔥', description:'English comedy show — stand-up night in Paris. Weekly at Le Bikini Bottom.', paid:false },
    { name:'Green Light Comedy', venueName:'Les Marquises', day:'Tuesday', time:'20:15', type:'standup', emoji:'🟢', description:'Standup comedy in English. Weekly at Les Marquises.', paid:false },
    { name:'The Englishman Comedy Night', venueName:'The Englishman Cocktail Club', day:'Thursday', time:'20:00', type:'standup', emoji:'🇬🇧', description:'English comedy night at The Englishman Cocktail Club in Paris.', paid:false },
    { name:'Funny Women Paris', venueName:'Le Noddi', day:'Tuesday', time:'20:00', type:'standup', emoji:'👩‍🎤', description:'English stand-up comedy in Paris featuring women comedians. At Le Noddi.', paid:false },
    { name:'The Open Mic Express', venueName:'Le Kibélé', day:'Friday', time:'19:00', type:'openmic', emoji:'🚂', description:'English stand-up open mic in Paris. Drop in, sign up, perform.', paid:false },
    { name:'English Comedy at Théâtre BO', venueName:'Théâtre BO Saint-Martin', day:'Various', time:'20:15', type:'standup', emoji:'🎭', description:'English-language comedy specials and one-person shows at the legendary Théâtre BO.', paid:false }
];

const KEY_PLAYERS = [
    { id:'seb', name:'Sebastian Marx', title:'The Pioneer', emoji:'🗽', bio:'New Yorker who fell in love with a French woman and moved to Paris. Created "New York Comedy Night" at SoGymnase — the FIRST regular English stand-up show in Paris. Appeared on Jamel Comedy Club (Canal+), got a radio gig on RTL with Stéphane Bern, and later France Inter. He\'s the one who proved English-language comedy could work in Paris.',
      bioFr:'New-Yorkais tombé amoureux d\'une Française. Créateur de "New York Comedy Night" au SoGymnase — le PREMIER spectacle régulier de stand-up en anglais à Paris.',
      bioEs:'Neoyorquino que se enamoró de una francesa. Creó "New York Comedy Night" en SoGymnase — el PRIMER show regular de stand-up en inglés en París.' },
    { id:'paul', name:'Paul Taylor', title:'The Breakout', emoji:'🇬🇧', bio:'British comedian who moved to Paris in 2009. His 2016 "La Bise" video went viral with 3M+ views, and Canal+ gave him "What The Fuck France" — the first English-language show on French TV. His #Franglais, "So British", and "Bisoubye x" tours sold out across France. 1.5M+ followers across platforms.',
      bioFr:'Humoriste britannique installé à Paris depuis 2009. Sa vidéo "La Bise" est devenue virale en 2016. Canal+ lui a confié "What The Fuck France".',
      bioEs:'Comediante británico que se mudó a París en 2009. Su video "La Bise" se volvió viral en 2016 con más de 3M de vistas.' },
    { id:'sarah', name:'Sarah Donnelly', title:'The Queen', emoji:'👑', bio:'American comedian who\'s been in Paris 12+ years. She opened for Jerry Seinfeld, toured with Gad Elmaleh, and regularly performs at Théâtre BO Saint-Martin. Her special "The Only American in Paris" is on YouTube. A pillar of the Paris English comedy scene.',
      bioFr:'Humoriste américaine installée à Paris depuis plus de 12 ans. Elle a fait la première partie de Jerry Seinfeld et tourné avec Gad Elmaleh.',
      bioEs:'Comediante estadounidense en París desde hace más de 12 años. Abrió para Jerry Seinfeld y giró con Gad Elmaleh.' },
    { id:'robert', name:'Robert Hoehn', title:'The Founder', emoji:'🍟', bio:'American bilingual comedian and founder of French Fried Comedy Night — now the oldest continuously running English-language stand-up comedy show in Paris. Started at Paname Art Café, now at Velvet Bar in Pigalle every Wednesday. Robert hosts three shows every Wednesday night — open mic, showcase, and the legendary FFCN — bridging the gap between French and international comedy scenes.',
      bioFr:'Humoriste américain bilingue et fondateur de French Fried Comedy Night — le plus ancien spectacle de stand-up en anglais encore en activité à Paris. Lancé au Paname Art Café, maintenant au Velvet Bar à Pigalle chaque mercredi.',
      bioEs:'Comediante estadounidense bilingüe y fundador de French Fried Comedy Night — el show de stand-up en inglés más antiguo en actividad en París. Comenzó en Paname Art Café, ahora en Velvet Bar en Pigalle cada miércoles.' },
    { id:'tamer', name:'Tamer Kattan', title:'NY to Paris', emoji:'🌍', bio:'New York comedian who made Paris his second home. 159K+ followers on social media. Regular collaborator with Robert Hoehn and a favorite on the Paris English-language comedy circuit.',
      bioFr:'Humoriste new-yorkais qui a fait de Paris sa deuxième maison. Plus de 159K abonnés sur les réseaux sociaux.',
      bioEs:'Comediante neoyorquino que hizo de París su segundo hogar. Más de 159K seguidores en redes sociales.' },
    { id:'gad', name:'Gad Elmaleh', title:'The Bridge', emoji:'🌉', bio:'French comedy legend who crossed over to perform in English, doing sets in New York and appearing on major US platforms. He bridged French and American comedy, proving the two worlds could connect. Toured with Sarah Donnelly.',
      bioFr:'Légende de l\'humour français qui a traversé l\'Atlantique pour se produire en anglais à New York.',
      bioEs:'Leyenda de la comedia francesa que cruzó al inglés, actuando en Nueva York y plataformas estadounidenses.' }
];

const TIMELINE = [
    { year:'~2004', title:'The Seed', text:'Sebastian Marx arrives from New York, falls in love with a French woman, and moves to Toulouse. He doesn\'t know it yet, but he\'s about to change Paris comedy forever.' },
    { year:'2010', title:'Ground Zero', text:'Seb Marx starts doing stand-up in French in Paris. He creates "New York Comedy Night" at SoGymnase — the FIRST regular English stand-up show in the city. This is where it all begins.' },
    { year:'2012', title:'TV Breakthrough', text:'Seb appears on Jamel Comedy Club on Canal+ — massive national exposure. Gets a radio gig on RTL with Stéphane Bern. English-language comedy in Paris is suddenly visible.' },
    { year:'2013', title:'New Voices', text:'Paul Taylor (British, moved to Paris in 2009) starts doing stand-up. Same year, Seb Marx gets a France Inter radio slot. The scene is growing.' },
    { year:'~2014', title:'Sarah Arrives', text:'Sarah Donnelly, American comedian in Paris for years, builds her career. She\'ll go on to open for Jerry Seinfeld, tour with Gad Elmaleh, and become one of Paris\'s most respected English-language comics.' },
    { year:'2016', title:'Viral Explosion', text:'Paul Taylor\'s "La Bise" video goes viral — 3M+ views. Canal+ gives him "What The Fuck France," the first English-language show on French TV. English comedy in Paris is now mainstream.' },
    { year:'2016–2019', title:'The Franglais Era', text:'Paul Taylor\'s #Franglais tour sells out venues across France. French Fried Comedy Night launches at Paname Art Café, then moves to Velvet Bar — becoming the weekly Wednesday institution.' },
    { year:'~2017', title:'French Fried is Born', text:'Robert Hoehn launches French Fried Comedy Night at Paname Art Café — a weekly bilingual comedy show mixing American and French comics on the same stage. It quickly becomes one of the most popular English-language comedy nights in Paris.' },
    { year:'2020–2023', title:'The Pandemic & Comeback', text:'Like every live venue, Paris comedy takes a hit. But the scene bounces back stronger. French Fried Comedy Night survives and evolves.' },
    { year:'~2024', title:'FFCN Moves to Velvet Bar', text:'French Fried Comedy Night moves to Velvet Bar in Pigalle — a more intimate basement venue that becomes the new home of Wednesday night comedy in Paris. Now the oldest continuously running English stand-up comedy show in Paris.' },
    { year:'2019–2024', title:'The Growth', text:'Paul Taylor\'s "So British" and "Bisoubye x" tours continue selling out. Sarah Donnelly releases "The Only American in Paris" special on YouTube. More English comedy nights keep appearing.' },
    { year:'2024–2025', title:'The Explosion', text:'The scene explodes. Multiple weekly English shows across Paris. What started as one guy from New York at SoGymnase is now 10+ regular English comedy nights at venues all over the city.' },
    { year:'Now', title:'The Golden Age', text:'Paris has one of Europe\'s most vibrant English-language comedy scenes. Locals, expats, and tourists fill rooms every week. The future is bilingual — and very, very funny.' }
];

const COMEDY_QUOTES = [
    { text:'"The French think Americans are funny. Americans think the French are funny. I\'m here to prove them both right."', author:'Robert Hoehn' },
    { text:'"I moved to Paris for love. I stayed for the comedy."', author:'Sebastian Marx' },
    { text:'"La bise... how many? Two? Three? Four? Nobody knows. Not even the French."', author:'Paul Taylor' },
    { text:'"If you can make a French person laugh, you can do anything."', author:'Anonymous Paris Comic' },
    { text:'"Paris is the only city where your set can bomb in two languages simultaneously."', author:'FFCN Wisdom' },
    { text:'"Comedy is the universal language. Well, comedy and miming. But miming doesn\'t sell tickets."', author:'Paris Comedy' }
];

const TESTIMONIALS = [
    { text:'Best Wednesday night in Paris. Three shows, zero regrets.', author:'Laura M.', source:'Google Reviews' },
    { text:'I didn\'t know I needed bilingual comedy in my life until FFCN. Now I\'m addicted.', author:'Thomas K.', source:'Eventbrite' },
    { text:'Brought my French friends who barely speak English. They laughed harder than me.', author:'Mike R.', source:'TripAdvisor' },
    { text:'The open mic is genuinely good — not just \"open mic good.\" Real talent every week.', author:'Sophie L.', source:'Google Reviews' },
    { text:'Paname on a Tuesday is the cheat code for having a great week.', author:'David P.', source:'Instagram' }
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
        stats: { shows:'10+', showsLabel:'Weekly Shows', venues:'5+', venuesLabel:'Venues', bilingual:'FR+EN', bilingualLabel:'Bilingual', est:'~2010', estLabel:'Est.' },
        sections: { featuredShows:'Featured Shows', allShows:'All Shows', showsSub:'Stand-up, open mics — every week at venues across Paris', calendar:'Calendar', calendarSub:'Tap a day to see what\'s on', venues:'Venue Map', venuesSub:'Where the comedy happens in Paris', bookShow:'Book a Show', bookCTA:'Book a Private Show', newsletter:'Get Show Alerts', newsletterSub:'Weekly email with upcoming shows. No spam, just laughs.', subscribe:'Subscribe', quoteTitle:'Comedy Quote of the Week', videoTitle:'Latest Clips', supportTitle:'Support the Scene', testimonials:'What People Say' },
        filters: { all:'All', standup:'Stand-Up', openmic:'Open Mic' },
        footer: { copyright:'© 2026 Paris Comedy', tagline:'The Home of English-Language Comedy in Paris', contact:'Contact', legal:'Legal', privacy:'Privacy', terms:'Terms' },
        book: { perform:'Want to Perform?', performDesc:'Got 5 minutes of material and zero fear? Email us to get on a show.', corporate:'Book a Comedian', corporateDesc:'Corporate events, private parties, festivals — we\'ll match you with the perfect comic.', list:'List Your Show', listDesc:'Running an English comedy night in Paris? Get featured on pariscomedy.com for €1/month.', contact:'Get in Touch', name:'Your Name', email:'Email', message:'Message', send:'Send Message' },
        about: { title:'About Paris Comedy', what:'What is this?', team:'Who runs this?', teamDesc:'Paris Comedy is run by a team of comedy lovers who believe English-language comedy in Paris deserves a proper home on the internet.', contactUs:'Contact Us' },
        history: { title:'The History of English Comedy in Paris', intro:'From one New Yorker with a dream to 10+ weekly shows — how Paris became one of Europe\'s greatest English-language comedy cities.', keyPlayers:'Key Players', notableVisitors:'Notable Visitors', visitorsIntro:'International comedians who\'ve performed on Paris stages:' }
    },
    fr: {
        nav: { home:'Accueil', shows:'Spectacles', calendar:'Calendrier', history:'Histoire', venues:'Salles', book:'Réserver', about:'À propos' },
        hero: { info:'🎟️ Réservez votre place · 🍺 Une consommation minimum · 🎩 Le chapeau pour les artistes', tag:'🇫🇷 Comédie bilingue chaque semaine à Paris', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'Le Foyer de la Comédie en Anglais à Paris', desc:'Stand-up en français et anglais. Scènes ouvertes, showcases et le légendaire French Fried Comedy Night. Chaque semaine à Paris.', cta:'🎟️ Réservez Votre Place', browse:'Voir les Spectacles' },
        stats: { shows:'10+', showsLabel:'Spectacles/sem', venues:'5+', venuesLabel:'Salles', bilingual:'FR+EN', bilingualLabel:'Bilingue', est:'~2010', estLabel:'Depuis' },
        sections: { featuredShows:'Spectacles Vedettes', allShows:'Tous les Spectacles', showsSub:'Stand-up, scènes ouvertes — chaque semaine dans les salles de Paris', calendar:'Calendrier', calendarSub:'Cliquez sur un jour pour voir le programme', venues:'Carte des Salles', venuesSub:'Où se passe la comédie à Paris', bookShow:'Réserver un Spectacle', bookCTA:'Réserver un Spectacle Privé', newsletter:'Recevez les Alertes', newsletterSub:'Un email hebdo avec les prochains spectacles. Pas de spam, que des rires.', subscribe:'S\'abonner', quoteTitle:'Citation de la Semaine', videoTitle:'Derniers Clips', supportTitle:'Soutenez la Scène', testimonials:'Ce Qu\'on Dit' },
        filters: { all:'Tout', standup:'Stand-Up', openmic:'Scène Ouverte' },
        footer: { copyright:'© 2026 Paris Comedy', tagline:'Le Foyer de la Comédie en Anglais à Paris', contact:'Contact', legal:'Mentions Légales', privacy:'Confidentialité', terms:'CGU' },
        book: { perform:'Vous Voulez Monter sur Scène ?', performDesc:'Vous avez 5 minutes de matériel et zéro peur ? Écrivez-nous pour être programmé.', corporate:'Engager un Humoriste', corporateDesc:'Événements d\'entreprise, soirées privées, festivals — on vous trouve le comique parfait.', list:'Référencer Votre Spectacle', listDesc:'Vous organisez un spectacle de comédie en anglais à Paris ? Apparaissez sur pariscomedy.com pour 1€/mois.', contact:'Contactez-nous', name:'Votre Nom', email:'Email', message:'Message', send:'Envoyer' },
        about: { title:'À Propos de Paris Comedy', what:'C\'est quoi ?', team:'Qui gère ça ?', teamDesc:'Paris Comedy est géré par une équipe de passionnés de comédie qui pensent que l\'humour anglophone à Paris mérite une vraie maison sur internet.', contactUs:'Nous Contacter' },
        history: { title:'L\'Histoire de la Comédie Anglaise à Paris', intro:'D\'un New-Yorkais avec un rêve à plus de 10 spectacles hebdomadaires — comment Paris est devenue l\'une des grandes capitales européennes de la comédie en anglais.', keyPlayers:'Les Acteurs Clés', notableVisitors:'Visiteurs Notables', visitorsIntro:'Humoristes internationaux qui se sont produits sur les scènes parisiennes :' }
    },
    es: {
        nav: { home:'Inicio', shows:'Shows', calendar:'Calendario', history:'Historia', venues:'Locales', book:'Reservar', about:'Acerca de' },
        hero: { info:'🎟️ Reserva tu lugar · 🍺 Una consumición mínima · 🎩 El sombrero para los artistas', tag:'🇫🇷 Comedia bilingüe cada semana en París', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'El Hogar de la Comedia en Inglés en París', desc:'Stand-up en francés e inglés. Micros abiertos, showcases y la legendaria French Fried Comedy Night. Cada semana en París.', cta:'🎟️ Reserva Tu Lugar', browse:'Ver Shows' },

        stats: { shows:'10+', showsLabel:'Shows/sem', venues:'5+', venuesLabel:'Locales', bilingual:'FR+EN', bilingualLabel:'Bilingüe', est:'~2010', estLabel:'Desde' },
        sections: { featuredShows:'Shows Destacados', allShows:'Todos los Shows', showsSub:'Stand-up, micros abiertos — cada semana en locales de París', calendar:'Calendario', calendarSub:'Toca un día para ver la programación', venues:'Mapa de Locales', venuesSub:'Dónde pasa la comedia en París', bookShow:'Reservar un Show', bookCTA:'Reservar un Show Privado', newsletter:'Recibe Alertas', newsletterSub:'Email semanal con los próximos shows. Sin spam, solo risas.', subscribe:'Suscribirse', quoteTitle:'Frase de la Semana', videoTitle:'Últimos Clips', supportTitle:'Apoya la Escena', testimonials:'Lo Que Dicen' },
        filters: { all:'Todo', standup:'Stand-Up', openmic:'Micro Abierto' },
        footer: { copyright:'© 2026 Paris Comedy', tagline:'El Hogar de la Comedia en Inglés en París', contact:'Contacto', legal:'Legal', privacy:'Privacidad', terms:'Términos' },
        book: { perform:'¿Quieres Actuar?', performDesc:'¿Tienes 5 minutos de material y cero miedo? Escríbenos para subir al escenario.', corporate:'Contrata un Comediante', corporateDesc:'Eventos corporativos, fiestas privadas, festivales — te encontramos al cómico perfecto.', list:'Lista Tu Show', listDesc:'¿Organizas una noche de comedia en inglés en París? Aparece en pariscomedy.com por 1€/mes.', contact:'Contáctanos', name:'Tu Nombre', email:'Email', message:'Mensaje', send:'Enviar' },
        about: { title:'Sobre Paris Comedy', what:'¿Qué es esto?', team:'¿Quién lo gestiona?', teamDesc:'Paris Comedy está gestionado por un equipo de amantes de la comedia que creen que la comedia en inglés en París merece un hogar propio en internet.', contactUs:'Contáctanos' },
        history: { title:'La Historia de la Comedia en Inglés en París', intro:'De un neoyorquino con un sueño a más de 10 shows semanales — cómo París se convirtió en una de las grandes ciudades europeas de la comedia en inglés.', keyPlayers:'Protagonistas', notableVisitors:'Visitantes Notables', visitorsIntro:'Comediantes internacionales que han actuado en escenarios de París:' }
    },
    de: {
        nav: { home:'Startseite', shows:'Shows', calendar:'Kalender', history:'Geschichte', venues:'Veranstaltungsorte', book:'Show buchen', about:'Über uns' },
        hero: { info:'🎟️ Platz reservieren · 🍺 Ein Getränk Minimum · 🎩 Der Hut für die Künstler', tag:'🇫🇷 Zweisprachige Comedy jede Woche in Paris', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'Das Zuhause der englischsprachigen Comedy in Paris', desc:'Live-Stand-up auf Französisch & Englisch. Open Mics, Showcases und die legendäre French Fried Comedy Night. Jede Woche in Paris.', cta:'🎟️ Platz reservieren', browse:'Shows ansehen' },
        sections: { featuredShows:'Ausgewählte Shows', allShows:'Alle Shows', showsSub:'Stand-up, Open Mics — jede Woche in Pariser Venues', calendar:'Kalender', calendarSub:'Tippen Sie auf einen Tag', venues:'Venue-Karte', venuesSub:'Wo die Comedy in Paris stattfindet', bookShow:'Show buchen', bookCTA:'Private Show buchen', newsletter:'Show-Benachrichtigungen', newsletterSub:'Wöchentliche E-Mail mit kommenden Shows. Kein Spam, nur Lacher.', subscribe:'Abonnieren', quoteTitle:'Comedy-Zitat der Woche', videoTitle:'Neueste Clips', supportTitle:'Die Szene unterstützen', testimonials:'Was die Leute sagen' },
        filters: { all:'Alle', standup:'Stand-Up', openmic:'Open Mic' },
        footer: { copyright:'© 2026 Paris Comedy', tagline:'Das Zuhause der englischsprachigen Comedy in Paris', contact:'Kontakt', legal:'Impressum', privacy:'Datenschutz', terms:'AGB' }
    },
    ja: {
        nav: { home:'ホーム', shows:'ショー', calendar:'カレンダー', history:'歴史', venues:'会場', book:'ショーを予約', about:'概要' },
        hero: { tag:'🇫🇷 毎週パリでバイリンガルコメディ', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'パリの英語コメディの拠点', desc:'フランス語と英語のライブスタンドアップ。オープンマイク、ショーケース、伝説のFrench Fried Comedy Night。毎週パリで開催。', cta:'🎟️ 席を予約する', browse:'ショーを見る' },
        sections: { featuredShows:'注目のショー', allShows:'全ショー', showsSub:'スタンドアップ、オープンマイク — 毎週パリの会場で', calendar:'カレンダー', calendarSub:'日付をタップして詳細を見る', venues:'会場マップ', venuesSub:'パリのコメディ会場', bookShow:'ショーを予約', bookCTA:'プライベートショーを予約', newsletter:'ショー通知を受け取る', newsletterSub:'毎週のショー情報メール。スパムなし、笑いだけ。', subscribe:'登録', quoteTitle:'今週のコメディ名言', videoTitle:'最新クリップ', supportTitle:'シーンを応援する', testimonials:'みんなの声' },
        filters: { all:'すべて', standup:'スタンドアップ', openmic:'オープンマイク' },
        footer: { copyright:'© 2026 Paris Comedy', tagline:'パリの英語コメディの拠点', contact:'お問い合わせ', legal:'法的情報', privacy:'プライバシー', terms:'利用規約' }
    },
    zh: {
        nav: { home:'首页', shows:'演出', calendar:'日历', history:'历史', venues:'场地', book:'预订演出', about:'关于' },
        hero: { tag:'🇫🇷 每周在巴黎的双语喜剧', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'巴黎英语喜剧之家', desc:'法语和英语现场脱口秀。开放麦、展演和传奇的French Fried Comedy Night。每周在巴黎举办。', cta:'🎟️ 预订座位', browse:'浏览演出' },
        sections: { featuredShows:'精选演出', allShows:'所有演出', showsSub:'脱口秀、开放麦 — 每周在巴黎各场地', calendar:'日历', calendarSub:'点击日期查看详情', venues:'场地地图', venuesSub:'巴黎喜剧演出场地', bookShow:'预订演出', bookCTA:'预订私人演出', newsletter:'获取演出提醒', newsletterSub:'每周演出邮件。不发垃圾邮件，只有欢笑。', subscribe:'订阅', quoteTitle:'本周喜剧名言', videoTitle:'最新片段', supportTitle:'支持喜剧圈', testimonials:'观众评价' },
        filters: { all:'全部', standup:'脱口秀', openmic:'开放麦' },
        footer: { copyright:'© 2026 Paris Comedy', tagline:'巴黎英语喜剧之家', contact:'联系我们', legal:'法律信息', privacy:'隐私', terms:'条款' }
    },
    ko: {
        nav: { home:'홈', shows:'공연', calendar:'캘린더', history:'역사', venues:'공연장', book:'공연 예약', about:'소개' },
        hero: { tag:'🇫🇷 매주 파리에서 이중 언어 코미디', title:'Paris <span class="gradient-text">Comedy</span>', subtitle:'파리 영어 코미디의 본거지', desc:'프랑스어와 영어로 진행되는 라이브 스탠드업. 오픈 마이크, 쇼케이스, 그리고 전설의 French Fried Comedy Night. 매주 파리에서.', cta:'🎟️ 좌석 예약하기', browse:'공연 보기' },
        sections: { featuredShows:'추천 공연', allShows:'전체 공연', showsSub:'스탠드업, 오픈 마이크 — 매주 파리 공연장에서', calendar:'캘린더', calendarSub:'날짜를 탭하여 일정 확인', venues:'공연장 지도', venuesSub:'파리의 코미디 공연장', bookShow:'공연 예약', bookCTA:'프라이빗 공연 예약', newsletter:'공연 알림 받기', newsletterSub:'매주 공연 정보 이메일. 스팸 없이, 웃음만.', subscribe:'구독', quoteTitle:'이번 주 코미디 명언', videoTitle:'최신 클립', supportTitle:'씬 응원하기', testimonials:'관객 후기' },
        filters: { all:'전체', standup:'스탠드업', openmic:'오픈 마이크' },
        footer: { copyright:'© 2026 Paris Comedy', tagline:'파리 영어 코미디의 본거지', contact:'연락처', legal:'법적 정보', privacy:'개인정보', terms:'이용약관' }
    }
};

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
                    type:show.type, time:show.time, venue:VENUES.find(v=>v.id===show.venue)?.name||'', emoji:show.emoji
                });
            }
        });
    }
    return events;
}
