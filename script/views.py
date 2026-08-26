from django.shortcuts import render

# Create your views here.


def script_list(request):
    return render(request, 'scripts/script-list.html')

def script_detail(request):
    return render(request, 'scripts/script-detail.html')

def script_detail_2(request):
    return render(request, 'scripts/script-detail-2.html')