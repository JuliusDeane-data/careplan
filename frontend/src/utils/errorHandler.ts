/**
 * Centralized error handling utilities
 */

import axios from 'axios'

export interface ApiError {
  message: string
  status?: number
  code?: string
  field?: string
}

/**
 * Extracts a user-friendly error message from an API error
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const data = error.response?.data

    // Extract message from various response formats
    const message =
      data?.message ||
      data?.detail ||
      data?.error ||
      (typeof data === 'string' ? data : null)

    // Map common HTTP status codes to user-friendly messages
    if (status === 400) {
      return message || 'Invalid request. Please check your input.'
    }
    if (status === 401) {
      return 'Your session has expired. Please log in again.'
    }
    if (status === 403) {
      return 'You do not have permission to perform this action.'
    }
    if (status === 404) {
      return 'The requested resource was not found.'
    }
    if (status === 409) {
      return message || 'This action conflicts with existing data.'
    }
    if (status === 422) {
      return message || 'Validation error. Please check your input.'
    }
    if (status === 429) {
      return 'Too many requests. Please try again later.'
    }
    if (status && status >= 500) {
      return 'Server error. Please try again later.'
    }

    return message || error.message || 'An unexpected error occurred.'
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred.'
}

/**
 * Extracts detailed API error information
 */
export function parseApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const data = error.response?.data

    return {
      message: getErrorMessage(error),
      status,
      code: data?.code,
      field: data?.field,
    }
  }

  return {
    message: getErrorMessage(error),
  }
}

/**
 * Extracts field-specific validation errors from API response
 */
export function getFieldErrors(
  error: unknown
): Record<string, string> | null {
  if (!axios.isAxiosError(error)) {
    return null
  }

  const data = error.response?.data

  // Django REST Framework format
  if (data && typeof data === 'object') {
    const fieldErrors: Record<string, string> = {}

    for (const [field, messages] of Object.entries(data)) {
      if (Array.isArray(messages)) {
        fieldErrors[field] = messages[0]
      } else if (typeof messages === 'string') {
        fieldErrors[field] = messages
      }
    }

    if (Object.keys(fieldErrors).length > 0) {
      return fieldErrors
    }
  }

  return null
}

/**
 * Logs error to console in development, and to error tracking service in production
 */
export function logError(error: unknown, context?: string): void {
  const isDevelopment = import.meta.env.DEV

  if (isDevelopment) {
    console.error(`[${context || 'Error'}]:`, error)
  } else {
    // In production, send to error tracking service (Sentry, etc.)
    // TODO: Integrate with error tracking service
    console.error(`[${context || 'Error'}]:`, getErrorMessage(error))
  }
}

/**
 * Determines if an error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return !error.response && (error.code === 'ERR_NETWORK' || error.message.includes('Network'))
  }
  return false
}

/**
 * Determines if an error is an authentication error
 */
export function isAuthError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 401
  }
  return false
}

/**
 * Determines if an error is a validation error
 */
export function isValidationError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 400 || error.response?.status === 422
  }
  return false
}
