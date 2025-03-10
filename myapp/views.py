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
import time
import cv2
# Create your views here.

name = ''
mail = ''


def dirhome(req):
    return redirect('/locked')


def check_user(req):
    global name, mail
    name = req.COOKIES.get('username')  # Get username from cookies
    mail = req.COOKIES.get('useremail')  # Get email from cookies
    print(name, mail)
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
    if(category == 'image'):
        return render(req, 'image.html')
    elif(category == 'video'):
        return render(req, 'video.html')
    elif(category == 'camera'):
        return render(req, 'camera.html')
    
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        
        # Save image to the 'upload' folder
        fs = FileSystemStorage(location='media/upload')
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)
        
        # You can return the uploaded image URL for use in the template
        return render(request, 'home.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'home.html')

@csrf_exempt
def save_image(request):
    try:
        if request.method == 'POST' and request.FILES.get('image'):
            image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            file_url = fs.url(filename)

            # Image path for original image
            image_path = os.path.join(settings.MEDIA_ROOT, filename)

            # Initialize and process the image
            hr = HazeRemoval()
            hr.open_image(image_path)
            hr.get_dark_channel()
            hr.get_air_light()
            hr.get_transmission()
            hr.guided_filter_opencv(r=60, eps=0.001)
            hr.recover()
            hr.enhance_visibility(alpha=1.5, beta=30)

            # Processed image saving
            processed_image_name = f"{os.path.splitext(filename)[0]}_dehazed{os.path.splitext(filename)[1]}"
            processed_image_path = os.path.join(settings.MEDIA_ROOT, 'dehazed', processed_image_name)

            # Save processed image to 'dehazed' directory
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'dehazed')):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'dehazed'))

            cv2.imwrite(processed_image_path, hr.dst[:, :, (2, 1, 0)])  # Save in BGR format

            # Return JSON response with URLs
            processed_image_url = os.path.join(settings.MEDIA_URL, 'dehazed', processed_image_name)
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

def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video = request.FILES['video']
        fs = FileSystemStorage()
        filename = fs.save(video.name, video)
        video_url = fs.url(filename)
        return JsonResponse({'success': True, 'video_url': video_url})
    else:
        return JsonResponse({'success': False, 'error': 'No video uploaded or invalid request'})
