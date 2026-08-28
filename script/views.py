from django.shortcuts import render
from django.core.paginator import Paginator
from .models import ScriptMeta


def script_list(request):
    scripts = ScriptMeta.objects.using('script_db').all()

    paginator = Paginator(scripts, 20)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(request, 'scripts/script-list.html', {
        'page_obj': page_obj
    })


def script_detail(request):
    return render(request, 'scripts/script-detail.html')


def script_detail_2(request):
    return render(request, 'scripts/script-detail-2.html')