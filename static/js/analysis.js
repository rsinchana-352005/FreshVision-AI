
document.addEventListener("DOMContentLoaded", () => {
    const imageInput = document.getElementById("fruitImage");
    const imagePreview = document.getElementById("imagePreview");
    const uploadTitle = document.getElementById("uploadTitle");
    const analyzeButton = document.getElementById("analyzeButton");
    const modelSelection = document.getElementById("modelSelection");
    const analysisStatus = document.getElementById("analysisStatus");
    const resultsPlaceholder = document.getElementById("resultsPlaceholder");
    const analysisResults = document.getElementById("analysisResults");
    const uploadArea = document.querySelector(".upload-area");

    let selectedFile = null;
    let previewURL = null;
    let latestResults = null;

    const MAX_FILE_SIZE = 8 * 1024 * 1024;

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    // Fetch CSRF token
    async function getCSRFToken() {
        const response = await fetch("/api/csrf-token", {
            credentials: "same-origin"
        });

        const data = await response.json();

        if (!response.ok || !data.csrf_token) {
            throw new Error("Unable to initialize secure analysis. Refresh the page.");
        }

        return data.csrf_token;
    }

    // Display status messages
    function showStatus(message, isError = false) {
        analysisStatus.textContent = message;
        analysisStatus.style.color = isError ? "#F87171" : "#94A3B8";
    }

    // Validate and preview uploaded image
    function handleFile(file) {
        if (!file) return;

        const extension = file.name.split(".").pop().toLowerCase();
        const validExtensions = ["jpg", "jpeg", "png", "webp"];

        if (!validExtensions.includes(extension) ||
            !allowedTypes.includes(file.type)) {
            showStatus("Please select a valid JPG, PNG or WEBP image.", true);
            return;
        }

        if (file.size > MAX_FILE_SIZE) {
            showStatus("Image size must not exceed 8 MB.", true);
            return;
        }

        selectedFile = file;

        if (previewURL) {
            URL.revokeObjectURL(previewURL);
        }

        previewURL = URL.createObjectURL(file);

        imagePreview.src = previewURL;
        imagePreview.style.display = "block";

        uploadTitle.textContent = file.name;
        analyzeButton.disabled = false;

        latestResults = null;
        analysisResults.hidden = true;
        analysisResults.innerHTML = "";
        resultsPlaceholder.hidden = false;

        showStatus("Image ready for analysis.");
    }

    imageInput.addEventListener("change", (event) => {
    const file = event.target.files[0];

    console.log("Selected file:", file);

    if (file) {
        handleFile(file);
    }
});

    // Drag and drop
    ["dragenter", "dragover"].forEach(eventName => {
        uploadArea.addEventListener(eventName, event => {
            event.preventDefault();
            uploadArea.style.borderColor = "#34D399";
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        uploadArea.addEventListener(eventName, event => {
            event.preventDefault();
            uploadArea.style.borderColor = "rgba(16,185,129,.4)";
        });
    });

    uploadArea.addEventListener("drop", event => {
        const file = event.dataTransfer.files[0];
        handleFile(file);
    });

    // Safely display text
    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[char]);
    }

    // Render prediction card
    function predictionCard(title, result) {
        return `
            <div style="
                padding:20px;
                background:#0B1220;
                border:1px solid rgba(148,163,184,.15);
                border-radius:13px;
                margin-bottom:15px;
            ">
                <h3 style="font-size:15px;margin:0 0 15px;">
                    ${title}
                </h3>

                <p style="color:#94A3B8;font-size:12px;margin-bottom:6px;">
                    Predicted Class
                </p>

                <h2 style="color:#34D399;font-size:21px;margin:0 0 15px;">
                    ${escapeHTML(result.predicted_class)}
                </h2>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    font-size:13px;
                    margin-bottom:8px;
                ">
                    <span style="color:#94A3B8;">Confidence</span>
                    <strong>${escapeHTML(result.confidence)}%</strong>
                </div>

                <div style="
                    height:8px;
                    background:#26364A;
                    border-radius:10px;
                    overflow:hidden;
                ">
                    <div style="
                        width:${Math.max(0, Math.min(100, Number(result.confidence) || 0))}%;
                        height:100%;
                        background:linear-gradient(90deg,#10B981,#22D3EE);
                    "></div>
                </div>
            </div>
        `;
    }

    // Render explanation images
    function explanationCard(title, explanation) {
        const imageURL = explanation.image_url;

        // Only allow this application's generated explanation URLs
        if (
            typeof imageURL !== "string" ||
            !/^\/api\/xai\/[a-f0-9]{12}_(mobilenet|efficientnet)_(gradcam|lime)\.png$/.test(imageURL)
        ) {
            return "";
        }

        return `
            <div style="
                padding:14px;
                background:#0B1220;
                border:1px solid rgba(148,163,184,.15);
                border-radius:13px;
            ">
                <h4 style="font-size:13px;margin:0 0 12px;">
                    ${title}
                </h4>

                <img
                    src="${imageURL}"
                    alt="${title} explanation"
                    loading="lazy"
                    style="
                        width:100%;
                        border-radius:9px;
                        display:block;
                        background:#17263A;
                    "
                    onerror="this.alt='Explanation image unavailable'; this.style.minHeight='100px';"
                >
            </div>
        `;
    }

    // Render all results
    function renderResults(data) {
        latestResults = data;
        try {
        sessionStorage.setItem(
            "freshvisionLatestAnalysis",
            JSON.stringify(data)
        );
    }catch (error) {
        console.error("Could not save temporary analysis:", error);
    }

        const results = data.results;
        const explanations = data.explanations;

        const selectedModel = modelSelection.value;

        let html = `
            <div style="margin-bottom:20px;">
                <h3 style="font-size:16px;margin-bottom:12px;">
                    Classification Results
                </h3>
        `;

        if (selectedModel === "both" || selectedModel === "mobilenetv2") {
            html += predictionCard(
                "MobileNetV2",
                results.mobilenet
            );
        }

        if (selectedModel === "both" || selectedModel === "efficientnetb0") {
            html += predictionCard(
                "EfficientNetB0",
                results.efficientnet
            );
        }

        html += `
            <div style="
                padding:13px;
                border-radius:10px;
                background:rgba(16,185,129,.08);
                border:1px solid rgba(16,185,129,.2);
                font-size:13px;
                color:#CBD5E1;
                margin-bottom:22px;
            ">
                <strong>Model Agreement:</strong>
                <span style="color:${results.models_agree ? "#34D399" : "#FBBF24"}">
                    ${results.models_agree ? "Both models agree" : "Models disagree"}
                </span>
            </div>

            <h3 style="font-size:16px;margin-bottom:13px;">
                Explainable AI Results
            </h3>

            <h4 style="color:#34D399;font-size:13px;margin-bottom:12px;">
                Grad-CAM Explanations
            </h4>

            <div style="
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
                gap:12px;
                margin-bottom:20px;
            ">
        `;

        if (selectedModel === "both" || selectedModel === "mobilenetv2") {
            html += explanationCard(
                "MobileNetV2 Grad-CAM",
                explanations.mobilenet_gradcam
            );
        }

        if (selectedModel === "both" || selectedModel === "efficientnetb0") {
            html += explanationCard(
                "EfficientNetB0 Grad-CAM",
                explanations.efficientnet_gradcam
            );
        }

        html += `
            </div>

            <h4 style="color:#22D3EE;font-size:13px;margin-bottom:12px;">
                LIME Explanations
            </h4>

            <div style="
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
                gap:12px;
            ">
        `;

        if (selectedModel === "both" || selectedModel === "mobilenetv2") {
            html += explanationCard(
                "MobileNetV2 LIME",
                explanations.mobilenet_lime
            );
        }

        if (selectedModel === "both" || selectedModel === "efficientnetb0") {
            html += explanationCard(
                "EfficientNetB0 LIME",
                explanations.efficientnet_lime
            );
        }

        html += `</div>`;

        html += `
    <div style="margin-top:24px;display:flex;justify-content:flex-end;">
        <button
            type="button"
            id="downloadIndividualReport"
            class="btn btn-primary"
        >
            <i data-lucide="file-down"></i>
            Download Individual PDF Report
        </button>
    </div>
`;

analysisResults.innerHTML = html;
analysisResults.hidden = false;
resultsPlaceholder.hidden = true;

const reportButton = document.getElementById(
    "downloadIndividualReport"
);

if (reportButton) {
    reportButton.addEventListener(
        "click",
        downloadIndividualReport
    );
}

        if (window.lucide) {
            lucide.createIcons();
        }
    }

async function downloadIndividualReport() {
    const button = document.getElementById(
        "downloadIndividualReport"
    );

    try {
        const savedAnalysis = sessionStorage.getItem(
            "freshvisionLatestAnalysis"
        );

        if (!savedAnalysis) {
            throw new Error("No recent analysis is available.");
        }

        const reportData = JSON.parse(savedAnalysis);
        const csrfToken = await getCSRFToken();

        button.disabled = true;
        button.textContent = "Generating PDF...";

        const response = await fetch(
            "/api/reports/individual",
            {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(reportData)
            }
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.message || "PDF generation failed."
            );
        }

        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = "FreshVision_Individual_Analysis.pdf";

        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(downloadUrl);

    } catch (error) {
        console.error("Individual report error:", error);
        alert(error.message || "Unable to download the report.");

    } finally {
        if (button) {
            button.disabled = false;
            button.innerHTML =
                '<i data-lucide="file-down"></i> Download Individual PDF Report';

            if (window.lucide) {
                lucide.createIcons();
            }
        }
    }
}

    // Run prediction
    analyzeButton.addEventListener("click", async () => {
        if (!selectedFile) {
            showStatus("Please select an image first.", true);
            return;
        }

        analyzeButton.disabled = true;
        analyzeButton.textContent = "Analyzing Image...";

        showStatus(
            "Running both AI models and generating Grad-CAM and LIME explanations. Please wait..."
        );

        try {
            const csrfToken = await getCSRFToken();

            const formData = new FormData();
            formData.append("image", selectedFile);

            const response = await fetch("/api/predict", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.message || "Image analysis failed."
                );
            }

            if (!data.results || !data.explanations) {
                throw new Error("The server returned incomplete analysis results.");
            }

            renderResults(data);

            showStatus("Analysis completed successfully!");

        } catch (error) {
            showStatus(
                error.message || "Unable to analyze this image.",
                true
            );

            console.error("FreshVision analysis error:", error);

        } finally {
            analyzeButton.disabled = !selectedFile;
            analyzeButton.innerHTML =
                '<i data-lucide="scan-search"></i> Analyze Fruit';

            if (window.lucide) {
                lucide.createIcons();
            }
        }
    });

    // Change visible model results without rerunning prediction
    modelSelection.addEventListener("change", () => {
        if (latestResults) {
            renderResults(latestResults);
        }
    });
});
