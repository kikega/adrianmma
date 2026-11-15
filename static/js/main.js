(function () {
    'use strict';

    const prefersReducedMotion = () =>
        window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function escapeHtmlText(value) {
        if (!value) return '';
        const escaped = String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
        // Evita que GLightbox interprete un '.' inicial en data-description como selector CSS
        return escaped.startsWith('.') ? '&#46;' + escaped.slice(1) : escaped;
    }

    function sanitizeGalleryNodes(root) {
        const scope = root || document;
        scope.querySelectorAll('.glightbox, .glightbox-video').forEach((el) => {
            if (el.dataset.sanitized === 'true') return;
            const title = el.getAttribute('data-title');
            const description = el.getAttribute('data-description');
            if (title !== null) {
                el.setAttribute('data-title', escapeHtmlText(title));
            }
            if (description !== null) {
                el.setAttribute('data-description', escapeHtmlText(description));
            }
            el.dataset.sanitized = 'true';
        });
    }

    // 1. Navbar scroll state (passive)
    const navbar = document.getElementById('navbar');
    let scrollTicking = false;
    function updateNavbarScroll() {
        if (!navbar) return;
        navbar.classList.toggle('scrolled', window.scrollY > 50);
        scrollTicking = false;
    }
    if (navbar) {
        updateNavbarScroll();
        window.addEventListener(
            'scroll',
            () => {
                if (!scrollTicking) {
                    window.requestAnimationFrame(updateNavbarScroll);
                    scrollTicking = true;
                }
            },
            { passive: true }
        );
    }

    // 2. Mobile menu toggle with ARIA state, Escape & click-outside
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    function setMobileMenuOpen(isOpen, restoreFocus) {
        if (!mobileToggle || !mobileMenu) return;
        mobileMenu.classList.toggle('hidden', !isOpen);
        mobileToggle.setAttribute('aria-expanded', String(isOpen));
        mobileToggle.setAttribute(
            'aria-label',
            isOpen ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'
        );
        if (!isOpen && restoreFocus) {
            mobileToggle.focus();
        }
    }

    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', () => {
            const isCurrentlyOpen = mobileToggle.getAttribute('aria-expanded') === 'true';
            setMobileMenuOpen(!isCurrentlyOpen, false);
        });

        document.addEventListener('keydown', (evt) => {
            if (evt.key === 'Escape' && mobileToggle.getAttribute('aria-expanded') === 'true') {
                setMobileMenuOpen(false, true);
            }
        });

        document.addEventListener('click', (evt) => {
            if (
                mobileToggle.getAttribute('aria-expanded') === 'true' &&
                navbar &&
                !navbar.contains(evt.target)
            ) {
                setMobileMenuOpen(false, false);
            }
        });
    }

    // 3. Smooth anchor navigation preserving URL hash + service prefill
    function selectContactService(serviceKey) {
        const select = document.getElementById('contact-service');
        if (!select || !serviceKey) return;
        const hasOption = Array.from(select.options).some((opt) => opt.value === serviceKey);
        if (hasOption) {
            select.value = serviceKey;
            select.dispatchEvent(new Event('change', { bubbles: true }));
        }
        const nameInput = document.getElementById('contact-name');
        if (nameInput) {
            nameInput.focus({ preventScroll: true });
        }
    }

    document.addEventListener('click', (evt) => {
        const anchor = evt.target.closest('a[href^="#"]');
        if (!anchor) return;

        const href = anchor.getAttribute('href');
        if (!href || href === '#') return;

        const targetId = href.slice(1);
        const target = document.getElementById(targetId);
        if (!target) return;

        evt.preventDefault();
        target.scrollIntoView({
            behavior: prefersReducedMotion() ? 'auto' : 'smooth',
            block: 'start',
        });

        if (window.location.hash !== href) {
            window.history.pushState(null, '', href);
        }

        setMobileMenuOpen(false, false);

        const serviceKey = anchor.getAttribute('data-select-service');
        if (serviceKey) {
            selectContactService(serviceKey);
        }
    });

    // 4. Scrollspy for navigation links
    const navLinks = Array.from(document.querySelectorAll('#navbar a.nav-link[href^="#"]'));
    const sections = Array.from(document.querySelectorAll('main section[id]'));

    function setActiveNav(sectionId) {
        navLinks.forEach((link) => {
            const matches = link.getAttribute('href') === '#' + sectionId;
            if (matches) {
                link.setAttribute('aria-current', 'location');
                link.classList.add('text-white');
                link.classList.remove('text-gray-300');
            } else {
                link.removeAttribute('aria-current');
                link.classList.remove('text-white');
                if (!link.classList.contains('btn-primary') && !link.classList.contains('text-red-400')) {
                    link.classList.add('text-gray-300');
                }
            }
        });
    }

    if ('IntersectionObserver' in window && sections.length && navLinks.length) {
        const sectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setActiveNav(entry.target.id);
                    }
                });
            },
            {
                rootMargin: '-25% 0px -60% 0px',
                threshold: 0,
            }
        );
        sections.forEach((section) => sectionObserver.observe(section));
    }

    // 5. Gallery Tabs (accessible ARIA tablist + keyboard arrows) & Show All Photos
    const btnFotos = document.getElementById('btn-fotos');
    const btnVideos = document.getElementById('btn-videos');
    const panelFotos = document.getElementById('gallery-fotos');
    const panelVideos = document.getElementById('gallery-videos');

    const ACTIVE_TAB_CLASSES =
        'px-8 py-3 bg-gradient-to-r from-red-900 to-red-700 text-white rounded font-display uppercase tracking-wider cursor-pointer transition';
    const INACTIVE_TAB_CLASSES =
        'px-8 py-3 bg-gray-800 text-gray-200 rounded font-display uppercase tracking-wider hover:bg-gray-700 hover:text-white transition cursor-pointer';

    function showGallery(type) {
        if (!btnFotos || !btnVideos || !panelFotos || !panelVideos) return;
        const showPhotos = type === 'fotos';

        panelFotos.classList.toggle('hidden', !showPhotos);
        panelVideos.classList.toggle('hidden', showPhotos);

        btnFotos.setAttribute('aria-selected', String(showPhotos));
        btnVideos.setAttribute('aria-selected', String(!showPhotos));
        btnFotos.setAttribute('tabindex', showPhotos ? '0' : '-1');
        btnVideos.setAttribute('tabindex', showPhotos ? '-1' : '0');

        btnFotos.className = showPhotos ? ACTIVE_TAB_CLASSES : INACTIVE_TAB_CLASSES;
        btnVideos.className = showPhotos ? INACTIVE_TAB_CLASSES : ACTIVE_TAB_CLASSES;
    }

    if (btnFotos && btnVideos) {
        btnFotos.addEventListener('click', () => showGallery('fotos'));
        btnVideos.addEventListener('click', () => showGallery('videos'));

        [btnFotos, btnVideos].forEach((tab, idx, tabs) => {
            tab.addEventListener('keydown', (evt) => {
                if (evt.key === 'ArrowRight' || evt.key === 'ArrowLeft') {
                    evt.preventDefault();
                    const nextIdx = idx === 0 ? 1 : 0;
                    const nextTab = tabs[nextIdx];
                    showGallery(nextTab.id === 'btn-fotos' ? 'fotos' : 'videos');
                    nextTab.focus();
                } else if (evt.key === 'Home') {
                    evt.preventDefault();
                    showGallery('fotos');
                    btnFotos.focus();
                } else if (evt.key === 'End') {
                    evt.preventDefault();
                    showGallery('videos');
                    btnVideos.focus();
                }
            });
        });
    }

    const toggleMorePhotosBtn = document.getElementById('btn-toggle-more-photos');
    const extraPhotosContainer = document.getElementById('gallery-fotos-extra');
    if (toggleMorePhotosBtn && extraPhotosContainer) {
        toggleMorePhotosBtn.addEventListener('click', () => {
            const willExpand = extraPhotosContainer.classList.contains('hidden');
            extraPhotosContainer.classList.toggle('hidden', !willExpand);
            toggleMorePhotosBtn.setAttribute('aria-expanded', String(willExpand));
            const totalCount = toggleMorePhotosBtn.dataset.totalCount || '';
            toggleMorePhotosBtn.textContent = willExpand
                ? 'Mostrar menos fotos'
                : `Ver todas las fotos (${totalCount})`;
        });
    }

    // 6. Privacy-friendly interactive Google Maps loader
    const mapLoadBtn = document.getElementById('map-load-btn');
    const mapContainer = document.getElementById('map-container');
    if (mapLoadBtn && mapContainer) {
        mapLoadBtn.addEventListener('click', () => {
            const iframe = document.createElement('iframe');
            iframe.src =
                'https://maps.google.com/maps?hl=es&q=Climent+Club,+C.+Burgos,+8,+03015+Alicante&t=&z=16&ie=UTF8&iwloc=&output=embed';
            iframe.title = 'Plano interactivo de ubicación de Climent Club en Google Maps';
            iframe.className = 'w-full h-full border-0';
            iframe.loading = 'lazy';
            iframe.referrerPolicy = 'strict-origin-when-cross-origin';
            iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-popups');
            mapContainer.replaceChildren(iframe);
            iframe.focus();
        });
    }

    // 7. GLightbox initialization (with sanitized titles/descriptions) & missing image fallback
    document.addEventListener(
        'error',
        (evt) => {
            const img = evt.target;
            if (!img || img.tagName !== 'IMG') return;
            const galleryItem = img.closest('.gallery-item');
            if (galleryItem) {
                galleryItem.classList.add('hidden');
            }
        },
        true
    );

    let lightboxPhotos = null;
    let lightboxVideos = null;

    if (typeof GLightbox === 'function') {
        sanitizeGalleryNodes(document);

        lightboxPhotos = GLightbox({
            selector: '.glightbox',
            touchNavigation: true,
            loop: true,
            zoomable: true,
        });

        lightboxVideos = GLightbox({
            selector: '.glightbox-video',
            touchNavigation: true,
            loop: true,
            zoomable: true,
            autoplayVideos: true,
        });
    }

    // 8. HTMX 422/429 swap handling, network fallback & focus management
    document.body.addEventListener('htmx:beforeSwap', (evt) => {
        const status = evt.detail.xhr ? evt.detail.xhr.status : 0;
        if (status === 422 || status === 429) {
            evt.detail.shouldSwap = true;
            evt.detail.isError = false;
        }
    });

    document.body.addEventListener('htmx:responseError', (evt) => {
        const status = evt.detail.xhr ? evt.detail.xhr.status : 0;
        if (status === 422 || status === 429) return;
        const container = document.getElementById('contact-form-container');
        if (!container) return;
        let errBanner = container.querySelector('#contact-network-error');
        if (!errBanner) {
            errBanner = document.createElement('div');
            errBanner.id = 'contact-network-error';
            errBanner.setAttribute('role', 'alert');
            errBanner.className =
                'mt-4 p-3 bg-red-900/40 border border-red-600 rounded text-red-200 text-sm';
            errBanner.textContent =
                'No se pudo enviar el mensaje en este momento. Por favor, inténtalo de nuevo en unos segundos.';
            const form = container.querySelector('form');
            (form || container).appendChild(errBanner);
        }
    });

    document.body.addEventListener('htmx:sendError', () => {
        const container = document.getElementById('contact-form-container');
        if (!container) return;
        let errBanner = container.querySelector('#contact-network-error');
        if (!errBanner) {
            errBanner = document.createElement('div');
            errBanner.id = 'contact-network-error';
            errBanner.setAttribute('role', 'alert');
            errBanner.className =
                'mt-4 p-3 bg-red-900/40 border border-red-600 rounded text-red-200 text-sm';
            errBanner.textContent =
                'Error de conexión al enviar el mensaje. Comprueba tu red e inténtalo de nuevo.';
            const form = container.querySelector('form');
            (form || container).appendChild(errBanner);
        }
    });

    document.body.addEventListener('htmx:afterSwap', (evt) => {
        sanitizeGalleryNodes(evt.target);
        if (lightboxPhotos) lightboxPhotos.reload();
        if (lightboxVideos) lightboxVideos.reload();

        const target = evt.detail && evt.detail.target;
        if (target && target.id === 'contact-form-container') {
            const successHeading = target.querySelector('#contact-success-heading');
            const firstInvalid = target.querySelector('[aria-invalid="true"]');
            const alertBox = target.querySelector('[role="alert"]');
            const nameInput = target.querySelector('#contact-name');

            if (successHeading) {
                successHeading.focus();
            } else if (firstInvalid) {
                firstInvalid.focus();
            } else if (alertBox) {
                alertBox.focus();
            } else if (nameInput) {
                nameInput.focus();
            }
        }
    });

    // 9. Clear field error indicators on user input (non-intrusive UX)
    document.body.addEventListener('input', (evt) => {
        const field = evt.target;
        if (!field || !field.closest('#contact-form-container')) return;
        if (field.getAttribute('aria-invalid') === 'true' && field.checkValidity()) {
            field.removeAttribute('aria-invalid');
        }
    });
})();
