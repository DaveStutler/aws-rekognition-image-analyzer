import cv2
import platform
import subprocess
import os

def check_system_info():
    """Check system information"""
    print("=== System Information ===")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"OpenCV: {cv2.__version__}")
    print()

def check_camera_permissions():
    """Check camera permissions and devices"""
    system = platform.system()
    
    if system == "Linux":
        print("=== Linux Camera Check ===")
        try:
            # Check video devices
            result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
            if result.returncode == 0:
                print("Available video devices:")
                print(result.stdout)
            else:
                print("No video devices found in /dev/")
            
            # Check if user is in video group
            result = subprocess.run(['groups'], capture_output=True, text=True)
            if 'video' in result.stdout:
                print("✓ User is in video group")
            else:
                print("✗ User is NOT in video group")
                print("Run: sudo usermod -a -G video $USER")
                print("Then log out and log back in")
        except Exception as e:
            print(f"Error checking Linux permissions: {e}")
    
    elif system == "Darwin":  # macOS
        print("=== macOS Camera Check ===")
        print("Check System Preferences > Security & Privacy > Camera")
        print("Make sure Python/Terminal has camera access")
    
    elif system == "Windows":
        print("=== Windows Camera Check ===")
        print("Check Device Manager for camera devices")
        print("Check Privacy Settings > Camera")
    
    print()

def test_camera_indices():
    """Test different camera indices"""
    print("=== Testing Camera Indices ===")
    working_cameras = []
    
    for i in range(5):
        print(f"Testing camera index {i}...", end=" ")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Working (Resolution: {frame.shape[1]}x{frame.shape[0]})")
                working_cameras.append(i)
            else:
                print("✗ Opens but can't read frames")
            cap.release()
        else:
            print("✗ Cannot open")
    
    if working_cameras:
        print(f"\n✓ Working camera indices: {working_cameras}")
        return working_cameras[0]
    else:
        print("\n✗ No working cameras found")
        return None

def test_camera_backends():
    """Test different OpenCV backends"""
    print("=== Testing Different Backends ===")
    
    backends = [
        ("CAP_ANY", cv2.CAP_ANY),
        ("CAP_V4L2", cv2.CAP_V4L2),
        ("CAP_GSTREAMER", cv2.CAP_GSTREAMER),
        ("CAP_FFMPEG", cv2.CAP_FFMPEG),
        ("CAP_DSHOW", cv2.CAP_DSHOW),  # Windows
    ]
    
    working_backends = []
    
    for name, backend in backends:
        try:
            print(f"Testing {name}...", end=" ")
            cap = cv2.VideoCapture(0, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print("✓ Working")
                    working_backends.append((name, backend))
                else:
                    print("✗ Opens but can't read")
                cap.release()
            else:
                print("✗ Cannot open")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return working_backends

def simple_camera_test(camera_index=0):
    """Simple camera test with live preview"""
    print(f"\n=== Live Camera Test (Index {camera_index}) ===")
    print("If successful, a window will open showing your camera feed")
    print("Press 'q' to quit the test")
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("✗ Failed to open camera")
        return False
    
    print("✓ Camera opened successfully")
    
    # Set some properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✗ Failed to read frame")
                break
            
            frame_count += 1
            
            # Add frame counter to image
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Camera Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"✓ Camera test completed. Processed {frame_count} frames")
        return True

def main():
    """Main diagnostic function"""
    print("🔍 Camera Diagnostic Tool")
    print("=" * 50)
    
    # Check system info
    check_system_info()
    
    # Check permissions
    check_camera_permissions()
    
    # Test camera indices
    working_camera = test_camera_indices()
    
    # Test backends
    working_backends = test_camera_backends()
    
    if working_camera is not None:
        # Run simple camera test
        print(f"\n🎥 Running live camera test with index {working_camera}")
        input("Press Enter to start the camera test (or Ctrl+C to skip)...")
        simple_camera_test(working_camera)
    else:
        print("\n❌ No working cameras found. Please check:")
        print("1. Camera is physically connected")
        print("2. Camera drivers are installed")
        print("3. No other applications are using the camera")
        print("4. Camera permissions are granted")
        
        if platform.system() == "Linux":
            print("5. User is in the 'video' group")
        elif platform.system() == "Darwin":
            print("5. Python has camera permission in System Preferences")
        elif platform.system() == "Windows":
            print("5. Camera privacy settings allow access")

if __name__ == "__main__":
    main()