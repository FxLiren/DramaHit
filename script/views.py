from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Min
from .models import ScriptMeta


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

    return render(request, 'scripts/script-list.html', {
        'page_obj': page_obj,
        'keyword': keyword,
        'category': category,
    })


def script_detail(request, script_id):

    script = (
        ScriptMeta.objects
        .using('script_db')
        .get(id=script_id)
    )

    return render(request, 'scripts/script-detail.html', {
        'script': script
    })


def script_detail_2(request):
    return render(request, 'scripts/script-detail-2.html')