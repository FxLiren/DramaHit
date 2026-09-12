from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count
from django.urls import reverse

import random
import math

from script.models import ScriptMeta
from .models import Review


# ==================================================
# 取得劇本 + 評論數
# ==================================================

def get_scripts_with_review_count():

    # 從 script_db 取得劇本
    scripts = list(
        ScriptMeta.objects.using("script_db").all()
    )

    # 從 default db 取得評論數
    review_counts = {
        item["script_id"]: item["count"]
        for item in Review.objects
        .values("script_id")
        .annotate(count=Count("id"))
    }

    # 把評論數加入劇本
    for script in scripts:
        script.review_count = review_counts.get(script.id, 0)

    return scripts


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

        # 避免同一部劇本重複
        candidates.remove(chosen)

    return selected


# ==================================================
# 推薦首頁
# ==================================================

def recommendation(request):

    # ==================================================
    # 新增評論
    # ==================================================

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


    # ==================================================
    # 取得劇本
    # ==================================================

    scripts = get_scripts_with_review_count()


    # ==================================================
    # 今日推薦
    # ==================================================

    if len(scripts) <= 3:

        recommendations = scripts

    else:

        recommendations = weighted_random_scripts(
            scripts,
            3
        )


    # ==================================================
    # 熱門榜單
    # ==================================================

    rankings = sorted(
        scripts,
        key=lambda script: script.review_count,
        reverse=True
    )[:10]


    # ==================================================
    # 評論
    # ==================================================

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
# AJAX 隨機推薦
# ==================================================

def random_recommendation(request):

    # 只接受 POST
    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "只接受 POST 請求"
            },
            status=405
        )


    # ==================================================
    # 取得使用者選擇的類型
    # ==================================================

    selected_type = request.POST.get(
        "type",
        ""
    ).strip()


    # ==================================================
    # 取得全部劇本
    # ==================================================

    scripts = get_scripts_with_review_count()


    # ==================================================
    # 類型篩選
    # ==================================================

    if selected_type:

        filtered_scripts = []

        for script in scripts:

            script_type = (
                script.script_type or ""
            ).strip()

            # 例如：
            # 「推理 / 日式 / 還原 / 3票」
            # 選擇「推理」也可以找到

            if selected_type in script_type:

                filtered_scripts.append(script)

        scripts = filtered_scripts


    # ==================================================
    # 沒有符合條件
    # ==================================================

    if not scripts:

        return JsonResponse(
            {
                "success": False,
                "message": "目前沒有符合「{}」的劇本。".format(
                    selected_type
                )
            }
        )


    # ==================================================
    # 隨機選最多 3 部
    # ==================================================

    selected_scripts = weighted_random_scripts(
        scripts,
        3
    )


    # ==================================================
    # 整理 JSON
    # ==================================================

    results = []


    for script in selected_scripts:

        # ==============================================
        # 取得劇本詳細頁網址
        # ==============================================

        try:

            detail_url = reverse(
                "script-detail",
                args=[script.id]
            )

        except Exception:

            # 如果組員的 script-detail 暫時不存在
            detail_url = "#"


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

                "detail_url": detail_url,
            }
        )


    # ==================================================
    # 回傳 JSON
    # ==================================================

    return JsonResponse(
        {
            "success": True,
            "results": results
        }
    )