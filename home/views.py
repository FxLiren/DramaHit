from django.shortcuts import render, redirect
from script.models import ScriptMeta  # 引入 script 的 Model

def home(request):
    # --------------------------------------------------
    # 1. 處理搜尋重定向
    # --------------------------------------------------
    query = request.GET.get('q') or request.GET.get('keyword')
    if query:
        return redirect(f"/script-list/?keyword={query}")

    # --------------------------------------------------
    # 2. 在 Home View 直接處理「不重複隨機抽劇本」
    # --------------------------------------------------
    if request.GET.get('random') == '1':
        # 取得 Session 看過的清單
        visited = request.session.get('visited_scripts', [])

        # 取出排除已看過的劇本（使用 script_db）
        unvisited = ScriptMeta.objects.using('script_db').exclude(id__in=visited)

        # 全部看過則清空 Session 重新開始
        if not unvisited.exists():
            visited = []
            unvisited = ScriptMeta.objects.using('script_db').all()

        # 若資料庫有資料則隨機抽一筆
        if unvisited.exists():
            selected = unvisited.order_by('?').first()
            visited.append(selected.id)
            request.session['visited_scripts'] = visited
            
            # 直接跳轉至 script-detail，帶入 script_id
            return redirect('script-detail', script_id=selected.id)
        
        return redirect('script-list')

    # --------------------------------------------------
    # 3. 渲染首頁輪播圖（使用 script_db）
    # --------------------------------------------------
    banners = ScriptMeta.objects.using('script_db').order_by('?')[:5]

    return render(request, 'home/home.html', {
        'banners': banners,
        'query': query or ''
    })