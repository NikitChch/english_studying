from django.shortcuts import render

def contacts(request):
    context = {
        'page_title': 'Контакты',
        'promo_product': 'Свяжитесь с нами'
    }
    return render(request, 'contacts.html', context)