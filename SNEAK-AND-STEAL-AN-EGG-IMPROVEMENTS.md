# Sneak and Steal an Egg — Improvement Spec

**Target game:** `Sneak and Steal an Egg` (Roblox)
**Date:** 2026-11-22
**Audience:** implementing dev / coding agent
**Status:** recommendations, not yet implemented

---

## 0. How to use this document

Work the phases in order: **P0 → P1 → P2 → P3 → P4.** Each phase has
acceptance criteria. Do not start a later phase until the earlier one ships and
its metrics are instrumented, because every later phase depends on P0 being
real. P0 is not a feature request — it is a correction to the core economic loop.
Shipping P2 (monetization) before P0 will produce a store nobody buys from.

Every number in here is a **starting hypothesis to tune**, not a constant handed
down from data. Instrument first (section 7), then tune.

---

## 1. Verified current state

Taken from the live Roblox store listing (official description):

> Sneak past the sleeping guards, grab a giant egg and RUN home before they wake
> up. Hatch it in your pen and your pets earn money while you play. Train your
> speed on the treadmill to open the desert, the snow, the volcano, the ocean and
> the crystal cave. Nobody ever dies here: if a guard catches you, the egg goes
> back on its nest and you pop home.

Decomposed:

| Element | Current design |
|---|---|
| Core verb | Steal egg from **NPC** guard |
| Threat model | PvE only — no player can affect another player |
| Failure cost | **Zero.** Egg resets to nest, player teleports home |
| Income | Idle — hatched pets earn while playing |
| Progression gate | Speed stat, trained on a treadmill |
| Content gate | Biomes: desert → snow → volcano → ocean → crystal cave |

The game is not indexed by search engines or third-party trackers, consistent
with a new release at negligible traffic.

---

## 2. Diagnosis

The genre this game enters does not monetize on *stealing*. It monetizes on
**fear of being stolen from.**

In the category leaders, your income exists only while you still hold your
assets. If a rival takes them, the income stops. That single rule produces four
things at once: moment-to-moment tension, shareable clips, sunk-cost retention,
and urgent spending. The leaders' best-selling passes are mostly *protection
from loss* or *acceleration under threat* — extra base slots, auto-collect,
raid-cooldown reduction, VIP access.

This game deletes both halves of that engine:

1. **No PvP.** Guards are NPCs. Nothing a player owns is ever at risk.
2. **"Nobody ever dies here."** Being caught costs nothing at all.

The result is a **cozy PvE idle game wearing the skin of a PvP steal game.**
That produces three compounding failures:

- **Retention** — no stakes means no reason to return tomorrow.
- **Monetization** — with nothing to lose, most of the proven pass catalogue has
  no reason to exist, and nothing creates urgency to spend.
- **Discovery** — the title and icon promise the steal genre (high click-through),
  then deliver calm. Promise/delivery mismatch is a top cause of instant exits.

The third is the most dangerous right now. Roblox reworked Recommended For You
in June 2026: it moved to a **28-day retention window**, **dropped** qualified
play-through rate as a signal, and **added first-play bounce rate**. New games
are tested daily and only scale impressions if performance improves. A game that
wins the click and loses the session is exactly what the current system
suppresses.

---

## 3. Definition of done (benchmarks)

Platform benchmarks to measure against:

| Metric | Median game | Top 1% | **Our target** |
|---|---|---|---|
| D1 retention | 10.3% | 22.2% | **20%+** |
| D7 retention | 1.6% | 9.1% | **6%+** |
| Session length | 9.8 min | 21.1 min | **15+ min** |
| Paying share | ~3.3–3.8% | — | **4%+** |
| ARPPU | $0.70 | $4.80 (top 5%) | **$2+** |

Economics to keep in mind while pricing: Roblox takes a **30%** marketplace fee
on passes and developer products, and DevEx pays **$0.0035 per Robux**. A
mid-tier simulator runs roughly **$0.003–0.006 ARPDAU**; a well-monetized game
reaches **$0.015–0.025**. Revenue is therefore gated by retention, not by price
points. Fix the loop before touching the store.

---

## 4. P0 — Restore loss (the whole game)

### 4.1 PvP raiding

Players must be able to steal **from each other**, not only from NPCs.

- A player may enter another player's pen and take **one hatched pet per raid**.
- The stolen pet transfers to the raider's pen and **its income transfers with it.**
- Per-target raid cooldown: **90s** (prevents one player being farmed).
- Global raid cooldown per raider: **45s**.
- The pen owner gets an **immediate on-screen alert** plus a **20s defend window**
  in which they can tag the raider to cancel the theft.
- Raids are **only possible while the owner's pen has at least 2 pets**, so a
  player can never be reduced to zero income.

### 4.2 Offline protection

- Offline players can lose at most **20% of their pen** per 24h, hard-capped.
- Never allow an offline player to be fully cleared. Returning to an empty pen is
  a churn event, not a retention event.

### 4.3 New-player immunity

This is what protects D1 while stakes exist.

- Immunity for the first **15 minutes of playtime** OR until the player has
  **3 pets hatched**, whichever comes later.
- Immunity is **visible** to other players (a shield marker on the pen) so the
  rule is legible and doesn't feel arbitrary.

### 4.4 Replace "nobody ever dies"

Getting caught must cost something recoverable but real. Remove the current
zero-penalty reset.

- The egg **drops at the point of capture** (not back on its nest) and any player
  may grab it — including the thief, after a delay.
- Caught player is **stunned 8s** at the drop point.
- That guard enters an **alert state for 30s** (wider vision cone, faster turn
  rate), so repeated attempts on the same target get harder.
- No death, no lost inventory, no teleport-home. The cost is **time and the
  contested egg**, which is enough to create tension without being punishing to
  a young audience.

### 4.5 Make income visible and visibly at risk

- Persistent HUD counter: **current $/sec**, updating live.
- When a pet is stolen, show the counter **drop** with a distinct sound and
  animation. The player must *feel* the loss, not read about it in a log.
- Each pen shows a floating **total $/sec value** to passers-by. This is the
  mechanic that turns pens into targets and makes the world feel alive.

### 4.6 Acceptance criteria for P0

- [ ] A player can steal a pet from another player's pen and keep its income
- [ ] Pen owner receives an alert and can contest within 20s
- [ ] A player can never drop below 2 pets by being raided
- [ ] Offline loss is capped at 20% / 24h
- [ ] New players are immune for 15 min / 3 pets and the shield is visible
- [ ] Being caught drops the egg, stuns 8s, raises guard alert 30s
- [ ] HUD shows live $/sec and animates losses
- [ ] D1 retention has **not fallen** versus the pre-P0 baseline (this is the
      guardrail — if it falls, immunity window is too short, not stakes too high)

---

## 5. P1 — Fix the first 90 seconds

First-play bounce rate is now a ranking signal, so the opening is a discovery
feature, not just UX polish.

Targets:

| Time | Player has |
|---|---|
| 0–10s | Control, and a stealable egg already visible |
| ~30s | Stolen their first egg |
| ~60s | Hatched it and seen a pet appear |
| ~90s | Watched their $/sec counter tick up for the first time |

Rules:

- **No cutscene. No forced tutorial. No text wall.** Teach with world design and
  a single guiding arrow, not dialogue.
- Spawn the player **within sight of an easy guard**, not in a hub they must
  navigate out of.
- The first steal must be **winnable by accident.** Make guard one trivially slow.
- **Critically: move the first biome unlock to under 10 minutes.** Right now the
  treadmill speed grind sits between the player and any environmental variety.
  A player who sees only the starting zone in their first session has no reason
  to believe the game has depth. Front-load the first biome, then let the curve
  steepen.
- A/B test the opening. Roblox's own guidance recommends testing individual
  tutorial steps (e.g. short dialogue vs. guided arrow) rather than shipping one
  guess.

### Acceptance criteria

- [ ] Median time-to-first-steal under 45s
- [ ] Median time-to-first-income under 100s
- [ ] Share of sessions ending under 60s reduced versus baseline
- [ ] First biome reachable in under 10 min of median play

---

## 6. P2 — Monetization ladder

Only build this after P0. Protection items are worthless in a game with no threat.

### Game passes

| Price (R$) | Pass | Notes |
|---|---|---|
| 49 | Starter Speed | +25% move speed |
| 99 | +2 Pen Slots | more pets = more income |
| 149 | Auto-Collect | idle income while offline, 2h cap |
| 299 | Pen Lock | raid shield, 30 min/day, **counterable** |
| 499 | VIP | 2× income, exclusive egg line, raid cooldown −50% |
| 999 | Founder Bundle | the above bundled at a discount |

### Developer products (consumables — repeat revenue)

| Price (R$) | Item |
|---|---|
| 25 | Instant hatch |
| 49 | 2× cash, 15 min |
| 75 | Distraction kit (one guaranteed guard bypass) |
| 150 | Pen shield, 1h |

### Rewarded ads

Add rewarded video for small boosts (a hatch skip, a short cash multiplier).
Reported to add **15–25% incremental revenue** without cannibalising pass sales.

### Guardrails — read before implementing

- **Never sell guaranteed, uncounterable theft.** Every purchased advantage must
  have a free counterplay. Pay-to-win is the single loudest criticism aimed at
  the category leader, and with a young player base it is both a reputational and
  a moderation risk.
- Do not gate the **core loop** behind payment. Sell speed, capacity, convenience
  and protection — never the ability to play.
- No purchase may let a player zero out another player's income.

### Acceptance criteria

- [ ] 4+ price points live across passes and products
- [ ] Paying share ≥ 3.3%
- [ ] Every paid advantage has a documented free counter
- [ ] Rewarded ads live and measured separately from pass revenue

---

## 7. Analytics to instrument (do this first)

Nothing above can be tuned without these. Log, with timestamps relative to
session start:

- `session_start`, `session_end`, `session_length`
- `first_steal_attempt`, `first_steal_success`, `first_hatch`, `first_income`
- `bounce_under_60s` (boolean)
- `biome_unlocked` (which, and at what elapsed time)
- `raid_attempted`, `raid_succeeded`, `raid_defended`, `raid_target_was_offline`
- `pet_stolen_from_me`, `income_delta`
- `pass_viewed`, `pass_purchased`, `product_purchased`, `ad_watched`
- `treadmill_time_total` (to detect whether the speed grind is a wall)
- D1 / D7 / D28 retention cohorts

Watch especially: **`treadmill_time_total` vs. D1.** If the players who churn are
the ones who spent the most time on the treadmill, the progression gate is the
churn cause and P1's biome change is the highest-value fix in this document.

---

## 8. P3 — Live ops cadence

The direct competitor in this genre ships an update **every Saturday** and that
cadence is credited with part of its concurrency. Roblox's own documentation
advises keeping each content update to **under three weeks of effort** so the
schedule stays sustainable.

- Pick one weekday and ship weekly, even when the update is small.
- Alternate: new egg/pet line → new biome or event → balance + quality pass.
- Run time-limited events with exclusive pets. Limited availability is what makes
  a weekly cadence worth returning for.
- Add a non-intrusive like prompt **after a win moment** (a successful raid, a
  rare hatch), never on join.

---

## 9. P4 — Differentiate: make "Sneak" real

A straight clone of the category leader loses to an incumbent with roughly
**10 billion visits** and an all-time peak near **14 million concurrent players**.
The clone field is already crowded with several near-identical titles.

The opening is in the game's own name. The leaders are **run-and-grab**. This game
has *sleeping guards* — which implies a stealth system nobody in this category has
actually built:

- **Noise**: sprinting wakes guards, walking doesn't. Surfaces differ (gravel vs.
  grass).
- **Vision cones**: visible to the player, so stealth is a readable skill rather
  than guesswork.
- **Hiding**: bushes, crates, behind nests.
- **Alert states**: calm → suspicious → awake, with clear visual tells.
- **Distraction tools**: throwables that pull a guard off its patrol.
- **Co-op heists**: one player distracts, another grabs. This is the strongest
  single idea in this document for virality — it creates a two-player story worth
  clipping, and it is genuinely absent from competitors.

Lean into stealth as **the mechanic**, not a word in the title. It is the one
defensible angle, and it also justifies the gentler tone the game already has:
the fantasy is being *clever*, not being *cruel*.

### Note on the name

`Sneak and Steal an Egg` collides with several established titles in search
results, so the game ranks as a weak substring match against its own competitors.
Consider whether a distinct hook word — built around the stealth identity — is
worth the rename before the game accumulates any ranking equity. Renaming later
is more expensive.

---

## 10. Non-goals / guardrails

- Do **not** remove stakes again to protect D1. Use the immunity window instead.
- Do **not** let offline players be cleared out.
- Do **not** sell uncounterable advantages.
- Do **not** add a cutscene, forced tutorial, or join-time like prompt.
- Keep the tone non-violent. "Nobody dies" was the right *instinct* — the fix is
  to add **stakes**, not **cruelty**. Loss of progress, not harm.
- Audience is substantially under 18. Every monetisation decision should survive
  a parent reading it.

---

## 11. Suggested order of work

1. **Instrument analytics** (section 7) — ship first, get a baseline
2. **P1 first-90-seconds + early biome unlock** — cheapest retention win, no new systems
3. **P0 PvP raiding + catch penalty** — the core correction
4. **P2 monetization ladder** — once there is something to protect
5. **P3 weekly cadence** — ongoing from here
6. **P4 stealth layer + co-op heists** — the differentiator and the long-term bet

---

## 12. Data caveats

- Benchmarks (retention, session length, ARPPU, conversion) are from the
  GameAnalytics 2026 Roblox Benchmark Report, covering 500+ games with 1M+ MAU.
- Discovery-algorithm changes are from Roblox's own developer forum and Discovery
  docs (June 2026 RFY change, October 2026 measurement change).
- **All competitor revenue and concurrency figures are third-party modeled
  estimates.** Roblox does not publish per-game revenue, and trackers disagree by
  up to 10×. Treat them as directional only.
- No live stats for this game were available when this document was written
  (`apis.roblox.com` was blocked), so section 1 is based on the public store
  listing. Pull real D1/D7, session length, play-through rate and pass conversion
  from Creator Dashboard before deciding priorities — they may reorder this list.
