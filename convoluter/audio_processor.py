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
    delay = int(1000 / reverb_amount)  # Delay in ms, inversely proportional to the reverb amount
    decay = 0.5  # Decay factor for the reverb effect

    delayed_audio = audio - 6  # Lower the volume of the delayed audio
    for _ in range(reverb_amount):
        audio = audio.overlay(delayed_audio, position=delay)
        delay *= 2  # Increase delay for subsequent echoes
        delayed_audio = delayed_audio - 6  # Further lower the volume of the delayed audio

    return audio

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

def add_mechanical_noise(audio, noise_level, mechanical_noise):
    if noise_level == 0:
        return audio
    
    audio_duration = len(audio)
    mechanical_noise_duration = len(mechanical_noise)
    
    if audio_duration > mechanical_noise_duration:
        raise ValueError("Mechanical noise audio is shorter than the input audio.")
    
    start_time = random.randint(0, mechanical_noise_duration - audio_duration)
    noise_segment = mechanical_noise[start_time:start_time + audio_duration]
    noise_segment = noise_segment - (50 - noise_level)  # Adjust noise level

    combined = audio.overlay(noise_segment)
    return combined


class AudioEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Editor")
        
        self.filepath = ""
        self.audio = None
        
        self.load_button = tk.Button(root, text="Load WAV", command=self.load_wav)
        self.load_button.pack()

        self.low_pass_slider = self.create_slider("Low Pass Filter", 300, 5000, 5000)  # Adjusted range
        self.high_pass_slider = self.create_slider("High Pass Filter", 20, 3000, 20)  # Adjusted range
        self.distortion_slider = self.create_slider("Distortion", 1, 10, 1)  # Neutral value
        self.reverb_slider = self.create_slider("Reverb", 1, 10, 1)  # Neutral value

        self.low_eq_slider = self.create_slider("Low EQ", 0, 10, 1)  # Neutral value
        self.mid_eq_slider = self.create_slider("Mid EQ", 0, 10, 1)  # Neutral value
        self.high_eq_slider = self.create_slider("High EQ", 0, 10, 1)  # Neutral value
        
        self.mechanical_noise_slider = self.create_slider("Mechanical Noise", 0, 40, 0)  # Adjusted range
        
        # Adding multiple ambient sound files
        self.ambient_sounds = [
            {"label": "Traffic Sound", "file": "/Users/luisliu/Desktop/Audiodata_convolution/convoluter/Traffic Sound 32180.mp3"},
            {"label": "Mechanical Noise", "file": "/Users/luisliu/Desktop/Audiodata_convolution/convoluter/Mechanical noise.m4a"},
            # Add paths to your additional ambient sound files here
            {"label": "Park Sound", "file": "/Users/luisliu/Desktop/Audiodata_convolution/convoluter/Central Park Sound.mp3"},
            {"label": "Subway Sound", "file": "/Users/luisliu/Desktop/Audiodata_convolution/convoluter/Subway Train Door Opening Sound.mp3"},
            {"label": "Chatter Sound", "file": "/Users/luisliu/Desktop/Audiodata_convolution/convoluter/Restaurant Chattering.mp3"}
        ]

        self.ambient_toggles = []
        self.ambient_sliders = []
        
        for ambient in self.ambient_sounds:
            toggle_var = tk.BooleanVar()
            toggle = self.create_toggle(ambient["label"], toggle_var)
            slider = self.create_slider(ambient["label"] + " Volume", 20, 35, 20)
            self.ambient_toggles.append(toggle_var)
            self.ambient_sliders.append(slider)
        
        self.randomize_button = tk.Button(root, text="Randomize", command=self.randomize_filters)
        self.randomize_button.pack()

        self.apply_button = tk.Button(root, text="Apply Filters", command=self.apply_filters)
        self.apply_button.pack()

        self.ambient_audio_segments = {
            ambient["label"]: AudioSegment.from_file(ambient["file"])
            for ambient in self.ambient_sounds
        }

    def create_slider(self, label, from_, to, default):
        frame = tk.Frame(self.root)
        frame.pack()
        label = tk.Label(frame, text=label)
        label.pack(side=tk.LEFT)
        slider = tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL)
        slider.set(default)
        slider.pack(side=tk.RIGHT)
        return slider

    def create_toggle(self, label, variable):
        frame = tk.Frame(self.root)
        frame.pack()
        label = tk.Label(frame, text=label)
        label.pack(side=tk.LEFT)
        toggle = tk.Checkbutton(frame, variable=variable)
        toggle.pack(side=tk.RIGHT)
        return toggle

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
        audio = add_mechanical_noise(audio, self.mechanical_noise_slider.get(), self.ambient_audio_segments["Mechanical Noise"])
        
        # Randomly choose an active ambient sound
        active_ambient_sounds = [
            i for i, toggle_var in enumerate(self.ambient_toggles) if toggle_var.get()
        ]

        if active_ambient_sounds:
            chosen_index = random.choice(active_ambient_sounds)
            chosen_ambient = self.ambient_sounds[chosen_index]["label"]
            ambient_volume = self.ambient_sliders[chosen_index].get()
            ambient_audio = self.ambient_audio_segments[chosen_ambient] - (50 - ambient_volume)  # Adjust ambient sound level
            
            # Randomize the start interval of the ambient sound
            if len(audio) < len(ambient_audio):
                start_time = random.randint(0, len(ambient_audio) - len(audio))
                ambient_audio = ambient_audio[start_time:start_time + len(audio)]
            
            audio = audio.overlay(ambient_audio)
        
        output_path = "output.wav"
        audio.export(output_path, format="wav")
        print("Saved to:", output_path)

    def randomize_filters(self):
        self.low_pass_slider.set(random.randint(300, 5000))
        self.high_pass_slider.set(random.randint(20, 3000))
        self.distortion_slider.set(random.randint(1, 10))
        self.reverb_slider.set(random.randint(1, 10))
        self.low_eq_slider.set(random.randint(0, 10))
        self.mid_eq_slider.set(random.randint(0, 10))
        self.high_eq_slider.set(random.randint(0, 10))
        self.mechanical_noise_slider.set(random.randint(20, 35))
        
        for toggle_var in self.ambient_toggles:
            toggle_var.set(False)
        
        chosen_index = random.randint(0, len(self.ambient_toggles) - 1)
        self.ambient_toggles[chosen_index].set(True)
        
        for slider in self.ambient_sliders:
            slider.set(random.randint(25, 35))

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEditorApp(root)
    root.mainloop()