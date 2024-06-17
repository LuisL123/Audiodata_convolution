import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
import numpy as np
from scipy.signal import butter, lfilter
import random

def apply_low_pass_filter(audio, cutoff):
    return low_pass_filter(audio, cutoff)

def apply_high_pass_filter(audio, cutoff):
    return high_pass_filter(audio, cutoff)

def apply_distortion(audio, gain):
    samples = np.array(audio.get_array_of_samples())
    samples = samples * gain
    samples = np.clip(samples, -32768, 32767)
    return audio._spawn(samples.astype(np.int16).tobytes())

def apply_reverb(audio, reverb_amount):
    samples = np.array(audio.get_array_of_samples())
    reverb_samples = np.convolve(samples, np.ones((reverb_amount,))/reverb_amount, mode='full')
    reverb_samples = np.clip(reverb_samples[:len(samples)], -32768, 32767)
    return audio._spawn(reverb_samples.astype(np.int16).tobytes())


class AudioEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Editor")
        
        self.filepath = ""
        self.audio = None
        
        self.load_button = tk.Button(root, text="Load WAV", command=self.load_wav)
        self.load_button.pack()

        self.low_pass_slider = self.create_slider("Low Pass Filter", 1, 5000, 1)
        self.high_pass_slider = self.create_slider("High Pass Filter", 1, 5000, 1)
        self.distortion_slider = self.create_slider("Distortion", 1, 10, 1)
        self.reverb_slider = self.create_slider("Reverb", 1, 100, 1)

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

        output_path = "output.wav"
        audio.export(output_path, format="wav")
        print("Saved to:", output_path)

    def randomize_filters(self):
        self.low_pass_slider.set(random.randint(0, 5000))
        self.high_pass_slider.set(random.randint(0, 5000))
        self.distortion_slider.set(random.randint(1, 10))
        self.reverb_slider.set(random.randint(1, 100))

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEditorApp(root)
    root.mainloop()

