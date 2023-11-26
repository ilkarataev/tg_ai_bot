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

input_video_path = '../media/Matrix.mp4'
video_clip = VideoFileClip(input_video_path)
video_clip = video_clip.subclip(0, 3)
# Load the PNG image with a transparent background as the watermark
watermark = ImageClip('imgs/watermark.png')
watermark = watermark.set_opacity(0.5)
# Уменьшить размер водяного знака
new_width = int(video_clip.size[0] * 0.6)  # Уменьшаем ширину до 40% от исходной
watermark = watermark.resize(width=new_width)
# watermark = watermark.resize(0.3)
# Set the duration of the watermark to match the video duration
watermark = watermark.set_duration(video_clip.duration)
watermark = watermark.set_position(('center','bottom') )
# Overlay the watermark on the video using CompositeVideoClip
video_with_watermark = CompositeVideoClip([video_clip, watermark])
# watermark_file='media/output_watermark.mp4'
# Save the video with the watermark
video_with_watermark.write_videofile('../media/output.mp4', codec='libx264')