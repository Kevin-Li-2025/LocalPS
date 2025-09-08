// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const previewSection = document.getElementById('previewSection');
const originalImage = document.getElementById('originalImage');
const processedImage = document.getElementById('processedImage');
const downloadBtn = document.getElementById('downloadBtn');
const newUploadBtn = document.getElementById('newUploadBtn');
const loadingOverlay = document.getElementById('loadingOverlay');

// Current processed filename
let currentProcessedFilename = '';

// Drag and drop upload functionality
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// Handle file selection
function handleFileSelect(file) {
    // Check file type
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file!');
        return;
    }

    // Check file size (16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('File size cannot exceed 16MB!');
        return;
    }

    // Display original image preview
    const reader = new FileReader();
    reader.onload = (e) => {
        originalImage.src = e.target.result;
        uploadFile(file);
    };
    reader.readAsDataURL(file);
}

// Upload file to server
function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Display loading animation and progress steps
    loadingOverlay.style.display = 'flex';
    updateProgress(1, 'Starting background recognition model...');
    simulateProgress();

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        loadingOverlay.style.display = 'none';

        if (data.success) {
            currentProcessedFilename = data.processed_filename;
            processedImage.src = `/processed/${data.processed_filename}`;

            // Add image loading error handling
            processedImage.onerror = function() {
                alert('Image loading failed, please try again later');
                loadingOverlay.style.display = 'none';
            };

            processedImage.onload = function() {
                // Image loaded successfully, hide loading animation
                loadingOverlay.style.display = 'none';

                // Hide upload area, show preview area
                uploadArea.style.display = 'none';
                previewSection.style.display = 'block';

                // Scroll to preview area
                previewSection.scrollIntoView({ behavior: 'smooth' });
            };
        } else {
            alert('Processing failed: ' + data.error);
        }
    })
    .catch(error => {
        loadingOverlay.style.display = 'none';
        console.error('Upload error:', error);
        alert('Upload failed: ' + error.message + '\nPlease check your network connection or refresh the page and try again');
    });
}

// Download processed image
downloadBtn.addEventListener('click', () => {
    if (currentProcessedFilename) {
        const link = document.createElement('a');
        link.href = `/download/${currentProcessedFilename}`;
        link.download = 'background_removed_result.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});

// Upload new image
newUploadBtn.addEventListener('click', () => {
    // Reset state
    fileInput.value = '';
    currentProcessedFilename = '';
    originalImage.src = '';
    processedImage.src = '';

    // Show upload area, hide preview area
    uploadArea.style.display = 'block';
    previewSection.style.display = 'none';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Error handling
window.addEventListener('unhandledrejection', (event) => {
    loadingOverlay.style.display = 'none';
    console.error('Unhandled promise rejection:', event.reason);
});

// Add some animation effects
function addAnimation() {
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

    // Add animation to feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Update progress display
function updateProgress(step, text) {
    const loadingText = document.getElementById('loadingText');
    const steps = ['step1', 'step2', 'step3', 'step4'];
    
    if (loadingText) {
        loadingText.textContent = text;
    }
    
    // 更新步骤状态
    steps.forEach((stepId, index) => {
        const stepElement = document.getElementById(stepId);
        if (stepElement) {
            stepElement.classList.remove('active', 'completed');
            if (index < step) {
                stepElement.classList.add('completed');
            } else if (index === step - 1) {
                stepElement.classList.add('active');
            }
        }
    });
}

// Simulate processing progress
function simulateProgress() {
    setTimeout(() => updateProgress(2, 'Precisely identifying background areas...'), 1000);
    setTimeout(() => updateProgress(3, 'Preserving subject, removing background...'), 3000);
    setTimeout(() => updateProgress(4, 'Transparent background generation complete!'), 5000);
}

// Initialize after page load
document.addEventListener('DOMContentLoaded', () => {
    addAnimation();
});
