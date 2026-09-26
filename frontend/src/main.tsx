import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import './index.css'

import Layout from './components/Layout'
import Login from './pages/Login'
import ForgotPassword from './pages/ForgotPassword'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Warehouses from './pages/Warehouses'
import Inventory from './pages/Inventory'
import Receipts from './pages/Receipts'
import Deliveries from './pages/Deliveries'
import Transfers from './pages/Transfers'
import Adjustments from './pages/Adjustments'
import MoveHistory from './pages/MoveHistory'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/warehouses" element={<Warehouses />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/receipts" element={<Receipts />} />
            <Route path="/deliveries" element={<Deliveries />} />
            <Route path="/transfers" element={<Transfers />} />
            <Route path="/adjustments" element={<Adjustments />} />
            <Route path="/history" element={<MoveHistory />} />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </QueryClientProvider>
  </React.StrictMode>
)
