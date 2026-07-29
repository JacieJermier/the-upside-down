# Structure Before Style: Choosing a Science-Fiction Frame That Matches the Data

**Jacie Jermier** — University of Waterloo — jjermier@uwaterloo.ca

*Submission to SciFi-VIS 2026 (position paper). Body text ~980 words.*

---

## Abstract

Science-fiction framing in visualization is usually judged on whether the theme feels
relevant. We argue it should be judged on whether the fiction's *structure* matches the
data's structure. We present *The Upside Down*, a web-based narrative visualization of
COVID-19 wastewater surveillance built on a *Stranger Things* frame, and we report what
happened when we tested the metaphor against measured lead times. The frame survived,
but only after it forced us to delete our most dramatic wave and to display a region
where the early-warning story is simply false.

## 1. Position

Wastewater carries SARS-CoV-2 RNA days to weeks before infected people seek testing, so
sewage can warn of an outbreak before hospitals register it [3, 5, 6]. Public dashboards
communicate this through line charts and choropleths — analytically precise, and almost
impossible for a non-expert to feel.

*Stranger Things* offers a hidden dimension that occupies the same physical space as the
visible world, where threats become detectable before they surface. This is not a mood
that happens to suit an epidemic. It is an isomorphism. The relationship we needed to
show — a signal existing underground before it appears above — is the relationship the
fiction already encodes spatially. Byrne et al. [1] argue figurative frames extend
expressiveness beyond decoration; we push further and claim the frame is only load-bearing
when its structure and the data's structure are the same shape.

The practical consequence is a testable criterion. If the metaphor genuinely encodes the
relationship, then wherever the data violates the relationship, the metaphor must visibly
break. A frame that looks equally convincing whether or not the underlying pattern holds
is decoration wearing an argument's clothes.

## 2. System

Two transparent `deck.gl` map layers share a 3D scene composed with CSS `preserve-3d`. The
lower layer (the Upside Down) draws wastewater sampling sites as dots whose radius and
brightness encode viral RNA percentile and population served. The upper layer (the surface)
draws procedurally generated cracks whose severity combines state case intensity with
local wastewater signal strength, so the places that detected most are the places that
crack hardest. Flat, the layers coincide; tilted to 65°, they separate in Z, exposing the
void between worlds (Fig. 1).

A synchronized D3 ridgeline stacks regional rows, each pairing a filled wastewater curve
with a dashed clinical curve; horizontal displacement between peaks is the lead time
(Fig. 3). Playback follows a five-act structure — entry, detection, breach, zoom,
exploration — following Segel and Heer's martini-glass model [7], because the lead-lag
relationship is unreadable if a first-time viewer scrubs past the detection phase.

## 3. Testing the Frame

Our original submission annotated lead times as manual estimates. Replacing them with
cross-correlation of weekly wastewater percentile against weekly cases changed the paper.

Two findings mattered. First, **the Delta wave had to be deleted.** CDC NWSS percentile
reporting does not begin until 15 November 2021, so the entire Delta window contains no
viral intensity data; only a near-constant detection flag, and only in six states. Delta
had been our flagship, carrying most of our figures. The visualization had been rendering
it confidently the whole time. The metaphor did not break, because nothing forced it to —
which is exactly the failure mode we are warning about.

Second, **the lead time is real but uneven** (Table 1). Idaho led Omicron by three weeks
(r = 0.99) and Arizona led BA.5 by two (r = 0.85). West Virginia led neither: its
correlation peaks at lag 0 in both waves (r = 0.94, r = 0.92). The signals move together.
There is no underground.

| Region / State | Wave | Lead | r |
|---|---|---|---|
| Southwest | BA.5 | 2 weeks | 0.97 |
| Upper Midwest | Omicron | 2 weeks | 0.82 |
| Upper Midwest | BA.5 | 2 weeks | 0.81 |
| Idaho | Omicron | 3 weeks | 0.99 |
| Appalachian | Omicron | **none** | 0.95 |
| West Virginia | BA.5 | **none** | 0.92 |

We now display Appalachia and West Virginia rather than hiding them. In those rows the two
curves sit on top of each other and the layers have nothing to separate. The frame fails
visibly, in public, which is the strongest evidence we have that it was encoding something.

## 4. Discussion

For a workshop on science fiction and visualization, we offer three claims.

**Pick frames by structural correspondence, not thematic fit.** Many fictions are
epidemiologically evocative; almost none place a hidden layer beneath a visible one in
shared space. That specific property is what does the work.

**A speculative frame must be falsifiable.** Our metaphor's credibility rests on the
regions where it fails. Speculative interfaces that cannot fail against real data are
concept art — valuable, but a different contribution.

**Fiction inherits its source's blind spots.** The Upside Down implies the underground
always knows first. Surveillance infrastructure does not work that way: before late 2021
there was no underground to look at, because the sensors were not installed. A frame that
cannot express *absence of instrumentation* will quietly imply coverage that never existed.

## 5. Limitations

Lead times are computed from aggregated weekly series at state and regional scale; sewer
transit time and sampling cadence are not modeled [5]. Coverage spans Omicron and BA.5
only. The 3D effect needs WebGL and hardware-accelerated transforms, and the Mercator
projection inflates northern states. We report correlations, not causal lead estimates.

---

## Figures (4 max)

**Fig. 1** — Tilt at 65°, both layers separated in Z. Red underground below, blue surface
above, dust in the void.
**Fig. 2** — Omicron detection phase: wastewater dots on the red layer before any surface
cracks.
**Fig. 3** — Ridgeline, Upper Midwest highlighted: a visible two-week gap between the red
wastewater peak and the blue clinical curve.
**Fig. 4** — Ridgeline, Appalachian highlighted: curves coincident. The counterexample.

## References

[1] L. Byrne, D. Angus, J. Wiles. Figurative frames: a critical vocabulary for images in
information visualization. *Information Visualization*, 18(1):45–67, 2019.
[2] Centers for Disease Control and Prevention. NWSS Public SARS-CoV-2 Wastewater Metric
Data, 2026. Accessed 16 Feb 2026.
[3] P. M. D'Aoust et al. Catching a resurgence: SARS-CoV-2 viral RNA in wastewater 48 h
before clinical tests. *Sci. Total Environ.*, 770:145319, 2021.
[4] C. North. Toward measuring visualization insight. *IEEE CG&A*, 26(3):6–9, 2006.
[5] M. Kumar, A. K. Srivastava, N. Srivastava. Lead time of early warning by wastewater
surveillance for COVID-19. *Chem. Eng. J.*, 441:135936, 2022.
[6] J. Peccia et al. Measurement of SARS-CoV-2 RNA in wastewater tracks community
infection dynamics. *Nat. Biotechnol.*, 38(10):1164–1167, 2020.
[7] E. Segel, J. Heer. Narrative visualization: telling stories with data. *IEEE TVCG*,
16(6):1139–1148, 2010.
