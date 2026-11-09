
document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("feedbackForm");
    const category = document.getElementById("feedbackCategory");
    const message = document.getElementById("feedbackMessage");
    const submitButton = document.getElementById("feedbackSubmit");
    const status = document.getElementById("feedbackStatus");
    const characterCount = document.getElementById("characterCount");

    // Character counter
    message.addEventListener("input", () => {
        characterCount.textContent =
            `${message.value.length} / 2000`;
    });

    // Get CSRF token
    async function getCSRFToken() {

        const response = await fetch("/api/csrf-token", {
            credentials: "same-origin"
        });

        const data = await response.json();

        if (!response.ok || !data.csrf_token) {
            throw new Error("Unable to initialize secure feedback submission.");
        }

        return data.csrf_token;
    }

    // Submit feedback
    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        if (!form.reportValidity()) {
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";
        status.textContent = "";

        try {

            const csrfToken = await getCSRFToken();

            const response = await fetch("/api/feedback", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    category: category.value,
                    message: message.value.trim()
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.message || "Unable to submit feedback."
                );
            }

            status.style.color = "#34D399";
            status.textContent =
                "Your feedback has been submitted successfully. Thank you!";

            form.reset();
            characterCount.textContent = "0 / 2000";

        } catch (error) {

            console.error("Feedback submission error:", error);

            status.style.color = "#F87171";
            status.textContent = error.message;

        } finally {

            submitButton.disabled = false;
            submitButton.innerHTML =
                '<i data-lucide="send"></i> Submit Feedback';

            if (window.lucide) {
                lucide.createIcons();
            }
        }

    });

});
