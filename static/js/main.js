document.addEventListener("DOMContentLoaded", () => {
  // Initialize particles.js
  if (document.getElementById("particles-js")) {
    // Check if particlesJS is defined before using it
    if (typeof particlesJS !== "undefined") {
      particlesJS("particles-js", {
        particles: {
          number: {
            value: 60,
            density: {
              enable: true,
              value_area: 800,
            },
          },
          color: {
            value: "#ffffff",
          },
          shape: {
            type: "circle",
            stroke: {
              width: 0,
              color: "#000000",
            },
            polygon: {
              nb_sides: 5,
            },
          },
          opacity: {
            value: 0.2,
            random: true,
            anim: {
              enable: true,
              speed: 0.5,
              opacity_min: 0.1,
              sync: false,
            },
          },
          size: {
            value: 2,
            random: true,
            anim: {
              enable: false,
              speed: 40,
              size_min: 0.1,
              sync: false,
            },
          },
          line_linked: {
            enable: true,
            distance: 150,
            color: "#ffffff",
            opacity: 0.2,
            width: 1,
          },
          move: {
            enable: true,
            speed: 1,
            direction: "none",
            random: true,
            straight: false,
            out_mode: "out",
            bounce: false,
            attract: {
              enable: false,
              rotateX: 600,
              rotateY: 1200,
            },
          },
        },
        interactivity: {
          detect_on: "canvas",
          events: {
            onhover: {
              enable: true,
              mode: "grab",
            },
            onclick: {
              enable: true,
              mode: "push",
            },
            resize: true,
          },
          modes: {
            grab: {
              distance: 140,
              line_linked: {
                opacity: 0.5,
              },
            },
            bubble: {
              distance: 400,
              size: 40,
              duration: 2,
              opacity: 8,
              speed: 3,
            },
            repulse: {
              distance: 200,
              duration: 0.4,
            },
            push: {
              particles_nb: 4,
            },
            remove: {
              particles_nb: 2,
            },
          },
        },
        retina_detect: true,
      })
    } else {
      console.error("particlesJS is not defined. Make sure the particles.js library is included.")
    }
  }

  // Add glow effect to titles only
  const pageTitles = document.querySelectorAll(".page-title")
  pageTitles.forEach((title) => {
    title.classList.add("title-glow")
  })

  // Filter athletes by gender
  const genderFilterButtons = document.querySelectorAll(".gender-filter")
  if (genderFilterButtons) {
    genderFilterButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const gender = this.dataset.gender
        window.location.href = `?gender=${gender}`
      })
    })
  }

  // Reset filters
  const resetFilterButton = document.getElementById("reset-filter")
  if (resetFilterButton) {
    resetFilterButton.addEventListener("click", () => {
      window.location.href = window.location.pathname
    })
  }

  // Filter athletes for match creation
  const matchGenderFilter = document.getElementById("match-gender-filter")
  if (matchGenderFilter) {
    matchGenderFilter.addEventListener("change", function () {
      const gender = this.value

      fetch(`/api/athletes/filter?gender=${gender}`)
        .then((response) => response.json())
        .then((athletes) => {
          updateAthleteOptions("blue_corner_id", athletes)
          updateAthleteOptions("red_corner_id", athletes)
        })
        .catch((error) => console.error("Error fetching athletes:", error))
    })
  }

  // Function to update athlete dropdown options
  function updateAthleteOptions(selectId, athletes) {
    const select = document.getElementById(selectId)
    if (!select) return

    // Clear existing options
    select.innerHTML = '<option value="">Select Athlete</option>'

    // Add new options
    athletes.forEach((athlete) => {
      const option = document.createElement("option")
      option.value = athlete.id
      option.textContent = athlete.full_name
      select.appendChild(option)
    })
  }

  // Confirm delete
  const deleteButtons = document.querySelectorAll(".delete-confirm")
  if (deleteButtons) {
    deleteButtons.forEach((button) => {
      button.addEventListener("click", (e) => {
        if (!confirm("Are you sure you want to delete this item? This action cannot be undone.")) {
          e.preventDefault()
        }
      })
    })
  }

  // Add enhanced hover effect to cards
  const cards = document.querySelectorAll(".card, .athlete-card, .match-card, .athlete-item, .stat-card")
  cards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-5px)"
      this.style.boxShadow = "0 0 20px rgba(255, 255, 255, 0.3)"
    })

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)"
      this.style.boxShadow = "0 0 15px rgba(255, 255, 255, 0.1)"
    })
  })

  // Fix modal close button functionality
  const modalCloseButtons = document.querySelectorAll(".modal .btn-close")
  modalCloseButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const modalId = this.closest(".modal").id
      // Check if bootstrap is defined before using it
      if (typeof bootstrap !== "undefined") {
        const modalInstance = bootstrap.Modal.getInstance(document.getElementById(modalId))
        if (modalInstance) {
          modalInstance.hide()
        }
      } else {
        console.error("Bootstrap is not defined. Make sure the Bootstrap library is included.")
      }
    })
  })

  // Ensure modals are properly initialized
  const modals = document.querySelectorAll(".modal")
  modals.forEach((modal) => {
    // Check if bootstrap is defined before using it
    if (typeof bootstrap !== "undefined") {
      new bootstrap.Modal(modal)
    } else {
      console.error("Bootstrap is not defined. Make sure the Bootstrap library is included.")
    }
  })

  // Fix for athlete selection in create match modal
  const athleteDataCards = document.querySelectorAll(".athlete-data-card")
  athleteDataCards.forEach((card) => {
    card.style.cursor = "pointer"
    card.style.position = "relative"
    card.style.zIndex = "1055"
  })
})

// Add this code at the end of the DOMContentLoaded event listener

// CRITICAL MODAL FIXES
document.addEventListener("DOMContentLoaded", () => {
  // Fix modal backdrop issues
  const modalBackdrops = document.querySelectorAll(".modal-backdrop")
  modalBackdrops.forEach((backdrop) => {
    backdrop.style.zIndex = "1040"
  })

  // Fix modal interaction issues
  const modals = document.querySelectorAll(".modal")
  modals.forEach((modal) => {
    modal.style.zIndex = "1050"

    // Ensure modal content is clickable
    const modalContent = modal.querySelector(".modal-content")
    if (modalContent) {
      modalContent.style.zIndex = "1055"
      modalContent.style.position = "relative"
      modalContent.style.pointerEvents = "auto"
    }

    // Fix close button
    const closeBtn = modal.querySelector(".btn-close")
    if (closeBtn) {
      closeBtn.style.zIndex = "1060"
      closeBtn.style.position = "relative"
      closeBtn.style.pointerEvents = "auto"

      // Add explicit click handler for close button
      closeBtn.addEventListener("click", (e) => {
        e.stopPropagation()
        if (typeof bootstrap !== "undefined") {
          const modalInstance = bootstrap.Modal.getInstance(modal)
          if (modalInstance) {
            modalInstance.hide()
          } else {
            // Fallback if bootstrap instance not available
            modal.classList.remove("show")
            modal.style.display = "none"
            document.body.classList.remove("modal-open")
            const backdrops = document.querySelectorAll(".modal-backdrop")
            backdrops.forEach((backdrop) => backdrop.remove())
          }
        } else {
          console.error("Bootstrap is not defined. Make sure the Bootstrap library is included.")
        }
      })
    }

    // Make all interactive elements in modal clickable
    const interactiveElements = modal.querySelectorAll("button, a, input, select, .athlete-data-card, .corner-card")
    interactiveElements.forEach((element) => {
      element.style.position = "relative"
      element.style.zIndex = "1055"
      element.style.pointerEvents = "auto"
    })
  })

  // Fix athlete data cards click issues
  const athleteCards = document.querySelectorAll(".athlete-data-card")
  athleteCards.forEach((card) => {
    card.style.position = "relative"
    card.style.zIndex = "1055"
    card.style.pointerEvents = "auto"
    card.style.cursor = "pointer"

    // Add explicit click handler
    card.addEventListener("click", function (e) {
      e.stopPropagation()
      const athleteId = this.dataset.id
      // Find the athlete in the allAthletes array
      const athlete = window.allAthletes ? window.allAthletes.find((a) => a.id == athleteId) : null
      if (athlete && typeof selectAthlete === "function") {
        selectAthlete(athlete)
      } else {
        console.error("selectAthlete is not defined. Make sure the function is available.")
      }
    })
  })

  // Fix corner cards click issues
  const cornerCards = document.querySelectorAll(".corner-card")
  cornerCards.forEach((card) => {
    card.style.position = "relative"
    card.style.zIndex = "1055"
    card.style.pointerEvents = "auto"
    card.style.cursor = "pointer"

    // Add explicit click handler
    card.addEventListener("click", function (e) {
      e.stopPropagation()
      const cornerId = this.id
      if (cornerId.includes("blue") && typeof selectCorner === "function") {
        selectCorner("blue")
      } else if (cornerId.includes("red") && typeof selectCorner === "function") {
        selectCorner("red")
      } else {
        console.error("selectCorner is not defined. Make sure the function is available.")
      }
    })
  })
})
