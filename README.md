# brunchplz-events
Public, hourly-refreshed `events.json` of upcoming BRUNCH, PLEASE! dates for the brunchplz.com date picker.
Public event info only (date, time, name, price-from, availability, ticket link). No API key, orders, or customer data.

Setup (one time):
1. Settings > Secrets and variables > Actions > New repository secret: `TICKET_TAILOR_API_KEY`.
2. Settings > Pages > Source: Deploy from branch `main`, folder `/`.
3. Actions > "Refresh events.json" > Run workflow.
Feed URL: https://<owner>.github.io/brunchplz-events/events.json
