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

function deleteCookie(name) {
    document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;`;
}

// ===== 🔥 Authentication Check (NEW) =====
function checkAuthentication() {
    const token = getCookie('token');
    if (!token) {
        window.location.href = 'index.html';
    }
    return token;
}

// ===== LOGIN =====
function initLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('error-message'); // FIXED ID

        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (res.ok) {
                setCookie('token', data.access_token);
                window.location.href = 'index.html';
            } else {
                if (errorDiv) {
                    errorDiv.style.display = 'block';
                    errorDiv.textContent = data.error || 'Login failed';
                } else {
                    alert('Login failed');
                }
            }
        } catch (err) {
            alert('Network error. Make sure backend is running');
            console.error(err);
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
        if (!res.ok) throw new Error('Failed to fetch places');

        const places = await res.json();

        if (!places || places.length === 0) {
            container.innerHTML = '<p>No places available.</p>';
            return;
        }

        container.innerHTML = '';

        places.forEach(place => {
            const card = document.createElement('div');
            card.className = 'place-card';
            card.setAttribute('data-price', place.price);

            card.innerHTML = `
                <h3>${escapeHtml(place.title)}</h3>
                <p class="price">$${place.price} / night</p>
                <button class="details-button" data-id="${place.id}">View Details</button>
            `;

            card.querySelector('.details-button').onclick = () => {
                window.location.href = `place.html?id=${place.id}`;
            };

            container.appendChild(card);
        });

        // Filter
        const filter = document.getElementById('price-filter');
        if (filter) {
            filter.onchange = () => {
                const maxPrice = filter.value;
                document.querySelectorAll('.place-card').forEach(card => {
                    const price = parseFloat(card.getAttribute('data-price'));
                    card.style.display = (maxPrice === 'all' || price <= maxPrice) ? 'flex' : 'none';
                });
            };
        }

    } catch (err) {
        container.innerHTML = '<p>Error loading places.</p>';
    }
}

// ===== PLACE DETAILS =====
async function loadPlaceDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const placeId = urlParams.get('id');

    if (!placeId) return;

    try {
        const token = getCookie('token');

        const res = await fetch(`${API_URL}/places/${placeId}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (!res.ok) throw new Error('Place not found');

        const place = await res.json();

        document.getElementById('place-details').innerHTML = `
            <h2>${escapeHtml(place.title)}</h2>
            <p>${escapeHtml(place.description || 'No description')}</p>
            <p class="price"><strong>Price:</strong> $${place.price} / night</p>
            <div><strong>Host:</strong> ${escapeHtml(place.owner?.first_name || 'Unknown')}</div>
            <div>
                <strong>Amenities:</strong>
                <ul>
                    ${place.amenities?.map(a => `<li>${escapeHtml(a.name)}</li>`).join('') || '<li>None</li>'}
                </ul>
            </div>
        `;

        // ===== REVIEWS =====
        const reviewsRes = await fetch(`${API_URL}/reviews/places/${placeId}/reviews`);
        const reviews = await reviewsRes.json();

        const reviewsContainer = document.getElementById('reviews-list');
        if (reviewsContainer) {
            reviewsContainer.innerHTML = reviews.length
                ? reviews.map(r => `
                    <div class="review-card">
                        <p>"${escapeHtml(r.text)}"</p>
                        <p>⭐ ${r.rating}/5 - ${escapeHtml(r.user?.first_name || 'Anonymous')}</p>
                    </div>
                `).join('')
                : '<p>No reviews yet.</p>';
        }

    } catch (err) {
        document.getElementById('place-details').innerHTML = '<p>Error loading place.</p>';
    }
}

// ===== ADD REVIEW =====
function initReviewForm() {
    const form = document.getElementById('review-form');
    if (!form) return;

    const token = checkAuthentication();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

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
                body: JSON.stringify({
                    text,
                    rating: parseInt(rating),
                    place_id: placeId
                })
            });

            if (res.ok) {
                alert('Review added successfully!');
                form.reset();
                loadPlaceDetails();
            } else {
                const err = await res.json();
                alert(err.error || 'Failed to add review');
            }

        } catch (err) {
            alert('Network error');
        }
    });
}

// ===== AUTH UI =====
function checkAuthForIndex() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    const adminLink = document.getElementById('admin-link');

    if (token) {
        if (loginLink) loginLink.style.display = 'none';

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (payload.is_admin && adminLink) {
                adminLink.style.display = 'inline-block';
            }
        } catch(e) {}
    } else {
        if (loginLink) loginLink.style.display = 'inline-block';
        if (adminLink) adminLink.style.display = 'none';
    }
}

// ===== HELPER =====
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, m =>
        m === '&' ? '&amp;' : m === '<' ? '&lt;' : '&gt;'
    );
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {

    // LOGIN
    if (document.getElementById('login-form')) {
        initLoginForm();
    }

    // INDEX
    if (document.getElementById('places-list')) {
        checkAuthForIndex();
        fetchPlaces();
    }

    // PLACE DETAILS
    if (document.getElementById('place-details')) {
        const token = getCookie('token');

        const addSection = document.getElementById('add-review-section');
        if (addSection) {
            addSection.style.display = token ? 'block' : 'none';
        }

        loadPlaceDetails();
        initReviewForm();
    }
});
