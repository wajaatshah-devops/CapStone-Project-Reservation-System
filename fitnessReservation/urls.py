from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'mainApp'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reservations/', include('reservations.urls')),
    path('accounts/', include('accounts.urls')),
    path('helpVids/', include('helpVids.urls')),
    path('', include('fitnessClass.urls'), name='home')
]

urlpatterns += staticfiles_urlpatterns()
