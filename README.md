# Chromatic Guitar Tuner (DSP-Powered)

A real-time, high-precision chromatic guitar tuner built in Python. This project utilizes advanced digital signal processing (DSP) concepts, featuring a **Harmonic Product Spectrum (HPS)** algorithm combined with **Zero-Padding** and **Parabolic Interpolation** to achieve sub-Hz frequency accuracy, effectively overcoming the octave-errors common in naive pitch detection.

Unlike basic frequency counters that simply track the loudest spectral peak, this tuner is engineered to look past dominant overtones and isolate the true musical fundamental ($f_0$). It is highly resilient to background ambient noise and works beautifully across instruments with rich harmonic profiles, like acoustic or electric guitars.

---

## Core Architecture & DSP Theory

When an acoustic string is plucked, it vibrates across a complex series of overlapping frequencies. The target note is known as the **fundamental frequency**, while the quieter overtones vibrating above it at integer multiples ($2\times, 3\times, 4\times\dots$) are called **harmonics**.

### The Pitfall of Standard FFT
On stringed instruments (especially the thick low E string), the physical fundamental is often structurally weak, while its second or third harmonic dominates the signal. Standard microphone hardware also rolls off drastically at low frequencies ($\|E_2\| \approx 82.4\text{ Hz}$). A simple Fast Fourier Transform (FFT) peak-picker will frequently lock onto an overtone instead of the fundamental, causing frustrating octave leaps and invalid pitch readings.

### The Solution: Harmonic Product Spectrum (HPS)
The HPS algorithm mathematically forces these integer multiples to cancel out. 

1. It takes the magnitude spectrum from a raw windowed FFT.
2. It creates downsampled copies of the spectrum array (slicing by factors of 2, 3, 4, etc.).
3. It multiplies these arrays together element-wise.

Because harmonics occur at perfect integer multiples, downsampling effectively "folds" them back onto the position of the true fundamental frequency. Non-harmonic noise components do not share this integer spacing, meaning they drop to near-zero during the multiplication phase, leaving an incredibly sharp, unambiguous spike at the true fundamental frequency ($f_0$).

### Overcoming the Time-Frequency Uncertainty Principle
Real-time streams require tight buffer blocks to keep system latency imperceptible ($\|\text{Buffer}\| = 2048$ frames at $44.1\text{ kHz} \approx 46\text{ms}$). However, the raw frequency spacing ($\|\Delta f\|$) of an FFT is strictly bound by $\|\Delta f = \frac{f_s}{N}\|$. A 2048-sample block yields bins spaced a wide $21.53\text{ Hz}$ apart—unusable for tuning, where the distance between notes on a low string is less than $5\text{ Hz}$.

To resolve this without introducing massive buffer delays, this implementation leverages two critical optimization techniques:
* **Zero-Padding ($N_{\text{FFT}} = 16384$):** By appending empty values to the audio frame prior to running the FFT, we mathematically interpolate the frequency domain. This compresses the bin spacing down to a tight $\approx 2.7\text{ Hz}$ grid without waiting for more audio data.
* **Parabolic Interpolation:** Rather than selecting a fixed integer bin index, the algorithm fits a parabolic curve over the peak bin and its direct left and right neighbors. Calculating the apex of this curve yields fractional sub-bin precision, driving the frequency resolution down to a surgical $\pm 0.1\text{ Hz}$.

---

## 🛠️ Features

- **Asynchronous Audio Pipeline:** Uses thread-safe queue buffering (`queue.Queue`) to cleanly offload heavy mathematical operations and terminal rendering away from the high-priority hardware audio callback thread. Prevents audio dropouts, pops, and stutter.
- **Robust Harmonic Rejection:** Runs HPS on the complete, un-shifted spectrum array before window cropping to keep mathematical indices globally aligned.
- **Real-Time Deviation Metrics:** Converts raw frequencies into standard musical note scales and provides a running tuning deviation readout measured in **Cents** (where 100 cents equal exactly one semitone).

---

## 📦 Requirements & Installation

This project is fully tested on modern platforms, including Apple Silicon (M1/M2/M3) Macs and Windows/Linux systems.

### 1. System Dependency (PortAudio)
The underlying Python audio stream wrapper requires the cross-platform `PortAudio` library to interface with your machine's microphone hardware.

- **macOS (via Homebrew):**
  ```bash
  brew install portaudio

  sudo apt-get update
sudo apt-get install libportaudio2


python -m pip install sounddevice numpy

## Usage
python tuner.py

Tuner started. Pluck a string... (Press Ctrl+C to stop)
E2    |    81.9 Hz |  -11.2 cents
E2    |    82.4 Hz |   -0.3 cents
E2    |    82.5 Hz |   +1.1 cents


Reading the Cents Output
Negative Values (e.g., -15.0 cents): The pitch is Flat. Tighten the string peg.

Positive Values (e.g., +22.0 cents): The pitch is Sharp. Loosen the string peg.

Target Range (-3.0 to +3.0 cents): The instrument is perfectly In Tune.

