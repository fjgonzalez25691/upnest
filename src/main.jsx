import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter  } from 'react-router-dom'
import { AuthProvider } from 'react-oidc-context'
import './index.css'
import App from './App.jsx'

import { cognitoConfig } from './auth/cognitoConfig.js'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider {...cognitoConfig}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>,
)

