import pretty_midi
import random
import os
import numpy as np
from typing import List, Tuple

class SongSection:
    def __init__(self, name: str, bars: int, intensity: float, groove: float = 0.5):
        self.name = name
        self.bars = bars
        self.intensity = intensity  # 0 to 1
        self.groove = groove  # 0 to 1, affects swing and rhythm complexity

class MidiDrumKit:
    KICK = 36
    SNARE = 38
    CLOSED_HAT = 42
    OPEN_HAT = 46
    CLAP = 39
    RIDE = 51
    CRASH = 49
    SHAKER = 70
    PERCUSSION = 60

def create_progressive_bassline(instrument, start_time: float, duration: float, 
                              intensity: float, key: int = 36):
    """
    Creates a classic progressive house bassline with occasional slides
    and rhythmic variations
    """
    note_duration = 0.25  # 16th notes
    slide_chance = 0.1 * intensity
    
    # Progressive house often uses simple but effective basslines
    patterns = [
        [0, None, None, 0, 0, None, None, 0, 0, None, None, 0, 0, None, 0, 0],
        [0, None, None, 0, None, None, 0, None, 0, None, None, 0, None, None, 0, None],
        [0, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None]
    ]
    
    pattern = random.choice(patterns)
    
    for bar in range(int(duration / 4)):
        for i in range(16):  # 16 steps per bar
            if pattern[i] is not None and random.random() < intensity:
                current_time = start_time + (bar * 4) + (i * note_duration)
                note_pitch = key + pattern[i]
                velocity = int(100 + (20 * intensity * random.random()))
                
                # Add occasional pitch slides
                if random.random() < slide_chance:
                    # Create pitch bend for slide effect
                    pb_start = int(8192 * 1.5)  # Start slightly higher
                    pb_end = 8192  # Return to center
                    pb_steps = 8
                    for step in range(pb_steps):
                        time = current_time + (step * note_duration / pb_steps)
                        value = int(np.interp(step, [0, pb_steps-1], [pb_start, pb_end]))
                        pb = pretty_midi.PitchBend(value, time)
                        instrument.pitch_bends.append(pb)
                
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=note_pitch,
                    start=current_time,
                    end=current_time + note_duration * 0.95
                )
                instrument.notes.append(note)

def create_prog_house_chords(instrument, start_time: float, duration: float, 
                           intensity: float, key: int = 60):
    """
    Creates atmospheric prog house chord progressions with variations
    """
    # Common prog house chord progressions
    progressions = [
        [[0, 4, 7, 11], [5, 9, 12, 16], [7, 11, 14, 17], [3, 7, 10, 14]],  # Cmaj7 - Fmaj7 - G7 - Dm7
        [[0, 4, 7, 11], [7, 11, 14, 17], [5, 9, 12, 16], [3, 7, 10, 14]],  # Cmaj7 - G7 - Fmaj7 - Dm7
        [[0, 4, 7, 11], [8, 12, 15, 19], [3, 7, 10, 14], [5, 9, 12, 16]]   # Cmaj7 - Abmaj7 - Dm7 - Fmaj7
    ]
    
    progression = random.choice(progressions)
    chord_duration = 4  # 4 beats per chord
    
    for bar in range(int(duration / 4)):
        chord = progression[bar % len(progression)]
        current_time = start_time + (bar * 4)
        
        # Add rhythmic variations based on intensity
        divisions = [1, 0.5, 0.25] if intensity > 0.7 else [1]
        for division in divisions:
            if random.random() < intensity:
                for step in range(int(4 / division)):
                    step_time = current_time + (step * division)
                    
                    # Add slight timing variations for humanization
                    for note_offset in chord:
                        note_start = step_time + random.uniform(-0.01, 0.01)
                        velocity = int(60 + (40 * intensity * random.random()))
                        
                        note = pretty_midi.Note(
                            velocity=velocity,
                            pitch=key + note_offset,
                            start=note_start,
                            end=note_start + (division * 0.95)
                        )
                        instrument.notes.append(note)

def create_prog_house_lead(instrument, start_time: float, duration: float, 
                         intensity: float, key: int = 72):
    """
    Creates melodic progressive house lead patterns
    """
    # Progressive house scale (minor scale typically)
    scale = [0, 2, 3, 5, 7, 8, 10, 12]
    pattern_length = 8
    note_duration = 0.25  # 16th notes
    
    for bar in range(int(duration / 4)):
        if random.random() < intensity:
            pattern = []
            for _ in range(pattern_length):
                if random.random() < 0.7:
                    pattern.append(random.choice(scale))
                else:
                    pattern.append(None)
            
            for i, note_offset in enumerate(pattern):
                if note_offset is not None:
                    current_time = start_time + (bar * 4) + (i * note_duration)
                    velocity = int(70 + (30 * intensity * random.random()))
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=key + note_offset,
                        start=current_time,
                        end=current_time + note_duration * 0.9
                    )
                    instrument.notes.append(note)

def create_prog_house_drums(instrument, start_time: float, duration: float, 
                          intensity: float, groove: float):
    """
    Creates progressive house drum patterns with dynamic groove
    """
    for bar in range(int(duration / 4)):
        current_bar = start_time + (bar * 4)
        
        # Kick pattern (four-on-the-floor with occasional variations)
        for beat in range(4):
            if random.random() < intensity:
                note = pretty_midi.Note(
                    velocity=int(110 + (10 * random.random())),
                    pitch=MidiDrumKit.KICK,
                    start=current_bar + beat + random.uniform(-0.01, 0.01),
                    end=current_bar + beat + 0.1
                )
                instrument.notes.append(note)
        
        # Hi-hats with groove
        for sixteenth in range(16):
            if random.random() < intensity * 0.9:
                # Add swing based on groove parameter
                swing_offset = 0
                if sixteenth % 2 == 1:  # Off-beats
                    swing_offset = groove * 0.08
                
                note = pretty_midi.Note(
                    velocity=int(70 + (40 * random.random())),
                    pitch=MidiDrumKit.CLOSED_HAT,
                    start=current_bar + (sixteenth * 0.25) + swing_offset,
                    end=current_bar + (sixteenth * 0.25) + 0.1 + swing_offset
                )
                instrument.notes.append(note)
        
        # Clap/Snare on 2 and 4
        for beat in [1, 3]:
            if random.random() < intensity * 0.95:
                note = pretty_midi.Note(
                    velocity=int(90 + (20 * random.random())),
                    pitch=MidiDrumKit.CLAP,
                    start=current_bar + beat,
                    end=current_bar + beat + 0.15
                )
                instrument.notes.append(note)
        
        # Add percussion layers based on intensity
        if intensity > 0.6:
            for eighth in range(8):
                if random.random() < intensity * 0.7:
                    note = pretty_midi.Note(
                        velocity=int(60 + (30 * random.random())),
                        pitch=MidiDrumKit.PERCUSSION,
                        start=current_bar + (eighth * 0.5),
                        end=current_bar + (eighth * 0.5) + 0.1
                    )
                    instrument.notes.append(note)

def add_prog_house_automation(instrument, start_time: float, duration: float, 
                            automation_type: str = 'filter', intensity: float = 1.0):
    """
    Adds various automation effects common in progressive house
    """
    steps = int(duration * 16)  # 16 steps per beat for smooth automation
    
    if automation_type == 'filter':
        cc_number = 74  # Filter cutoff
        
        # Create filter envelope
        for i in range(steps):
            time = start_time + (i * duration / steps)
            # Create rhythmic filter movement
            value = int(np.interp(i % 64, 
                                [0, 16, 32, 48, 63],
                                [40, 127, 40, 127, 40]) * intensity)
            cc = pretty_midi.ControlChange(number=cc_number, value=value, time=time)
            instrument.control_changes.append(cc)
            
    elif automation_type == 'sidechain':
        cc_number = 7  # Volume
        
        # Create pumping sidechain effect
        for i in range(steps):
            time = start_time + (i * duration / steps)
            # Create characteristic progressive house sidechain curve
            value = int(np.interp(i % 16,
                                [0, 1, 4, 15],
                                [127 - (90 * intensity), 
                                 127 - (60 * intensity),
                                 127,
                                 127]))
            cc = pretty_midi.ControlChange(number=cc_number, value=value, time=time)
            instrument.control_changes.append(cc)

def create_prog_house_structure():
    """
    Creates a typical progressive house arrangement
    """
    return [
        SongSection("Intro", 32, 0.3, 0.3),
        SongSection("Build-up 1", 16, 0.5, 0.4),
        SongSection("Breakdown", 16, 0.2, 0.3),
        SongSection("Build-up 2", 16, 0.7, 0.6),
        SongSection("Main Theme", 32, 1.0, 0.7),
        SongSection("Bridge", 16, 0.4, 0.5),
        SongSection("Climax", 32, 1.0, 0.8),
        SongSection("Outro", 16, 0.3, 0.4)
    ]

def create_progressive_house():
    """
    Generates a complete progressive house track
    """
    midi = pretty_midi.PrettyMIDI(initial_tempo=128)
    
    # Create instruments with appropriate MIDI programs
    bass = pretty_midi.Instrument(program=38)      # Synth Bass
    chords = pretty_midi.Instrument(program=81)    # Pad
    lead = pretty_midi.Instrument(program=80)      # Square Lead
    drums = pretty_midi.Instrument(program=0, is_drum=True)
    
    song_structure = create_prog_house_structure()
    current_time = 0
    
    for section in song_structure:
        print(f"Generating {section.name}...")
        duration = section.bars * 4
        
        # Add musical elements
        create_progressive_bassline(bass, current_time, duration, section.intensity)
        create_prog_house_chords(chords, current_time, duration, section.intensity)
        create_prog_house_lead(lead, current_time, duration, section.intensity)
        create_prog_house_drums(drums, current_time, duration, section.intensity, 
                              section.groove)
        
        # Add automation
        if "Build-up" in section.name or section.name in ["Climax", "Main Theme"]:
            add_prog_house_automation(lead, current_time, duration, 'filter', 
                                   section.intensity)
        
        # Add sidechain to appropriate instruments
        add_prog_house_automation(chords, current_time, duration, 'sidechain', 
                                section.intensity)
        add_prog_house_automation(lead, current_time, duration, 'sidechain', 
                                section.intensity * 0.7)
        
        current_time += duration
    
    # Add all instruments to the MIDI file
    midi.instruments.extend([bass, chords, lead, drums])
    
    # Save the MIDI file
    output_directory = os.path.join(os.path.expanduser("~"), "Desktop", "Progressive_House_MIDI")
    os.makedirs(output_directory, exist_ok=True)
    
    midi_file_path = os.path.join(output_directory, "progressive_house_track.mid")
    midi.write(midi_file_path)
    print(f"Progressive house track saved to: {midi_file_path}")

if __name__ == "__main__":
    create_progressive_house()