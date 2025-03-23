document.addEventListener('DOMContentLoaded', function() {
    const videoUploadInput = document.getElementById('video-upload');
    const videoPlayer = document.getElementById('video-player');
    const videoPreviewContainer = document.getElementById('video-preview-container');
    const uploadArea = document.querySelector('.upload-area');
    const removeButton = document.querySelector('#remove-button');
    const uploadNowButton = document.querySelector('#upload-now');
    const uploadStatus = document.getElementById('upload-status');
    const processedVideoContainer = document.getElementById('processed-video-container');
    const processedVideoPlayer = document.getElementById('processed-video');
    const downloadButton = document.getElementById('download-button');
    
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('[name="csrf-token"]').content;

    // Handle file selection via file input
    videoUploadInput.addEventListener('change', handleFileSelection);
    
    // Handle drag and drop
    const dropArea = document.getElementById('drop-area');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('highlight');
    }

    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Handle file drop
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0 && files[0].type.startsWith('video/')) {
            videoUploadInput.files = files;
            handleFileSelection({ target: videoUploadInput });
        } else {
            alert('Please drop a valid video file.');
        }
    }

    function handleFileSelection(event) {
        const videoFile = event.target.files[0];

        if (videoFile) {
            // Check if the selected file is a video
            if (!videoFile.type.startsWith('video/')) {
                alert('Please select a valid video file.');
                return;
            }
            
            // Check file size (50MB limit)
            if (videoFile.size > 50 * 1024 * 1024) {
                alert('File size exceeds the maximum limit of 50MB.');
                return;
            }

            // Preview the video with a fade-in animation
            const videoURL = URL.createObjectURL(videoFile);
            videoPlayer.src = videoURL;
            
            // Add fade-in animation
            videoPreviewContainer.style.opacity = '0';
            videoPreviewContainer.style.display = 'block';
            
            // Trigger reflow for animation to work
            videoPreviewContainer.offsetHeight;
            
            // Apply the fade-in animation
            videoPreviewContainer.style.transition = 'opacity 0.5s ease';
            videoPreviewContainer.style.opacity = '1';
            
            uploadArea.style.display = 'none';

            // Reset button text if it was changed
            uploadNowButton.innerHTML = '<span class="material-icons">publish</span> Upload & Process';
            
            // Add button animation on hover
            applyButtonAnimation();

            // Store file in a global variable for later upload
            window.selectedVideoFile = videoFile;
        }
    }

    // Function to apply button hover/click animations
    function applyButtonAnimation() {
        // Adding pulse animation for the upload button
        uploadNowButton.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        uploadNowButton.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        uploadNowButton.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    }

    uploadNowButton.addEventListener('click', function() {
        if (uploadNowButton.innerHTML.includes('Process Another Video')) {
            // If the button is in "Process Another Video" state, reload the page
            window.location.reload();
        } else {
            // Otherwise, proceed with uploading the video
            if (window.selectedVideoFile) {
                uploadVideo(window.selectedVideoFile);
            }
        }
    });
    

    // Function to reset the interface for uploading another video
    function resetInterface() {
        // Fade out effect
        videoPreviewContainer.style.opacity = '0';
        
        setTimeout(() => {
            videoUploadInput.value = '';
            videoPreviewContainer.style.display = 'none';
            uploadArea.style.display = 'block';
            uploadStatus.style.display = 'none';
            processedVideoContainer.style.display = 'none';
            
            // Reset video sources
            videoPlayer.src = '';
            processedVideoPlayer.src = '';
            
            // Clear stored file
            window.selectedVideoFile = null;
            
            // Fade in upload area
            uploadArea.style.opacity = '0';
            uploadArea.style.transition = 'opacity 0.5s ease';
            
            // Trigger reflow
            uploadArea.offsetHeight;
            
            uploadArea.style.opacity = '1';
        }, 500); // Wait for fade-out to complete
    }

    // Function to upload the video to the server
    function uploadVideo(videoFile) {
        const formData = new FormData();
        formData.append('video', videoFile);

        // Show upload status with fade-in
        uploadStatus.style.opacity = '0';
        uploadStatus.style.display = 'block';
        
        setTimeout(() => {
            uploadStatus.style.transition = 'opacity 0.5s ease';
            uploadStatus.style.opacity = '1';
        }, 10);
        
        // Disable button during upload
        uploadNowButton.disabled = true;
        uploadNowButton.innerHTML = '<span class="material-icons">hourglass_empty</span> Uploading...';
        uploadNowButton.style.backgroundColor = '#8892d6'; // Lighter color to indicate disabled state

        fetch('/upload_video/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                uploadStatus.innerHTML = '<p><span class="material-icons">check_circle</span> Upload complete. Processing video...</p>';
                
                // Process the video after upload
                processUploadedVideo(data.video_path);
            } else {
                uploadStatus.innerHTML = '<p><span class="material-icons">error</span> Error uploading video: ' + (data.error || 'Unknown error') + '</p>';
                uploadNowButton.disabled = false;
                uploadNowButton.innerHTML = '<span class="material-icons">publish</span> Upload & Process';
                uploadNowButton.style.backgroundColor = '#5e72e4'; // Reset button color
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = '<p><span class="material-icons">error</span> Error uploading video: ' + error.message + '</p>';
            uploadNowButton.disabled = false;
            uploadNowButton.innerHTML = '<span class="material-icons">publish</span> Upload & Process';
            uploadNowButton.style.backgroundColor = '#5e72e4'; // Reset button color
        });
    }

    // Function to start processing the uploaded video (dehazing)
    function processUploadedVideo(videoPath) {
        uploadStatus.innerHTML = '<p><span class="material-icons spin">auto_fix_high</span> Processing video... This may take a few minutes.</p>';
        
        // Add spinning animation for the processing icon
        const style = document.createElement('style');
        style.innerHTML = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .spin {
                animation: spin 2s linear infinite;
                display: inline-block;
            }
        `;
        document.head.appendChild(style);
        
        fetch('/process_video/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ video_path: videoPath })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                uploadStatus.innerHTML = '<p><span class="material-icons">check_circle</span> Video processed successfully!</p>';
                
                // Get the processed video URL
                const processedVideoURL = data.processed_video_path;
                
                // Set the processed video source
                videoPlayer.pause();
                
                // Add transition effect to the video container
                videoPreviewContainer.style.transition = 'opacity 0.5s ease';
                videoPreviewContainer.style.opacity = '0';
                
                setTimeout(() => {
                    // Replace the original video with processed video
                    videoPlayer.src = processedVideoURL;
                    videoPlayer.load();
                    videoPlayer.play();
                    
                    // Update preview header
                    const previewHeader = videoPreviewContainer.querySelector('.preview-header h3');
                    previewHeader.textContent = 'Processed Video';
                    
                    // Show download button next to the video controls
                    const videoControls = videoPreviewContainer.querySelector('.video-controls');
                    downloadButton.style.display = 'inline-block';
                    downloadButton.href = processedVideoURL;
                    
                    // Fixed: Move the download button to a better position
                    if (!videoControls.querySelector('#download-button')) {
                        videoControls.appendChild(downloadButton);
                    }
                    
                    // Change button text to "Process Another Video"
                    uploadNowButton.innerHTML = '<span class="material-icons">refresh</span> Process Another Video';
                    
                    // Fade the video back in
                    videoPreviewContainer.style.opacity = '1';
                    
                    // Re-enable the button
                    uploadNowButton.disabled = false;
                    uploadNowButton.style.backgroundColor = '#5e72e4'; // Reset button color
                    
                    // Hide the processed video container (not needed since we're replacing)
                    processedVideoContainer.style.display = 'none';
                }, 500);
                
            } else {
                uploadStatus.innerHTML = '<p><span class="material-icons">error</span> Error processing video: ' + (data.error || 'Unknown error') + '</p>';
                uploadNowButton.disabled = false;
                uploadNowButton.innerHTML = '<span class="material-icons">publish</span> Upload & Process';
                uploadNowButton.style.backgroundColor = '#5e72e4'; // Reset button color
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = '<p><span class="material-icons">error</span> Error processing video: ' + error.message + '</p>';
            uploadNowButton.disabled = false;
            uploadNowButton.innerHTML = '<span class="material-icons">publish</span> Upload & Process';
            uploadNowButton.style.backgroundColor = '#5e72e4'; // Reset button color
        });
    }

    // Handle the remove button click
    removeButton.addEventListener('click', function() {
        // Instead of resetInterface(), reload the page for consistency
        window.location.reload();
    });
});