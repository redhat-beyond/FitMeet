from django.shortcuts import render

def static_home_page(request):
    return render(request, 'home_page/index.html')
