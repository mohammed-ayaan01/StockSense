import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

// Auth
export const authApi = {
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  register: (data: object) => api.post('/auth/register', data),
  forgotPassword: (email: string) => api.post('/auth/forgot-password', { email }),
  resetPassword: (email: string, otp: string, new_password: string) =>
    api.post('/auth/reset-password', { email, otp, new_password }),
  me: () => api.get('/auth/me'),
}

// Dashboard
export const dashboardApi = {
  kpis: () => api.get('/dashboard/kpis'),
  recentMovements: () => api.get('/dashboard/recent-movements'),
}

// Products
export const productsApi = {
  list: (params?: object) => api.get('/products', { params }),
  get: (id: number) => api.get(`/products/${id}`),
  create: (data: object) => api.post('/products', data),
  update: (id: number, data: object) => api.patch(`/products/${id}`, data),
  listCategories: () => api.get('/categories'),
  createCategory: (data: object) => api.post('/categories', data),
  listUom: () => api.get('/uom'),
  createUom: (data: object) => api.post('/uom', data),
}

// Warehouses
export const warehousesApi = {
  list: () => api.get('/warehouses'),
  get: (id: number) => api.get(`/warehouses/${id}`),
  create: (data: object) => api.post('/warehouses', data),
  update: (id: number, data: object) => api.patch(`/warehouses/${id}`, data),
  listLocations: (params?: object) => api.get('/locations', { params }),
  createLocation: (data: object) => api.post('/locations', data),
  updateLocation: (id: number, data: object) => api.patch(`/locations/${id}`, data),
}

// Inventory
export const inventoryApi = {
  list: (params?: object) => api.get('/inventory', { params }),
}

// Receipts
export const receiptsApi = {
  list: (params?: object) => api.get('/receipts', { params }),
  get: (id: number) => api.get(`/receipts/${id}`),
  create: (data: object) => api.post('/receipts', data),
  confirm: (id: number) => api.post(`/receipts/${id}/confirm`),
  validate: (id: number) => api.post(`/receipts/${id}/validate`),
  cancel: (id: number) => api.post(`/receipts/${id}/cancel`),
}

// Deliveries
export const deliveriesApi = {
  list: (params?: object) => api.get('/deliveries', { params }),
  get: (id: number) => api.get(`/deliveries/${id}`),
  create: (data: object) => api.post('/deliveries', data),
  advance: (id: number) => api.post(`/deliveries/${id}/advance`),
  cancel: (id: number) => api.post(`/deliveries/${id}/cancel`),
}

// Transfers
export const transfersApi = {
  list: (params?: object) => api.get('/transfers', { params }),
  get: (id: number) => api.get(`/transfers/${id}`),
  create: (data: object) => api.post('/transfers', data),
  validate: (id: number) => api.post(`/transfers/${id}/validate`),
  cancel: (id: number) => api.post(`/transfers/${id}/cancel`),
}

// Adjustments
export const adjustmentsApi = {
  list: (params?: object) => api.get('/adjustments', { params }),
  get: (id: number) => api.get(`/adjustments/${id}`),
  create: (data: object) => api.post('/adjustments', data),
  validate: (id: number) => api.post(`/adjustments/${id}/validate`),
  cancel: (id: number) => api.post(`/adjustments/${id}/cancel`),
}

// Movements
export const movementsApi = {
  list: (params?: object) => api.get('/movements', { params }),
}
