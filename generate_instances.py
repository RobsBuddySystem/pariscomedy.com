#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
import re

# Today in Paris time (2026-05-19)
today = datetime(2026, 5, 19)
end_date = today + timedelta(days=30)

# Weekday name -> weekday number (Mon=0)
WEEKDAY_MAP = {
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
    'Friday': 4, 'Saturday': 5, 'Sunday': 6,
    'daily': list(range(7))
}

# The shows from js/data.js — copied here for Python processing
# IMPORTANT: Do NOT include paname-archive (archived:true)
RECURRING_SHOWS = [
    # SHOWS array
    {"id":"velvet-openmic","name":"Velvet Bar Comedy — Open Mic","venueName":"Velvet Bar","address":"43 Rue Saint-Honoré, 75001 Paris","neighborhood":"Les Halles (1er)","day":"Wednesday","time":"19:00","bookingUrl":"https://www.eventbrite.com/e/velvet-bar-comedy-open-mic-stand-up-comedy-a-paris-tickets-1977106148713","featured":False,"type":"openmic"},
    {"id":"velvet-comedy","name":"Velvet Bar Comedy — Le meilleur du stand-up","venueName":"Velvet Bar","address":"43 Rue Saint-Honoré, 75001 Paris","neighborhood":"Les Halles (1er)","day":"Wednesday","time":"20:30","bookingUrl":"https://www.eventbrite.com/e/velvet-bar-comedy-le-meilleur-du-stand-up-a-paris-tickets-1989840111338","featured":True,"type":"standup"},
    {"id":"ffcn","name":"French Fried Comedy Night","venueName":"Velvet Bar","address":"43 Rue Saint-Honoré, 75001 Paris","neighborhood":"Les Halles (1er)","day":"Wednesday","time":"22:00","bookingUrl":"https://www.eventbrite.com/e/french-fried-comedy-night-tickets-603182383747","featured":True,"type":"standup"},
    # OTHER_SHOWS_RAW
    {"id":"kuhl-open-mic","name":"Kuhl Comedy Open Mic","venueName":"Toloache","address":"Paris","neighborhood":"","day":"Tuesday","time":"19:30","bookingUrl":"https://www.eventbrite.fr/e/stand-up-open-mic-in-english-by-kuhl-comedy-tickets-1760885549079","featured":False,"type":"openmic"},
    {"id":"green-light","name":"Green Light Comedy","venueName":"Les Marquises","address":"Paris","neighborhood":"","day":"Tuesday","time":"20:15","bookingUrl":"https://www.eventbrite.fr/e/standup-comedy-in-english-green-light-in-paris-tickets-927454971787","featured":False,"type":"standup"},
    {"id":"cuba-compagnie","name":"Cuba Compagnie Comedy Club","venueName":"Cuba Compagnie","address":"48 Bd Beaumarchais, 75011 Paris","neighborhood":"Bastille (11th)","day":"Tuesday","time":"19:30","bookingUrl":"https://www.eventbrite.fr/e/cuba-compagnie-comedy-club-tickets-1254791257429","featured":False,"type":"standup"},
    {"id":"funny-women","name":"Funny Women Paris","venueName":"Le Noddi","address":"16 Rue Bernardins, 75005 Paris","neighborhood":"Latin Quarter (5th)","day":"Tuesday","time":"20:30","bookingUrl":"https://www.eventbrite.fr/e/english-stand-up-comedy-in-paris-funny-women-tickets-295960655287","featured":False,"type":"standup"},
    {"id":"rocket","name":"Rocket Comedy Club","venueName":"Cotte 23","address":"23 Rue de la Mare, 75020 Paris","neighborhood":"Belleville (20th)","day":"Tuesday","time":"19:00","bookingUrl":"https://www.eventbrite.fr/e/rocket-comedy-club-tickets-1001216875627","featured":False,"type":"standup"},
    {"id":"lofi","name":"LOFI Comedy Club","venueName":"Fada Paris","address":"Paris","neighborhood":"","day":"Tuesday","time":"19:00","bookingUrl":"https://www.eventbrite.com/e/lofi-comedy-club-2-tickets-1982107345427","featured":False,"type":"standup"},
    {"id":"comedy-crush","name":"Comedy Crush Wednesday Show","venueName":"Les Cariatiades","address":"Paris","neighborhood":"","day":"Wednesday","time":"20:30","bookingUrl":"https://www.eventbrite.fr/e/comedy-crushs-wednesday-show-tickets-1982356098454","featured":False,"type":"standup"},
    {"id":"millennial-meltdown","name":"Millennial Meltdown","venueName":"Le Bikini Bottom","address":"49 Rue de Lappe, 75011 Paris","neighborhood":"Bastille (11th)","day":"Wednesday","time":"20:00","bookingUrl":"https://www.eventbrite.fr/e/billets-english-comedy-show-millennial-meltdown-paris-stand-up-night-1984665294321","featured":False,"type":"standup"},
    {"id":"dissident","name":"The Dissident Comedy Show","venueName":"The Dissident Club","address":"58 Rue Richer, 75009 Paris","neighborhood":"Grands Boulevards (9th)","day":"Wednesday","time":"20:30","bookingUrl":"https://www.eventbrite.fr/e/the-dissident-comedy-show-tickets-1985334998424","featured":False,"type":"standup"},
    {"id":"mic-drop","name":"Mic Drop Comedy Club","venueName":"Speechless","address":"45 Rue de Montreuil, 75011 Paris","neighborhood":"Nation (11th)","day":"Wednesday","time":"20:00","bookingUrl":"https://www.eventbrite.com/e/mic-drop-comedy-club-tickets-1982353596972","featured":False,"type":"standup"},
    {"id":"mango","name":"MANGO English Stand-Up","venueName":"Le Paris de l'Humour","address":"Paris","neighborhood":"","day":"Wednesday","time":"19:45","bookingUrl":"https://www.eventbrite.ca/e/mango-english-stand-up-comedy-in-paris-randy-j-dreams-tickets-1984868292494","featured":False,"type":"standup"},
    {"id":"wednesday-night-comedy","name":"Wednesday Night Comedy","venueName":"La Pomme d'Eve","address":"1 Rue des Boulangers, 75005 Paris","neighborhood":"Latin Quarter (5th)","day":"Wednesday","time":"19:30","bookingUrl":"https://www.eventbrite.fr/e/english-standup-wednesday-night-comedy-tickets-1750646975229","featured":False,"type":"standup"},
    {"id":"kiss-comedy","name":"Kiss Comedy Club","venueName":"Le Coquin","address":"Paris","neighborhood":"","day":"Wednesday","time":"20:00","bookingUrl":"https://www.eventbrite.fr/e/kiss-comedy-club-tickets-1935245083139","featured":False,"type":"standup"},
    {"id":"south-comedy","name":"South Comedy Club","venueName":"Comédie Café","address":"Paris","neighborhood":"","day":"Wednesday","time":"20:00","bookingUrl":"https://www.eventbrite.fr/e/billets-south-comedy-club-1716456721259","featured":False,"type":"standup"},
    {"id":"theatre-bo-julie","name":"Oh My God She's Parisian! — Julie Coulon","venueName":"Théâtre BO Saint-Martin","address":"19 Boulevard Saint-Martin, 75003 Paris","neighborhood":"République (3rd)","day":["Friday","Saturday"],"time":"20:15","bookingUrl":"https://www.eventbrite.fr/e/the-comedy-in-english-by-a-french-girl-that-will-make-you-love-paris-tickets-1764207685679","featured":True,"type":"standup"},
    {"id":"fiap","name":"FIAP Comedy Club","venueName":"FIAP Paris","address":"30 Rue Cabanis, 75014 Paris","neighborhood":"14th arrondissement","day":"Thursday","time":"19:30","bookingUrl":"https://www.eventbrite.fr/e/fiap-comedy-club-tickets-1986207987558","featured":False,"type":"standup"},
    {"id":"englishman-night","name":"The Englishman Comedy Night","venueName":"The Englishman Cocktail Club","address":"Paris","neighborhood":"","day":"Thursday","time":"20:00","bookingUrl":"https://www.eventbrite.com/e/the-englishman-comedy-night-tickets-1982274965784","featured":False,"type":"standup"},
    {"id":"greenwashing","name":"Greenwashing Comedy Club","venueName":"Césure","address":"Paris","neighborhood":"","day":"Thursday","time":"20:00","bookingUrl":"https://www.eventbrite.fr/e/greenwashing-comedy-club-a-cesure-tickets-1984380900692","featured":False,"type":"standup"},
    {"id":"sparkle","name":"Sparkle Comedy Club","venueName":"Le TLM Paris","address":"Paris","neighborhood":"","day":"Thursday","time":"21:00","bookingUrl":"https://www.eventbrite.fr/e/sparkle-comedy-club-tickets-1985497313914","featured":False,"type":"standup"},
    {"id":"comedy-lab-chat-noir","name":"Comedy Lab","venueName":"Chat Noir","address":"76 Rue Jean-Pierre Timbaud, 75011 Paris","neighborhood":"Oberkampf (11th)","day":["Thursday","Saturday"],"time":"20:00","bookingUrl":"https://www.eventbrite.com/e/english-stand-up-comedy-in-paris-thursday-saturday-night-shows-tickets-77709323679","featured":False,"type":"standup"},
    {"id":"green-mic-showcase","name":"Green Mic Showcase","venueName":"Au Soleil de la Butte","address":"32 Rue Muller, 75018 Paris","neighborhood":"Montmartre (18th)","day":"Friday","time":"20:30","bookingUrl":"https://www.eventbrite.fr/e/billets-standup-comedy-in-english-green-mic-showcase-montmartre-573952757147","featured":True,"type":"standup"},
    {"id":"coucou-friday","name":"English Stand-Up Comedy in Paris — Friday Night Show","venueName":"La Pomme d'Eve","address":"1 Rue Laplace, 75005 Paris","neighborhood":"Latin Quarter (5th)","day":"Friday","time":"20:30","bookingUrl":"https://www.eventbrite.fr/e/english-stand-up-comedy-in-paris-friday-night-show-tickets-364336088047","featured":False,"type":"standup"},
    {"id":"open-mic-express","name":"The Open Mic Express","venueName":"Le Kibélé","address":"12 Rue de l'Éperon, 75006 Paris","neighborhood":"Saint-Germain (6th)","day":"Friday","time":"19:00","bookingUrl":"https://www.eventbrite.com/e/the-open-mic-express-english-stand-up-comedy-april-17-tickets-1985629550437","featured":False,"type":"openmic"},
    {"id":"kinto","name":"Kinto Comedy Club","venueName":"Poinçon Paris","address":"Paris","neighborhood":"","day":"Friday","time":"19:30","bookingUrl":"https://www.eventbrite.fr/e/kinto-comedy-club-au-poincon-tickets-1981428458859","featured":False,"type":"standup"},
    {"id":"smash","name":"Smash Comedy Club","venueName":"Comédie Café","address":"Paris","neighborhood":"","day":"Saturday","time":"19:00","bookingUrl":"https://www.eventbrite.com/e/smash-comedy-club-tickets-1902240916789","featured":False,"type":"standup"},
    {"id":"integrire","name":"IntégRire Comedy Night","venueName":"Le Kibélé","address":"12 Rue de l'Éperon, 75006 Paris","neighborhood":"Saint-Germain (6th)","day":"Saturday","time":"19:00","bookingUrl":"https://www.eventbrite.fr/e/integrire-comedy-night-3-tickets-1986334225138","featured":False,"type":"standup"},
    {"id":"blast-off","name":"Blast Off All Stars","venueName":"La Pomme d'Eve","address":"1 Rue des Boulangers, 75005 Paris","neighborhood":"Latin Quarter (5th)","day":"Saturday","time":"19:30","bookingUrl":"https://www.eventbrite.com/e/blast-off-all-stars-english-stand-up-comedy-april-25-tickets-1986150988071","featured":False,"type":"standup"},
    {"id":"charonne","name":"Charonne Comedy Club","venueName":"Le Café de la Plage","address":"Paris","neighborhood":"","day":"Saturday","time":"19:30","bookingUrl":"https://www.eventbrite.fr/e/charonne-comedy-club-tickets-1697805324429","featured":False,"type":"standup"},
    {"id":"oscar","name":"Oscar Comedy Club","venueName":"Café Oscar","address":"Paris","neighborhood":"","day":"Sunday","time":"17:00","bookingUrl":"https://www.eventbrite.fr/e/oscar-comedy-club-tickets-1985916648154","featured":False,"type":"standup"},
    {"id":"green-mic-sunday","name":"Green Mic Comedy Show","venueName":"Ma Cocotte du Faubourg","address":"5 Rue du Faubourg Montmartre, 75009 Paris","neighborhood":"Grands Boulevards (9th)","day":"Sunday","time":"19:30","bookingUrl":"https://www.eventbrite.fr/e/green-mic-comedy-show-tickets-214634947907","featured":False,"type":"standup"},
    {"id":"broadway-comedy-club","name":"Broadway Comedy Club - Paris","venueName":"25 Bd de Bonne Nouvelle","address":"25 Bd de Bonne Nouvelle, 75002 Paris","neighborhood":"Bonne Nouvelle (2nd)","day":"daily","time":"19:00","bookingUrl":"https://www.eventbrite.com/e/billets-broadway-comedy-club-paris-1978410990530","featured":False,"type":"standup"},
]

instances = []
last_checked = "2026-05-19T00:00:00+02:00"

for show in RECURRING_SHOWS:
    days = show['day']
    if days == 'daily':
        target_weekdays = list(range(7))
    elif isinstance(days, list):
        target_weekdays = [WEEKDAY_MAP[d] for d in days]
    else:
        target_weekdays = [WEEKDAY_MAP[days]]

    h, m = map(int, show['time'].split(':'))

    # Generate all occurrences in next 30 days
    current = today
    while current <= end_date:
        if current.weekday() in target_weekdays:
            start_dt = current.replace(hour=h, minute=m, second=0)
            # Skip if already past for today
            if current == today and h < 12:  # morning shows already past
                current += timedelta(days=1)
                continue

            instance = {
                "id": f"{show['id']}-{current.strftime('%Y%m%d')}",
                "recurring_id": show['id'],
                "name": show['name'],
                "venue_name": show['venueName'],
                "address": show.get('address', ''),
                "neighborhood": show.get('neighborhood', ''),
                "start_date": start_dt.strftime('%Y-%m-%dT') + show['time'] + ':00+02:00',
                "end_date": None,
                "time": show['time'],
                "booking_url": show['bookingUrl'],
                "source_url": show['bookingUrl'],
                "last_checked": last_checked,
                "recurring_source": True,
                "featured": show.get('featured', False),
                "type": show.get('type', 'standup'),
                "is_archived": False,
                "langs": ["en"],
            }
            instances.append(instance)
        current += timedelta(days=1)

# Sort by start_date
instances.sort(key=lambda x: x['start_date'])

print(f"Generated {len(instances)} instances from {len(RECURRING_SHOWS)} recurring shows")

with open('data/shows_generated.json', 'w') as f:
    json.dump(instances, f, indent=2, ensure_ascii=False)

print("Written to data/shows_generated.json")

# Count by section
tonight_date = today.strftime('%Y-%m-%d')
this_week_end = (today + timedelta(days=7)).strftime('%Y-%m-%d')
tonight = [i for i in instances if i['start_date'].startswith(tonight_date)]
this_week = [i for i in instances if tonight_date <= i['start_date'][:10] <= this_week_end]
print(f"Tonight: {len(tonight)}, This week: {len(this_week)}, All upcoming: {len(instances)}")

# Neighborhood coverage
with_neighborhood = [i for i in instances if i['neighborhood']]
print(f"Neighborhood coverage: {len(with_neighborhood)}/{len(instances)} = {len(with_neighborhood)/len(instances)*100:.1f}%")

# First 10
print("\nFirst 10 instances:")
for inst in instances[:10]:
    print(f"  {inst['start_date'][:10]} {inst['time']} — {inst['name']}")
