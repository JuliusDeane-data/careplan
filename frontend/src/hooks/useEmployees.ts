/**
 * Employee React Query hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { employeeService } from '@/services/employee.service'
import type { EmployeeFilters, EmployeeCreate, EmployeeUpdate } from '@/types/employee'
import { EMPLOYEE_CONFIG } from '@/config/employee.config'

/**
 * Hook to fetch paginated employees with filters
 */
export function useEmployees(filters?: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => employeeService.getEmployees(filters),
    staleTime: EMPLOYEE_CONFIG.QUERY_STALE_TIME,
    placeholderData: (prev) => prev, // Keep previous data while loading
  })
}

/**
 * Hook to fetch single employee
 */
export function useEmployee(id: number | undefined) {
  return useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeeService.getEmployee(id!),
    enabled: !!id,
    staleTime: EMPLOYEE_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch employee profile (detailed)
 */
export function useEmployeeProfile(id: number | undefined) {
  return useQuery({
    queryKey: ['employee-profile', id],
    queryFn: () => employeeService.getEmployeeProfile(id!),
    enabled: !!id,
    staleTime: EMPLOYEE_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to create employee
 */
export function useCreateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: EmployeeCreate) => employeeService.createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })
}

/**
 * Hook to update employee
 */
export function useUpdateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<EmployeeUpdate> }) =>
      employeeService.updateEmployee(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      queryClient.invalidateQueries({ queryKey: ['employee', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['employee-profile', variables.id] })
    },
  })
}

/**
 * Hook to delete employee
 */
export function useDeleteEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => employeeService.deleteEmployee(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })
}
