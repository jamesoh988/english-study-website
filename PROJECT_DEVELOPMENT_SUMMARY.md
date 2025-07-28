# 영어 공부 웹사이트 개발 과정 정리

## 프로젝트 개요

### 목적
- TTS(Text-to-Speech)와 번역 기능을 제공하는 영어 학습 웹사이트
- 다양한 AI API 서비스 통합으로 고품질 음성 및 번역 서비스 제공
- 사용자별 학습 기록 관리 및 개인화된 설정

### 기술 스택
- **프론트엔드**: HTML5, CSS3, JavaScript (Vanilla)
- **백엔드**: Django 5.2.4 (Python)
- **데이터베이스**: SQLite (개발용)
- **API 통합**: ElevenLabs, Google Cloud TTS, Google Translate, Groq AI

---

## 개발 과정

### 1. 초기 구조 설정

#### 1.1 Django 프로젝트 생성
```bash
# Django 프로젝트 구조
english_study_backend/
├── manage.py
├── english_study_backend/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py (UserProfile, StudyHistory)
│   └── migrations/
└── api/
    ├── views.py (API 엔드포인트)
    └── urls.py
```

#### 1.2 사용자 모델 설계
```python
# accounts/models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # API Keys
    elevenlabs_api_key = models.CharField(max_length=255, blank=True, null=True)
    groq_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_translate_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_tts_api_key = models.CharField(max_length=255, blank=True, null=True)
    
    # 사용자 설정
    preferred_tts_service = models.CharField(max_length=20, default='google')
    preferred_voice_speed = models.CharField(max_length=10, default='normal')
    preferred_translation_service = models.CharField(max_length=20, default='auto')
    
    # 사용량 추적
    daily_character_usage = models.IntegerField(default=0)
    total_characters_used = models.IntegerField(default=0)
```

### 2. 프론트엔드 개발

#### 2.1 HTML 구조
- **반응형 레이아웃**: 헤더, 사이드바, 메인 컨텐츠 영역
- **모달 시스템**: 로그인/회원가입, 설정 모달
- **서비스 상태 표시**: 현재 사용 중인 번역/TTS 서비스 실시간 표시

```html
<!-- 주요 구조 -->
<div class="top-header">
    <!-- 로그인/설정 버튼 -->
</div>

<div class="main-container">
    <div class="sidebar">
        <!-- 학습 기록 히스토리 -->
    </div>
    
    <div class="content">
        <!-- 서비스 상태 바 -->
        <div class="service-status-bar">
            <span id="currentTranslationService">Google Free</span>
            <span id="currentTtsService">Google TTS</span>
        </div>
        
        <!-- 음성 컨트롤 -->
        <div class="voice-controls">
            <button class="voice-btn">Fast</button>
            <button class="voice-btn active">Normal</button>
            <button class="voice-btn">Slow</button>
        </div>
        
        <!-- 액션 버튼 -->
        <div class="action-buttons">
            <button id="translateBtn">Translate</button>
            <button id="saveBtn">Save</button>
        </div>
    </div>
</div>
```

#### 2.2 CSS 스타일링
- **모던 디자인**: 그라데이션, 그림자, 애니메이션 효과
- **3D 버튼 효과**: hover 시 transform 및 그림자 변화
- **서비스 상태 뱃지**: 실시간 서비스 표시를 위한 동적 뱃지 시스템

```css
/* 주요 스타일 특징 */
.voice-btn {
    position: relative;
    border-radius: 25px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.voice-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.btn-status {
    position: absolute;
    top: -8px;
    right: -8px;
    background: #4CAF50;
    border-radius: 10px;
    font-size: 0.7em;
}
```

### 3. 백엔드 API 개발

#### 3.1 인증 시스템
```python
# 주요 API 엔드포인트
@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    # 사용자 로그인 처리
    # 프로필 정보 반환 (API 키 보유 여부 포함)

@csrf_exempt  
@require_http_methods(["GET", "PUT"])
def user_profile(request):
    # GET: 사용자 프로필 정보 조회
    # PUT: 사용자 설정 업데이트 (API 키, 선호 서비스 등)
```

#### 3.2 TTS API 통합
```python
@csrf_exempt
@require_http_methods(["POST"])
def text_to_speech(request):
    # 사용자 인증 확인
    # 선호 서비스 우선순위 결정
    # 1. ElevenLabs (최고품질)
    # 2. Google Cloud TTS (고품질)
    # 3. Google TTS Free (무료)
    # 4. Browser TTS (브라우저 기본)
    
    # 각 서비스별 API 호출 및 오디오 데이터 반환
```

#### 3.3 번역 API 통합
```python
@csrf_exempt
@require_http_methods(["POST"])
def translate_text(request):
    # 번역 서비스 우선순위
    # 1. Groq AI (AI 번역)
    # 2. Google Translate Official (유료)
    # 3. Google Translate Free (무료)
    # 4. Basic Dictionary (기본 사전)
```

### 4. AI API 서비스 통합

#### 4.1 ElevenLabs TTS
```python
def call_elevenlabs_api(text, api_key, speed='normal'):
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel 음성
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    # 속도에 따른 안정성/유사성 조정
    stability = {'slow': 0.75, 'normal': 0.65, 'fast': 0.50}[speed]
    similarity_boost = {'slow': 0.75, 'normal': 0.80, 'fast': 0.85}[speed]
    
    # Base64 오디오 데이터 반환
```

#### 4.2 Google Cloud TTS
```python
def call_google_cloud_tts_api(text, api_key, speed='normal'):
    # API Key 방식 인증 (Bearer Token 아님)
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    
    # Neural 음성 사용 (en-US-Neural2-D)
    # 속도별 speaking_rate 조정
    speaking_rate = {'slow': 0.75, 'normal': 1.0, 'fast': 1.25}[speed]
```

#### 4.3 Groq AI 번역
```python
def call_groq_translation_api(text, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # LLaMA 모델 사용한 고품질 번역
    model = "llama3-70b-8192"
    prompt = f"Translate this English text to Korean. Return only the Korean translation:\\n\\n{text}"
```

### 5. 사용자 경험 개선

#### 5.1 실시간 서비스 상태 표시
```javascript
function updateServiceStatusAfterAction(service, type) {
    // 메인 상태 바 업데이트
    const serviceNames = {
        'elevenlabs': 'ElevenLabs',
        'google_cloud': 'Google Cloud TTS',
        'google': 'Google Free',
        'groq': 'Groq AI',
        'browser': 'Browser TTS'
    };
    
    // 버튼 뱃지 업데이트
    const serviceLabels = {
        'elevenlabs': 'AI+',
        'google_cloud': 'GC', 
        'google': 'G',
        'groq': 'AI'
    };
}
```

#### 5.2 학습 기록 관리
```javascript
// 로그인 사용자: 데이터베이스 저장
// 게스트 사용자: localStorage 사용
async function saveLocally(text, translation) {
    if (currentUser && authToken) {
        // 서버에 저장
        await fetch(`${API_BASE_URL}/study/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${authToken}`
            },
            body: JSON.stringify({ text, translation })
        });
    } else {
        // 로컬 저장소에 저장
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    }
}
```

### 6. 최적화 및 리팩토링

#### 6.1 코드 최적화
- **불필요한 함수 제거**: 중복된 TTS/번역 함수들 삭제
- **콘솔 로그 정리**: 디버그 메시지 간소화
- **API 요청 최적화**: 불필요한 GET 요청 제거

#### 6.2 성능 개선
```javascript
// 이전: 매번 API 요청
function updateServiceStatus() {
    fetch(`${API_BASE_URL}/auth/profile/`).then(...)  // 불필요한 요청
}

// 개선: 캐시된 데이터 사용
function updateServiceStatus() {
    if (currentUser && currentUser.profile) {
        const profile = currentUser.profile;  // 캐시된 데이터 사용
        // UI 업데이트
    }
}
```

#### 6.3 에러 해결
- **Favicon 404 에러**: SVG 기반 인라인 favicon 추가
- **데이터베이스 마이그레이션**: 새 필드 추가 시 적절한 마이그레이션 수행
- **CORS 문제**: Django CORS 설정으로 해결

---

## 주요 기능

### 1. TTS (Text-to-Speech)
- **4가지 서비스 지원**: ElevenLabs, Google Cloud, Google Free, Browser
- **3단계 속도 조절**: Fast, Normal, Slow
- **실시간 서비스 상태 표시**: 현재 사용 중인 TTS 서비스 표시
- **자동 fallback**: API 오류 시 자동으로 다음 서비스로 전환

### 2. 번역 서비스
- **4가지 번역 엔진**: Groq AI, Google Official, Google Free, Basic Dictionary
- **컨텍스트 인식**: 문장 단위 및 구문 단위 번역
- **사용자 선호 서비스**: 개인별 번역 엔진 선택 가능

### 3. 사용자 관리
- **회원가입/로그인**: 간단한 토큰 기반 인증
- **API 키 관리**: 개인 API 키로 프리미엄 서비스 이용
- **사용량 추적**: 일일/총 사용량 모니터링
- **학습 기록**: 번역한 텍스트와 사용한 서비스 기록

### 4. 반응형 디자인
- **모바일 친화적**: 다양한 화면 크기 지원
- **모던 UI**: 그라데이션, 애니메이션, 3D 효과
- **직관적 UX**: 명확한 서비스 상태 표시 및 피드백

---

## 파일 구조

```
web_plan1/
├── index.html                 # 메인 HTML 페이지
├── style.css                  # 스타일시트
├── script.js                  # 프론트엔드 JavaScript
└── english_study_backend/     # Django 백엔드
    ├── manage.py
    ├── english_study_backend/
    │   ├── settings.py         # Django 설정
    │   ├── urls.py            # URL 라우팅
    │   └── wsgi.py
    ├── accounts/
    │   ├── models.py          # 사용자 모델
    │   ├── admin.py
    │   └── migrations/        # 데이터베이스 마이그레이션
    └── api/
        ├── views.py           # API 엔드포인트
        ├── urls.py            # API URL 라우팅
        └── __init__.py
```

---

## 개발 도구 및 환경

### 개발 환경
- **Python**: 3.x
- **Django**: 5.2.4
- **데이터베이스**: SQLite (개발용)
- **서버**: Django 개발 서버 (localhost:8002)

### 외부 API
- **ElevenLabs**: 고품질 AI 음성 합성
- **Google Cloud TTS**: Neural 음성 엔진
- **Google Translate**: 번역 서비스
- **Groq**: LLaMA 기반 AI 번역

### 개발 과정에서 사용된 도구
- **브라우저 개발자 도구**: 디버깅 및 네트워크 모니터링
- **Django Admin**: 사용자 및 데이터 관리
- **콘솔 로깅**: API 요청/응답 추적

---

## 향후 개선 방향

### 1. 기능 확장
- **음성 인식**: Speech-to-Text 기능 추가
- **발음 평가**: 사용자 발음 분석 및 피드백
- **단어장 기능**: 학습한 단어 저장 및 복습
- **진도 추적**: 학습 진행률 시각화

### 2. 기술적 개선
- **데이터베이스**: PostgreSQL로 업그레이드
- **캐싱**: Redis 도입으로 성능 향상
- **배포**: Docker + AWS/GCP 배포
- **보안**: JWT 토큰, HTTPS 적용

### 3. UX/UI 개선
- **다크 모드**: 사용자 선택 가능한 테마
- **키보드 단축키**: 효율적인 학습을 위한 단축키
- **PWA**: 모바일 앱 같은 경험 제공

---

## 개발 과정에서 배운 점

### 1. API 통합의 복잡성
- 각 API마다 다른 인증 방식 (Bearer Token vs API Key)
- 오류 처리 및 fallback 시스템의 중요성
- 비동기 처리와 사용자 피드백

### 2. 사용자 경험 중심 설계
- 실시간 상태 피드백의 중요성
- 로딩 상태 및 에러 메시지 표시
- 직관적인 UI/UX 설계

### 3. 코드 품질 관리
- 중복 코드 제거의 필요성
- 함수 책임 분리 및 모듈화
- 효율적인 에러 핸들링

이 프로젝트를 통해 프론트엔드와 백엔드를 아우르는 풀스택 웹 개발 경험을 쌓을 수 있었으며, 특히 다양한 AI API 서비스를 통합하는 과정에서 실용적인 개발 스킬을 습득할 수 있었습니다.