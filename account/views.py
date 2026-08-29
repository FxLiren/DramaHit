from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings


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

        # 建立會員，但先禁止登入
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        # 產生 Email 驗證 Token
        token = default_token_generator.make_token(user)

        # 產生驗證網址
        verification_url = request.build_absolute_uri(
            reverse('verify-email', args=[user.pk, token])
        )

        # 寄送驗證信
        send_mail(
            '探劇實錄｜會員 Email 驗證',
            f'''您好 {username}，

感謝您註冊「探劇實錄」。

請點擊以下連結完成 Email 驗證：

{verification_url}

完成驗證後即可登入網站。

如果這不是您本人註冊的，請忽略此郵件。

探劇實錄'''
            ,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return render(request, 'account/register.html', {
            'success': '註冊成功！請至 Email 點擊驗證連結後再登入。'
        })

    return render(request, 'account/register.html')


def verify_email(request, user_id, token):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return render(request, 'account/register.html', {
            'error': '驗證連結無效。'
        })

    if user.is_active:
        return render(request, 'account/register.html', {
            'success': '此 Email 已經完成驗證，可以直接登入。'
        })

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        return render(request, 'account/register.html', {
            'success': 'Email 驗證成功！現在可以登入了。'
        })

    return render(request, 'account/register.html', {
        'error': '驗證連結無效或已經失效。'
    })


def logout_view(request):
    logout(request)
    return redirect('home')