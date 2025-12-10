// Add project functionality for AI-Interns dashboard
(function() {
    'use strict';

    // Get DOM elements
    const addProjectBtn = document.getElementById('add-project-btn');
    const addProjectModal = document.getElementById('add-project-modal');
    const cancelAddProject = document.getElementById('cancel-add-project');
    const addProjectForm = document.getElementById('add-project-form');

    // Initialize
    function init() {
        if (!addProjectBtn || !addProjectModal) {
            return; // Elements not found on this page
        }

        // Open modal
        addProjectBtn.addEventListener('click', function() {
            addProjectModal.classList.add('active');
        });

        // Close modal
        cancelAddProject.addEventListener('click', function() {
            addProjectModal.classList.remove('active');
            addProjectForm.reset();
        });

        // Close modal on backdrop click
        addProjectModal.addEventListener('click', function(e) {
            if (e.target === addProjectModal) {
                addProjectModal.classList.remove('active');
                addProjectForm.reset();
            }
        });

        // Handle form submission
        addProjectForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = {
                name: document.getElementById('project-name').value,
                description: document.getElementById('project-description').value,
                icon: document.getElementById('project-icon').value,
                path: document.getElementById('project-path').value,
                color: document.getElementById('project-color').value
            };

            // Send to backend
            fetch('/api/add-project', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload page to show new project
                    window.location.reload();
                } else {
                    alert('Error adding project: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding project. Please try again.');
            });
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
