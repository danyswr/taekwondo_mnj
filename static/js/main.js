document.addEventListener('DOMContentLoaded', function() {
    // Filter athletes by gender
    const genderFilterButtons = document.querySelectorAll('.gender-filter');
    if (genderFilterButtons) {
        genderFilterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const gender = this.dataset.gender;
                window.location.href = `?gender=${gender}`;
            });
        });
    }

    // Reset filters
    const resetFilterButton = document.getElementById('reset-filter');
    if (resetFilterButton) {
        resetFilterButton.addEventListener('click', function() {
            window.location.href = window.location.pathname;
        });
    }

    // Filter athletes for match creation
    const matchGenderFilter = document.getElementById('match-gender-filter');
    if (matchGenderFilter) {
        matchGenderFilter.addEventListener('change', function() {
            const gender = this.value;
            
            fetch(`/api/athletes/filter?gender=${gender}`)
                .then(response => response.json())
                .then(athletes => {
                    updateAthleteOptions('blue_corner_id', athletes);
                    updateAthleteOptions('red_corner_id', athletes);
                })
                .catch(error => console.error('Error fetching athletes:', error));
        });
    }

    // Function to update athlete dropdown options
    function updateAthleteOptions(selectId, athletes) {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        // Clear existing options
        select.innerHTML = '<option value="">Select Athlete</option>';
        
        // Add new options
        athletes.forEach(athlete => {
            const option = document.createElement('option');
            option.value = athlete.id;
            option.textContent = athlete.full_name;
            select.appendChild(option);
        });
    }

    // Confirm delete
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    if (deleteButtons) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
    }
});