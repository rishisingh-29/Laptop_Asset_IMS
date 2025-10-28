// main.js

document.addEventListener('DOMContentLoaded', () => {

    // ===================================================================
    // THEME TOGGLE LOGIC (DARK/LIGHT MODE)
    // ===================================================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('theme-toggle-sun');
    const moonIcon = document.getElementById('theme-toggle-moon');

    // This function applies the theme by adding/removing the 'dark' class
    // from the <html> element and showing the correct icon.
    // It follows best practices:
    // 1. Checks for a user's saved choice in localStorage.
    // 2. If no choice exists, it respects the user's Operating System preference.
    // 3. Defaults to light mode if neither is available.
    const applyTheme = () => {
        // Validation: Ensure the icon elements exist before trying to use them.
        if (!sunIcon || !moonIcon) {
            console.error("Theme toggle icons not found in the DOM.");
            return;
        }

        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            // Apply Dark Mode
            document.documentElement.classList.add('dark');
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            // Apply Light Mode
            document.documentElement.classList.remove('dark');
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    };

    // Validation: Only add the event listener if the theme toggle button exists.
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            // Toggle the 'dark' class on the root <html> element
            const isDark = document.documentElement.classList.toggle('dark');
            // Save the user's choice to localStorage to remember it for the next visit
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            // Update the icons immediately after the click
            applyTheme();
        });
    }

    // Apply the correct theme as soon as the page loads
    applyTheme();


    // ===================================================================
    // MOBILE SIDEBAR NAVIGATION LOGIC
    // ===================================================================
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const mobileOverlay = document.getElementById('mobile-overlay');

    const openSidebar = () => {
        // Validation: Ensure sidebar and overlay exist before manipulating them.
        if (sidebar && mobileOverlay) {
            sidebar.classList.remove('mobile-sidebar'); // This should be a class that translates it off-screen
            mobileOverlay.classList.remove('mobile-overlay'); // This should be a class that hides it (e.g., opacity-0, invisible)
        }
    };

    const closeSidebar = () => {
        if (sidebar && mobileOverlay) {
            sidebar.classList.add('mobile-sidebar');
            mobileOverlay.classList.add('mobile-overlay');
        }
    };
    
    // Validation: Add listeners only if the elements exist
    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openSidebar);
    if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', closeSidebar);
    if (mobileOverlay) mobileOverlay.addEventListener('click', closeSidebar);

});