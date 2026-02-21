"""
Main URL configuration for akaraka project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    path('', include('users.urls', namespace='users')),
    path('courses/', include('courses.urls', namespace='courses')),
    path('exercises/', include('exercises.urls', namespace='exercises')),
    path('gamification/', include('gamification.urls', namespace='gamification')),
    path('community/', include('community.urls', namespace='community')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('certificates/', include('certificates.urls', namespace='certificates')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
