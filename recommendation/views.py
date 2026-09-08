from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count
import random
import math

from script.models import ScriptMeta
from .models import Review


def get_scripts_with_review_count():

    # 從 script_db 取得劇本
    scripts = list(
        ScriptMeta.objects.using("script_db").all()
    )

    # 從 default db 取得評論數量
    review_counts = {
        item["script_id"]: item["count"]
        for item in Review.objects
        .values("script_id")
        .annotate(count=Count("id"))
    }

    # 把評論數量加入劇本
    for script in scripts:
        script.review_count = review_counts.get(script.id, 0)

    return scripts


# ==================================================
# 推薦首頁
# ==================================================

def recommendation(request):

    # ==============================================
    # 新增評論
    # ==============================================

    if request.method == "POST":

        script_id = request.POST.get("script_id")
        nickname = request.POST.get("nickname")
        content = request.POST.get("content")

        if script_id and nickname and content:

            Review.objects.create(
                script_id=int(script_id),
                nickname=nickname,
                content=content
            )

        return redirect("/recommendation/")


    # ==============================================
    # 取得劇本
    # ==============================================

    scripts = get_scripts_with_review_count()


    # ==============================================
    # 今日推薦
    # ==============================================

    if len(scripts) <= 3:

        recommendations = scripts

    else:

        recommendations = weighted_random_scripts(
            scripts,
            3
        )


    # ==============================================
    # 熱門榜單
    # ==============================================

    rankings = sorted(
        scripts,
        key=lambda script: script.review_count,
        reverse=True
    )[:10]


    # ==============================================
    # 評論
    # ==============================================

    reviews = Review.objects.all().order_by("-created_at")


    context = {

        "recommendations": recommendations,

        "rankings": rankings,

        "reviews": reviews,

        "scripts": scripts,

    }


    return render(
        request,
        "recommendation/index.html",
        context
    )


# ==================================================
# 評論數加權隨機
# ==================================================

def weighted_random_scripts(scripts, amount):

    if not scripts:
        return []

    amount = min(amount, len(scripts))

    selected = []

    candidates = scripts.copy()

    for _ in range(amount):

        # 權重：
        #
        # 評論 0 → 1
        # 評論 1 → 2
        # 評論 4 → 3
        # 評論 9 → 4
        # 評論 100 → 11
        #
        # 使用 sqrt 避免評論很多的劇本
        # 完全壟斷推薦

        weights = [
            math.sqrt(script.review_count) + 1
            for script in candidates
        ]

        chosen = random.choices(
            candidates,
            weights=weights,
            k=1
        )[0]

        selected.append(chosen)

        # 移除已選擇的劇本
        # 避免同一部出現兩次
        candidates.remove(chosen)

    return selected


# ==================================================
# AJAX 隨機推薦
# ==================================================

def random_recommendation(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "只接受 POST 請求"
            },
            status=405
        )


    # ==============================================
    # 取得類型
    # ==============================================

    selected_type = request.POST.get(
        "type",
        ""
    )


    # ==============================================
    # 取得所有劇本
    # ==============================================

    scripts = get_scripts_with_review_count()


    # ==============================================
    # 如果有選擇類型
    # ==============================================

    if selected_type:

        scripts = [
            script
            for script in scripts
            if selected_type in (script.script_type or "")
        ]


    # ==============================================
    # 沒有劇本
    # ==============================================

    if not scripts:

        return JsonResponse(
            {
                "success": False,
                "message": "目前沒有符合條件的劇本"
            }
        )


    # ==============================================
    # 隨機選 3 部
    # ==============================================

    selected_scripts = weighted_random_scripts(
        scripts,
        3
    )


    # ==============================================
    # 整理 JSON
    # ==============================================

    results = []

    for script in selected_scripts:

        results.append(
            {
                "id": script.id,

                "name": script.script_name,

                "image": script.image_url,

                "type": script.script_type,

                "players": script.players_count,

                "play_time": script.play_time,

                "description": script.description,

                "review_count": script.review_count,
            }
        )


    return JsonResponse(
        {
            "success": True,

            "results": results
        }
    )