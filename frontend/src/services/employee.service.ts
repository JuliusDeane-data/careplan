/**
 * Employee service - API integration for employee management
 */

import api from './api'
import type {
  Employee,
  EmployeeSummary,
  EmployeeFilters,
  EmployeeCreate,
  EmployeeUpdate,
} from '@/types/employee'

export const employeeService = {
  /**
   * Get paginated list of employees with optional filters
   */
  async getEmployees(filters?: EmployeeFilters) {
    const response = await api.get<{
      count: number
      next: string | null
      previous: string | null
      results: EmployeeSummary[]
    }>('/employees/', { params: filters })

    return response.data
  },

  /**
   * Get single employee by ID
   */
  async getEmployee(id: number): Promise<Employee> {
    const response = await api.get<Employee>(`/employees/${id}/`)
    return response.data
  },

  /**
   * Get employee profile (more detailed than basic GET)
   */
  async getEmployeeProfile(id: number): Promise<Employee> {
    const response = await api.get<Employee>(`/employees/${id}/profile/`)
    return response.data
  },

  /**
   * Create new employee (admin only)
   */
  async createEmployee(data: EmployeeCreate): Promise<Employee> {
    const response = await api.post<Employee>('/employees/', data)
    return response.data
  },

  /**
   * Update employee (admin/manager only)
   */
  async updateEmployee(id: number, data: Partial<EmployeeUpdate>): Promise<Employee> {
    const response = await api.patch<Employee>(`/employees/${id}/`, data)
    return response.data
  },

  /**
   * Delete employee (soft delete - admin only)
   */
  async deleteEmployee(id: number): Promise<void> {
    await api.delete(`/employees/${id}/`)
  },

  /**
   * Search employees by query
   */
  async searchEmployees(query: string): Promise<EmployeeSummary[]> {
    const response = await api.get<EmployeeSummary[]>('/employees/search/', {
      params: { q: query },
    })
    return response.data
  },

  /**
   * Export employees to CSV
   */
  async exportEmployees(filters?: EmployeeFilters): Promise<Blob> {
    const response = await api.get('/employees/export/', {
      params: filters,
      responseType: 'blob',
    })
    return response.data
  },
}
