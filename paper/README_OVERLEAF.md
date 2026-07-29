# Getting `main.tex` into Overleaf

`main.tex` needs `vgtc.cls`, the official IEEE VGTC conference class. A copy is in this
folder, downloaded from <https://github.com/ieeevgtc/vgtc_conference_latex>. It only loads
the standard `article` class, so no other support files are needed.

## Setup

1. In Overleaf, create a **Blank Project**.
2. Upload **both** `main.tex` and `vgtc.cls` into it. They must sit in the same folder, at
   the top level of the project, not inside a subfolder.
3. Set `main.tex` as the compile target. Use the *Menu* panel on the left, then
   *Main document*, and pick `main.tex`.
4. Compile. It should build with no bibliography pass, because the references are written
   inline with `thebibliography` rather than pulled from a `.bib` file.

If you see `File 'vgtc.cls' not found`, the class file is either missing from the project or
sitting in a subfolder. Overleaf only finds it if it is beside `main.tex`.

## Adding the figures

The four figures are currently grey placeholder boxes so the document compiles before the
screenshots exist. For each one:

1. Create a `figs/` folder in the Overleaf project and upload the screenshot.
2. In `main.tex`, uncomment the `\includegraphics` line directly above the placeholder.
3. Delete the `\fbox{\parbox...}` line underneath it.

Expected filenames, matching the commented-out lines already in the file:

| File | Shot |
|---|---|
| `figs/fig1-tilt` | 65 degree tilt, both layers separated in Z (this is the wide teaser at the top) |
| `figs/fig2-detection` | Omicron detection phase, red dots before any cracks |
| `figs/fig3-ridge-uppermidwest` | Ridgeline, Upper Midwest hovered, showing the two week gap |
| `figs/fig4-ridge-appalachian` | Ridgeline, Appalachian hovered, curves sitting on top of each other |

Capture all four from `http://localhost:8080/` after running `python -m http.server 8080`
in the project root.

## Class options

`\documentclass{vgtc}` gives the plain conference style, which is right for a non-blind
workshop submission. If SciFi-VIS turns out to want blind review, switch to
`\documentclass[review]{vgtc}` and set `\onlineid` to the id they assign you. The alternate
line is already in the file, commented out.

## Word count

Body sections come to roughly 840 words. Counting the abstract and all figure captions as
well brings it to roughly 1050, and about 25 of those are placeholder text that disappears
once the real images go in. The workshop cap is 1000. If they mean body text only there is
plenty of room, and if they count everything it is worth cutting one more paragraph.
