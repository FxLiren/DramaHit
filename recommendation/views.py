from django.shortcuts import render

# Create your views here.
def recommendation(request):

    recommendations = [
        {
            "title": "消失的玫瑰",
            "rating": 4.8,
            "type": "硬核推理",
        },
        {
            "title": "最後一封情書",
            "rating": 4.6,
            "type": "情感立意",
        },
        {
            "title": "午夜來客",
            "rating": 4.5,
            "type": "恐怖機關",
        },
    ]

    rankings = [
        {
            "title": "消失的玫瑰",
            "rating": 4.8,
        },
        {
            "title": "最後一封情書",
            "rating": 4.7,
        },
        {
            "title": "午夜來客",
            "rating": 4.6,
        },
        {
            "title": "時間的囚徒",
            "rating": 4.5,
        },
        {
            "title": "無人之島",
            "rating": 4.4,
        },
    ]

    return render(request, "recommendation/index.html", {
        "recommendations": recommendations,
        "rankings": rankings,
    })