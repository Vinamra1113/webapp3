import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import os
import cv2
import numpy as np
import tempfile

def watermark_video(video_path, watermark_image_path, user_choice):
    st.write("Executing video dubbing with watermark...")

    # Load the input video
    video_clip = VideoFileClip(video_path)

    # Extract audio from the video
    audio_clip = video_clip.audio
    audio_clip.write_audiofile("temp_audio.wav")

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Recognize speech from the audio file
    with sr.AudioFile("temp_audio.wav") as source:
        audio_data = recognizer.record(source)
        audio_text = recognizer.recognize_google(audio_data)

    # Print the recognized text
    st.write("Recognized Text:")
    st.write(audio_text)

    # Translate the recognized English text to the target language
    translator = Translator()
    translated_text = translator.translate(audio_text, src='en', dest=user_choice).text

    # Create a Text-to-Speech object for the translated text
    tts = gTTS(text=translated_text, lang=user_choice)

    # Save the TTS audio to a temporary file
    temp_audio_path = os.path.join(tempfile.gettempdir(), f'temp_audio_{user_choice}.mp3')
    tts.save(temp_audio_path)

    # Load the generated audio
    generated_audio_clip = AudioFileClip(temp_audio_path)

    # Combine the generated audio with the video
    video_with_audio = video_clip.set_audio(generated_audio_clip)

    # Load the watermark image
    watermark_image = cv2.imread(watermark_image_path)
    watermark_image = cv2.resize(watermark_image, (100, 100))  # Adjust the size as needed
    watermark_image = cv2.cvtColor(watermark_image, cv2.COLOR_BGR2RGB)

    # Watermark each frame in the video
    frames_with_watermark = []
    for frame in video_with_audio.iter_frames(fps=video_clip.fps):
        frame_with_watermark = add_watermark(frame, watermark_image)
        frames_with_watermark.append(frame_with_watermark)

    # Close MoviePy objects
    video_clip.close()
    generated_audio_clip.close()

    # Define the output video file path
    output_video_path = os.path.join(tempfile.gettempdir(), f'output_{user_choice}_with_watermark.mp4')

    # Write the video to the output file with compatible codecs
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), video_clip.fps,
                          (video_clip.size[0], video_clip.size[1]))
    for frame_with_watermark in frames_with_watermark:
        out.write(frame_with_watermark)
    out.release()

    # Clean up temporary files
    os.remove("temp_audio.wav")
    os.remove(temp_audio_path)

    # Display the output video with watermark
    st.video(output_video_path)


def add_watermark(frame, watermark_image):
    watermark_height, watermark_width, _ = watermark_image.shape
    
    # Create a copy of the frame to avoid modifying the original (read-only) data
    frame_with_watermark = np.copy(frame)

    # Add the watermark to the frame copy
    frame_with_watermark[0:watermark_height, 0:watermark_width] = watermark_image

    return frame_with_watermark


def main():
    st.title("Video Dubbing with Watermark Streamlit App")

    # File uploader for the input video
    video_file = st.file_uploader("Upload Video File", type=["mp4"])

    # File uploader for the watermark image
    watermark_image_file = st.file_uploader("Upload Watermark Image", type=["png", "jpg", "jpeg"])

    if video_file is not None and watermark_image_file is not None:
        # Display the uploaded video and watermark image
        st.video(video_file)
        st.image(watermark_image_file, caption="Watermark Image", use_column_width=True)

        # Language selection for dubbing
        target_language = st.selectbox("Select Target Language", ['hi', 'ta', 'te', 'mr', 'bn', 'gu', 'kn', 'ur'])

        if st.button("Dub Video with Watermark"):
            # Save the uploaded video and watermark image to temporary files
            with open("temp_video.mp4", "wb") as f:
                f.write(video_file.read())
            with open("temp_watermark_image.png", "wb") as f:
                f.write(watermark_image_file.read())

            # Dub the video with watermark
            watermark_video("temp_video.mp4", "temp_watermark_image.png", target_language)

            # Clean up temp files
            st.success("Video dubbing with watermark complete!")
            st.balloons()

if __name__ == "__main__":
    main()