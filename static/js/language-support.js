// Multi-language support JavaScript

let currentLanguage = 'en';
let translations = {};

// Initialize language support
function initLanguageSupport() {
    // Get current language from page or default to English
    if (typeof currentLanguage === 'undefined') {
        currentLanguage = 'en';
    }
    
    // Update page content if translations are available
    if (typeof translations !== 'undefined' && translations) {
        updatePageContent();
    }
}

// Load translations for a specific language
function loadTranslations(langCode) {
    if (typeof translations !== 'undefined' && translations) {
        updatePageContent();
        return;
    }
    
    fetch(`/get_translations/${langCode}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                translations = data.translations;
                currentLanguage = langCode;
                updatePageContent();
            }
        })
        .catch(error => {
            console.error('Error loading translations:', error);
        });
}

// Create language selector dropdown
function createLanguageSelector() {
    const languages = {
        'en': { name: 'English', flag: '🇬🇧' },
        'hi': { name: 'हिंदी', flag: '🇮🇳' },
        'te': { name: 'తెలుగు', flag: '🇮🇳' },
        'ta': { name: 'தமிழ்', flag: '🇮🇳' },
        'bn': { name: 'বাংলা', flag: '🇮🇳' },
        'ml': { name: 'മലയാളം', flag: '🇮🇳' }
    };
    
    // Find navigation or header to add language selector
    const nav = document.querySelector('.gov-header .nav-links') || document.querySelector('nav');
    if (!nav) return;
    
    // Create language selector HTML
    const langSelector = document.createElement('div');
    langSelector.className = 'language-selector';
    langSelector.innerHTML = `
        <div class="lang-dropdown">
            <button class="lang-btn" onclick="toggleLanguageDropdown()">
                <span class="lang-flag">${languages[currentLanguage].flag}</span>
                <span class="lang-name">${languages[currentLanguage].name}</span>
                <span class="lang-arrow">▼</span>
            </button>
            <div class="lang-options" id="langOptions" style="display: none;">
                ${Object.entries(languages).map(([code, lang]) => `
                    <div class="lang-option" onclick="changeLanguage('${code}')">
                        <span class="lang-flag">${lang.flag}</span>
                        <span class="lang-name">${lang.name}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    nav.appendChild(langSelector);
}

// Toggle language dropdown
function toggleLanguageDropdown() {
    const dropdown = document.getElementById('langOptions');
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
}

// Change language
function changeLanguage(langCode) {
    if (langCode !== currentLanguage) {
        // Redirect to set language in session
        const currentUrl = window.location.pathname + window.location.search;
        window.location.href = `/set_language/${langCode}?redirect=${encodeURIComponent(currentUrl)}`;
    }
    
    // Hide dropdown
    const dropdown = document.getElementById('langOptions');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

// Update page content with translations
function updatePageContent() {
    // Update elements with data-translate attribute
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[key]) {
            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translations[key];
            } else if (element.tagName === 'INPUT' && element.placeholder) {
                element.placeholder = translations[key];
            } else {
                element.textContent = translations[key];
            }
        }
    });
    
    // Update page title if translation exists
    if (translations.page_title) {
        document.title = translations.page_title;
    }
}

// Get translation for a key
function t(key, defaultValue = null) {
    return translations[key] || defaultValue || key;
}

// Format emergency type for display
function formatEmergencyType(type) {
    const typeTranslations = {
        'heart_attack': t('heart_attack'),
        'breathing_difficulty': t('breathing_difficulty'),
        'severe_pain': t('severe_pain'),
        'unconscious': t('unconscious'),
        'injury_accident': t('injury_accident'),
        'high_fever': t('high_fever'),
        'sos': t('sos'),
        'other': t('other')
    };
    
    return typeTranslations[type] || type;
}

// Format status for display
function formatStatus(status) {
    const statusTranslations = {
        'pending': t('pending'),
        'in_progress': t('in_progress'),
        'resolved': t('resolved')
    };
    
    return statusTranslations[status] || status;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we have language support elements
    if (document.querySelector('.language-selector') || typeof translations !== 'undefined') {
        initLanguageSupport();
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const langSelector = document.querySelector('.language-selector');
        const dropdown = document.getElementById('langOptions');
        
        if (langSelector && !langSelector.contains(event.target) && dropdown) {
            dropdown.style.display = 'none';
        }
    });
});

// Export functions for use in other scripts
window.languageSupport = {
    t: t,
    formatEmergencyType: formatEmergencyType,
    formatStatus: formatStatus,
    changeLanguage: changeLanguage,
    currentLanguage: () => currentLanguage
};