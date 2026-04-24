# Fork Quiz — Deployment Notes

**Live:** https://loringtonian.github.io/fork-quiz/
**Deploy repo:** https://github.com/Loringtonian/fork-quiz (separate from Second_Brain)
**Pages source:** `main` branch, `/` path (push-to-main → GitHub Pages auto-builds)
**HTTPS:** enforced

## Source of truth

This folder (`Second_Brain/Projects/Fork_Quiz/`) is where Lorin develops. The public repo `Loringtonian/fork-quiz` is the deploy target — it is **not a git submodule or symlink**, just a separate repo that receives snapshots. Today's working tree has NOT been pushed to `fork-quiz` yet unless you see otherwise in its commit log.

## To ship changes

The repo has exactly the files in this folder — `index.html` at the root, `assets/` alongside. No build step.

```bash
# One-shot: clone the deploy repo elsewhere, copy, push.
cd /tmp && rm -rf fork-quiz-deploy
gh repo clone Loringtonian/fork-quiz fork-quiz-deploy
cp -R /Users/lts/Desktop/Second_Brain/Second_Brain/Projects/Fork_Quiz/index.html /tmp/fork-quiz-deploy/
cp -R /Users/lts/Desktop/Second_Brain/Second_Brain/Projects/Fork_Quiz/assets /tmp/fork-quiz-deploy/
cd /tmp/fork-quiz-deploy && git add -A && git commit -m "Sync from Second_Brain" && git push
```

GitHub Pages build typically completes in 30–90s. Check status:
```bash
gh api repos/Loringtonian/fork-quiz/pages/builds/latest --jq '{status, commit, url}'
```

## Important: OG/Twitter image URL

The `og:image` and `twitter:image` meta tags in `index.html` are **absolute URLs** pointing at `https://loringtonian.github.io/fork-quiz/assets/hero.png`. If the deploy URL ever changes (custom domain, repo rename), update those tags — X/Twitter's card crawler requires absolute URLs to reliably fetch the hero.

Validate the X card after a deploy: https://cards-dev.twitter.com/validator

## Asset generation

- `assets/hero.png` was generated via `nano-banana-pro` (Gemini 3 Pro). Prompt is preserved at `/tmp/gen_hero.py` on the dev machine — re-run if the image needs to be regenerated. File is 1376×768, 16:9.
- `assets/favicon.svg` is hand-written SVG — 5 diverging colored lines matching the fork palette.

## Future enhancements (not scoped)

- URL-encoded shareable results (e.g. `?r=base64scores` reproduces a specific outcome)
- Per-fork iconography on the results breakdown
- Analytics (currently none — the quiz runs entirely client-side)
