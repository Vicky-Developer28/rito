# Portal/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('USER.urls')),  # Your main app URLs
    path('api/', include('USER.apiurls')),  # API endpoints
]

# Redirect root to main app
def root_redirect(request):
    return redirect('user:index')

urlpatterns += [
    path('', root_redirect),
]