# CONTENT.SOURCE-COVERAGE.2B — Candidate Details

**Status: AUDIT ONLY — NO IMPORTS**  
**Date: 2026-05-30**  
**Candidate count: 12**

---

## Candidate Table

| ID | Show name | Venue | Address | Recurrence | Platform | Source URL | Language | Confidence | Recommendation | Duplicate? |
|---|---|---|---|---|---|---|---|---|---|---|
| C001 | Coucou Comedy — Tuesday | Le Noddi | 16 Rue Bernardins, 75005 | 1st + 3rd Tuesday | Eventbrite + coucoucomedyclub.com | [Eventbrite](https://www.eventbrite.com/o/coucou-comedy-43230488853) | en | 90 | manual_review | no_match |
| C002 | Coucou Comedy — Friday | Broadway Comedy Club | 25 Bd de Bonne Nouvelle, 75002 | Fridays recurring | Eventbrite + coucoucomedyclub.com | [Eventbrite](https://www.eventbrite.com/o/coucou-comedy-43230488853) | en | 85 | manual_review | no_match |
| C003 | Sebastian Marx — NY Comedy Night | La Scène Barbès | 18 Bd Barbès, 75018 | Weekly Sundays | sebmarx.com + comedyinparis.com | [sebmarx.com](https://www.sebmarx.com/en/) | en/bilingual | 80 | manual_review | no_match |
| C004 | Paname Comedy Club | Paname Art Cafe | Canal Saint-Martin, Paris | Daily (multiple sessions); runs through June 30, 2026 | FNAC Spectacles | [FNAC](https://www.fnacspectacles.com/artist/paname-comedy-club/paname-comedy-club-paris-3410304/) | fr | 88 | manual_review | no_match |
| C005 | Golden Comedy Club | Golden Comedy Spot | 36 rue Dalayrac, 75002 | 7 days/week through Dec 30, 2026 | Fever + BilletRéduc | [Fever](https://feverup.com/m/111045/en) · [BilletRéduc](https://www.billetreduc.com/spectacle/golden-comedy-club-299705) | fr | 92 | manual_review | no_match |
| C006 | Oscar Comedy Club | Café Oscar | 155 Rue Montmartre, 75002 | Nightly through June 30, 2026 | Fever + Eventbrite + BilletRéduc | [Eventbrite](https://www.eventbrite.fr/e/oscar-comedy-club-tickets-1672589683769) · [Fever](https://feverup.com/m/122614/en) | fr | 88 | manual_review | no_match |
| C007 | Marco Polo Comedy Club | Bistrot du Jardin | 33 Rue Berger, 75001 (Châtelet) | Recurring sessions; verify if extended past April 2026 | Fever + agendaculturel.fr | [Fever](https://feverup.com/m/124093/en) · [agendaculturel](https://75.agendaculturel.fr/marco-polo-comedy-club) | fr | 65 | future_watch | no_match |
| C008 | The Joke Comedy Club | The Joke | 37 rue Quincampoix, 75004 | Recurring nightly | Fever + BilletRéduc | [Fever](https://feverup.com/en/paris/venue/the-joke) · [BilletRéduc](https://www.billetreduc.com/spectacle/the-joke-comedy-club-290613) | fr | 82 | manual_review | no_match |
| C009 | Le Plateau Comedy Club | Monsieur le Zinc | 16 Rue de Mazagran, 75010 | Recurring 8:30–10pm | Fever | [Fever](https://feverup.com/m/474472/en) | fr | 78 | manual_review | no_match |
| C010 | Le Fridge Comedy Night | Le Fridge Comedy | Paris 2nd arr. | Recurring evenings | BilletRéduc + lefridgecomedy.com | [BilletRéduc](https://www.billetreduc.com/263384/evt.htm) · [Website](https://lefridgecomedy.com/) | fr | 75 | manual_review | no_match |
| C011 | Fridge Open Mic | Le Fridge Comedy | Paris 2nd arr. | Every weekend at 15:45 | BilletRéduc + lefridgecomedy.com | [BilletRéduc](https://www.billetreduc.com/263450/evt.htm) · [Website](https://lefridgecomedy.com/open-mics-reservation/) | fr | 72 | manual_review | no_match |
| C012 | No Name Comedy Club | Comédie Café | Paris | Recurring open mic | BilletRéduc | [BilletRéduc](https://www.billetreduc.com/263800/evt.htm) | fr | 65 | future_watch | no_match |

---

## Top 5 High-Confidence Candidates

1. **C005 — Golden Comedy Club** (92) — Daily, 7 days/week through Dec 2026. French. Fever + BilletRéduc.
2. **C001 — Coucou Comedy Tuesday** (90) — English, recurring 1st/3rd Tuesday. Primary English gap. Eventbrite-ticketed.
3. **C004 — Paname Comedy Club** (88) — French, multiple sessions/day. FNAC Spectacles. Major tour show.
4. **C006 — Oscar Comedy Club** (88) — French, oldest comedy club in Paris. Nightly through June. Eventbrite + Fever.
5. **C002 — Coucou Comedy Friday** (85) — English, Friday recurring. Same organizer as C001.

---

## Duplicate Check Summary

0 of 12 candidates overlap with current 14 active listings. Current active listings are:
- Charonne, Comedy Crush, Comedy Lab, Cuba Compagnie, English Stand-Up Friday, FFCN, Green Light, Green Mic Showcase, Millennial Meltdown, Oh My God She's Parisian!, Rocket Comedy Club, Smash Comedy Club, Velvet Bar, Wednesday Night Comedy

No duplicates detected.

---

## Compliance Notes

- No scraping behind login performed
- Instagram not used as import source (appears in notes as signal-only for C011)
- All 12 candidates sourced from public ticket pages (Fever, Eventbrite, BilletRéduc, FNAC Spectacles, venue websites)
- All 12 recommendations are `manual_review` or `future_watch` — no `auto-import` recommendation used
- Affiliate links remain `AFFILIATE_LINKS_ENABLED=false`
- No ticket import routes were enabled

---

## Rollback Command

```bash
git revert HEAD  # docs only — no DB changes were made
```
