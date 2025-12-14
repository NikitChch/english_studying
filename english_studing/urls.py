from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse

def ignore_chrome_devtools(request):
    return HttpResponse(status=204)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('courses/', include('courses.urls', namespace='courses')),
    path('grammar/', include('grammar.urls')),
    path('vocabulary/', include('vocabulary.urls')),
    path('about/', include('about.urls')),
    path('contacts/', include('contacts.urls')),
    path('users/', include('users.urls', namespace='users')), 
    path('profil/', include('profil.urls')),
    path('diary/', include('diary.urls')),
    path('feedback/', include('feedback.urls')),
    path('login/', RedirectView.as_view(url='/users/login/', permanent=True)),
    path('register/', RedirectView.as_view(url='/users/register/', permanent=True)),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)