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
