from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # API Keys for AI services
    elevenlabs_api_key = models.CharField(max_length=255, blank=True, null=True)
    groq_api_key = models.CharField(max_length=255, blank=True, null=True)
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_translate_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_tts_api_key = models.CharField(max_length=255, blank=True, null=True)
    
    # User preferences
    preferred_voice_speed = models.CharField(
        max_length=10,
        choices=[
            ('fast', 'Fast'),
            ('normal', 'Normal'),
            ('slow', 'Slow'),
        ],
        default='normal'
    )
    
    preferred_tts_service = models.CharField(
        max_length=20,
        choices=[
            ('browser', 'Browser TTS'),
            ('google', 'Google TTS (Free)'),
            ('google_cloud', 'Google Cloud TTS'),
            ('elevenlabs', 'ElevenLabs AI'),
        ],
        default='google'
    )
    
    preferred_translation_service = models.CharField(
        max_length=20,
        choices=[
            ('auto', 'Auto (Best Available)'),
            ('groq', 'Groq AI'),
            ('google', 'Google Translate'),
            ('basic', 'Basic Dictionary'),
        ],
        default='auto'
    )
    
    # Usage tracking
    daily_character_usage = models.IntegerField(default=0)
    last_usage_date = models.DateField(auto_now=True)
    total_characters_used = models.IntegerField(default=0)
    
    # Profile info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def can_use_ai_services(self):
        """Check if user has API keys for AI services"""
        return bool(self.elevenlabs_api_key or self.groq_api_key or self.google_translate_api_key or self.google_tts_api_key)
    
    def reset_daily_usage_if_needed(self):
        """Reset daily usage counter if it's a new day"""
        from datetime import date
        if self.last_usage_date < date.today():
            self.daily_character_usage = 0
            self.last_usage_date = date.today()
            self.save()

class StudyHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_history')
    
    # Study content
    english_text = models.TextField()
    korean_translation = models.TextField(blank=True)
    target_language = models.CharField(max_length=10, default='ko')  # Language code
    source_language = models.CharField(max_length=10, default='auto')  # Source language code
    
    # Usage info  
    tts_service_used = models.CharField(max_length=20, blank=True)
    voice_speed_used = models.CharField(max_length=10, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    accessed_count = models.IntegerField(default=1)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username}: {self.english_text[:50]}..."
