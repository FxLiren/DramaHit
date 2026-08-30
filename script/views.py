from django.shortcuts import render
from django.core.paginator import Paginator
from .models import ScriptMeta


def script_list(request):

    # 搜尋關鍵字
    keyword = request.GET.get('keyword', '')

    # 分類
    category = request.GET.get('category', '')

    # 取得資料庫資料
    # 去除完全相同的重複劇本
    scripts = (
        ScriptMeta.objects
        .using('script_db')
        .values(
            'script_name',
            'image_url',
            'script_type',
            'players_count',
            'play_time',
            'rating'
        )
        .distinct()
    )

    # 搜尋
    if keyword:
        scripts = scripts.filter(script_name__icontains=keyword)

    # 分類
    if category and category != '全部':
        scripts = scripts.filter(script_type=category)

    # 分頁
    paginator = Paginator(scripts, 20)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(request, 'scripts/script-list.html', {
        'page_obj': page_obj,
        'keyword': keyword,
        'category': category,
    })


def script_detail(request):
    return render(request, 'scripts/script-detail.html')


def script_detail_2(request):
    return render(request, 'scripts/script-detail-2.html')