#!/usr/bin/env bash
# make_sfx_kit.sh — synthesise an ORIGINAL, licence-free SFX starter kit with ffmpeg.
# Output: assets/sfx/*.wav (48 kHz stereo). Re-run any time; files are overwritten.
# These are basic synthetic sounds (no samples), so there are no licensing concerns.
set -euo pipefail
OUT="${1:-$(dirname "$0")/../assets/sfx}"
mkdir -p "$OUT"
FF=(ffmpeg -hide_banner -loglevel error -y)
FIN="aformat=sample_rates=48000:channel_layouts=stereo,alimiter=limit=0.89"

# Whooshes: band-limited noise with a swelling envelope
"${FF[@]}" -f lavfi -i "anoisesrc=d=0.35:c=pink:r=48000:a=0.9" -af "highpass=f=300,lowpass=f=4500,volume='sin(PI*t/0.35)^2':eval=frame,afade=t=out:st=0.28:d=0.07,$FIN" "$OUT/whoosh_short.wav"
"${FF[@]}" -f lavfi -i "anoisesrc=d=0.7:c=pink:r=48000:a=0.9" -af "highpass=f=200,lowpass=f=3500,volume='sin(PI*t/0.7)^3':eval=frame,$FIN" "$OUT/whoosh_long.wav"
"${FF[@]}" -f lavfi -i "anoisesrc=d=0.5:c=white:r=48000:a=0.6" -af "highpass=f=1500,lowpass=f=9000,volume='sin(PI*t/0.5)^2':eval=frame,$FIN" "$OUT/whoosh_airy.wav"

# Impacts: decaying low sine sweep + transient click
"${FF[@]}" -f lavfi -i "aevalsrc='0.9*sin(2*PI*(90*t-60*t*t))*exp(-5*t)+0.5*(random(0)-0.5)*exp(-60*t)':s=48000:d=0.9" -af "lowpass=f=6000,$FIN" "$OUT/impact_hit.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.95*sin(2*PI*(70*t-25*t*t))*exp(-2.2*t)':s=48000:d=1.6" -af "$FIN" "$OUT/sub_drop.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.8*(random(0)-0.5)*exp(-35*t)+0.6*sin(2*PI*160*t)*exp(-14*t)':s=48000:d=0.4" -af "lowpass=f=5000,$FIN" "$OUT/punch.wav"

# UI: pop, click, ding
"${FF[@]}" -f lavfi -i "aevalsrc='0.8*sin(2*PI*(1400*t-4000*t*t))*exp(-45*t)':s=48000:d=0.12" -af "$FIN" "$OUT/pop.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.7*(random(0)-0.5)*exp(-300*t)':s=48000:d=0.04" -af "highpass=f=2000,$FIN" "$OUT/click.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.5*sin(2*PI*1760*t)*exp(-4*t)+0.25*sin(2*PI*3520*t)*exp(-6*t)':s=48000:d=1.0" -af "$FIN" "$OUT/ding.wav"

# Riser: rising tone + swelling noise (2 s), ends at full level
"${FF[@]}" -f lavfi -i "aevalsrc='(t/2)^2*(0.5*sin(2*PI*(200*t+180*t*t))+0.35*(random(0)-0.5))':s=48000:d=2" -af "highpass=f=150,$FIN" "$OUT/riser_2s.wav"

# Comedy: "scratch-like" stop (fast pitch wobble + noise), tape-stop-style falling tone
"${FF[@]}" -f lavfi -i "aevalsrc='0.7*sin(2*PI*(600*t+400*sin(2*PI*9*t)))*exp(-4*t)+0.3*(random(0)-0.5)*exp(-8*t)':s=48000:d=0.45" -af "highpass=f=300,lowpass=f=5000,$FIN" "$OUT/scratch_stop.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.7*sin(2*PI*(440*t-380*t*t))*(1-t/0.6)':s=48000:d=0.6" -af "$FIN" "$OUT/tape_stop.wav"

# Camera shutter-ish snap (for freeze frames)
"${FF[@]}" -f lavfi -i "aevalsrc='0.8*(random(0)-0.5)*(exp(-120*t)+0.6*exp(-120*abs(t-0.06)))':s=48000:d=0.15" -af "highpass=f=1200,$FIN" "$OUT/shutter.wav"

# Peak-normalise every file to -3 dBFS so the kit has consistent levels
for f in "$OUT"/*.wav; do
  peak=$(ffmpeg -hide_banner -nostats -i "$f" -af volumedetect -f null - 2>&1 | sed -n 's/.*max_volume: \(-\?[0-9.]*\) dB.*/\1/p')
  gain=$(python3 -c "print(round(-3.0 - float('$peak'), 2))")
  "${FF[@]}" -i "$f" -af "volume=${gain}dB" "$f.tmp.wav" && mv "$f.tmp.wav" "$f"
done

echo "SFX kit written to $OUT:"; ls -1 "$OUT"
