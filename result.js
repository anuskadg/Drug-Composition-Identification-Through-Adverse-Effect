// REPLACE your result.js with this version
console.log("JavaScript file is loading!");

function toggleDropdown(element) {
    console.log("toggleDropdown called with:", element);
    
    const content = element.querySelector('.medicine-content');
    const isActive = element.classList.contains('active');
    
    // FIRST: Close all other dropdowns
    const allDropdowns = document.querySelectorAll('.medicine-dropdown');
    allDropdowns.forEach(function(dropdown) {
        if (dropdown !== element && dropdown.classList.contains('active')) {
            const otherContent = dropdown.querySelector('.medicine-content');
            otherContent.style.maxHeight = '0px';
            dropdown.classList.remove('active');
            console.log("Closed other dropdown");
        }
    });
    
    // THEN: Toggle the clicked dropdown
    if (isActive) {
        // Closing the clicked dropdown
        content.style.maxHeight = '0px';
        element.classList.remove('active');
        console.log("Closed clicked dropdown");
    } else {
        // Opening the clicked dropdown
        content.style.maxHeight = 'none'; // Temporarily remove limit
        const height = content.scrollHeight; // Get actual height
        content.style.maxHeight = '0px'; // Reset to 0
        
        // Force reflow then animate to actual height
        content.offsetHeight; // Force reflow
        content.style.maxHeight = height + 'px';
        element.classList.add('active');
        console.log("Opened clicked dropdown, height:", height);
        
        // Optional: Scroll into view if needed
        setTimeout(() => {
            const rect = element.getBoundingClientRect();
            const isPartiallyHidden = rect.bottom > window.innerHeight;
            
            if (isPartiallyHidden) {
                element.scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                    inline: 'nearest'
                });
            }
        }, 200);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM is ready!");
    
    const dropdowns = document.querySelectorAll('.medicine-dropdown');
    console.log("Found", dropdowns.length, "dropdowns");
    
    // Add click event listeners to headers only
    dropdowns.forEach(function(dropdown, index) {
        const header = dropdown.querySelector('.medicine-header');
        if (header) {
            header.addEventListener('click', function(event) {
                event.stopPropagation();
                toggleDropdown(dropdown);
            });
        }
        
        // Prevent clicks on content from closing the dropdown
        const content = dropdown.querySelector('.medicine-content');
        if (content) {
            content.addEventListener('click', function(event) {
                event.stopPropagation();
            });
        }
    });
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.medicine-dropdown')) {
            dropdowns.forEach(function(dropdown) {
                if (dropdown.classList.contains('active')) {
                    const content = dropdown.querySelector('.medicine-content');
                    content.style.maxHeight = '0px';
                    dropdown.classList.remove('active');
                }
            });
        }
    });
});

// Utility function to close all dropdowns
function closeAllDropdowns() {
    const dropdowns = document.querySelectorAll('.medicine-dropdown.active');
    dropdowns.forEach(function(dropdown) {
        const content = dropdown.querySelector('.medicine-content');
        content.style.maxHeight = '0px';
        dropdown.classList.remove('active');
    });
}