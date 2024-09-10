import cv2
import datetime

cap = cv2.VideoCapture('http://10.141.10.103:8080/video')

save_dir = r"C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 8 - Using smartphone to capture sensor data\8.3D\1\\"

while(cap.isOpened()):

    ret, frame = cap.read()

    try:
        # Rotate and resize the image
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        resized_frame = cv2.resize(rotated_frame, (720, 1280))
        cv2.imshow('Stream', resized_frame)
        
        key = cv2.waitKey(1)
        
        # Press 's' to save picture
        if key == ord('s'):
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            image_filename = f"{save_dir}captured_image_{timestamp}.jpg"
            cv2.imwrite(image_filename, resized_frame)
            print(f"Image saved: {image_filename}")
        
        # Press 'q' to exit
        if key == ord('q'):
            break
    except cv2.error as e:
        print(f"OpenCV Error: {e}")
        break

# Release the capture and close opencv windows
cap.release()
cv2.destroyAllWindows()