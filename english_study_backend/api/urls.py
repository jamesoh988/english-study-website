from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.user_login, name='user_login'),
    path('auth/register/', views.user_register, name='user_register'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    
    # TTS and Translation services
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
    path('translate/', views.translate_text, name='translate_text'),
    
    # Study History management
    path('study/history/', views.get_study_history, name='get_study_history'),
    path('study/save/', views.save_study_item, name='save_study_item'),
    path('study/delete-all/', views.delete_all_study_history, name='delete_all_study_history'),
    path('study/delete-selected/', views.delete_study_history_items, name='delete_study_history_items'),
]