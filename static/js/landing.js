
/* =====================================================
   FRESHVISION AI — LANDING PAGE INTERACTIONS
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    // MOBILE NAVIGATION

    const menuButton = document.getElementById("landingMenuToggle");
    const navLinks = document.querySelector(".landing-nav-links");

    menuButton?.addEventListener("click", () => {

        const isOpen = navLinks.classList.toggle("mobile-open");

        menuButton.innerHTML = isOpen
            ? '<i data-lucide="x"></i>'
            : '<i data-lucide="menu"></i>';

        menuButton.setAttribute("aria-expanded", String(isOpen));

        if (window.lucide) {
            lucide.createIcons();
        }
    });


    // CLOSE MENU AFTER NAVIGATION

    navLinks?.querySelectorAll("a").forEach(link => {

        link.addEventListener("click", () => {

            navLinks.classList.remove("mobile-open");

            menuButton.innerHTML = '<i data-lucide="menu"></i>';

            menuButton.setAttribute("aria-expanded", "false");

            if (window.lucide) {
                lucide.createIcons();
            }
        });

    });


    // SMOOTH SECTION NAVIGATION

    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.addEventListener("click", event => {

            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);

            if (target) {
                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }

        });

    });


    // SCROLL REVEAL ANIMATIONS

    const revealElements = document.querySelectorAll(
        ".about-card, .feature-card, .fruit-item, .technology-item"
    );

    revealElements.forEach(element => {
        element.style.opacity = "0";
        element.style.transform = "translateY(22px)";
        element.style.transition =
            "opacity 0.6s ease, transform 0.6s ease";
    });

    if ("IntersectionObserver" in window) {

        const observer = new IntersectionObserver(entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.style.opacity = "1";
                    entry.target.style.transform = "translateY(0)";

                    observer.unobserve(entry.target);
                }

            });

        }, {
            threshold: 0.12
        });

        revealElements.forEach(element => {
            observer.observe(element);
        });

    } else {

        revealElements.forEach(element => {
            element.style.opacity = "1";
            element.style.transform = "translateY(0)";
        });

    }

});
