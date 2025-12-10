// Main JavaScript for AI-Interns dashboard
(function() {
    'use strict';

    // Initialize on DOM ready
    function init() {
        console.log('AI-Interns dashboard loaded');

        // Add any dashboard-specific functionality here
        // For now, this file ensures no 404 errors in the console
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
