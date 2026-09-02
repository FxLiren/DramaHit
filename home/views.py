from django.shortcuts import render
from .models import Script

def home(request):
    # ⭕ .order_by('?') 代表每次請求都隨機排序，[:3] 取前 3 筆當輪播
    banner_scripts = Script.objects.order_by('?')[:3]
    
    # 列表維持原本的所有資料
    all_scripts = Script.objects.all()

    context = {
        'banners': banner_scripts,
        'scripts': all_scripts,
    }
    return render(request, 'home/home.html', context)