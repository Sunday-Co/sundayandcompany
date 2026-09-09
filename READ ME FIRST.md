# Sunday & Company — Netlify Deploy

## What to upload

Drag the **`deploy`** folder onto Netlify. That is the whole site and nothing else.
Do not upload `reference/` — it is documentation for you, not for the web.

Netlify: log in → **Sites** → drag the `deploy` folder onto the drop zone.
It publishes in about thirty seconds and gives you a temporary URL to check.

## Connect your domain

1. In Netlify: **Domain management → Add a domain →** `sundayandcompany.co`
2. Netlify shows you four nameservers. Copy them.
3. In GoDaddy: **My Products → Domains → sundayandcompany.co → Nameservers →
   Change → I'll use my own nameservers.** Paste all four, save.
4. Wait. Usually under an hour, occasionally up to 24. Netlify issues the HTTPS
   certificate automatically once DNS resolves — you do nothing for that.

Your old Wix site stays live until the nameservers switch, so there is no gap.

## What is already handled

`netlify.toml` travels inside `deploy/` and configures all of this on publish:

- Security headers — HSTS, clickjacking protection, no MIME sniffing and a strict referrer policy
- HTTPS forced, `www` redirected to the bare domain
- Clean URLs — `/about`, `/our-work/luckys-cafe-bakery`, no `.html` anywhere
- `404.html` served on unknown paths
- Long-lived caching on assets, none on HTML, so corrections publish instantly

`robots.txt` and `sitemap.xml` are in there too. Nothing to configure.

## Two things to do after it is live

**1. Submit the sitemap.** Google Search Console → add `sundayandcompany.co` →
verify (easiest via the DNS record Netlify can host) → **Sitemaps** → submit
`https://sundayandcompany.co/sitemap.xml`. This is what gets you indexed in days
rather than weeks.

**2. Take the old Wix site down.** It is still indexed calling Sunday "a
full-service marketing agency," which competes with the new site for your own
name. Either unpublish it or point it at the new domain.

## One Google Business Profile edit

Your profile is verified and correctly set as a service-area business with no
public address. The only gap: it lists no North Carolina areas, while the site
names North Carolina — and two of four case studies are NC work.

Add to the profile's service areas: **Raleigh NC, Durham NC, North Carolina.**
Site and profile should agree; a mismatch weakens both.

## Forms

All seven post to Web3Forms on your three existing keys. Nothing to set up.
Test one after launch and check `hello@sundayandcompany.co`.

One optional hardening step: in your Web3Forms dashboard, switch on captcha for
the **project inquiry** key only. Honeypots are already in every form and stop
most bots; captcha stops the determined ones. Leave the newsletter frictionless.

## If something looks wrong after publishing

Netlify keeps every previous deploy. **Deploys →** pick the last good one →
**Publish deploy.** Instant rollback, no rebuild.
