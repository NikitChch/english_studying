from django.shortcuts import render

def vocabulary(request):
    words = [
        {
            'title': 'Ubiquitous',
            'description': 'Present, appearing, or found everywhere. Something that is ubiquitous seems to be everywhere at the same time.',
            'transcription': '[juːˈbɪkwɪtəs]',
            'translation': 'вездесущий, повсеместный'
        },
        {
            'title': 'Comprehensive',
            'description': 'Complete and including everything that is necessary. A comprehensive guide or study includes all the necessary details.',
            'transcription': '[ˌkɒmprɪˈhɛnsɪv]',
            'translation': 'всесторонний, исчерпывающий'
        },
        {
            'title': 'Fluency', 
            'description': 'The ability to speak or write a language easily, well, and quickly. Language fluency indicates high proficiency.',
            'transcription': '[ˈfluːənsi]',
            'translation': 'беглость речи'
        },
        {
            'title': 'Proficiency',
            'description': 'A high degree of skill or expertise in a particular subject or activity.',
            'transcription': '[prəˈfɪʃənsi]',
            'translation': 'мастерство, умение'
        }
    ]
    
    context = {
        'words': words,
        'page_title': 'Словарь английского языка',
        'promo_product': '5000+ слов для изучения'
    }
    return render(request, 'vocabulary.html', context)