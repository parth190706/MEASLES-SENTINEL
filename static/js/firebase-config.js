// ============================================================
// REPLACE THESE VALUES WITH YOUR FIREBASE PROJECT CREDENTIALS
// Firebase Console → Project Settings → Your Apps → Firebase SDK
// ============================================================
const firebaseConfig = {
  apiKey: "AIzaSyBYUflFhbkotKmNiUGYhyt0J8EbOhVhKOI",
  authDomain: "measles-sentinel.firebaseapp.com",
  projectId: "measles-sentinel",
  storageBucket: "measles-sentinel.firebasestorage.app",
  messagingSenderId: "537680892605",
  appId: "1:537680892605:web:efd2cb86ef3ab59d0e5dd4",
  measurementId: "G-MKT06SEHLT"
};

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  GoogleAuthProvider,
  signInWithPopup
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import {
  getFirestore,
  collection,
  addDoc,
  getDocs,
  doc,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  serverTimestamp
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import {
  getStorage,
  ref,
  uploadBytes,
  getDownloadURL
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-storage.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);
const googleProvider = new GoogleAuthProvider();

// ===== AUTH HELPERS =====
export async function registerUser(email, password, name) {
  const cred = await createUserWithEmailAndPassword(auth, email, password);
  await updateProfile(cred.user, { displayName: name });
  await addDoc(collection(db, "users"), {
    uid: cred.user.uid,
    name,
    email,
    createdAt: serverTimestamp()
  });
  return cred.user;
}

export async function loginUser(email, password) {
  const cred = await signInWithEmailAndPassword(auth, email, password);
  return cred.user;
}

export async function loginWithGoogle() {
  const result = await signInWithPopup(auth, googleProvider);
  return result.user;
}

export async function logoutUser() {
  await signOut(auth);
  window.location.href = "/login";
}

export function onAuthChange(cb) {
  return onAuthStateChanged(auth, cb);
}

export function getCurrentUser() {
  return auth.currentUser;
}

// ===== FIRESTORE HELPERS =====
export async function saveScan(userId, scanData) {
  const ref = await addDoc(collection(db, "scans"), {
    userId,
    ...scanData,
    createdAt: serverTimestamp()
  });
  return ref.id;
}

export async function getUserScans(userId) {
  const q = query(
    collection(db, "scans"),
    where("userId", "==", userId),
    orderBy("createdAt", "desc")
  );
  const snap = await getDocs(q);
  return snap.docs.map(d => ({ id: d.id, ...d.data() }));
}

export async function deleteScan(scanId) {
  await deleteDoc(doc(db, "scans", scanId));
}

// ===== STORAGE HELPERS =====
export async function uploadImage(userId, file) {
  const storageRef = ref(storage, `scans/${userId}/${Date.now()}_${file.name}`);
  const snap = await uploadBytes(storageRef, file);
  return await getDownloadURL(snap.ref);
}

export { auth, db, storage };
