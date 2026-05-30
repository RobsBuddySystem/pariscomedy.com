# /book.html — CONTAMINATED LEGACY ROUTE

**Status: PERMANENTLY DECOMMISSIONED**

## Do not use, link, advertise, or treat as canonical.

`/book.html` is a legacy route that has been permanently decommissioned.
It now contains only a meta-refresh redirect to `/connect.html` and is marked `noindex, nofollow`.

### Why it is contaminated

The page previously contained unsafe copy including:
- "Message bookers directly with Comic Plus — €1 lifetime (first 100)"
- "Claim my €1 lifetime spot →"

These phrases violated honesty and payment-readiness requirements. The page has been
hard-replaced but its URL remains in ChatGPT's browsing tool session cache, making it
permanently untrustworthy as a canonical URL.

### The canonical route

`/connect.html` is the **only** canonical booking and contact page.

### Guards

`regression_guard.py::check_book_html_decommissioned` — fails if any HTML, script, or
sitemap file (other than `book.html` itself) references `book.html`.

### Operator note

If you encounter a future scenario where `/book.html` needs content:
1. Do not restore old content — create a new route instead
2. Do not remove the `noindex` meta tag
3. Do not add `/book.html` back to the sitemap
4. Do not update the canonical tag away from `/connect.html`
