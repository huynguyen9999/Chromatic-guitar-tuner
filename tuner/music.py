import numpy as np

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def freq_to_note(frequency):
    """Converts a frequency (Hz) to a musical note name and its offset in cents."""
    if frequency <= 0:
        return None, 0
    
    # Calculate fractional MIDI note number
    n = 12 * np.log2(frequency / 440.0) + 69
    midi_note = int(round(n))
    
    # Calculate deviation in cents (100 cents = 1 semitone)
    cents_off = (n - midi_note) * 100
    
    note_name = NOTE_NAMES[midi_note % 12]
    octave = (midi_note // 12) - 1
    
    return f"{note_name}{octave}", cents_off