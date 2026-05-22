# Measles Sentinel — Setup Guide

## Requirements
- Python 3.9+
- Node.js 16+
- Firebase project

---

## 1. Install Python dependencies
```
pip install -r requirements.txt
```

## 2. Install JS dependencies (optional — for bundling)
```
npm install
```

## 3. Place model files
Copy your Teachable Machine export into:
```
static/model/model.json
static/model/metadata.json
static/model/weights.bin
```

## 4. Configure Firebase
Edit `static/js/firebase-config.js` — replace all `YOUR_*` values:
```
Firebase Console → Project Settings → Your Apps → Web App → Config
```
Enable in Firebase Console:
- Authentication → Email/Password + Google
- Firestore Database → Create database (test mode to start)
- Storage → Get started

## 5. Set environment variable
```
copy .env.example .env
```
Edit `.env` and set `SECRET_KEY` to any random string.

## 6. Run the app
```
python app.py
```
Open: http://localhost:5000

---

## Firestore Security Rules (production)
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /scans/{scanId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.userId;
      allow create: if request.auth != null && request.auth.uid == request.resource.data.userId;
    }
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Storage Rules (production)
```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /scans/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```
