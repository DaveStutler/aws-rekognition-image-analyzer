import cv2
import boto3
import json
import time
from botocore.exceptions import ClientError
import base64
from io import BytesIO

class RekognitionVideoAnalyzer:
    def __init__(self, region_name='us-east-1'):
        """
        Initialize the Rekognition client
        Make sure your AWS credentials are configured via AWS CLI or environment variables
        """
        try:
            self.rekognition = boto3.client('rekognition', region_name=region_name)
            print("✓ AWS Rekognition client initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing AWS Rekognition: {e}")
            raise
    
    def encode_image(self, frame):
        """
        Convert OpenCV frame to bytes for Rekognition API
        """
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    
    def detect_faces(self, image_bytes):
        """
        Detect faces in the image using Rekognition
        """
        try:
            response = self.rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']  # Get all face attributes
            )
            return response.get('FaceDetails', [])
        except ClientError as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def detect_labels(self, image_bytes):
        """
        Detect objects/labels in the image using Rekognition
        """
        try:
            response = self.rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=10,
                MinConfidence=70
            )
            return response.get('Labels', [])
        except ClientError as e:
            print(f"Error detecting labels: {e}")
            return []
    
    def draw_face_boxes(self, frame, faces):
        """
        Draw bounding boxes around detected faces
        """
        height, width = frame.shape[:2]
        
        for face in faces:
            box = face['BoundingBox']
            
            # Convert relative coordinates to pixel coordinates
            x = int(box['Left'] * width)
            y = int(box['Top'] * height)
            w = int(box['Width'] * width)
            h = int(box['Height'] * height)
            
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add confidence score
            confidence = face.get('Confidence', 0)
            cv2.putText(frame, f'Face: {confidence:.1f}%', 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Add age range if available
            age_range = face.get('AgeRange')
            if age_range:
                age_text = f"Age: {age_range['Low']}-{age_range['High']}"
                cv2.putText(frame, age_text, 
                           (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        return frame
    
    def print_detection_results(self, faces, labels, frame_count):
        """
        Print detection results to CLI
        """
        print(f"\n--- Frame {frame_count} Analysis ---")
        
        # Print face detection results
        if faces:
            print(f"🔍 Detected {len(faces)} face(s):")
            for i, face in enumerate(faces, 1):
                confidence = face.get('Confidence', 0)
                age_range = face.get('AgeRange', {})
                gender = face.get('Gender', {})
                emotions = face.get('Emotions', [])
                
                print(f"  Face {i}: {confidence:.1f}% confidence")
                if age_range:
                    print(f"    Age: {age_range.get('Low', 'N/A')}-{age_range.get('High', 'N/A')}")
                if gender:
                    print(f"    Gender: {gender.get('Value', 'N/A')} ({gender.get('Confidence', 0):.1f}%)")
                if emotions:
                    top_emotion = max(emotions, key=lambda x: x['Confidence'])
                    print(f"    Emotion: {top_emotion['Type']} ({top_emotion['Confidence']:.1f}%)")
        else:
            print("🔍 No faces detected")
        
        # Print object detection results
        if labels:
            print(f"🏷️  Detected {len(labels)} object(s)/label(s):")
            for label in labels[:5]:  # Show top 5 labels
                name = label['Name']
                confidence = label['Confidence']
                print(f"  {name}: {confidence:.1f}%")
        else:
            print("🏷️  No objects detected")
        
        print("-" * 40)
    
    def run_video_analysis(self, analyze_every_n_frames=30):
        """
        Main function to run video analysis
        """
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Error: Could not open webcam")
            return
        
        print("✓ Webcam initialized")
        print("📹 Starting video analysis...")
        print("Press 'q' to quit, 'space' to analyze current frame")
        print("Automatic analysis every {} frames".format(analyze_every_n_frames))
        
        frame_count = 0
        last_analysis_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("✗ Error: Could not read frame")
                    break
                
                frame_count += 1
                current_time = time.time()
                
                # Analyze frame automatically every N frames or when spacebar is pressed
                analyze_frame = False
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord(' '):  # Spacebar pressed
                    analyze_frame = True
                elif frame_count % analyze_every_n_frames == 0:  # Automatic analysis
                    analyze_frame = True
                elif key == ord('q'):  # Quit
                    break
                
                if analyze_frame and (current_time - last_analysis_time) > 2:  # Limit to once every 2 seconds
                    print(f"\n🔄 Analyzing frame {frame_count}...")
                    
                    # Convert frame to bytes
                    image_bytes = self.encode_image(frame)
                    
                    # Detect faces and objects
                    faces = self.detect_faces(image_bytes)
                    labels = self.detect_labels(image_bytes)
                    
                    # Print results to CLI
                    self.print_detection_results(faces, labels, frame_count)
                    
                    # Draw face boxes on frame
                    frame = self.draw_face_boxes(frame, faces)
                    
                    last_analysis_time = current_time
                
                # Add instructions to frame
                cv2.putText(frame, "Press SPACE to analyze, Q to quit", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Frame: {frame_count}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow('AWS Rekognition Video Analysis', frame)
        
        except KeyboardInterrupt:
            print("\n🛑 Analysis stopped by user")
        
        finally:
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            print("✓ Resources cleaned up")

def main():
    """
    Main function to run the application
    """
    print("🚀 AWS Rekognition Video Stream Analyzer")
    print("=" * 50)
    
    try:
        # Initialize analyzer
        analyzer = RekognitionVideoAnalyzer(region_name='us-east-1')  # Change region if needed
        
        # Run video analysis
        analyzer.run_video_analysis(analyze_every_n_frames=60)  # Analyze every 60 frames
        
    except Exception as e:
        print(f"✗ Application error: {e}")
        print("\nMake sure:")
        print("1. AWS credentials are configured (aws configure)")
        print("2. You have permissions for Rekognition")
        print("3. Your webcam is connected and working")
        print("4. Required packages are installed (pip install opencv-python boto3)")

if __name__ == "__main__":
    main()