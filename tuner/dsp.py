import numpy as np

def apply_window(audio_buffer):
    return audio_buffer * np.hanning(len(audio_buffer))

def compute_fft(windowed_buffer, sample_rate, n_fft):
    # Pass n=N_FFT to automatically zero-pad the buffer
    spectrum = np.abs(np.fft.rfft(windowed_buffer, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    return spectrum, freqs

def harmonic_product_spectrum(spectrum, num_harmonics=4):
    # Limit the max length to prevent array sizing mismatches during downsampling
    max_len = len(spectrum) // num_harmonics
    hps = spectrum[:max_len].copy()
    
    for h in range(2, num_harmonics + 1):
        downsampled = spectrum[::h][:max_len]
        hps *= downsampled
        
    return hps