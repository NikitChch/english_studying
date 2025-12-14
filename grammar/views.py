from django.shortcuts import render

def grammar(request):
    context = {
        'page_title': 'Грамматика английского языка',
        'promo_product': 'Полный курс грамматики со скидкой 20%',
    }
    
    return render(request, 'grammar.html', context)