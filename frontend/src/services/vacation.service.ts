import api from './api'
import type {
  VacationRequest,
  VacationBalance,
  VacationRequestCreate,
  VacationRequestUpdate,
  VacationDenyRequest,
  VacationFilters,
} from '@/types/vacation'

export const vacationService = {
  /**
   * Get all vacation requests (with optional filters)
   */
  async getRequests(filters?: VacationFilters) {
    const response = await api.get('/vacation/requests/', { params: filters })
    return response.data
  },

  /**
   * Get my vacation requests
   */
  async getMyRequests(filters?: VacationFilters): Promise<VacationRequest[]> {
    const response = await api.get('/vacation/requests/my/', { params: filters })
    return response.data.results || response.data
  },

  /**
   * Get a single vacation request by ID
   */
  async getRequest(id: number): Promise<VacationRequest> {
    const response = await api.get(`/vacation/requests/${id}/`)
    return response.data
  },

  /**
   * Create a new vacation request
   */
  async createRequest(data: VacationRequestCreate): Promise<VacationRequest> {
    const response = await api.post('/vacation/requests/', data)
    return response.data
  },

  /**
   * Update a vacation request
   */
  async updateRequest(
    id: number,
    data: VacationRequestUpdate
  ): Promise<VacationRequest> {
    const response = await api.put(`/vacation/requests/${id}/`, data)
    return response.data
  },

  /**
   * Cancel a vacation request
   */
  async cancelRequest(id: number): Promise<VacationRequest> {
    const response = await api.post(`/vacation/requests/${id}/cancel/`)
    return response.data
  },

  /**
   * Approve a vacation request (manager/admin only)
   */
  async approveRequest(id: number): Promise<VacationRequest> {
    const response = await api.post(`/vacation/requests/${id}/approve/`)
    return response.data
  },

  /**
   * Deny a vacation request (manager/admin only)
   */
  async denyRequest(id: number, data: VacationDenyRequest): Promise<VacationRequest> {
    const response = await api.post(`/vacation/requests/${id}/deny/`, data)
    return response.data
  },

  /**
   * Get vacation balance for current user
   */
  async getBalance(): Promise<VacationBalance> {
    const response = await api.get('/vacation/balance/')
    return response.data
  },

  /**
   * Get vacation balance for a specific employee (manager/admin only)
   */
  async getEmployeeBalance(employeeId: number): Promise<VacationBalance> {
    const response = await api.get(`/vacation/balance/${employeeId}/`)
    return response.data
  },
}
