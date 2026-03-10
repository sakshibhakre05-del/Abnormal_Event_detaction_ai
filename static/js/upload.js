const socket = io();

document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevents the page from reloading
    uploadVideo();
});

function uploadVideo() {
    const fileInput = document.getElementById('video');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    if (!fileInput.files[0]) {
        alert("Please select a video file first.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();

    // Updates the progress bar as the file is sent
    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const percent = (event.loaded / event.total) * 100;
            progressBar.style.width = percent + '%';
            progressText.innerText = `Upload progress: ${Math.round(percent)}%`;
        }
    };

    xhr.onload = () => {
        if (xhr.status === 200) {
            progressText.innerText = "Upload Complete! Starting AI processing...";
            // Optional: You can send a socket message to start the model here
            // socket.emit('start_processing', { filename: file.name });
        } else {
            progressText.innerText = "Error: Upload failed.";
        }
    };

    // Make sure your Python backend has an @app.route('/upload')
    xhr.open('POST', '/upload', true);
    xhr.send(formData);
}

// Existing detection listeners
socket.on('detection_update', (data) => {
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.innerHTML = `<h5>Latest: ${data.label} (${(data.confidence * 100).toFixed(1)}%)</h5>`;
    }
});