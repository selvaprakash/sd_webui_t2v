import sys
from moviepy.editor import *

video = VideoFileClip(sys.argv[1]) # 2.
audio = video.audio # 3.
audio.write_audiofile(sys.argv[2]) # 4.