import sounddevice as sd
import queue
import sys

# Audio System Constants
SAMPLE_RATE = 44100   
BUFFER_SIZE = 2048    # Low buffer size keeping latency low (~46ms)

# Thread-safe queue to pass audio from the microphone callback to the main loop
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Captures incoming audio from hardware and passes it safely to the queue."""
    if status:
        print(status, file=sys.stderr)
    # Push mono channel data into the queue
    audio_queue.put(indata[:, 0].copy())

# Initialize the stream configuration
stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    blocksize=BUFFER_SIZE,
    callback=audio_callback
)