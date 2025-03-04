// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Logo animation
    const logoIcon = document.querySelector('.logo-icon');
    logoIcon.style.opacity = '0';
    setTimeout(() => {
        logoIcon.style.transition = 'opacity 1.5s ease, transform 1.5s ease';
        logoIcon.style.opacity = '1';
        logoIcon.style.transform = 'scale(1)';
    }, 300);

    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            this.classList.toggle('active');
            
            if (navLinks.style.display === 'flex') {
                navLinks.style.opacity = '0';
                setTimeout(() => {
                    navLinks.style.display = 'none';
                }, 300);
            } else {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '100%';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.padding = '1rem';
                navLinks.style.backgroundColor = 'var(--white)';
                navLinks.style.boxShadow = '0 10px 15px rgba(0, 0, 0, 0.1)';
                navLinks.style.zIndex = '1000';
                navLinks.style.opacity = '0';
                navLinks.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {
                    navLinks.style.opacity = '1';
                }, 10);
            }
        });
    }

    // Testimonial slider
    const testimonials = document.querySelectorAll('.testimonial');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentSlide = 0;

    function showSlide(n) {
        // Hide all slides
        testimonials.forEach(testimonial => {
            testimonial.classList.remove('active');
        });
        
        // Remove active class from all dots
        dots.forEach(dot => {
            dot.classList.remove('active');
        });
        
        // Show the current slide and activate the corresponding dot
        testimonials[n].classList.add('active');
        dots[n].classList.add('active');
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % testimonials.length;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + testimonials.length) % testimonials.length;
        showSlide(currentSlide);
    }

    // Add event listeners to dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentSlide = index;
            showSlide(currentSlide);
        });
    });

    // Add event listeners to prev/next buttons
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', prevSlide);
        nextBtn.addEventListener('click', nextSlide);
    }

    // Auto slide every 5 seconds
    setInterval(nextSlide, 5000);

    // Scroll animations
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.feature-box, .step, .section-title');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 100) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Set initial state for scroll animations
    const elementsToAnimate = document.querySelectorAll('.feature-box, .step, .section-title');
    elementsToAnimate.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    });

    // Run animation on scroll
    window.addEventListener('scroll', animateOnScroll);
    // Run once on page load
    animateOnScroll();

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add active class to nav links based on scroll position
    function setActiveNavLink() {
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('nav a');
        
        let currentSection = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                currentSection = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSection}`) {
                link.classList.add('active');
            }
        });
    }
    
    window.addEventListener('scroll', setActiveNavLink);

    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero');
    
    window.addEventListener('scroll', function() {
        if (heroSection) {
            const scrollPosition = window.scrollY;
            heroSection.style.backgroundPosition = `center ${scrollPosition * 0.4}px`;
        }
    });

    // Interactive feature boxes
    const featureBoxes = document.querySelectorAll('.feature-box');
    
    featureBoxes.forEach(box => {
        box.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-15px)';
            this.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.15)';
        });
        
        box.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.1)';
        });
    });
});