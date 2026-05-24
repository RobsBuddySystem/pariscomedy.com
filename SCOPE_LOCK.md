# SCOPE_LOCK.md — ParisComedy.com

**Locked decisions.** Each item below cannot change without an explicit Scope Change Proposal approved by Robert. If you think a change is necessary, stop work and write a proposal; do not edit the locked surface.

---

## Locked surfaces

1. **Pricing** — tier prices, names, durations (see `PROJECT_CANON.md` → Pricing & money).
2. **Paid tier names** — `comic_plus_lifetime`, `comic_plus_monthly`, `comic_plus_annual`, `booker_plus_intro`, `booker_plus_monthly`, `featured_show_7d`, `featured_show_30d`, `featured_show_90d`.
3. **Affiliate assumptions** — placeholder refs stay `enabled:false`; never invent a real-looking ID.
4. **Scraper source strategy** — multi-source, no source privileged. Adding a source is fine; removing a source needs a proposal.
5. **Show ranking rules** — see `PROJECT_CANON.md` → Editorial neutrality and Featured placement.
6. **Featured logic** — only the three documented reasons (day-of-week match, paid promo, editorial feature with reason).
7. **Definition of "current"** — show is current if its next `start_date` is today or future in Europe/Paris.
8. **Definition of "verified"** — `verified_at` is set ONLY when a human or the §0.A LLM verification pass confirmed the row against an upstream authority. Auto-discovered shows have `verification_status: "auto-discovered"`, not `verified`.
9. **Homepage launch banner** — current copy: "Paris Comedy is live — every English stand-up show in Paris, one place." Any change touches scope.
10. **Social links** — no Instagram/Twitter/Facebook handles owned by the site. Footer shows only `payments@pariscomedy.com`.
11. **Public contact emails** — `payments@pariscomedy.com` (general), `bio@pariscomedy.com` (comic bios). No personal emails.
12. **Payment provider** — SumUp. Not Stripe.
13. **Data retention** — events 18 months, page_views 18 months. Prune script is manual (not auto-cron).
14. **What counts as an English show** — `language: "en"` requires explicit English signal in title OR description, validated by the LLM classifier with `confidence ≥ 0.5`.
15. **Whether French/bilingual shows are included** — yes, with `language: fr` or `language: bi` tags. Default scraper focus is English; `--include-french` flag broadens to FR.
16. **Any rule that privileges Robert's shows** — there is none. Locked at zero privilege.
17. **Manual SHOWS_DATA edits** — locked. New rows enter SHOWS_DATA only via the four paths documented in PROJECT_CANON.md → "No manual SHOWS_DATA patching." Any patch that adds rows without a matching url_health entry, show_approvals entry, or recurrence_source_url fails the build.
18. **Canceled-show blocklist** — `data/canceled_shows.json` is canonical. Removing a slug from the blocklist (un-canceling) requires Robert's written approval and a Scope Change Proposal.

---

## How to propose a scope change

1. Open `docs/scope-changes/YYYY-MM-DD-<short-slug>.md`.
2. Sections required: Current rule, Proposed rule, Reason, Risk, Reversibility, Robert's approval (initial + date).
3. Do not edit any locked surface until the proposal is committed AND Robert confirms in writing.
4. After approval, update `PROJECT_CANON.md` and `SCOPE_LOCK.md` in the same commit as the implementation change.
