import pygame
import numpy as np
import sounddevice as sd
from scipy.fftpack import fft
import colorsys
import random
import math
from collections import deque

# Initialize PyGame
pygame.init()

# Enhanced Audio Configuration
SAMPLE_RATE = 44100
BUFFER_SIZE = 2048  # Increased buffer size for better frequency resolution
FFT_SMOOTHING = 0.7  # Smoothing factor for FFT data

# Window Configuration
WIDTH = 1200
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Rhythm-Based Music Visualizer")

# Refined color scheme with more dynamic range
BACKGROUND_COLOR = (10, 10, 15)  # Darker background
COLOR_SCHEME = {
    'sub_bass': (0.98, 0.8, 0.8),    # Deeper red
    'bass': (0.88, 0.8, 0.8),        # Richer orange
    'low_mid': (0.75, 0.7, 0.7),     # Warmer green
    'mid': (0.65, 0.7, 0.8),         # Deeper blue
    'high_mid': (0.55, 0.7, 0.8),    # Richer purple
    'high': (0.45, 0.7, 0.8)         # Deeper indigo
}

# Refined frequency bands for better separation
FREQ_BANDS = {
    'sub_bass': (20, 60),
    'bass': (60, 250),
    'low_mid': (250, 500),
    'mid': (500, 2000),
    'high_mid': (2000, 4000),
    'high': (4000, 20000)
}

class EnhancedBeatDetector:
    def __init__(self):
        self.energy_history = deque(maxlen=43)
        self.beat_history = deque(maxlen=20)
        self.last_beat_time = 0
        self.beat_threshold = 1.5  # More sensitive threshold
        self.tempo = 120
        self.smoothed_energy = 0
        self.energy_smoothing = 0.3

    def detect_beat(self, data, current_time):
        # Enhanced energy calculation using RMS
        energy = np.sqrt(np.mean(np.square(data[:len(data)//4])))
        
        # Smooth the energy
        self.smoothed_energy = (self.smoothed_energy * (1 - self.energy_smoothing) + 
                              energy * self.energy_smoothing)
        
        self.energy_history.append(self.smoothed_energy)
        
        # Dynamic threshold based on recent history
        local_avg = np.mean(list(self.energy_history))
        local_std = np.std(list(self.energy_history))
        dynamic_threshold = max(local_avg + local_std * 0.8, 1e-6)  # Prevent zero threshold
        
        is_beat = self.smoothed_energy > dynamic_threshold
        min_time_between_beats = 60000 / max(self.tempo * 2, 1)  # Prevent division by zero
        
        if is_beat and (current_time - self.last_beat_time) > min_time_between_beats:
            self.last_beat_time = current_time
            self.beat_history.append(current_time)
            
            if len(self.beat_history) > 3:
                recent_intervals = np.diff(list(self.beat_history)[-4:])
                median_interval = np.median(recent_intervals)
                if median_interval > 0:  # Prevent division by zero
                    self.tempo = 60000 / median_interval
            
            energy_ratio = self.smoothed_energy / dynamic_threshold
            return True, min(max(energy_ratio, 0.1), 5.0)  # Clamp ratio to reasonable range
        
        energy_ratio = self.smoothed_energy / dynamic_threshold
        return False, min(max(energy_ratio, 0.1), 5.0)  # Clamp ratio to reasonable range

class EnhancedParticle:
    def __init__(self, x, y, color, velocity=1):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(2, 5)
        self.velocity = velocity * 0.7
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = 255
        self.decay_rate = random.uniform(2, 4)
        self.spin = random.uniform(-0.1, 0.1)
        self.pulse_phase = random.uniform(0, 2 * math.pi)

    def update(self, beat_intensity, delta_time):
        # Add subtle circular motion
        self.angle += self.spin * beat_intensity
        
        # Pulsing movement
        pulse = math.sin(self.pulse_phase + delta_time * 2)
        pulse_intensity = 0.3 * beat_intensity
        
        self.x += (math.cos(self.angle) * self.velocity * 
                  beat_intensity * (1 + pulse * pulse_intensity))
        self.y += (math.sin(self.angle) * self.velocity * 
                  beat_intensity * (1 + pulse * pulse_intensity))
        
        self.life -= self.decay_rate
        self.pulse_phase += 0.1
        
        return self.life > 0

    def draw(self, surface):
        alpha = int(self.life)
        color_with_alpha = (*self.color, min(alpha, 200))
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color_with_alpha, 
                         (self.size, self.size), self.size)
        surface.blit(surf, (int(self.x - self.size), 
                          int(self.y - self.size)))

class FrequencyAnalyzer:
    def __init__(self):
        self.prev_fft = None
        self.smoothing = FFT_SMOOTHING

    def analyze(self, audio_data):
        current_fft = np.abs(fft(audio_data)[:BUFFER_SIZE//2])
        
        # Normalize and apply smoothing
        if np.max(current_fft) > 0:
            current_fft = current_fft * 20 / np.max(current_fft)
        
        if self.prev_fft is None:
            self.prev_fft = current_fft
        else:
            current_fft = (self.prev_fft * self.smoothing + 
                         current_fft * (1 - self.smoothing))
            self.prev_fft = current_fft
        
        return np.clip(current_fft, 0, 1)

def get_frequency_band_amplitude(fft_data, band, sample_rate):
    start_freq, end_freq = FREQ_BANDS[band]
    start_idx = int(start_freq * len(fft_data) / (sample_rate/2))
    end_idx = int(end_freq * len(fft_data) / (sample_rate/2))
    return np.mean(fft_data[start_idx:end_idx])

def get_color_for_frequencies(freq_amplitudes, beat_intensity, time):
    # Weight the frequency bands
    weighted_amplitudes = {
        band: amp * (1.2 if band in ['bass', 'sub_bass'] else 1.0)
        for band, amp in freq_amplitudes.items()
    }
    
    max_band = max(weighted_amplitudes.items(), key=lambda x: x[1])[0]
    hue, sat, val = COLOR_SCHEME[max_band]
    
    # More dynamic color variation
    sat = min(0.9, sat + beat_intensity * 0.3)
    val = min(0.9, val + beat_intensity * 0.3)
    
    # Smooth color transitions
    hue = (hue + time / 25000) % 1.0
    
    rgb = colorsys.hsv_to_rgb(hue, sat, val)
    return tuple(int(x * 255) for x in rgb)

# Initialize audio stream
try:
    device_id = sd.default.device[0]
    stream = sd.InputStream(
        device=device_id,
        channels=1,
        samplerate=SAMPLE_RATE,
        blocksize=BUFFER_SIZE,
        callback=lambda indata, frames, time, status: setattr(stream, 'audio_data', indata[:, 0])
    )
    stream.audio_data = np.zeros(BUFFER_SIZE)
    stream.start()
except Exception as e:
    print(f"Error starting audio stream: {e}")
    pygame.quit()
    exit()

# Initialize components
particles = []
beat_detector = EnhancedBeatDetector()
freq_analyzer = FrequencyAnalyzer()
rotation = 0
pulse_size = 100

running = True
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
last_time = start_time

while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0
    last_time = current_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Process audio
    audio_data = stream.audio_data
    data_fft = freq_analyzer.analyze(audio_data)
    
    freq_amplitudes = {
        band: get_frequency_band_amplitude(data_fft, band, SAMPLE_RATE) 
        for band in FREQ_BANDS
    }
    
    is_beat, energy_ratio = beat_detector.detect_beat(data_fft, current_time)
    beat_intensity = 1.5 if is_beat else 1.0 + (energy_ratio - 1) * 0.3
    
    # Clear screen with fade effect
    fade_surf = pygame.Surface((WIDTH, HEIGHT))
    fade_surf.fill(BACKGROUND_COLOR)
    fade_surf.set_alpha(25)
    screen.blit(fade_surf, (0, 0))
    
    # Update rotation based on tempo and energy
    rotation += (beat_detector.tempo / 180.0) * (1 + energy_ratio * 0.2)
    
    # Draw visualization
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # Draw frequency circles
    for band, amplitude in freq_amplitudes.items():
        radius = 100 + list(FREQ_BANDS.keys()).index(band) * 50
        color = get_color_for_frequencies({band: amplitude}, beat_intensity, current_time)
        points = []
        num_points = 32  # Increased for smoother circles
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points + rotation / 30
            # Ensure amplitude and beat_intensity are within reasonable ranges
            safe_amplitude = min(max(amplitude, 0), 1)
            safe_beat_intensity = min(max(beat_intensity, 0.1), 5.0)
            r = radius * (1 + safe_amplitude * safe_beat_intensity * 0.7)
            x = center_x + math.cos(angle) * r
            y = center_y + math.sin(angle) * r
            # Ensure coordinates are valid before converting to int
            if not (math.isnan(x) or math.isnan(y)):
                points.append((int(x), int(y)))
            
            if is_beat and random.random() < 0.2:
                particles.append(EnhancedParticle(x, y, color, velocity=1.5+amplitude*4))
        
        # Draw smoother lines
        if len(points) > 1:
            pygame.draw.lines(screen, color, True, points, 2)
    
    # Update and draw particles
    particles = [p for p in particles if p.update(beat_intensity, delta_time)]
    for particle in particles[:150]:  # Increased particle limit
        particle.draw(screen)
    
    # Draw central pulse
    pulse_size = 90 * (1 + 0.4 * beat_intensity)
    pygame.draw.circle(screen, (60, 60, 70), (center_x, center_y), 
                      int(pulse_size), 2)
    
    pygame.display.flip()
    clock.tick(60)

# Cleanup
stream.stop()
stream.close()
pygame.quit()