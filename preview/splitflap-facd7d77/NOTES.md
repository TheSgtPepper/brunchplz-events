# Split-flap shout-out board — open questions

Draft mockup only. Nothing is live, no payment is set up, and nothing has been spent. Values below come from Brunch Ops (Nov 25, 2026) and are **pending Alex's approval**. The mockup is labeled that way throughout.

## Pricing and time on the board

Draft launch tiers (shown in the guest mockup):

- **Standard, $10** — next open slot, **3 minutes** on the board.
- **Spotlight, $20** — guest names the moment (e.g. cake time) in a short note; host gives a **mic call-out**; **5 minutes** on the board.

A **$40 proposal slot** was floated as a later idea only. It is **not** in the mockup UI and should stay off launch. If Alex wants it later, it could be a host-only or limited slot with a planned moment and a longer hold.

Open questions for Alex / Brunch Ops:

- Approve or change the $10 / $20 prices and the 3 / 5 minute holds.
- Is 3 minutes enough for a Standard shout-out in a loud room?
- For Spotlight, does the 5 minutes start at the named moment, or at the next open slot if that moment is missed?
- What happens if two Spotlights ask for the same moment?

## Daily cap

Draft cap: **6 paid shout-outs per brunch**, with a live counter (“3 of 6 left”) and a **Sold out today** state that points people at the next brunch (mockup links to [brunchplz.com](https://www.brunchplz.com/) and uses Sat, Nov 28 as the example next date).

Open questions:

- Confirm the cap of 6.
- Do unused slots roll, or is it simply “once 6 have been sold, that’s it”?
- Should Spotlight count as one of the six, or use a separate smaller cap?
- With a 10 AM–2 PM brunch, 6 messages at 3–5 minutes is only 18–30 minutes of paid board time. Is the rest of the time an idle brand frame (e.g. `BRUNCH, PLEASE!`), house messages, or coming-later vote mode?

## Moderation

Draft flow:

1. A **profanity / content filter** runs first.
2. The **floor lead** approves, edits, or rejects from a **phone queue**, aiming for **2 minutes**.
3. Anything still waiting at **5 minutes** is **held**, never auto-approved.

Draft guest rules (on the mockup):

- No profanity or slurs
- No explicit content
- No mean roasts
- No last names
- No phone numbers or social handles
- No ads for other businesses
- No politics
- Cheeky fun is fine

Open questions:

- Who is the floor lead at a typical Saturday vs Sunday?
- Confirm the 2-minute target and 5-minute hold. After a hold, does the lead still have time to approve, or does a hold auto-refund?
- First names only: how do we handle “the Miller party” or a last-name birthday the guest really wants?
- Should the filter also catch phone numbers, @handles, and URLs automatically?
- Do we need a short “why it was rejected” note for the guest, or is “Not approved — refunded” enough?

## Refunds

Draft policy in the mockup:

- **Rejected** or **held-and-expired** messages get an **automatic full refund** to the original payment. Guest status: **Not approved — refunded**.
- Messages that have **already run** are **not refundable**.
- Ticket Tailor ticket sales stay on their own “all sales are final” policy; this refund rule would apply only to shout-out purchases.

Open questions:

- Confirm automatic refunds, including after a 5-minute hold.
- If a Spotlight moment is missed and we run it later, is that still honored or refundable?
- Who a guest writes if a refund doesn’t land?

## Guest status screens

The mockup has three post-pay states:

1. **Pending approval** — “You’re in the queue! #4 — we’ll flash it soon.”
2. **You’re up around 11:40** — once approved / scheduled.
3. **Not approved — refunded.**

Open questions:

- How do we notify the guest of the status change — this same page if they leave it open, a text, or a receipt email?
- Do we show a queue position, a clock time, or both?

## Payment processor

Do **not** set anything up yet. The mockup only shows generic, fake **Apple Pay**, **Google Pay**, and **card** buttons.

Options to discuss with Alex (no recommendation locked in):

- **Square** — already familiar in restaurants; hardware and staff may already know it at Bucci’s. Online checkout and Apple/Google Pay are available. Settlement sits next to food-and-drink payments, which may or may not be desirable.
- **Stripe** — common for a custom web checkout (Payment Links, Checkout, or Payment Element) with Apple Pay / Google Pay, easy automatic refunds, and a clean split from in-house dining payments.

Other context: tickets already go through **Ticket Tailor**. Using it for $10–$20 add-ons would be a third option, but it is a weaker fit for a 60-character form, a staff approval queue, and automatic refunds.

## Character set

The mockup allows: **A–Z, 0–9, space, and `! ? . , ' - & # @ :`**. Input is forced to uppercase. 60 characters total, including spaces, on a **4 × 15** grid. Words wrap by row and are not split mid-word when it can be avoided.

**The actual character set still needs confirming with the seller** before we lock the input filter. Split-flap modules vary: some omit `@`, `#`, `&`, or the apostrophe; some use a different punctuation set. Once we have the vendor’s list, the guest field, the staff edit field, and the API mapper should all use that same list, and unknown characters should be rejected (or mapped) before anything is sent to the sign.

## How the sign could be fed from the approval queue

Brief technical note, vendor-agnostic, since the open-source, app-controlled sign is not ordered yet.

1. The **approval queue is the source of truth**. A guest payment creates a row in `pending_filter`, then `pending_staff`. Unapproved text never goes to the sign.
2. After the automated filter, the floor lead’s Approve / Edit / Reject (or a 5-minute hold) moves the row to `scheduled`, `rejected` (refund), or `held`.
3. A small **on-site agent** (Raspberry Pi, the sign’s own controller host, or a tiny always-on box on the same network) either polls something like `GET /api/board/current` every few seconds or receives a push (MQTT or webhook).
4. The payload is a fixed **4 × 15** frame plus a hold time, e.g. `{ "id": "…", "lines": ["HAPPY BDAY    ", "JESS!         ", "…", "…"], "hold_seconds": 180 }`, already mapped to the vendor character set.
5. The agent translates that into whatever the open-source controller speaks (HTTP, MQTT, websocket, or serial — depends on the seller) and sends it. After `hold_seconds`, it asks for the next scheduled item or shows an **idle / brand frame**.
6. Spotlight items are scheduled for a target window; the staff phone gets a cue for the mic call-out. If the official companion app cannot be bypassed, we need the seller’s API or a local integration path before we promise automation.
7. If the link drops, the sign should keep the last safe frame or revert to the idle frame — it should not invent a message. Logs (what was shown, when, and who approved it) stay internal and must not be published on a public page.

Until the seller is chosen, this stays a plan, not a build.

## What’s in this folder

- `index.html` — guest QR order page, including sold-out and status screens (use the preview controls, or `?state=pending|upnext|rejected` and `?cap=soldout`).
- `staff.html` — floor-lead approval queue with Now showing, Up next, and pending cards. Sample data only (e.g. “HAPPY BDAY JESS!” from Table 12).
- `later.html` — light “Coming later” sketches for A/B/C/D song voting and a $5 song request.
- `styles.css`, `flap.js` — shared look and the 4 × 15 flap preview.
- `screenshots/` — 390px-wide PNGs of each screen.
- This file is for the team, not a public page.

No real customer names or payments are in the mockup.
