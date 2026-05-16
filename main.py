import numpy as np
import sounddevice as sd
import queue 

SAMPLE_RATE = 44100   # samples per second
BUFFER_SIZE = 2048    # how many samples per chunk (~46ms of audio)

def audio_callback(indata, frames, time, status):
    # indata shape: (BUFFER_SIZE, channels)
    # take only the first channel (mono)
    audio_buffer = indata[:, 0].copy()
    process(audio_buffer)

stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    blocksize=BUFFER_SIZE,
    callback=audio_callback
)
stream.start()

def apply_window(audio_buffer):
    window = np.hanning(len(audio_buffer))
    return audio_buffer * window

def compute_fft(windowed_buffer, sample_rate):
    spectrum = np.abs(np.fft.rfft(windowed_buffer))
    freqs = np.fft.rfftfreq(len(windowed_buffer), d=1.0 / sample_rate)
    return spectrum, freqs

def harmonic_product_spectrum(spectrum, num_harmonics=5):
    hps = spectrum.copy()
    for h in range(2, num_harmonics + 1):
        # downsample spectrum by factor h
        downsampled = spectrum[::h]
        # multiply — only keep frequency bins that exist in the shorter version
        hps[:len(downsampled)] *= downsampled
    return hps

# Convert Hz to a note name
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def freq_to_note(frequency):
    if frequency <= 0:
        return None, 0
    # MIDI note number (can be fractional)
    n = 12 * np.log2(frequency / 440.0) + 69
    # nearest integer note
    midi_note = int(round(n))
    # how far off from perfectly in tune (in cents, 100 cents = 1 semitone)
    cents_off = (n - midi_note) * 100
    note_name = NOTE_NAMES[midi_note % 12]
    octave = (midi_note // 12) - 1
    return f"{note_name}{octave}", cents_off

# putting everything together
def process(audio_buffer):
    # ignore quiet signals (not playing anything)
    if np.max(np.abs(audio_buffer)) < 0.01:
        return

    windowed = apply_window(audio_buffer)
    spectrum, freqs = compute_fft(windowed, SAMPLE_RATE)

    # only look at guitar-relevant frequencies (80 Hz - 1200 Hz)
    low_idx = np.searchsorted(freqs, 80)
    high_idx = np.searchsorted(freqs, 1200)
    spectrum_cropped = spectrum[low_idx:high_idx]
    freqs_cropped = freqs[low_idx:high_idx]

    hps = harmonic_product_spectrum(spectrum_cropped)
    peak_idx = np.argmax(hps)
    fundamental_freq = freqs_cropped[peak_idx]

    note, cents = freq_to_note(fundamental_freq)
    print(f"{note}  |  {fundamental_freq:.1f} Hz  |  {cents:+.1f} cents")