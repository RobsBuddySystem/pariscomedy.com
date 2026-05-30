# CONTENT.SOURCE-COVERAGE.4 — Manual Review Packet for Robert

**For: Robert (operator)**  
**Status: REVIEW PACKET ONLY — NO PUBLIC IMPORT**  
**Date: 2026-05-30**

> ⚠️ **Approval here does NOT auto-publish.** If you approve a candidate, Claude must create a separate manual import phase and ChatGPT must verify proof before any listing appears publicly.

---

## What This Is

9 candidate Paris comedy shows identified from public ticket sources (Fever, Eventbrite, BilletRéduc, FNAC Spectacles). None are in the current database. None have been imported. Your job: mark each one as approve / reject / needs more research / future watch.

---

## Allowed Decisions per Candidate

- **approve_for_manual_import** — You've verified the source, the show is current, and you want it added
- **reject** — Not a fit for the site
- **needs_more_research** — Uncertain — needs more info before deciding
- **future_watch** — Real show, not urgent, revisit later

---

## Minimum Data Required Before Any Import Can Happen

For any approved candidate, Claude needs to confirm:
- Show name (final)
- Venue name + full address
- Next date or recurrence (day of week + time)
- Start time
- Language (en / fr / bilingual)
- Primary ticket or source URL
- Date source was verified
- No duplicate confirmation

---

## Do NOT Import If

- Date or recurrence unclear
- Source page is stale / no upcoming events listed
- Source is only a blog or guide (no primary ticket source)
- Possible duplicate of existing listing
- Venue or address unclear
- Language unclear
- Ticket URL returns 404 or no upcoming dates

---

## Candidate Review Sections

---

### S001 — Coucou Comedy (Tuesday)

| Field | Value |
|---|---|
| Show name | Coucou Comedy — Tuesday English Stand-Up |
| Venue | Le Noddi, 16 Rue Bernardins, 75005 Paris |
| Recurrence | 1st + 3rd Tuesday of each month |
| Language | English |
| Confidence | 90 |
| Source URL | https://www.eventbrite.com/o/coucou-comedy-43230488853 |
| Platform | Eventbrite + coucoucomedyclub.com |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- Is the listing still current? (Check Eventbrite for upcoming dates)
- Is Le Noddi still the venue? (Verify at coucoucomedyclub.com)

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S002 — Coucou Comedy (Friday)

| Field | Value |
|---|---|
| Show name | Coucou Comedy — Friday English Stand-Up |
| Venue | Broadway Comedy Club, 25 Bd de Bonne Nouvelle, 75002 Paris |
| Recurrence | Fridays recurring |
| Language | English |
| Confidence | 85 |
| Source URL | https://www.eventbrite.com/o/coucou-comedy-43230488853 |
| Platform | Eventbrite + coucoucomedyclub.com |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- Is the Friday show at Broadway Comedy Club still running?
- Should this and S001 be listed as one entry or two?

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S003 — Sebastian Marx — NY Comedy Night

| Field | Value |
|---|---|
| Show name | Sebastian Marx — New York Comedy Night |
| Venue | La Scène Barbès, 18 Bd Barbès, 75018 Paris |
| Recurrence | Weekly Sundays |
| Language | English / bilingual |
| Confidence | 80 |
| Source URL | https://www.sebmarx.com/en/ |
| Platform | sebmarx.com + comedyinparis.com |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- Is the Sunday show still running at La Scène Barbès?
- Does sebmarx.com have a primary ticket link? (Verify before import)

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S004 — Paname Comedy Club

| Field | Value |
|---|---|
| Show name | Paname Comedy Club |
| Venue | Paname Art Cafe |
| Recurrence | Multiple sessions daily; through June 30, 2026 |
| Language | French |
| Confidence | 88 |
| Source URL | https://www.fnacspectacles.com/artist/paname-comedy-club/paname-comedy-club-paris-3410304/ |
| Secondary URL | https://www.panameartcafe.com/programmation/paname-comedy-club |
| Platform | FNAC Spectacles |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- Is the Paris run still on sale? (Verify dates on FNAC)
- Is French-only OK for the site's audience?

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S005 — Golden Comedy Club

| Field | Value |
|---|---|
| Show name | Golden Comedy Club |
| Venue | Golden Comedy Spot, 36 rue Dalayrac, 75002 Paris |
| Recurrence | 7 days/week, through December 30, 2026 |
| Language | French |
| Confidence | 92 |
| Source URL | https://feverup.com/m/111045/en |
| Secondary URL | https://www.billetreduc.com/spectacle/golden-comedy-club-299705 |
| Platform | Fever + BilletRéduc |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- Is the typical show time known? (Verify on Fever or BilletRéduc before import)
- Is this French-only? (Confirm — 4–6 comedians per session)

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S006 — Oscar Comedy Club

| Field | Value |
|---|---|
| Show name | Oscar Comedy Club |
| Venue | Café Oscar Comedy Club, 155 Rue Montmartre, 75002 Paris |
| Recurrence | Nightly recurring, through June 30, 2026 |
| Language | French |
| Confidence | 88 |
| Source URL | https://www.eventbrite.fr/e/oscar-comedy-club-tickets-1672589683769 |
| Secondary URL | https://feverup.com/m/122614/en |
| Platform | Eventbrite + Fever + BilletRéduc |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- Is entry still free with mandatory drink? (Verify before importing price info)
- Does Oscar have any English-language shows?

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S007 — The Joke Comedy Club

| Field | Value |
|---|---|
| Show name | The Joke Comedy Club |
| Venue | The Joke, 37 rue Quincampoix, 75004 Paris |
| Recurrence | Recurring nightly |
| Language | French |
| Confidence | 82 |
| Source URL | https://feverup.com/en/paris/venue/the-joke |
| Secondary URL | https://www.billetreduc.com/spectacle/the-joke-comedy-club-290613 |
| Platform | Fever + BilletRéduc + thejoke.fr |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- What are the typical comedy show start times? (Bar/restaurant venue — confirm)
- Is there an English night at The Joke?

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S008 — Le Plateau Comedy Club

| Field | Value |
|---|---|
| Show name | Le Plateau Comedy Club |
| Venue | Monsieur le Zinc — Bonne Nouvelle, 16 Rue de Mazagran, 75010 Paris |
| Recurrence | Recurring, 8:30pm–10pm (verify days) |
| Language | French |
| Confidence | 78 |
| Source URL | https://feverup.com/m/474472/en |
| Platform | Fever |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- Which days of the week does this run? (Verify on Fever)
- Is Fever the only source? (Low source diversity — verify if primary ticket source exists elsewhere)

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

### S009 — Le Fridge Comedy Night

| Field | Value |
|---|---|
| Show name | Le Fridge Comedy Night |
| Venue | Le Fridge Comedy, Paris 2nd arr. |
| Recurrence | Recurring evenings (comedy showcase) |
| Language | French |
| Confidence | 75 |
| Source URL | https://www.billetreduc.com/263384/evt.htm |
| Secondary URL | https://lefridgecomedy.com/ |
| Platform | BilletRéduc + lefridgecomedy.com |
| Duplicate check | No match in current 14 active listings |

**Review questions**:
- What is the full venue address? (BilletRéduc says 2nd arr. — confirm exact address)
- Is the show still running? (Check lefridgecomedy.com)
- Is this linked to Kev Adams / the larger Fridge Comedy franchise?

**Robert decision**: `[ ] approve_for_manual_import   [ ] reject   [ ] needs_more_research   [ ] future_watch`  
**Notes**: _____

---

## Summary Decision Table

| Seed | Show name | Your decision | Notes |
|---|---|---|---|
| S001 | Coucou Comedy Tuesday | | |
| S002 | Coucou Comedy Friday | | |
| S003 | Sebastian Marx NY Comedy Night | | |
| S004 | Paname Comedy Club | | |
| S005 | Golden Comedy Club | | |
| S006 | Oscar Comedy Club | | |
| S007 | The Joke Comedy Club | | |
| S008 | Le Plateau Comedy Club | | |
| S009 | Le Fridge Comedy Night | | |

---

> **Reminder**: After you fill in this table, paste your decisions back and Claude will create the manual import phase for approved candidates and get ChatGPT verification.
