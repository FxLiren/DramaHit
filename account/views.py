from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from .models import ViewHistory
from script.models import ScriptMeta
import re


def account(request):

    if request.user.is_authenticated:
        return redirect('member-center')

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
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # 帳號格式檢查
        if not re.fullmatch(r'[A-Za-z0-9_]{3,20}', username):
            return render(request, 'account/register.html', {
                'error': '帳號格式錯誤。',
                'username': username,
                'email': email,
            })

        # Email 格式檢查
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'account/register.html', {
                'error': '請輸入正確格式的 Email 地址。',
                'username': username,
                'email': email,
            })

        # 密碼確認
        if password != confirm_password:
            return render(request, 'account/register.html', {
                'error': '兩次輸入的密碼不一致。',
                'username': username,
                'email': email,
            })

        # Django 密碼驗證
        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, 'account/register.html', {
                'error': e.messages,
                'username': username,
                'email': email,
            })

        # 帳號是否已存在
        if User.objects.filter(username=username).exists():
            return render(request, 'account/register.html', {
                'error': '此帳號已經被註冊。',
                'username': username,
                'email': email,
            })

        # Email 是否已存在
        if User.objects.filter(email=email).exists():
            return render(request, 'account/register.html', {
                'error': '此 Email 已經被註冊。',
                'username': username,
                'email': email,
            })

        # 建立會員，但先禁止登入
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        try:
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

探劇實錄''',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

        except Exception:
            # 如果寄信失敗，刪除剛建立的會員
            user.delete()

            return render(request, 'account/register.html', {
                'error': '驗證信寄送失敗，請稍後再試。',
                'username': username,
                'email': email,
            })

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

        return redirect('account')

    return render(request, 'account/register.html', {
        'error': '驗證連結無效或已經失效。'
    })


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def member_center(request):
    return render(request, 'account/member_center.html')


@login_required
def history_view(request):

    histories = ViewHistory.objects.filter(
        user=request.user
    )

    script_ids = [
        history.script_id
        for history in histories
    ]

    scripts = (
        ScriptMeta.objects
        .using('script_db')
        .filter(id__in=script_ids)
    )

    script_map = {
        script.id: script
        for script in scripts
    }

    history_list = []

    for history in histories:

        script = script_map.get(history.script_id)

        if script:
            history_list.append({
                'script': script,
                'viewed_at': history.viewed_at,
            })

    return render(request, 'account/history.html', {
        'history_list': history_list
    })


@login_required
def clear_history(request):
    if request.method == 'POST':
        ViewHistory.objects.filter(
            user=request.user
        ).delete()

    return redirect('history')