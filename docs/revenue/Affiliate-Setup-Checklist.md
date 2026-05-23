# Affiliate Setup Checklist — ParisComedy (2026-05-23)

## Status: Infrastructure ready. NO real affiliate IDs in production.

All ticket links flow through `/r.html` which reads `data/affiliates.json` and injects the matching ref parameter. To activate revenue: sign up for each program, get the real ref ID, and replace the placeholder in `data/affiliates.json`.

`/r.html` redirects safely without affiliate IDs — if `ref` is empty or matches the placeholder `pariscomedy`, the redirect still works to the destination URL. Click tracking fires regardless (event_type=`affiliate_click`).

---

## Where to insert real IDs

File: `data/affiliates.json` → `networks[<domain>].ref`

Current placeholders all set to `"pariscomedy"` (harmless string, doesn't earn commission until replaced).

---

## Program checklist

### 1. Eventbrite Affiliate Program
- **Sign-up**: https://www.eventbrite.com/l/affiliateprogram/
- **Commission**: 1.5% of net ticket revenue
- **Cookie window**: 30 days
- **Param**: `aff`
- **Update**: `networks["eventbrite.com"].ref` AND `networks["eventbrite.fr"].ref`
- **Priority**: 🔴 HIGHEST — ~80% of Paris English comedy shows ticket through Eventbrite
- **Status**: ⏳ NOT REGISTERED

### 2. GetYourGuide Partner Program
- **Sign-up**: https://partner.getyourguide.com/
- **Commission**: 8% on bookings
- **Cookie window**: 30 days
- **Param**: `partner_id`
- **Update**: add `networks["getyourguide.com"]`
- **Priority**: 🟡 MEDIUM — tourist-heavy traffic on venue pages
- **Status**: ⏳ NOT REGISTERED

### 3. Fever
- **Sign-up**: https://feverup.com/affiliates (apply via Impact or Awin)
- **Commission**: 6–10% via Impact network
- **Param**: `aid` or via Impact tracking link
- **Update**: add `networks["feverup.com"]`
- **Priority**: 🟡 MEDIUM — growing comedy events in Paris
- **Status**: ⏳ NOT REGISTERED

### 4. Ticketmaster France
- **Sign-up**: Awin → search "Ticketmaster FR"
- **Commission**: ~5%
- **Cookie window**: 1 day (short — fast-checkout flow)
- **Param**: `camefrom`
- **Update**: `networks["ticketmaster.fr"].ref`
- **Priority**: 🟢 LOW — rarely used for stand-up
- **Status**: ⏳ NOT REGISTERED

### 5. BilletReduc
- **Sign-up**: https://www.billetreduc.com/partenaires/
- **Commission**: contact for rate (typically 3–6%)
- **Param**: `partenaire`
- **Update**: add `networks["billetreduc.com"]`
- **Priority**: 🟡 MEDIUM — Paris-native, French comedy events
- **Status**: ⏳ NOT REGISTERED

### 6. Fnac / France Billet
- **Sign-up**: via Awin or direct Fnac Spectacles
- **Commission**: ~4%
- **Param**: `Origin`
- **Update**: add `networks["fnacspectacles.com"]`
- **Priority**: 🟢 LOW — mostly French-language shows
- **Status**: ⏳ NOT REGISTERED

### 7. See Tickets
- **Sign-up**: Awin → "See Tickets"
- **Commission**: ~5%
- **Param**: `aff`
- **Update**: add `networks["seetickets.com"]`
- **Priority**: 🟢 LOW — niche
- **Status**: ⏳ NOT REGISTERED

### 8. Dice.fm
- **Sign-up**: https://dice.fm/partners
- **Commission**: invite-only, custom
- **Param**: TBD (depends on contract)
- **Priority**: 🟡 MEDIUM — gaining traction with younger comedy crowd
- **Status**: ⏳ NOT REGISTERED

---

## Adding a new network

Edit `data/affiliates.json` and add:

```json
"<domain.tld>": {
  "param": "<aff_param>",
  "ref": "<real_id_from_program>",
  "note": "Program name + sign-up date"
}
```

Then `/r.html` will automatically inject `?<aff_param>=<real_id>` on any outbound link matching that domain.

---

## Fastest revenue activation path

1. **Eventbrite first** (covers ~80% of clicks). 24-hour approval typical.
2. **GetYourGuide second** (venue/tourist traffic).
3. **BilletReduc third** (French-language comedy reach).

Everything else can wait until volume justifies the paperwork.
