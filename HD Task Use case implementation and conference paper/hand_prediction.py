import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
from tensorflow.keras.models import load_model
from tensorflow.keras import mixed_precision
import tensorflow as tf

class HandGestureRecognizer:
    def __init__(self, model_path='model11.h5', class_labels=None, img_size=300, offset=100):
        # Set default class labels if none are provided
        if class_labels is None:
            class_labels = ['5', 'no', 'yes']

        # Load the trained model
        self.model = load_model(model_path)

        # Initialize the hand detector
        self.detector = HandDetector(maxHands=1)  # Track only one hand

        # Parameters for image size, frame dimensions, and offset for cropping
        self.img_size = img_size  # Final image size (with padding)
        self.offset = offset  # Increased offset for better cropping
        self.class_labels = class_labels

        # Enable memory growth for GPUs to prevent full memory allocation
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError as e:
                print(e)

    def resize_with_padding(self, image, target_size=300, padding_color=(255, 255, 255)):
        h, w, _ = image.shape
        if w == 0 or h == 0:
            return np.full((target_size, target_size, 3), padding_color, dtype=np.uint8)  # Return blank image if width or height is zero

        aspect_ratio = h / w
        
        if aspect_ratio > 1:  # If height > width
            k = target_size / h
            w_cal = math.ceil(k * w)
            img_resize = cv2.resize(image, (w_cal, target_size))
            # Calculate padding for the width
            pad_width = (target_size - w_cal) // 2
            img_padded = cv2.copyMakeBorder(img_resize, 0, 0, pad_width, pad_width, cv2.BORDER_CONSTANT, value=padding_color)
        else:  # If width >= height
            k = target_size / w
            h_cal = math.ceil(k * h)
            img_resize = cv2.resize(image, (target_size, h_cal))
            # Calculate padding for the height
            pad_height = (target_size - h_cal) // 2
            img_padded = cv2.copyMakeBorder(img_resize, pad_height, pad_height, 0, 0, cv2.BORDER_CONSTANT, value=padding_color)

        return img_padded

    def preprocess_image(self, image, target_size=64):
        """
        Preprocesses the hand image by resizing and normalizing it to fit the model input.
        """
        # Resize the image to the target size
        image = cv2.resize(image, (target_size, target_size))
        
        # Normalize the pixel values to [0, 1]
        image = image / 255.0
        
        # Expand dimensions to match the model's input format (batch_size, height, width, channels)
        image = np.expand_dims(image, axis=0)
        
        return image

    def predict_hand_gestures(self, frame):
        # Rotate the frame
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Detect hands in the frame
        hands, img = self.detector.findHands(rotated_frame, draw=False)  # Do not draw hand landmarks

        if hands:
            hand = hands[0]  # Get the first detected hand
            x, y, w, h = hand['bbox']  # Get the bounding box coordinates of the hand

            # Crop the hand region from the original image with offset
            img_crop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]

            # Resize the cropped hand image with padding to keep aspect ratio
            img_padded = self.resize_with_padding(img_crop, target_size=self.img_size)

            # Preprocess the padded image (resize to match model input, normalize)
            img_preprocessed = self.preprocess_image(img_padded, target_size=64)  # Adjust size based on your model input size

            # Make the prediction
            prediction = self.model.predict(img_preprocessed)

            # Get the predicted class (index of the class with the highest probability)
            predicted_class = np.argmax(prediction, axis=1)[0]

            # Get the corresponding label
            predicted_label = self.class_labels[predicted_class]
            
            # Return the predicted gesture
            return predicted_label, img_preprocessed 
        
        return None, None # No hand detected, return None
