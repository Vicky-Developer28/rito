# USER/apiurls.py
from django.urls import path
from .api import api

app_name = 'api'

urlpatterns = [
    path('', api.urls),
]