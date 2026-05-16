import numpy as np
import sounddevice as sd
import queue
import sys

from tuner.dsp import apply_window, compute_fft, harmonic_product_spectrum
from tuner.dsp import freq_to_note

SAMPLE_RATE = 44100   
BUFFER_SIZE = 2048    # Low buffer size keeping latency low (~46ms)
N_FFT = 16384         # Zero-padded FFT size for high frequency resolution

# Thread-safe queue to pass audio from the microphone callback to the main loop
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # Push mono channel data into the queue
    audio_queue.put(indata[:, 0].copy())


def process(audio_buffer):
    if np.max(np.abs(audio_buffer)) < 0.01:
        return

    windowed = apply_window(audio_buffer)
    spectrum, freqs = compute_fft(windowed, SAMPLE_RATE, N_FFT)

    # 1. Run HPS on the FULL spectrum first to keep index math valid
    hps = harmonic_product_spectrum(spectrum, num_harmonics=4)
    # Sync the frequency array size with the truncated HPS array size
    freqs_hps = freqs[:len(hps)]

    # 2. Crop the HPS results to guitar ranges
    low_idx = np.searchsorted(freqs_hps, 80)
    high_idx = np.searchsorted(freqs_hps, 1200)
    
    hps_cropped = hps[low_idx:high_idx]
    freqs_cropped = freqs_hps[low_idx:high_idx]

    if len(hps_cropped) == 0:
        return

    peak_idx = np.argmax(hps_cropped)
    
    # 3. Parabolic Interpolation for sub-bin precision
    if 0 < peak_idx < len(hps_cropped) - 1:
        y1 = hps_cropped[peak_idx - 1]
        y2 = hps_cropped[peak_idx]
        y3 = hps_cropped[peak_idx + 1]
        denom = (2 * y2 - y1 - y3)
        if denom != 0:
            p = 0.5 * (y1 - y3) / denom
            # Adjust fundamental frequency by fractional bin amount
            bin_spacing = freqs_cropped[1] - freqs_cropped[0]
            fundamental_freq = freqs_cropped[peak_idx] + p * bin_spacing
        else:
            fundamental_freq = freqs_cropped[peak_idx]
    else:
        fundamental_freq = freqs_cropped[peak_idx]

    note, cents = freq_to_note(fundamental_freq)
    print(f"{note:<5} | {fundamental_freq:7.1f} Hz | {cents:+6.1f} cents")
    # if between +- 5 cents, you're in tune!

# Start the audio stream
stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    blocksize=BUFFER_SIZE,
    callback=audio_callback
)

print("Tuner started. Pluck a string... (Press Ctrl+C to stop)")
with stream:
    try:
        while True:
            # Block until a new audio buffer frame is ready
            buffer_data = audio_queue.get()
            process(buffer_data)
    except KeyboardInterrupt:
        print("\nStopping Tuner.")