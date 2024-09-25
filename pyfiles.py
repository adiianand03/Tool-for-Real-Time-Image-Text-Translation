import cv2
import math
import io
import json
from translate import Translator
import requests
from PIL import Image

# Set up webcam and images folder
images_folder = "images"
cap = cv2.VideoCapture(0)  # Open webcam
frame_rate = cap.get(120)  # Get frame rate

# Language selection for translation
print("Select Language for Translation: ")
language_options = {"1": "hi", "2": "es", "3": "fr", "4": "de", "5": "zh"}
for key, lang in language_options.items():
    print(f"{key}: {lang}")

selected_option = input("Enter the option number: ")
selected_language = language_options.get(selected_option, "en")  # Default to English if invalid option
trans = Translator(to_lang=selected_language)

# Start capturing and processing images
print("Press 'q' to quit the image capture")

while cap.isOpened():
    frame_id = cap.get(1)  # current frame number
    ret, frame = cap.read()
    if not ret:
        break

    # Display real-time webcam feed in a window
    cv2.imshow("Webcam Feed", frame)

    # Process every nth frame
    if frame_id % math.floor(frame_rate) == 0:
        filename = images_folder + "/image_" + str(int(frame_id)) + ".jpg"
        cv2.imwrite(filename, frame)  # Save images

        # OCR (Extract Text from Image)
        roi = frame  # Set the region of interest as the entire frame
        url_api = "https://api.ocr.space/parse/image"
        _, compressed_image = cv2.imencode(".jpg", roi, [1, 90])
        file_bytes = io.BytesIO(compressed_image)

        result = requests.post(
            url_api,
            files={"image_480.jpg": file_bytes},
            data={"apikey": "K83352208388957", "language": "eng"},
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

                        # Print original and translated text to the terminal
                        print("\nOriginal Text: " + text_detected)
                        print("Translated Text: " + trt)
                    else:
                        print("No text detected in the image.")
                else:
                    print("No parsed results found in API response.")
            else:
                print("No 'ParsedResults' key found in the API response.")

        except requests.RequestException as e:
            print(f"Error in API request: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # Quit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
