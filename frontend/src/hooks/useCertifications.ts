/**
 * Certification React Query hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { certificationService } from '@/services/certification.service'
import type {
  CreateEmployeeCertification,
  UpdateEmployeeCertification,
  VerifyCertification,
  Qualification,
} from '@/types'
import { CERTIFICATION_CONFIG } from '@/config/certification.config'

// ============== Qualification Hooks ==============

/**
 * Hook to fetch qualifications with optional filtering
 */
export function useQualifications(params?: {
  category?: string
  is_required?: boolean
  is_active?: boolean
  search?: string
  ordering?: string
}) {
  return useQuery({
    queryKey: ['qualifications', params],
    queryFn: () => certificationService.getQualifications(params),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
    placeholderData: (prev) => prev,
  })
}

/**
 * Hook to fetch single qualification
 */
export function useQualification(id: number | undefined) {
  return useQuery({
    queryKey: ['qualification', id],
    queryFn: () => certificationService.getQualification(id!),
    enabled: !!id,
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch required qualifications
 */
export function useRequiredQualifications() {
  return useQuery({
    queryKey: ['qualifications', 'required'],
    queryFn: () => certificationService.getRequiredQualifications(),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch qualifications grouped by category
 */
export function useQualificationsByCategory() {
  return useQuery({
    queryKey: ['qualifications', 'by-category'],
    queryFn: () => certificationService.getQualificationsByCategory(),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to create qualification
 */
export function useCreateQualification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Qualification>) =>
      certificationService.createQualification(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['qualifications'] })
    },
  })
}

/**
 * Hook to update qualification
 */
export function useUpdateQualification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Qualification> }) =>
      certificationService.updateQualification(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['qualifications'] })
      queryClient.invalidateQueries({ queryKey: ['qualification', variables.id] })
    },
  })
}

/**
 * Hook to delete qualification
 */
export function useDeleteQualification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => certificationService.deleteQualification(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['qualifications'] })
    },
  })
}

// ============== Employee Certification Hooks ==============

/**
 * Hook to fetch employee certifications with optional filtering
 */
export function useEmployeeCertifications(params?: {
  employee?: number
  qualification?: number
  status?: string
  search?: string
  ordering?: string
}) {
  return useQuery({
    queryKey: ['employee-certifications', params],
    queryFn: () => certificationService.getEmployeeCertifications(params),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
    placeholderData: (prev) => prev,
  })
}

/**
 * Hook to fetch single employee certification
 */
export function useEmployeeCertification(id: number | undefined) {
  return useQuery({
    queryKey: ['employee-certification', id],
    queryFn: () => certificationService.getEmployeeCertification(id!),
    enabled: !!id,
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch current user's certifications
 */
export function useMyCertifications() {
  return useQuery({
    queryKey: ['my-certifications'],
    queryFn: () => certificationService.getMyCertifications(),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch certifications for specific employee
 */
export function useEmployeeCertificationsByEmployee(employeeId: number | undefined) {
  return useQuery({
    queryKey: ['employee-certifications', 'by-employee', employeeId],
    queryFn: () =>
      certificationService.getEmployeeCertificationsByEmployee(employeeId!),
    enabled: !!employeeId,
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to create employee certification
 */
export function useCreateEmployeeCertification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateEmployeeCertification) =>
      certificationService.createEmployeeCertification(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['employee-certifications'] })
      queryClient.invalidateQueries({ queryKey: ['my-certifications'] })
      queryClient.invalidateQueries({
        queryKey: ['employee-certifications', 'by-employee', data.employee.id],
      })
      queryClient.invalidateQueries({ queryKey: ['expiring-certifications'] })
      queryClient.invalidateQueries({ queryKey: ['compliance-report'] })
    },
  })
}

/**
 * Hook to update employee certification
 */
export function useUpdateEmployeeCertification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number
      data: UpdateEmployeeCertification
    }) => certificationService.updateEmployeeCertification(id, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['employee-certifications'] })
      queryClient.invalidateQueries({
        queryKey: ['employee-certification', variables.id],
      })
      queryClient.invalidateQueries({ queryKey: ['my-certifications'] })
      queryClient.invalidateQueries({
        queryKey: ['employee-certifications', 'by-employee', data.employee.id],
      })
      queryClient.invalidateQueries({ queryKey: ['expiring-certifications'] })
      queryClient.invalidateQueries({ queryKey: ['compliance-report'] })
    },
  })
}

/**
 * Hook to delete employee certification
 */
export function useDeleteEmployeeCertification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => certificationService.deleteEmployeeCertification(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-certifications'] })
      queryClient.invalidateQueries({ queryKey: ['my-certifications'] })
      queryClient.invalidateQueries({ queryKey: ['expiring-certifications'] })
      queryClient.invalidateQueries({ queryKey: ['compliance-report'] })
    },
  })
}

/**
 * Hook to verify employee certification
 */
export function useVerifyCertification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: VerifyCertification }) =>
      certificationService.verifyCertification(id, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['employee-certifications'] })
      queryClient.invalidateQueries({
        queryKey: ['employee-certification', variables.id],
      })
      queryClient.invalidateQueries({
        queryKey: ['pending-verification-certifications'],
      })
      queryClient.invalidateQueries({
        queryKey: ['employee-certifications', 'by-employee', data.employee.id],
      })
      queryClient.invalidateQueries({ queryKey: ['compliance-report'] })
    },
  })
}

// ============== Certification Report Hooks ==============

/**
 * Hook to fetch expiring certifications
 */
export function useExpiringCertifications(days: number = 90) {
  return useQuery({
    queryKey: ['expiring-certifications', days],
    queryFn: () => certificationService.getExpiringCertifications(days),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch expired certifications
 */
export function useExpiredCertifications() {
  return useQuery({
    queryKey: ['expired-certifications'],
    queryFn: () => certificationService.getExpiredCertifications(),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch certifications pending verification
 */
export function usePendingVerificationCertifications() {
  return useQuery({
    queryKey: ['pending-verification-certifications'],
    queryFn: () => certificationService.getPendingVerificationCertifications(),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch certification compliance report
 */
export function useComplianceReport() {
  return useQuery({
    queryKey: ['compliance-report'],
    queryFn: () => certificationService.getComplianceReport(),
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch certification statistics for an employee
 */
export function useEmployeeCertificationStats(employeeId: number | undefined) {
  return useQuery({
    queryKey: ['employee-certification-stats', employeeId],
    queryFn: () => certificationService.getEmployeeCertificationStats(employeeId!),
    enabled: !!employeeId,
    staleTime: CERTIFICATION_CONFIG.QUERY_STALE_TIME,
  })
}
