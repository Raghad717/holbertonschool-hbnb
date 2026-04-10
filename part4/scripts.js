// ===== Configuration =====
const API_URL = 'http://localhost:5000/api/v1';

// ===== Cookie Helpers =====
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value, days = 7) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value}; path=/; expires=${expires.toUTCString()}`;
}

function isAuthenticated() {
    return !!getCookie('token');
}

function getToken() {
    return getCookie('token');
}

// ===== Page Navigation =====
function showPage(pageName) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) targetPage.classList.add('active');
}

// ===== LOGIN =====
function initLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await res.json();
            
            if (res.ok) {
                setCookie('token', data.access_token);
                // Update navigation
                const loginLink = document.getElementById('login-nav-link');
                if (loginLink) loginLink.style.display = 'none';
                // Show places page
                showPage('home');
                fetchPlaces();
            } else {
                const errorDiv = document.getElementById('login-error-message');
                if (errorDiv) errorDiv.textContent = data.error || 'Login failed';
                else alert('Login failed');
            }
        } catch (err) {
            alert('Network error: ' + err.message);
        }
    });
}

// ===== PLACES =====
async function fetchPlaces() {
    const container = document.getElementById('places-list');
    if (!container) return;
    
    container.innerHTML = '<p>Loading places...</p>';
    
    try {
        const res = await fetch(`${API_URL}/places`);
        const places = await res.json();
        
        if (!places || places.length === 0) {
            container.innerHTML = '<p>No places available. Create places in database.</p>';
            return;
        }
        
        container.innerHTML = '';
        places.forEach(place => {
            const card = document.createElement('div');
            card.className = 'place-card';
            card.setAttribute('data-price', place.price);
            card.innerHTML = `
                <h3>${place.title}</h3>
                <p class="price">$${place.price} / night</p>
                <button class="details-button" data-id="${place.id}">View Details</button>
            `;
            card.querySelector('.details-button').onclick = () => {
                showPlaceDetails(place.id);
            };
            container.appendChild(card);
        });
        
        // Price filter
        const filter = document.getElementById('price-filter');
        if (filter) {
            filter.onchange = () => {
                const maxPrice = filter.value;
                document.querySelectorAll('.place-card').forEach(card => {
                    const price = parseFloat(card.getAttribute('data-price'));
                    card.style.display = (maxPrice === 'all' || price <= maxPrice) ? 'block' : 'none';
                });
            };
        }
    } catch (err) {
        container.innerHTML = '<p>Error loading places. Make sure backend is running.</p>';
    }
}

// ===== PLACE DETAILS =====
async function showPlaceDetails(placeId) {
    showPage('place');
    const container = document.getElementById('place-details');
    container.innerHTML = '<p>Loading...</p>';
    
    try {
        const res = await fetch(`${API_URL}/places/${placeId}`);
        const place = await res.json();
        
        container.innerHTML = `
            <h2>${place.title}</h2>
            <p>${place.description || 'No description'}</p>
            <p class="price">$${place.price} / night</p>
            <div class="owner-info"><strong>Host:</strong> ${place.owner?.first_name || 'Unknown'}</div>
            <div class="amenities"><strong>Amenities:</strong><ul>${place.amenities?.map(a => `<li>${a.name}</li>`).join('') || '<li>None</li>'}</ul></div>
        `;
        
        // Load reviews
        const reviewsRes = await fetch(`${API_URL}/reviews/places/${placeId}/reviews`);
        const reviews = await reviewsRes.json();
        const reviewsContainer = document.getElementById('reviews-list');
        if (reviewsContainer) {
            reviewsContainer.innerHTML = reviews.map(r => `
                <div class="review-card">
                    <p>"${r.text}"</p>
                    <p>⭐ ${r.rating}/5 - ${r.user?.first_name || 'Anonymous'}</p>
                </div>
            `).join('');
        }
        
        // Show add review section if logged in
        const addSection = document.getElementById('add-review-section');
        if (addSection && isAuthenticated()) {
            addSection.style.display = 'block';
            document.getElementById('place-id').value = placeId;
        }
    } catch (err) {
        container.innerHTML = '<p>Error loading place details.</p>';
    }
}

// ===== ADD REVIEW =====
function initReviewForm() {
    const form = document.getElementById('review-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = getToken();
        if (!token) {
            alert('Please login first');
            showPage('login');
            return;
        }
        
        const placeId = document.getElementById('place-id').value;
        const text = document.getElementById('review-text').value;
        const rating = document.getElementById('rating').value;
        
        try {
            const res = await fetch(`${API_URL}/reviews/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ text, rating: parseInt(rating), place_id: placeId })
            });
            
            if (res.ok) {
                alert('Review added!');
                document.getElementById('review-text').value = '';
                showPlaceDetails(placeId);
            } else {
                const error = await res.json();
                alert(error.error || 'Failed to add review');
            }
        } catch (err) {
            alert('Network error');
        }
    });
}

// ===== ADMIN DASHBOARD =====
async function loadAdminDashboard() {
    const token = getToken();
    if (!token) {
        showPage('login');
        return;
    }
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (!payload.is_admin) {
            alert('Admin access required');
            showPage('home');
            return;
        }
    } catch(e) {
        showPage('home');
        return;
    }
    
    // Load users
    const usersRes = await fetch(`${API_URL}/users/`, { headers: { 'Authorization': `Bearer ${token}` } });
    const users = await usersRes.json();
    const usersTable = document.getElementById('users-list');
    if (usersTable) {
        usersTable.innerHTML = users.map(u => `
            <tr>
                <td>${u.email}</td>
                <td>${u.first_name} ${u.last_name}</td>
                <td>${u.is_admin ? 'Admin' : 'User'}</td>
            </tr>
        `).join('');
    }
    
    // Load places
    const placesRes = await fetch(`${API_URL}/places/`, { headers: { 'Authorization': `Bearer ${token}` } });
    const places = await placesRes.json();
    const placesTable = document.getElementById('admin-places-list');
    if (placesTable) {
        placesTable.innerHTML = places.map(p => `
            <tr>
                <td>${p.title}</td>
                <td>$${p.price}</td>
                <td>${p.owner?.first_name || 'Unknown'}</td>
                <td><button class="btn-delete" onclick="deletePlace('${p.id}')">Delete</button></td>
            </tr>
        `).join('');
    }
    
    // Load amenities
    const amenitiesRes = await fetch(`${API_URL}/amenities/`, { headers: { 'Authorization': `Bearer ${token}` } });
    const amenities = await amenitiesRes.json();
    const amenitiesTable = document.getElementById('amenities-list');
    if (amenitiesTable) {
        amenitiesTable.innerHTML = amenities.map(a => `
            <tr>
                <td>${a.name}</td>
                <td><button class="btn-delete" onclick="deleteAmenity('${a.id}')">Delete</button></td>
            </tr>
        `).join('');
    }
}

// ===== DELETE FUNCTIONS =====
async function deletePlace(placeId) {
    if (!confirm('Delete this place?')) return;
    const token = getToken();
    try {
        const res = await fetch(`${API_URL}/places/${placeId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            alert('Place deleted');
            loadAdminDashboard();
            fetchPlaces();
        } else {
            alert('Failed to delete');
        }
    } catch (err) {
        alert('Network error');
    }
}

async function deleteAmenity(amenityId) {
    if (!confirm('Delete this amenity?')) return;
    const token = getToken();
    try {
        const res = await fetch(`${API_URL}/amenities/${amenityId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            alert('Amenity deleted');
            loadAdminDashboard();
        } else {
            alert('Failed to delete');
        }
    } catch (err) {
        alert('Network error');
    }
}

// ===== CREATE AMENITY =====
function initCreateAmenityForm() {
    const form = document.getElementById('create-amenity-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = getToken();
        const name = document.getElementById('amenity-name').value;
        const description = document.getElementById('amenity-description').value;
        
        try {
            const res = await fetch(`${API_URL}/amenities/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name, description })
            });
            
            if (res.ok) {
                alert('Amenity created!');
                form.reset();
                loadAdminDashboard();
            } else {
                const error = await res.json();
                alert(error.error || 'Failed to create');
            }
        } catch (err) {
            alert('Network error');
        }
    });
}

// ===== LOGOUT =====
function logout() {
    setCookie('token', '', -1);
    window.location.reload();
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initLoginForm();
    initReviewForm();
    initCreateAmenityForm();
    
    // Show home page by default
    showPage('home');
    fetchPlaces();
    
    // Check if admin link should show
    if (isAuthenticated()) {
        try {
            const payload = JSON.parse(atob(getToken().split('.')[1]));
            if (payload.is_admin) {
                const adminLink = document.getElementById('admin-nav-link');
                if (adminLink) adminLink.style.display = 'inline-block';
            }
        } catch(e) {}
    }
});

// Make functions global for HTML onclick handlers
window.deletePlace = deletePlace;
window.deleteAmenity = deleteAmenity;
window.logout = logout;
