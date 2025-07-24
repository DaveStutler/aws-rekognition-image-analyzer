import boto3
import json
import requests
from PIL import Image
import io
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import random
import os
import sys

class RekognitionImageTester:
    def __init__(self, region_name='us-east-1'):
        """Initialize the Rekognition client"""
        try:
            self.rekognition = boto3.client('rekognition', region_name=region_name)
            print("✓ AWS Rekognition client initialized successfully")
            
            # Setup matplotlib backend
            self.setup_matplotlib()
            
        except Exception as e:
            print(f"✗ Error initializing AWS Rekognition: {e}")
            raise
    
    def setup_matplotlib(self):
        """Setup matplotlib backend for different environments"""
        print("🔧 Setting up matplotlib...")
        
        # Try to detect the environment and set appropriate backend
        backends_to_try = []
        
        # Check if we're in different environments
        if 'DISPLAY' in os.environ:
            backends_to_try.extend(['Qt5Agg', 'TkAgg', 'GTK3Agg'])
        elif sys.platform.startswith('win'):
            backends_to_try.extend(['Qt5Agg', 'TkAgg'])
        elif sys.platform.startswith('darwin'):  # macOS
            backends_to_try.extend(['MacOSX', 'Qt5Agg', 'TkAgg'])
        
        # Always add non-interactive backends as fallback
        backends_to_try.extend(['Agg'])
        
        backend_set = False
        for backend in backends_to_try:
            try:
                matplotlib.use(backend, force=True)
                print(f"✓ Using matplotlib backend: {backend}")
                self.interactive_mode = backend != 'Agg'
                backend_set = True
                break
            except Exception as e:
                print(f"⚠️  Backend {backend} failed: {e}")
                continue
        
        if not backend_set:
            print("⚠️  Using default matplotlib backend")
            self.interactive_mode = True
        
        # Configure matplotlib settings
        plt.rcParams['figure.max_open_warning'] = 0
        
        if not self.interactive_mode:
            print("📁 Non-interactive mode detected - images will be saved to files")
            os.makedirs('rekognition_output', exist_ok=True)
    
    def download_test_image(self, url):
        """Download a test image from URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def analyze_image(self, image_bytes):
        """Analyze image with Rekognition"""
        results = {}
        
        # Detect faces
        try:
            face_response = self.rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )
            results['faces'] = face_response.get('FaceDetails', [])
        except Exception as e:
            print(f"Error detecting faces: {e}")
            results['faces'] = []
        
        # Detect labels/objects
        try:
            label_response = self.rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=10,
                MinConfidence=70
            )
            results['labels'] = label_response.get('Labels', [])
        except Exception as e:
            print(f"Error detecting labels: {e}")
            results['labels'] = []
        
        return results
    
    def visualize_results(self, image_bytes, results, image_name):
        """Visualize detection results with bounding boxes using matplotlib"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get image dimensions
        img_width, img_height = image.size
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(f'AWS Rekognition Analysis: {image_name}', fontsize=16, fontweight='bold')
        
        # Left subplot: Face detection
        ax1.imshow(image)
        ax1.set_title('Face Detection', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        faces = results.get('faces', [])
        if faces:
            colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
            for i, face in enumerate(faces):
                bbox = face['BoundingBox']
                
                # Convert relative coordinates to pixel coordinates
                x = bbox['Left'] * img_width
                y = bbox['Top'] * img_height
                width = bbox['Width'] * img_width
                height = bbox['Height'] * img_height
                
                # Choose color
                color = colors[i % len(colors)]
                
                # Draw bounding box
                rect = Rectangle((x, y), width, height, 
                               linewidth=3, edgecolor=color, facecolor='none')
                ax1.add_patch(rect)
                
                # Add face information
                confidence = face.get('Confidence', 0)
                age_range = face.get('AgeRange', {})
                gender = face.get('Gender', {})
                emotions = face.get('Emotions', [])
                
                # Create label text
                label_parts = [f'Face {i+1}: {confidence:.1f}%']
                
                if age_range:
                    label_parts.append(f"Age: {age_range.get('Low', '?')}-{age_range.get('High', '?')}")
                
                if gender:
                    label_parts.append(f"{gender.get('Value', 'Unknown')}")
                
                if emotions:
                    top_emotion = max(emotions, key=lambda x: x['Confidence'])
                    label_parts.append(f"{top_emotion['Type']}")
                
                label_text = '\n'.join(label_parts)
                
                # Position label above the box
                label_y = max(0, y - 10)
                ax1.text(x, label_y, label_text, 
                        fontsize=10, fontweight='bold', color=color,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                        verticalalignment='bottom')
        else:
            ax1.text(img_width/2, img_height/2, 'No Faces Detected', 
                    fontsize=16, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
        
        # Right subplot: Object/Label detection
        ax2.imshow(image)
        ax2.set_title('Object Detection', fontsize=14, fontweight='bold')
        ax2.axis('off')
        
        labels = results.get('labels', [])
        if labels:
            # Filter labels that have bounding box instances
            labels_with_boxes = []
            labels_without_boxes = []
            
            for label in labels:
                instances = label.get('Instances', [])
                if instances:
                    labels_with_boxes.extend([(label['Name'], label['Confidence'], inst) 
                                            for inst in instances])
                else:
                    labels_without_boxes.append((label['Name'], label['Confidence']))
            
            # Draw bounding boxes for object instances
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels_with_boxes)))
            
            for i, (name, confidence, instance) in enumerate(labels_with_boxes):
                bbox = instance.get('BoundingBox', {})
                if bbox:
                    # Convert relative coordinates to pixel coordinates
                    x = bbox['Left'] * img_width
                    y = bbox['Top'] * img_height
                    width = bbox['Width'] * img_width
                    height = bbox['Height'] * img_height
                    
                    color = colors[i]
                    
                    # Draw bounding box
                    rect = Rectangle((x, y), width, height, 
                                   linewidth=2, edgecolor=color, facecolor='none')
                    ax2.add_patch(rect)
                    
                    # Add label
                    inst_confidence = instance.get('Confidence', confidence)
                    label_text = f'{name}\n{inst_confidence:.1f}%'
                    
                    ax2.text(x, max(0, y - 5), label_text, 
                            fontsize=9, fontweight='bold', color='black',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor=color, alpha=0.8),
                            verticalalignment='bottom')
            
            # Add general labels (without specific locations) as text overlay
            if labels_without_boxes:
                general_labels = [f'{name} ({conf:.1f}%)' 
                                for name, conf in labels_without_boxes[:5]]
                general_text = 'General Labels:\n' + '\n'.join(general_labels)
                
                ax2.text(10, img_height - 10, general_text, 
                        fontsize=10, fontweight='bold', color='white',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7),
                        verticalalignment='top')
        else:
            ax2.text(img_width/2, img_height/2, 'No Objects Detected', 
                    fontsize=16, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        
        # Save or show the plot
        if self.interactive_mode:
            try:
                plt.show()
            except Exception as e:
                print(f"⚠️  Interactive display failed: {e}")
                self.save_plot(fig, f'detection_results_{image_name}')
        else:
            self.save_plot(fig, f'detection_results_{image_name}')
        
        plt.close(fig)  # Clean up memory
        
        # Also create a summary statistics plot
        self.create_summary_plot(results, image_name)
    
    def save_plot(self, fig, filename):
        """Save plot to file"""
        # Clean filename
        clean_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_filename = clean_filename.replace(' ', '_')
        filepath = f'rekognition_output/{clean_filename}.png'
        
        try:
            fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"💾 Saved visualization: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save plot: {e}")
    
    def create_summary_plot(self, results, image_name):
        """Create summary statistics visualization"""
        faces = results.get('faces', [])
        labels = results.get('labels', [])
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Detection Summary: {image_name}', fontsize=16, fontweight='bold')
        
        # Face emotions distribution
        if faces:
            all_emotions = {}
            for face in faces:
                emotions = face.get('Emotions', [])
                for emotion in emotions:
                    emotion_type = emotion['Type']
                    confidence = emotion['Confidence']
                    if emotion_type not in all_emotions:
                        all_emotions[emotion_type] = []
                    all_emotions[emotion_type].append(confidence)
            
            if all_emotions:
                emotion_names = list(all_emotions.keys())
                emotion_scores = [max(scores) for scores in all_emotions.values()]
                
                bars = ax1.bar(emotion_names, emotion_scores, color='skyblue', alpha=0.8)
                ax1.set_title('Detected Emotions (Max Confidence)', fontweight='bold')
                ax1.set_ylabel('Confidence %')
                ax1.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar, score in zip(bars, emotion_scores):
                    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            f'{score:.1f}%', ha='center', va='bottom', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No Faces Detected', ha='center', va='center',
                    transform=ax1.transAxes, fontsize=14)
            ax1.set_title('Detected Emotions', fontweight='bold')
        
        # Age distribution
        if faces:
            ages = []
            for face in faces:
                age_range = face.get('AgeRange', {})
                if age_range:
                    avg_age = (age_range.get('Low', 0) + age_range.get('High', 0)) / 2
                    ages.append(avg_age)
            
            if ages:
                ax2.hist(ages, bins=max(1, len(ages)), color='lightcoral', alpha=0.8, edgecolor='black')
                ax2.set_title('Age Distribution', fontweight='bold')
                ax2.set_xlabel('Age')
                ax2.set_ylabel('Count')
            else:
                ax2.text(0.5, 0.5, 'No Age Data', ha='center', va='center',
                        transform=ax2.transAxes, fontsize=14)
                ax2.set_title('Age Distribution', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No Faces Detected', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=14)
            ax2.set_title('Age Distribution', fontweight='bold')
        
        # Top objects/labels
        if labels:
            top_labels = sorted(labels, key=lambda x: x['Confidence'], reverse=True)[:8]
            label_names = [label['Name'] for label in top_labels]
            label_scores = [label['Confidence'] for label in top_labels]
            
            bars = ax3.barh(label_names, label_scores, color='lightgreen', alpha=0.8)
            ax3.set_title('Top Detected Objects/Labels', fontweight='bold')
            ax3.set_xlabel('Confidence %')
            
            # Add value labels
            for bar, score in zip(bars, label_scores):
                ax3.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                        f'{score:.1f}%', ha='left', va='center', fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'No Objects Detected', ha='center', va='center',
                    transform=ax3.transAxes, fontsize=14)
            ax3.set_title('Top Detected Objects/Labels', fontweight='bold')
        
        # Detection counts
        detection_counts = {
            'Faces': len(faces),
            'Total Labels': len(labels),
            'Labels w/ Boxes': sum(1 for label in labels if label.get('Instances'))
        }
        
        bars = ax4.bar(detection_counts.keys(), detection_counts.values(), 
                      color=['gold', 'mediumpurple', 'orange'], alpha=0.8)
        ax4.set_title('Detection Counts', fontweight='bold')
        ax4.set_ylabel('Count')
        
        # Add value labels
        for bar, count in zip(bars, detection_counts.values()):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontweight='bold', fontsize=12)
        
        plt.tight_layout()
        
        # Save or show the plot
        if self.interactive_mode:
            try:
                plt.show()
            except Exception as e:
                print(f"⚠️  Interactive display failed: {e}")
                self.save_plot(fig, f'summary_stats_{image_name}')
        else:
            self.save_plot(fig, f'summary_stats_{image_name}')
        
        plt.close(fig)  # Clean up memory
        """Display analysis results"""
        print(f"\n{'='*50}")
        print(f"🔍 Analysis Results for: {image_name}")
        print(f"{'='*50}")
        
        faces = results.get('faces', [])
        labels = results.get('labels', [])
        
        # Display face results
        if faces:
            print(f"\n👥 FACES DETECTED: {len(faces)}")
            print("-" * 30)
            for i, face in enumerate(faces, 1):
                confidence = face.get('Confidence', 0)
                print(f"Face {i}: {confidence:.1f}% confidence")
                
                # Age
                age_range = face.get('AgeRange', {})
                if age_range:
                    print(f"  Age: {age_range.get('Low', 'N/A')}-{age_range.get('High', 'N/A')}")
                
                # Gender
                gender = face.get('Gender', {})
                if gender:
                    print(f"  Gender: {gender.get('Value', 'N/A')} ({gender.get('Confidence', 0):.1f}%)")
                
                # Emotions
                emotions = face.get('Emotions', [])
                if emotions:
                    top_emotion = max(emotions, key=lambda x: x['Confidence'])
                    print(f"  Primary Emotion: {top_emotion['Type']} ({top_emotion['Confidence']:.1f}%)")
                
                # Other attributes
                smile = face.get('Smile', {})
                if smile:
                    print(f"  Smiling: {smile.get('Value', 'N/A')} ({smile.get('Confidence', 0):.1f}%)")
                
                eyeglasses = face.get('Eyeglasses', {})
                if eyeglasses:
                    print(f"  Eyeglasses: {eyeglasses.get('Value', 'N/A')} ({eyeglasses.get('Confidence', 0):.1f}%)")
                
                print()
        else:
            print("\n👥 No faces detected")
        
        # Display object/label results
        if labels:
            print(f"\n🏷️  OBJECTS/LABELS DETECTED: {len(labels)}")
            print("-" * 30)
            for label in labels:
                name = label['Name']
                confidence = label['Confidence']
                print(f"📍 {name}: {confidence:.1f}%")
                
                # Show instances if available
                instances = label.get('Instances', [])
                if instances:
                    print(f"   Instances found: {len(instances)}")
                    for instance in instances[:3]:  # Show first 3 instances
                        bbox = instance.get('BoundingBox', {})
                        inst_conf = instance.get('Confidence', 0)
                        print(f"     - Confidence: {inst_conf:.1f}%")
        else:
            print("\n🏷️  No objects/labels detected")
    
    def test_with_sample_images(self):
        """Test with sample images"""
        # Sample images (these are public domain/freely available)
        test_images = [
            {
                'name': 'People in a meeting',
                'url': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=600&fit=crop'
            },
            {
                'name': 'Person with objects',
                'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop'
            },
            {
                'name': 'Office scene',
                'url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=600&fit=crop'
            }
        ]
        
        for image_info in test_images:
            print(f"\n🖼️  Downloading and analyzing: {image_info['name']}")
            
            image_bytes = self.download_test_image(image_info['url'])
            if image_bytes:
                results = self.analyze_image(image_bytes)
                
                # Show visual results
                print("\n📊 Generating visualizations...")
                self.visualize_results(image_bytes, results, image_info['name'])
                
            else:
                print(f"❌ Failed to download {image_info['name']}")
            
            input("\nPress Enter to continue to next image...")
    
    def test_custom_image(self, image_path):
        """Test with a custom image file"""
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            print(f"🖼️  Analyzing custom image: {image_path}")
            results = self.analyze_image(image_bytes)
            
            # Show visual results
            print("\n📊 Generating visualizations...")
            self.visualize_results(image_bytes, results, image_path)
            
        except Exception as e:
            print(f"❌ Error processing custom image: {e}")

    def test_bucket_image(self, bucket_name, object_key):
        """Test with an image from S3 bucket"""
        try:
            s3 = boto3.client('s3')
            if object_key.lower() == 'all':
                # List all objects in the bucket
                print(f"📂 Listing all images in bucket: {bucket_name}")
                response = s3.list_objects_v2(Bucket=bucket_name)
                if 'Contents' not in response:
                    print("❌ No objects found in the bucket")
                    return
                
                for obj in response['Contents']:
                    object_key = obj['Key']
                    print(f"🖼️  Processing image: {object_key}")
                    response = s3.get_object(Bucket=bucket_name, Key=object_key)
                    image_bytes = response['Body'].read()
                    # Analyze the image
                    results = self.analyze_image(image_bytes)
                    # Show visual results
                    print("\n📊 Generating visualizations...")
                    self.visualize_results(image_bytes, results, object_key)
                    input("\nPress Enter to continue to next image...")
                return

            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            image_bytes = response['Body'].read()
            print(f"🖼️  Analyzing image from S3: {object_key} in bucket {bucket_name}")
            results = self.analyze_image(image_bytes)
            
            # Show visual results
            print("\n📊 Generating visualizations...")
            self.visualize_results(image_bytes, results, object_key)

        except Exception as e:
            print(f"❌ Error processing image from S3: {e}")



def main():
    """Main function"""
    print("🧪 AWS Rekognition Visual Analysis Tool")
    print("This script analyzes images and shows visual bounding boxes!")
    print("=" * 60)
    
    try:
        # Initialize tester
        tester = RekognitionImageTester()
        
        print("\nChoose an option:")
        print("1. Test with sample images from the internet")
        print("2. Test with your own image file")
        print("3. Test with images from an S3 bucket")
        
        choice = input("Enter choice (1, 2, or 3): ").strip()
        
        if choice == '1':
            print("\n📥 This will download and analyze sample images from the internet")
            confirm = input("Continue? (y/n): ").lower().strip()
            if confirm == 'y':
                tester.test_with_sample_images()
            else:
                print("Sample test cancelled")

        elif choice == '2':
            image_path = input("Enter the path to your image file: ").strip()
            if image_path:
                tester.test_custom_image(image_path)
            else:
                print("No image path provided")
        
        elif choice == '3':
            bucket_name = input("Enter the S3 bucket name: ").strip()
            object_key = input("Enter the S3 object key (name of the file) or type \"all\" for all images: ").strip()
            if bucket_name and object_key:
                tester.test_bucket_image(bucket_name, object_key)
            else:
                print("Bucket name or object key not provided")

        else:
            print("Invalid choice")
            return
            
        print("\n✅ Visual analysis completed!")
        print("You should have seen:")
        print("• Bounding boxes around faces and objects")
        print("• Labels with confidence scores")
        print("• Summary statistics charts")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nPlease check:")
        print("1. AWS credentials are configured: aws configure")
        print("2. You have Rekognition permissions")
        print("3. Internet connection is working (for sample images)")
        print("4. matplotlib is installed: pip install matplotlib")
        print("5. Your input is correct (image paths, S3 bucket/key)")

if __name__ == "__main__":
    main()