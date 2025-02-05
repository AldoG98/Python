import pyttsx3
import os

def create_voiceover(text, filename, voice_speed=150, voice_id=None):
    """
    Create a voiceover from text and save it as an audio file
    
    Args:
        text (str): The text to convert to speech
        filename (str): Output filename (will save as .mp3)
        voice_speed (int): Speech rate (default 150)
        voice_id (str): Optional specific voice ID to use
    """
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    
    # Get available voices
    voices = engine.getProperty('voices')
    
    # Set properties
    engine.setProperty('rate', voice_speed)  # Speed of speech
    
    # Set voice (default to first female voice if available)
    if voice_id:
        engine.setProperty('voice', voice_id)
    else:
        # Try to find a female voice
        female_voice = None
        for voice in voices:
            if 'female' in voice.name.lower():
                female_voice = voice.id
                break
        
        if female_voice:
            engine.setProperty('voice', female_voice)
    
    # Remove .mp3 extension if present in filename
    filename = filename.replace('.mp3', '')
    
    # Save to file
    engine.save_to_file(text, f"{filename}.mp3")
    engine.runAndWait()

def list_available_voices():
    """Print all available voices"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print("\nAvailable voices:")
    for idx, voice in enumerate(voices):
        print(f"{idx + 1}. ID: {voice.id}")
        print(f"   Name: {voice.name}")
        print(f"   Languages: {voice.languages}")
        print("---")

def main():
    print("Text-to-Speech Voiceover Generator")
    print("=================================")
    
    while True:
        print("\nOptions:")
        print("1. Create new voiceover")
        print("2. List available voices")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            text = input("\nEnter the text for the voiceover: ")
            filename = input("Enter output filename: ")
            speed = input("Enter speech rate (150 is default, higher = faster): ")
            
            try:
                speed = int(speed) if speed.strip() else 150
                create_voiceover(text, filename, speed)
                print(f"\nVoiceover saved as {filename}.mp3")
            except Exception as e:
                print(f"Error creating voiceover: {e}")
                
        elif choice == '2':
            list_available_voices()
            
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()