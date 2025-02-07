from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout, authenticate, login

from apps.account.models import User
from apps.organization.models import Organization
from django.http import HttpResponseRedirect
from django.contrib import messages


def user_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        inn = request.POST.get('inn')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        icon = request.POST.get('icon')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        user = User.objects.filter(username=inn)
        if user.exists():
            messages.warning(request, "Organization already exists!")
            return redirect('register')
        else:
            if password == password2:
                instance = User.objects.create_user(username=inn, password=password, role="Organization")
                organization = Organization.objects.create(name=name, inn=inn, district=address, icon=icon,
                                                           phone=phone_number, user=instance)
                user = authenticate(username=inn, password=password)
                if user is not None:
                    login(request, user)
                messages.success(request, 'Your account has been created!')
                return redirect('/dashboard/')
            else:
                messages.warning(request, 'Password did not match!')
                return redirect('register')

    return render(request, 'auth/register.html')


def user_login(request):
    if request.method == 'POST':
        inn = request.POST.get('inn')
        password = request.POST.get('password')
        user = authenticate(username=inn, password=password)
        # org_user = User.objects.filter(id=user.id).first()
        if user is None:
            messages.warning(request, "Login or Password is invalid")
            return HttpResponseRedirect('/auth/login/')
        organization = Organization.objects.filter(user=user).first()
        if user.role != 'Organization':
            messages.warning(request, "You are not Organization user, Please register")
            return HttpResponseRedirect('/auth/register/')

        if user.role == 'Organization' and organization:
            login(request, user)
            return HttpResponseRedirect('/dashboard/')
        else:
            messages.warning(request, "Login Error !! Phone number or Password is incorrect")
            return HttpResponseRedirect('/auth/login/')

    return render(request, 'auth/login.html')


def logout_func(request):
    logout(request)
    messages.success(request, "Please login to access the site!")
    return HttpResponseRedirect('/auth/login/')


def profile(request):
    organization = get_object_or_404(Organization, user=request.user)
    return render(request, 'auth/profile.html', {'organization': organization})
