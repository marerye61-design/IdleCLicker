import './style.css'

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId) {
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        }
    });
});

// Simple intersection observer for reveal animations on scroll
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            // Stop observing once it has become visible
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Select elements to animate
const featureCards = document.querySelectorAll('.feature-card');
featureCards.forEach((card, index) => {
    // Add initial styles for animation via JS or use a CSS class
    (card as HTMLElement).style.opacity = '0';
    (card as HTMLElement).style.transform = 'translateY(30px)';
    (card as HTMLElement).style.transition = `all 0.6s ease ${index * 0.1}s`;
    
    // Add it to the observer
    observer.observe(card);
});

// Add a visible class handler in CSS (or via JS inline styles when intersecting)
const style = document.createElement('style');
style.textContent = `
    .feature-card.visible {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

console.log("IdleRPG promotional page loaded successfully.");
