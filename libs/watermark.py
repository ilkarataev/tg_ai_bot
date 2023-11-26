# from moviepy.editor import *

# # Specify the full path to the input video
# input_video_path = 'media/Barby.mp4'
# video_clip = VideoFileClip(input_video_path)

# # Set the duration of the watermark to match the video duration
# watermark = TextClip("GNEURO.RU", fontsize=150, color="White", font="Arial", bg_opacity=0.5)
# watermark = watermark.set_duration(video_clip.duration)  # Устанавливаем продолжительность

# # Position the watermark at the center-bottom of the video
# watermark = watermark.set_position(('center'))

# # Overlay the watermark on the video using CompositeVideoClip
# video_with_watermark = CompositeVideoClip([video_clip, watermark])

# # Save the video with the watermark
# video_with_watermark.write_videofile('media/output_video.mp4', codec='libx264')

from moviepy.editor import *

# Specify the full path to the input video
input_video_path = 'media/Barby.mp4'
video_clip = VideoFileClip(input_video_path)

# Load the PNG image with a transparent background as the watermark
watermark = ImageClip('media/watermark.png')

watermark = watermark.set_opacity(0.5)

# Set the duration of the watermark to match the video duration
watermark = watermark.set_duration(video_clip.duration)

# Position the watermark at the center-bottom of the video
watermark = watermark.set_position(('center'))

# Overlay the watermark on the video using CompositeVideoClip
video_with_watermark = CompositeVideoClip([video_clip, watermark])

# Save the video with the watermark
video_with_watermark.write_videofile('media/output_video.mp4', codec='libx264')
