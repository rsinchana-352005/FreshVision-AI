
/* =====================================================
   FRESHVISION AI — SHARED FRONTEND JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    // DOM ELEMENTS
    const sidebar = document.getElementById("sidebar");
    const menuToggle = document.getElementById("menuToggle");
    const sidebarClose = document.getElementById("sidebarClose");
    const sidebarOverlay = document.getElementById("sidebarOverlay");

    const logoutButton = document.getElementById("logoutButton");

    const userNameElement = document.getElementById("userName");
    const userAvatarElement = document.getElementById("userAvatar");

    let csrfToken = null;


    // MOBILE SIDEBAR

    function openSidebar() {
        sidebar?.classList.add("open");
        sidebarOverlay?.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        sidebar?.classList.remove("open");
        sidebarOverlay?.classList.remove("active");
        document.body.style.overflow = "";
    }

    menuToggle?.addEventListener("click", openSidebar);

    sidebarClose?.addEventListener("click", closeSidebar);

    sidebarOverlay?.addEventListener("click", closeSidebar);


    // FETCH CSRF TOKEN

    async function getCSRFToken() {

        try {

            const response = await fetch("/api/csrf-token", {
                method: "GET",
                credentials: "same-origin"
            });

            const data = await response.json();

            if (!response.ok || !data.success || !data.csrf_token) {
                throw new Error("Unable to obtain CSRF token.");
            }

            csrfToken = data.csrf_token;

            return csrfToken;

        } catch (error) {

            console.error("CSRF error:", error);
            throw error;

        }
    }


    // LOAD LOGGED-IN USER

    async function loadCurrentUser() {

        try {

            const response = await fetch("/api/me", {
                method: "GET",
                credentials: "same-origin"
            });

            const data = await response.json();

            if (response.status === 401) {

                window.location.replace("/login");
                return;

            }

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Unable to load user.");
            }

            const user = data.user;

            if (userNameElement) {
                userNameElement.textContent = user.name;
            }

            if (userAvatarElement) {
                userAvatarElement.textContent =
                    user.name.trim().charAt(0).toUpperCase() || "U";
            }

        } catch (error) {

            console.error("User loading error:", error);

        }
    }


    // SECURE LOGOUT

    async function logoutUser() {

        if (!logoutButton) return;

        logoutButton.disabled = true;

        const originalContent = logoutButton.innerHTML;

        logoutButton.innerHTML = "Logging out...";

        try {

            const token = await getCSRFToken();

            const response = await fetch("/api/logout", {

                method: "POST",

                credentials: "same-origin",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": token
                },

                body: JSON.stringify({})

            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Logout failed.");
            }

            window.location.replace("/login");

        } catch (error) {

            console.error("Logout error:", error);

            alert("Unable to log out. Please try again.");

            logoutButton.disabled = false;
            logoutButton.innerHTML = originalContent;

        }
    }


    // LOGOUT BUTTON EVENT

    logoutButton?.addEventListener("click", logoutUser);


    // INITIALIZE AUTHENTICATED WORKSPACE

    if (document.querySelector(".app-layout")) {
        loadCurrentUser();
    }

});
