from django.shortcuts import render
import random


# ==========================================
# 假資料
# ==========================================

SCRIPTS = [
    {
        "id": 1,
        "title": "消失的玫瑰",
        "rating": 4.8,
        "type": "推理",
        "summary": "一場看似普通的聚會，卻藏著一個無法解開的謎團。",
        "reviews": [
            {
                "user": "小明",
                "rating": 5,
                "content": "推理線索很多，非常好玩！"
            },
            {
                "user": "小華",
                "rating": 4,
                "content": "故事很完整，但有些地方比較難。"
            },
            {
                "user": "小美",
                "rating": 5,
                "content": "最後的反轉很精彩。"
            }
        ]
    },

    {
        "id": 2,
        "title": "最後一封情書",
        "rating": 4.6,
        "type": "情感",
        "summary": "一封多年以前留下的信，讓所有人的關係重新交錯。",
        "reviews": [
            {
                "user": "阿杰",
                "rating": 5,
                "content": "很吃角色感情，代入感很強。"
            },
            {
                "user": "小安",
                "rating": 4,
                "content": "故事很好，很有代入感。"
            }
        ]
    },

    {
        "id": 3,
        "title": "午夜來客",
        "rating": 4.5,
        "type": "恐怖",
        "summary": "午夜十二點，一名不應該出現的人敲響了房門。",
        "reviews": [
            {
                "user": "阿鬼",
                "rating": 5,
                "content": "氣氛營造得非常棒！"
            },
            {
                "user": "小林",
                "rating": 3,
                "content": "有幾個地方真的被嚇到。"
            }
        ]
    },

    {
        "id": 4,
        "title": "歡樂大冒險",
        "rating": 4.3,
        "type": "歡樂",
        "summary": "一群朋友展開一場充滿笑料的荒唐冒險。",
        "reviews": [
            {
                "user": "阿明",
                "rating": 5,
                "content": "整場一直笑，非常適合朋友一起玩。"
            },
            {
                "user": "阿華",
                "rating": 4,
                "content": "氣氛很好，很適合第一次玩劇本殺的人。"
            }
        ]
    },

    {
        "id": 5,
        "title": "誰才是敵人",
        "rating": 4.7,
        "type": "陣營",
        "summary": "六名玩家各自隱藏著不同的目的，你能找到真正的敵人嗎？",
        "reviews": [
            {
                "user": "小王",
                "rating": 5,
                "content": "陣營對抗非常刺激。"
            },
            {
                "user": "小陳",
                "rating": 4,
                "content": "很適合喜歡互相猜疑的人。"
            }
        ]
    },

    {
        "id": 6,
        "title": "時間機關",
        "rating": 4.4,
        "type": "機制",
        "summary": "時間不斷倒流，你必須利用遊戲機制找出真相。",
        "reviews": [
            {
                "user": "阿凱",
                "rating": 5,
                "content": "機制非常有創意。"
            },
            {
                "user": "小婷",
                "rating": 4,
                "content": "第一次玩可能需要一點時間理解。"
            }
        ]
    }
]


# ==========================================
# 推薦首頁
# ==========================================

def recommendation(request):

    # -----------------------------
    # 搜尋
    # -----------------------------

    query = request.GET.get("q", "").strip()

    # -----------------------------
    # 選擇劇本類型
    # -----------------------------

    selected_type = request.GET.get("type", "").strip()

    # -----------------------------
    # 評論排序方式
    # -----------------------------

    review_sort = request.GET.get("review_sort", "high")


    # ==========================================
    # 搜尋結果
    # ==========================================

    filtered_scripts = SCRIPTS

    if query:

        filtered_scripts = [
            script
            for script in filtered_scripts

            if query.lower() in script["title"].lower()
            or query.lower() in script["summary"].lower()
            or query.lower() in script["type"].lower()
        ]


    # ==========================================
    # 類型篩選
    # ==========================================

    if selected_type:

        filtered_scripts = [
            script
            for script in filtered_scripts

            if script["type"] == selected_type
        ]


    # ==========================================
    # 熱門排行榜
    # 評分由高到低
    # ==========================================

    rankings = sorted(
        SCRIPTS,
        key=lambda script: script["rating"],
        reverse=True
    )[:5]


    # ==========================================
    # 今日推薦
    # 隨機選 3 本
    # ==========================================

    if len(SCRIPTS) >= 3:

        recommendations = random.sample(SCRIPTS, 3)

    else:

        recommendations = SCRIPTS


    # ==========================================
    # 類型隨機推薦
    # ==========================================

    random_script = None

    if selected_type and not query:

        type_scripts = [
            script
            for script in SCRIPTS
            if script["type"] == selected_type
        ]

        if type_scripts:

            random_script = random.choice(type_scripts)


    # ==========================================
    # 評論排序
    # ==========================================

    for script in SCRIPTS:

        if review_sort == "high":

            script["reviews"] = sorted(
                script["reviews"],
                key=lambda review: review["rating"],
                reverse=True
            )

        elif review_sort == "low":

            script["reviews"] = sorted(
                script["reviews"],
                key=lambda review: review["rating"]
            )


    # ==========================================
    # 劇本類型
    # ==========================================

    types = [
        "推理",
        "情感",
        "恐怖",
        "歡樂",
        "陣營",
        "機制"
    ]


    # ==========================================
    # 傳送資料給 HTML
    # ==========================================

    context = {

        "recommendations": recommendations,

        "rankings": rankings,

        "scripts": filtered_scripts,

        "types": types,

        "selected_type": selected_type,

        "random_script": random_script,

        "query": query,

        "review_sort": review_sort,
    }


    return render(
        request,
        "recommendation/index.html",
        context
    )