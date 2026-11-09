
document.addEventListener("DOMContentLoaded", () => {

    const emptyState = document.getElementById("explainabilityEmpty");
    const resultsSection = document.getElementById("explainabilityResults");
    const summary = document.getElementById("explanationSummary");

    const imageElements = {
        mobileGradcam: document.getElementById("mobileGradcam"),
        efficientGradcam: document.getElementById("efficientGradcam"),
        mobileLime: document.getElementById("mobileLime"),
        efficientLime: document.getElementById("efficientLime")
    };

    // Load the latest temporary analysis
    const savedData = sessionStorage.getItem(
        "freshvisionLatestAnalysis"
    );

    if (!savedData) {
        emptyState.style.display = "block";
        resultsSection.style.display = "none";
        return;
    }

    let data;

    try {
        data = JSON.parse(savedData);
    } catch (error) {
        console.error("Invalid saved analysis:", error);
        emptyState.style.display = "block";
        resultsSection.style.display = "none";
        return;
    }

    if (!data.success || !data.results || !data.explanations) {
        emptyState.style.display = "block";
        resultsSection.style.display = "none";
        return;
    }

    const results = data.results;
    const explanations = data.explanations;

    // Display prediction summary
    summary.innerHTML = `
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;">

            <div>
                <p style="color:#94A3B8;">MobileNetV2 Prediction</p>
                <h3 style="color:#34D399;">
                    ${escapeHTML(results.mobilenet?.predicted_class)}
                </h3>
                <p>Confidence: ${escapeHTML(results.mobilenet?.confidence)}%</p>
            </div>

            <div>
                <p style="color:#94A3B8;">EfficientNetB0 Prediction</p>
                <h3 style="color:#22D3EE;">
                    ${escapeHTML(results.efficientnet?.predicted_class)}
                </h3>
                <p>Confidence: ${escapeHTML(results.efficientnet?.confidence)}%</p>
            </div>

        </div>
    `;

    // Validate application-generated explanation URLs
    function setExplanationImage(element, explanation, expectedModel, expectedType) {

        const imageURL = explanation?.image_url;

        const pattern = new RegExp(
            `^/api/xai/[a-f0-9]{12}_${expectedModel}_${expectedType}\\.png$`
        );

        if (
            typeof imageURL === "string" &&
            pattern.test(imageURL)
        ) {
            element.src = imageURL;
        } else {
            element.alt = "Explanation image unavailable";
            element.style.display = "none";
        }
    }

    // Grad-CAM images
    setExplanationImage(
        imageElements.mobileGradcam,
        explanations.mobilenet_gradcam,
        "mobilenet",
        "gradcam"
    );

    setExplanationImage(
        imageElements.efficientGradcam,
        explanations.efficientnet_gradcam,
        "efficientnet",
        "gradcam"
    );

    // LIME images
    setExplanationImage(
        imageElements.mobileLime,
        explanations.mobilenet_lime,
        "mobilenet",
        "lime"
    );

    setExplanationImage(
        imageElements.efficientLime,
        explanations.efficientnet_lime,
        "efficientnet",
        "lime"
    );

    emptyState.style.display = "none";
    resultsSection.style.display = "block";

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[char]);
    }

    if (window.lucide) {
        lucide.createIcons();
    }

});
