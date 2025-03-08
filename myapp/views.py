from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
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
        return render(req, 'home.html')
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
    if check_user:
        print('kua')
        return redirect('login')
    return redirect('about')

def team(req):
    check_user(req)  # Ensure user is checked
    if not req.COOKIES.get('username'):
        return redirect('login')  # Redirect if the user is not logged in
    return render(req, 'team.html')
