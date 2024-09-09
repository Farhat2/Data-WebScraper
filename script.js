// script.js
// Add event listener to sidebar links
const sidebarLinks = document.querySelectorAll('.sidebar a');

sidebarLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
        // Remove active class from all links
        sidebarLinks.forEach((link) => {
            link.classList.remove('active');
        });
        // Add active class to clicked link
        e.target.classList.add('active');
    });
});