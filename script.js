// DOM Elements
const englishText = document.getElementById('englishText');
const fastTtsBtn = document.getElementById('fastTtsBtn');
const normalTtsBtn = document.getElementById('normalTtsBtn');
const slowTtsBtn = document.getElementById('slowTtsBtn');
// const aiTtsBtn = document.getElementById('aiTtsBtn'); // Removed - functionality moved to speed buttons
const translateBtn = document.getElementById('translateBtn');
const saveBtn = document.getElementById('saveBtn');
const clearBtn = document.getElementById('clearBtn');
const translationResult = document.getElementById('translationResult');
const translationText = document.getElementById('translationText');
const selectAllBtn = document.getElementById('selectAllBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const historyList = document.getElementById('historyList');
const loginBtn = document.getElementById('loginBtn');
const settingsBtn = document.getElementById('settingsBtn');

// Modal elements
const loginModal = document.getElementById('loginModal');
const settingsModal = document.getElementById('settingsModal');
const loginTab = document.getElementById('loginTab');
const registerTab = document.getElementById('registerTab');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

// Django backend URL
const API_BASE_URL = 'http://localhost:8002/api';

// User state
let currentUser = null;
let authToken = null;

// Storage key (fallback for guests)
const STORAGE_KEY = 'english_study_history';

// Utility function to convert base64 to blob
function base64ToBlob(base64Data, contentType = '') {
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: contentType });
}

// TTS functionality with speed control
async function playTTS(text, speed) {
    if (!text) {
        alert('Please enter English text!');
        return;
    }
    
    // Disable all TTS buttons
    fastTtsBtn.disabled = true;
    normalTtsBtn.disabled = true;
    slowTtsBtn.disabled = true;
    
    // Update button text based on speed
    const speedBtns = { 'fast': fastTtsBtn, 'normal': normalTtsBtn, 'slow': slowTtsBtn };
    const speedIcons = { 'fast': '🚀', 'normal': '🔊', 'slow': '🐌' };
    speedBtns[speed].textContent = `${speedIcons[speed]} Playing...`;
    
    try {
        // Always try Django backend first (works for both authenticated and guest users)
        let success = await tryDjangoTTS(text, speed);
        
        // Final fallback to browser TTS if Django backend fails
        if (!success) {
            fallbackToSynthesis();
        }
        
    } catch (error) {
        console.error('TTS error:', error);
        fallbackToSynthesis();
    }
    
    // Django backend TTS for all users
    async function tryDjangoTTS(text, speed) {
        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            
            // Add auth header if user is logged in
            if (currentUser && authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }
            
            const response = await fetch(`${API_BASE_URL}/text-to-speech/`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    text: text,
                    speed: speed,
                    service: 'auto' // Let backend choose best service based on user preferences
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.audio_data) {
                    console.log(`TTS via ${data.service} (${speed})`);
                    // Play audio from Django backend (binary data)
                    const audioBlob = base64ToBlob(data.audio_data, data.content_type || 'audio/mpeg');
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    
                    // Adjust playback rate for speed control
                    audio.oncanplaythrough = () => {
                        if (speed === 'fast') {
                            audio.playbackRate = 1.3;
                        } else if (speed === 'normal') {
                            audio.playbackRate = 1.0;
                        } else if (speed === 'slow') {
                            audio.playbackRate = 0.8;
                        }
                    };
                    
                    audio.onended = () => {
                        URL.revokeObjectURL(audioUrl);
                        resetButtons();
                    };
                    
                    audio.onerror = (error) => {
                        console.error('Audio playback error:', error);
                        URL.revokeObjectURL(audioUrl);
                        return false;
                    };
                    
                    await audio.play();
                    // Update service status display
                    updateServiceStatusAfterAction(data.service, 'tts');
                    return true;
                } else if (data.success && data.use_browser_tts) {
                    fallbackToSynthesis();
                    updateServiceStatusAfterAction('browser', 'tts');
                    return true;
                }
            }
        } catch (error) {
            console.error('TTS failed:', error);
        }
        return false;
    }
    
    // Note: tryGoogleTTS function removed - all TTS now goes through Django backend
    
    // Fallback function using browser TTS
    function fallbackToSynthesis() {
        console.log(`Browser TTS fallback (${speed})`);
        speechSynthesis.cancel();
        
        setTimeout(() => {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.pitch = 1;
            utterance.volume = 1;
            
            // Set rate based on speed
            if (speed === 'fast') {
                utterance.rate = 1.3;
            } else if (speed === 'normal') {
                utterance.rate = 0.9;
            } else if (speed === 'slow') {
                utterance.rate = 0.6;
            }
            
            utterance.onend = () => {
                resetButtons();
            };
            
            utterance.onerror = () => {
                resetButtons();
                alert('Speech playback failed.');
            };
            
            if ('speechSynthesis' in window) {
                speechSynthesis.speak(utterance);
                updateServiceStatusAfterAction('browser', 'tts');
            } else {
                resetButtons();
                alert('This browser does not support speech playback.');
            }
        }, 100);
    }
    
    // Reset buttons function
    function resetButtons() {
        fastTtsBtn.disabled = false;
        normalTtsBtn.disabled = false;
        slowTtsBtn.disabled = false;
        fastTtsBtn.textContent = '🚀 Fast';
        normalTtsBtn.textContent = '🔊 Normal';
        slowTtsBtn.textContent = '🐌 Slow';
    }
}

// 불필요한 TTS 함수들 삭제됨 - Django 백엔드에서 모든 TTS 서비스 처리

// Translation functionality (using Django backend with fallback)
translateBtn.addEventListener('click', async () => {
    const text = englishText.value.trim();
    if (!text) {
        alert('Please enter English text!');
        return;
    }
    
    translateBtn.disabled = true;
    translateBtn.textContent = '🌐 Translating...';
    
    try {
        console.log('Starting translation for:', text);
        
        // Use Django backend (handles all services and fallbacks)
        let translation = await translateWithDjango(text);
        
        // Final fallback to client-side dictionary
        if (!translation) {
            console.log('Using smart translation fallback...');
            translation = getSmartTranslation(text);
        }
        
        translationText.textContent = translation;
        translationResult.style.display = 'block';
        
    } catch (error) {
        console.error('Translation error:', error);
        translationText.textContent = getSmartTranslation(text);
        translationResult.style.display = 'block';
    }
    
    translateBtn.disabled = false;
    translateBtn.textContent = '🌐 Translate';
});

// 불필요한 번역 함수들 삭제됨 - Django 백엔드에서 모든 번역 서비스 처리

// Django backend translation (supports guests)
async function translateWithDjango(text) {
    try {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Add auth header if user is logged in
        if (currentUser && authToken) {
            headers['Authorization'] = `Token ${authToken}`;
        }
        
        // Get user's preferred translation service
        let preferredService = 'auto';  // default
        if (currentUser && authToken) {
            const translationSelect = document.getElementById('preferredTranslation');
            if (translationSelect) {
                preferredService = translationSelect.value || 'auto';
            }
        }
        
        const response = await fetch(`${API_BASE_URL}/translate/`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                text: text,
                service: preferredService
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.translation) {
                console.log(`Translation via ${data.service}: ${data.translation}`);
                // Update service status display
                updateServiceStatusAfterAction(data.service, 'translation');
                return data.translation;
            }
        }
    } catch (error) {
        console.error('Translation failed:', error);
    }
    return null;
}

// Smart translation with better context understanding
function getSmartTranslation(text) {
    // Enhanced vocabulary with more context-aware translations
    const smartTranslations = {
        // Common phrases
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
        
        // Single words with better context
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
        
        // Pronouns
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
        
        // Verbs
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
        
        // Common words
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
    };
    
    // First try to find complete phrases
    const lowerText = text.toLowerCase().trim();
    if (smartTranslations[lowerText]) {
        return smartTranslations[lowerText];
    }
    
    // Then try sentence by sentence
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());
    const translatedSentences = sentences.map(sentence => {
        const lowerSentence = sentence.trim().toLowerCase();
        if (smartTranslations[lowerSentence]) {
            return smartTranslations[lowerSentence];
        }
        
        // Word by word translation with better grammar
        const words = sentence.trim().split(/\s+/);
        const translatedWords = words.map(word => {
            const cleanWord = word.toLowerCase().replace(/[.,!?;:()"]/, '');
            return smartTranslations[cleanWord] || word;
        });
        
        return translatedWords.filter(w => w !== '').join(' ');
    });
    
    return translatedSentences.join('. ');
}

// Save functionality
saveBtn.addEventListener('click', async () => {
    const text = englishText.value.trim();
    if (!text) {
        alert('Please enter English text!');
        return;
    }
    
    if (currentUser && authToken) {
        // Save to Django backend for authenticated users (English text only)
        try {
            const response = await fetch(`${API_BASE_URL}/study/save/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`
                },
                body: JSON.stringify({
                    text: text,
                    translation: ''  // 번역 결과는 저장하지 않음
                })
            });
            
            if (response.ok) {
                alert('Saved successfully!');
                // 즉시 목록 새로고침
                if (currentUser && authToken) {
                    loadStudyHistory();
                } else {
                    loadHistory();
                }
            } else {
                alert('Error saving to server. Please try again.');
                console.error('Server save failed:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error saving to server:', error);
            alert('Error saving to server. Please try again.');
        }
    } else {
        // Save locally for guests (English text only)
        saveLocally(text, '');
    }
    
    // Clear inputs after save
    clearInputs();
});

// Clear button functionality
clearBtn.addEventListener('click', () => {
    if (confirm('Clear text and translation?')) {
        clearInputs();
    }
});

function clearInputs() {
    englishText.value = '';
    translationResult.style.display = 'none';
    translationText.textContent = '';
}

async function saveLocally(text, translation) {
    console.log(`Saving locally - Guest user, Text: ${text.substring(0, 50)}...`);
    
    // For guest users only, save to localStorage
    const studyItem = {
        id: Date.now(),
        text: text,
        translation: translation,
        date: new Date().toLocaleString('en-US')
    };
    
    let history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    history.unshift(studyItem);
    
    if (history.length > 50) {
        history = history.slice(0, 50);
    }
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    alert('Saved locally!');
    loadHistory();
}

// Load and display history on page load
async function loadHistory() {
    console.log(`Loading history - User: ${currentUser ? currentUser.username : 'guest'}`);
    
    // For logged-in users, try to load from database first
    if (currentUser && authToken) {
        try {
            const response = await fetch(`${API_BASE_URL}/study/history/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${authToken}`
                }
            });
            
            const data = await response.json();
            if (data.success && data.history) {
                console.log(`Loaded ${data.history.length} items from database`);
                displayHistory(data.history);
                return;
            } else {
                console.error('Database load failed:', data.error);
                // Fallback to localStorage
            }
        } catch (error) {
            console.error('Database load error:', error);
            // Fallback to localStorage
        }
    }
    
    // For guest users or fallback, load from localStorage
    const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    console.log(`Loaded ${history.length} items from localStorage`);
    displayHistory(history);
}

// Load history item from memory (for current session)
window.loadHistoryItemFromMemory = (id) => {
    console.log('Loading history item from memory:', id);
    console.log('Current history data:', currentHistoryData);
    
    // First try to find in current loaded data
    let item = currentHistoryData.find(h => h.id == id);
    
    if (!item) {
        // Fallback to local storage for guests or if not found
        const localHistory = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        item = localHistory.find(h => h.id == id);
    }
    
    if (item) {
        console.log('Found item:', item);
        englishText.value = item.english_text || item.text || '';
        
        if (item.korean_translation || item.translation) {
            translationText.textContent = item.korean_translation || item.translation;
            translationResult.style.display = 'block';
        } else {
            translationResult.style.display = 'none';
        }
    } else {
        console.error('History item not found:', id);
    }
};

// Legacy function for backward compatibility
window.loadHistoryItem = async (id, isFromServer = false) => {
    // Use the memory-based function instead
    loadHistoryItemFromMemory(id);
};

// Select All button - toggles all checkboxes
selectAllBtn.addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
    
    if (checkboxes.length === 0) {
        alert('No items to select.');
        return;
    }
    
    // If all are checked, uncheck all. Otherwise, check all.
    const shouldCheck = checkedBoxes.length !== checkboxes.length;
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = shouldCheck;
    });
    
    // Update button text
    selectAllBtn.textContent = shouldCheck ? 'Deselect All' : 'Select All';
});

// Delete selected history items
clearHistoryBtn.addEventListener('click', async () => {
    // Get all selected checkboxes
    const selectedCheckboxes = document.querySelectorAll('.item-checkbox:checked');
    
    if (selectedCheckboxes.length === 0) {
        alert('Please select items to delete.');
        return;
    }
    
    if (confirm(`Delete ${selectedCheckboxes.length} selected study record(s)? This cannot be undone.`)) {
        if (currentUser && authToken) {
            // Delete selected items from database for authenticated users
            try {
                const selectedIds = Array.from(selectedCheckboxes).map(cb => cb.dataset.id);
                
                const response = await fetch(`${API_BASE_URL}/study/delete-selected/`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Token ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ item_ids: selectedIds })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    alert(`Deleted ${data.deleted_count} selected study records from server.`);
                    loadStudyHistory(); // Reload from database
                } else {
                    alert('Error deleting selected items from server. Please try again.');
                }
            } catch (error) {
                console.error('Error deleting selected items from server:', error);
                alert('Error deleting selected items from server. Please try again.');
            }
        } else {
            // Delete selected items from local storage for guests
            try {
                const selectedIds = Array.from(selectedCheckboxes).map(cb => cb.dataset.id);
                let localHistory = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
                
                // Filter out selected items
                localHistory = localHistory.filter(item => !selectedIds.includes(item.id.toString()));
                
                localStorage.setItem(STORAGE_KEY, JSON.stringify(localHistory));
                loadHistory();
                alert(`Deleted ${selectedCheckboxes.length} selected local study records.`);
            } catch (error) {
                console.error('Error deleting selected local items:', error);
                alert('Error deleting selected local items. Please try again.');
            }
        }
    }
});

// Authentication functions
async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            currentUser.profile = data.profile; // Store profile information
            
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            console.log('User profile loaded:', data.profile);
            console.log('Available services:', {
                elevenlabs: data.profile.has_elevenlabs_key,
                groq: data.profile.has_groq_key,
                can_use_ai: data.profile.can_use_ai
            });
            
            updateUIForLoggedInUser();
            loadHistory(); // Load user's study history from database
            
            // Refresh page after successful login
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
            return { success: true };
        } else {
            return { success: false, error: data.error || 'Login failed' };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Network error' };
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true };
        } else {
            return { success: false, error: data.error || 'Registration failed' };
        }
    } catch (error) {
        console.error('Registration error:', error);
        return { success: false, error: 'Network error' };
    }
}

function logout() {
    // Logout confirmation
    if (!confirm('Are you sure you want to logout?')) {
        return;
    }
    
    console.log(`Logging out user: ${currentUser ? currentUser.username : 'unknown'}`);
    
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    updateUIForLoggedOutUser();
    
    // Refresh page after logout
    setTimeout(() => {
        window.location.reload();
    }, 500);
}

function updateUIForLoggedInUser() {
    loginBtn.textContent = currentUser.username;
    document.getElementById('settingsBtn').style.display = 'inline-block';
    closeModal(loginModal);
    loadStudyHistory();
    
    // Update service status after login
    setTimeout(() => updateServiceStatus(), 500);
}

function updateUIForLoggedOutUser() {
    loginBtn.textContent = 'Login';
    document.getElementById('settingsBtn').style.display = 'none';
    loadHistory(); // Load local storage history
    
    // Update service status for guest user
    updateServiceStatus();
}

// CSRF token function removed - not needed for API-only backend

// Login button click handler
loginBtn.addEventListener('click', () => {
    if (currentUser) {
        logout();
    } else {
        openModal(loginModal);
    }
});

// Modal functions
function openModal(modal) {
    modal.style.display = 'flex';
}

function closeModal(modal) {
    modal.style.display = 'none';
}

// Modal event listeners
document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.addEventListener('click', (e) => {
        const modal = e.target.closest('.modal');
        closeModal(modal);
    });
});

// Close modal on background click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal(modal);
        }
    });
});

// Auth tab switching
document.getElementById('loginTab').addEventListener('click', () => {
    switchAuthTab('login');
});

document.getElementById('registerTab').addEventListener('click', () => {
    switchAuthTab('register');
});

function switchAuthTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (tab === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
    } else {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.style.display = 'flex';
        loginForm.style.display = 'none';
    }
}

// Form submissions
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    const result = await login(username, password);
    if (result.success) {
        alert('Logged in successfully!');
    } else {
        alert(result.error);
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    const result = await register(username, email, password);
    if (result.success) {
        alert('Registration successful! Please login.');
        switchAuthTab('login');
    } else {
        alert(result.error);
    }
});

// Settings button
document.getElementById('settingsBtn').addEventListener('click', () => {
    openModal(document.getElementById('settingsModal'));
    loadUserSettings();
});

// Auto-resize textarea
englishText.addEventListener('input', () => {
    englishText.style.height = 'auto';
    englishText.style.height = englishText.scrollHeight + 'px';
});

// Enter key to play audio (normal speed)
englishText.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!normalTtsBtn.disabled) {
            normalTtsBtn.click();
        }
    }
});

// API functions for authenticated users
async function loadUserSettings() {
    if (!currentUser || !authToken) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/profile/`, {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const profile = data.profile;
            
            document.getElementById('elevenLabsKey').value = profile.elevenlabs_api_key || '';
            document.getElementById('groqKey').value = profile.groq_api_key || '';
            document.getElementById('googleTranslateKey').value = profile.google_translate_api_key || '';
            document.getElementById('googleTtsKey').value = profile.google_tts_api_key || '';
            document.getElementById('preferredTTS').value = profile.preferred_tts_service;
            document.getElementById('preferredSpeed').value = profile.preferred_voice_speed;
            document.getElementById('preferredTranslation').value = profile.preferred_translation_service || 'auto';
            document.getElementById('dailyUsage').textContent = profile.daily_usage;
            document.getElementById('totalUsage').textContent = profile.total_usage;
            
            console.log('Settings loaded - API keys available:', {
                elevenlabs: profile.has_elevenlabs_key,
                groq: profile.has_groq_key,
                google: profile.has_google_key
            });
        }
    } catch (error) {
        console.error('Error loading user settings:', error);
    }
}

async function saveUserSettings() {
    if (!currentUser || !authToken) return;
    
    const settings = {
        elevenlabs_api_key: document.getElementById('elevenLabsKey').value,
        groq_api_key: document.getElementById('groqKey').value,
        google_translate_api_key: document.getElementById('googleTranslateKey').value,
        google_tts_api_key: document.getElementById('googleTtsKey').value,
        preferred_tts_service: document.getElementById('preferredTTS').value,
        preferred_voice_speed: document.getElementById('preferredSpeed').value,
        preferred_translation_service: document.getElementById('preferredTranslation').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/profile/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${authToken}`
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Settings saved. Updated profile:', data.profile);
            
            // Update current user profile in memory
            if (currentUser.profile) {
                currentUser.profile = { ...currentUser.profile, ...data.profile };
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
            }
            
            alert('Settings saved successfully!');
            closeModal(document.getElementById('settingsModal'));
        } else {
            alert('Error saving settings');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('Error saving settings');
    }
}

async function loadStudyHistory() {
    if (!currentUser || !authToken) {
        loadHistory(); // Fall back to local storage
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/study/history/`, {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Django study history response:', data);
            displayHistory(data.history || []);
        } else {
            loadHistory(); // Fall back to local storage
        }
    } catch (error) {
        console.error('Error loading study history:', error);
        loadHistory(); // Fall back to local storage
    }
}

// Store current history data for click handling
let currentHistoryData = [];

function displayHistory(history) {
    currentHistoryData = history; // Store for later use
    
    if (history.length === 0) {
        historyList.innerHTML = '<p class="no-history">No study records saved.</p>';
        selectAllBtn.textContent = 'Select All';
    } else {
        historyList.innerHTML = history.map(item => {
            const text = item.english_text || item.text;
            const displayText = text.length > 50 ? text.substring(0, 50) + '...' : text;
            return `
                <div class="history-item">
                    <div class="history-checkbox">
                        <input type="checkbox" class="item-checkbox" data-id="${item.id}" onclick="event.stopPropagation(); updateSelectAllButton();">
                    </div>
                    <div class="history-content" onclick="loadHistoryItemFromMemory('${item.id}')">
                        <div class="history-date">${new Date(item.created_at || item.date).toLocaleString()}</div>
                        <div class="history-text" title="${text.replace(/"/g, '&quot;')}">${displayText}</div>
                    </div>
                </div>
            `;
        }).join('');
        selectAllBtn.textContent = 'Select All';
    }
}

// Update Select All button text based on current selection state
function updateSelectAllButton() {
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
    
    if (checkboxes.length === 0) {
        selectAllBtn.textContent = 'Select All';
    } else if (checkedBoxes.length === checkboxes.length) {
        selectAllBtn.textContent = 'Deselect All';
    } else {
        selectAllBtn.textContent = 'Select All';
    }
}

// Save settings button
document.getElementById('saveSettings').addEventListener('click', saveUserSettings);

// Service status management
function updateServiceStatus() {
    const translationService = document.getElementById('currentTranslationService');
    const ttsService = document.getElementById('currentTtsService');
    
    if (currentUser && currentUser.profile) {
        // Use cached profile data instead of making API request
        const profile = currentUser.profile;
        
        // Update translation service status
        let translationText = 'Basic Dictionary';
        if (profile.has_google_key && profile.preferred_translation_service === 'google') {
            translationText = 'Google Official';
        } else if (profile.has_groq_key && profile.preferred_translation_service === 'groq') {
            translationText = 'Groq AI';
        } else if (profile.has_google_key || profile.has_groq_key) {
            translationText = 'Auto (AI)';
        } else {
            translationText = 'Google Free';
        }
        translationService.textContent = translationText;
        translationService.className = 'status-value';
        
        // Update TTS service status
        let ttsText = 'Browser TTS';
        if (profile.has_elevenlabs_key && profile.preferred_tts_service === 'elevenlabs') {
            ttsText = 'ElevenLabs';
        } else if (profile.has_google_tts_key && profile.preferred_tts_service === 'google_cloud') {
            ttsText = 'Google Cloud TTS';
        } else if (profile.preferred_tts_service === 'google') {
            ttsText = 'Google TTS (Free)';
        }
        ttsService.textContent = ttsText;
        ttsService.className = 'status-value';
        
        // Update speed button active state
        updateSpeedButtonState(profile.preferred_voice_speed || 'normal');
    } else {
        // For guest users
        translationService.textContent = 'Google Free';
        translationService.className = 'status-value';
        ttsService.textContent = 'Google TTS';
        ttsService.className = 'status-value';
        updateSpeedButtonState('normal');
    }
}

function updateSpeedButtonState(speed) {
    // Remove active class from all voice buttons
    document.querySelectorAll('.voice-btn').forEach(btn => btn.classList.remove('active'));
    
    // Add active class to current speed button
    const speedMap = {
        'fast': 'fastTtsBtn',
        'normal': 'normalTtsBtn',
        'slow': 'slowTtsBtn'
    };
    
    const activeButton = document.getElementById(speedMap[speed]);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

function updateButtonServiceStatus(service, type, speed = null) {
    // Update service status badges on buttons
    const serviceClasses = {
        'google_official': 'google',
        'google': 'google', 
        'groq': 'groq',
        'elevenlabs': 'elevenlabs',
        'browser': 'browser',
        'basic': 'basic'
    };
    
    const serviceLabels = {
        'google_official': 'G+',
        'google': 'G',
        'google_cloud': 'GC',
        'groq': 'AI',
        'elevenlabs': 'AI+',
        'browser': 'B',
        'basic': 'Dict'
    };
    
    if (type === 'translation') {
        const translateStatus = document.getElementById('translateStatus');
        if (translateStatus) {
            translateStatus.textContent = serviceLabels[service] || service;
            translateStatus.className = `btn-status active ${serviceClasses[service] || ''}`;
        }
    } else if (type === 'tts') {
        // Update all voice button status badges
        const statusElements = ['fastTtsStatus', 'normalTtsStatus', 'slowTtsStatus'];
        statusElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = serviceLabels[service] || service;
                element.className = `btn-status active ${serviceClasses[service] || ''}`;
            }
        });
    }
}

function updateServiceStatusAfterAction(service, type) {
    // Update main status bar
    const element = document.getElementById(type === 'translation' ? 'currentTranslationService' : 'currentTtsService');
    
    const serviceNames = {
        'google_official': 'Google Official',
        'google': 'Google Free',
        'google_cloud': 'Google Cloud TTS',
        'groq': 'Groq AI',
        'elevenlabs': 'ElevenLabs',
        'browser': 'Browser TTS',
        'basic': 'Basic Dictionary'
    };
    
    if (element) {
        element.textContent = serviceNames[service] || service;
        element.className = 'status-value';
    }
    
    // Update button status badges
    updateButtonServiceStatus(service, type);
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Check for saved auth token
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        updateUIForLoggedInUser();
        loadHistory(); // Load user's study history from database
    } else {
        loadHistory(); // Load local storage history for guests
    }
    
    // Initialize service status
    updateServiceStatus();
    
    // Add speed button event listeners
    document.getElementById('fastTtsBtn').addEventListener('click', () => setVoiceSpeed('fast'));
    document.getElementById('normalTtsBtn').addEventListener('click', () => setVoiceSpeed('normal'));
    document.getElementById('slowTtsBtn').addEventListener('click', () => setVoiceSpeed('slow'));
});

function setVoiceSpeed(speed) {
    const text = englishText.value.trim();
    if (!text) {
        alert('Please enter English text!');
        return;
    }
    
    currentVoiceSpeed = speed;
    updateSpeedButtonState(speed);
    
    // Play TTS with selected speed
    playTTS(text, speed);
    
    // If user is logged in, save the preference
    if (currentUser && authToken) {
        fetch(`${API_BASE_URL}/auth/profile/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${authToken}`
            },
            body: JSON.stringify({
                preferred_voice_speed: speed
            })
        }).catch(error => console.error('Error saving voice speed:', error));
    }
}