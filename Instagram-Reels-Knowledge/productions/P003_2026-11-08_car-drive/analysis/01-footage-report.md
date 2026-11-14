# P003 Car Drive: footage report
Labels: [measured] tool number · [seen] looked at frames · [opinion]

## Inventory (all 5 files, `clip/car drive/`, never modified; copies in `source/`)
| File | Dur | Spec [measured] | Angle [seen] | Audio [measured] | Verdict |
|---|---|---|---|---|---|
| IMG_7415 | 2.1 s | 2160×3840 vertical, HEVC 10-bit HLG, 59.9 fps | Passenger-side, driver profile + dashboard | −14.4 LUFS engine/wind | **Weak**: ceiling dominates, highlights blown. Dropped |
| IMG_7425 | 14.7 s | same | Rear-right over-shoulder, sunroof + mirror + road through windscreen | −14.8 LUFS | **Good** 0–1.5 s, 6.2–7.5 s (roof-light sweep), 7.6–10 s (sunroof opens to sky). Arm raised to mirror 3.5–6 s: skipped |
| IMG_7427 | 5.0 s | same | Clean side profile, both hands visible, sunroof sky | −13.6 LUFS | **Good**, steady. Black neck-cushion on headrest (not an animal) |
| IMG_7441 | 12.7 s | same | Front-right, wide: wheel, cluster, sunroof with golden clouds, treetops sweeping overhead (3.5–9 s) | −12.9 LUFS | **Best clip**: hook, hero and calm shots |
| IMG_7444 | 7.5 s | same | Exterior: oncoming white Hyundai, road, motorbikes, stray dog | −28 LUFS wind | **Good 0–2.2 s only**. After ~3.5 s the other car's number plate is legible and from ~6 s its driver's face. Not used |

No duplicate overlap between files (all different moments). Total raw ≈ 42 s.

## Findings
- All clips are the same drive in warm low sun; no cutaway to the car's exterior (the exterior shot is another vehicle).
- Audio [measured + spectrogram, no speech or music detected]: engine rumble + wind only. Speech recognition could not be completed (large model killed for memory), so "no speech" rests on spectrograms + VAD-less listening of levels. **[opinion]** it is ambience; clean file keeps it.
- HDR HLG → tone-mapped with `hable` (tested vs `mobius` on stills: hable kept sky/highlight detail, mobius washed the bright interiors).
- 60 fps sources → clean 50 % slow-mo at 30 fps output, no interpolation needed.
- Privacy: other car's plate TN50… and driver face (7444 late), roadside pedestrians (small, unidentifiable at used range). Avoided by cutting early; verified on the final frame.
- Safety: the driver has both hands on the wheel in all used shots; no speed claims or stunts. Camera is held by someone else.

## Concept chosen: Cinematic "Golden Hour Drive"
Hook = sunroof canopy rushing overhead; establish with the road; build with rear angle; drop = golden-sky slow-mo hero; angle changes to the end; final slow-mo hold on the last hit. Honest alternative (rejected): "POV comedy" has no comedic beat in the footage.
