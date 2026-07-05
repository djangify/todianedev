# Blog post draft — ready to publish

Paste the fields below into a new post in your blog admin. The **Body** section is HTML — paste it into the TinyMCE **source/code view** (`<>`), then switch back to visual.

---

**Title:** Marketplaces vs Your Own Store: Why "Free" Is the Most Expensive Word in Digital Business

**Slug:** `marketplaces-vs-your-own-store`
*(the pillar page already links to this slug — publishing with it makes the link go live)*

**Suggested category:** your closest "independent business / ownership" category (pick in admin)

**Meta title:** Marketplaces vs Your Own Store — Why "Free" Costs the Most | Diane Corriette

**Meta description:** Etsy, Gumroad, Shopify, or your own store? A real, numbers-first look at what each platform actually costs you in fees, data, and ownership — and why "free" is rarely free.

**Meta keywords:** marketplace fees, own your store, Etsy vs own website, Gumroad fees, Shopify alternative, digital products, platform independence, Djangify

**Introduction (teaser field):**
When you sell digital products, you have to decide where your business actually lives. Most platforms fall into one of three traps — and "free" is often the most expensive word in the room. Here's how they really stack up, in real numbers.

---

## Body (HTML — paste into the editor's source/code view)

```html
<p>When you sell digital products, you have to choose where your business lives. And most people choose based on one word: <em>free</em>. But free is often the most expensive word in digital business — it just charges you later, in fees, in data you don't own, and in a business you can't take with you.</p>

<p>I use marketplaces. I use social platforms. I'm not against any of them. But none of them are my business — they're <strong>roads</strong> that lead people back to the one place I own. Your 1,000 true fans shouldn't live on rented land. They belong at your own storefront and on your email list. A marketplace is a starting block, not a foundation.</p>

<p>Here's how the options actually stack up.</p>

<h2>The three traps</h2>

<h3>Trap 1 — The Revenue Tax</h3>
<p>The more you sell, the more they take. Your success is their payday. Growth costs you more every month instead of less.</p>

<h3>Trap 2 — The Walled Garden</h3>
<p>Build inside their walls and you can never truly leave. Your custom setup, your customer relationships, your content — all live on their terms, and you can't take the house with you.</p>

<h3>Trap 3 — The Marketplace Meatgrinder</h3>
<p>Your unique expertise becomes a commodity. Your direct competitors sit right beneath your listing, and you get buried in the results.</p>

<h2>Free platforms: what "free" really costs</h2>
<table>
  <thead>
    <tr><th>Platform</th><th>Monthly</th><th>Transaction fee</th><th>The reality for creators</th></tr>
  </thead>
  <tbody>
    <tr><td>Amazon KDP</td><td>£0</td><td>~50% (under £9.99)</td><td>They take half your revenue off the top, then deduct printing costs from your remaining half.</td></tr>
    <tr><td>Gumroad</td><td>£0</td><td>10% + Stripe fees</td><td>The success tax: grow to £2,000/mo and they take £200 every single month.</td></tr>
    <tr><td>Etsy</td><td>£0</td><td>6.5% + listing &amp; payment fees</td><td>Plasters your direct competitors under your listings and buries you in search.</td></tr>
    <tr><td>Payhip</td><td>£0</td><td>5% + Stripe fees</td><td>Better than most — but to drop the fee to 0% you pay £79/month.</td></tr>
    <tr><td>Systeme.io</td><td>£0</td><td>0% (up to 2k contacts)</td><td>A great free tool, but a walled garden. Your setup is stuck in their walls.</td></tr>
    <tr><td><strong>Your own store (Djangify)</strong></td><td>£12</td><td>0% (just standard Stripe)</td><td>A fixed, predictable cost. £100 or £10,000 in sales, your overhead is still £12 — and you own the data, the customer, and the profit.</td></tr>
  </tbody>
</table>

<h2>Paid managed platforms: renting someone else's software</h2>
<p>On managed SaaS platforms you're renting proprietary software. Leave Shopify or Wix and you can't take their code with you — you rebuild the whole house from scratch.</p>
<table>
  <thead>
    <tr><th>Platform</th><th>Monthly</th><th>Transaction fee</th><th>Data ownership</th><th>Software lock-in</th></tr>
  </thead>
  <tbody>
    <tr><td>Shopify</td><td>~£25–£105+</td><td>2%–0.5% + card fees</td><td>They hold your customer data. Flagged account = store gone overnight.</td><td>None — leave and you leave everything.</td></tr>
    <tr><td>Wix / Squarespace</td><td>~£16–£40+</td><td>0% on top tiers</td><td>Basic CSV export only; you depend on their servers and rules.</td><td>Locked into their templates and architecture.</td></tr>
    <tr><td>WordPress.com + WooCommerce</td><td>£36–£55</td><td>0% (standard card fees)</td><td>You own the records, but under their terms and hosting.</td><td>Partial — export is possible but a manual migration.</td></tr>
    <tr><td><strong>Your own store (Djangify)</strong></td><td>£12</td><td>0% (just standard Stripe)</td><td>100% yours — customer list, data, and profits.</td><td>None. Clean, private architecture; all your data goes with you.</td></tr>
  </tbody>
</table>

<h2>Self-hosted open source: full control, real maintenance</h2>
<p>Go fully self-hosted and your only ongoing software costs are infrastructure (a small VPS) and standard Stripe fees. The trade-off is maintenance — and how much depends heavily on what you run.</p>
<table>
  <thead>
    <tr><th>Software</th><th>Upfront</th><th>Ongoing</th><th>Hosting/mo</th><th>Maintenance</th></tr>
  </thead>
  <tbody>
    <tr><td>WordPress + WooCommerce</td><td>£0 (open source)</td><td>None</td><td>£5–£20</td><td>High — constant plugin, theme and security updates that frequently conflict and break layouts.</td></tr>
    <tr><td>Magento / Adobe Commerce</td><td>£0 (open source)</td><td>None</td><td>£50–£100+</td><td>Extreme — built for enterprise; needs a developer just to maintain basics.</td></tr>
    <tr><td><strong>Djangify (self-hosted)</strong></td><td>One-time purchase</td><td>£0</td><td>£5</td><td>Minimal — clean, lightweight Python/Django. No fragile plugin web to patch every week.</td></tr>
  </tbody>
</table>

<h2>Where Djangify lands — and why I built it</h2>
<p>I built Djangify because I was tired of watching creators do everything right and still hand most of their profit to platforms that don't know their name. It's a Django-based eCommerce platform for independent creators — available as managed hosting at £12/month, or a one-time self-hosted purchase. Either way, you own your store, your data, and your profits, with no platform taking a cut of every sale. I'm not talking at creators when I describe those traps — I've lived them. That's where it came from: not a business plan, a problem I refused to keep accepting.</p>

<h2>The real point isn't the platform. It's the ownership.</h2>
<p>Whether you pick a managed store for a hassle-free launch or a self-hosted setup for total control, the logic is the same: stop renting space on platforms that tax your growth or hide you in the noise. Use them as roads — then send everyone back to something you own. That's the whole game, and it's part of a bigger idea I build everything around: <a href="/owning-your-platform/">owning the platform you build your business on</a>.</p>

<p><a href="https://djangify.com">Take a look at Djangify →</a></p>
```

---

*Note: I kept this evergreen and ownership-focused, and left out the original page's "back a woman in tech" emotional close — that's a personal positioning choice, so add it back in your own words if you want it here.*
