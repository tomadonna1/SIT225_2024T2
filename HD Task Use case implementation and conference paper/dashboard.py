import streamlit as st
from collections import Counter
import time
from hand_prediction import HandGestureRecognizer
import cv2
import firebase_admin
from firebase_admin import db
import threading

# Firebase set up
if not firebase_admin._apps:
    databaseURL = ''
    cred_obj = firebase_admin.credentials.Certificate(
        ''
    )
    default_app = firebase_admin.initialize_app(cred_obj, {
        'databaseURL':databaseURL
    })

# Reference to Firebase Realtime Database
ref = db.reference('/food-likes')

# Initialize the hand prediction class
recognizer = HandGestureRecognizer()

# Sample menu items
menu_items = [
    {'name': 'Pizza', 'image': 'https://upload.wikimedia.org/wikipedia/commons/9/91/Pizza-3007395.jpg'},
    {'name': 'Burger', 'image': 'https://www.foodandwine.com/thmb/jldKZBYIoXJWXodRE9ut87K8Mag=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/crispy-comte-cheesburgers-FT-RECIPE0921-6166c6552b7148e8a8561f7765ddf20b.jpg'},
    {'name': 'Pasta', 'image': 'https://assets.epicurious.com/photos/5988e3458e3ab375fe3c0caf/1:1/w_3607,h_3607,c_limit/How-to-Make-Chicken-Alfredo-Pasta-hero-02082017.jpg'}
]

# Threaded VideoCapture class
class VideoCaptureThread:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.ret = False
        self.frame = None
        self.stopped = False
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def release(self):
        self.stopped = True
        self.cap.release()

# State to keep track of current menu selection and confirmation
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None
if 'confirm_order' not in st.session_state:
    st.session_state.confirm_order = False
if 'cancel_order' not in st.session_state:
    st.session_state.cancel_order = False
if 'menu_index' not in st.session_state:
    st.session_state.menu_index = 0
if 'cycle_state' not in st.session_state:
    st.session_state.cycle_state = 'navigation'
if 'start_stream' not in st.session_state:
    st.session_state.start_stream = False 
if 'video_thread' not in st.session_state:
    st.session_state.video_thread = None 

# Control processing interval
PROCESS_EVERY_N_FRAMES = 2
frame_counter = 0

# Placeholder for video and gesture prediction (side by side)
col1, col2 = st.columns(2)
video_placeholder = col1.empty()
cropped_image_placeholder = col1.empty()

def save_food_firebase(food_item):
    """Save food selection to Firebase Realtime Database."""
    votes_ref = ref.child(food_item).get()
    current_votes = votes_ref.get('votes', 0) if votes_ref else 0
    ref.child(food_item).set({
        'votes': current_votes + 1  # Increment votes for the selected food item
    })


def predict_gesture():
    """
    Capture predictions for 10s and return the most frequent label. 
    """    
    global frame_counter
    end_time = time.time() + 10
    predictions = []

    if st.session_state.video_thread and st.session_state.video_thread.cap.isOpened():
        while time.time() < end_time:
            ret, frame = st.session_state.video_thread.read()
            if not ret:
                break
            
            if frame_counter % PROCESS_EVERY_N_FRAMES == 0:
                # Predict user gestures via camera
                # frame = cv2.resize(frame, (360, 640)) # Lower the resolution
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                predicted_gesture, cropped_image = recognizer.predict_hand_gestures(rgb_frame)
                
                # Display the cropped image being fed into the model
                if cropped_image is not None:
                    cropped_image_placeholder.image(cropped_image, channels="RGB")
                
                if predicted_gesture:
                    predictions.append(predicted_gesture)
                    
                # Display the video
                rotated_frame = cv2.rotate(rgb_frame, cv2.ROTATE_90_CLOCKWISE)
                resized_frame = cv2.resize(rotated_frame, (180, 320))
                video_placeholder.image(resized_frame, channels="RGB")
                # video_placeholder.image(rgb_frame, channels="RGB")
                
            # Increment frame counter
            frame_counter += 1
                

        if predictions:
            # return the most frequent gesture
            most_common_gesture = Counter(predictions).most_common(1)[0][0]
            return most_common_gesture
        else:
            return None
    else:
        st.warning("Video stream not started yet.")
        return None

# Display menu option in the second column
with col2:  
    # Display menu options
    st.title("Touchless Menu")
    
    # Button to start the video stream
    if not st.session_state.start_stream:
        if st.button("Start Video Stream"):
            st.session_state.start_stream = True
            
            # Set up the video capture
            st.session_state.video_thread = VideoCaptureThread('http://10.141.10.103:8080/video')
            # st.session_state.cap = cv2.VideoCapture(0)
            st.rerun() 
    
    # Button to stop the video stream
    if st.session_state.start_stream:
        if st.button("Stop Video Stream"):
            st.write("Video stream stopped.")
            if st.session_state.video_thread:
                st.session_state.video_thread.release()
            st.session_state.start_stream = False
            st.stop()

    # Menu Cycle State Management
    if st.session_state.cycle_state == 'navigation':
        st.subheader("Menu Navigation: Show '5' to cycle through the menu, and 'yes' to select an item.")
        # st.session_state.start_stream = True
        
        # Display the current menu item
        current_item = menu_items[st.session_state.menu_index]
        st.write(f"Currently viewing: {current_item['name']}")
        
        # Display the corresponding image
        st.image(current_item['image'], use_column_width=True)

        # Prediction for cycling or selection
        gesture = predict_gesture()
        
        # Debugging information to check which gesture was predicted
        st.write(f"Predicted Gesture: {gesture}")
        
        # Menu ordering
        if gesture == '5':
            st.session_state.menu_index = (st.session_state.menu_index + 1) % len(menu_items)
            st.rerun()  
        elif gesture == 'yes':
            st.session_state.selected_item = current_item['name']
            st.session_state.cycle_state = 'selection'
            st.rerun() 
        elif gesture == 'no': 
            st.session_state.cycle_state = 'navigation'
            st.rerun() 
        else:
            pass

            
    # Item Confirmation
    elif st.session_state.cycle_state == 'selection':
        st.subheader(f"Confirm your selection: {st.session_state.selected_item}")
        st.write("Show 'yes' to confirm or 'no' to cancel.")

        # Prediction for confirmation
        gesture = predict_gesture()
        
        # Debugging information to check which gesture was predicted
        st.write(f"Predicted Gesture: {gesture}")

        if gesture == 'yes':
            save_food_firebase(st.session_state.selected_item) # add food to firebase
            st.session_state.cycle_state = 'confirmation'
            st.session_state.confirm_order = True
            st.rerun() 
        elif gesture == 'no':
            st.session_state.selected_item = None
            st.session_state.cycle_state = 'navigation'
            st.rerun() 
        elif gesture == '5':
            st.session_state.cycle_state = 'selection'
            st.rerun() 
        else:
            pass
            
        
            
    # Final Confirmation or Cancelation
    elif st.session_state.cycle_state == 'confirmation':
        st.subheader(f"Order Confirmed: {st.session_state.selected_item}")
        st.write("Your order has been placed!")
        st.balloons()  # Adds a Streamlit animation for feedback
        time.sleep(5)
        st.session_state.cycle_state = 'navigation'
        st.session_state.selected_item = None
        st.rerun()  


# Release the video capture at the end if stream is stopped
if 'video_thread' in st.session_state and st.session_state.video_thread and st.session_state.cycle_state == 'stop':
    st.session_state.video_thread.release()