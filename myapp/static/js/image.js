function previewImage(input) {
    const preview = document.getElementById('previewBeforeUpload');
    const previewContainer = document.getElementById('previewContainer');
    const uploadBtn = document.getElementById('uploadBtn');
    const saveBtn = document.getElementById('saveBtn');  // Add this line
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;  // Set the preview image to the selected file
            previewContainer.style.display = 'block';  // Show the preview area
            uploadBtn.disabled = false;  // Enable the upload button
            saveBtn.disabled = false;  // Enable the save button
        }
        reader.readAsDataURL(input.files[0]);
    } else {
        previewContainer.style.display = 'none';  // Hide the preview area
        uploadBtn.disabled = true;  // Disable the upload button
        saveBtn.disabled = true;  // Disable the save button
    }
}

function uploadImage() {
    const card = document.getElementById('card');
    const preview = document.getElementById('preview');
    const previewBeforeUpload = document.getElementById('previewBeforeUpload');
    const resetButton = document.getElementById('resetButton');
    
    // Copy the preview image to the back of the card
    preview.src = previewBeforeUpload.src;
    
    // Flip the card to show the uploaded image
    card.classList.add('flip');
    
    // Display the reset button to allow uploading another image
    resetButton.style.display = 'block';
}

function resetUpload() {
    const card = document.getElementById('card');
    const input = document.getElementById('imageInput');
    const previewContainer = document.getElementById('previewContainer');
    const previewBeforeUpload = document.getElementById('previewBeforeUpload');
    const resetButton = document.getElementById('resetButton');
    const uploadBtn = document.getElementById('uploadBtn');
    
    // Remove the flip class to go back to the front of the card
    card.classList.remove('flip');
    
    // Reset the input and preview
    input.value = "";
    previewContainer.style.display = 'none';
    previewBeforeUpload.src = "";
    resetButton.style.display = 'none';
    uploadBtn.disabled = true;
}

function openInNewWindow() {
    const img = document.getElementById('preview');
    const imgWindow = window.open("", "_blank");
    imgWindow.document.write("<html><head><title>Image</title></head><body style='margin:0;display:flex;justify-content:center;align-items:center;background:#f0f0f0;height:100vh;'><img src='" + img.src + "' style='max-width:90%;max-height:90%;box-shadow:0 5px 15px rgba(0,0,0,0.1);'></body></html>");
}

function downloadImage() {
    const img = document.getElementById('preview');
    const link = document.createElement('a');
    link.href = img.src;
    link.download = 'image.' + getImageExtension(img.src);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function getImageExtension(src) {
    // Try to get the file extension from data URL
    if (src.startsWith('data:image/')) {
        const mimeType = src.split(';')[0].split(':')[1];
        return mimeType.split('/')[1] || 'png';
    }
    return 'png'; // Default extension
}

// Add event listener for file input
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('imageInput').addEventListener('change', function() {
        previewImage(this);
    });
});

function saveImage() {
    const input = document.getElementById('imageInput');
    const formData = new FormData();
    const file = input.files[0];
    
    if (!file) {
        return;  // No image selected, just exit the function
    }

    formData.append('image', file);

    // Get CSRF token from the meta tag in the HTML head
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Send the image via AJAX to the Django backend
    fetch('/save_image/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken  // Ensure the CSRF token is included in the request headers
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.file_url) {
            // Remove success alert and update the preview with the processed image (dehazed)
            const previewImage = document.getElementById('preview');
            previewImage.src = data.processed_image_url;  // Set to the dehazed image URL

            // Flip the card to show the uploaded and dehazed image
            const card = document.getElementById('card');
            card.classList.add('flip');  // Show the back side of the card

            // Display the reset button to allow uploading another image
            document.getElementById('resetButton').style.display = 'block';
        } else {
            console.error("Failed to save the image.");
        }
    })
    .catch(error => {
        console.error("An error occurred while saving the image:", error);
    });
}