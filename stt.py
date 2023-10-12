import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import requests


def listen():
    print("Speak now...")
    # Sampling frequency
    freq = 16000

    # Recording duration
    duration = 5

    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq),
                       samplerate=freq, channels=1)

    # Record audio for the given number of seconds
    sd.wait()

    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write("voices/recording0.wav", freq, recording)

    # Convert the NumPy array to audio file
    # wv.write("recording1.wav", recording, freq, sampwidth=2)

    url = "https://api.muxlisa.uz/v1/api/services/stt/"

    payload = {'token': 'vhRe6NFj9CJwpkW_U07dEQ'}
    files = [
        ('audio', ('recording0.wav', open('/home/ilyos/Work/archive/voices/recording0.wav', 'rb'), 'audio/wav'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response.text


print(listen())
