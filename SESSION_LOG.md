# SESSION_LOG.md — pariscomedy.com build sessions

## 2026-05-22 Confirmed.show parity build
- Offers system: POST/GET /api/booker/offers, GET /api/performer/offers, POST /api/performer/offers/{id}/respond
- Performed-in-Paris (3mo) filter wired in /api/booker/comics (cross-refs booker_lineup table)
- Comic tags: touring/one-man/active-paris/language via PUT /api/admin/comics/{slug}/tags + tags column migration
- Venue CRUD: GET/POST /api/booker/venues, PUT /api/booker/venues/{id} + booker-dashboard Venues tab
- Surveys: POST/GET /api/booker/surveys + POST /api/surveys/{id}/respond (public) + Surveys tab in dashboard
- Multi-image: comic_photos table + GET /api/comics/{slug}/photos + POST /api/admin/comics/{slug}/photos + startup migration from photo_url
- Performer portal: Offers section shows pending offers with Accept/Decline buttons
- Booker dashboard: "Send offer" button per comic card, Venues tab, Surveys tab
- Backend restarted and health confirmed at api.pariscomedy.com/health
- Pushed to GitHub: b4afcac
