# CONTENT.FRESHNESS.3 — Operator Decision Packet (Freshness Repoints)

**For: Robert (operator)**  
**Status: DECISION PACKET ONLY — NO REPOINTS EXECUTED**  
**Date: 2026-05-30**

> ⚠️ Decisions here do NOT auto-apply. A separate authorized phase is required for any DB change.

---

## Allowed Decisions per Listing

- **approve_repoint** — You've confirmed the replacement URL is current. Claude will execute the repoint in a separate phase.
- **keep_needs_human_review** — Leave as-is until you have more info.
- **hide_until_current_source_found** — Remove from promoted panels until a valid source is confirmed.
- **needs_more_research** — Requires additional investigation before deciding.

---

### Listing 1 — Millennial Meltdown

| Field | Value |
|---|---|
| Slug | `millennial-meltdown` |
| Current source URL | https://www.eventbrite.fr/e/billets-english-comedy-show-millennial-meltdown-paris-stand-up-night-1984665294321 |
| Stale signal | "ventes terminées" — this is a past-event page |
| What we know | Show is confirmed still running: Kuhl Productions, every Wednesday at 8pm, Le Bikini Bottom (Bastille, Paris) |
| Problem | The Eventbrite ID above is for a specific past date. The organizer (Kuhl Comedy) likely publishes new event IDs per period. |
| Replacement candidate | Search Eventbrite for the current recurring Millennial Meltdown event under Kuhl Comedy organizer |
| Confidence | 70 |
| Risk note | Do not repoint until a current Kuhl Productions Eventbrite organizer URL is confirmed. Using a stale event ID leaves the booking link broken. |
| Proof needed before action | Current Eventbrite event URL with at least one future date visible |

**Robert decision**: `[ ] approve_repoint   [ ] keep_needs_human_review   [ ] hide_until_current_source_found   [ ] needs_more_research`  
**Replacement URL (if approving)**: _____  
**Notes**: _____

---

### Listing 2 — Oh My God She's Parisian!

| Field | Value |
|---|---|
| Slug | `theatre-bo-julie` |
| Current source URL | https://www.eventbrite.fr/e/the-comedy-in-english-by-a-french-girl-that-will-make-you-love-paris-tickets-1764207685679 |
| Stale signal | "event ended" — this is a past-event page |
| What we know | Show is confirmed still running in 2026. Active on Viator and GetYourGuide. |
| Replacement candidate 1 | [julie-collas.com](https://www.julie-collas.com/) — official performer website (confidence 80) |
| Replacement candidate 2 | [Viator 2026](https://www.viator.com/tours/Paris/Oh-my-god-shes-Parisian-The-brand-new-comedy-show-in-English-language-in-Paris/d479-67244P1) — active 2026 ticket booking (confidence 75) |
| Confidence | 80 |
| Risk note | None — show is clearly active. Choose primary source (performer site vs ticket platform). |
| ⚠️ Name correction needed? | DB entry says "Julie Coulon" — official site and all sources say **Julie Collas**. Do not change name until you verify: it could be a stage name vs legal name distinction. |
| Proof needed before action | Confirm venue address + verify performer name (Collas vs Coulon) |

**Robert decision**: `[ ] approve_repoint   [ ] keep_needs_human_review   [ ] hide_until_current_source_found   [ ] needs_more_research`  
**Preferred replacement URL**: `[ ] julie-collas.com   [ ] Viator 2026   [ ] Other: _____`  
**Name correction**: `[ ] correct to Collas   [ ] leave as Coulon   [ ] verify first`  
**Notes**: _____

---

### Listing 3 — Wednesday Night Comedy

| Field | Value |
|---|---|
| Slug | `wednesday-night-comedy` |
| Current source URL | https://www.eventbrite.fr/e/english-standup-wednesday-night-comedy-tickets-1750646975229 |
| Stale signal | "event ended" — this is a past-event page |
| What we know | No replacement URL found. Organizer not identified in search. |
| Replacement candidate | None found |
| Confidence | 30 |
| Risk note | Show may have ended, been renamed, or moved to a different organizer. Showing a broken source link undermines site credibility. |
| Recommendation | **hide_until_current_source_found** — remove from promoted panels until a valid current source is confirmed |
| Proof needed before action | A current Eventbrite or primary ticket URL with at least one future date visible |

**Robert decision**: `[ ] approve_repoint   [ ] keep_needs_human_review   [ ] hide_until_current_source_found   [ ] needs_more_research`  
**Replacement URL (if found)**: _____  
**Notes**: _____

---

## Summary Decision Table

| Slug | Recommendation | Your decision | Replacement URL | Notes |
|---|---|---|---|---|
| millennial-meltdown | keep_needs_human_review | | | |
| theatre-bo-julie | approve_repoint (julie-collas.com or Viator) | | | |
| wednesday-night-comedy | hide_until_current_source_found | | | |

---

> **After you fill in this table**: paste decisions back and Claude will create a separate authorized phase to apply any approved repoints. No DB changes happen until then.
