# CHART Baselines Generator

This repository automatically regenerates the CHART build baselines image from the shared Google My Maps export.

Each day, the workflow downloads the latest KML export, parses the build locations, and updates:

- `assets/scripts/builds.kml`
- `assets/scripts/chart_baselines.png`

If the image changes, the workflow commits the updated file back to this repository.
