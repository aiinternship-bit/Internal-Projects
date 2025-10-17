// Add Project Modal Handler
document.addEventListener('DOMContentLoaded', () => {
    const addProjectCard = document.getElementById('add-project-card');
    const addProjectModal = document.getElementById('add-project-modal');
    const closeAddProject = document.getElementById('close-add-project');
    const cancelAddProject = document.getElementById('cancel-add-project');
    const addProjectForm = document.getElementById('add-project-form');

    // Open modal
    addProjectCard.addEventListener('click', () => {
        addProjectModal.classList.add('active');
    });

    // Close modal
    const closeModal = () => {
        addProjectModal.classList.remove('active');
        addProjectForm.reset();
    };

    closeAddProject.addEventListener('click', closeModal);
    cancelAddProject.addEventListener('click', closeModal);

    // Close on backdrop click
    addProjectModal.addEventListener('click', (e) => {
        if (e.target === addProjectModal) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && addProjectModal.classList.contains('active')) {
            closeModal();
        }
    });

    // Handle form submission
    addProjectForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            name: document.getElementById('project-name').value,
            description: document.getElementById('project-description').value,
            icon: document.getElementById('project-icon').value,
            path: document.getElementById('project-path').value,
            color: document.getElementById('project-color').value
        };

        try {
            const response = await fetch('/api/add-project', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                // Show success message
                alert('Project added successfully!');
                // Reload the page to show the new project
                window.location.reload();
            } else {
                alert('Error: ' + (result.error || 'Failed to add project'));
            }
        } catch (error) {
            console.error('Error adding project:', error);
            alert('Error: Failed to add project. Please try again.');
        }
    });
});
