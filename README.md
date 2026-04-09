# The Upside Down — COVID-19 Wastewater Surveillance Visualization

An animated, web-based narrative visualization that uses a *Stranger Things*-inspired figurative frame to make the lead-lag relationship between wastewater viral signals and clinical COVID-19 cases intuitively accessible.

## Overview

This visualization renders two transparent deck.gl map layers — a red wastewater detection layer and a blue clinical surface layer — that separate and rejoin in 3D space to dramatize the moment underground signals breach into visible outbreaks. A synchronized ridgeline plot encodes regional lead times, and guided narrative annotations walk viewers through three major variant waves (Delta, Omicron, BA.5).

## Prerequisites

- Python 3.x (for the local server)
- A modern web browser with WebGL support (Chrome, Firefox, Edge)

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/jaciejermier/the-upside-down.git
cd the-upside-down
```

2. Start a local server:

```bash
python -m http.server 8080
```

3. Open your browser and navigate to:

- **Visualization:** `http://localhost:8080/project`
- **Pictorial:** `http://localhost:8080/project/pictorial.html`

4. Click **"Enter the Upside Down"** to begin the guided animation.

## Viewing the Pictorial

The pictorial is a VISAP-format visual essay documenting the design process and visual encoding decisions. To view it, navigate to `http://localhost:8080/project/pictorial.html` in Chrome. To export as PDF, press `Ctrl+P`, set margins to **None**, and select **Save as PDF**.

## Project Structure

```
project/
├── index.html              # Main visualization (single-page application)
├── pictorial.html          # VISAP pictorial (visual design essay)
├── data/
│   ├── us-states.geojson   # U.S. state boundaries
│   ├── sites.json          # Wastewater treatment plant locations
│   ├── site_weekly.json    # Weekly wastewater metrics per site
│   ├── state_cases_weekly.json  # Weekly clinical cases per state
│   ├── region_weekly.json  # Regional aggregations for ridgeline plot
│   └── region_order.json   # Region display ordering
└── audio/
    └── stranger-things-theme.mp3  # Did not end up including audio 
```

## Usage

**Guided playback:** Click "Enter the Upside Down" and the animation plays automatically through a five-act narrative structure with auto-pause on key story moments.

**Variant selection:** Use the Delta, Omicron, and BA.5 buttons at the top to switch between variant waves. Each variant resets the visualization with its own narrative text, zoom targets, and lead time annotations.

**Manual scrubbing:** Use the timeline slider at the bottom to scrub to any point in the variant's timeline. The visualization instantly updates to the correct state.

**Ridgeline plot:** Toggle with the 📊 button. Hover over a region to highlight its wastewater and clinical curves. The horizontal gap between peaks encodes the lead time.

**Speed control:** Click the speed button (1x / 1.5x / 3x) to adjust playback speed.

## Tech Stack

- **deck.gl v8.9** — WebGL-accelerated geospatial map rendering (two synchronized instances)
- **D3.js v7** — Ridgeline plot, geographic projections
- **Vanilla JavaScript** — No build step, no framework
- **CSS 3D Transforms** — `preserve-3d` scene tilting, `translateZ` layer separation

## Data Sources

- [CDC NWSS Public SARS-CoV-2 Wastewater Metric Data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Wastewater-Metric-Data/2ew6-ywp6)
- CDC COVID Data Tracker (weekly cases by state)

## Author

Jacie Jermier — University of Waterloo