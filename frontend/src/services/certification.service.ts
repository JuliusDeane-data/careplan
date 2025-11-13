/**
 * Certification service - API integration for certification and qualification management
 */

import api from './api'
import type {
  Qualification,
  QualificationList,
  EmployeeCertification,
  CreateEmployeeCertification,
  UpdateEmployeeCertification,
  VerifyCertification,
  ExpiringCertification,
  CertificationComplianceReport,
} from '@/types'

export const certificationService = {
  // ============== Qualification Management ==============

  /**
   * Get all qualifications with optional filtering
   */
  async getQualifications(params?: {
    category?: string
    is_required?: boolean
    is_active?: boolean
    search?: string
    ordering?: string
  }): Promise<QualificationList[]> {
    const response = await api.get<QualificationList[]>(
      '/certifications/qualifications/',
      { params }
    )
    return response.data
  },

  /**
   * Get single qualification by ID
   */
  async getQualification(id: number): Promise<Qualification> {
    const response = await api.get<Qualification>(
      `/certifications/qualifications/${id}/`
    )
    return response.data
  },

  /**
   * Create new qualification (admin/manager only)
   */
  async createQualification(data: Partial<Qualification>): Promise<Qualification> {
    const response = await api.post<Qualification>(
      '/certifications/qualifications/',
      data
    )
    return response.data
  },

  /**
   * Update qualification (admin/manager only)
   */
  async updateQualification(
    id: number,
    data: Partial<Qualification>
  ): Promise<Qualification> {
    const response = await api.patch<Qualification>(
      `/certifications/qualifications/${id}/`,
      data
    )
    return response.data
  },

  /**
   * Delete qualification (soft delete - admin/manager only)
   */
  async deleteQualification(id: number): Promise<void> {
    await api.delete(`/certifications/qualifications/${id}/`)
  },

  /**
   * Get required qualifications only
   */
  async getRequiredQualifications(): Promise<QualificationList[]> {
    const response = await api.get<QualificationList[]>(
      '/certifications/qualifications/required/'
    )
    return response.data
  },

  /**
   * Get qualifications grouped by category
   */
  async getQualificationsByCategory(): Promise<{
    [key: string]: {
      name: string
      qualifications: QualificationList[]
    }
  }> {
    const response = await api.get(
      '/certifications/qualifications/by-category/'
    )
    return response.data
  },

  // ============== Employee Certification Management ==============

  /**
   * Get employee certifications with optional filtering
   */
  async getEmployeeCertifications(params?: {
    employee?: number
    qualification?: number
    status?: string
    search?: string
    ordering?: string
  }): Promise<EmployeeCertification[]> {
    const response = await api.get<EmployeeCertification[]>(
      '/certifications/employee-certifications/',
      { params }
    )
    return response.data
  },

  /**
   * Get single employee certification by ID
   */
  async getEmployeeCertification(id: number): Promise<EmployeeCertification> {
    const response = await api.get<EmployeeCertification>(
      `/certifications/employee-certifications/${id}/`
    )
    return response.data
  },

  /**
   * Create new employee certification
   */
  async createEmployeeCertification(
    data: CreateEmployeeCertification
  ): Promise<EmployeeCertification> {
    // Handle file upload if certificate_document is provided
    let formData: FormData | CreateEmployeeCertification = data

    if (data.certificate_document) {
      formData = new FormData()
      formData.append('qualification_id', String(data.qualification_id))
      if (data.employee_id) {
        formData.append('employee_id', String(data.employee_id))
      }
      formData.append('issue_date', data.issue_date)
      if (data.expiry_date) {
        formData.append('expiry_date', data.expiry_date)
      }
      if (data.certificate_document) {
        formData.append('certificate_document', data.certificate_document)
      }
      if (data.notes) {
        formData.append('notes', data.notes)
      }
    }

    const response = await api.post<EmployeeCertification>(
      '/certifications/employee-certifications/',
      formData,
      {
        headers:
          formData instanceof FormData
            ? { 'Content-Type': 'multipart/form-data' }
            : undefined,
      }
    )
    return response.data
  },

  /**
   * Update employee certification
   */
  async updateEmployeeCertification(
    id: number,
    data: UpdateEmployeeCertification
  ): Promise<EmployeeCertification> {
    // Handle file upload if certificate_document is provided
    let formData: FormData | UpdateEmployeeCertification = data

    if (data.certificate_document) {
      formData = new FormData()
      if (data.issue_date) {
        formData.append('issue_date', data.issue_date)
      }
      if (data.expiry_date) {
        formData.append('expiry_date', data.expiry_date)
      }
      if (data.certificate_document) {
        formData.append('certificate_document', data.certificate_document)
      }
      if (data.notes) {
        formData.append('notes', data.notes)
      }
    }

    const response = await api.patch<EmployeeCertification>(
      `/certifications/employee-certifications/${id}/`,
      formData,
      {
        headers:
          formData instanceof FormData
            ? { 'Content-Type': 'multipart/form-data' }
            : undefined,
      }
    )
    return response.data
  },

  /**
   * Delete employee certification
   */
  async deleteEmployeeCertification(id: number): Promise<void> {
    await api.delete(`/certifications/employee-certifications/${id}/`)
  },

  /**
   * Verify employee certification (manager/admin only)
   */
  async verifyCertification(
    id: number,
    data: VerifyCertification
  ): Promise<EmployeeCertification> {
    const response = await api.post<{
      message: string
      certification: EmployeeCertification
    }>(`/certifications/employee-certifications/${id}/verify/`, data)
    return response.data.certification
  },

  /**
   * Get current user's certifications
   */
  async getMyCertifications(): Promise<EmployeeCertification[]> {
    const response = await api.get<EmployeeCertification[]>(
      '/certifications/employee-certifications/my-certifications/'
    )
    return response.data
  },

  /**
   * Get certifications for specific employee
   */
  async getEmployeeCertificationsByEmployee(
    employeeId: number
  ): Promise<EmployeeCertification[]> {
    const response = await api.get<EmployeeCertification[]>(
      '/certifications/employee-certifications/',
      { params: { employee: employeeId } }
    )
    return response.data
  },

  // ============== Certification Reports & Analytics ==============

  /**
   * Get expiring certifications
   */
  async getExpiringCertifications(
    days: number = 90
  ): Promise<ExpiringCertification[]> {
    const response = await api.get<ExpiringCertification[]>(
      '/certifications/employee-certifications/expiring/',
      { params: { days } }
    )
    return response.data
  },

  /**
   * Get expired certifications
   */
  async getExpiredCertifications(): Promise<ExpiringCertification[]> {
    const response = await api.get<ExpiringCertification[]>(
      '/certifications/employee-certifications/expired/'
    )
    return response.data
  },

  /**
   * Get certifications pending verification (manager/admin only)
   */
  async getPendingVerificationCertifications(): Promise<ExpiringCertification[]> {
    const response = await api.get<ExpiringCertification[]>(
      '/certifications/employee-certifications/pending-verification/'
    )
    return response.data
  },

  /**
   * Get certification compliance report
   */
  async getComplianceReport(): Promise<CertificationComplianceReport> {
    const response = await api.get<CertificationComplianceReport>(
      '/certifications/employee-certifications/compliance-report/'
    )
    return response.data
  },

  /**
   * Get certification statistics for an employee
   */
  async getEmployeeCertificationStats(employeeId: number): Promise<{
    total: number
    active: number
    expiring_soon: number
    expired: number
    pending_verification: number
  }> {
    const certifications = await this.getEmployeeCertificationsByEmployee(employeeId)

    return {
      total: certifications.length,
      active: certifications.filter((c) => c.status === 'ACTIVE').length,
      expiring_soon: certifications.filter((c) => c.status === 'EXPIRING_SOON').length,
      expired: certifications.filter((c) => c.status === 'EXPIRED').length,
      pending_verification: certifications.filter(
        (c) => c.status === 'PENDING_VERIFICATION'
      ).length,
    }
  },
}
