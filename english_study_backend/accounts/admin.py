from django.contrib import admin
from .models import UserProfile, StudyHistory

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_tts_service', 'daily_character_usage', 'total_characters_used', 'can_use_ai_services', 'created_at']
    list_filter = ['preferred_tts_service', 'preferred_voice_speed', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('API Keys', {
            'fields': ('elevenlabs_api_key', 'groq_api_key', 'openai_api_key'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('preferred_voice_speed', 'preferred_tts_service')
        }),
        ('Usage Tracking', {
            'fields': ('daily_character_usage', 'total_characters_used', 'last_usage_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(StudyHistory)
class StudyHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'english_text_preview', 'tts_service_used', 'voice_speed_used', 'accessed_count', 'created_at']
    list_filter = ['tts_service_used', 'voice_speed_used', 'created_at']
    search_fields = ['user__username', 'english_text', 'korean_translation']
    readonly_fields = ['created_at', 'last_accessed']
    
    def english_text_preview(self, obj):
        return obj.english_text[:50] + "..." if len(obj.english_text) > 50 else obj.english_text
    english_text_preview.short_description = 'English Text'
