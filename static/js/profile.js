
document.addEventListener("DOMContentLoaded", () => {

    const profileName = document.getElementById("profileName");
    const profileEmail = document.getElementById("profileEmail");
    const profileAvatar = document.getElementById("profileAvatar");

    const detailName = document.getElementById("detailName");
    const detailEmail = document.getElementById("detailEmail");
    const detailInstitution = document.getElementById("detailInstitution");

    const logoutButton = document.getElementById("profileLogoutButton");
    const profileMessage = document.getElementById("profileMessage");

    // Safely display text
    function setText(element, value, fallback = "Not provided") {
        if (element) {
            element.textContent = value || fallback;
        }
    }

    // Load researcher information
    async function loadProfile() {

        try {
            const response = await fetch("/api/me", {
                method: "GET",
                credentials: "same-origin"
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = "/login";
                    return;
                }

                throw new Error(
                    data.message || "Unable to load profile information."
                );
            }

            const user = data.user || data;

            const name = user.name || "Researcher";
            const email = user.email || "";
            const institution = user.institution || "Not provided";

            setText(profileName, name);
            setText(profileEmail, email, "Email unavailable");

            setText(detailName, name);
            setText(detailEmail, email);
            setText(detailInstitution, institution);

            if (profileAvatar) {
                profileAvatar.textContent =
                    name.trim().charAt(0).toUpperCase() || "R";
            }

            if (window.lucide) {
                lucide.createIcons();
            }

        } catch (error) {

            console.error("Profile loading error:", error);

            setText(profileName, "Unable to load profile");
            setText(profileEmail, "Please refresh the page.");
            setText(detailName, "Unavailable");
            setText(detailEmail, "Unavailable");
            setText(detailInstitution, "Unavailable");

            profileMessage.textContent = error.message;
        }
    }

    // Retrieve a fresh CSRF token
    async function getCSRFToken() {

        const response = await fetch("/api/csrf-token", {
            credentials: "same-origin"
        });

        const data = await response.json();

        if (!response.ok || !data.csrf_token) {
            throw new Error("Unable to initialize secure logout.");
        }

        return data.csrf_token;
    }

    // Secure logout
    logoutButton.addEventListener("click", async () => {

        logoutButton.disabled = true;
        logoutButton.textContent = "Logging out...";

        profileMessage.textContent = "";

        try {

            const csrfToken = await getCSRFToken();

            const response = await fetch("/api/logout", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": csrfToken
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "Logout failed. Please try again."
                );
            }

            // Clear temporary analysis from this browser tab
            sessionStorage.removeItem("freshvisionLatestAnalysis");

            window.location.href = "/login";

        } catch (error) {

            console.error("Logout error:", error);

            profileMessage.textContent = error.message;

            logoutButton.disabled = false;
            logoutButton.innerHTML =
                '<i data-lucide="log-out"></i> Logout';

            if (window.lucide) {
                lucide.createIcons();
            }
        }
    });

    // Initialize profile
    loadProfile();

});
