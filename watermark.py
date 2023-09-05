from moviepy.editor import *

# IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# Specify the full path to the input video
input_video_path = 'media/Barby.mp4'
video_clip = VideoFileClip(input_video_path)

# Set the duration of the watermark to match the video duration
watermark = TextClip("GNEURO.RU",fontsize=150,color="White",font="Arial")

# ActayWide-Bold
# Position the watermark at the center-bottom of the video
watermark = watermark.set_position(('center'))

# Overlay the watermark on the video using CompositeVideoClip
video_with_watermark = CompositeVideoClip([video_clip, watermark])

# Save the video with the watermark
video_with_watermark.write_videofile('output_video.mp4', codec='libx264')
