import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
from pydub.generators import WhiteNoise, Sine
from pydub.effects import low_pass_filter, high_pass_filter
import numpy as np
from scipy.signal import butter, lfilter
import random

def apply_low_pass_filter(audio, cutoff):
    if cutoff >= 5000:
        return audio # Set a minimum cutoff frequency
    return low_pass_filter(audio, cutoff)

def apply_high_pass_filter(audio, cutoff):
    if cutoff <= 20:
        return audio  # Set a minimum cutoff frequency
    return high_pass_filter(audio, cutoff)

def apply_distortion(audio, gain):
    if gain == 1:
        return audio
    samples = np.array(audio.get_array_of_samples())
    samples = samples * gain
    samples = np.clip(samples, -32768, 32767)
    return audio._spawn(samples.astype(np.int16).tobytes())

def apply_reverb(audio, reverb_amount):
    if reverb_amount == 1:
        return audio
    samples = np.array(audio.get_array_of_samples())
    reverb_samples = np.convolve(samples, np.ones((reverb_amount,))/reverb_amount, mode='full')
    reverb_samples = np.clip(reverb_samples[:len(samples)], -32768, 32767)
    return audio._spawn(reverb_samples.astype(np.int16).tobytes())

def apply_eq(audio, low_gain, mid_gain, high_gain):
    if low_gain == 1 and mid_gain == 1 and high_gain == 1:
        return audio
    def band_pass_filter(audio, lowcut, highcut):
        nyquist = 0.5 * audio.frame_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(1, [low, high], btype='band')
        return lfilter(b, a, audio.get_array_of_samples())

    samples = np.array(audio.get_array_of_samples())

    # Low frequencies
    low_samples = band_pass_filter(audio, 20, 250)
    low_samples = low_samples * low_gain

    # Mid frequencies
    mid_samples = band_pass_filter(audio, 250, 4000)
    mid_samples = mid_samples * mid_gain

    # High frequencies
    high_samples = band_pass_filter(audio, 4000, 20000)
    high_samples = high_samples * high_gain

    # Combine bands
    eq_samples = low_samples + mid_samples + high_samples
    eq_samples = np.clip(eq_samples, -32768, 32767)

    return audio._spawn(eq_samples.astype(np.int16).tobytes())

def add_electrical_noise(audio, noise_level):
    if noise_level == 0:
        return audio
    noise = WhiteNoise().to_audio_segment(duration=len(audio))
    noise = noise - (50 - noise_level)  # Adjust noise level
    combined = audio.overlay(noise)
    return combined

def add_mechanical_noise(audio, noise_level):
    if noise_level == 0:
        return audio
    thump = Sine(50).to_audio_segment(duration=10).fade_in(5).fade_out(5) - (50 - noise_level)
    thump_sequence = [thump for _ in range(len(audio) // 5000)]
    noise = AudioSegment.silent(duration=len(audio))
    for i, t in enumerate(thump_sequence):
        noise = noise.overlay(t, position=i*5000)
    combined = audio.overlay(noise)
    return combined


# ambient sounds: traffic, parks, subway, wind, chatter.


class AudioEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Editor")
        
        self.filepath = ""
        self.audio = None
        
        self.load_button = tk.Button(root, text="Load WAV", command=self.load_wav)
        self.load_button.pack()

        self.low_pass_slider = self.create_slider("Low Pass Filter", 20, 5000, 5000)  # Neutral value
        self.high_pass_slider = self.create_slider("High Pass Filter", 20, 5000, 20)  # Neutral value
        self.distortion_slider = self.create_slider("Distortion", 1, 10, 1)  # Neutral value
        self.reverb_slider = self.create_slider("Reverb", 1, 100, 1)  # Neutral value

        self.low_eq_slider = self.create_slider("Low EQ", 0, 10, 1)  # Neutral value
        self.mid_eq_slider = self.create_slider("Mid EQ", 0, 10, 1)  # Neutral value
        self.high_eq_slider = self.create_slider("High EQ", 0, 10, 1)  # Neutral value
        
        # self.electrical_noise_slider = self.create_slider("Electrical Noise", 0, 50, 0)  # Neutral value
        self.mechanical_noise_slider = self.create_slider("Mechanical Noise", 0, 50, 0)  # Neutral value

        self.randomize_button = tk.Button(root, text="Randomize", command=self.randomize_filters)
        self.randomize_button.pack()

        self.apply_button = tk.Button(root, text="Apply Filters", command=self.apply_filters)
        self.apply_button.pack()

    def create_slider(self, label, from_, to, default):
        frame = tk.Frame(self.root)
        frame.pack()
        label = tk.Label(frame, text=label)
        label.pack(side=tk.LEFT)
        slider = tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL)
        slider.set(default)
        slider.pack(side=tk.RIGHT)
        return slider

    def load_wav(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        self.audio = AudioSegment.from_wav(self.filepath)
        print("Loaded:", self.filepath)

    def apply_filters(self):
        if not self.audio:
            return
        
        audio = self.audio
        audio = apply_low_pass_filter(audio, self.low_pass_slider.get())
        audio = apply_high_pass_filter(audio, self.high_pass_slider.get())
        audio = apply_distortion(audio, self.distortion_slider.get())
        audio = apply_reverb(audio, self.reverb_slider.get())
        audio = apply_eq(audio, self.low_eq_slider.get(), self.mid_eq_slider.get(), self.high_eq_slider.get())
        # audio = add_electrical_noise(audio, self.electrical_noise_slider.get())
        audio = add_mechanical_noise(audio, self.mechanical_noise_slider.get())

        output_path = "output.wav"
        audio.export(output_path, format="wav")
        print("Saved to:", output_path)

    def randomize_filters(self):
        self.low_pass_slider.set(random.randint(1, 5000))
        self.high_pass_slider.set(random.randint(1, 5000))
        self.distortion_slider.set(random.randint(1, 10))
        self.reverb_slider.set(random.randint(1, 100))
        self.low_eq_slider.set(random.randint(0, 10))
        self.mid_eq_slider.set(random.randint(0, 10))
        self.high_eq_slider.set(random.randint(0, 10))
        # self.electrical_noise_slider.set(random.randint(0, 50))
        self.mechanical_noise_slider.set(random.randint(0, 50))

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEditorApp(root)
    root.mainloop()

