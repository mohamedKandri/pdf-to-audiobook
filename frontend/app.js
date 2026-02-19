// ===== Configuration =====
const API_BASE_URL = 'http://127.0.0.1:8000';

// ===== DOM Elements =====
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.querySelector('.upload-section');
const statusSection = document.getElementById('statusSection');
const statusText = document.getElementById('statusText');
const statusDetail = document.getElementById('statusDetail');
const progressFill = document.getElementById('progressFill');
const playerSection = document.getElementById('playerSection');
const fileName = document.getElementById('fileName');
const audioPlayer = document.getElementById('audioPlayer');
const playPauseBtn = document.getElementById('playPauseBtn');
const stopBtn = document.getElementById('stopBtn');
const speedSelect = document.getElementById('speedSelect');
const downloadBtn = document.getElementById('downloadBtn');
const convertNewBtn = document.getElementById('convertNewBtn');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');

// ===== State =====
let currentAudioUrl = '';
let currentFilename = '';

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    setupUploadZone();
    setupAudioPlayer();
    setupButtons();
    console.log('🎧 PDF to Audiobook Frontend Ready');
    console.log('Connecting to Backend:', API_BASE_URL);
});

// ===== Upload Zone Functions =====
function setupUploadZone() {
    // Click to upload
    uploadZone.addEventListener('click', () => fileInput.click());
    
    // File selection
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFileUpload(file);
    });
    
    // Drag & Drop Effects
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            handleFileUpload(file);
        } else {
            showError('Please upload a valid PDF file');
        }
    });
}

// ===== Core Conversion Logic =====
async function handleFileUpload(file) {
    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
        showError('File size exceeds 50MB limit');
        return;
    }
    
    // Show processing section
    showProcessing();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Update UI
        statusDetail.textContent = 'Uploading PDF...';
        progressFill.style.width = '20%';
        
        // Call Backend API
        const response = await fetch(`${API_BASE_URL}/api/v1/convert`, {
            method: 'POST',
            body: formData
        });
        
        // Update UI
        statusDetail.textContent = 'Processing text...';
        progressFill.style.width = '50%';
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Conversion failed');
        }
        
        const data = await response.json();
        console.log('✅ Conversion successful:', data);
        
        // Update UI
        statusDetail.textContent = 'Finalizing audio...';
        progressFill.style.width = '100%';
        
        // Small delay for smooth UX
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Show Player with REAL Audio
        showPlayer(file.name, data.audio_url);
        
    } catch (error) {
        console.error('❌ Conversion error:', error);
        showError(error.message);
    }
}

// ===== UI State Management =====
function showProcessing() {
    hideAllSections();
    statusSection.style.display = 'block';
    progressFill.style.width = '10%';
    statusText.textContent = 'Converting PDF to Audio...';
    statusDetail.textContent = 'Initializing...';
}

function showPlayer(filename, audioUrl) {
    hideAllSections();
    playerSection.style.display = 'block';
    fileName.textContent = filename;
    currentFilename = filename;
    currentAudioUrl = audioUrl;
    
    // Set Audio Source
    audioPlayer.src = currentAudioUrl;
    audioPlayer.load(); // Reload player with new source
    
    // Optional: Auto-play
    // audioPlayer.play().catch(e => console.log("Auto-play blocked by browser"));
}

function showError(message) {
    hideAllSections();
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
    // Show upload zone again in case of error
    uploadSection.style.display = 'block';
}

function hideAllSections() {
    statusSection.style.display = 'none';
    playerSection.style.display = 'none';
    errorSection.style.display = 'none';
    uploadSection.style.display = 'none';
}

function resetApp() {
    // Stop audio
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    audioPlayer.src = '';
    
    // Reset state
    fileInput.value = '';
    currentAudioUrl = '';
    currentFilename = '';
    playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
    
    // Show upload zone
    hideAllSections();
    uploadSection.style.display = 'block';
}

// ===== Audio Player Controls =====
function setupAudioPlayer() {
    playPauseBtn.addEventListener('click', togglePlayPause);
    stopBtn.addEventListener('click', stopAudio);
    speedSelect.addEventListener('change', changeSpeed);
    
    // Update icon when state changes
    audioPlayer.addEventListener('play', () => {
        playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
    });
    
    audioPlayer.addEventListener('pause', () => {
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
    });
    
    audioPlayer.addEventListener('ended', () => {
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
        audioPlayer.currentTime = 0;
    });
}

function togglePlayPause() {
    if (audioPlayer.paused) {
        audioPlayer.play();
    } else {
        audioPlayer.pause();
    }
}

function stopAudio() {
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
}

function changeSpeed() {
    const speed = parseFloat(speedSelect.value);
    audioPlayer.playbackRate = speed;
}

// ===== Button Actions =====
function setupButtons() {
    downloadBtn.addEventListener('click', downloadAudio);
    convertNewBtn.addEventListener('click', resetApp);
}

function downloadAudio() {
    if (currentAudioUrl) {
        const link = document.createElement('a');
        link.href = currentAudioUrl;
        link.download = currentFilename.replace('.pdf', '.mp3');
        link.target = '_blank'; // Open in new tab to trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        showError('No audio file available for download');
    }
}