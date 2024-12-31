# GOViral Wizard - Tiktok & Youtube Shorts Video Creator

This is a video maker tool that can create videos with customizable subtitles and various sample background videos.

## Project Inspiration

I'm sure you've seen those videos on TikTok or YouTube Shorts where an AI-generated voiceover is paired with synchronized subtitles and random background clips, like Minecraft gameplay or oddly satisfying videos. The idea for this project came to me when I decided to create an all-in-one tool that allows users to make TikTok-style videos with just a few clicks. I thought it would be a great opportunity to practice coding while kickstarting my own TikTok account.

## Key Features

### AssemblyAI Integration
The key driving factor of this project is [AssemblyAI](https://www.assemblyai.com/), a speech-to-text API that can convert audio to text with precise timestamps. The API provides 5000 free credits, which is more than enough for this project. 

To use AssemblyAI:
- Sign up for a free account [here](https://www.assemblyai.com/).
- Add your API key to the `config.py` file.

### ElevenLabs Voiceover Option
- Includes an option to use the [ElevenLabs API](https://elevenlabs.io/) for voiceovers to give more life to the video.
- Alternatively, you can use `gtts` (Google Text-to-Speech) as a free option.

### GUI with Tkinter
- A user-friendly GUI built with Tkinter allows you to customize your video easily.

## How to Use

1. **Run the Code**
   - Run the main script to open an 800 x 600 window with three tabs: `Script`, `Subtitle Customization`, and `Other Options`.

2. **Script Tab**
   - Write your script.
   - Choose a voice-over option: `gtts` (free) or `ElevenLabs`.
     - If `ElevenLabs` is chosen, you will be prompted to enter your API key.

3. **Subtitle Customization Tab**
   - Customize subtitle color, stroke color, display style, and highlighting style.
   - Choose from 5 font options.

4. **Other Options Tab**
   - Select video duration:
     - TikTok (15-60 seconds).
     - YouTube Shorts (up to 1 minute).
   - Choose the type of background video from 5 categories.
   - Add background music:
     - 3 songs are available in the `Songs` folder, with one selected randomly.

5. **Create Video**
   - After setting all options, click the `Create Video` button.
   - The video will be created in the `output` folder.
   - A loading GIF and progress bar are displayed during video creation.

## Setup Instructions

1. **Download Resources**
   - Download the sample `videos` and `Songs` folders [here](https://drive.google.com/drive/folders/1rCnLkZHQpSGqy9oPb8BobFRLSiPBlBAK?usp=sharing).
   - Place them in the same directory as `main.py` and `config.py`.

2. **Manual Folder Creation**
   - Alternatively, manually create folders named:
     - `videos` for background videos.
     - `Songs` for background music.
     - Then you can add your own videos and songs in the folders.

## Planned Improvements

- Add a precise real-time progress bar.
- Modularize the code for better readability and maintainability.

## Contribution

I'm still new to Python, so I’m open to suggestions and improvements. Contributions are highly appreciated!

I hope you find this tool helpful and enjoyable to use!
