import numpy as np
from scipy import signal
import sounddevice as sd
import threading
import time
import keyboard
from dataclasses import dataclass
import queue
from typing import List, Dict, Optional, Tuple

@dataclass
class OscillatorParams:
    frequency: float
    waveform: str
    level: float
    phase: float
    sub_levels: List[float]

@dataclass
class ModulationParams:
    amount: float
    rate: float
    shape: str
    destination: str

class ModernSubharmonicon:
    def __init__(self, sample_rate: int = 44100):
        # Audio parameters
        self.sample_rate = sample_rate
        self.buffer_size = 1024
        self.audio_queue = queue.Queue(maxsize=64)
        
        # Synth state
        self.is_playing = False
        self.is_recording = False
        self.recording_buffer = []
        
        # Oscillator setup
        self.oscillators = [
            OscillatorParams(440.0, 'saw', 0.4, 0.0, [0.3, 0.3]),
            OscillatorParams(440.0, 'saw', 0.4, 0.0, [0.3, 0.3])
        ]
        
        # Effects parameters
        self.filter_cutoff = 2000.0
        self.filter_resonance = 1.0
        self.reverb_amount = 0.2
        self.delay_time = 0.25
        self.delay_feedback = 0.3
        
        # Sequencer
        self.sequence_length = 16
        self.step_duration = 0.25
        self.current_step = 0
        self.sequence = np.zeros((self.sequence_length, 4))
        self.sequence_playing = False
        
        # Keyboard mapping
        self.setup_keyboard_mapping()
        
        # Modulation
        self.modulations = []
        self.lfo_phase = 0.0
        
    def setup_keyboard_mapping(self):
        """Set up musical keyboard mapping and controls"""
        base_freq = 261.63  # C4
        semitone = 2 ** (1/12)
        
        # Musical keys (two octaves)
        self.key_to_freq = {}
        keys = ['z', 's', 'x', 'd', 'c', 'v', 'g', 'b', 'h', 'n', 'j', 'm',  # First octave
                ',', 'l', '.', ';', '/', "'"]                                  # Second octave
        
        for i, key in enumerate(keys):
            self.key_to_freq[key] = base_freq * (semitone ** i)
        
        # Control keys
        self.control_functions = {
            '1': self.cycle_waveform,
            '2': self.cycle_effects,
            '3': self.toggle_recording,
            'space': self.toggle_sequence,
            'up': lambda: self.adjust_parameter('filter_cutoff', 100),
            'down': lambda: self.adjust_parameter('filter_cutoff', -100),
            'left': lambda: self.adjust_parameter('reverb_amount', -0.1),
            'right': lambda: self.adjust_parameter('reverb_amount', 0.1)
        }
        
    def generate_waveform(self, frequency: float, waveform: str, phase: float = 0.0) -> np.ndarray:
        """Generate a single cycle of the specified waveform"""
        t = np.linspace(0, 2*np.pi, int(self.sample_rate/frequency), endpoint=False)
        phase_offset = phase * 2 * np.pi
        
        if waveform == 'saw':
            return signal.sawtooth(t + phase_offset)
        elif waveform == 'square':
            return signal.square(t + phase_offset)
        elif waveform == 'triangle':
            return signal.sawtooth(t + phase_offset, width=0.5)
        else:  # sine
            return np.sin(t + phase_offset)
            
    def apply_filter(self, audio: np.ndarray) -> np.ndarray:
        """Apply filter with current settings"""
        nyquist = self.sample_rate / 2
        normalized_cutoff = np.clip(self.filter_cutoff / nyquist, 0.01, 0.99)
        
        # Create filter coefficients
        b, a = signal.butter(2, normalized_cutoff, 'low')
        
        # Apply filter
        filtered = signal.lfilter(b, a, audio)
        
        # Add resonance if needed
        if self.filter_resonance > 1.0:
            resonant_freq = np.sin(2 * np.pi * self.filter_cutoff * np.arange(len(audio)) / self.sample_rate)
            filtered += resonant_freq * (self.filter_resonance - 1.0) * 0.1
            
        return np.clip(filtered, -1, 1)
        
    def apply_effects(self, audio: np.ndarray) -> np.ndarray:
        """Apply all effects in chain"""
        # Apply filter
        audio = self.apply_filter(audio)
        
        # Apply reverb
        if self.reverb_amount > 0:
            reverb_time = int(self.sample_rate * 0.1)  # 100ms reverb
            impulse = np.exp(-np.linspace(0, 10, reverb_time))
            audio = signal.convolve(audio, impulse * self.reverb_amount, mode='same')
        
        # Apply delay
        if self.delay_feedback > 0:
            delay_samples = int(self.delay_time * self.sample_rate)
            delayed = np.zeros_like(audio)
            for i in range(1, 4):
                delayed = np.roll(audio, delay_samples * i) * (self.delay_feedback ** i)
                audio += delayed
        
        return np.clip(audio, -1, 1)
        
    def handle_key_press(self, key):
        """Handle keyboard input"""
        try:
            print(f"Key pressed: {key.name}")  # Debug output
            if key.name in self.key_to_freq:
                freq = self.key_to_freq[key.name]
                print(f"Playing frequency: {freq}")  # Debug output
                self.play_note(freq)
            elif key.name in self.control_functions:
                print(f"Control key: {key.name}")  # Debug output
                self.control_functions[key.name]()
        except Exception as e:
            print(f"Error handling key press: {e}")
            
    def play_note(self, frequency: float):
        """Play a note at the specified frequency"""
        try:
            # Update oscillator frequencies
            self.oscillators[0].frequency = frequency
            self.oscillators[1].frequency = frequency * 1.5  # Fifth above
            
            # Generate and play audio directly
            audio = self.generate_voice()
            sd.play(audio, self.sample_rate, blocking=False)
            
            if self.is_recording:
                self.recording_buffer.append(audio)
                
            print(f"Playing note: {frequency:.1f} Hz")  # Debug output
        except Exception as e:
            print(f"Error playing note: {e}")
            
    def generate_voice(self) -> np.ndarray:
        """Generate audio for current oscillator settings"""
        duration = 0.1  # 100ms buffer
        samples = int(self.sample_rate * duration)
        mixed = np.zeros(samples)
        
        # Generate main oscillators
        for osc in self.oscillators:
            wave = self.generate_waveform(osc.frequency, osc.waveform, osc.phase)
            wave = np.resize(wave, samples) * osc.level
            
            # Generate subharmonics
            for sub_level, division in zip(osc.sub_levels, [2, 3]):
                sub_freq = osc.frequency / division
                sub_wave = self.generate_waveform(sub_freq, osc.waveform, osc.phase)
                sub_wave = np.resize(sub_wave, samples) * sub_level
                wave += sub_wave
                
            mixed += wave
            
        # Normalize and apply effects
        mixed = mixed / len(self.oscillators)
        mixed = self.apply_effects(mixed)
        
        return mixed
        
    def cycle_waveform(self):
        """Cycle through available waveforms"""
        waveforms = ['saw', 'square', 'triangle', 'sine']
        current = self.oscillators[0].waveform
        next_idx = (waveforms.index(current) + 1) % len(waveforms)
        new_waveform = waveforms[next_idx]
        
        for osc in self.oscillators:
            osc.waveform = new_waveform
            
        print(f"Waveform: {new_waveform}")
        
    def cycle_effects(self):
        """Cycle through effect combinations"""
        if self.filter_cutoff > 1000:  # Current: No effects
            self.filter_cutoff = 800
            self.reverb_amount = 0
            print("Effects: Filter")
        elif self.reverb_amount == 0:  # Current: Filter only
            self.filter_cutoff = 2000
            self.reverb_amount = 0.3
            print("Effects: Reverb")
        elif self.filter_cutoff > 1000:  # Current: Reverb only
            self.filter_cutoff = 800
            self.reverb_amount = 0.3
            print("Effects: Filter + Reverb")
        else:  # Current: Both
            self.filter_cutoff = 2000
            self.reverb_amount = 0
            print("Effects: None")
            
    def toggle_recording(self):
        """Toggle recording state"""
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.recording_buffer = []
            print("Recording started...")
        else:
            if len(self.recording_buffer) > 0:
                # Save recording buffer to sequence
                recorded = np.concatenate(self.recording_buffer)
                # TODO: Implement quantization and sequence conversion
                print("Recording stopped. Length:", len(recorded)/self.sample_rate, "seconds")
            
    def toggle_sequence(self):
        """Toggle sequence playback"""
        self.sequence_playing = not self.sequence_playing
        if self.sequence_playing:
            # Set up a simple sequence if empty
            if not np.any(self.sequence):
                for i in range(self.sequence_length):
                    self.sequence[i, 0] = 1.0 if i % 4 == 0 else 0.0
                    self.sequence[i, 1] = 1.0 if i % 3 == 0 else 0.0
            print("Sequence: Playing")
        else:
            print("Sequence: Stopped")
            
    def adjust_parameter(self, param: str, amount: float):
        """Adjust a parameter by the specified amount"""
        current = getattr(self, param)
        setattr(self, param, current + amount)
        print(f"{param}: {getattr(self, param):.2f}")
        
    def audio_processor(self):
        """Main audio processing loop"""
        print("Audio processor started")  # Debug output
        while self.is_playing:
            try:
                if self.sequence_playing:
                    # Play sequence
                    if np.any(self.sequence[self.current_step]):
                        audio = self.generate_voice()
                        sd.play(audio, self.sample_rate, blocking=False)
                        print(f"Playing sequence step {self.current_step}")  # Debug output
                    self.current_step = (self.current_step + 1) % self.sequence_length
                    time.sleep(self.step_duration)
                else:
                    time.sleep(0.01)  # Small delay to prevent CPU overload
            except Exception as e:
                print(f"Audio processing error: {e}")
                
    def start(self):
        """Start the synth"""
        print("\nModern Subharmonicon")
        print("-------------------")
        print("Musical keys: Z-M, comma, period, slash (like a piano)")
        print("Controls:")
        print("  1: Change waveform")
        print("  2: Cycle effects")
        print("  3: Toggle recording")
        print("  Space: Toggle sequence")
        print("  Arrow keys: Adjust filter (↑↓) and reverb (←→)")
        print("  Esc: Quit")
        
        self.is_playing = True
        
        # Start audio processing thread
        self.audio_thread = threading.Thread(target=self.audio_processor)
        self.audio_thread.start()
        
        # Set up keyboard hooks
        for key in self.key_to_freq:
            keyboard.on_press_key(key, self.handle_key_press)
        for key in self.control_functions:
            keyboard.on_press_key(key, self.handle_key_press)
            
        # Wait for escape key
        keyboard.wait('esc')
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources"""
        self.is_playing = False
        self.sequence_playing = False
        time.sleep(0.5)  # Allow threads to finish
        print("\nShutting down...")

if __name__ == "__main__":
    synth = ModernSubharmonicon()
    synth.start()