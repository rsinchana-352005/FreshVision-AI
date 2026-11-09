
document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    const registerButton = document.getElementById("registerButton");
    const registerMessage = document.getElementById("registerMessage");

    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");

    // Fetch a fresh CSRF token
    async function getCSRFToken() {
        const response = await fetch("/api/csrf-token", {
            method: "GET",
            credentials: "same-origin"
        });

        const data = await response.json();

        if (!response.ok || !data.csrf_token) {
            throw new Error("Unable to initialize secure registration. Please refresh.");
        }

        return data.csrf_token;
    }

    // Handle registration
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        registerMessage.textContent = "";
        registerMessage.className = "auth-message";

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const institution = document.getElementById("institution").value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // Validate password confirmation
        if (password !== confirmPassword) {
            registerMessage.textContent = "Passwords do not match.";
            return;
        }

        if (password.length < 8) {
            registerMessage.textContent = "Password must contain at least 8 characters.";
            return;
        }

        registerButton.disabled = true;
        registerButton.textContent = "Creating account...";

        try {
            const csrfToken = await getCSRFToken();

            const response = await fetch("/api/register", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    institution: institution,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Registration failed. Please try again.");
            }

            registerMessage.textContent =
                "Account created successfully! Redirecting to login...";
            registerMessage.classList.add("success");

            registerForm.reset();

            setTimeout(() => {
                window.location.href = "/login";
            }, 1500);

        } catch (error) {
            registerMessage.textContent =
                error.message || "Something went wrong. Please try again.";
        } finally {
            registerButton.disabled = false;
            registerButton.innerHTML =
                'Create Account <i data-lucide="arrow-right"></i>';

            lucide.createIcons();
        }
    });
});
