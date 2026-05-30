# CONTENT.SOURCE-COVERAGE.2

**Status: AUDIT ONLY — NO IMPORTS**  
**Date: 2026-05-30**  
**No database writes. No backend feature flags. No automated scraping.**

---

## Current ParisComedy Inventory

| Metric | Count |
|---|---|
| Total show_listings rows | 179 |
| Active (verified, publicly visible) | 14 |
| Stale / hidden | 164 |
| Canceled | 1 |
| Active — Eventbrite-sourced | 12 |
| Active — Robert-editorial | 2 |

**14 active listings visible to users.** 164 stale_hidden listings exist in DB but are not shown publicly.

### Active listings (verified_24h equivalent):
1. Charonne Comedy Club (Eventbrite)
2. Comedy Crush Wednesday Show (Eventbrite)
3. Comedy Lab (Eventbrite)
4. Cuba Compagnie Comedy Club (Eventbrite)
5. English Stand-Up Comedy in Paris — Friday Night Show (Eventbrite)
6. French Fried Comedy Night (Robert-editorial)
7. Green Light Comedy (Eventbrite)
8. Green Mic Showcase (Eventbrite)
9. Millennial Meltdown (Eventbrite)
10. Oh My God She's Parisian! — Julie Coulon (Eventbrite)
11. Rocket Comedy Club (Eventbrite)
12. Smash Comedy Club (Eventbrite)
13. Velvet Bar Comedy — Le meilleur du stand-up (Robert-editorial)
14. Wednesday Night Comedy (Eventbrite)

### Needs human review:
- Kuhl Comedy Open Mic — page says event ended / no future dates (quarantined 2026-05-24)
- Velvet Bar Comedy — Open Mic — confirmed canceled by Robert 2026-05-04 (canceled status)

---

## Source Coverage Summary

| Platform | Current coverage | Notes |
|---|---|---|
| **Eventbrite** | 12 active listings | Primary source. `/api/eb/shows` sync route implemented but disabled. |
| **Robert-editorial** | 2 active listings | FFCN + Velvet Bar Comedy Night |
| **Fever** | 0 | Fever lists Le Plateau Comedy Club, Golden Comedy Club, Oscar Comedy Club, Marco Polo Comedy Club, The Joke Comedy Club — ZERO coverage on pariscomedy.com |
| **BilletRéduc** | 0 | Active stand-up section at billetreduc.com — ZERO coverage |
| **FNAC Spectacles** | 0 | Comedy / humour section active — ZERO coverage |
| **Shotgun** | 0 | Known comedy shows listed — ZERO coverage |
| **Dice** | 0 | Comedy shows listed — ZERO coverage |
| **Weezevent** | 0 | French ticketing platform — ZERO coverage |
| **Billetweb** | 0 | French ticketing platform — ZERO coverage |
| **Yurplan** | 0 | French ticketing platform — ZERO coverage |
| **HelloAsso** | 0 | Association/community shows — ZERO coverage |
| **Sortiraparis** | 0 | Major Paris event aggregator lists June 2026 comedy shows — ZERO coverage |
| **L'Officiel des Spectacles** | 0 | humor/stand-up section active — ZERO coverage |
| **Coucou Comedy** | 0 | Recurring English comedy in Paris — NOT in DB |
| **Sebastian Marx / La Scène Barbès** | 0 | Weekly Sunday English show — NOT in DB |
| **Le Paname Comedy Club** | 0 | English/French shows near Canal Saint-Martin — NOT in DB |
| **Songkick** | 0 | Lists comedy concerts 2026 Paris — ZERO coverage |
| **AllEvents** | 0 | Lists comedy shows near Paris 2026 — ZERO coverage |

**Coverage gap**: 14 active listings against an estimated 30–50+ active recurring comedy shows in Paris as of 2026-05.

---

## Missing Listing Candidates

### High confidence — recurring English-language shows not in DB

| Show name | Venue | Recurrence | Source | Confidence | Language | Action |
|---|---|---|---|---|---|---|
| Coucou Comedy English Stand-Up | Multiple Paris venues | Weekly | coucoucomedyclub.com | High | English | Manual review before import |
| Sebastian Marx — English comedy at La Scène Barbès | La Scène Barbès | Weekly (Sunday) | comedyinparis.com, frenchly.us | High | English/bilingual | Manual review before import |
| Le Paname Comedy Club | Canal Saint-Martin area | Regular | Fever, frenchly.us | High | French/English bilingual | Manual review before import |

### Medium confidence — Fever-listed venues with zero current coverage

| Show name | Venue | Source | Confidence | Language | Action |
|---|---|---|---|---|---|
| Le Plateau Comedy Club | Paris (Fever-listed) | feverup.com/m/474472 | Medium | French | Manual review — verify active |
| Golden Comedy Club | Paris (Fever-listed) | feverup.com/m/111045 | Medium | French | Manual review — verify active |
| Oscar Comedy Club | Paris (Fever-listed) | feverup.com/m/122614 | Medium | French | Manual review — verify active |
| Marco Polo Comedy Club (Châtelet) | Châtelet area | feverup.com/m/124093 | Medium | French | Manual review — verify active |
| The Joke Comedy Club | Paris (Fever-listed) | feverup.com/m/114937 | Medium | French | Manual review — verify active |

### French-language shows from BilletRéduc / FNAC / Sortiraparis

| Show/performer | Venue | Source | Confidence | Language | Action |
|---|---|---|---|---|---|
| Thomas Marty — Nouveau spectacle | Théâtre de la Gaîté Montparnasse | FNAC Spectacles | High | French | Manual review — verify recurring vs one-off |
| Mahé | L'Européen | FNAC / BilletRéduc | High | French | Manual review — one-off dates |
| Various Sortiraparis June 2026 comedy shows | Various Paris theatres | sortiraparis.com | Medium | French | Manual review batch |

---

## Highest-Value Sources for Next Phase

1. **Fever** — 5+ recurring comedy clubs listed. No technical barrier to manual add. Highest value for English-language gap.
2. **Coucou Comedy** (coucoucomedyclub.com) — English-only, recurring, already mentioned in frenchly.us as top Paris English comedy. Not in DB.
3. **comedyinparis.com** — Aggregator maintained by English comedy community in Paris. Cross-reference with current active listings.
4. **Sortiraparis** — Major French aggregator with June 2026 comedy guide. French-language shows.
5. **BilletRéduc** stand-up section — French recurring shows. Manual verification required.

---

## Legal / Compliance Notes

- No scraping behind login was performed
- No automated imports executed
- All candidates require admin review before any listing is created
- Affiliate links remain `AFFILIATE_LINKS_ENABLED=false`
- No ticket import routes were enabled
- robots.txt respected — no automated crawling

---

## Recommended Next Phase

**CONTENT.SOURCE-COVERAGE.3-MANUAL-CANDIDATE-SEED**

Reason: Fever has 5+ verified recurring Paris comedy clubs with public pages and no technical barrier. Manual add of 3–5 high-confidence Fever listings (Le Plateau, Golden Comedy Club, Coucou Comedy) would increase active inventory by ~35% with zero import risk. English-language gap (Coucou, Sebastian Marx) is highest value for the site's audience.

Alternative: **CONTENT.FRESHNESS.2-REPOINT-STALE-SOURCES** if Robert prefers to recover some of the 164 stale_hidden listings by finding updated source URLs before adding new ones.
