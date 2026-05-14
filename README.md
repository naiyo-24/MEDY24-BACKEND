# Medy24 Backend

Backend system for Patho Lab management, including authentication, document uploads, and profile management.

## Setup Instructions

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Firebase Configuration (Required for Phone Authentication)

#### Step A: Download Firebase Service Account Key
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (Medy24)
3. Click the gear icon → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Save the JSON file as `secrets/firebase-adminsdk-medy24.json`

#### Step B: Enable Phone Authentication in Firebase
1. Go to **Build** → **Authentication** → **Get Started**
2. Click **Phone** and enable it
3. Add your phone numbers to the test list (for testing)

### 5. Configure Environment Variables
Copy values from `.env.example` and update `.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/medy24_db
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=medy24_db
DB_HOST=localhost
DB_PORT=5432

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=secrets/firebase-adminsdk-medy24.json

# JWT Configuration for backend tokens
JWT_SECRET=your-strong-random-secret-key-here
JWT_ALGORITHM=HS256
```

**To generate a strong JWT_SECRET:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Start the Backend Server
```bash
python main.py
```
The server will start on `http://0.0.0.0:8000`. You can access the API documentation at `http://localhost:8000/docs`.

## Customer Authentication API

### Phone Authentication Flow

#### 1. Check if Phone Number is Registered
```bash
POST /customers/check-phone
Body: {
  "phone_number": "+919876543210"
}
Response: {
  "message": "Phone check completed",
  "phone_number": "+919876543210",
  "exists": false,
  "user_id": null
}
```

#### 2. Send OTP (Triggered from Frontend)
The OTP is sent by Firebase from the client-side using Firebase Phone Authentication.

#### 3. Verify OTP and Register/Login
```bash
POST /customers/verify-otp
Body (Multipart Form):
{
  "token": "firebase_id_token_here",
  "phone_number": "+919876543210",
  "full_name": "John Doe",           # Required for new users
  "email": "john@example.com",       # Optional
  "alternative_phone_no": "+919876543211",  # Optional
  "saved_addresses": [               # Optional (JSON list)
    {
      "address": "123 Main St, City",
      "type": "home"
    }
  ],
  "profile_photo": <file>            # Optional
}
Response:
{
  "message": "Registration successful",
  "status": "signup",
  "user": {
    "customer_id": "CUST-1715708933",
    "phone_number": "+919876543210",
    "full_name": "John Doe",
    "email": "john@example.com",
    "alternative_phone_no": "+919876543211",
    "profile_photo": "/uploads/auth/CUST-1715708933/profile_photo.jpg",
    "saved_addresses": [...],
    "created_at": "2026-05-14T...",
    "updated_at": "2026-05-14T..."
  },
  "backend_token": "eyJhbGc..."  # Use this for authenticated requests
}
```

#### 4. Get Customer Profile
```bash
GET /customers/profile/{customer_id}
Response: {
  "message": "Profile retrieved successfully",
  "user": { ... }
}
```

#### 5. Update Customer Profile
```bash
PUT /customers/profile/{customer_id}
Body (Multipart Form):
{
  "full_name": "Jane Doe",           # Optional
  "email": "jane@example.com",       # Optional
  "alternative_phone_no": "+919876543212",  # Optional
  "profile_photo": <file>            # Optional
}
```

#### 6. Add Saved Address
```bash
POST /customers/addresses/{customer_id}
Body (JSON):
{
  "address": "456 Oak St, City",
  "address_type": "office"
}
Response: {
  "message": "Address added successfully",
  "address": {
    "id": 1,
    "address": "456 Oak St, City",
    "type": "office",
    "created_at": "2026-05-14T..."
  },
  "user": { ... }
}
```

#### 7. Delete Saved Address
```bash
DELETE /customers/addresses/{customer_id}/{address_id}
Response: {
  "message": "Address deleted successfully",
  "user": { ... }
}
```


