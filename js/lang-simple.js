// Language switching for standalone pages (non-SPA)
const body = document.body;
const btnEn = document.getElementById('lang-en');
const btnJa = document.getElementById('lang-ja');

function setLang(lang) {
    if (lang === 'ja') {
        body.classList.add('ja');
        btnJa.classList.add('active');
        btnEn.classList.remove('active');
        document.documentElement.lang = 'ja';
    } else {
        body.classList.remove('ja');
        btnEn.classList.add('active');
        btnJa.classList.remove('active');
        document.documentElement.lang = 'en';
    }
    localStorage.setItem('lang', lang);
}

btnEn.addEventListener('click', () => setLang('en'));
btnJa.addEventListener('click', () => setLang('ja'));

// Initialize from saved preference or browser language
const savedLang = localStorage.getItem('lang');
if (savedLang) {
    setLang(savedLang);
} else if (navigator.language.startsWith('ja')) {
    setLang('ja');
}
