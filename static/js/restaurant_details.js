        const API_URL = "/restaurant";

        function getQueryParam(name) {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(name);
        }

        async function fetchRestaurantDetails() {
    let restaurantName = getQueryParam("name");
    if (!restaurantName) {
        document.getElementById("details").innerHTML = "<p>No restaurant selected.</p>";
        return;
    }

    document.getElementById("loading").style.display = "block"; // Show loading

    try {
        let url = `${API_URL}?name=${encodeURIComponent(restaurantName)}`;
        let response = await fetch(url, {
            headers: {
                'Accept': 'application/json'
            }
        });
        let restaurant = await response.json();

        if (restaurant.error) {
            document.getElementById("details").innerHTML = `<p>${restaurant.error}</p>`;
            return;
        }

        document.getElementById("restaurant-name").innerText = restaurant.Restaurant_Name;

        // Set image if available
let imageContainer = document.getElementById("image-container");
if (restaurant.featured_image) {
    imageContainer.innerHTML = `<img src="${restaurant.featured_image}" alt="Restaurant Image">`;
} else {
    imageContainer.innerHTML = `<p style="text-align:center;">No image available</p>`;
}

document.getElementById("details").innerHTML = `
    <div class="detail-item"><strong>📍 Address:</strong> ${restaurant.Address}, ${restaurant.City}</div>
    <div class="detail-item"><strong>🏘️ Locality:</strong> ${restaurant.Locality}</div>
    <div class="detail-item"><strong>🍽️ Cuisine:</strong> ${restaurant.Cuisine}</div>
    <div class="detail-item"><strong>⭐ Rating:</strong> ${restaurant.Rating} / 5</div>
    <div class="detail-item"><strong>🌎 Country:</strong> ${restaurant.Country}</div>
    <div class="detail-item"><strong>🎨 Rating Color:</strong> <span style="color:#${restaurant.Rating_Color};">${restaurant.Rating_Text}</span></div>
    <div class="detail-item"><strong>💰 Currency:</strong> ${restaurant.Currency}</div>
    <div class="detail-item"><strong>🗺️ Location:</strong> Latitude: ${restaurant.Latitude}, Longitude: ${restaurant.Longitude}</div>
    <div class="detail-item"><strong>📞 Contact:</strong> ${restaurant.Contact || 'Not available'}</div>
    <div class="detail-item"><strong>🕒 Opening Hours:</strong> ${restaurant.Opening_Hours || 'Not available'}</div>
    <div class="detail-item"><strong>💰 Average Cost for Two:</strong> ${restaurant.Avg_Cost_for_Two || 'Not available'} ${restaurant.Currency || ''}</div>
    <div class="detail-item"><strong>📅 Table Booking:</strong> ${restaurant.Has_Table_booking ? 'Yes' : 'No'}</div>
    <div class="detail-item"><strong>📦 Online Delivery:</strong> ${restaurant.Has_Online_delivery ? 'Yes' : 'No'}</div>
    <div class="detail-item"><strong>🚚 Delivering Now:</strong> ${restaurant.Is_delivering_now ? 'Yes' : 'No'}</div>
    <div class="detail-item"><strong>🔗 View Menu:</strong> <a href="${restaurant.menu_url}" target="_blank">Menu</a></div>
    <div class="detail-item"><strong>🖼️ Photos:</strong> <a href="${restaurant.photos_url}" target="_blank">View Photos</a></div>
    <div class="detail-item"><strong>🎉 Events:</strong> <a href="${restaurant.events_url}" target="_blank">View Events</a></div>
    <div class="detail-item"><strong>🔗 Restaurant Page:</strong> <a href="${restaurant.Restaurant_URL}" target="_blank">Visit Page</a></div>
    <div class="detail-item"><strong>🗺️ Map:</strong> <a href="https://www.google.com/maps/search/?api=1&query=${restaurant.Latitude},${restaurant.Longitude}" target="_blank">View on Google Maps</a></div>
`;

    } catch (error) {
        document.getElementById("details").innerHTML = "<p>Error fetching details.</p>";
    } finally {
        document.getElementById("loading").style.display = "none"; // Hide loading
    }
}

        function goBack() {
            window.history.back();
        }

        window.onload = fetchRestaurantDetails;