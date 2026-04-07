# HBnB – Part 4: Simple Web Client

## Overview

This project represents the **frontend (client-side)** of the HBnB application. It is built using **HTML5, CSS3, and JavaScript (ES6)** and connects to a previously developed backend API.

The goal is to provide a dynamic, user-friendly interface that allows users to:

* Authenticate (login)
* View places
* View place details
* Add reviews
* (Optional) Admin management

---

## Features

### 1. Authentication

* Users can log in using email and password.
* JWT token is stored in browser cookies.
* Token is used for authenticated API requests.

### 2. Places Listing

* Fetches all places from the API.
* Displays them as cards.
* Supports client-side filtering by price.

### 3. Place Details

* Displays full details of a selected place.
* Shows amenities, owner info, and reviews.
* Allows adding reviews if authenticated.

### 4. Add Review

* Authenticated users can submit reviews.
* Includes rating and text.
* Redirects unauthenticated users.

### 5. Admin Panel (Optional)

* Admin-only access.
* Manage users, places, and amenities.

---

## Technologies Used

* HTML5 (Semantic structure)
* CSS3 (Responsive design)
* JavaScript ES6
* Fetch API (AJAX requests)
* JWT Authentication (Cookies)

---

## Project Structure

```
part4/
│
├── index.html           # Main page (places list)
├── login.html           # Login page
├── place.html           # Place details page
├── add_review.html      # Add review page
├── admin.html           # Admin dashboard
│
├── css/
│   └── styles.css       # Styling
│
├── js/
│   ├── scripts.js       # Main frontend logic
│   ├── admin.js         # Admin dashboard logic
│   └── config.js        # API configuration
│
├── images/
│   └── logo.png
│
└── README.md
```

---

## Setup Instructions

### 1. Clone Repository

```
git clone https://github.com/<your-username>/holbertonschool-hbnb.git
cd part4
```

### 2. Start Backend Server

Make sure your Flask API is running:

```
http://localhost:5000
```

### 3. Open Frontend

Open any HTML file in browser:

```
index.html
```

---

## API Configuration

In `scripts.js`:

```js
const API_URL = 'http://localhost:5000/api/v1';
```

Make sure this matches your backend URL.

---

## Authentication Flow

1. User submits login form.
2. Frontend sends POST request:

```
POST /auth/login
```

3. Backend returns JWT token.
4. Token is stored in cookies:

```js
document.cookie = "token=...";
```

5. Token is included in future requests:

```js
Authorization: Bearer <token>
```

---

## Pages Description

### Login Page (login.html)

* Form with email & password
* Sends login request
* Stores token
* Redirects to index

---

### Index Page (index.html)

* Displays all places
* Each place shown as a card:

  * Title
  * Price
  * View Details button
* Price filtering (client-side)
* Login link visibility based on authentication

---

### Place Details Page (place.html)

* Displays:

  * Title
  * Description
  * Price
  * Location
  * Owner
  * Amenities
* Displays reviews
* Shows review form if logged in

---

### Add Review Page (add_review.html)

* Accessible only if authenticated
* Form includes:

  * Review text
  * Rating
* Sends POST request to API

---

### Admin Page (admin.html)

* Restricted to admin users
* Displays:

  * Users
  * Places
  * Amenities
* Supports delete operations

---

## Key JavaScript Functions

### Authentication

* `getCookie(name)`
* `setCookie(name, value)`
* `isAuthenticated()`

### Places

* `fetchPlaces()`
* `displayPlaces(places)`
* `filterPlacesByPrice()`

### Place Details

* `loadPlaceDetails(placeId)`
* `displayPlaceDetails(place)`
* `loadReviews(placeId)`

### Reviews

* `submitReview(event)`

### Admin

* `checkAdmin()`
* `loadDashboard()`
* `deleteUser()`
* `deletePlace()`
* `deleteAmenity()`

---

## Security Considerations

* JWT stored in cookies for session management
* Authorization header used for protected routes
* HTML escaping to prevent XSS:

```js
escapeHtml()
```

---

## CORS Configuration (Backend Required)

If you encounter CORS errors, update your Flask backend:

```python
from flask_cors import CORS
CORS(app)
```

---

## Validation

* All HTML pages validated using W3C Validator
* Responsive design supported

---

## Future Improvements

* Edit functionality for admin
* Better UI/UX enhancements
* Pagination for places
* Search functionality

---

## Author

HBnB Project – Frontend Part (Part 4)

---

## License

This project is for educational purposes (Holberton School).
