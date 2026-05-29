document.addEventListener("DOMContentLoaded", () => {
    const fetchBtn = document.getElementById("fetch-btn");
    const consoleBox = document.getElementById("console-box");
    const jsonOutput = document.getElementById("json-output");
    const responseTime = document.getElementById("response-time");

    if (fetchBtn) {
        fetchBtn.addEventListener("click", async () => {
            const startTime = performance.now();
            fetchBtn.disabled = true;
            fetchBtn.innerText = "Querying API...";

            try {
                const response = await fetch("/api/health");
                const data = await response.json();
                const endTime = performance.now();
                const duration = (endTime - startTime).toFixed(1);

                // Show console
                consoleBox.classList.add("visible");
                
                // Set text
                jsonOutput.textContent = JSON.stringify(data, null, 2);
                responseTime.textContent = `Response time: ${duration}ms`;
            } catch (error) {
                consoleBox.classList.add("visible");
                jsonOutput.textContent = `Error fetching API: ${error.message}`;
                responseTime.textContent = "";
            } finally {
                fetchBtn.disabled = false;
                fetchBtn.innerText = "Test Health Check API";
            }
        });
    }

    // Feature 1: Image loading logic
    const picFetchBtn = document.getElementById("pic-fetch-btn");
    const picNameInput = document.getElementById("pic-name-input");
    const imagePreview = document.getElementById("image-preview");
    const picPlaceholder = document.getElementById("pic-placeholder");

    if (picFetchBtn) {
        picFetchBtn.addEventListener("click", () => {
            const picName = picNameInput.value.trim();
            if (!picName) {
                picPlaceholder.textContent = "Please enter a valid picture name.";
                picPlaceholder.style.display = "block";
                imagePreview.style.display = "none";
                return;
            }

            picPlaceholder.textContent = "Loading image...";
            picPlaceholder.style.display = "block";
            imagePreview.style.display = "none";

            // Load via feature1 route
            imagePreview.src = `/feature1/${encodeURIComponent(picName)}`;
            
            imagePreview.onload = () => {
                picPlaceholder.style.display = "none";
                imagePreview.style.display = "block";
            };

            imagePreview.onerror = () => {
                picPlaceholder.textContent = `Error loading image "${picName}". (File not found or access denied)`;
                picPlaceholder.style.display = "block";
                imagePreview.style.display = "none";
            };
        });
    }

    // Feature 2: Text file reading logic
    const txtFetchBtn = document.getElementById("txt-fetch-btn");
    const txtNameInput = document.getElementById("txt-name-input");
    const textPreviewOutput = document.getElementById("text-preview-output");

    if (txtFetchBtn) {
        txtFetchBtn.addEventListener("click", async () => {
            const fileName = txtNameInput.value.trim();
            if (!fileName) {
                textPreviewOutput.textContent = "Please enter a valid file name.";
                return;
            }

            textPreviewOutput.textContent = "Loading file content...";
            txtFetchBtn.disabled = true;

            try {
                const response = await fetch(`/feature2/${encodeURIComponent(fileName)}`);
                if (response.ok) {
                    const text = await response.text();
                    textPreviewOutput.textContent = text;
                } else {
                    const text = await response.text();
                    // Extract error description if available
                    textPreviewOutput.textContent = `Error ${response.status}: ${response.statusText}\n${text}`;
                }
            } catch (error) {
                textPreviewOutput.textContent = `Network Error: ${error.message}`;
            } finally {
                txtFetchBtn.disabled = false;
            }
        });
    }
    // Feature 3: S3 Upload
    const uploadZone = document.getElementById('upload-zone');
    const s3FileInput = document.getElementById('s3-file-input');
    const s3UploadBtn = document.getElementById('s3-upload-btn');
    const uploadStatus = document.getElementById('upload-status');
    const uploadResultBox = document.getElementById('upload-result-box');
    const uploadDownloadLink = document.getElementById('upload-download-link');
    const uploadSelectedFile = document.getElementById('upload-selected-file');

    if (uploadZone && s3FileInput) {
        // Click zone to open file picker
        uploadZone.addEventListener('click', () => s3FileInput.click());

        // Drag-and-drop events
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                s3FileInput.files = e.dataTransfer.files;
                uploadSelectedFile.textContent = e.dataTransfer.files[0].name;
            }
        });

        // Show selected file name
        s3FileInput.addEventListener('change', () => {
            if (s3FileInput.files.length > 0) {
                uploadSelectedFile.textContent = s3FileInput.files[0].name;
            }
        });
    }

    if (s3UploadBtn) {
        s3UploadBtn.addEventListener('click', async () => {
            const file = s3FileInput && s3FileInput.files[0];
            if (!file) {
                uploadStatus.textContent = '⚠️ Please select a file first.';
                return;
            }

            // Reset UI
            uploadResultBox.style.display = 'none';
            uploadStatus.innerHTML = '<span class="spinner"></span> Uploading to S3...';
            s3UploadBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('file', file);
                const resp = await fetch('/upload', {
                    method: 'POST',
                    body: formData,
                });
                const data = await resp.json();

                if (resp.ok && data.download_url) {
                    uploadStatus.textContent = '';
                    uploadDownloadLink.href = data.download_url;
                    uploadDownloadLink.textContent = `Download ${file.name}`;
                    uploadResultBox.style.display = 'flex';
                } else {
                    uploadStatus.textContent = `❌ Error: ${data.error || 'Unknown error'}`;
                }
            } catch (err) {
                uploadStatus.textContent = `❌ Network error: ${err.message}`;
            } finally {
                s3UploadBtn.disabled = false;
            }
        });
    }

    // Feature 4: CPU Load Generator Logic
    const cpuPercentageInput = document.getElementById("cpu-percentage-input");
    const cpuStartBtn = document.getElementById("cpu-start-btn");
    const cpuStopBtn = document.getElementById("cpu-stop-btn");
    const cpuStatusText = document.getElementById("cpu-status-text");
    const cpuCoresText = document.getElementById("cpu-cores-text");
    const cpuProgressBar = document.getElementById("cpu-progress-bar");
    const cpuProgressValue = document.getElementById("cpu-progress-value");
    const cpuDetailsRow = document.getElementById("cpu-details-row");
    const cpuProcessesText = document.getElementById("cpu-processes-text");
    const cpuTargetText = document.getElementById("cpu-target-text");

    let statusIntervalId = null;

    async function updateCPUStatus() {
        try {
            const resp = await fetch("/api/cpu/status");
            if (!resp.ok) return;
            const data = await resp.json();

            // Update CPU cores
            if (cpuCoresText) {
                cpuCoresText.textContent = `Cores: ${data.num_cores}`;
            }

            // Update real-time system CPU usage progress bar
            if (cpuProgressBar && cpuProgressValue) {
                const cpuVal = Math.round(data.system_cpu);
                cpuProgressBar.style.width = `${cpuVal}%`;
                cpuProgressValue.textContent = `${cpuVal}% System CPU`;

                // If load is high (> 70%), make it red/orange
                if (cpuVal > 70) {
                    cpuProgressBar.classList.add("high-load");
                } else {
                    cpuProgressBar.classList.remove("high-load");
                }
            }

            // Update active state and buttons
            if (data.running) {
                if (cpuStatusText) {
                    cpuStatusText.textContent = `Running (+${data.target_percentage}%)`;
                    cpuStatusText.className = "text-running";
                }
                if (cpuStartBtn) cpuStartBtn.style.display = "none";
                if (cpuStopBtn) cpuStopBtn.style.display = "inline-flex";
                if (cpuDetailsRow) cpuDetailsRow.style.display = "flex";
                if (cpuProcessesText) cpuProcessesText.textContent = `Processes: ${data.process_count}`;
                if (cpuTargetText) cpuTargetText.textContent = `Target: +${data.target_percentage}%`;
            } else {
                if (cpuStatusText) {
                    cpuStatusText.textContent = "Idle";
                    cpuStatusText.className = "text-idle";
                }
                if (cpuStartBtn) cpuStartBtn.style.display = "inline-flex";
                if (cpuStopBtn) cpuStopBtn.style.display = "none";
                if (cpuDetailsRow) cpuDetailsRow.style.display = "none";
            }
        } catch (err) {
            console.error("Error polling CPU status:", err);
        }
    }

    if (cpuStartBtn) {
        cpuStartBtn.addEventListener("click", async () => {
            const percentage = parseInt(cpuPercentageInput.value.trim(), 10);
            if (isNaN(percentage) || percentage < 1 || percentage > 100) {
                alert("⚠️ Please enter a valid percentage between 1 and 100.");
                return;
            }

            cpuStartBtn.disabled = true;
            cpuStartBtn.textContent = "Starting...";

            try {
                const resp = await fetch("/api/cpu/start", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ percentage: percentage })
                });

                const data = await resp.json();
                if (resp.ok) {
                    await updateCPUStatus();
                } else {
                    alert(`❌ Error starting CPU load: ${data.error || 'Unknown error'}`);
                }
            } catch (err) {
                alert(`❌ Network error: ${err.message}`);
            } finally {
                cpuStartBtn.disabled = false;
                cpuStartBtn.textContent = "Start CPU Load";
            }
        });
    }

    if (cpuStopBtn) {
        cpuStopBtn.addEventListener("click", async () => {
            cpuStopBtn.disabled = true;
            cpuStopBtn.textContent = "Stopping...";

            try {
                const resp = await fetch("/api/cpu/stop", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });

                const data = await resp.json();
                if (resp.ok) {
                    await updateCPUStatus();
                } else {
                    alert(`❌ Error stopping CPU load: ${data.error || 'Unknown error'}`);
                }
            } catch (err) {
                alert(`❌ Network error: ${err.message}`);
            } finally {
                cpuStopBtn.disabled = false;
                cpuStopBtn.textContent = "Stop CPU Load";
            }
        });
    }

    // Start polling CPU status
    updateCPUStatus();
    statusIntervalId = setInterval(updateCPUStatus, 1500);
});
