import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { vacationService } from '@/services/vacation.service'
import type {
  VacationFilters,
  VacationRequestCreate,
  VacationDenyRequest,
} from '@/types/vacation'

/**
 * Hook to fetch vacation requests with optional filters
 */
export function useVacationRequests(filters?: VacationFilters) {
  return useQuery({
    queryKey: ['vacation-requests', filters],
    queryFn: () => vacationService.getRequests(filters),
    keepPreviousData: true,
  })
}

/**
 * Hook to fetch my vacation requests
 */
export function useMyVacationRequests(filters?: VacationFilters) {
  return useQuery({
    queryKey: ['my-vacation-requests', filters],
    queryFn: () => vacationService.getMyRequests(filters),
  })
}

/**
 * Hook to fetch a single vacation request
 */
export function useVacationRequest(id: number | undefined) {
  return useQuery({
    queryKey: ['vacation-request', id],
    queryFn: () => vacationService.getRequest(id!),
    enabled: !!id,
  })
}

/**
 * Hook to fetch vacation balance
 */
export function useVacationBalance() {
  return useQuery({
    queryKey: ['vacation-balance'],
    queryFn: vacationService.getBalance,
  })
}

/**
 * Hook to create a vacation request
 */
export function useCreateVacationRequest() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: VacationRequestCreate) => vacationService.createRequest(data),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries(['my-vacation-requests'])
      queryClient.invalidateQueries(['vacation-requests'])
      queryClient.invalidateQueries(['vacation-balance'])
    },
  })
}

/**
 * Hook to cancel a vacation request
 */
export function useCancelVacationRequest() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => vacationService.cancelRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['my-vacation-requests'])
      queryClient.invalidateQueries(['vacation-requests'])
      queryClient.invalidateQueries(['vacation-balance'])
    },
  })
}

/**
 * Hook to approve a vacation request (manager/admin)
 */
export function useApproveVacationRequest() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => vacationService.approveRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['vacation-requests'])
      queryClient.invalidateQueries(['vacation-balance'])
    },
  })
}

/**
 * Hook to deny a vacation request (manager/admin)
 */
export function useDenyVacationRequest() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: VacationDenyRequest }) =>
      vacationService.denyRequest(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['vacation-requests'])
    },
  })
}
