from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.http import HttpResponse

def login(request):
    return render(request, 'login.html')


def login_view(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        print('post uname' + username)

        password = request.POST.get('password')
        print('post pass' + password)

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            return HttpResponse('success')
        else:
            return HttpResponse('failed')
    else:
        return redirect("choices_list")