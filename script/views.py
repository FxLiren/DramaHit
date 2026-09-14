from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Min
from .models import ScriptMeta, Favorite
from account.models import ViewHistory
import random


def script_list(request):

    # 搜尋關鍵字
    keyword = request.GET.get('keyword', '')

    # 分類
    category = request.GET.get('category', '')

    # 找出每個劇本名稱最小的 id
    first_ids = (
        ScriptMeta.objects
        .using('script_db')
        .values('script_name')
        .annotate(first_id=Min('id'))
        .values('first_id')
    )

    # 每個劇本只保留一筆
    scripts = (
        ScriptMeta.objects
        .using('script_db')
        .filter(id__in=first_ids)
        .order_by('id')
    )

    # 搜尋
    if keyword:
        scripts = scripts.filter(
            script_name__icontains=keyword
        )

    # 分類
    if category and category != '全部':
        scripts = scripts.filter(
            script_type__icontains=category
        )

    # 分頁
    paginator = Paginator(scripts, 20)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    for script in page_obj:
        random.seed(script.id)
        script.fake_rating = round(random.uniform(4.0, 5.0), 1)

    favorite_ids = set()

    if request.user.is_authenticated:
        favorite_ids = set(
            Favorite.objects.filter(
                user=request.user
            ).values_list('script_id', flat=True)
        )

    return render(request, 'scripts/script-list.html', {
        'page_obj': page_obj,
        'keyword': keyword,
        'category': category,
        'favorite_ids': favorite_ids,
    })


def script_detail(request, script_id):

    from_favorite = request.GET.get('from') == 'favorite'

    from_list = request.GET.get('from') == 'list'

    script = (
        ScriptMeta.objects
        .using('script_db')
        .get(id=script_id)
    )

    random.seed(script.id)
    script.fake_rating = round(random.uniform(4.0, 5.0), 1)

    is_favorite = False

    if request.user.is_authenticated:

        is_favorite = Favorite.objects.filter(
            user=request.user,
            script_id=script_id
        ).exists()

        ViewHistory.objects.update_or_create(
            user=request.user,
            script_id=script_id
        )

    return render(request, 'scripts/script-detail.html', {
        'script': script,
        'is_favorite': is_favorite,
        'from_favorite': from_favorite,
        'from_list': from_list,
        'page': request.GET.get('page', '1'),
        'keyword': request.GET.get('keyword', ''),
        'category': request.GET.get('category', '')
    })

def script_detail_2(request):
    return render(request, 'scripts/script-detail-2.html')

def toggle_favorite(request, script_id):

    if not request.user.is_authenticated:
        return redirect('account')

    favorite = Favorite.objects.filter(
        user=request.user,
        script_id=script_id
    ).first()

    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(
            user=request.user,
            script_id=script_id
        )

    return redirect(request.META.get('HTTP_REFERER', 'script-list') + '#script-' + str(script_id))

def my_favorite(request):

    if not request.user.is_authenticated:
        return redirect('account')

    favorites = Favorite.objects.filter(
        user=request.user
    )

    return render(request, 'scripts/my-favorite.html', {
        'favorites': favorites
    })