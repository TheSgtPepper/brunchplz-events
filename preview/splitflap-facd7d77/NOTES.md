# Split-flap shout-out board — open questions

Draft mockup only. Nothing is live, no payment is set up, and nothing has been spent. Values below come from Brunch Ops (Nov 25, 2026) and are **pending Alex's approval** unless marked decided. The mockup is labeled that way throughout.

**Alex's decisions (Nov 25, 2026, America/New_York, relayed by Big Dawg):**

- Payment processor: **Square** (online checkout or payment links, Apple Pay and Google Pay, refunds through Square). Not Stripe. (9:04 PM)
- Moderation (9:13 PM, replaces the 9:10 PM call): **no filter and no staff approval.** Paid shout-outs **go straight into the rotation**. No profanity filter for now: the crowd is all 21+ women, so swearing is fine. Floor staff can still **pull** a message from the live rotation, and a pulled message is **refunded**.
- Cap: start at **6 shout-outs per brunch**; **raise the price before adding slots**.
- Character set: **TBD**. Alex is asking the seller for the flap character list.

## Pricing and time on the board

Draft launch tiers (shown in the guest mockup):

- **Standard, $10** — next open slot, **3 minutes** on the board.
- **Spotlight, $20** — guest names the moment (e.g. cake time) in a short note; host gives a **mic call-out**; **5 minutes** on the board.

A **$40 proposal slot** was floated as a later idea only. It is **not** in the mockup UI and should stay off launch. If Alex wants it later, it could be a host-only or limited slot with a planned moment and a longer hold.

Open questions for Alex / Brunch Ops:

- Approve or change the $10 / $20 prices (still unconfirmed) and the 3 / 5 minute holds.
- Is 3 minutes enough for a Standard shout-out in a loud room?
- For Spotlight, does the 5 minutes start at the named moment, or at the next open slot if that moment is missed?
- What happens if two Spotlights ask for the same moment?

## Daily cap

**Decided:** cap of **6 paid shout-outs per brunch** to start; when demand outgrows it, raise the price before adding slots. Live counter (“3 of 6 left”) sits next to the brunch date (mockup uses a fake **Sat, Nov 28 brunch**). The **Sold out today** state points people at the next brunch (mockup: Sun, Nov 29, linking to [brunchplz.com](https://www.brunchplz.com/)). House messages do **not** count toward the 6.

Open questions:

- Do unused slots roll, or is it simply “once 6 have been sold, that’s it”?
- Should Spotlight count as one of the six, or use a separate smaller cap?
- With a 10 AM–2 PM brunch, 6 messages at 3–5 minutes is only 18–30 minutes of paid board time. Is the rest of the time an idle brand frame (e.g. `BRUNCH, PLEASE!`), house messages, or coming-later vote mode?

## Moderation

**Decided (Nov 25, 9:13 PM ET, replaces the 9:10 PM filter plan):**

1. After Square payment, a paid shout-out goes **straight into the live rotation**. There is **no filter** (no profanity filter for now; the crowd is all 21+ women, so swearing is fine) and **no staff approval**, review target, or hold.
2. Floor staff can **pull** a message from the rotation (Now showing or Up next). A pulled message is **refunded** (decided).
3. Messages that have **already run** are not refundable.
4. **Content rule (approved by Alex, Nov 25):** shout-outs use **first names only**: no last names, phone numbers or social handles. This is the only content rule; there is still no filter otherwise.

A short hint sits directly under the guest message field: “First names only — no last names, phone numbers or handles.”

Draft guest rules (on the mockup):

> Messages go up automatically. Keep it fun and kind. No last names, phone numbers or handles. Staff can pull a message, and pulled messages are refunded. Once it's run, it isn't refundable.

There is **no automatic profanity filter at launch**. Adding a filter later is an optional idea if the board ever needs a harder gate than staff Pull.

Open questions:

- Who may pull a message — any floor host, or a named person?
- Is a pull refunded the moment staff pull it, or only if it hasn't finished running?

## Refunds

Policy:

- **Pulled** messages are **refunded** to the original payment (decided Nov 25, 9:13 PM).
- Messages that have **already run** (and weren't pulled) are **not refundable**.
- There is no filter, so there are no filter-block refunds.
- Ticket Tailor ticket sales stay on their own “all sales are final” policy; this refund rule would apply only to shout-out purchases.

Open questions:

- If a Spotlight moment is missed and we run it later, is that still honored or refundable?
- Who a guest writes if a refund doesn’t land?

## Guest status screens

After paying, the guest sees **You're in the rotation! Up around 11:40** (`?state=upnext`). There is no pending-approval screen and no filter-blocked screen. Older `?state=pending|rejected|blocked` URLs fall through to the rotation confirmation.

Open questions:

- How do we notify the guest of a later change (a pull, or a new time) — this same page if they leave it open, a text, or a receipt email?
- Do we show a rotation position, a clock time, or both?

## Payment processor

**Decided: Square.** The mockup shows fake Apple Pay, Google Pay, and card buttons with a “Secure checkout by Square” line. Use Square online checkout or Square payment links, with Apple Pay and Google Pay, and issue refunds through Square. **Not Stripe.** Nothing is set up yet; this stays a draft until Alex says go. No Square keys or live integration are in the mockup.

How a Square payment would feed the board (plan only):

1. A successful Square `payment.updated` / checkout completed webhook creates the shout-out row.
2. The row goes straight into the **live rotation** (`scheduled`). No filter. The on-site sign agent (see below) picks up the next frame.
3. If floor staff **pull** a message, a Square refund API call sends the full amount back to the original payment.
4. The receipt goes to the guest’s phone or email (stored only for the receipt and refunds — never shown on the board or on the staff rotation view).
5. If the webhook never arrives, do not queue a message and do not light the board.

Tickets still go through **Ticket Tailor**, which stays separate from shout-out purchases.

## Character set

The mockup allows: **A–Z, 0–9, space, and `! ? . , ' - & # @ : $`**. Input is forced to uppercase. Unsupported characters are **blocked as the guest types** (they never land in the field); a short note explains that the character is not on the board. 60 characters total, including spaces, on a **4 × 15** grid. Words wrap by row and are not split mid-word when it can be avoided. `$` is included as a draft character so house lines like `MIMOSA TOWER $35 10 LEFT` can be typed; drop it if the seller’s flaps do not have a dollar sign.

**Character set: TBD.** Alex is asking the seller for the flap character list. The list above is a placeholder, and it **still needs confirming with the seller** before we lock the allowed characters. Split-flap modules vary: some omit `@`, `#`, `&`, `$`, or the apostrophe; some use a different punctuation set. Once we have the vendor’s list, the guest field, the house-message field, and the API mapper should all use that same list, and unknown characters should be rejected (or mapped) before anything is sent to the sign.

## How the sign could be fed from the rotation

Brief technical note, vendor-agnostic, since the open-source, app-controlled sign is not ordered yet.

1. The **live rotation is the source of truth**. A guest payment creates a row that goes straight to `scheduled` (no filter). Only characters the sign supports are sent.
2. A small **on-site agent** (Raspberry Pi, the sign’s own controller host, or a tiny always-on box on the same network) either polls something like `GET /api/board/current` every few seconds or receives a push (MQTT or webhook).
3. The payload is a fixed **4 × 15** frame plus a hold time, e.g. `{ "id": "…", "lines": ["HAPPY BDAY    ", "JESS!         ", "…", "…"], "hold_seconds": 180 }`, already mapped to the vendor character set.
4. The agent translates that into whatever the open-source controller speaks (HTTP, MQTT, websocket, or serial — depends on the seller) and sends it. After `hold_seconds`, it asks for the next scheduled item or shows an **idle / brand frame**.
5. Spotlight items are scheduled for a target window; the staff phone can still get a cue for the mic call-out. If the official companion app cannot be bypassed, we need the seller’s API or a local integration path before we promise automation.
6. A **pull** removes the item from `scheduled` (and triggers a refund) before the agent sends that frame.
7. If the link drops, the sign should keep the last safe frame or revert to the idle frame — it should not invent a message. Logs (what was shown and when) stay internal and must not be published on a public page.

Until the seller is chosen, this stays a plan, not a build.

## Guest details

The guest form collects:

- **First name** — shown on the staff rotation as the “From” name only. No last names.
- **Table #** — optional.
- **Phone or email for your receipt** — with the note: “Only used for your receipt. Never shown on the board.”

The staff rotation view shows first name and table only. Contact info is not displayed there, even in this mockup’s sample data.

Open questions:

- Is first name required to submit, or optional?
- Is a receipt contact required for Square checkout, or can a guest skip it?

## House messages

Staff can compose and queue **house messages** (example: `MIMOSA TOWER $35 10 LEFT`), tagged **HOUSE**. They do not count toward the 6 paid shout-outs. Use them for specials, wayfinding, or idle-board lines when no paid message is running.

Open questions:

- Who may send a house message — any host, or a named person?
- How long does a house message stay up, and can a paid Spotlight bump it?

## What’s in this folder

- `index.html` — guest QR order page, including sold-out and in-the-rotation screens (use the preview controls, or `?state=upnext` and `?cap=soldout`).
- `staff.html` — live rotation view with Now showing (countdown), Up next, a Pull button on each item (pulled = refunded), a cap counter, and a House message composer. Sample data only (e.g. “HAPPY BDAY JESS!” from Table 12). No receipt contact is shown.
- `later.html` — light “Coming later” sketches for A/B/C/D song voting and a $5 song request.
- `styles.css`, `flap.js` — shared look and the 4 × 15 flap preview.
- `screenshots/` — 390px-wide PNGs of each screen.
- This file is for the team, not a public page.

No real customer names or payments are in the mockup.
