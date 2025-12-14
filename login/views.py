from django.shortcuts import render

def login_view(request):
    context = {
        'page_title': 'Вход в систему'
    }
    return render(request, 'login.html', context)