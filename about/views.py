from django.shortcuts import render

def about(request):
    context = {
        'page_title': 'О нас - ENGLISH STUDING',
        'promo_product': 'Наша команда профессионалов'
    }
    return render(request, 'about.html', context)