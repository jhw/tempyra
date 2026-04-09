# Tempera Canvas File Format

Reverse-engineered documentation for the Beetlecrab Tempera `.canvas` file format.

## Overview

The Beetlecrab Tempera is a hardware granular sampling instrument. A **canvas** is the Tempera's complete patch format — it bundles audio samples with all synth parameters into a single self-contained file.

A `.canvas` file is a **ZIP archive** (uncompressed, using `store` method) containing:

- **64 FLAC audio files** — 8 tracks × 8 resolution levels
- **parameters.txt** — all synth parameters as key:value pairs

Canvas versions observed in the wild: 2, 3, 4, 6, 7, 11, 14, 15. The parameter set grows with each firmware update; newer versions add parameters while retaining backward compatibility.

## Audio Files

### Naming

Files are named `{track}_{level}.flac` where:

- `track` is 0–7 (the 8 sample slots)
- `level` is 0–7 (resolution levels, 0 = full length)

### Format

- **Codec:** FLAC (Free Lossless Audio Codec)
- **Sample rate:** 48,000 Hz
- **Bit depth:** 16-bit
- **Channels:** 2 (stereo)
- **Encoder:** reference libFLAC 1.4.3

### Resolution Levels

Each track is stored at 8 progressively shorter lengths. Level 0 contains the full audio; each subsequent level is approximately 10/13 (≈77%) the length of the previous, truncated from the start of the sample.

| Level | Samples  | Duration |
|-------|----------|----------|
| 0     | 524,288  | ~10.92s  |
| 1     | 403,298  | ~8.40s   |
| 2     | 310,229  | ~6.46s   |
| 3     | 238,637  | ~4.97s   |
| 4     | 183,567  | ~3.82s   |
| 5     | 141,205  | ~2.94s   |
| 6     | 108,619  | ~2.26s   |
| 7     | 83,553   | ~1.74s   |

The base sample count (524,288) is 2^19. The exact counts at each level appear to be firmware-specific rounding of the ×10/13 ratio and have been empirically determined.

All levels contain the same audio content — level N is identical to the first N samples of level 0. These are likely pre-computed for performance on the embedded hardware, avoiding the need to seek into large FLAC streams during real-time playback at different zoom levels on the touch surface.

### ZIP Ordering

Files are ordered in the ZIP from track 7 down to track 0, and within each track from level 7 down to level 0. The final entry is `parameters.txt`.

## Parameters

`parameters.txt` is a newline-delimited list of `key:value` pairs. Values may be integers, floats, or strings. String values may include a leading space after the colon (e.g. `track5Name: I Stand Before You`).

Non-track parameters are sorted alphabetically. Track parameters follow at the end; their ordering varies by firmware version (grouped by track index in older versions, grouped by property name in newer versions).

### Canvas Metadata

| Key | Type | Description |
|-----|------|-------------|
| `canvasVersion` | int | Format version (observed: 2, 3, 4, 6, 7, 11, 14, 15) |
| `masterVolume` | float | Master output volume |
| `activeEmittor` | int | Currently selected emitter |
| `defaultPlayMode` | int | Default play mode |
| `emittorPlayMode` | int | Emitter play mode |
| `effectsChannelSend` | int | Effects channel routing |
| `keyboardEmitterTarget` | int | Bitmask of emitters targeted by keyboard |
| `keyboardHold` | int | Keyboard hold on/off |
| `tempoClockBPMCanvas` | int | Canvas tempo in BPM (0 = not set; v11+) |
| `overlayKeyboardHidden` | int | Overlay keyboard visibility (v14+) |

### Tracks (0–7)

Each track represents one loaded audio sample.

| Key pattern | Type | Description |
|-------------|------|-------------|
| `track{N}Name` | string | Original source filename |
| `track{N}Amp` | float | Track amplitude |
| `track{N}Tuning` | float | Base tuning in Hz (default 440) |
| `track{N}TuningMode` | int | Tuning mode |
| `track{N}From` | int | Playback start point (in samples) |
| `track{N}To` | int | Playback end point (in samples) |
| `track{N}GridMode` | float | Grid quantisation mode (v2) |
| `track{N}RecordEnabled` | int | Recording enabled flag (v2) |

#### BPM and Tuning from Filename

The Tempera parses BPM and base frequency from the source filename when samples are first loaded. For example:

- `DrumGroove130BPM.wav` → sets track tempo to 130 BPM
- `Bells_533Hz.wav` → sets base frequency to 533 Hz

In older firmware versions this was the only way to set BPM. Newer versions (v11+) also store the canvas-level BPM in `tempoClockBPMCanvas`.

### Emitters (0–3)

The Tempera has 4 emitters, each a granular playback voice that can be positioned on the touch surface canvas.

| Key pattern | Type | Description |
|-------------|------|-------------|
| `emittor{N}Name` | string | Emitter name |
| `emittor{N}Volume` | float | Output volume |
| `emittor{N}Mute` | int | Mute on/off |
| `emittor{N}Lock` | int | Lock emitter position |
| `emittor{N}Octave` | int | Octave setting |
| `emittor{N}MidiChannel` | int | MIDI channel |
| `emittor{N}PlacementMode` | int | Placement mode |
| `emittor{N}FadeIn` | float | Fade in time |
| `emittor{N}FadeOut` | float | Fade out time |
| `emittor{N}SprayX` | float | Horizontal spray amount |
| `emittor{N}SprayY` | float | Vertical spray amount |
| `emittor{N}TwoLane` | int | Two-lane mode |
| `emittor{N}Direction` | int | Playback direction (v11+) |
| `emittor{N}EffectsSend` | float | Effects send level (v6+) |
| `emittor{N}Filter` | int | Filter on/off (v6+) |
| `emittor{N}RelX` | float | Relative X position (v6+) |
| `emittor{N}RelY` | float | Relative Y position (v6+) |

#### Grain Parameters

| Key pattern | Type | Description |
|-------------|------|-------------|
| `emittor{N}GrainSize` | float | Grain size |
| `emittor{N}GrainSizeMode` | int | Grain size mode |
| `emittor{N}GrainSizeTime` | int | Grain size time division |
| `emittor{N}GrainSizeJitter` | float | Grain size randomisation |
| `emittor{N}GrainDensity` | float | Grain density |
| `emittor{N}GrainDensityJitter` | float | Grain density randomisation |
| `emittor{N}GrainFade` | float | Grain crossfade amount |
| `emittor{N}GrainAlign` | int | Grain alignment on/off |
| `emittor{N}GrainAlignX` | int | Grain X alignment (v6+) |
| `emittor{N}GrainEnvelopeAttack` | int | Grain envelope attack shape (v6+) |
| `emittor{N}GrainPan` | float | Grain pan position |
| `emittor{N}GrainPanJitter` | float | Grain pan randomisation |
| `emittor{N}GrainPanMidSide` | int | Mid/side panning mode |

#### Filter & Tuning (per-emitter)

| Key pattern | Type | Description |
|-------------|------|-------------|
| `emittor{N}TiltFilterCentre` | float | Tilt filter centre frequency |
| `emittor{N}TiltFilterWidth` | float | Tilt filter width |
| `emittor{N}QuantizeAmount` | float | Pitch quantise amount |
| `emittor{N}QuantizeNote` | int | Pitch quantise scale/note |
| `emittor{N}TuneSpread` | float | Tuning spread amount |
| `emittor{N}TuneSpreadFifthSnap` | int | Snap spread to fifths (v6+) |
| `emittor{N}TuneSpreadOctaveSnap` | int | Snap spread to octaves (v6+) |

#### Euclidean Rhythm (v14+)

| Key pattern | Type | Description |
|-------------|------|-------------|
| `emittor{N}EuclidX` | int | Euclidean rhythm hits |
| `emittor{N}EuclidY` | int | Euclidean rhythm steps |
| `emittor{N}EuclidRotate` | int | Euclidean rhythm rotation |

### Cell-Emitter Mapping

The 8×8 touch grid has 64 cells (0–63). Each cell can be assigned to an emitter.

| Key pattern | Type | Description |
|-------------|------|-------------|
| `cellEmitter{N}` | int | Emitter index (0–3) or -1 (unassigned) |

### Modulators

Variable number of modulators depending on firmware version (5 in v2, 10 in v7+).

| Key pattern | Type | Description |
|-------------|------|-------------|
| `modulator{N}Type` | int | Modulator waveform type |
| `modulator{N}Amount` | float | Modulation depth (-1 to 1) |
| `modulator{N}Destination` | int | Modulation target parameter |
| `modulator{N}P1` | float | Parameter 1 (rate/shape) |
| `modulator{N}P2` | float | Parameter 2 (phase/shape) |
| `modulator{N}Polarity` | int | Uni/bipolar |
| `modulator{N}Sync` | int | Tempo sync on/off |
| `modulator{N}Free` | int | Free-running mode (v7+) |
| `modulator{N}Retrigger` | int | Retrigger on note (v14+) |

#### Step Sequencer Modulator (v11+)

| Key pattern | Type | Description |
|-------------|------|-------------|
| `modulator{N}StepCount` | int | Number of steps in sequence |
| `modulator{N}Step{M}` | float | Value for step M |
| `modulatorSizeTarget` | int | Modulator size routing target |
| `modulatorSizeTarget{N}` | int | Per-modulator size target |

### Effects

#### Chorus

| Key | Type | Description |
|-----|------|-------------|
| `chorusDepth` | float | Chorus depth |
| `chorusFlange` | float | Flanger amount |
| `chorusMix` | float | Wet/dry mix |
| `chorusSpeed` | float | Modulation speed |

#### Delay

| Key | Type | Description |
|-----|------|-------------|
| `delayTime` | float | Delay time |
| `delayFeedback` | float | Feedback amount |
| `delayMix` | float | Wet/dry mix |
| `delayColor` | float | Tone colour |
| `delayColorActive` | int | Colour filter active |
| `delayPingPong` | int | Ping-pong mode |
| `delaySync` | int | Tempo sync |
| `delayDot` | int | Dotted time (v7+) |

#### Reverb

| Key | Type | Description |
|-----|------|-------------|
| `reverbSize` | float | Room size |
| `reverbDamp` | float | Damping |
| `reverbMix` | float | Wet/dry mix |
| `reverbColor` | float | Tone colour |

#### Degrade (v14+)

| Key | Type | Description |
|-----|------|-------------|
| `degradeAge` | float | Degradation age/intensity |
| `degradeCompress` | float | Compression amount |
| `degradeMix` | float | Wet/dry mix |
| `degradeSlip` | float | Timing slip amount |

### Filter (Global)

| Key | Type | Description |
|-----|------|-------------|
| `filterType` | int | Filter type |
| `filterCutoff` | float | Cutoff frequency |
| `filterResonance` | float | Resonance |
| `filterKeytrack` | float | Key tracking amount |

### Amp Envelope

| Key | Type | Description |
|-----|------|-------------|
| `ampAttack` | float | Attack time |
| `ampDecay` | float | Decay time |
| `ampSustain` | float | Sustain level |
| `ampRelease` | float | Release time |

### Touchgrid / Keyboard

| Key | Type | Description |
|-----|------|-------------|
| `touchgridLayout` | int | Grid layout preset |
| `touchgridPlayMode` | int | Play mode |
| `touchgridOverlayMode` | int | Overlay keyboard mode |
| `touchgridKeyboardChannel` | int | MIDI channel |
| `touchgridTranspose` | int | Transpose (semitones) |

### MIDI Mapping

| Key pattern | Type | Description |
|-------------|------|-------------|
| `MI{N}` | int | MIDI input mapping for track N |
| `ML{N}` | int | MIDI learn mapping for track N |
| `manualControl{N}` | float | Manual control value for emitter N |

## Canvases Analysed

This format documentation was reverse-engineered by examining the following canvas files:

| Canvas | Version | Size | Source |
|--------|---------|------|--------|
| 3rd-wave | 15 | 31.8 MB | Gallery |
| BREAKSONE | 2 | 3.7 MB | Local |
| Speak&Spell | 7 | 33.9 MB | Gallery |
| dancing-notes | 14 | 23.5 MB | Gallery |
| dancing-notes-2 | 14 | 11.3 MB | Gallery |
| david-stevens | 15 | 15.4 MB | Gallery |
| flashy-spark | 2 | 14.1 MB | Gallery |
| fretless | 6 | 8.6 MB | Gallery |
| funky-core | 14 | 4.8 MB | Gallery |
| graphicvco-wavetable-synth-mode | 15 | 18.1 MB | Gallery |
| hell-on | 15 | 5.5 MB | Gallery |
| in-the-jongle | 11 | 15.0 MB | Gallery |
| lyra | 11 | 25.1 MB | Gallery |
| medieval-chaos | 14 | 15.0 MB | Gallery |
| meight | 4 | 15.5 MB | Gallery |
| nimble-trance | 15 | 21.7 MB | Gallery |
| rendezvous | 4 | 21.5 MB | Gallery |
| rolling-fantasy | 3 | 37.2 MB | Gallery |
| substantials-cfs1 | 11 | 37.2 MB | Gallery |
| substantials-cfs2 | 11 | 33.3 MB | Gallery |
| substantials-cfs3 | 11 | 31.8 MB | Gallery |
| tempera-cell-matrix | 15 | 20.0 MB | Gallery |
| tribal-puzzle | 15 | 13.8 MB | Gallery |

## Resources

- [Tempera Owner's Manual (PDF)](https://docs.beetlecrab.audio/tempera/_static/tempera_manual.pdf)
- [Tempera Online Manual — Tracks](https://docs.beetlecrab.audio/tempera/tracks.html)
- [Official Canvas Gallery](https://gallery.beetlecrab.audio/patches/)
- [Beetlecrab Tempera Homepage](https://beetlecrab.audio/tempera/)
- [Canvas Walkthrough (YouTube)](https://www.youtube.com/watch?v=qzPf6r-FwOk)
- [Canvas From Scratch Tutorial (YouTube)](https://www.youtube.com/watch?v=cIcJK0BDGvk)
- [Free Canvas Downloads — Red Means Recording (Patreon)](https://www.patreon.com/posts/free-download-104016065)
- [New Tempera Canvases — Red Means Recording (Patreon)](https://www.patreon.com/posts/new-tempera-107644277)
