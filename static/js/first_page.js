// Keep track of selected suggestion index
let selectedSuggestionIndex = -1;

async function fetchSuggestions() {
  const query = document.getElementById("search-input").value.trim();
  const suggestionBox = document.getElementById("suggestion-box");

  // Reset selection index when fetching new suggestions
  selectedSuggestionIndex = -1;

  if (!query) {
    suggestionBox.style.display = "none";
    return;
  }

  try {
    // Build URL with proper parameter checks
    const baseUrl = `/restaurants/names?search=${encodeURIComponent(query)}`;
    const url =
      userLocation && userLocation.latitude && userLocation.longitude
        ? `${baseUrl}&latitude=${userLocation.latitude}&longitude=${userLocation.longitude}`
        : baseUrl;

    const response = await fetch(url);

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    suggestionBox.innerHTML = "";

    if (data.restaurants?.length > 0) {
      // Create a Set to ensure uniqueness (just in case)
      const uniqueSuggestions = [...new Set(data.restaurants)];

      // Add a header with count of suggestions
      if (uniqueSuggestions.length > 0) {
        const header = document.createElement("div");
        header.className = "suggestion-header";
        header.textContent = `${uniqueSuggestions.length} restaurant${
          uniqueSuggestions.length > 1 ? "s" : ""
        } found`;
        suggestionBox.appendChild(header);
      }

      uniqueSuggestions.forEach((suggestion, index) => {
        const div = document.createElement("div");
        div.className = "suggestion-item";
        div.dataset.index = index;
        div.textContent = suggestion;
        div.onclick = () => goToDetailsPage(suggestion);

        // Add mouseover event to update selection
        div.onmouseover = () => {
          clearSelectedSuggestion();
          selectedSuggestionIndex = index;
          div.classList.add("selected");
        };

        suggestionBox.appendChild(div);
      });
      suggestionBox.style.display = "block";
    } else {
      suggestionBox.style.display = "none";
    }
  } catch (error) {
    console.error("Fetch suggestions error:", error);
    suggestionBox.style.display = "none";
  }
}

// Function to clear selected suggestion
function clearSelectedSuggestion() {
  const suggestions = document.querySelectorAll(".suggestion-item");
  suggestions.forEach((item) => item.classList.remove("selected"));
}

// Add keyboard navigation for suggestions
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");

  searchInput.addEventListener("keydown", (e) => {
    const suggestionBox = document.getElementById("suggestion-box");
    const suggestions = document.querySelectorAll(".suggestion-item"); // Only select actual suggestion items, not the header

    if (suggestionBox.style.display === "none" || suggestions.length === 0) {
      return;
    }

    // Down arrow
    if (e.key === "ArrowDown") {
      e.preventDefault();
      selectedSuggestionIndex =
        (selectedSuggestionIndex + 1) % suggestions.length;
      clearSelectedSuggestion();
      suggestions[selectedSuggestionIndex].classList.add("selected");
      suggestions[selectedSuggestionIndex].scrollIntoView({ block: "nearest" });
    }

    // Up arrow
    else if (e.key === "ArrowUp") {
      e.preventDefault();
      selectedSuggestionIndex =
        selectedSuggestionIndex <= 0
          ? suggestions.length - 1
          : selectedSuggestionIndex - 1;
      clearSelectedSuggestion();
      suggestions[selectedSuggestionIndex].classList.add("selected");
      suggestions[selectedSuggestionIndex].scrollIntoView({ block: "nearest" });
    }

    // Enter key
    else if (e.key === "Enter") {
      if (selectedSuggestionIndex >= 0) {
        e.preventDefault();
        const selectedSuggestion =
          suggestions[selectedSuggestionIndex].textContent;
        goToDetailsPage(selectedSuggestion);
      } else if (searchInput.value.trim()) {
        // If no suggestion is selected but there's text in the input, perform a search
        searchRestaurants();
      }
    }

    // Escape key
    else if (e.key === "Escape") {
      suggestionBox.style.display = "none";
      selectedSuggestionIndex = -1;
    }
  });

  // Close suggestion box when clicking outside
  document.addEventListener("click", function (event) {
    const suggestionBox = document.getElementById("suggestion-box");
    const searchInput = document.getElementById("search-input");

    if (
      !searchInput.contains(event.target) &&
      !suggestionBox.contains(event.target)
    ) {
      suggestionBox.style.display = "none";
      selectedSuggestionIndex = -1;
    }
  });
});

// Close suggestion box when clicking outside
document.addEventListener("click", function (event) {
  const suggestionBox = document.getElementById("suggestion-box");
  const searchInput = document.getElementById("search-input");

  if (
    !searchInput.contains(event.target) &&
    !suggestionBox.contains(event.target)
  ) {
    suggestionBox.style.display = "none";
  }
});

// Close suggestion box when input is cleared
const searchInput = document.getElementById("search-input");
searchInput.addEventListener("input", function () {
  if (this.value.trim() === "") {
    suggestionBox.style.display = "none";
  }
});

function goToDetailsPage(restaurantName) {
  const encodedName = encodeURIComponent(restaurantName);
  window.location.href = `/restaurant?name=${encodedName}`;
}

function searchRestaurants() {
  const searchTerm = document.getElementById("search-input").value.trim();
  if (searchTerm.length > 0) {
    window.location.href = `/restaurants?search=${encodeURIComponent(
      searchTerm
    )}&latitude=${userLocation?.latitude}&longitude=${userLocation?.longitude}`;
  }
}

let locationEnabled = false;
let userLocation = null;
let nearbyRestaurantsDB = [];
let mainRestaurantsDB = [];
let isLoading = false;

// Toggle location with enhanced handling
async function toggleLocation() {
  const locationBtn = document.getElementById("location-btn");
  const locationOverlay = document.getElementById("location-search-overlay");

  try {
    if (!locationEnabled) {
      // Step 1: Show loading state
      locationBtn.disabled = true;
      locationBtn.textContent = "Detecting Location...";
      
      // Show our custom location overlay
      locationOverlay.classList.add("active");
      
      // Animate the dots
      const locationDots = document.querySelector(".location-dots");
      let dotCount = 3;
      const dotsInterval = setInterval(() => {
        dotCount = (dotCount % 6) + 1;
        locationDots.textContent = ".".repeat(dotCount);
      }, 300);
      
      // Step 2: Get location
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        });
      });
      
      // Update message
      document.querySelector(".location-message").textContent = "Finding the best restaurants near you";
      
      // Wait a moment to show the "finding restaurants" message
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Clear the dots animation
      clearInterval(dotsInterval);
      
      // Step 3: Redirect to location results page
      window.location.href = `/location?lat=${position.coords.latitude}&lon=${
        position.coords.longitude
      }&ts=${Date.now()}`;
    } else {
      // Step 4: Handle location off
      resetLocationState();
      displayRestaurants(mainRestaurantsDB, false);
    }
  } catch (error) {
    console.error("Location Error:", error);
    
    // Update the overlay message to show the error
    const locationOverlay = document.getElementById("location-search-overlay");
    if (locationOverlay.classList.contains("active")) {
      document.querySelector(".location-message").textContent = error.message.includes("denied")
        ? "Location access denied"
        : "Failed to get your location";
      document.querySelector(".location-dots").textContent = "";
      
      // Show the error message for 2 seconds before hiding the overlay
      setTimeout(() => {
        locationOverlay.classList.remove("active");
      }, 2000);
    }
    
    displayMessage(
      error.message.includes("denied")
        ? "Location access denied. Showing main list."
        : "Failed to get location. Try again."
    );
    resetLocationState();
  } finally {
    // Step 5: Reset UI states
    locationBtn.disabled = false;
    showLoading(false);
    
    // Hide the location overlay if it's still visible
    setTimeout(() => {
      const locationOverlay = document.getElementById("location-search-overlay");
      locationOverlay.classList.remove("active");
    }, 500);
    
    if (!locationEnabled) {
      locationBtn.textContent = "Location Search";
    }
  }
}

// New helper function
function resetLocationState() {
  locationEnabled = false;
  userLocation = null;
  nearbyRestaurantsDB = [];
  const locationBtn = document.getElementById("location-btn");
  locationBtn.classList.replace("btn-success", "btn-secondary");
  locationBtn.textContent = "Location Off";
}

// Enhanced fetch function
async function fetchNearbyRestaurants(lat, lon) {
  try {
    const response = await fetch(
      `/fetch_nearby_restaurants?lat=${lat}&lon=${lon}`,
      {
        headers: {
          Accept: "application/json",
        },
      }
    );

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();

    // Handle different response formats
    if (Array.isArray(data)) return data;
    if (data.restaurants) return data.restaurants;
    return [];
  } catch (error) {
    console.error("Fetch error:", error);
    displayMessage("Failed to fetch nearby restaurants");
    return [];
  }
}

// Improved display function
function displayRestaurants(restaurants, isNearby) {
  const restaurantList = document.getElementById("restaurant-list");
  restaurantList.innerHTML = "";

  if (restaurants.length === 0) {
    displayMessage(
      isNearby ? "No restaurants found nearby" : "No restaurants available"
    );
    return;
  }

  restaurants.forEach((restaurant) => {
    const div = document.createElement("div");
    div.className = "restaurant-item card mb-3";
    div.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${restaurant.Restaurant_Name}</h5>
                <p class="card-text">
                    ${restaurant.Address}<br>
                    <small class="text-muted">${restaurant.Cuisines}</small>
                </p>
                ${
                  isNearby
                    ? `
                <div class="restaurant-meta">
                    <span class="badge bg-primary">${
                      restaurant.Aggregate_rating || "N/A"
                    } ★</span>
                    ${
                      restaurant.Distance_km
                        ? `<span class="badge bg-secondary">${restaurant.Distance_km}km</span>`
                        : ""
                    }
                </div>`
                    : ""
                }
            </div>
        `;
    restaurantList.appendChild(div);
  });
}

// New helper functions
function showLoading(show) {
  const spinner = document.getElementById("loading-spinner");
  const mainContent = document.getElementById("main-container");
  if (show) {
    spinner.style.display = "block";
    mainContent.style.opacity = "0.5";
  } else {
    spinner.style.display = "none";
    mainContent.style.opacity = "1";
  }

  // Make sure the image analysis overlay is hidden when using the regular loading spinner
  if (!show) {
    showImageAnalysisOverlay(false);
  }
}

function displayMessage(message) {
  const restaurantList = document.getElementById("restaurant-list");
  restaurantList.innerHTML = `
        <div class="alert alert-info mt-3">
            ${message}
        </div>
    `;
}

function resetLocationState() {
  const locationBtn = document.getElementById("location-btn");
  locationEnabled = false;
  userLocation = null;
  nearbyRestaurantsDB = [];
  locationBtn.classList.replace("btn-success", "btn-secondary");
  locationBtn.textContent = "Location Off";
}

// Initial load with error handling
async function fetchMainRestaurants() {
  try {
    showLoading(true);
    const response = await fetch("/restaurants");
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    mainRestaurantsDB = data.restaurants || [];
    displayRestaurants(mainRestaurantsDB, false);
  } catch (error) {
    console.error("Fetch error:", error);
  } finally {
    showLoading(false);
  }
}

// Function to ensure image input event listener is attached
function setupImageInputListener() {
  const imageInput = document.getElementById("imageInput");
  if (imageInput) {
    // First remove any existing event listeners to avoid duplicates
    imageInput.removeEventListener("change", analyzeImage);
    // Then add the event listener
    imageInput.addEventListener("change", analyzeImage);
    console.log("Image input event listener added/refreshed");
  } else {
    console.error("Image input element not found!");
  }

  // Also set up the click handler for the image icon
  const imageIcon = document.querySelector("#image-icon-container span");
  if (imageIcon) {
    imageIcon.onclick = function () {
      const imageInput = document.getElementById("imageInput");
      if (imageInput) {
        imageInput.click();
      }
    };
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  fetchMainRestaurants();

  // Set up location button
  const locationBtn = document.getElementById("location-btn");
  if (locationBtn) {
    locationBtn.addEventListener("click", toggleLocation);
  }

  // Ensure image analysis is ready
  ensureImageAnalysisReady();

  // Add a global click handler for the image icon as a fallback
  document.addEventListener("click", function (event) {
    // Check if the clicked element or its parent is the image icon
    if (event.target.closest("#image-icon-container span")) {
      const imageInput = document.getElementById("imageInput");
      if (imageInput) {
        imageInput.click();
      }
    }
  });
});

// Reset image analysis when the page becomes visible again
document.addEventListener("visibilitychange", function () {
  if (document.visibilityState === "visible") {
    console.log("Page is now visible, resetting image analysis");
    ensureImageAnalysisReady();
  }
});

// Additional event listener for page load/reload
window.addEventListener("pageshow", function (event) {
  // The pageshow event is fired when the page is loaded or when navigating back to the page
  // The persisted property indicates if the page is being restored from the bfcache
  if (event.persisted) {
    console.log(
      "Page restored from back/forward cache, resetting image analysis"
    );
    ensureImageAnalysisReady();
  }
});

// Global variable to track if an analysis is in progress
let isAnalyzing = false;

async function analyzeImage() {
  console.log("analyzeImage function called");

  // Prevent multiple simultaneous analyses
  if (isAnalyzing) {
    console.log("Analysis already in progress, ignoring new request");
    return;
  }

  const fileInput = document.getElementById("imageInput");
  if (!fileInput) {
    console.error("Image input element not found!");
    return;
  }

  const file = fileInput.files[0];
  console.log("Selected file:", file ? file.name : "No file selected");

  if (!file) {
    alert("Please select an image.");
    return;
  }

  // Set analyzing flag
  isAnalyzing = true;

  // Show the image analysis overlay
  showImageAnalysisOverlay(true);

  // Reset and start the progress
  updateProgressBar(0);

  const formData = new FormData();
  formData.append("image", file);

  try {
    // Step 1: Uploading image - 20%
    updateAnalysisMessage("Analyzing your food image");
    updateAnalysisStatus("Searching restaurants...");
    updateProgressBar(20);

    // Small delay to show the initial message
    await new Promise((resolve) => setTimeout(resolve, 800));

    const response = await fetch("/analyze-image", {
      method: "POST",
      body: formData,
    });

    // Check if the response is OK
    if (!response.ok) {
      throw new Error(
        `Server returned ${response.status}: ${response.statusText}`
      );
    }

    // Step 2: Analyzing image - 50%
    updateAnalysisStatus("Analyzing the image...");
    updateProgressBar(50);

    // Small delay to show the analyzing message
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const data = await response.json();
    console.log("Image analysis response:", data);

    // Step 3: Finding restaurants - 80%
    updateAnalysisStatus("Image analyzed, almost completed...");
    updateProgressBar(80);

    // Small delay to show the finding restaurants message
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Step 4: Complete - 100%
    updateProgressBar(100);

    if (data?.cuisine) {
      const detectedCuisine = data.cuisine;

      // If it's a mock response, show a note to the user
      if (data.note) {
        console.log("Note from server:", data.note);
        updateAnalysisStatus("Using test data (API key not configured)");
      } else {
        updateAnalysisStatus("Found restaurants matching: " + detectedCuisine);
      }

      // Small delay before redirecting to show the complete message
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Log the redirect URL for debugging
      const redirectUrl = `/restaurants?search=${encodeURIComponent(
        detectedCuisine
      )}&latitude=${userLocation?.latitude || ""}&longitude=${
        userLocation?.longitude || ""
      }`;
      console.log("Redirecting to:", redirectUrl);

      // Reset the analyzing flag before redirecting
      isAnalyzing = false;

      // Reset the file input so it can be used again after returning to this page
      const fileInput = document.getElementById("imageInput");
      if (fileInput) {
        fileInput.value = "";
      }

      window.location.href = redirectUrl;
    } else {
      // Hide the overlay
      showImageAnalysisOverlay(false);
      alert(
        "Could not recognize the food in the image. Please try another image."
      );

      // Reset the analyzing flag
      isAnalyzing = false;

      // Reset the file input
      const fileInput = document.getElementById("imageInput");
      if (fileInput) {
        fileInput.value = "";
      }
    }
  } catch (error) {
    console.error("Error analyzing image:", error);

    // Update the analysis message to show the error
    updateAnalysisMessage("Analysis Failed");
    updateAnalysisStatus("Error: " + error.message);
    updateProgressBar(100); // Fill the progress bar

    // Change the progress bar color to red to indicate error
    const progressFill = document.querySelector(".progress-fill");
    if (progressFill) {
      progressFill.style.backgroundColor = "#ff0000";
    }

    // Wait 3 seconds before hiding the overlay so the user can see the error
    setTimeout(() => {
      showImageAnalysisOverlay(false);
      // Reset the progress bar color
      if (progressFill) {
        progressFill.style.backgroundColor = "#ff4500";
      }
      alert(
        "There was a problem analyzing your image. Please try again with a different image."
      );

      // Reset the analyzing flag
      isAnalyzing = false;

      // Reset the file input so the same file can be selected again
      const fileInput = document.getElementById("imageInput");
      if (fileInput) {
        fileInput.value = "";
      }
    }, 3000);
  } finally {
    // Make sure the analyzing flag is reset even if there's an unexpected error
    setTimeout(() => {
      isAnalyzing = false;
    }, 3500); // Slightly longer than the error timeout
  }
}

// Function to ensure all image analysis components are ready
function ensureImageAnalysisReady() {
  // Reset the analyzing flag
  isAnalyzing = false;

  // Reset the file input
  const fileInput = document.getElementById("imageInput");
  if (fileInput) {
    fileInput.value = "";
  }

  // Make sure the overlay is hidden
  showImageAnalysisOverlay(false);

  // Refresh the event listeners
  setupImageInputListener();

  console.log("Image analysis functionality reset and ready");
}

// Function to show/hide the image analysis overlay
function showImageAnalysisOverlay(show) {
  const overlay = document.getElementById("image-analysis-overlay");
  if (!overlay) {
    console.error("Image analysis overlay element not found!");
    return;
  }

  if (show) {
    overlay.classList.add("active");
  } else {
    overlay.classList.remove("active");
    // Reset progress bar and messages when hiding
    updateProgressBar(0);
    updateAnalysisMessage("Analyzing your food image");
    updateAnalysisStatus("Searching restaurants...");
  }
}

// Function to update the main analysis message
function updateAnalysisMessage(message) {
  const messageElement = document.getElementById("analysis-message");
  if (messageElement) {
    messageElement.textContent = message;
  }
}

// Function to update the status message
function updateAnalysisStatus(status) {
  const statusElement = document.getElementById("analysis-status");
  if (statusElement) {
    statusElement.textContent = status;
  }
}

// Function to update the progress bar
function updateProgressBar(percentage) {
  const progressFill = document.querySelector(".progress-fill");
  if (progressFill) {
    progressFill.style.width = `${percentage}%`;
  }
}
