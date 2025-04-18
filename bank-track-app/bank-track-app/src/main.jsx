import { ChakraProvider } from "@chakra-ui/react";
import { ClerkProvider } from '@clerk/clerk-react';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
// import './index.css';

// Import the Clerk publishable key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Publishable Key")
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <ChakraProvider>
        <App />
      </ChakraProvider>
    </ClerkProvider>
  </React.StrictMode>,
)
