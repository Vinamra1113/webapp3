import streamlit as st
from moviepy.editor import AudioFileClip, VideoFileClip
from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
import os
import io
import requests

def translator(user_choice, video_source):
    st.write("Executing video dubbing...")

    # Check if the video source is a URL
    if isinstance(video_source, str) and video_source.startswith(('http://', 'https://')):
        video_content = get_video_content_from_url(video_source)
        if video_content is None:
            st.error("Error fetching video from URL.")
            return
    else:
        # Save the uploaded video file to a temporary file
        temp_video_path = "temp_video.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(video_source.read())
        video_content = VideoFileClip(temp_video_path)

    # Extract audio from the video
    audio_clip = video_content.audio if hasattr(video_content, 'audio') else None
    if audio_clip is None:
        st.error("Unable to extract audio from the video.")
        return

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
    temp_audio_path = f'temp_audio_{user_choice}.mp3'
    tts.save(temp_audio_path)

    # Load the generated audio
    generated_audio_clip = AudioFileClip(temp_audio_path)

    # Combine the generated audio with the video
    video_with_audio = video_content.set_audio(generated_audio_clip)

    # Define the output video file path
    output_video_path = f'output_{user_choice}.mp4'

    # Write the video to the output file with compatible codecs
    video_with_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac', threads=4)

    # Clean up temporary files
    os.remove(temp_video_path)
    os.remove("temp_audio.wav")
    os.remove(temp_audio_path)

    # Display the output video
    st.video(output_video_path)

def get_video_content_from_url(video_url):
    try:
        response = requests.get(video_url)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.exceptions.RequestException as err:
        st.error(f"Error fetching video content: {err}")
        return None
       
def main():
    st.title("ANUVADAK")

    # Option to upload video file or provide URL
    upload_option = st.radio("Choose video source:", ("Upload Video", "Enter Video URL"))
    if upload_option == "Upload Video":
        video_source = st.file_uploader("Upload Video File", type=["mp4"])
    else:
        video_source = st.text_input("Enter Video URL")

    if video_source:
        if upload_option == "Upload Video":
            st.video(video_source)
        else:
            st.video(video_source)

        # Language selection for dubbing
        target_language = st.selectbox("Select Target Language", ['hi', 'te', 'ta', 'ma', 'bn', 'gu', 'kn', 'ur'])

        if st.button("Dub Video"):
            # Dub the video
            translator(target_language, video_source)

            # Clean up temp files
            st.success("Video dubbing complete!")
            st.balloons()

if __name__ == "__main__":
    main()

footer = """<style>
.footer {
    position:fixed;
    left:0;
    bottom:0;
    width:100%;
    background-color:black;
    color:white;
    text-align:center;
}
</style>
<div class="footer">
    <p>Developed by DIGITAL_DYNAMOSS</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
