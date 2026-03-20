// Enhanced Multi-language support JavaScript
// This script properly updates page content when language is changed

(function() {
    'use strict';
    
    console.log('Language support script loaded');
    
    // Get current language from page meta tag or default to English
    let currentLanguage = document.documentElement.lang || 'en';
    let translations = {};
    
    // Initialize translations from server-rendered data
    function initTranslations() {
        console.log('=== Language Support Initialization ===');
        console.log('Current page URL:', window.location.href);
        
        // Get translations from window object
        if (window.TRANSLATIONS) {
            translations = window.TRANSLATIONS;
            currentLanguage = window.CURRENT_LANG || currentLanguage;
            console.log('✓ Loaded translations for language:', currentLanguage);
            console.log('✓ Total translation keys:', Object.keys(translations).length);
        } else {
            console.warn('✗ No translations found in window.TRANSLATIONS');
            return;
        }
        
        // Update page content immediately
        updatePageContent();
        
        // Setup language dropdown
        setupLanguageDropdown();
        
        console.log('=== Initialization Complete ===');
    }
    
    // Setup language dropdown functionality
    function setupLanguageDropdown() {
        const langBtn = document.getElementById('langBtn');
        const langDropdown = document.getElementById('langDropdown');
        
        if (!langBtn || !langDropdown) {
            return;
        }
        
        // Toggle dropdown on button click
        langBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            const newState = !isExpanded;
            
            if (newState) {
                langDropdown.classList.add('lang-switcher__dropdown--show');
            } else {
                langDropdown.classList.remove('lang-switcher__dropdown--show');
            }
            
            this.setAttribute('aria-expanded', newState);
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!langBtn.contains(e.target) && !langDropdown.contains(e.target)) {
                langDropdown.classList.remove('lang-switcher__dropdown--show');
                langBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    // Update page content with translations
    function updatePageContent() {
        if (!translations || Object.keys(translations).length === 0) {
            return;
        }
        
        // Update elements with data-translate attribute
        const elements = document.querySelectorAll('[data-translate]');
        
        elements.forEach(element => {
            const key = element.getAttribute('data-translate');
            
            if (!translations[key]) {
                return;
            }
            
            const translation = translations[key];
            
            if (element.tagName === 'INPUT') {
                if (element.type === 'submit' || element.type === 'button') {
                    element.value = translation;
                } else if (element.placeholder !== undefined) {
                    element.placeholder = translation;
                }
            } else if (element.tagName === 'TEXTAREA') {
                if (element.placeholder !== undefined) {
                    element.placeholder = translation;
                }
            } else if (element.tagName === 'OPTION') {
                element.textContent = translation;
            } else {
                element.textContent = translation;
            }
        });
        
        // Update page title
        if (translations.page_title) {
            document.title = translations.page_title;
        }
        
        // Update HTML lang attribute
        document.documentElement.lang = currentLanguage;
    }
    
    // Export function globally so it can be called from inline script
    window.initTranslations = initTranslations;
    
    // Export functions globally
    window.languageSupport = {
        currentLanguage: () => currentLanguage,
        updatePageContent: updatePageContent,
        translations: () => translations
    };
    
})();
