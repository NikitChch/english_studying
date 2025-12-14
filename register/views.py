from django.shortcuts import render

def register(request):
    context = {
        'page_title': 'Регистрация'
    }
    return render(request, 'register.html', context)