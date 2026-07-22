# Kolak ERM — Frontend Integration Guide

> [!IMPORTANT]
> **Base API URL**: `http://127.0.0.1:8000/api/`  
> **Interactive Swagger UI**: `http://127.0.0.1:8000/api/docs/`  
> **ReDoc Documentation**: `http://127.0.0.1:8000/api/redoc/`

---

## 1. Authentication & JWT Flow

Kolak ERM uses JSON Web Tokens (JWT) for secure authentication. 

### Token Lifecycle
1. **Login**: `POST /api/auth/login/` with `username` (or `email`) + `password`.
2. **Save Tokens**: Store `access` (short-lived, 1 day) in memory or state manager and `refresh` (long-lived, 7 days) securely.
3. **Authorization Header**: Include `Authorization: Bearer <access_token>` in all API requests.
4. **Token Refresh**: When an API request returns `401 Unauthorized`, send `POST /api/auth/token/refresh/` with `{ "refresh": "<refresh_token>" }` to get a new `access` token.
5. **Logout**: `POST /api/auth/logout/` with `{ "refresh": "<refresh_token>" }` to blacklist the refresh token on the server and clear local state.

---

## 2. API Endpoints Summary

### Auth Endpoints (`/api/auth/`)

| Method | Endpoint | Description | Request Body / Params |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login/` | Staff login (returns access, refresh, user object) | `{ "username": "...", "password": "..." }` |
| `POST` | `/api/auth/token/refresh/` | Refresh access token | `{ "refresh": "<refresh_token>" }` |
| `POST` | `/api/auth/logout/` | Blacklist refresh token & logout | `{ "refresh": "<refresh_token>" }` |
| `GET` | `/api/auth/me/` | Fetch current logged-in user profile | None |
| `PATCH` | `/api/auth/me/` | Update logged-in user details | Profile fields |
| `POST` | `/api/auth/change-password/` | Change password | `{ "old_password": "...", "new_password": "..." }` |

---

### Staff & User Administration (`/api/users/`)

| Method | Endpoint | Description | Query Params / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/users/` | List all staff members | `?search=...`, `?department=...`, `?role=...`, `?status=...` |
| `POST` | `/api/users/` | Create a new staff account | `{ "email": "...", "password": "...", "first_name": "...", "last_name": "...", "role": "<uuid>", "department": "<uuid>" }` |
| `GET` | `/api/users/<id>/` | Get single staff details | None |
| `PATCH` | `/api/users/<id>/` | Update staff info/role/dept | Updated fields |
| `POST` | `/api/users/<id>/toggle-status/` | Toggle account Active/Inactive | None |
| `GET` | `/api/users/doctors/` | Quick list of active doctors | `?search=...`, `?department=...` |

---

### Roles & Departments (`/api/users/roles/`, `/api/users/departments/`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/users/roles/` | List all hospital roles |
| `POST` | `/api/users/roles/` | Create custom role |
| `GET` | `/api/users/departments/` | List all hospital departments |
| `POST` | `/api/users/departments/` | Create department |
| `GET` | `/api/users/permissions/` | List system permissions |

---

### Patients API (`/api/patients/`)

| Method | Endpoint | Description | Example Request / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/patients/` | List patients (paginated) | `?search=Jane`, `?gender=Female`, `?status=Active` |
| `POST` | `/api/patients/` | Register patient with nested allergies & NOK | `{ "first_name": "...", "last_name": "...", "allergies": [...], "next_of_kin": [...] }` |
| `GET` | `/api/patients/search/` | Quick front-desk lookup | `?q=Jane` (searches name, phone, PAT-ID) |
| `GET` | `/api/patients/<id>/` | Retrieve full patient record | None |
| `GET` | `/api/patients/<id>/enrollments/` | Get patient HMO enrollments | `?is_active=true` |
| `POST` | `/api/patients/<id>/enrollments/` | Add HMO enrollment | `{ "hmo_provider": "<uuid>", "hmo_number": "...", "plan_name": "..." }` |

---

### Appointments API (`/api/appointments/`)

| Method | Endpoint | Description | Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/appointments/` | List appointments | `?doctor=<uuid>`, `?patient=<uuid>`, `?appointment_date=YYYY-MM-DD` |
| `POST` | `/api/appointments/` | Book appointment (prevents double-booking) | `{ "patient": "<uuid>", "doctor": "<uuid>", "appointment_date": "YYYY-MM-DD", "start_time": "09:00", "end_time": "09:30" }` |
| `POST` | `/api/appointments/<id>/check-in/` | Check-in patient & auto-create queue entry | None |
| `POST` | `/api/appointments/<id>/cancel/` | Cancel appointment | `{ "cancellation_reason": "..." }` |

---

### Queue Management API (`/api/appointments/queue/`)

| Method | Endpoint | Description | Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/appointments/queue/` | Today's waiting queue | `?doctor=<uuid>`, `?status=Waiting` |
| `POST` | `/api/appointments/queue/` | Add walk-in patient to queue | `{ "patient": "<uuid>", "doctor": "<uuid>", "priority": "Urgent" }` |
| `POST` | `/api/appointments/queue/<id>/call-next/` | Call next patient for consultation | None |
| `POST` | `/api/appointments/queue/<id>/complete/` | Mark consultation completed | None |

---

## 3. Recommended Frontend Axios Setup (JavaScript / TypeScript)

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Access Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor: Automatic Token Refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          window.location.href = '/login';
          return Promise.reject(error);
        }

        const res = await axios.post(`${API_BASE_URL}auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken = res.data.access;
        const newRefreshToken = res.data.refresh;

        localStorage.setItem('access_token', newAccessToken);
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken);
        }

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 4. Sample Integration Snippets

### Staff Login
```typescript
async function loginUser(usernameOrEmail, password) {
  const response = await api.post('auth/login/', {
    username: usernameOrEmail,
    password: password,
  });

  const { access, refresh, user } = response.data;
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
  
  console.log('Logged in user:', user.full_name, 'Role:', user.role_detail?.name);
  return user;
}
```

### Patient Quick Search & Registration
```typescript
// Quick search for Front Desk
async function searchPatients(query: string) {
  const res = await api.get(`patients/search/?q=${encodeURIComponent(query)}`);
  return res.data; // Array of lightweight patient objects
}

// Full Registration
async function registerPatient(patientData) {
  const res = await api.post('patients/', patientData);
  return res.data; // Auto-generated patient_id included (e.g. PAT-00001)
}
```

### Book Appointment & Check-In
```typescript
// Book appointment
async function bookAppointment(patientId, doctorId, date, startTime, endTime) {
  const res = await api.post('appointments/', {
    patient: patientId,
    doctor: doctorId,
    appointment_date: date,
    start_time: startTime,
    end_time: endTime,
    appointment_type: 'Consultation',
  });
  return res.data;
}

// Check in patient when they arrive
async function checkInPatient(appointmentId) {
  const res = await api.post(`appointments/${appointmentId}/check-in/`);
  console.log('Queue Ticket Number:', res.data.queue_entry.ticket_number);
  return res.data;
}
```
