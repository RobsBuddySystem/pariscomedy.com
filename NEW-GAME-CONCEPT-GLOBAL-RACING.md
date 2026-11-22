# New Game Concept — Global Racing, Tied to Real-World Events

**Date:** 2026-11-22
**Status:** concept + market read, pre-production
**Audience:** implementing dev / coding agent, and whoever greenlights this

---

## 1. Read this first: the honest market read

You asked for a car racing game. Before the concept, the number that should shape
every decision:

| Genre | Best-in-class concurrency |
|---|---|
| "Steal a ___" / social-PvP | **~14.3M peak CCU**, ~10B+ visits |
| **Roblox racing** | **~17,000–28,000 CCU** |

The top racing games on Roblox — Driving Empire, Can You Pass A Driving Test? —
run in the **tens of thousands** of concurrent players. The steal genre runs in
the **millions**. That is a 500–1000× difference in ceiling.

**Racing is a structurally low-ceiling genre on Roblox.** Not a bad genre — a
small pond. If the goal of game two is revenue, going from a millions-scale genre
into a tens-of-thousands-scale genre is a step down, however well it is executed.

There is also a tell inside the data worth copying: **the top "racing" game isn't
a racing game.** Driving Empire is a *car collection and wealth* game — acquire,
own, show off, upgrade. Players stay for ownership and progression, not lap times.
Pure lap-time racers rank far below it (one tracked at ~1,700 CCU).

**Conclusion:** build a game *about cars*, not a game *about racing*. Lap-time
skill gates casual players and caps your audience. Ownership, progression and
social stakes do not.

---

## 2. What "current events" should and shouldn't mean

The instinct is right — a real-world hook gives you free cultural relevance and,
more importantly, **a free live-ops calendar**. But choose carefully.

**Use:** sport and motorsport culture. Globally shared, politically neutral,
recurring on a published schedule, and genuinely booming.

**Avoid:** politics, conflict, disasters, or anything tied to real tragedy. The
audience is largely under 18, these themes narrow appeal rather than widen it,
and they are a moderation risk. "Current events" that unite worldwide players are
*sporting and cultural* events, not news events.

### Why motorsport specifically

Formula 1 is in a genuine global boom, and the demographics match Roblox:

- **830M+ global fans**, roughly **+64% since 2018**
- **43% of the fanbase is under 35**
- **Women are 42% of the audience and about three-quarters of new fans**
- **Every 2026 race sold out** — 11 consecutive sell-outs, ~3.7M spectators across
  the first 11 events, attendance up ~6% year on year
- Genuinely global, not US-centric: the British GP drew a record **18M viewers in
  Brazil**; Italian TV audiences up 27%; social following up 19% YoY
- **2026 brought major new technical regulations** (a new hybrid power-unit era) —
  a real "new era" narrative to hang a game on, and fan ratings of the racing
  actually improved (66% rated it good/excellent, up from 60%)

Caveat: most of those figures are Formula 1's own reported numbers, and the
reports available are mid-season 2026.

---

## 3. Recommended concept: **Grand Prix Tycoon**

A team-ownership game with a real-world race calendar and rival sabotage.
Not a lap-time simulator.

### 3.1 Core loop

1. **Own a garage.** You run a team, not a car.
2. **Your cars earn prize money idle** while you play — the proven income engine.
3. **Race weekends are events**, not the whole game. Short, forgiving, skill-light
   races that a new player can finish.
4. **Rivals can sabotage your pit or poach your driver** — the loss mechanic that
   actually drives retention and spending.
5. **Upgrade** power units, aero and tyres across tiers that mirror the real
   hybrid-era regulations.
6. **Unlock regions** — circuits by continent, which doubles as the progression
   gate *and* the global identity hook.

This deliberately reuses the engine that works at millions-scale (ownership +
idle income + loss risk + progression) and dresses it in the fastest-growing
global sport. You are not betting on racing-game demand; you are betting on a
proven loop with a culturally hot skin.

### 3.2 The three global hooks

These are what make people **worldwide** want to play, which was the actual ask.

**1. Pick your nation.** Every player picks a country at onboarding. Liveries and
cosmetics carry the flag.

**2. National leaderboards.** Individual performance contributes to a **country
score** with a weekly reset. This is the single most important feature in this
document. It gives *every* country a reason to organise, recruit and share —
including small countries that can realistically win a weekly board. It converts
national pride into free user acquisition, which is exactly why World Cup–timed
games spike.

**3. Real calendar = automatic live ops.** Each real-world Grand Prix weekend
becomes an in-game event: that circuit's layout, a limited livery reward, a
weekend-only leaderboard. The published season calendar hands you a **globally
synchronised weekly update cadence for free** — which solves the cadence problem
that most games have to solve with raw labour, and makes the game feel connected
to the real world.

Between motorsport seasons, the 2027 global calendar gives further event pegs
(FIFA Women's World Cup in Brazil, Rugby World Cup in Australia, ICC Cricket
World Cup in South Africa) for themed liveries and national-pride pushes. Note
there are **no Olympic Games in 2027** — the next Summer Games are Los Angeles
2028.

### 3.3 Monetization

Same ladder logic as the egg game (see the other document), re-skinned:

| Price (R$) | Item |
|---|---|
| 49 | Starter tune (+handling) |
| 99 | +2 garage slots |
| 149 | Auto-collect prize money (offline, capped) |
| 299 | Pit security (sabotage shield, time-limited, counterable) |
| 499 | VIP team — 2× prize money, exclusive livery line |
| 999 | Founder bundle |

Plus consumables (instant repair, 2× prize weekend, scout report) and rewarded
ads. **National liveries and flag cosmetics should be the cosmetic spine** — they
monetise identity, which is the strongest driver in a nation-leaderboard game.

Same guardrails apply: no uncounterable paid advantage, never gate the core loop,
no purchase that can zero another player out.

---

## 4. Legal guardrails — do not skip this

This is the main risk of a real-world hook, and it is a real one.

- **Do not use real team names, driver names, team logos, or sponsor branding.**
  Ferrari, Mercedes, Red Bull, driver names and likenesses are all protected.
  Roblox acts on IP reports and you can lose the game.
- **Do not use official championship marks** — the "F1" and "Formula 1" word marks
  and logos are trademarked. Do not name the game after them.
- **Use fictional teams with evocative liveries** — a red Italian team, a silver
  German one. Players will read the reference. That is enough, and it is how
  every safe motorsport game handles this.
- **Circuit names can also be trademarked.** Prefer **city and country** framing
  ("Monaco street circuit", "Suzuka-style figure-eight") over official circuit
  branding, and build original layouts inspired by real ones rather than
  surveyed copies.
- Keep the real-world tie-in at the level of **calendar, cities and culture** —
  not **brands**. The calendar is not protectable; the logos are.

---

## 5. Risks and the honest ceiling

- **Genre ceiling is the big one.** Even executed well, racing-adjacent is a far
  smaller pond than the steal genre. If the objective is revenue, consider instead
  applying the car theme *inside* a proven high-concurrency genre rather than
  entering the racing category at all.
- **Vehicle physics are expensive.** Netcode for driving is materially harder than
  for the egg game's on-foot movement, and bad car physics are instantly obvious.
  This raises cost and risk at the same time as entering a smaller market.
- **Topical hooks decay.** A game pegged to a season needs the evergreen
  ownership loop to carry it between seasons. Build the tycoon layer first and the
  topical layer second, never the other way around.
- **IP risk** as above — survivable only with discipline from day one.

---

## 6. If you want the higher-expected-value version

A sharper option, stated plainly because the data points at it:

Keep **national leaderboards** and the **real-world event calendar** — those are
the genuinely good ideas here and they are what makes a game global — but attach
them to a **high-concurrency social-PvP loop** rather than to racing. Cars as the
collectible and status object, theft or sabotage as the stake, nations as the
team structure, the real sporting calendar as the live-ops engine.

That keeps everything in this document that is strong (global identity, free
cadence, cultural relevance, ownership loop) and drops the one thing that is
structurally weak (the racing genre's ~25K ceiling).

---

## 7. Suggested MVP scope

Ship small and prove the loop before building a season.

1. One region, three circuits, four cars
2. Garage ownership + idle prize income + visible income counter
3. Nation select + a single weekly national leaderboard
4. One sabotage/poach mechanic with a defend window and new-player immunity
5. Analytics from day one (same event list as the egg game spec)
6. **Then** add the calendar-driven weekend events

Validate against the same benchmarks: D1 20%+, D7 6%+, session 15+ min. If the
MVP cannot clear median D1 (10.3%) without the calendar gimmick, the loop is not
working and no amount of real-world theming will rescue it.

---

## 8. Data caveats

- Racing-genre concurrency figures are third-party trackers with unclear snapshot
  times and they disagree with each other; treat them as approximate. The
  *order of magnitude* gap versus the steal genre is the reliable part, not the
  specific numbers.
- Formula 1 audience figures are largely self-reported by Formula 1 and drawn
  from mid-2026 reports.
- 2027 event dates come from secondary calendars, several marked TBA. Verify
  against official organiser sites before committing to an event schedule.
