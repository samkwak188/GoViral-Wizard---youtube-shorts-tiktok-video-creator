import os
import random
import subprocess
from pydub import AudioSegment
import requests
import time
from gtts import gTTS
import tkinter as tk
from tkinter import messagebox, colorchooser, ttk
import threading
from elevenlabs import ElevenLabs
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from config import ASSEMBLYAI_API_KEY, OUTPUT_DIRECTORY, CANVAS_BACKGROUND_IMAGE, GIF_PATH



# Function Definitions
def on_option_select():
    """Handles the display of the API key entry based on the selected voice option."""
    if voice_option.get() == "elevenlabs":
        api_key_label.pack()
        api_key_entry.pack()
    else:
        api_key_label.pack_forget()
        api_key_entry.pack_forget()
    check_create_button_state()

def choose_subtitle_color():
    """Opens a color chooser dialog to select the subtitle color."""
    color = colorchooser.askcolor()[1]
    if color:
        subtitle_color_var.set(color)
        update_preview()

def choose_stroke_color():
    """Opens a color chooser dialog to select the stroke color."""
    color = colorchooser.askcolor()[1]
    if color:
        stroke_color_var.set(color)
        update_preview()

def toggle_stroke_color_button():
    """Updates the preview and enables/disables the stroke color button based on the stroke option."""
    if stroke_var.get():
        stroke_color_button.config(state=tk.NORMAL)
    else:
        stroke_color_button.config(state=tk.DISABLED)
    update_preview()

def update_preview():
    """Updates the canvas to reflect the current subtitle customization settings."""
    selected_font = font_var.get()
    subtitle_color = subtitle_color_var.get()
    stroke_color = stroke_color_var.get()
    stroke_width = 2 if stroke_var.get() else 0
    

    canvas.delete("all")

    # Load and resize the image
    background_image = Image.open(CANVAS_BACKGROUND_IMAGE)  # Replace with your image path
    background_image = background_image.resize((300, 100), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)

    # Display the background image
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Draw stroke effect if enabled
    if stroke_width > 0:
        for x_offset in range(-stroke_width, stroke_width + 1):
            for y_offset in range(-stroke_width, stroke_width + 1):
                if x_offset != 0 or y_offset != 0:
                    canvas.create_text(150 + x_offset, 50 + y_offset, text="Subtitle Preview", font=(selected_font, 24),
                                       fill=stroke_color, anchor="center")

    # Draw main text
    canvas.create_text(150, 50, text="Subtitle Preview", font=(selected_font, 24),
                       fill=subtitle_color, anchor="center")

    # Ensure the image reference is kept
    canvas.background_photo = background_photo

def navigate_tabs(direction):
    current_tab = notebook.index(notebook.select())
    if direction == "next":
        notebook.select(current_tab + 1)
    elif direction == "previous":
        notebook.select(current_tab - 1)

def select_and_concatenate_videos(audio_duration):
    """Selects and concatenates video clips to match the audio duration using ffmpeg."""
    video_categories = {
        "Oddly satisfying video": os.path.join('videos', 'fg'),
        "Minecraft Parkour video": os.path.join('videos', 'mk'),
        "GTA gameplay": os.path.join('videos', 'gta'),
        "Subway Surfers gameplay": os.path.join('videos', 'sb')
    }

    selected_category = video_type_option.get()
    if selected_category == "Randomize":
        selected_category = random.choice(list(video_categories.keys()))

    video_directory = video_categories.get(selected_category)
    if not video_directory:
        raise Exception("Invalid video category selected")

    all_videos = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if f.endswith('.mp4')]
    selected_clips = []
    total_duration = 0

    while total_duration < audio_duration:
        available_videos = [video for video in all_videos if video not in selected_clips]
        if not available_videos:
            raise Exception("Not enough unique videos to cover the required duration")

        video_path = random.choice(available_videos)
        video_duration = get_video_duration(video_path)

        remaining_duration = audio_duration - total_duration
        if remaining_duration < video_duration:
            video_duration = remaining_duration

        selected_clips.append((video_path, video_duration))
        total_duration += video_duration

    # Adjust the last clip to match the exact audio duration
    if total_duration > audio_duration:
        last_clip_path, last_clip_duration = selected_clips[-1]
        selected_clips[-1] = (last_clip_path, last_clip_duration - (total_duration - audio_duration))

    # Create a temporary file list for ffmpeg
    with open("file_list.txt", "w") as f:
        for video_path, duration in selected_clips:
            f.write(f"file '{video_path}'\n")
            f.write(f"inpoint 0\n")
            f.write(f"outpoint {duration}\n")

    final_clip_path = "final_video.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt",
        "-vf", "scale=1080:1920", "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k", "-an", "-y", final_clip_path
    ], creationflags=subprocess.CREATE_NO_WINDOW)

    return final_clip_path

def convert_color_to_ffmpeg(color):
    """Convert #RRGGBB to &HBBGGRR& format for ASS."""
    return f"&H{color[5:7]}{color[3:5]}{color[1:3]}&"

def generate_text_clips(sentences, video_size):
    """Generates an ASS subtitle file for karaoke-style subtitles with word-by-word background highlighting."""
    subtitle_file = "subtitles.ass"
    with open(subtitle_file, "w") as f:
        # Write the ASS header
        f.write("[Script Info]\n")
        f.write("Title: Karaoke Example\n")
        f.write("ScriptType: v4.00+\n")
        f.write("Collisions: Normal\n")
        f.write("PlayDepth: 0\n\n")

        # Determine stroke width based on the stroke_var
        stroke_width = 10 if stroke_var.get() else 0

        # Define default style
        default_primary_color = convert_color_to_ffmpeg(subtitle_color_var.get())
        default_outline_color = convert_color_to_ffmpeg(stroke_color_var.get())
        default_fontsize = 15

        # Define highlighted style based on user selection
        highlighting_style = highlighting_style_var.get()

        if subtitle_display_style_var.get() == "Word by Word":
            default_fontsize = 20
        else:
            default_fontsize = 15

        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        
        # Default style
        f.write(( 
            f"Style: Default," 
            f"{font_var.get()}," 
            f"{default_fontsize}," 
            f"{default_primary_color},"  # PrimaryColour
            f"&H000000FF,"  # SecondaryColour
            f"{default_outline_color},"  # OutlineColour
            f"&H00000000,"  # BackColour
            f"-1,"          # Bold
            f"0,"           # Italic
            f"0,"           # Underline
            f"0,"           # StrikeOut
            f"100,"         # ScaleX
            f"100,"         # ScaleY
            f"0,"           # Spacing
            f"0,"           # Angle
            f"1,"           # BorderStyle
            f"{stroke_width},"  # Outline (stroke width)
            f"0,"           # Shadow depth removed
            f"2,"           # Alignment
            f"10,"          # MarginL
            f"10,"          # MarginR
            f"70,"          # MarginV
            f"1\n"
        ))

        f.write(( 
            f"Style: Highlighted," 
            f"{font_var.get()}," 
            f"15," 
            f"&H0000FFFF,"  # Highlight Color   
            f"&H00FFFF00,"  # SecondaryColour
            f"{default_outline_color},"  # OutlineColour for background box
            f"&H00000000,"  # BackColour 
            f"-1,"          # Bold  
            f"0,"           # Italic
            f"0,"           # Underline
            f"0,"           # StrikeOut
            f"100,"         # ScaleX
            f"100,"         # ScaleY
            f"0,"           # Spacing
            f"0,"           # Angle
            f"1,"           # BorderStyle for text box
            f"{stroke_width},"  # Outline (stroke width)
            f"0,"           # Shadow
            f"2,"           # Alignment
            f"10,"          # MarginL
            f"10,"          # MarginR
            f"70,"          # MarginV
            f"1\n\n"        # Encoding
        ))

        # HighlightedBackground style
        f.write(( 
            f"Style: HighlightedBackground," 
            f"{font_var.get()}," 
            f"15," 
            f"&H00000000,"  # Transparent PrimaryColour
            f"&H00FFFF00,"  # SecondaryColour
            f"&H0000FFFF,"  # Background box Color (OutlineColour)
            f"&H00000000,"  # BackColour (should be transparent)
            f"-1,"          # Bold  
            f"0,"           # Italic
            f"0,"           # Underline
            f"0,"           # StrikeOut
            f"100,"         # ScaleX
            f"100,"         # ScaleY
            f"0,"           # Spacing
            f"0,"           # Angle
            f"3,"           # BorderStyle for text box
            f"10,"  # Outline (stroke width)
            f"0,"           # Shadow (ensure this is 0 for no shadow)
            f"2,"           # Alignment
            f"10,"          # MarginL
            f"10,"          # MarginR
            f"70,"          # MarginV
            f"1\n\n"        # Encoding
        ))

        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

        # Write the dialogue with background effect
        for sentence in sentences:
            words = sentence['words']
            sentence_start_time = sentence['start'] / 1000
            sentence_end_time = sentence['end'] / 1000

            if subtitle_display_style_var.get() == "Word by Word":
                for word in words:
                    word_start_time = word['start'] / 1000
                    word_end_time = word['end'] / 1000

                    # Add popping effect using \t tag and center-center alignment with \an5
                    # Use \pos to position the text at the desired location
                    popping_effect = r"{\an5\t(0,70,\fscx120\fscy120)\t(70,120,\fscx100\fscy100)}"
                    f.write(f"Dialogue: 0,{format_time(word_start_time)},{format_time(word_end_time)},Default,,0,0,0,,{popping_effect}{word['text']}\n")

            else:  # Sentence by Sentence
                if highlighting_style == "No Highlighting":
                    f.write(f"Dialogue: 0,{format_time(sentence_start_time)},{format_time(sentence_end_time)},Default,,0,0,0,,{sentence['text']}\n")

                elif highlighting_style == "Color Highlight":
                    f.write(f"Dialogue: 0,{format_time(sentence_start_time)},{format_time(sentence_end_time)},Default,,0,0,0,,{sentence['text']}\n")

                    for i, word in enumerate(words):
                        word_start_time = word['start'] / 1000
                        word_end_time = word['end'] / 1000

                        start_ass = format_time(word_start_time)
                        end_ass = format_time(word_end_time)

                        highlighted_text = ' '.join(
                            f"{{\\rHighlighted}}{w['text']}" if j == i else f"{{\\rDefault}}{w['text']}" for j, w in enumerate(words)
                        )

                        f.write(f"Dialogue: 1,{start_ass},{end_ass},Highlighted,,0,0,0,,{highlighted_text}\n")

                elif highlighting_style == "Boxed Highlighter":
                    f.write(f"Dialogue: 1,{format_time(sentence_start_time)},{format_time(sentence_end_time)},Default,,0,0,0,,{sentence['text']}\n")
                    
                    for i, word in enumerate(words):
                        word_start_time = word['start'] / 1000
                        word_end_time = word['end'] / 1000

                        start_ass = format_time(word_start_time)
                        end_ass = format_time(word_end_time)

                        # Add fade effect to highlighted text
                        fade_duration = 50  # Adjust this value as needed
                        highlighted_text = ' '.join(
                            f"{{\\rHighlightedBackground\\fad({fade_duration},{fade_duration})}}{w['text']}" if j == i else f"{{\\rDefault}}{w['text']}" for j, w in enumerate(words)
                        )

                        f.write(f"Dialogue: 0,{start_ass},{end_ass},HighlightedBackground,,0,0,0,,{highlighted_text}\n")

    return subtitle_file

def format_time(seconds):
    """Formats time in seconds to ASS time format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 100)
    return f"{hours:01}:{minutes:02}:{int(seconds):02}.{milliseconds:02}"

def cleanup_temp_files():
    """Deletes temporary files created during video compilation."""
    temp_files = ["audio_elevenlabs.mp3", "audio_gtts.mp3", "file_list.txt", "subtitles.ass", "combined_audio.mp3","final_video.mp4"]
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def select_random_song():
    """Selects a random song from the Songs directory."""
    songs_directory = os.path.join(os.path.dirname(__file__), 'Songs')
    all_songs = [os.path.join(songs_directory, f) for f in os.listdir(songs_directory) if f.endswith('.mp3')]
    if not all_songs:
        raise Exception("No songs available in the Songs directory")
    return random.choice(all_songs)

def create_video_with_voiceover_and_subtitles(audio_file_path):
    update_progress(10, "Uploading audio to AssemblyAI...")
    upload_url = upload_audio_to_assemblyai(audio_file_path)
    
    update_progress(30, "Transcribing audio...")
    transcription_id = transcribe_audio(upload_url)
    
    update_progress(50, "Fetching transcription results...")
    sentences = get_transcription_result(transcription_id)
    
    update_progress(70, "Selecting and concatenating videos...")
    audio_duration_seconds = len(AudioSegment.from_file(audio_file_path)) / 1000
    video_clip_path = select_and_concatenate_videos(audio_duration_seconds)
    
    if background_song_var.get():
        update_progress(80, "Selecting background music...")
        song_path = select_random_song()
        song = AudioSegment.from_file(song_path)
        song = song - 7  # Reduce volume by 5dB (slightly higher than before)

        # Trim or loop the song to match the audio duration
        song = song[:audio_duration_seconds * 1000]  # Trim to match audio duration

        # Combine voiceover and song
        voiceover = AudioSegment.from_file(audio_file_path)
        combined_audio = voiceover.overlay(song)
    else:
        combined_audio = AudioSegment.from_file(audio_file_path)

    # Save the combined audio
    combined_audio_path = "combined_audio.mp3"
    combined_audio.export(combined_audio_path, format="mp3")
    
    update_progress(90, "Generating subtitles and finalizing video...")
    subtitle_file = generate_text_clips(sentences, (1080, 1920))
    
    # Combine video and audio using ffmpeg
    output_video_number = get_next_video_number()
    output_video_path = os.path.join(OUTPUT_DIRECTORY, f"output_video_{output_video_number}.mp4")
    subprocess.run([
        "ffmpeg", "-i", video_clip_path, "-i", combined_audio_path, "-map", "0:v", "-map", "1:a",
        "-vf", f"subtitles={subtitle_file}",
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-shortest", "-y", output_video_path
    ], creationflags=subprocess.CREATE_NO_WINDOW)
    
    update_progress(100, "Video compilation complete!")
    stop_progress()  # Stop the progress bar and GIF animation
    show_final_message(output_video_number)  # Show the final message with the video number
    cleanup_temp_files()  # Clean up temporary files
    root.after(0, lambda: create_button.config(state=tk.NORMAL))

def get_video_duration(video_path):
    """Returns the duration of a video file in seconds using ffmpeg."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def get_next_video_number():
    """Determine the next available video number."""
    existing_numbers = [
        int(f.split('_')[-1].split('.')[0]) 
        for f in os.listdir(OUTPUT_DIRECTORY) 
        if f.startswith('output_video_') and f.endswith('.mp4')
    ]
    if existing_numbers:
        return max(existing_numbers) + 1
    else:
        return 1

def get_audio_duration(audio_file_path):
    """Returns the duration of the audio file in seconds."""
    audio = AudioSegment.from_file(audio_file_path)
    return len(audio) / 1000  # Convert milliseconds to seconds

# Function to generate voice with ElevenLabs
def generate_voice_with_elevenlabs(script, api_key):
    client = ElevenLabs(api_key=api_key)
    voice_id = "pNInz6obpgDQGcFmaJgB"  # Replace with the desired voice ID
    voice_settings = {
        "stability": 0.5,
        "similarity_boost": 0.75,
    }
   
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id='eleven_multilingual_v2',
        text=script,
        voice_settings=voice_settings
    )
   
    audio_file_path = "audio_elevenlabs.mp3"
    with open(audio_file_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)
   
    return audio_file_path


# Function to generate voice with gTTS
def generate_voice_with_gtts(script):
    tts = gTTS(text=script, lang='en', slow=False)
    audio_file_path = "audio_gtts.mp3"
    tts.save(audio_file_path)
    return audio_file_path


# Function to convert text to speech
def text_to_speech(script, elevenlabs_api_key=None):
    if elevenlabs_api_key:
        audio_file = generate_voice_with_elevenlabs(script, elevenlabs_api_key)
    else:
        audio_file = generate_voice_with_gtts(script)
   
    audio = AudioSegment.from_file(audio_file)
    return audio_file


# Function to upload audio to AssemblyAI
def upload_audio_to_assemblyai(audio_file):
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    with open(audio_file, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': f})
    response.raise_for_status()
    return response.json()['upload_url']


# Function to transcribe audio
def transcribe_audio(upload_url):
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json'
    }
    json = {
        'audio_url': upload_url,
        'auto_chapters': False,
        'speaker_labels': False,
        'punctuate': True
    }
    response = requests.post('https://api.assemblyai.com/v2/transcript', headers=headers, json=json)
    response.raise_for_status()
    return response.json()['id']


# Function to get transcription result
def get_transcription_result(transcription_id):
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    while True:
        response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcription_id}', headers=headers)
        response.raise_for_status()
        result = response.json()
        if result['status'] == 'completed':
            sentences = []
            current_sentence = {'start': None, 'end': None, 'text': '', 'words': []}
            for word in result['words']:
                if current_sentence['start'] is None:
                    current_sentence['start'] = word['start']
                current_sentence['end'] = word['end']
                current_sentence['text'] += word['text'] + ' '
                current_sentence['words'].append({'text': word['text'], 'start': word['start'], 'end': word['end']})
                
                if word['text'].endswith(('.', '!', '?', ',','and',"for",'that','to')):
                    sentences.append(current_sentence)
                    current_sentence = {'start': None, 'end': None, 'text': '', 'words': []}
            
            # Add any remaining sentence
            if current_sentence['text'].strip():
                sentences.append(current_sentence)
            
            return sentences
        elif result['status'] == 'failed':
            raise Exception("Transcription failed")
        time.sleep(5)


# Function to handle video creation on button click
def on_create():
    script = script_text.get("1.0", tk.END).strip()
    
    # Replace line breaks with spaces to avoid terminal errors
    script = script.replace("\n", " ")

    selected_option = voice_option.get()

    if selected_option == "gtts":
        elevenlabs_api_key = None
    elif selected_option == "elevenlabs":
        elevenlabs_api_key = api_key_entry.get().strip()
        if not elevenlabs_api_key:
            messagebox.showwarning("Input Error", "Please enter your ElevenLabs API key.")
            return

    # Disable the create button and start the progress animation
    create_button.config(state=tk.DISABLED)
    start_progress()

    # Run the entire process in a separate thread
    threading.Thread(target=process_video_creation, args=(script, elevenlabs_api_key)).start()

def process_video_creation(script, elevenlabs_api_key):
    # Generate the audio file and get the path
    audio_file_path = text_to_speech(script, elevenlabs_api_key)

    # Continue with video creation
    create_video_with_voiceover_and_subtitles(audio_file_path)

def check_create_button_state():
    """Enable the create button only if a script is entered and a voice option is selected."""
    script_entered = bool(script_text.get("1.0", tk.END).strip())
    voice_selected = voice_option.get() is not None
    if script_entered and voice_selected:
        create_button.config(state=tk.NORMAL)
    else:
        create_button.config(state=tk.DISABLED)

# GUI Setup
root = ThemedTk(theme="clearlooks")  # You can change "clam" to any available theme
root.title("Go-Viral Wizard")
root.geometry("800x600")

# Disable window resizing
root.resizable(False, False)

# Create a notebook for tabbed navigation
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Create frames for each tab
script_tab = tk.Frame(notebook)
subtitle_tab = tk.Frame(notebook)
options_tab = tk.Frame(notebook)

# Add tabs to the notebook
notebook.add(script_tab, text='Script')
notebook.add(subtitle_tab, text='Subtitle Customization')
notebook.add(options_tab, text='Video Settings')

# Script Prompt Tab
script_label = tk.Label(script_tab, text="Enter your script:")
script_label.pack(pady=10)
script_text = tk.Text(script_tab, height=15, width=60)
script_text.pack(pady=10)

# Bind the script text widget to check the button state on any input
script_text.bind("<KeyRelease>", lambda event: check_create_button_state())

# Voice option selection
script_label = tk.Label(script_tab, text="Choose your voice-over option:")
script_label.pack(pady=10)
voice_option = tk.StringVar(value=None)
gtts_radio = tk.Radiobutton(script_tab, text="gTTS (Free)", variable=voice_option, value="gtts", command=on_option_select)
gtts_radio.pack(anchor='center')
elevenlabs_radio = tk.Radiobutton(script_tab, text="ElevenLabs", variable=voice_option, value="elevenlabs", command=on_option_select)
elevenlabs_radio.pack(anchor='center')

# Ensure no selection is made initially
voice_option.set(None)

# API Key Entry for ElevenLabs
api_key_label = tk.Label(script_tab, text="Enter ElevenLabs API Key:")
api_key_entry = tk.Entry(script_tab, width=50)

# Subtitle Customization Tab
canvas = tk.Canvas(subtitle_tab, width=300, height=100, bg="white")
canvas.pack(pady=20)

# Create a frame for the two-column layout
options_frame = tk.Frame(subtitle_tab)
options_frame.pack(pady=20)

# Set default colors
subtitle_color_var = tk.StringVar(value="#FFFFFF")  # White
stroke_color_var = tk.StringVar(value="#000000")    # Black
font_var = tk.StringVar(value="Arial")
stroke_var = tk.BooleanVar(value=True)

# Use font names instead of file paths
font_options = {
    "Arial": "Arial",
    "BadaBoom BB": "BadaBoom BB",
    "NanumGothic": "NanumGothic",
    "Montserrat-Bold": "Montserrat-Bold"
}

# Left Column
font_label = tk.Label(options_frame, text="Select Font:")
font_label.grid(row=0, column=0, pady=5, padx=20, sticky='n')
font_combobox = ttk.Combobox(options_frame, textvariable=font_var, values=list(font_options.keys()), state='readonly')
font_combobox.grid(row=1, column=0, pady=5, padx=20, sticky='n')
font_combobox.current(0)
font_combobox.bind("<<ComboboxSelected>>", lambda event: update_preview())

subtitle_color_button = tk.Button(options_frame, text="Choose Subtitle Color", command=choose_subtitle_color)
subtitle_color_button.grid(row=2, column=0, pady=5, padx=20, sticky='n')

stroke_checkbox = tk.Checkbutton(options_frame, text="Enable Stroke Width (fixed to 10)", variable=stroke_var, command=lambda: [toggle_stroke_color_button()])
stroke_checkbox.grid(row=3, column=0, pady=5, padx=20, sticky='n')

stroke_color_button = tk.Button(options_frame, text="Choose Stroke Color", command=choose_stroke_color, state=tk.NORMAL)
stroke_color_button.grid(row=4, column=0, pady=5, padx=20, sticky='n')

# Right Column
subtitle_display_style_label = tk.Label(options_frame, text="Select Subtitle Display Style:")
subtitle_display_style_label.grid(row=0, column=1, pady=5, padx=40, sticky='n')

subtitle_display_style_var = tk.StringVar(value="Sentence by Sentence")
subtitle_display_style_options = [
    "Word by Word",
    "Sentence by Sentence"
]

subtitle_display_style_dropdown = ttk.Combobox(options_frame, textvariable=subtitle_display_style_var, values=subtitle_display_style_options, state='readonly')
subtitle_display_style_dropdown.grid(row=1, column=1, pady=5, padx=40, sticky='n')
subtitle_display_style_dropdown.current(1)  # Default to "Sentence by Sentence"
subtitle_display_style_dropdown.bind("<<ComboboxSelected>>", lambda event: toggle_highlighting_option())

highlighting_style_label = tk.Label(options_frame, text="Select Highlighting Style:")
highlighting_style_label.grid(row=2, column=1, pady=5, padx=40, sticky='n')

highlighting_style_var = tk.StringVar(value="No Highlighting")
highlighting_style_options = [
    "No Highlighting",
    "Color Highlight",
    "Boxed Highlighter"
]

highlighting_style_dropdown = ttk.Combobox(options_frame, textvariable=highlighting_style_var, values=highlighting_style_options, state='readonly')
highlighting_style_dropdown.grid(row=3, column=1, pady=5, padx=40, sticky='n')
highlighting_style_dropdown.current(0)

def toggle_highlighting_option():
    """Enable or disable the highlighting style option based on the subtitle display style."""
    if subtitle_display_style_var.get() == "Sentence by Sentence":
        highlighting_style_dropdown.config(state='readonly')
    else:
        highlighting_style_dropdown.config(state='disabled')

# Initial call to set the correct state
toggle_stroke_color_button()

toggle_highlighting_option()

# Other Options Tab
duration_option = tk.StringVar(value="max_1minute")

duration_label = tk.Label(options_tab, text="Select Video Duration:")
duration_label.pack(pady=10)
duration_options = [
    "I want my videos for youtube shorts (Max 1 minute)",
    "I want my videos for tiktok (Any duration)"
]
duration_dropdown = ttk.Combobox(options_tab, textvariable=duration_option, values=duration_options, state='readonly', width=50)
duration_dropdown.pack(pady=10)
duration_dropdown.current(0)

video_type_label = tk.Label(options_tab, text="Select Background Video Type:")
video_type_label.pack(pady=10)
video_type_option = tk.StringVar(value="Oddly satisfying video")
video_type_options = [
    "Oddly satisfying video",
    "Minecraft Parkour video",
    "GTA gameplay",
    "Subway Surfers gameplay",
    "Randomize"
]
video_type_dropdown = ttk.Combobox(options_tab, textvariable=video_type_option, values=video_type_options, state='readonly')
video_type_dropdown.pack(pady=10)
video_type_dropdown.current(0)

# Add a variable to track the background song option
background_song_var = tk.BooleanVar(value=True)

# Add the option to the third tab
background_song_checkbox = tk.Checkbutton(options_tab, text="Background Song", variable=background_song_var)
background_song_checkbox.pack(pady=10)

create_button = tk.Button(options_tab, text="Create Video", state=tk.DISABLED, command=on_create)
create_button.pack(pady=20)

# Load the GIF
gif_path = GIF_PATH
gif_image = Image.open(gif_path)

# Define the bounding box for cropping (adjust these values as needed)
crop_box = (10, 30, gif_image.width - 15, gif_image.height - 15)

# Create a list to store the frames
frames = []

# Load and crop each frame into the list
try:
    while True:
        frame = gif_image.copy().crop(crop_box).convert('RGBA')
        frames.append(ImageTk.PhotoImage(frame))
        gif_image.seek(gif_image.tell() + 1)
except EOFError:
    pass  # End of sequence

gif_image.close()

# Create a label to display the GIF
loading_label = tk.Label(options_tab)
loading_label.pack(pady=10)  # Position it below the 'Create Video' button

# Function to animate the GIF
def animate_gif(frame_index=0):
    frame = frames[frame_index]
    loading_label.config(image=frame)
    root.after(100, animate_gif, (frame_index + 1) % len(frames))

# Function to start the GIF animation
def start_progress():
    loading_label.place(relx=0.5, rely=0.7, anchor='center')  # Move the GIF higher
    progress_bar.place(relx=0.5, rely=0.9, anchor='center')   # Move the progress bar higher
    progress_label.place(relx=0.5, rely=0.95, anchor='center') # Move the label higher
    loading_label.lift()
    animate_gif()

# Function to stop the GIF animation
def stop_progress():
    loading_label.place_forget()
    progress_bar.place_forget()
    progress_label.place_forget()

# Navigation Buttons
nav_frame = tk.Frame(root)
nav_frame.pack(side='bottom', pady=10)

prev_button = tk.Button(nav_frame, text="Previous", command=lambda: navigate_tabs("previous"))
prev_button.pack(side='left', padx=5)

next_button = tk.Button(nav_frame, text="Next", command=lambda: navigate_tabs("next"))
next_button.pack(side='left', padx=5)

# Initial preview update
update_preview()

def update_navigation_buttons():
    current_tab = notebook.index(notebook.select())
    total_tabs = notebook.index("end")

    if current_tab == 0:
        prev_button.config(state=tk.DISABLED)
    else:
        prev_button.config(state=tk.NORMAL)

    if current_tab == total_tabs - 1:
        next_button.config(state=tk.DISABLED)
    else:
        next_button.config(state=tk.NORMAL)

# Call update_navigation_buttons initially to set the correct state
update_navigation_buttons()

# Bind the tab change event to update the buttons
notebook.bind("<<NotebookTabChanged>>", lambda event: update_navigation_buttons())

# Create a progress bar and a label for the explanation message
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(options_tab, variable=progress_var, maximum=100, length=200)  # Set a length for visibility
progress_label = tk.Label(options_tab, text="")
final_message_label = tk.Label(options_tab, text="", font=("Arial", 12, "bold"))

# Function to update the progress bar and message
def update_progress(value, message):
    progress_var.set(value)
    progress_label.config(text=message)
    root.update_idletasks()

# Function to show the final message as a messagebox
def show_final_message(video_number):
    messagebox.showinfo("Video Compilation", f"Your video is here!\nYour video number is: {video_number}")

root.mainloop()

