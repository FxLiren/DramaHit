from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, 'account/account.html', {
            'error': '帳號或密碼錯誤。'
        })

    return render(request, 'account/account.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'account/register.html', {
                'error': '兩次輸入的密碼不一致。'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'account/register.html', {
                'error': '此帳號已經被註冊。'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'account/register.html', {
                'error': '此 Email 已經被註冊。'
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return render(request, 'account/register.html', {
            'success': '註冊成功！'
        })

    return render(request, 'account/register.html')

def logout_view(request):
    logout(request)
    return redirect('home')