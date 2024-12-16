# AudioData Convoluter

AudioData Convoluter is a Python-based tool designed for creating augmented audio datasets. This project allows you to input a set of audio files and generate modified copies with various transformations such as adding filters, noise, pitch shifting, and more. It provides a simple Python GUI for configuring these parameters and can also randomize them for greater variability in the output data.

This tool is ideal for generating diverse audio datasets for training neural networks, especially in scenarios where real-world audio data is noisy or inconsistent.

## Features

- **Audio Transformations**:
  - Add filters (low-pass, high-pass, etc.)
  - Introduce noise (Mechanical, Electrical, Traffic, a mix of them) with adjustable intensities.
  - Shift pitch
  - Other customizable transformations
- **Randomization**:
  - Automatically randomize parameters to create diverse datasets.
- **User-Friendly GUI**:
  - Set parameters and generate transformed files through an interactive Python GUI.
- **Batch Processing**:
  - Process multiple audio files at once to save time.
- **Purpose-Built for Neural Network Training**:
  - Generate data that mimics real-world audio conditions for robust model training.

## Motivation

While developing **Synfi**, an AI music application, I needed to train a neural network capable of recognizing notes from hummed melodies by amateur singers. However, real-world recordings often contain noise, inconsistencies, and imperfections. This tool was created to simulate those conditions, enabling the generation of training datasets that better reflect real-world scenarios.

## Requirements

- Python 3.8 or later
- Required Python libraries:
  - `numpy`
  - `scipy`
  - `pydub`
  - `tkinter`
- Ensure you have an appropriate environment for running Python GUI applications.

## How to set up and use it

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/audiodata-convoluter.git
   cd audiodata-convoluter
2. Install all dependencies.
3. Run the program:
   ```bash
   python audio_processor.py #or
   python3 audio_processor.py
3. Use the Python GUI to:
  * Select the audio files you want to process.
  * Configure transformation parameters (filters, noise, pitch shifting, etc.).
  * Optionally, randomize the parameters for greater variability.

## Contribution

Contributions are welcome! The idea of this program is to facilitate the process of audio data creation and quality. If you'd like to improve this project or add new features, feel free to open an issue or submit a pull request.




