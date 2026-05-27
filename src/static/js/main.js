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
});
