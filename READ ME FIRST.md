# Sunday & Company — GitHub + Netlify

## Production source

The **repository root is the production site**. Netlify is connected to this GitHub repository and publishes from `.` as configured in `netlify.toml`.

Do **not** drag a separate `deploy` folder into Netlify. There is no separate production folder in the current workflow.

## Normal update workflow

1. Make and verify source changes in this repository.
2. Keep shared production assets and each page's asset-version query aligned.
3. Use `[skip netlify]` on preparatory commits when a production deploy is not wanted yet.
4. When the source is fully verified and a deploy is intended, publish the final approved GitHub state through the connected Netlify workflow.
5. Check the live site after deployment on desktop and mobile before considering the change complete.

## Netlify configuration

`netlify.toml` lives at the repository root and currently configures:

- `publish = "."`
- Security headers, including HSTS, clickjacking protection, MIME-sniffing protection and a strict referrer policy
- HTTPS and `www` redirects to `https://sundayandcompany.co`
- Asset caching at `public, max-age=3600, must-revalidate`
- HTML revalidation at `public, max-age=0, must-revalidate`

The production site uses stable asset filenames such as `/assets/site.css`, `/assets/rendered-corrections.css` and `/assets/site.js`, with version query strings in the HTML for cache-busting. Do not leave pages pointing at an older version after a shared asset update.

## Site files

The public routes live in the repository root and route folders. `404.html`, `robots.txt`, `sitemap.xml`, `support.js`, `web3forms.js` and the `/assets` directory are also production files.

`robots.txt` points search engines to `https://sundayandcompany.co/sitemap.xml`.

## Forms

Forms post through Web3Forms using the existing site configuration. After a production form change, submit a real test and confirm delivery to `hello@sundayandcompany.co`.

## If something looks wrong after publishing

First verify that the live page is requesting the same current asset version as the source in GitHub. Then check the latest Netlify deploy against the expected GitHub commit. If a deployment itself is bad, Netlify keeps previous deploys available for rollback.

Avoid making broad global CSS or JavaScript changes to fix a single page unless the shared behavior is actually the source of the issue. Prefer the smallest source-aligned correction and verify it before deploying again.
