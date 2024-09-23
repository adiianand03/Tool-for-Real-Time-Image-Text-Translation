import streamlit as st
import cv2
import math
import io
import json
from translate import Translator
import requests
from PIL import Image

# Initialize session state
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

st.set_page_config(layout="wide")

# Centered image logo and title
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.write("")

with col2:
    image = Image.open("logo.jpeg")
    st.image(image, width=450, use_column_width=True)

with col3:
    st.write("")

st.markdown("<h1 style='text-align: center;'>Real Time Image Text Translator</h1>", unsafe_allow_html=True)

# Set up webcam and images folder
images_folder = "images"
cap = cv2.VideoCapture(0)  # Open web cam
frame_rate = cap.get(120)  # frame rate

# Streamlit App

# Centered selectbox for language selection
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.write("")

with col2:
    selected_language = st.selectbox("Select Language for Translation", ["hi", "es", "fr", "de", "zh"], key="language_select")
    trans = Translator(to_lang=selected_language)

with col3:
    st.write("")

# Centered button to start image capture
start_button_col1, start_button_col2, start_button_col3 = st.columns([1, 4, 1])

with start_button_col1:
    st.write("")

with start_button_col2:
    # Center the button
    if st.button("Start Image Capture", key="start_button"):
        st.session_state.button_clicked = True

with start_button_col3:
    st.write("")



# Run capture_and_translate when the button is clicked
if st.session_state.button_clicked:
    image_placeholder = st.empty()  # Create an empty space for dynamic updates
    text_placeholder = st.empty()   # Create an empty space for text output

    while cap.isOpened():
        frame_id = cap.get(1)  # current frame number
        ret, frame = cap.read()
        if not ret:
            break

        # Display real-time webcam feed
        image_placeholder.image(frame, channels="BGR")

        if frame_id % math.floor(frame_rate) == 0:
            filename = images_folder + "/image_" + str(int(frame_id)) + ".jpg"
            cv2.imwrite(filename, frame)  # Save Images

            # OCR (Extract Text from Image)
            roi = frame  # Set the region of interest as the entire frame
            url_api = "https://api.ocr.space/parse/image"
            _, compressed_image = cv2.imencode(".jpg", roi, [1, 90])
            file_bytes = io.BytesIO(compressed_image)

            result = requests.post(
                url_api,
                files={"image_480.jpg": file_bytes},
                data={"apikey": "K84345466788957", "language": "eng"},
            )

            try:
                result.raise_for_status()  # Check for errors in the HTTP response
                result_dict = result.json()  # Attempt to parse JSON response

                if "ParsedResults" in result_dict:
                    parsed_results = result_dict["ParsedResults"]

                    if parsed_results:
                        text_detected = parsed_results[0].get("ParsedText")

                        # Text Translation
                        if text_detected:
                            trt = trans.translate(text_detected)

                            # Display text output in reverse order
                            text_placeholder.text("\nOriginal Text: " + text_detected)
                            text_placeholder.text("Translated Text: " + trt)

                            # Wait for a short duration to show the translation
                            st.empty()

                else:
                    st.error("No 'ParsedResults' key found in the API response.")

            except requests.RequestException as e:
                st.error(f"Error in API request: {e}")
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    # Reset the button state when the loop is complete
    st.session_state.button_clicked = False
