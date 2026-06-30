# CHART Baselines Generator

This repository is a standalone generator for the CHART build baselines image.
It fetches the latest Google My Maps KML export, regenerates `chart_baselines.png`,
and commits the updated image back to this repo on a schedule.

## How it works

- `assets/scripts/builds_uv.py` downloads the My Maps KML file
- it parses the build locations
- it generates `assets/scripts/chart_baselines.png`
- the workflow commits `chart_baselines.png` and `builds.kml` if they change

## Set up

1. Create a new GitHub repository and push this folder into it.
2. Enable GitHub Actions for the repo.
3. Optionally set branch protection rules on `main` if you want to preserve safety.

## Workflow

The workflow at `.github/workflows/generate-chart-baselines.yml` runs daily and
can also be triggered manually.

## Updating the CHART site

Once this repo exists, update `wiki/builds.md` in the main site repo to point to
this generated image via the raw GitHub URL:

```html
<img src="https://raw.githubusercontent.com/<OWNER>/<REPO>/main/assets/scripts/chart_baselines.png" alt="CHART build baselines">
```

Replace `<OWNER>` and `<REPO>` with your GitHub account/org and the repo name.
