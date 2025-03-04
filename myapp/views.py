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
    mail = req.COOKIES.get('email')  # Get email from cookies

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
            if (User.objects.filter(Name=name).exists()):
                return render(req, 'login.html', {'active': 'register', 'error': 'The UserName is already Taken'})

            if (User.objects.filter(Mail=mail).exists()):
                return render(req, 'login.html', {'active': 'register', 'error': 'The UserEmail is already Taken'})

            data = User()
            data.Name = name
            data.Mail = mail
            data.Password = make_password(req.POST.get('password'))
            data.save()
            return render(req, 'login.html', {'success': 'User Registartion was successful'})
        print('Registered Failure')
    return render(req, 'login.html')


def login(req):
    if(req.COOKIES.get('username')):
        return render(req, 'home.html')
    if (req.method == "POST"):
        print("kumar")
        mail = req.POST.get('email')

        password = req.POST.get('password')
        data = User.objects.filter(Mail=mail).first()
        if data:
            if check_password(password, data.Password):
                res = render(req, 'home.html', {
                    'username': data.Name,
                    'email': data.Mail
                })

                res.set_cookie('username', data.Name, max_age=6 * 60 * 60)
                res.set_cookie('useremail', data.Mail, max_age=6 * 60 * 60)

                return res
            return render(req, 'login.html', {'error': 'Passowrd was Incorrect'})
        return render(req, 'login.html', {'error': 'UserMail was not registered'})
    return render(req, 'login.html')

def logout(req):
    global name, mail
    name = ''
    mail = ''

    res = redirect('login')
    res.delete_cookie('username')
    res.delete_cookie('useremail')
    return res
