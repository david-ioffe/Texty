import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDOBkq_VrIvOs_t2-2VhwaVKvXylIUO5z8",
  authDomain: "texty-ee5ff.firebaseapp.com",
  projectId: "texty-ee5ff",
  storageBucket: "texty-ee5ff.firebasestorage.app",
  messagingSenderId: "73073852972",
  appId: "1:73073852972:web:668f6ab637cd2f9879c789",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);