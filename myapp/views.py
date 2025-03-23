from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from myapp.Real_time_video_Dehazing.haze_removal import HazeRemoval  # Assuming your haze removal script is in this file
from myapp.Real_time_video_Dehazing.camera_dehaze import main  # Import your main function

import time
import cv2
import numpy as np
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import StreamingHttpResponse
import subprocess
import threading


name = ''
mail = ''


def dirhome(req):
    check_user(req)
    return redirect('/home')


def check_user(req):
    global name, mail
    name = req.COOKIES.get('username')  # Get username from cookies
    mail = req.COOKIES.get('useremail')  # Get email from cookies
    if name and mail:
        return
    else:
        print("No user found in cookies. Redirecting to login...")  # Debugging
        return redirect('/locked')  # Redirect if cookies are missing


def registration(req):
    check_user(req)
    global name, mail
    if name:
        return redirect('home')
    if (req.method == 'POST'):
        name = req.POST.get('name')
        mail = req.POST.get('mail')
        if (name and mail and len(req.POST.get('password')) >= 8):
            if not req.POST.get("terms"):
                return render(req, 'login.html', {'active': 'register', 'error': 'Accept the terms to continue', 'name': name, 'mail': mail})

            if (User.objects.filter(Name=name).exists()):
                return render(req, 'login.html', {'active': 'register', 'error': 'The UserName is already Taken', 'name': name, 'mail': mail})

            if (User.objects.filter(Mail=mail).exists()):
                return render(req, 'login.html', {'active': 'register', 'error': 'The UserEmail is already Taken', 'name': name, 'mail': mail})

            data = User()
            data.Name = name
            data.Mail = mail
            data.Password = make_password(req.POST.get('password'))
            data.save()
            return render(req, 'login.html', {'success': 'User Registartion was successful'})
        elif (len(req.POST.get('password')) < 8):
            return render(req, 'login.html', {'active': 'register', 'error': 'The Password must need to contain more than 8 words', 'name': name, 'mail': mail})

        print('Registered Failure')
    return render(req, 'login.html')


def login(req):
    if (req.COOKIES.get('username')):
        return render(req, 'home.html', {'request': req})
    if (req.method == "POST"):
        print("kumar")
        mail = req.POST.get('email')
        password = req.POST.get('password')
        if (len(password) < 8):
            return render(req, 'login.html', {'error': 'Passowrd need to havecd  more than 8 characters', 'umail': mail})
        data = User.objects.filter(Mail=mail).first()
        if data:
            if check_password(password, data.Password):
                res = render(req, 'home.html', {
                    'username': data.Name,
                    'email': data.Mail,
                    'success': 'Login Successful'
                })

                res.set_cookie('username', data.Name, max_age=6 * 60 * 60)
                res.set_cookie('useremail', data.Mail, max_age=6 * 60 * 60)

                return res
            return render(req, 'login.html', {'error': 'Passowrd was Incorrect', 'umail': mail})
        return render(req, 'login.html', {'error': 'UserEmail was not registered'})
    return render(req, 'login.html')


def logout(req):
    global name, mail
    name = ''
    mail = ''

    res = redirect('login')
    res.delete_cookie('username')
    res.delete_cookie('useremail')
    return res


def about(req):
    check_user(req)
    if not req.COOKIES.get('username'):
        return redirect('login')  # Redirect if the user is not logged in
    return render(req, 'about.html', {'request': req})

def team(req):
    check_user(req)  # Ensure user is checked
    if not req.COOKIES.get('username'):
        return redirect('login')  # Redirect if the user is not logged in
    return render(req, 'team.html', {'request': req})

def product(req):
    check_user(req)
    if not req.COOKIES.get('username'):
        return redirect('login')  # Redirect if the user is not logged in
    return render(req, 'product.html')

def product_redirect(req, category):
    if check_user(req):
        return redirect('/locked')
    if(category == 'image'):
        return render(req, 'image.html')
    elif(category == 'video'):
        return render(req, 'video.html')
    elif(category == 'camera'):
        return render(req, 'camera.html')
    
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'upload')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        # Save image to the 'upload' folder
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(image.name, image)

        uploaded_file_url = fs.url(filename)
        
        # You can return the uploaded image URL for use in the template
        return render(request, 'home.html', {
            'uploaded_file_url': uploaded_file_url
        })

@csrf_exempt
def save_image(request):
    try:
        if request.method == 'POST' and request.FILES.get('image'):
            image = request.FILES['image']

            # Ensure 'upload' folder exists
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'upload')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            # Save image in 'media/upload/' folder
            fs = FileSystemStorage(location=upload_dir, base_url=f"{settings.MEDIA_URL}upload/")
            filename = fs.save(image.name, image)
            file_url = fs.url(filename)

            # Image path for original image
            image_path = os.path.join(upload_dir, filename)

            # Initialize and process the image
            hr = HazeRemoval()
            hr.open_image(image_path)
            hr.get_dark_channel()
            hr.get_air_light()
            hr.get_transmission()
            hr.guided_filter_opencv(r=60, eps=0.001)
            hr.recover()
            hr.enhance_visibility(alpha=1.5, beta=30)

            # Ensure 'dehazed' folder exists
            dehazed_dir = os.path.join(settings.MEDIA_ROOT, 'dehazed')
            if not os.path.exists(dehazed_dir):
                os.makedirs(dehazed_dir)

            # Save processed image in 'media/dehazed/'
            processed_image_name = f"{os.path.splitext(filename)[0]}_dehazed{os.path.splitext(filename)[1]}"
            processed_image_path = os.path.join(dehazed_dir, processed_image_name)
            cv2.imwrite(processed_image_path, hr.dst[:, :, (2, 1, 0)])  # Save in BGR format

            # Construct correct URLs
            processed_image_url = f"{settings.MEDIA_URL}dehazed/{processed_image_name}"

            return JsonResponse({'file_url': file_url, 'processed_image_url': processed_image_url})

        else:
            return JsonResponse({'error': 'No image uploaded'}, status=400)

    except Exception as e:
        print(f"Error during image processing: {e}")
        return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)


@csrf_exempt
def save_video(request):
    try:
        if request.method == 'POST' and request.FILES.get('video'):
            video = request.FILES['video']
            
            # Create videos directory if it doesn't exist
            videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
            if not os.path.exists(videos_dir):
                os.makedirs(videos_dir)
            
            # Save video to the 'videos' folder
            fs = FileSystemStorage(location=videos_dir)
            filename = fs.save(video.name, video)
            
            # Construct the URL for the saved video
            file_url = os.path.join(settings.MEDIA_URL, 'videos', filename)
            
            # Return the URL for use in the template
            return JsonResponse({
                'success': True,
                'file_url': file_url,
                'message': 'Video uploaded successfully'
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'No video uploaded'
            }, status=400)
            
    except Exception as e:
        print(f"Error during video upload: {e}")
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {str(e)}"
        }, status=500)

def extract_frames(video_path, frames_folder):
    """ Extract frames from a video and save them as images. """
    os.makedirs(frames_folder, exist_ok=True)
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_path = os.path.join(frames_folder, f"frame{count}.jpg")
        dehazed_frame = process_frame_with_haze_removal(image)
        cv2.imwrite(frame_path, dehazed_frame)
        success, image = vidcap.read()
        count += 1

    vidcap.release()
    return frames_folder

def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        upload_dir = 'media/uploads/'  # Adjust this path as needed
        
        # Ensure the upload directory exists
        os.makedirs(upload_dir, exist_ok=True)

        video_path = os.path.join(upload_dir, video_file.name)

        # Save the file
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        # ✅ Ensure the correct video path is returned
        return JsonResponse({"success": True, "video_path": f"/{video_path}"})

    return JsonResponse({"success": False, "error": "No video file provided"})

@csrf_exempt
def process_video(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        video_path = data.get('video_path')

        if not video_path:
            return JsonResponse({'success': False, 'error': 'No video path provided'})

        # Define input and output paths
        input_video_path = os.path.join(settings.BASE_DIR, video_path.lstrip('/'))
        
        # Create a unique name for the processed video to avoid conflicts
        video_filename = os.path.basename(input_video_path)
        output_filename = f"processed_{video_filename}"
        processed_videos_dir = os.path.join(settings.MEDIA_ROOT, 'processed_videos')
        output_video_path = os.path.join(processed_videos_dir, output_filename)

        # Ensure processed_videos directory exists
        os.makedirs(processed_videos_dir, exist_ok=True)

        try:
            # Debug information
            print(f"Input video path: {input_video_path}")
            print(f"Output video path: {output_video_path}")
            
            # Check if input file exists and is readable
            if not os.path.exists(input_video_path):
                return JsonResponse({'success': False, 'error': f'Input video file does not exist: {input_video_path}'})
                
            # Get video properties for rebuilding it later
            cap = cv2.VideoCapture(input_video_path)
            if not cap.isOpened():
                return JsonResponse({'success': False, 'error': 'Could not open video file'})
                
            # Get original video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # ===== CHANGE THIS PART =====
            # Use a browser-compatible codec - H.264 for MP4
            # 'avc1' is the H.264 codec which is widely supported in browsers
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Browser-compatible codec
            
            # Alternative options if 'avc1' doesn't work:
            # fourcc = cv2.VideoWriter_fourcc(*'H264')
            # fourcc = cv2.VideoWriter_fourcc(*'X264')
            # ===========================
            
            # Try to create a test file to ensure permissions are correct
            test_file_path = os.path.join(processed_videos_dir, "test.txt")
            try:
                with open(test_file_path, 'w') as f:
                    f.write("test")
                os.remove(test_file_path)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Permission error: Cannot write to output directory: {str(e)}'})
            
            # Setup video writer with same properties
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
            if not out.isOpened():
                # If codec fails, try using a temporary file with a different extension
                temp_output_path = output_video_path.replace('.mp4', '.avi')
                temp_fourcc = cv2.VideoWriter_fourcc(*'XVID')  # More compatible codec for temp file
                out = cv2.VideoWriter(temp_output_path, temp_fourcc, fps, (width, height))
                
                if not out.isOpened():
                    return JsonResponse({'success': False, 'error': f'Could not create output video writer. Codec issue detected.'})
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Process frame with error handling
                try:
                    processed_frame = process_frame_with_haze_removal(frame)
                    # Write directly to output video
                    out.write(processed_frame)
                except Exception as e:
                    cap.release()
                    out.release()
                    return JsonResponse({'success': False, 'error': f'Error processing frame {frame_count}: {str(e)}'})
                
                frame_count += 1
                if frame_count % 10 == 0:  # Log progress every 10 frames
                    print(f"Processed {frame_count}/{total_frames} frames")
            
            # Explicitly release resources
            cap.release()
            out.release()
            
            # If we used a temp file, convert it to browser-compatible format
            if 'temp_output_path' in locals():
                # Use ffmpeg to convert to a browser-compatible format
                import subprocess
                ffmpeg_cmd = [
                    'ffmpeg', '-i', temp_output_path, 
                    '-c:v', 'libx264', '-preset', 'fast', 
                    '-movflags', '+faststart', 
                    '-pix_fmt', 'yuv420p',
                    output_video_path
                ]
                subprocess.run(ffmpeg_cmd, check=True)
                # Remove temporary file
                os.remove(temp_output_path)
            
            # Verify the output file exists and has content
            if not os.path.exists(output_video_path):
                return JsonResponse({'success': False, 'error': 'Output file was not created'})
                
            file_size = os.path.getsize(output_video_path)
            if file_size == 0:
                return JsonResponse({'success': False, 'error': 'Output file was created but is empty (0 bytes)'})
            
            # Return path to processed video
            processed_video_url = os.path.join(settings.MEDIA_URL, 'processed_videos', output_filename)
            return JsonResponse({
                'success': True, 
                'processed_video_path': processed_video_url,
                'frames_processed': frame_count,
                'file_size': file_size
            })
            
        except Exception as e:
            import traceback
            print(f"Error processing video: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': f'Error processing video: {str(e)}'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def extract_frames(video_path, frames_folder):
    """ Extract frames from a video and save them as images. """
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_path = os.path.join(frames_folder, f"frame{count}.jpg")
        cv2.imwrite(frame_path, image)
        success, image = vidcap.read()
        count += 1

    vidcap.release()

def process_frames_with_haze_removal(frames_folder, processed_frames_folder):
    """ Process each frame with haze removal and save the processed frames. """
    frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith('.jpg')])
    
    for frame_file in frame_files:
        frame_path = os.path.join(frames_folder, frame_file)
        frame = cv2.imread(frame_path)

        # Apply haze removal to the frame
        dehazed_frame = process_frame_with_haze_removal(frame)

        # Save the processed frame
        processed_frame_path = os.path.join(processed_frames_folder, frame_file)
        cv2.imwrite(processed_frame_path, dehazed_frame)

def process_frame_with_haze_removal(frame):
    """ Apply haze removal to a single frame. """
    try:
        # Ensure frame is valid
        if frame is None or frame.size == 0:
            print("Warning: Empty frame received")
            return frame
            
        # Make a copy to avoid modifying the original
        frame_copy = frame.copy()
        
        # Convert BGR to RGB (OpenCV uses BGR by default)
        frame_rgb = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
        
        # Normalize to 0-1 range for processing
        frame_normalized = frame_rgb.astype(np.float64) / 255.0
        
        # Initialize and apply haze removal
        hr = HazeRemoval()
        hr.src = frame_normalized
        hr.rows, hr.cols, _ = hr.src.shape
        
        # Apply dehazing steps
        hr.get_dark_channel()
        hr.get_air_light()
        hr.get_transmission()
        hr.guided_filter_opencv(r=60, eps=0.001)
        hr.recover()
        
        # Optional: enhance visibility
        hr.enhance_visibility(alpha=1.5, beta=30)
        
        # Convert the result back to BGR format for OpenCV
        if np.max(hr.dst) <= 1.0:
            # If the image is still in 0-1 range, scale to 0-255
            result = (hr.dst * 255).astype(np.uint8)
        else:
            # If already in 0-255 range
            result = hr.dst.astype(np.uint8)
        
        # If the result is RGB, convert back to BGR for OpenCV compatibility
        if result.shape[2] == 3:  # Check if it has 3 channels
            result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            
        # Verify the frame is valid
        if result is None or result.size == 0:
            print("Warning: Dehazing produced an empty frame")
            return frame_copy
            
        # Ensure frame has the right dimensions
        if result.shape != frame.shape:
            print(f"Warning: Frame dimensions changed from {frame.shape} to {result.shape}")
            result = cv2.resize(result, (frame.shape[1], frame.shape[0]))
            
        return result
        
    except Exception as e:
        print(f"Error in frame processing: {str(e)}")
        # Return original frame if processing fails
        return frame

def frames_to_video(frames_folder, output_video_path, fps=30):
    """ Convert processed frames back into a video. """
    frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith('.jpg')])
    
    if not frame_files:
        return None

    first_frame = cv2.imread(os.path.join(frames_folder, frame_files[0]))
    height, width, _ = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(frames_folder, frame_file))
        out.write(frame)

    out.release()

def start_webcam(request):
    """Starts the webcam in a separate thread when the button is clicked."""
    thread = threading.Thread(target=main)  # Run `main()` in a separate thread
    thread.daemon = True  # Daemonize so it closes when Django stops
    thread.start()
    
    return JsonResponse({"status": "Webcam started"})