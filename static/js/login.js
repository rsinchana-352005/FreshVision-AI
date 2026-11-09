
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const loginButton = document.getElementById("loginButton");
    const loginMessage = document.getElementById("loginMessage");
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("togglePassword");

    // Show or hide password
    togglePassword.addEventListener("click", () => {
        const isPassword = passwordInput.type === "password";

        passwordInput.type = isPassword ? "text" : "password";
        togglePassword.innerHTML = isPassword
            ? '<i data-lucide="eye-off"></i>'
            : '<i data-lucide="eye"></i>';

        togglePassword.setAttribute(
            "aria-label",
            isPassword ? "Hide password" : "Show password"
        );

        lucide.createIcons();
    });

    // Fetch a fresh CSRF token
    async function getCSRFToken() {
        const response = await fetch("/api/csrf-token", {
            method: "GET",
            credentials: "same-origin"
        });

        const data = await response.json();

        if (!response.ok || !data.csrf_token) {
            throw new Error("Unable to initialize secure login. Please refresh.");
        }

        return data.csrf_token;
    }

    // Handle login
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        loginMessage.textContent = "";
        loginMessage.className = "auth-message";

        const email = document.getElementById("email").value.trim();
        const password = passwordInput.value;

        loginButton.disabled = true;
        loginButton.textContent = "Signing in...";

        try {
            const csrfToken = await getCSRFToken();

            const response = await fetch("/api/login", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Login failed. Please try again.");
            }

            loginMessage.textContent = "Login successful! Redirecting...";
            loginMessage.classList.add("success");

            window.location.href = "/dashboard";

        } catch (error) {
            loginMessage.textContent = error.message || "Something went wrong.";
        } finally {
            loginButton.disabled = false;
            loginButton.innerHTML =
                'Sign In <i data-lucide="arrow-right"></i>';

            lucide.createIcons();
        }
    });
});
