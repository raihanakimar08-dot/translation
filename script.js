// File upload and form handling
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const extractedTextSection = document.getElementById('extractedTextSection');
    const extractedText = document.getElementById('extractedText');
    const translateBtn = document.getElementById('translateBtn');
    const translationSection = document.getElementById('translationSection');
    const translatedText = document.getElementById('translatedText');
    const answerSection = document.getElementById('answerSection');
    const userAnswer = document.getElementById('userAnswer');
    const backTranslateBtn = document.getElementById('backTranslateBtn');
    const backTranslationSection = document.getElementById('backTranslationSection');
    const backTranslatedText = document.getElementById('backTranslatedText');
    const targetLanguage = document.getElementById('targetLanguage');
    
    // Image upload form elements
    const imageUploadForm = document.getElementById('imageUploadForm');
    const imageFileInput = document.getElementById('imageFileInput');
    
    // Audio upload form elements
    const audioUploadForm = document.getElementById('audioUploadForm');
    const audioFileInput = document.getElementById('audioFileInput');
    
    // Audio recording elements
    const startRecordingBtn = document.getElementById('startRecording');
    const stopRecordingBtn = document.getElementById('stopRecording');
    const playRecordingBtn = document.getElementById('playRecording');
    const recordingStatus = document.getElementById('recordingStatus');
    const audioPlayback = document.getElementById('audioPlayback');
    
    let mediaRecorder;
    let audioChunks = [];
    let recordedAudioBlob;

    // --- NEW/MODIFIED LOGIC FOR RECORDED AUDIO UPLOAD ---

    // Function to upload recorded audio
    function uploadRecordedAudio() {
        if (!recordedAudioBlob) {
            alert('No audio recorded. Please record audio first.');
            return;
        }

        const formData = new FormData();
        // Append the recorded audio blob as a file
        formData.append('file', recordedAudioBlob, 'recording.wav');

        // Target the dynamically created button for visual feedback
        const submitBtn = document.getElementById('uploadRecordedAudioBtn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing Audio...';
        submitBtn.disabled = true;

        fetch('/upload', { // Uses the same backend endpoint as other uploads
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                extractedText.value = data.text;
                extractedTextSection.style.display = 'block';
                // Also display translation steps
                translationSection.style.display = 'block';
                answerSection.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the audio.');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }

    // FIX: Function to dynamically show the Upload button after recording
    function showUploadRecordedAudioButton() {
        const recordingOptionDiv = document.querySelector('.recording-option');
        if (!recordingOptionDiv) return;

        // 1. Remove any existing button to prevent duplicates
        const existingUploadBtn = document.getElementById('uploadRecordedAudioBtn');
        if (existingUploadBtn) existingUploadBtn.remove();
        
        // 2. Create the new button
        const uploadAudioBtn = document.createElement('button');
        uploadAudioBtn.id = 'uploadRecordedAudioBtn'; 
        uploadAudioBtn.textContent = 'Upload Recorded Audio';
        
        // 3. Attach the corrected click handler
        uploadAudioBtn.addEventListener('click', uploadRecordedAudio);
        
        // 4. Insert the button into the recording option div, after the audio playback element
        const audioPlayback = document.getElementById('audioPlayback');
        recordingOptionDiv.insertBefore(uploadAudioBtn, audioPlayback.nextSibling);
    }

    // --- EXISTING LOGIC (Modified to call the new function) ---

    // Handle file input change to show selected file (Keep this for debugging)
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            console.log('File selected:', this.files[0].name);
        }
    });

    // Handle form submission (Document)
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!fileInput.files || !fileInput.files[0]) {
            alert('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Show loading state
        const submitBtn = uploadForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing...';
        submitBtn.disabled = true;

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                extractedText.value = data.text;
                extractedTextSection.style.display = 'block';
                translationSection.style.display = 'block';
                answerSection.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the file.');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });

    // Handle translation (Keep original logic)
    translateBtn.addEventListener('click', function() {
        const text = extractedText.value;
        if (!text.trim()) {
            alert('No text to translate.');
            return;
        }

        const selectedLanguage = targetLanguage.value;
        this.textContent = 'Translating...';
        this.disabled = true;

        fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: text,
                target_language: selectedLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Translation error: ' + data.error);
            } else {
                translatedText.value = data.translation;
                translationSection.style.display = 'block';
                answerSection.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during translation.');
        })
        .finally(() => {
            this.textContent = 'Translate Form';
            this.disabled = false;
        });
    });

    // Handle back translation (Keep original logic)
    backTranslateBtn.addEventListener('click', function() {
        const text = userAnswer.value;
        if (!text.trim()) {
            alert('Please enter your answer first.');
            return;
        }

        const selectedLanguage = targetLanguage.value;
        this.textContent = 'Back-translating...';
        this.disabled = true;

        fetch('/backtranslate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: text,
                source_language: selectedLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Back-translation error: ' + data.error);
            } else {
                backTranslatedText.value = data.translation;
                backTranslationSection.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during back-translation.');
        })
        .finally(() => {
            this.textContent = 'Back-Translate';
            this.disabled = false;
        });
    });

    // Handle image file upload form submission (Keep original logic)
    imageUploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!imageFileInput.files || !imageFileInput.files[0]) {
            alert('Please select an image file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', imageFileInput.files[0]);

        // Show loading state
        const submitBtn = imageUploadForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing Image...';
        submitBtn.disabled = true;

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                extractedText.value = data.text;
                extractedTextSection.style.display = 'block';
                translationSection.style.display = 'block';
                answerSection.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the image.');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });

    // Handle audio file upload form submission (Keep original logic)
    audioUploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!audioFileInput.files || !audioFileInput.files[0]) {
            alert('Please select an audio file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', audioFileInput.files[0]);

        // Show loading state
        const submitBtn = audioUploadForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing Audio...';
        submitBtn.disabled = true;

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                extractedText.value = data.text;
                extractedTextSection.style.display = 'block';
                translationSection.style.display = 'block';
                answerSection.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the audio file.');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });

    // Audio recording functionality (MODIFIED onstop)
    startRecordingBtn.addEventListener('click', async function() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = function(event) {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = function() {
                // Determine the correct blob type
                recordedAudioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(recordedAudioBlob);
                audioPlayback.src = audioUrl;
                audioPlayback.style.display = 'block';
                playRecordingBtn.style.display = 'inline-block';
                recordingStatus.textContent = 'Recording completed! (WAV format)';
                recordingStatus.style.color = 'green';
                
                // CRITICAL FIX: Show the upload button now in the correct location
                showUploadRecordedAudioButton();
            };

            mediaRecorder.start();
            startRecordingBtn.style.display = 'none';
            stopRecordingBtn.style.display = 'inline-block';
            playRecordingBtn.style.display = 'none';
            recordingStatus.textContent = 'Recording... Speak now!';
            recordingStatus.style.color = 'red';

            // Hide the upload button while recording if it exists
            const existingUploadBtn = document.getElementById('uploadRecordedAudioBtn');
            if(existingUploadBtn) existingUploadBtn.remove();

        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Error accessing microphone. Please check permissions.');
        }
    });

    stopRecordingBtn.addEventListener('click', function() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            startRecordingBtn.style.display = 'inline-block';
            stopRecordingBtn.style.display = 'none';
        }
    });

    playRecordingBtn.addEventListener('click', function() {
        if (audioPlayback.src) {
            audioPlayback.play();
        }
    });
    
    // REMOVE THE OLD APPEND BUTTON BLOCK!
    /*
    const uploadAudioBtn = document.createElement('button');
    uploadAudioBtn.textContent = 'Upload Recorded Audio';
    uploadAudioBtn.style.background = '#6f42c1';
    uploadAudioBtn.style.marginTop = '10px';
    uploadAudioBtn.addEventListener('click', uploadRecordedAudio);
    document.querySelector('.container').appendChild(uploadAudioBtn); // <-- REMOVED
    */

});

// Copy back translation to clipboard (Keep original logic)
function copyBackTranslation() {
    const backTranslatedText = document.getElementById('backTranslatedText');
    backTranslatedText.select();
    backTranslatedText.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        document.execCommand('copy');
        alert('Text copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy text. Please select and copy manually.');
    }
}