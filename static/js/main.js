// Apple-style smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initializeAnimations();
    initializeNavBar();
    initializeKeyboardNavigation();
});

// Animate cards on load with stagger effect
function initializeAnimations() {
    const cards = document.querySelectorAll('.project-card');

    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.8s cubic-bezier(0.28, 0.11, 0.32, 1), transform 0.8s cubic-bezier(0.28, 0.11, 0.32, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });

    // Animate detail page items
    const itemCards = document.querySelectorAll('.item-card');
    itemCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.6s cubic-bezier(0.28, 0.11, 0.32, 1), transform 0.6s cubic-bezier(0.28, 0.11, 0.32, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

// Apple-style navigation bar scroll effect
function initializeNavBar() {
    const navBar = document.querySelector('.nav-bar');
    if (!navBar) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        // Add shadow on scroll
        if (currentScroll > 10) {
            navBar.style.boxShadow = '0 1px 0 0 rgba(0, 0, 0, 0.1)';
        } else {
            navBar.style.boxShadow = 'none';
        }

        lastScroll = currentScroll;
    }, { passive: true });
}

// Keyboard navigation
function initializeKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // ESC key to go back
        if (e.key === 'Escape') {
            const backLink = document.querySelector('.back-link');
            if (backLink) {
                window.location.href = '/';
            }
        }

        // Arrow key navigation for cards
        const cards = Array.from(document.querySelectorAll('.project-card'));
        const activeElement = document.activeElement;
        const currentIndex = cards.indexOf(activeElement);

        if (currentIndex !== -1) {
            if (e.key === 'ArrowRight' && currentIndex < cards.length - 1) {
                e.preventDefault();
                cards[currentIndex + 1].focus();
            } else if (e.key === 'ArrowLeft' && currentIndex > 0) {
                e.preventDefault();
                cards[currentIndex - 1].focus();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                activeElement.click();
            }
        }
    });
}

// Add focus styles for accessibility
const style = document.createElement('style');
style.textContent = `
    .project-card:focus {
        outline: 2px solid var(--accent-blue);
        outline-offset: 4px;
    }

    .project-card:focus:not(:focus-visible) {
        outline: none;
    }

    /* Smooth hover transitions */
    .project-card,
    .item-card,
    .back-link,
    .nav-logo {
        transition: all 0.3s cubic-bezier(0.28, 0.11, 0.32, 1);
    }

    /* Reduced motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
`;
document.head.appendChild(style);

// Add parallax effect to hero section (subtle, Apple-style)
window.addEventListener('scroll', () => {
    const hero = document.querySelector('.hero');
    if (hero) {
        const scrolled = window.pageYOffset;
        const parallax = scrolled * 0.5;
        hero.style.transform = `translateY(${parallax}px)`;
        hero.style.opacity = 1 - (scrolled / 500);
    }
}, { passive: true });

// Performance monitoring
if (window.performance) {
    window.addEventListener('load', () => {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
    });
}

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe info cards and sections
document.querySelectorAll('.info-card, .detail-section').forEach(el => {
    observer.observe(el);
});
