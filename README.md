# Multilingual Study Platform

🌍 다국어 학습을 위한 웹 플랫폼입니다. 14개 언어를 지원하며, 양방향 번역과 다국어 음성 합성 기능을 제공합니다.

## 🌟 주요 기능

### 1. 다국어 텍스트 음성 변환 (TTS)
- **14개 언어 지원**: 영어, 한국어, 일본어, 중국어, 스페인어, 프랑스어, 독일어, 이탈리아어, 포르투갈어, 러시아어, 아랍어, 힌디어, 태국어, 베트남어
- **4가지 속도 옵션**: Fast, Normal, Slow, AI
- **스마트 언어 감지**: 입력된 텍스트의 언어를 자동으로 감지
- **활성 영역 인식**: 입력창과 번역창 모두에서 TTS 재생 가능

### 2. 양방향 다국어 번역
- **다중 번역 서비스**: Groq AI, Google Translate, 기본 사전 번역
- **양방향 번역**: 어떤 언어에서든 다른 언어로 번역 가능
- **자동 언어 감지**: 소스 언어를 자동으로 식별
- **스마트 언어 교환**: 소스와 타겟 언어를 원클릭으로 교환

### 3. 향상된 학습 기록 관리
- **다국어 기록**: 소스 언어와 타겟 언어 정보 포함
- **사용자 인증**: Django 백엔드를 통한 안전한 사용자 관리
- **실시간 동기화**: 서버와 클라이언트 간 실시간 데이터 동기화
- **선택적 삭제**: 개별 또는 일괄 학습 기록 삭제

### 4. 반응형 UI/UX
- **수평 언어 선택**: From/To 언어 선택이 한 줄에 배치
- **활성 영역 표시**: 현재 선택된 텍스트 영역을 시각적으로 표시
- **서비스 상태 표시**: 현재 활성화된 번역/TTS 서비스 실시간 표시
- **모바일 최적화**: 다양한 화면 크기에 최적화된 반응형 디자인

## 🛠️ 기술 스택

### Frontend
- **HTML5**: 시맨틱 마크업 및 접근성 개선
- **CSS3**: 
  - Flexbox 및 Grid 레이아웃
  - 반응형 디자인 (모바일 퍼스트)
  - CSS 변수 및 애니메이션
  - 다크/라이트 테마 지원
- **Vanilla JavaScript**: 
  - ES6+ 모던 문법
  - async/await 패턴
  - 모듈형 코드 구조
  - Web Speech API 활용

### Backend
- **Django 5.2.4**: Python 웹 프레임워크
- **Django REST Framework**: API 개발
- **SQLite**: 로컬 데이터베이스
- **Custom Middleware**: CORS 처리 및 보안

### APIs & Services
- **Groq AI**: 고품질 AI 번역
- **Google Translate**: 무료 번역 서비스
- **Google Cloud TTS**: 프리미엄 음성 합성
- **ElevenLabs**: AI 음성 생성
- **Web Speech API**: 브라우저 내장 TTS

## 📁 프로젝트 구조

```
web_plan1/
├── index.html                          # 메인 프론트엔드
├── style.css                           # 스타일시트
├── script.js                           # 클라이언트 JavaScript
├── english_study_backend/              # Django 백엔드
│   ├── manage.py                       # Django 관리 도구
│   ├── english_study_backend/          # 프로젝트 설정
│   │   ├── settings.py                 # Django 설정
│   │   ├── urls.py                     # URL 라우팅
│   │   └── wsgi.py                     # WSGI 설정
│   ├── accounts/                       # 사용자 관리 앱
│   │   ├── models.py                   # 사용자 및 학습 기록 모델
│   │   ├── views.py                    # 인증 관련 뷰
│   │   └── migrations/                 # 데이터베이스 마이그레이션
│   └── api/                            # API 앱
│       ├── views.py                    # 번역/TTS API 뷰
│       ├── middleware.py               # CORS 미들웨어
│       └── urls.py                     # API URL 라우팅
├── README.md                           # 프로젝트 문서
├── RECENT_UPDATES.md                   # 최신 업데이트 로그
├── PROJECT_DEVELOPMENT_SUMMARY.md      # 개발 요약
└── LAYOUT_DOCUMENTATION.md             # 레이아웃 문서
```

## 🚀 실행 방법

### 1. 백엔드 서버 실행
```bash
cd english_study_backend
python3 manage.py migrate
python3 manage.py runserver 8002
```

### 2. 프론트엔드 서버 실행
```bash
# 프로젝트 루트 디렉토리에서
python3 -m http.server 8001
```

### 3. 브라우저 접속
```
http://localhost:8001
```

## 🎯 사용법

### 기본 학습 과정
1. **언어 선택**: From(소스)과 To(타겟) 언어 선택
2. **텍스트 입력**: 어떤 언어든 텍스트 영역에 입력
3. **음성 듣기**: Fast/Normal/Slow 버튼으로 다양한 속도로 재생
4. **번역하기**: 🌐 Translate 버튼으로 선택한 언어로 번역
5. **저장하기**: 💾 Save 버튼으로 학습 기록에 저장

### 고급 기능
1. **언어 교환**: 🔄 Swap 버튼으로 소스↔타겟 언어 교환
2. **자동 감지**: Auto-detect 옵션으로 소스 언어 자동 인식
3. **이중 TTS**: 입력 텍스트와 번역 결과 모두 음성 재생 가능
4. **활성 영역**: 클릭으로 입력창/번역창 선택하여 TTS 대상 지정

### 단축키
- **Enter**: 현재 활성 영역의 텍스트로 TTS 재생
- **Shift+Enter**: 줄바꿈

## 🔧 API 키 설정

### Settings 메뉴에서 설정 가능:
- **ElevenLabs API Key**: 프리미엄 AI 음성 생성
- **Groq API Key**: 고품질 AI 번역
- **Google Translate API Key**: 공식 Google 번역
- **Google Cloud TTS API Key**: 프리미엄 음성 합성

### 환경 변수 설정:
```bash
# 필요한 경우 환경 변수로도 설정 가능
export ELEVENLABS_API_KEY="your_key_here"
export GROQ_API_KEY="your_key_here"
```

## 🎨 디자인 특징

### 색상 테마
- **Primary**: 녹색 그라데이션 (#4CAF50 → #45a049)
- **Secondary**: 오렌지 그라데이션 (#FF9800 → #F57C00)
- **Background**: 보라색 그라데이션 (#667eea → #764ba2)
- **Accent**: 블루 그라데이션 (#2196F3 → #1976D2)

### 레이아웃
- **3단 레이아웃**: 좌측 사이드바, 중앙 메인, 우측 리소스
- **수평 언어 선택**: 가로 배치된 From/To 선택기
- **활성 상태 표시**: 시각적 피드백으로 사용자 경험 향상
- **서비스 상태바**: 현재 활성 서비스 실시간 표시

## 📱 다국어 지원

### 지원 언어 (14개)
| 언어 | 코드 | TTS | 번역 |
|------|------|-----|------|
| 영어 | en | ✅ | ✅ |
| 한국어 | ko | ✅ | ✅ |
| 일본어 | ja | ✅ | ✅ |
| 중국어 | zh | ✅ | ✅ |
| 스페인어 | es | ✅ | ✅ |
| 프랑스어 | fr | ✅ | ✅ |
| 독일어 | de | ✅ | ✅ |
| 이탈리아어 | it | ✅ | ✅ |
| 포르투갈어 | pt | ✅ | ✅ |
| 러시아어 | ru | ✅ | ✅ |
| 아랍어 | ar | ✅ | ✅ |
| 힌디어 | hi | ✅ | ✅ |
| 태국어 | th | ✅ | ✅ |
| 베트남어 | vi | ✅ | ✅ |

## 🔒 보안 및 프라이버시

- **로컬 우선**: 브라우저 로컬 저장소 활용
- **암호화된 통신**: HTTPS 지원
- **API 키 보안**: 클라이언트 사이드 암호화 저장
- **CORS 보안**: 적절한 CORS 정책 적용
- **사용자 인증**: Django 내장 인증 시스템

## 🐛 알려진 이슈

1. **네트워크 의존성**: 번역 및 TTS는 인터넷 연결 필요
2. **API 제한**: 무료 API는 사용량 제한 있음
3. **브라우저 호환성**: 일부 구형 브라우저에서 제한적 기능
4. **언어별 TTS 품질**: 언어에 따라 음성 품질 차이 있음

## 🚀 향후 개선 계획

- [ ] 오프라인 모드 지원
- [ ] 학습 진도 및 통계 기능
- [ ] 맞춤형 단어장 및 플래시카드
- [ ] 발음 평가 및 교정 기능
- [ ] 실시간 대화 학습 모드
- [ ] PWA (Progressive Web App) 지원
- [ ] 더 많은 언어 추가 (20+ 언어)
- [ ] AI 기반 학습 추천 시스템

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

**Made with ❤️ for multilingual learners worldwide 🌍**