import numpy as np
from scipy import signal
import sounddevice as sd
import threading
import time
from typing import List, Dict

class SubharmoniconEmulator:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.main_oscillators = [440.0, 440.0]  # VCO1 and VCO2 frequencies
        self.sub_oscillators = [[220.0, 146.67], [220.0, 146.67]]  # Subharmonics for each VCO
        self.rhythm_generators = [1, 2, 3, 4]  # Four rhythm generators
        self.step_duration = 0.25  # Duration of each step in seconds
        self.is_playing = False
        self.current_step = 0
        self.sequence = np.zeros(16)  # 16-step sequence
        
    def generate_waveform(self, frequency: float, duration: float) -> np.ndarray:
        """Generate a single waveform at specified frequency."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Combine sawtooth and square waves for richer timbre
        saw = signal.sawtooth(2 * np.pi * frequency * t)
        square = signal.square(2 * np.pi * frequency * t)
        return 0.5 * (saw + square)
    
    def generate_voice(self, main_freq: float, sub_freqs: List[float], duration: float) -> np.ndarray:
        """Generate a voice combining main oscillator with its subharmonics."""
        main_wave = self.generate_waveform(main_freq, duration)
        sub_waves = [self.generate_waveform(freq, duration) for freq in sub_freqs]
        # Mix all waves together
        mixed = main_wave * 0.4  # Main oscillator at 40% volume
        for sub_wave in sub_waves:
            mixed += sub_wave * 0.3  # Subharmonics at 30% volume each
        return mixed / (1 + len(sub_freqs))  # Normalize
    
    def apply_envelope(self, audio: np.ndarray) -> np.ndarray:
        """Apply a simple ADSR envelope to the audio."""
        samples = len(audio)
        attack = int(0.05 * samples)  # 5% attack
        decay = int(0.1 * samples)    # 10% decay
        sustain = int(0.5 * samples)  # 50% sustain
        release = samples - attack - decay - sustain
        
        envelope = np.ones(samples)
        # Attack
        envelope[:attack] = np.linspace(0, 1, attack)
        # Decay
        envelope[attack:attack+decay] = np.linspace(1, 0.7, decay)
        # Sustain
        envelope[attack+decay:attack+decay+sustain] = 0.7
        # Release
        envelope[attack+decay+sustain:] = np.linspace(0.7, 0, release)
        
        return audio * envelope
    
    def generate_step(self, step: int) -> np.ndarray:
        """Generate audio for a single step in the sequence."""
        duration = self.step_duration
        # Generate both voices
        voice1 = self.generate_voice(self.main_oscillators[0], self.sub_oscillators[0], duration)
        voice2 = self.generate_voice(self.main_oscillators[1], self.sub_oscillators[1], duration)
        # Mix voices based on sequence value
        mixed = (voice1 + voice2) * self.sequence[step]
        return self.apply_envelope(mixed)
    
    def play_sequence(self):
        """Play the sequence continuously."""
        while self.is_playing:
            step_audio = self.generate_step(self.current_step)
            sd.play(step_audio, self.sample_rate, blocking=True)
            self.current_step = (self.current_step + 1) % 16
            
    def start(self):
        """Start playing the sequence."""
        if not self.is_playing:
            self.is_playing = True
            self.play_thread = threading.Thread(target=self.play_sequence)
            self.play_thread.start()
            
    def stop(self):
        """Stop playing the sequence."""
        self.is_playing = False
        if hasattr(self, 'play_thread'):
            self.play_thread.join()
            
    def set_sequence(self, steps: List[float]):
        """Set the sequence pattern (16 steps, values 0-1)."""
        self.sequence = np.array(steps[:16])
        
    def set_main_frequency(self, osc_index: int, frequency: float):
        """Set the frequency of a main oscillator."""
        self.main_oscillators[osc_index] = frequency
        # Update subharmonics accordingly
        self.sub_oscillators[osc_index][0] = frequency / 2  # First subharmonic
        self.sub_oscillators[osc_index][1] = frequency / 3  # Second subharmonic
        
    def set_rhythm(self, generator_index: int, division: int):
        """Set the rhythm division for a rhythm generator."""
        self.rhythm_generators[generator_index] = division

# Example usage
if __name__ == "__main__":
    # Create synth instance
    synth = SubharmoniconEmulator()
    
    # Set up a simple sequence
    sequence = [1.0 if i % 4 == 0 else 0.5 if i % 2 == 0 else 0.0 for i in range(16)]
    synth.set_sequence(sequence)
    
    # Set frequencies
    synth.set_main_frequency(0, 440)  # A4 for first oscillator
    synth.set_main_frequency(1, 554.37)  # C#5 for second oscillator
    
    # Start playback
    print("Playing sequence... Press Ctrl+C to stop")
    try:
        synth.start()
        time.sleep(10)  # Play for 10 seconds
    except KeyboardInterrupt:
        pass
    finally:
        synth.stop()