from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count
from django.urls import reverse  # 【修改】新增 reverse

import random
import math

from script.models import ScriptMeta
from .models import Review


def get_scripts_with_review_count():

    # 從 script_db 取得劇本
    scripts = list(
        ScriptMeta.objects.using("script_db").all()
    )

    # 取得每個劇本的評論數量
    review_counts = {
        item["script_id"]: item["count"]
        for item in Review.objects
        .values("script_id")
        .annotate(count=Count("id"))
    }

    # 把評論數量放進每個劇本
    for script in scripts:
        script.review_count = review_counts.get(script.id, 0)

    return scripts


def recommendation(request):

    # ==================================================
    # 【修改】處理評論送出
    # ==================================================
    if request.method == "POST":

        # 【修改】
        # 未登入使用者不能發表評論
        if not request.user.is_authenticated:
            return redirect("account")

        script_id = request.POST.get("script_id")
        content = request.POST.get("content")

        # 【修改】
        # 使用登入帳號名稱，不再讓使用者輸入 nickname
        nickname = request.user.get_username()

        # 【修改】
        # 取得目前資料庫中的劇本
        scripts = get_scripts_with_review_count()

        # 【修改】
        # 建立合法的劇本 ID 清單
        valid_script_ids = {
            script.id
            for script in scripts
        }

        # 【修改】
        # 檢查資料是否完整
        if (
            script_id
            and content
            and content.strip()
            and int(script_id) in valid_script_ids
        ):

            Review.objects.create(
                script_id=int(script_id),
                nickname=nickname,
                content=content.strip()
            )

        return redirect("/recommendation/")

    # ==================================================
    # 原本的劇本資料
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
    # 【修改】
    # 取得所有評論
    # ==================================================

    reviews = Review.objects.all().order_by("-created_at")

    # ==================================================
    # 【修改】
    # 建立 script_id → 劇本名稱對照表
    #
    # 因為 ScriptMeta 與 Review 在不同資料庫，
    # 所以不能直接使用 ForeignKey。
    # ==================================================

    script_name_map = {
        script.id: script.script_name
        for script in scripts
    }

    # ==================================================
    # 【修改】
    # 將劇本名稱附加到每一筆 Review
    # ==================================================

    for review in reviews:
        review.script_name = script_name_map.get(
            review.script_id,
            "未知劇本"
        )

    # ==================================================
    # Context
    # ==================================================

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


# ======================================================
# 今日推薦的加權隨機
# ======================================================

def weighted_random_scripts(scripts, amount):

    if not scripts:
        return []

    amount = min(
        amount,
        len(scripts)
    )

    selected = []

    candidates = scripts.copy()

    for _ in range(amount):

        # 評論越多，機率越高
        # 但不會差距太誇張
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

        candidates.remove(chosen)

    return selected


# ======================================================
# 隨機推薦 AJAX
# ======================================================

def random_recommendation(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "只接受 POST 請求"
            },
            status=405
        )

    selected_type = request.POST.get(
        "type",
        ""
    )

    scripts = get_scripts_with_review_count()

    # ==================================================
    # 類型篩選
    # ==================================================

    if selected_type:

        scripts = [
            script
            for script in scripts
            if selected_type in (
                script.script_type or ""
            )
        ]

    # ==================================================
    # 沒有符合的劇本
    # ==================================================

    if not scripts:

        return JsonResponse(
            {
                "success": False,
                "message": "目前沒有符合條件的劇本"
            }
        )

    # ==================================================
    # 隨機選擇
    # ==================================================

    selected_scripts = weighted_random_scripts(
        scripts,
        3
    )

    # ==================================================
    # 回傳 JSON
    # ==================================================

    results = []

    for script in selected_scripts:

        # ==================================================
        # 【修改】
        # 取得詳細頁 URL
        #
        # 如果 teammate 的 script-detail 存在，
        # 就會使用：
        #
        # /script/<id>/
        #
        # 如果不存在則使用 #
        # ==================================================

        try:
            detail_url = reverse(
                "script-detail",
                args=[script.id]
            )

        except Exception:
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

                # 【修改】
                # 提供前端詳細頁連結
                "detail_url": detail_url,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "results": results
        }
    )



