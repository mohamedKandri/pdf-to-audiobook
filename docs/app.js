// ===== Configuration =====
const API_BASE_URL = 'https://your-render-app.onrender.com';

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
const voiceSelect = document.getElementById('voiceSelect');
const downloadBtn = document.getElementById('downloadBtn');
const convertNewBtn = document.getElementById('convertNewBtn');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const dialogueModeToggle = document.getElementById('dialogueModeToggle');
const dialogueHint = document.getElementById('dialogueHint');

// ===== State =====
let currentAudioUrl = '';
let currentFilename = '';
let dialogueMode = false;

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    setupUploadZone();
    setupAudioPlayer();
    setupButtons();
    setupDialogueMode();
    console.log('🎧 PDF to Audiobook Frontend Ready');
    console.log('🔌 Connecting to Backend:', API_BASE_URL);
    console.log('🎭 Dialogue Mode:', dialogueMode ? 'ON' : 'OFF');
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

// ===== Dialogue Mode Setup =====
function setupDialogueMode() {
    if (dialogueModeToggle) {
        dialogueModeToggle.addEventListener('change', (e) => {
            dialogueMode = e.target.checked;
            
            // Show/hide hint
            if (dialogueHint) {
                dialogueHint.style.display = dialogueMode ? 'block' : 'none';
            }
            
            // Show/hide voice select (disabled in dialogue mode)
            if (voiceSelect) {
                voiceSelect.disabled = dialogueMode;
                voiceSelect.style.opacity = dialogueMode ? '0.5' : '1';
            }
            
            console.log('🎭 Dialogue Mode:', dialogueMode ? 'ON ✅' : 'OFF ❌');
        });
    }
}

// ===== Core Conversion Logic =====
async function handleFileUpload(file) {
    // Validate file size (10MB max for free tier)
    if (file.size > 10 * 1024 * 1024) {
        showError('File size exceeds 10MB limit (free tier)');
        return;
    }
    
    // Validate file type
    if (file.type !== 'application/pdf') {
        showError('Please upload a valid PDF file');
        return;
    }
    
    // Show processing section
    showProcessing();
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('voice', voiceSelect?.value || 'en-us-female');
    formData.append('dialogue_mode', dialogueMode ? 'true' : 'false');
    
    try {
        // Update UI
        if (dialogueMode) {
            statusDetail.textContent = '🎭 Parsing dialogue segments...';
        } else {
            statusDetail.textContent = 'Uploading PDF...';
        }
        progressFill.style.width = '20%';
        
        // Show server wake-up message
        statusDetail.textContent = '🔄 Connecting to server... (first load may take 30s)';
        
        // Call Backend API
        const response = await fetch(`${API_BASE_URL}/api/v1/convert`, {
            method: 'POST',
            body: formData
        });
        
        // Update UI
        if (dialogueMode) {
            statusDetail.textContent = '🎙️ Converting dialogue segments...';
        } else {
            statusDetail.textContent = 'Processing text...';
        }
        progressFill.style.width = '50%';
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Conversion failed');
        }
        
        const data = await response.json();
        console.log('✅ Conversion successful:', data);
        
        // Update UI
        if (dialogueMode) {
            statusDetail.textContent = `✅ Converted ${data.segments_count || 1} segments`;
        } else {
            statusDetail.textContent = 'Finalizing audio...';
        }
        progressFill.style.width = '100%';
        
        // Small delay for smooth UX
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Show Player with REAL Audio
        showPlayer(file.name, data.audio_url);
        
    } catch (error) {
        console.error('❌ Conversion error:', error);
        
        // Friendly error for Render sleep/timeout
        if (error.message.includes('waking up') || error.message.includes('timeout')) {
            showError('⏳ Server is waking up! Please try again in 30 seconds.');
        } else if (error.message.includes('pydub') || error.message.includes('ffmpeg')) {
            showError('🔧 Server configuration error. Please contact support.');
        } else {
            showError(error.message);
        }
    }
}

// ===== UI State Management =====
function showProcessing() {
    hideAllSections();
    statusSection.style.display = 'block';
    progressFill.style.width = '10%';
    statusText.textContent = dialogueMode ? '🎭 Converting Dialogue...' : '🎧 Converting PDF to Audio...';
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
    
    // Show dialogue mode indicator
    if (dialogueMode) {
        const indicator = document.createElement('div');
        indicator.className = 'dialogue-indicator';
        indicator.innerHTML = '🎭 Dialogue Mode Active';
        indicator.style.cssText = 'background: #667eea; color: white; padding: 8px 15px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 15px; display: inline-block;';
        playerCard = document.querySelector('.player-card');
        if (playerCard && !playerCard.querySelector('.dialogue-indicator')) {
            playerCard.insertBefore(indicator, playerCard.firstChild);
        }
    }
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
    
    // Remove dialogue indicator if exists
    const indicator = document.querySelector('.dialogue-indicator');
    if (indicator) {
        indicator.remove();
    }
    
    // Show upload zone
    hideAllSections();
    uploadSection.style.display = 'block';
    
    // Reset dialogue mode UI
    if (dialogueHint) {
        dialogueHint.style.display = 'none';
    }
    if (voiceSelect) {
        voiceSelect.disabled = false;
        voiceSelect.style.opacity = '1';
    }
}

// ===== Audio Player Controls =====
function setupAudioPlayer() {
    playPauseBtn.addEventListener('click', togglePlayPause);
    stopBtn.addEventListener('click', stopAudio);
    
    // Speed control
    if (speedSelect) {
        speedSelect.addEventListener('change', changeSpeed);
    }
    
    // Voice control (note: requires re-conversion)
    if (voiceSelect) {
        voiceSelect.addEventListener('change', () => {
            if (currentFilename && !dialogueMode) {
                showVoiceChangeNotice();
            }
        });
    }
    
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

function showVoiceChangeNotice() {
    // Show a temporary notice that voice change requires re-conversion
    const notice = document.createElement('div');
    notice.className = 'voice-notice';
    notice.innerHTML = '💡 Voice change requires re-conversion. Upload again to apply.';
    notice.style.cssText = 'background: #fff3cd; color: #856404; padding: 10px 15px; border-radius: 8px; font-size: 0.9rem; margin-top: 15px; border-left: 4px solid #ffc107;';
    
    const playerCard = document.querySelector('.player-card');
    if (playerCard && !playerCard.querySelector('.voice-notice')) {
        playerCard.appendChild(notice);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notice.remove();
        }, 5000);
    }
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

// ===== Utility Functions =====
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ===== Debug/Console Info =====
console.log('🎧 PDF to Audiobook Converter');
console.log('Version: 1.0.0');
console.log('Features: Voice Selection, Dialogue Mode, Speed Control');
console.log('Backend:', API_BASE_URL);
console.log('Ready to convert! 🚀');

// Add to state
let usePremiumVoices = false;

// Add toggle handler in setupDialogueMode()
const premiumToggle = document.getElementById('premiumToggle');
if (premiumToggle) {
    premiumToggle.addEventListener('change', (e) => {
        usePremiumVoices = e.target.checked;
        console.log(' Premium Voices:', usePremiumVoices ? 'ON' : 'OFF');
    });
}

// Update handleFileUpload to send premium parameter
formData.append('premium', usePremiumVoices ? 'true' : 'false');