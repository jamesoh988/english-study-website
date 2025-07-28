from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from accounts.models import UserProfile
import json
import requests
import base64

@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
        
        print(f"Login attempt - Username: {username}")
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            print(f"Login successful for user: {username}")
            
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                print(f"Created new profile for user: {username}")
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': f'token_{user.id}',  # Simple token for demo
                'profile': {
                    'can_use_ai': profile.can_use_ai_services(),
                    'has_elevenlabs_key': bool(profile.elevenlabs_api_key),
                    'has_groq_key': bool(profile.groq_api_key),
                    'preferred_voice_speed': profile.preferred_voice_speed,
                    'preferred_tts_service': profile.preferred_tts_service,
                    'daily_usage': profile.daily_character_usage,
                    'total_usage': profile.total_characters_used,
                }
            })
        else:
            print(f"Login failed for user: {username}")
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Login error: {e}")
        return JsonResponse({'error': 'Login failed'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def user_register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return JsonResponse({'error': 'All fields required'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'token': 'dummy_token',
            'message': 'User created successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Registration error: {e}")
        return JsonResponse({'error': 'Registration failed'}, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT"])
def user_profile(request):
    # Simple authentication check - in real app, use proper token authentication
    user_id = request.headers.get('Authorization', '').replace('Token token_', '')
    if not user_id.isdigit():
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        user = User.objects.get(id=int(user_id))
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            return JsonResponse({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'profile': {
                    'can_use_ai': profile.can_use_ai_services(),
                    'has_elevenlabs_key': bool(profile.elevenlabs_api_key),
                    'has_groq_key': bool(profile.groq_api_key),
                    'has_google_key': bool(profile.google_translate_api_key),
                    'has_google_tts_key': bool(profile.google_tts_api_key),
                    'preferred_voice_speed': profile.preferred_voice_speed,
                    'preferred_tts_service': profile.preferred_tts_service,
                    'preferred_translation_service': profile.preferred_translation_service,
                    'daily_usage': profile.daily_character_usage,
                    'total_usage': profile.total_characters_used,
                    'elevenlabs_api_key': profile.elevenlabs_api_key or '',
                    'groq_api_key': profile.groq_api_key or '',
                    'google_translate_api_key': profile.google_translate_api_key or '',
                    'google_tts_api_key': profile.google_tts_api_key or '',
                }
            })
        
        elif request.method == 'PUT':
            # Update profile settings
            data = json.loads(request.body)
            
            if 'elevenlabs_api_key' in data:
                profile.elevenlabs_api_key = data['elevenlabs_api_key']
            if 'groq_api_key' in data:
                profile.groq_api_key = data['groq_api_key']
            if 'google_translate_api_key' in data:
                profile.google_translate_api_key = data['google_translate_api_key']
            if 'google_tts_api_key' in data:
                profile.google_tts_api_key = data['google_tts_api_key']
            if 'preferred_tts_service' in data:
                profile.preferred_tts_service = data['preferred_tts_service']
            if 'preferred_voice_speed' in data:
                profile.preferred_voice_speed = data['preferred_voice_speed']
            if 'preferred_translation_service' in data:
                profile.preferred_translation_service = data['preferred_translation_service']
                
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully',
                'profile': {
                    'can_use_ai': profile.can_use_ai_services(),
                    'has_elevenlabs_key': bool(profile.elevenlabs_api_key),
                    'has_groq_key': bool(profile.groq_api_key),
                    'has_google_key': bool(profile.google_translate_api_key),
                    'has_google_tts_key': bool(profile.google_tts_api_key),
                    'preferred_voice_speed': profile.preferred_voice_speed,
                    'preferred_tts_service': profile.preferred_tts_service,
                    'preferred_translation_service': profile.preferred_translation_service,
                }
            })
            
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Profile error: {e}")
        return JsonResponse({'error': 'Profile operation failed'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_study_history(request):
    # Simple authentication check
    user_id = request.headers.get('Authorization', '').replace('Token token_', '')
    if not user_id.isdigit():
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        from accounts.models import StudyHistory
        user = User.objects.get(id=int(user_id))
        
        # Get user's study history from DB
        history_items = StudyHistory.objects.filter(user=user).order_by('-created_at')[:50]
        
        history_data = []
        for item in history_items:
            history_data.append({
                'id': int(item.created_at.timestamp() * 1000),  # Convert to JS timestamp
                'text': item.english_text,
                'translation': item.korean_translation,
                'target_language': item.target_language,
                'source_language': getattr(item, 'source_language', 'auto'),  # Safe access for backward compatibility
                'date': item.created_at.strftime('%m/%d/%Y, %I:%M:%S %p'),
                'tts_service': item.tts_service_used,
                'voice_speed': item.voice_speed_used,
                'accessed_count': item.accessed_count
            })
        
        print(f"Loading {len(history_data)} study history items for user {user.username}")
        
        return JsonResponse({
            'success': True,
            'history': history_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        print(f"Study history error: {e}")
        return JsonResponse({'error': 'Failed to load study history'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_study_item(request):
    try:
        print(f"Save study item request body: {request.body}")
        data = json.loads(request.body)
        print(f"Parsed data: {data}")
        text = data.get('text', '')
        translation = data.get('translation', '')
        target_language = data.get('target_language', 'ko')
        source_language = data.get('source_language', 'auto')
        tts_service = data.get('tts_service', '')
        voice_speed = data.get('voice_speed', 'normal')
        
        if not text:
            print(f"Error: Text is empty - received: '{text}'")
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        # Check if user is authenticated
        user_id = request.headers.get('Authorization', '').replace('Token token_', '')
        if user_id.isdigit():
            try:
                from accounts.models import StudyHistory
                user = User.objects.get(id=int(user_id))
                
                # Check if this text already exists for this user
                existing_item = StudyHistory.objects.filter(
                    user=user, 
                    english_text=text
                ).first()
                
                if existing_item:
                    # Update existing item
                    existing_item.korean_translation = translation
                    existing_item.target_language = target_language
                    existing_item.source_language = source_language
                    existing_item.tts_service_used = tts_service
                    existing_item.voice_speed_used = voice_speed
                    existing_item.accessed_count += 1
                    existing_item.save()
                    
                    print(f"Updated existing study item for user {user.username}: {text[:50]}...")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Study item updated in database',
                        'item_id': int(existing_item.created_at.timestamp() * 1000)
                    })
                else:
                    # Create new item
                    study_item = StudyHistory.objects.create(
                        user=user,
                        english_text=text,
                        korean_translation=translation,
                        target_language=target_language,
                        source_language=source_language,
                        tts_service_used=tts_service,
                        voice_speed_used=voice_speed
                    )
                    
                    print(f"Saved new study item for user {user.username}: {text[:50]}...")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Study item saved to database',
                        'item_id': int(study_item.created_at.timestamp() * 1000)
                    })
                    
            except User.DoesNotExist:
                pass
        
        # Guest user - return success but let frontend handle localStorage
        print(f"Guest user study save request: {text[:50]}...")
        return JsonResponse({
            'success': True,
            'message': 'Use localStorage for guest users',
            'guest': True
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Save study item error: {e}")
        return JsonResponse({'error': 'Failed to save study item'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_all_study_history(request):
    """Delete all study history for the authenticated user"""
    try:
        # Check if user is authenticated
        user_id = request.headers.get('Authorization', '').replace('Token token_', '')
        if not user_id.isdigit():
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            from accounts.models import StudyHistory
            user = User.objects.get(id=int(user_id))
            
            # Delete all study history for this user
            deleted_count, _ = StudyHistory.objects.filter(user=user).delete()
            
            print(f"Deleted {deleted_count} study history items for user {user.username}")
            
            return JsonResponse({
                'success': True,
                'message': f'Deleted {deleted_count} study records',
                'deleted_count': deleted_count
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
            
    except Exception as e:
        print(f"Delete study history error: {e}")
        return JsonResponse({'error': 'Failed to delete study history'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_study_history_items(request):
    """Delete specific study history items by ID for the authenticated user"""
    try:
        # Check if user is authenticated
        user_id = request.headers.get('Authorization', '').replace('Token token_', '')
        if not user_id.isdigit():
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            data = json.loads(request.body)
            item_ids = data.get('item_ids', [])
            
            if not item_ids:
                return JsonResponse({'error': 'No item IDs provided'}, status=400)
            
            from accounts.models import StudyHistory
            user = User.objects.get(id=int(user_id))
            
            # Convert timestamp IDs back to datetime for querying
            import datetime
            deleted_count = 0
            for item_id in item_ids:
                try:
                    # Convert JS timestamp (milliseconds) to datetime
                    timestamp = datetime.datetime.fromtimestamp(int(item_id) / 1000)
                    # Find item by user and approximate timestamp (within 1 second)
                    items = StudyHistory.objects.filter(
                        user=user,
                        created_at__range=[
                            timestamp - datetime.timedelta(seconds=1),
                            timestamp + datetime.timedelta(seconds=1)
                        ]
                    )
                    deleted_count += items.count()
                    items.delete()
                except (ValueError, StudyHistory.DoesNotExist):
                    continue
            
            print(f"Deleted {deleted_count} selected study history items for user {user.username}")
            
            return JsonResponse({
                'success': True,
                'message': f'Deleted {deleted_count} selected study records',
                'deleted_count': deleted_count
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Delete selected study history error: {e}")
        return JsonResponse({'error': 'Failed to delete selected study history'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def text_to_speech(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        speed = data.get('speed', 'normal')
        service = data.get('service', 'google')
        source_language = data.get('source_language', 'auto')  # Get source language for TTS
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        # Auto-detect language for TTS if not specified
        if source_language == 'auto':
            detected_lang = detect_text_language(text)
            source_language = detected_lang or 'en'  # Default to English if detection fails
        
        print(f"TTS Request - Text: '{text}', Language: {source_language}, Service: {service}, Speed: {speed}")
        
        # Check if user is authenticated and has API keys
        user_id = request.headers.get('Authorization', '').replace('Token token_', '')
        if user_id.isdigit():
            try:
                user = User.objects.get(id=int(user_id))
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                print(f"User: {user.username}, Has ElevenLabs: {bool(profile.elevenlabs_api_key)}")
                print(f"User preferred TTS service: {profile.preferred_tts_service}, Requested service: {service}")
                
                # Determine the actual service to use
                actual_service = service
                if service == 'auto':
                    actual_service = profile.preferred_tts_service or 'auto'
                    print(f"Auto mode - using preferred TTS service: {actual_service}")
                
                # Use ElevenLabs API if available and requested
                if profile.elevenlabs_api_key and (actual_service == 'elevenlabs' or (actual_service == 'auto' and profile.elevenlabs_api_key)):
                    try:
                        audio_data = call_elevenlabs_api(text, profile.elevenlabs_api_key, speed)
                        if audio_data:
                            return JsonResponse({
                                'success': True,
                                'service': 'elevenlabs',
                                'audio_data': audio_data,
                                'message': 'ElevenLabs TTS generated successfully'
                            })
                    except Exception as e:
                        print(f"ElevenLabs API error: {e}")
                        # Continue to try next service
                
                # Use Google Cloud TTS API if available and requested
                if profile.google_tts_api_key and (actual_service == 'google_cloud' or (actual_service == 'auto' and profile.google_tts_api_key and not profile.elevenlabs_api_key)):
                    try:
                        audio_data = call_google_cloud_tts_api(text, profile.google_tts_api_key, speed, source_language)
                        if audio_data:
                            return JsonResponse({
                                'success': True,
                                'service': 'google_cloud',
                                'audio_data': audio_data,
                                'message': 'Google Cloud TTS generated successfully'
                            })
                    except Exception as e:
                        print(f"Google Cloud TTS API error: {e}")
                        # Continue to try next service
                
                # Use Groq API if available and requested (placeholder - not implemented yet)
                if profile.groq_api_key and (actual_service == 'groq'):
                    try:
                        audio_data = call_groq_tts_api(text, profile.groq_api_key, speed)
                        if audio_data:
                            return JsonResponse({
                                'success': True,
                                'service': 'groq',
                                'audio_data': audio_data,
                                'message': 'Groq TTS generated successfully'
                            })
                    except Exception as e:
                        print(f"Groq API error: {e}")
                        # Continue to try next service
                
                # Fallback to Google TTS via Django proxy (to avoid CORS)
                try:
                    audio_data = call_google_tts_api(text, speed, source_language)
                    if audio_data:
                        return JsonResponse({
                            'success': True,
                            'service': 'google',
                            'audio_data': audio_data,
                            'message': f'Using Google TTS via proxy (User has: ElevenLabs={bool(profile.elevenlabs_api_key)}, Groq={bool(profile.groq_api_key)})'
                        })
                except Exception as e:
                    print(f"Google TTS proxy error: {e}")
                
                # Final fallback - return URL for browser TTS
                return JsonResponse({
                    'success': True,
                    'service': 'browser',
                    'use_browser_tts': True,
                    'message': 'Use browser TTS fallback'
                })
                
            except User.DoesNotExist:
                pass
        
        # Guest user - try Google TTS via proxy
        try:
            audio_data = call_google_tts_api(text, speed)
            if audio_data:
                return JsonResponse({
                    'success': True,
                    'service': 'google',
                    'audio_data': audio_data,
                    'message': 'Using Google TTS for guest user'
                })
        except Exception as e:
            print(f"Guest Google TTS error: {e}")
        
        # Final fallback for guests - browser TTS
        return JsonResponse({
            'success': True,
            'service': 'browser',
            'use_browser_tts': True,
            'message': 'Use browser TTS for guest'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"TTS error: {e}")
        return JsonResponse({'error': 'TTS failed'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def translate_text(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        service = data.get('service', 'auto')  # auto, groq, google
        target_language = data.get('target_language', 'ko')  # default to Korean
        source_language = data.get('source_language', 'auto')  # default to auto-detect
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        print(f"Translation request - Text: '{text}', From: {source_language}, To: {target_language}, Service: {service}")
        
        # Check if user is authenticated for premium services
        user_id = request.headers.get('Authorization', '').replace('Token token_', '')
        if user_id.isdigit():
            try:
                user = User.objects.get(id=int(user_id))
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                print(f"User: {user.username}, Has Groq: {bool(profile.groq_api_key)}, Has Google: {bool(profile.google_translate_api_key)}")
                print(f"User preferred service: {profile.preferred_translation_service}, Requested service: {service}")
                
                # Determine the actual service to use
                actual_service = service
                if service == 'auto':
                    actual_service = profile.preferred_translation_service or 'auto'
                    print(f"Auto mode - using preferred service: {actual_service}")
                
                # Use Groq API if requested and available
                if profile.groq_api_key and (actual_service == 'groq' or (actual_service == 'auto' and profile.groq_api_key)):
                    try:
                        translation = call_groq_translation_api(text, profile.groq_api_key, target_language, source_language)
                        if translation:
                            return JsonResponse({
                                'success': True,
                                'service': 'groq',
                                'translation': translation
                            })
                    except Exception as e:
                        print(f"Groq translation error: {e}")
                        # Continue to try next service
                
                # Use user's Google Translate API if requested and available
                if profile.google_translate_api_key and (actual_service == 'google' or (actual_service == 'auto' and profile.google_translate_api_key)):
                    try:
                        translation = call_official_google_translate_api(text, profile.google_translate_api_key, target_language, source_language)
                        if translation:
                            return JsonResponse({
                                'success': True,
                                'service': 'google_official',
                                'translation': translation
                            })
                    except Exception as e:
                        print(f"Official Google translation error: {e}")
                        # Continue to free Google API
                        
            except User.DoesNotExist:
                pass
        
        # Try Google Translate API (for guests or fallback)
        try:
            translation = handle_google_translation(text, target_language, source_language)
            if translation:
                return JsonResponse({
                    'success': True,
                    'service': 'google',
                    'translation': translation
                })
        except Exception as e:
            print(f"Google translation error: {e}")
        
        # Fallback to basic dictionary translation
        return JsonResponse({
            'success': True,
            'service': 'basic',
            'translation': get_basic_translation(text),
            'message': 'Using basic translation dictionary'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Translation error: {e}")
        return JsonResponse({'error': 'Translation failed'}, status=500)

def handle_google_translation(text, target_language='ko', source_language='auto'):
    """Use free Google Translate API (for guests or fallback)"""
    # Use free Google Translate API
    try:
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        
        response = requests.get(
            f'https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_language}&tl={target_language}&dt=t&q={encoded_text}',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract translation from Google's response format
            if data and data[0]:
                full_translation = ''
                for segment in data[0]:
                    if segment and segment[0]:
                        full_translation += segment[0]
                
                return full_translation.strip()
                
    except Exception as e:
        print(f"Free Google translation failed: {e}")
        return None
    
    return None

def call_official_google_translate_api(text, api_key, target_language='ko', source_language='auto'):
    """Call official Google Translate API with user's API key"""
    try:
        if not api_key:
            return None
            
        url = "https://translation.googleapis.com/language/translate/v2"
        
        params = {
            'key': api_key,
            'q': text,
            'source': source_language if source_language != 'auto' else None,
            'target': target_language
        }
        
        print(f"Calling official Google Translate API with user key to translate to {target_language}...")
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            translation = result['data']['translations'][0]['translatedText']
            print(f"Official Google Translate success: '{translation}'")
            return translation
        else:
            print(f"Official Google Translate API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Official Google Translate API exception: {e}")
        return None

def get_basic_translation(text):
    """Fallback basic translation dictionary"""
    # Enhanced vocabulary with more context-aware translations
    smart_translations = {
        # Common phrases
        'hello world': '안녕, 세상',
        'good morning': '좋은 아침',
        'good evening': '좋은 저녁', 
        'good night': '잘 자',
        'thank you': '감사합니다',
        'how are you': '어떻게 지내세요',
        'i am fine': '저는 괜찮습니다',
        'what is your name': '이름이 뭐예요',
        'nice to meet you': '만나서 반갑습니다',
        'see you later': '나중에 봐요',
        'have a good day': '좋은 하루 보내세요',
        
        # Single words with better context
        'hello': '안녕하세요',
        'hi': '안녕',
        'world': '세상',
        'good': '좋은',
        'bad': '나쁜',
        'morning': '아침',
        'afternoon': '오후', 
        'evening': '저녁',
        'night': '밤',
        'today': '오늘',
        'tomorrow': '내일',
        'yesterday': '어제',
        'now': '지금',
        'later': '나중에',
        'here': '여기',
        'there': '저기',
        'this': '이것',
        'that': '저것',
        'these': '이것들',
        'those': '저것들',
        
        # Pronouns
        'i': '나는',
        'you': '당신은',
        'he': '그는',
        'she': '그녀는',
        'we': '우리는',
        'they': '그들은',
        'my': '나의',
        'your': '당신의',
        'his': '그의',
        'her': '그녀의',
        'our': '우리의',
        'their': '그들의',
        'me': '나를',
        'him': '그를',
        'us': '우리를',
        'them': '그들을',
        
        # Verbs
        'am': '입니다',
        'is': '입니다',
        'are': '입니다',
        'was': '였습니다',
        'were': '였습니다',
        'have': '가지고 있다',
        'has': '가지고 있다',
        'do': '하다',
        'does': '하다',
        'did': '했다',
        'will': '할 것이다',
        'would': '할 것이다',
        'can': '할 수 있다',
        'could': '할 수 있었다',
        'should': '해야 한다',
        'must': '해야 한다',
        'go': '가다',
        'come': '오다',
        'see': '보다',
        'look': '보다',
        'hear': '듣다',
        'listen': '듣다',
        'speak': '말하다',
        'talk': '이야기하다',
        'say': '말하다',
        'tell': '말하다',
        'know': '알다',
        'think': '생각하다',
        'want': '원하다',
        'need': '필요하다',
        'like': '좋아하다',
        'love': '사랑하다',
        'eat': '먹다',
        'drink': '마시다',
        'sleep': '자다',
        'work': '일하다',
        'play': '놀다',
        'study': '공부하다',
        'learn': '배우다',
        'teach': '가르치다',
        'read': '읽다',
        'write': '쓰다',
        
        # Common words
        'the': '',
        'a': '',
        'an': '',
        'and': '그리고',
        'or': '또는',
        'but': '하지만',
        'so': '그래서',
        'if': '만약',
        'when': '언제',
        'where': '어디',
        'what': '무엇',
        'who': '누구',
        'why': '왜',
        'how': '어떻게',
        'yes': '네',
        'no': '아니오',
        'not': '않다',
        'very': '매우',
        'really': '정말',
        'please': '부탁합니다',
        'sorry': '죄송합니다',
        'excuse': '실례합니다',
        'thank': '감사',
        'welcome': '환영합니다'
    }
    
    # First try to find complete phrases
    lower_text = text.lower().strip()
    if lower_text in smart_translations:
        return smart_translations[lower_text]
    
    # Then try sentence by sentence
    import re
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if sentences:
        translated_sentences = []
        for sentence in sentences:
            lower_sentence = sentence.strip().lower()
            if lower_sentence in smart_translations:
                translated_sentences.append(smart_translations[lower_sentence])
            else:
                # Word by word translation with better grammar
                words = sentence.strip().split()
                translated_words = []
                for word in words:
                    clean_word = re.sub(r'[.,!?;:()]', '', word.lower())
                    translated_words.append(smart_translations.get(clean_word, word))
                
                translated_sentences.append(' '.join([w for w in translated_words if w]))
        
        return '. '.join(translated_sentences)
    
    # Single word fallback
    import re
    clean_text = re.sub(r'[.,!?;:()]', '', text.lower().strip())
    return smart_translations.get(clean_text, text)

def call_elevenlabs_api(text, api_key, speed='normal'):
    """Call ElevenLabs API to generate TTS"""
    try:
        # Default voice ID for Rachel
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Convert speed to stability and similarity_boost values
        if speed == 'slow':
            stability = 0.75
            similarity_boost = 0.75
        elif speed == 'fast':
            stability = 0.50
            similarity_boost = 0.85
        else:  # normal
            stability = 0.65
            similarity_boost = 0.80
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        print(f"Calling ElevenLabs API with voice_id: {voice_id}")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Convert audio to base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            print(f"ElevenLabs API success - Audio length: {len(audio_base64)} chars")
            return audio_base64
        else:
            print(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"ElevenLabs API exception: {e}")
        return None

def call_groq_tts_api(text, api_key, speed='normal'):
    """Call Groq API for TTS (placeholder - Groq doesn't have TTS API yet)"""
    try:
        # Groq doesn't have TTS API yet, so this is a placeholder
        print(f"Groq TTS not implemented yet - API key available: {bool(api_key)}")
        return None
    except Exception as e:
        print(f"Groq TTS API exception: {e}")
        return None

def call_google_tts_api(text, speed='normal', language='en'):
    """Call Google TTS API via proxy to avoid CORS issues"""
    try:
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        
        # Use Google TTS API with specified language
        slow_param = "1" if speed == "slow" else "0"
        url = f'https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl={language}&client=tw-ob&slow={slow_param}'
        
        print(f"Calling Google TTS API via proxy - Language: {language}, Speed: {speed}")
        
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200 and len(response.content) > 1000:  # Valid audio file
            # Convert audio to base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            print(f"Google TTS proxy success - Audio length: {len(audio_base64)} chars")
            return audio_base64
        else:
            print(f"Google TTS proxy error: {response.status_code} - Content length: {len(response.content)}")
            return None
            
    except Exception as e:
        print(f"Google TTS proxy exception: {e}")
        return None

def call_groq_translation_api(text, api_key, target_language='ko', source_language='auto'):
    """Call Groq API for translation"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Language code to full language name mapping
        language_names = {
            'ko': 'Korean',
            'ja': 'Japanese', 
            'zh': 'Chinese',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'th': 'Thai',
            'vi': 'Vietnamese'
        }
        
        target_lang_name = language_names.get(target_language, target_language)
        source_lang_name = language_names.get(source_language, source_language) if source_language != 'auto' else 'auto-detected language'
        
        # Create prompt based on source language
        if source_language == 'auto':
            prompt = f"Translate this text to {target_lang_name}. Return only the {target_lang_name} translation without any additional text:\n\n{text}"
        else:
            prompt = f"Translate this {source_lang_name} text to {target_lang_name}. Return only the {target_lang_name} translation without any additional text:\n\n{text}"
        
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        print(f"Calling Groq translation API to translate to {target_lang_name}...")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            translation = result['choices'][0]['message']['content'].strip()
            print(f"Groq translation success: '{translation}'")
            return translation
        else:
            print(f"Groq translation API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Groq translation API exception: {e}")
        return None

def call_google_cloud_tts_api(text, api_key, speed='normal', language='en'):
    """Call Google Cloud Text-to-Speech API"""
    try:
        if not api_key:
            return None
            
        # Use API key as URL parameter (not Bearer token)
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
        
        # Convert speed to speaking rate
        speaking_rate = 1.0
        if speed == 'fast':
            speaking_rate = 1.25
        elif speed == 'slow':
            speaking_rate = 0.75
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Language code mapping for Google Cloud TTS
        tts_lang_mapping = {
            'ko': 'ko-KR',
            'ja': 'ja-JP', 
            'zh': 'zh-CN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-PT',
            'ru': 'ru-RU',
            'ar': 'ar-XA',
            'hi': 'hi-IN',
            'th': 'th-TH',
            'vi': 'vi-VN'
        }
        
        language_code = tts_lang_mapping.get(language, 'en-US')
        
        # Select appropriate voice based on language
        voice_name = f"{language_code}-Standard-A"  # Default voice
        if language_code == 'en-US':
            voice_name = "en-US-Neural2-D"
        elif language_code == 'ko-KR':
            voice_name = "ko-KR-Neural2-A"
        elif language_code == 'ja-JP':
            voice_name = "ja-JP-Neural2-B"
        
        data = {
            "input": {
                "text": text
            },
            "voice": {
                "languageCode": language_code,
                "name": voice_name,
                "ssmlGender": "MALE"
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": speaking_rate,
                "pitch": 0.0,
                "volumeGainDb": 0.0
            }
        }
        
        print(f"Calling Google Cloud TTS API - Language: {language_code}, Voice: {voice_name}, Rate: {speaking_rate}")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            audio_content = result.get('audioContent')
            if audio_content:
                print(f"Google Cloud TTS success - Audio length: {len(audio_content)} chars")
                return audio_content
        else:
            print(f"Google Cloud TTS API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Google Cloud TTS API exception: {e}")
        return None

def detect_text_language(text):
    """Detect language of text using Google Translate API"""
    try:
        import urllib.parse
        encoded_text = urllib.parse.quote(text[:100])  # Limit text length for detection
        
        response = requests.get(
            f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={encoded_text}',
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            # Google returns detected language in data[2]
            if data and len(data) > 2 and data[2]:
                detected_lang = data[2]
                print(f"Detected language: {detected_lang}")
                return detected_lang
                
    except Exception as e:
        print(f"Language detection failed: {e}")
    
    return None