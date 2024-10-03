# camera_app/views.py
from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
import mediapipe as mp

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Function to detect hand gestures and return the gesture type
def detect_gestures(frame):
    # No frame flipping for detection
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    gesture = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmark points for thumb and index finger
            thumb_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
            index_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

            # Determine gestures based on landmark positions
            if thumb_tip_y < index_tip_y:  # Thumb above index = 'like'
                gesture = 'like'
            else:
                gesture = 'dislike'

            # Identify if it's a left or right hand (landmark 0 is at wrist)
            wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
            # REVERSE LOGIC to account for display mirroring
            if wrist_x > 0.5:  # Reverse the x-axis check
                gesture = f'left hand {gesture}'
            else:
                gesture = f'right hand {gesture}'

    return gesture

# Video streaming generator function
def generate_video_stream():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gesture = detect_gestures(frame)

        # Flip the frame for DISPLAY purposes only (to mirror camera feed)
        display_frame = cv2.flip(frame, 1)

        # Display the detected gesture on the frame
        if gesture:
            cv2.putText(display_frame, f'Gesture: {gesture}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        _, jpeg = cv2.imencode('.jpg', display_frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()

# View for video feed
def video_feed(request):
    return StreamingHttpResponse(generate_video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')

# Main page view
def index(request):
    return render(request, 'camera_app/index.html')
