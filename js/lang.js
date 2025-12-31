        const body = document.body;
        const btnEn = document.getElementById('lang-en');
        const btnJa = document.getElementById('lang-ja');

        // Language
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

        // Navigation
        const navLinks = document.querySelectorAll('[data-nav]');
        const pageSections = document.querySelectorAll('.page-section');

        function showPage(pageId) {
            pageSections.forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById('page-' + pageId).classList.add('active');

            navLinks.forEach(link => {
                if (link.tagName === 'A') {
                    link.classList.remove('active');
                    if (link.getAttribute('data-nav') === pageId) {
                        link.classList.add('active');
                    }
                }
            });

            window.scrollTo(0, 0);
        }

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pageId = link.getAttribute('data-nav');
                showPage(pageId);
            });
        });

        // Initialize
        const savedLang = localStorage.getItem('lang');
        if (savedLang) {
            setLang(savedLang);
        } else if (navigator.language.startsWith('ja')) {
            setLang('ja');
        }
