# MIDI To Strudel GUI 🎹 ⚡

> 💡 **Attribution & Origin**: This project is built upon and evolved from the original open-source project [**MIDI-To-Strudel**](https://github.com/Emanuel-de-Jong/MIDI-To-Strudel) created by [Emanuel de Jong](https://github.com/Emanuel-de-Jong).  
> It extends the core conversion engine with a modern drag-and-drop GUI, intelligent drum mapping (Roland TR-909), acoustic instrument DSP sound profiles, dynamic volume/gain balancing, stereo panning, and native cross-platform execution scripts for macOS and Windows.

---

A modern, cross-platform Desktop GUI and CLI tool that converts MIDI files into clean, executable [Strudel](https://strudel.cc) live-coding pattern code.

Designed for live-coding performers, algorithmic music creators, remixers, and electronic music producers.

---

## ✨ Key Features

- 🖱️ **Modern Drag-and-Drop GUI**: Drag `.mid` files directly onto the window or browse files with one click.
- 📋 **One-Click Instant Copy**: Copy converted Strudel code directly to clipboard ready for live-coding in the browser/REPL.
- 🥁 **Intelligent Channel 10 Drum Mapping**: Automatically converts standard General MIDI drum tracks (Channel 10) into Strudel Roland TR-909 sample sound sources (`bd`, `sd`, `hh`, `oh`, `rim`, `cp`, `tom`, `cy`, etc.).
- 🎛️ **Smart Acoustic DSP Profiles**: Automatically chains professional DSP parameters (`legato`, `sustain`, `decay`, `release`, `lpf`, `room`) to acoustic and synth instruments, preventing abrupt note cutoffs.
- 🔊 **Auto Track Volume & Panning**: Preserves the mix balance by calculating RMS velocity and MIDI CC 7 Volume into `.gain(...)` and MIDI CC 10 into `.pan(...)`.
- 🎼 **Octave Shift Control**: Transpose melodic tracks on the fly (-2 to +2 octaves) to hit the sweet spot for Strudel soundfonts.
- 💻 **Cross-Platform Scripts**: Includes zero-configuration one-click install, run, and standalone binary packaging scripts for both **macOS** and **Windows**.

---

## 🚀 Quick Start (Powered by `uv`)

This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast, reproducible dependency management without manual virtualenv hassles.

### 🍎 On macOS / Linux:

```bash
# 1. One-click install (installs uv if needed and syncs dependencies)
chmod +x *.sh
./install.sh

# 2. One-click run
./run.sh

# 3. (Optional) Build standalone native macOS .app bundle
./build_macos.sh
```

### 🪟 On Windows:

1. **One-Click Install**: Double-click [`install.bat`](file:///d:/AI/cursor/VST3/Strudel-REPL/MIDI-To-Strudel/install.bat) (or run `uv sync`).
2. **One-Click Run**: Double-click [`run.bat`](file:///d:/AI/cursor/VST3/Strudel-REPL/MIDI-To-Strudel/run.bat) to launch the GUI.
3. **One-Click Package to EXE**: Double-click [`build_exe.bat`](file:///d:/AI/cursor/VST3/Strudel-REPL/MIDI-To-Strudel/build_exe.bat) to compile a standalone `dist\MIDI-to-Strudel.exe`.

---

## 🖥️ GUI Options Breakdown

| Setting | Description | Default |
| :--- | :--- | :--- |
| **Guess Instruments** | Matches MIDI track names / program changes to General MIDI Soundfont instruments (`gm_piano`, `gm_violin`, `gm_overdriven_guitar`, etc.). | `ON` |
| **Smart DSP Acoustics** | Adds release/decay/legato/room filters to matched soundfonts to avoid dry, chopped cuts. | `ON` |
| **Auto Track Volume** | Analyzes velocities and CC 7 to scale track volumes nicely with `.gain(...)`. | `ON` |
| **Auto Drum (Ch 10)** | Maps MIDI Channel 10 to Strudel Roland TR-909 drum samples (`sound("909")`). | `ON` |
| **Octave Shift** | Shifts note octaves (`-2`, `-1`, `0`, `+1`, `+2`) to prevent bass/piano from playing too low or too high. | `0` |
| **Resolution** | Notes per bar (quantization grid). Default is `64` for high timing fidelity. | `64` |
| **Bar Limit** | Restricts export to first N bars (`0` = convert full song). | `0` |
| **Tab Size** | Code indentation spaces. | `2` |

---

## ⌨️ CLI Usage

You can also use the converter via command line:

```bash
uv run python Midi-to-Strudel.py -m your_song.mid
```

### CLI Arguments

```
usage: Midi-to-Strudel.py [-h] [-m MIDI] [-b BAR_LIMIT] [-f] [-t TAB_SIZE] [-n NOTES_PER_BAR]
                          [-g] [-s] [-d] [-o {-2,-1,0,1,2}] [-e] [-v]

options:
  -m, --midi              Path to the Midi file. (default: Uses first .mid in folder)
  -b, --bar-limit         The amount of bars to convert. 0 means no limit. (default: 0)
  -n, --notes-per-bar     The resolution. Usually in steps of 4 (4, 8, 16...). Higher gives better note placement. (default: 64)
  -t, --tab-size          How many spaces to use for indentation in the output. (default: 2)
  -g, --guess-instrument  Use the sounds closest to the instruments mentioned in the MIDI. (default: off)
  -f, --flat-sequences    No complex timing or chords. (default: off)
  -s, --small-print       Put all notes on a single line. (default: off)
  -d, --no-auto-drums     Do not auto-convert MIDI channel 10 to Strudel drum samples. (default: on)
  -o, --octave-shift      Shift melodic notes up or down by N octaves (-2 to +2). (default: 0)
  -e, --no-enhance        Do not apply smart DSP chains (legato, ADSR, lpf, room) to matched instruments. (default: on)
  -v, --no-auto-gain      Do not auto-balance track volumes based on MIDI velocity and CC 7. (default: on)
```

---

## 📝 Example Output

```javascript
setcpm(120/4)

$: note(`<
    [b3 b3 - c#4 c#4 - d4 d4] [- - - - b3 c#4 d4 e4] [f#4 f#4 - a3 a3 - b3 b3] [- - - - f#4 e4 d4 c#4]>`)
  .sound("saw")
  .gain(0.85)

$: s(`<
    [bd - - - bd - - -] [sd - - - sd - - -]
    [hh hh hh hh hh hh hh hh] [bd - - bd - - sd -]>`)
  .bank("RolandTR909")
  .gain(0.92)

$: note(`<
    [g1 g1 - a1 a1 - b1 b1] - [d2 d2 - f#1 f#1 - g1 g1] [- - - - f#1 e1 d1 c#1]>`)
  .sound("gm_lead_8_bass_lead")
  .legato(1.1)
  .decay(0.8)
  .sustain(0.7)
  .gain(0.78)
```

---

## 👥 Credits & Acknowledgments

- **Original Project**: [MIDI-To-Strudel](https://github.com/Emanuel-de-Jong/MIDI-To-Strudel) by [Emanuel de Jong](https://github.com/Emanuel-de-Jong) — the core MIDI parsing and Strudel pattern conversion engine.
- **Web Version Contributors**: [badele](https://github.com/badele) and [rayanfer32](https://github.com/rayanfer32).
- **GUI & Enhancements**: [martjay](https://github.com/martjay) — Modern Tkinter/DnD GUI, Roland TR-909 drum sound mapping, smart acoustic DSP chains, auto track volume/gain balance, stereo panning, and cross-platform packaging.
