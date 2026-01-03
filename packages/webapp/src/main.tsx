import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { LocaleProvider } from '@/lib/locale'
import { router } from './router'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <LocaleProvider>
        <RouterProvider router={router} />
      </LocaleProvider>
    </HelmetProvider>
  </React.StrictMode>,
)
