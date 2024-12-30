Hi,

This is a video maker tool that can make videos with customizable subtitles and various sample background videos.

I got idea for this project from tiktok and youtube, where short-form videos with random background videos and subtitles are popular, so I wanted to create a tool for myself to make videos for my own tiktok account.

The key driving factor of this project is AssemblyAI, which is a speech-to-text API that can convert audio to text with precise timestamps. The API has 5000 free credits, which is more than enough for this project. You can sign up for a free account [here](https://www.assemblyai.com/) and use your own API key in the config.py file.

I also implemented an option where you can choose elevenlabs API for the voiceover, to give more life to the video, and tkinter for the GUI set up, to make it more user-friendly.

Once you run the code, you will see a 800 x 600 window created with three tabs, which are "Script", "Subtitle customization", and "Other options". In the script tab, you can write your script and choose voice-over option,either gtts or elevenlabs. gtts is a free option. If you choose elevenlabs, you will be prompted to enter your elevenlabs API key. In Subtitle customization tab, you can customize the subtitle color, stroke color, and subtitle display style, and subtitle highlighting style. You will have 5 font options to choose from. In the other options tab, you can choose the video duration; whether you want it for tiktok video or youtube shorts (youtube shorts videos have 1 minute limit.), and the type of background video you want to use. There are five categories of videos. Lastly, you can choose to have background music in your video. There are 3 songs in the resource folder and one of them are selected randomly for every request. Once you have done all the settings, go ahead and click "Create Video" button. The video will be created in the output folder. I added a loading gif above the progress bar to make it less boring. Download the sample videos and songs folder [here](https://drive.google.com/drive/folders/1rCnLkZHQpSGqy9oPb8BobFRLSiPBlBAK?usp=sharing) and place the folders in the same directory with main.py and config.py. 

There are still some improvements that I want to make, such as adding precise real-time progress bar, and modularizing the code for better readability and maintainability. I'm still new to python so I'm open to any suggestions and improvements. I would appreciate your contribution to this project.

I hope you enjoy using this tool!
"# GoViral-Wizard---youtube-shorts-tiktok-video-creator" 
