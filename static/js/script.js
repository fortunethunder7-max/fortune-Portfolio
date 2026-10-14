// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}

// Typing animation
const typedEl = document.getElementById('typed');
if (typedEl) {
    const roles = [
        'Cybersecurity Professional',
        'Web Developer (Python & Flask)',
        'Web Designer',
        'Digital Marketer',
        'Programmer & Coder'
    ];
    let roleIndex = 0;
    let charIndex = 0;
    let deleting = false;

    function type() {
        const current = roles[roleIndex];
        if (!deleting) {
            typedEl.textContent = current.substring(0, charIndex + 1);
            charIndex++;
            if (charIndex === current.length) {
                deleting = true;
                setTimeout(type, 1800);
                return;
            }
        } else {
            typedEl.textContent = current.substring(0, charIndex - 1);
            charIndex--;
            if (charIndex === 0) {
                deleting = false;
                roleIndex = (roleIndex + 1) % roles.length;
            }
        }
        setTimeout(type, deleting ? 50 : 100);
    }
    type();
}

// Animate skill bars on scroll
const skillFills = document.querySelectorAll('.skill-fill');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const fill = entry.target;
            const width = fill.getAttribute('data-width');
            fill.style.width = width + '%';
            observer.unobserve(fill);
        }
    });
}, { threshold: 0.3 });

skillFills.forEach(fill => observer.observe(fill));

// Auto-hide flash messages
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
        el.style.transition = 'opacity 0.5s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    });
}, 5000);