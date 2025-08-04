// DOM elements
const upload = document.getElementById('upload');
const uploadArea = document.getElementById('uploadArea');
const originalCanvas = document.getElementById('originalCanvas');
const processedCanvas = document.getElementById('processedCanvas');
const scaleSelect = document.getElementById('scale');
const interpolationSelect = document.getElementById('interpolation');
const compressSlider = document.getElementById('compress');
const qualityValue = document.getElementById('qualityValue');
const formatSelect = document.getElementById('format');
const processBtn = document.getElementById('processBtn');
const resetBtn = document.getElementById('resetBtn');
const downloadBtn = document.getElementById('downloadBtn');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const controlsSection = document.getElementById('controlsSection');
const previewSection = document.getElementById('previewSection');
const originalInfo = document.getElementById('originalInfo');
const processedInfo = document.getElementById('processedInfo');

// Global variables
let originalImg = new Image();
let currentFile = null;
let processedData = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateQualityDisplay();
});

function setupEventListeners() {
    // File upload
    upload.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('click', () => upload.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Controls
    compressSlider.addEventListener('input', updateQualityDisplay);
    processBtn.addEventListener('click', processImage);
    resetBtn.addEventListener('click', resetApp);
    downloadAllBtn.addEventListener('click', downloadAllVersions);
    
    // Image load handler
    originalImg.onload = displayOriginalImage;
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && isValidImageFile(file)) {
        loadImageFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && isValidImageFile(files[0])) {
        loadImageFile(files[0]);
    }
}

function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    return validTypes.includes(file.type);
}

function loadImageFile(file) {
    currentFile = file;
    const reader = new FileReader();
    
    reader.onload = (event) => {
        originalImg.src = event.target.result;
        controlsSection.style.display = 'block';
        previewSection.style.display = 'block';
    };
    
    reader.readAsDataURL(file);
}

function displayOriginalImage() {
    const ctx = originalCanvas.getContext('2d');
    
    // Calculate display size (max 400px width/height while maintaining aspect ratio)
    const maxDisplaySize = 400;
    let displayWidth = originalImg.width;
    let displayHeight = originalImg.height;
    
    if (displayWidth > maxDisplaySize || displayHeight > maxDisplaySize) {
        const ratio = Math.min(maxDisplaySize / displayWidth, maxDisplaySize / displayHeight);
        displayWidth *= ratio;
        displayHeight *= ratio;
    }
    
    originalCanvas.width = displayWidth;
    originalCanvas.height = displayHeight;
    
    ctx.drawImage(originalImg, 0, 0, displayWidth, displayHeight);
    
    // Update image info
    const fileSizeKB = currentFile ? (currentFile.size / 1024).toFixed(1) : 'N/A';
    originalInfo.innerHTML = `
        <strong>Dimensions:</strong> ${originalImg.width} × ${originalImg.height}px<br>
        <strong>File Size:</strong> ${fileSizeKB} KB<br>
        <strong>Type:</strong> ${currentFile ? currentFile.type : 'Unknown'}
    `;
}

function updateQualityDisplay() {
    qualityValue.textContent = compressSlider.value;
}

function processImage() {
    if (!originalImg.src) return;
    
    processBtn.classList.add('processing');
    processBtn.textContent = '⏳ Processing...';
    processBtn.disabled = true;
    
    // Use setTimeout to allow UI to update
    setTimeout(() => {
        try {
            const scale = parseInt(scaleSelect.value);
            const interpolation = interpolationSelect.value;
            const quality = parseInt(compressSlider.value) / 100;
            const format = formatSelect.value;
            
            // Calculate scaled dimensions
            const scaledWidth = originalImg.width * scale;
            const scaledHeight = originalImg.height * scale;
            
            // Calculate display dimensions
            const maxDisplaySize = 400;
            let displayWidth = scaledWidth;
            let displayHeight = scaledHeight;
            
            if (displayWidth > maxDisplaySize || displayHeight > maxDisplaySize) {
                const ratio = Math.min(maxDisplaySize / displayWidth, maxDisplaySize / displayHeight);
                displayWidth *= ratio;
                displayHeight *= ratio;
            }
            
            // Set up processed canvas
            processedCanvas.width = displayWidth;
            processedCanvas.height = displayHeight;
            
            const ctx = processedCanvas.getContext('2d');
            
            // Set interpolation method
            ctx.imageSmoothingEnabled = (interpolation === 'smooth');
            if (ctx.imageSmoothingEnabled) {
                ctx.imageSmoothingQuality = 'high';
            }
            
            // Draw scaled image
            ctx.drawImage(originalImg, 0, 0, displayWidth, displayHeight);
            
            // For download, create a full-size canvas
            const fullCanvas = document.createElement('canvas');
            fullCanvas.width = scaledWidth;
            fullCanvas.height = scaledHeight;
            const fullCtx = fullCanvas.getContext('2d');
            
            fullCtx.imageSmoothingEnabled = (interpolation === 'smooth');
            if (fullCtx.imageSmoothingEnabled) {
                fullCtx.imageSmoothingQuality = 'high';
            }
            
            fullCtx.drawImage(originalImg, 0, 0, scaledWidth, scaledHeight);
            
            // Generate download data
            processedData = fullCanvas.toDataURL(format, quality);
            
            // Update download button
            const extension = getFileExtension(format);
            const filename = `processed-image-${scale}x.${extension}`;
            downloadBtn.href = processedData;
            downloadBtn.download = filename;
            downloadBtn.style.display = 'inline-flex';
            downloadAllBtn.style.display = 'inline-flex';
            
            // Update processed image info
            const blob = dataURLtoBlob(processedData);
            const processedSizeKB = (blob.size / 1024).toFixed(1);
            const originalSizeKB = currentFile ? (currentFile.size / 1024).toFixed(1) : 'N/A';
            const compression = currentFile ? (((currentFile.size - blob.size) / currentFile.size) * 100).toFixed(1) : 'N/A';
            
            processedInfo.innerHTML = `
                <strong>Dimensions:</strong> ${scaledWidth} × ${scaledHeight}px<br>
                <strong>File Size:</strong> ${processedSizeKB} KB<br>
                <strong>Compression:</strong> ${compression}% reduction<br>
                <strong>Scale:</strong> ${scale}x ${interpolation}
            `;
            
        } catch (error) {
            console.error('Error processing image:', error);
            alert('Error processing image. Please try again.');
        } finally {
            processBtn.classList.remove('processing');
            processBtn.textContent = '🚀 Process Image';
            processBtn.disabled = false;
        }
    }, 100);
}

function resetApp() {
    // Reset form
    upload.value = '';
    scaleSelect.value = '2';
    interpolationSelect.value = 'smooth';
    compressSlider.value = '80';
    formatSelect.value = 'image/jpeg';
    updateQualityDisplay();
    
    // Clear canvases
    clearCanvas(originalCanvas);
    clearCanvas(processedCanvas);
    
    // Reset image
    originalImg.src = '';
    currentFile = null;
    processedData = null;
    
    // Hide sections
    controlsSection.style.display = 'none';
    previewSection.style.display = 'none';
    downloadBtn.style.display = 'none';
    downloadAllBtn.style.display = 'none';
    
    // Clear info
    originalInfo.innerHTML = '';
    processedInfo.innerHTML = '';
}

function clearCanvas(canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function getFileExtension(mimeType) {
    const extensions = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/webp': 'webp'
    };
    return extensions[mimeType] || 'jpg';
}

function dataURLtoBlob(dataURL) {
    const arr = dataURL.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    
    return new Blob([u8arr], { type: mime });
}

async function downloadAllVersions() {
    if (!originalImg.src) return;
    
    downloadAllBtn.textContent = '⏳ Creating ZIP...';
    downloadAllBtn.disabled = true;
    
    try {
        // Dynamically import JSZip
        const JSZip = await loadJSZip();
        const zip = new JSZip();
        
        const scales = [1, 2, 4];
        const interpolations = ['smooth', 'pixelated'];
        const formats = ['image/jpeg', 'image/png'];
        const quality = parseInt(compressSlider.value) / 100;
        
        for (const scale of scales) {
            for (const interpolation of interpolations) {
                for (const format of formats) {
                    const canvas = document.createElement('canvas');
                    canvas.width = originalImg.width * scale;
                    canvas.height = originalImg.height * scale;
                    
                    const ctx = canvas.getContext('2d');
                    ctx.imageSmoothingEnabled = (interpolation === 'smooth');
                    if (ctx.imageSmoothingEnabled) {
                        ctx.imageSmoothingQuality = 'high';
                    }
                    
                    ctx.drawImage(originalImg, 0, 0, canvas.width, canvas.height);
                    
                    const dataURL = canvas.toDataURL(format, quality);
                    const blob = dataURLtoBlob(dataURL);
                    
                    const extension = getFileExtension(format);
                    const filename = `image-${scale}x-${interpolation}.${extension}`;
                    
                    zip.file(filename, blob);
                }
            }
        }
        
        // Generate and download ZIP
        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const zipURL = URL.createObjectURL(zipBlob);
        
        const link = document.createElement('a');
        link.href = zipURL;
        link.download = 'processed-images.zip';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(zipURL);
        
    } catch (error) {
        console.error('Error creating ZIP:', error);
        alert('Error creating ZIP file. Please try downloading individual images.');
    } finally {
        downloadAllBtn.textContent = '📦 Download All Versions (ZIP)';
        downloadAllBtn.disabled = false;
    }
}

// Load JSZip library dynamically
async function loadJSZip() {
    return new Promise((resolve, reject) => {
        if (window.JSZip) {
            resolve(window.JSZip);
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
        script.onload = () => resolve(window.JSZip);
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Advanced image processing functions
function applyColorQuantization(imageData, colors = 16) {
    const data = imageData.data;
    const pixels = [];
    
    // Extract pixels
    for (let i = 0; i < data.length; i += 4) {
        pixels.push({
            r: data[i],
            g: data[i + 1],
            b: data[i + 2],
            a: data[i + 3]
        });
    }
    
    // Simple color quantization (can be improved with k-means)
    const step = 256 / Math.cbrt(colors);
    
    for (let i = 0; i < data.length; i += 4) {
        data[i] = Math.floor(data[i] / step) * step;     // R
        data[i + 1] = Math.floor(data[i + 1] / step) * step; // G
        data[i + 2] = Math.floor(data[i + 2] / step) * step; // B
    }
    
    return imageData;
}

// Error handling
window.addEventListener('error', (e) => {
    console.error('Application error:', e.error);
});

// Prevent default drag behavior on the document
document.addEventListener('dragover', (e) => e.preventDefault());
document.addEventListener('drop', (e) => e.preventDefault());
