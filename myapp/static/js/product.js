const container = document.getElementById('product-container-custom');

// ✅ Define imageBaseUrl before using it
const imageBaseUrl = container.getAttribute('data-image-url');
const redirectBaseUrl = window.location.href.endsWith('/') ? window.location.href : window.location.href + '/';

const data = [
    { 
        name: 'Image Dehazer',
        icon: `${imageBaseUrl}image.png`,
        grad: '#0fcf7b, #0c9f30',
        link: `${redirectBaseUrl}image` // ✅ Redirect to Google
    },
    { 
        name: 'Video Dehazer',
        icon: `${imageBaseUrl}video.png`,
        grad: '#f7256e, #cc0c48',
        link: `${redirectBaseUrl}video` // ✅ Redirect to ChatGPT
    },
    { 
        name: 'Real-Time Dehazer',
        icon: `${imageBaseUrl}camera.png`,
        grad: '#f7ea1f, #f87d2c',
        link: `${redirectBaseUrl}camera` // ✅ Redirect to YouTube
    }
];

function createPricingCards() {
    const n = data.length;

    data.forEach((plan, i) => {
        const article = document.createElement('article');
        article.className = 'product-card-custom';
        article.style.setProperty('--custom-i', i);
        article.style.setProperty('--custom-n', n);

        const header = document.createElement('header');
        header.className = 'product-header-custom';
        header.style.setProperty('--custom-grad', plan.grad);

        // ✅ Image/Icon
        const icon = document.createElement('img');
        icon.className = 'product-icon-custom';
        icon.src = plan.icon;
        icon.alt = plan.name;

        // ✅ Title
        const title = document.createElement('h3');
        title.className = 'product-title-custom';
        title.textContent = plan.name;

        // ✅ Bottom Border
        const border = document.createElement('div');
        border.className = 'product-border-custom';

        const section = document.createElement('section');
        section.className = 'product-section-custom';

        // ✅ Button with redirection
        const button = document.createElement('button');
        button.className = 'product-button-custom';
        button.textContent = 'Click to Dehaze';
        button.onclick = () => window.location.href = plan.link; // ✅ Redirect to the specified link

        header.appendChild(icon);
        header.appendChild(title);
        header.appendChild(border);
        section.appendChild(button);
        article.appendChild(header);
        article.appendChild(section);
        container.appendChild(article);
    });
}

document.addEventListener('DOMContentLoaded', createPricingCards);
