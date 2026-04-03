const VENUES = [
    { id:'velvet', name:'Velvet Bar', address:'39 Rue de Douai, 75009 Paris', neighborhood:'9th (Pigalle)', lat:48.8821, lng:2.3349, mapX:48, mapY:20 },
    { id:'paname', name:'Paname Art Café', address:'2bis Quai de la Loire, 75019 Paris', neighborhood:'19th', lat:48.8844, lng:2.3728, mapX:72, mapY:18 }
];

const SHOWS = [
    { id:'velvet-openmic', name:'Velvet Bar Comedy — Open Mic', shortName:'Open Mic', venue:'velvet', type:'openmic', day:'Wednesday', time:'19:00', price:'Free', emoji:'🎙️',
      description:'Sign up, step up, make them laugh. All levels welcome. The best open mic in Pigalle.',
      bookingUrl:'https://www.eventbrite.com/e/velvet-bar-comedy-open-mic-stand-up-comedy-a-paris-tickets-1977106148713', featured:false },
    { id:'velvet-comedy', name:'Velvet Bar Comedy — Le meilleur du stand-up', shortName:'Comedy Night', venue:'velvet', type:'standup', day:'Wednesday', time:'20:30', price:'€10', emoji:'🎭',
      description:'Curated showcase — the best comics in Paris on one stage. Bilingual, unpredictable, unforgettable.',
      bookingUrl:'https://www.eventbrite.com/e/velvet-bar-comedy-le-meilleur-du-stand-up-a-paris-tickets-1825871804719', featured:true },
    { id:'ffcn', name:'French Fried Comedy Night', shortName:'FFCN', venue:'velvet', type:'standup', day:'Wednesday', time:'22:00', price:'€10', emoji:'🍟',
      description:'THE bilingual comedy show. American & French comics, English & French jokes, same night. The show that started it all.',
      bookingUrl:'https://www.eventbrite.com/e/french-fried-comedy-night-tickets-603182383747', featured:true },
    { id:'paname', name:'Paname Comedy', shortName:'Paname', venue:'paname', type:'standup', day:'Tuesday', time:'17:30', price:'€8', emoji:'🎤',
      description:'Live comedy at one of Paris\'s legendary stages overlooking Canal Saint-Martin.',
      bookingUrl:'https://www.eventbrite.com/e/french-fried-comedy-night-tickets-603182383747', featured:false }
];

const APRIL_2026 = (() => {
    const events = [];
    const dayMap = { 'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5,'Saturday':6,'Sunday':0 };
    const specificDates = [
        { day:7, showId:'paname' }, { day:8, showId:'velvet-openmic' }, { day:8, showId:'velvet-comedy' }, { day:8, showId:'ffcn' },
        { day:15, showId:'paname' }, { day:15, showId:'velvet-openmic' }, { day:15, showId:'velvet-comedy' }, { day:15, showId:'ffcn' },
        { day:22, showId:'velvet-openmic' }, { day:22, showId:'velvet-comedy' }, { day:22, showId:'ffcn' },
        { day:25, showId:'paname' },
        { day:29, showId:'velvet-openmic' }, { day:29, showId:'velvet-comedy' }, { day:29, showId:'ffcn' }
    ];
    specificDates.forEach(sd => {
        const show = SHOWS.find(s => s.id === sd.showId);
        if (show) {
            events.push({ day:sd.day, showId:show.id, showName:show.name, shortName:show.shortName,
                type:show.type, time:show.time, venue:VENUES.find(v=>v.id===show.venue)?.name||'', emoji:show.emoji });
        }
    });
    return events;
})();
