document.addEventListener('DOMContentLoaded', function() {
    // Initialize particles.js
    if (document.getElementById('particles-js')) {
        // Check if particlesJS is defined before using it
        if (typeof particlesJS !== 'undefined') {
            particlesJS('particles-js', {
                "particles": {
                    "number": {
                        "value": 80,
                        "density": {
                            "enable": true,
                            "value_area": 800
                        }
                    },
                    "color": {
                        "value": "#ffffff"
                    },
                    "shape": {
                        "type": "circle",
                        "stroke": {
                            "width": 0,
                            "color": "#000000"
                        },
                        "polygon": {
                            "nb_sides": 5
                        }
                    },
                    "opacity": {
                        "value": 0.3,
                        "random": true,
                        "anim": {
                            "enable": true,
                            "speed": 1,
                            "opacity_min": 0.1,
                            "sync": false
                        }
                    },
                    "size": {
                        "value": 3,
                        "random": true,
                        "anim": {
                            "enable": false,
                            "speed": 40,
                            "size_min": 0.1,
                            "sync": false
                        }
                    },
                    "line_linked": {
                        "enable": true,
                        "distance": 150,
                        "color": "#ffffff",
                        "opacity": 0.2,
                        "width": 1
                    },
                    "move": {
                        "enable": true,
                        "speed": 2,
                        "direction": "none",
                        "random": true,
                        "straight": false,
                        "out_mode": "out",
                        "bounce": false,
                        "attract": {
                            "enable": false,
                            "rotateX": 600,
                            "rotateY": 1200
                        }
                    }
                },
                "interactivity": {
                    "detect_on": "canvas",
                    "events": {
                        "onhover": {
                            "enable": true,
                            "mode": "grab"
                        },
                        "onclick": {
                            "enable": true,
                            "mode": "push"
                        },
                        "resize": true
                    },
                    "modes": {
                        "grab": {
                            "distance": 140,
                            "line_linked": {
                                "opacity": 0.5
                            }
                        },
                        "bubble": {
                            "distance": 400,
                            "size": 40,
                            "duration": 2,
                            "opacity": 8,
                            "speed": 3
                        },
                        "repulse": {
                            "distance": 200,
                            "duration": 0.4
                        },
                        "push": {
                            "particles_nb": 4
                        },
                        "remove": {
                            "particles_nb": 2
                        }
                    }
                },
                "retina_detect": true
            });
        } else {
            console.error('particlesJS is not defined. Make sure the particles.js library is included.');
        }
    }

    // Add glow effect to titles
    const titles = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    titles.forEach(title => {
        title.classList.add('glow-effect');
    });

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
    
    // Add hover effect to cards
    const cards = document.querySelectorAll('.card, .athlete-card, .match-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 0 20px rgba(255, 255, 255, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 0 15px rgba(255, 255, 255, 0.1)';
        });
    });
});