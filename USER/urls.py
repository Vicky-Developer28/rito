# USER/urls.py
from django.urls import path, include
from . import views
from .api import api

app_name = 'user'

urlpatterns = [
    # ===== PUBLIC PAGES =====
    path('', views.index, name='index'),
    path('SORRY/', views.sorry, name='sorry'),
    path('docs/', views.docs, name='docs'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('community-join/', views.community_join, name='community_join'),
    
    # ===== AUTHENTICATION =====
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ===== DASHBOARD & DEVICE MANAGEMENT =====
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register-device/', views.register_device_view, name='register_device'),
    path('social-account/create/', views.create_social_account, name='create_social_account'),
    path('social-account/<str:platform>/', views.account_detail, name='account_detail'),
    path('social-account/<str:platform>/delete/', views.delete_social_account, name='delete_social_account'),
    
    # ===== COMMUNITY (Quora-like) =====
    path('community/', views.community_home, name='community'),
    path('community/ask/', views.ask_question, name='ask_question'),
    path('community/question/<slug:slug>/', views.question_detail, name='question_detail'),
    path('community/question/<slug:slug>/answer/', views.post_answer, name='post_answer'),
    path('community/question/<slug:slug>/vote/<str:vote_type>/', views.vote_question, name='vote_question'),
    path('community/question/<slug:slug>/follow/', views.follow_question, name='follow_question'),
    path('community/question/<slug:slug>/bookmark/', views.bookmark_question, name='bookmark_question'),
    path('community/answer/<uuid:answer_id>/accept/', views.accept_answer, name='accept_answer'),
    path('community/member/<str:user_id>/', views.member_profile, name='member_profile'),
    path('community/topics/', views.topics, name='topics'),
    path('community/topic/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('community/topic/<slug:slug>/follow/', views.follow_topic, name='follow_topic'),
    path('community/search/', views.search, name='search'),
]

# ===== LEGACY API ENDPOINTS (for backward compatibility with ESP8266) =====
# ADD TRAILING SLASHES TO ALL API ENDPOINTS
legacy_api_patterns = [
    path('device/register/', views.device_register_api, name='device_register_api'),
    path('device/status/', views.device_status_api, name='device_status_api'),
    path('device/location/', views.device_location_api, name='device_location_api'),
    path('device/refresh-code/', views.refresh_registration_code, name='refresh_registration_code'),
]

# Add legacy endpoints to urlpatterns
urlpatterns.extend(legacy_api_patterns)