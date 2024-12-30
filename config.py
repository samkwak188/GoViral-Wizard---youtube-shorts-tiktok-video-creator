import os
import threading

# Constants and Configurations

ASSEMBLYAI_API_KEY = 'YOUR_ASSEMBLYAI_API_KEY'
OUTPUT_DIRECTORY = os.path.join('output')
CANVAS_BACKGROUND_IMAGE = os.path.join('Images', 'preview back.jpg')
GIF_PATH = os.path.join('Images', 'loading2.gif') 

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)

video_creation_lock = threading.Lock()