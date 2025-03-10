document.addEventListener('DOMContentLoaded', function() {
    const videoUploadInput = document.getElementById('video-upload');
    const videoPlayer = document.getElementById('video-player');
    const videoPreviewContainer = document.getElementById('video-preview-container');
    const uploadArea = document.querySelector('.upload-area');
    const removeButton = document.querySelector('#remove-button');
    const csrfToken = document.querySelector('[name="csrf-token"]').content;

    // Handle file selection
    videoUploadInput.addEventListener('change', handleFileSelection);

    function handleFileSelection(event) {
        const videoFile = event.target.files[0];
        
        if (videoFile) {
            // Check if the selected file is a video
            if (!videoFile.type.startsWith('video/')) {
                alert('Please select a valid video file.');
                return;
            }

            // Preview the video
            const videoURL = URL.createObjectURL(videoFile);
            videoPlayer.src = videoURL;
            videoPreviewContainer.style.display = 'block';
            uploadArea.style.display = 'none';

            // Automatically upload the video after selection
            uploadVideo(videoFile);
        }
    }

    // Function to upload the video to the server
    function uploadVideo(videoFile) {
        const formData = new FormData();
        formData.append('video', videoFile);

        fetch('/upload_video/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken // Add CSRF token to headers
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("ok");
                
            } else {
                alert('Error uploading video: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Error uploading video: ' + error.message);
        });
    }

    // Handle the remove button click
    removeButton.addEventListener('click', function() {
        videoUploadInput.value = '';
        videoPreviewContainer.style.display = 'none';
        uploadArea.style.display = 'block';
    });
});
