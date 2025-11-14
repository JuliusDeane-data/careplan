/**
 * Certification module configuration
 */

export const CERTIFICATION_CONFIG = {
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,

  // Search
  MIN_SEARCH_LENGTH: 2,
  SEARCH_DEBOUNCE_MS: 300,

  // Caching
  QUERY_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  QUERY_CACHE_TIME: 10 * 60 * 1000, // 10 minutes

  // Expiry warnings (in days)
  EXPIRY_WARNING_CRITICAL: 14,
  EXPIRY_WARNING_HIGH: 30,
  EXPIRY_WARNING_MEDIUM: 60,
  EXPIRY_WARNING_LOW: 90,

  // Default expiry lookup window
  DEFAULT_EXPIRY_LOOKUP_DAYS: 90,

  // Document upload
  MAX_DOCUMENT_SIZE_MB: 10,
  ALLOWED_DOCUMENT_TYPES: [
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png',
  ],

  // Validation
  MAX_NOTES_LENGTH: 1000,
  MAX_CODE_LENGTH: 20,
  MAX_NAME_LENGTH: 100,
} as const

// Helper to get expiry warning color
export function getExpiryWarningColor(
  warningLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | null
): string {
  switch (warningLevel) {
    case 'CRITICAL':
      return 'red'
    case 'HIGH':
      return 'orange'
    case 'MEDIUM':
      return 'yellow'
    case 'LOW':
      return 'blue'
    default:
      return 'gray'
  }
}

// Helper to get status color
export function getCertificationStatusColor(
  status: 'ACTIVE' | 'EXPIRING_SOON' | 'EXPIRED' | 'PENDING_VERIFICATION'
): string {
  switch (status) {
    case 'ACTIVE':
      return 'green'
    case 'EXPIRING_SOON':
      return 'yellow'
    case 'EXPIRED':
      return 'red'
    case 'PENDING_VERIFICATION':
      return 'gray'
    default:
      return 'gray'
  }
}

// Helper to get category display name
export function getCategoryDisplayName(
  category: 'MUST_HAVE' | 'SPECIALIZED' | 'OPTIONAL'
): string {
  switch (category) {
    case 'MUST_HAVE':
      return 'Must Have'
    case 'SPECIALIZED':
      return 'Specialized'
    case 'OPTIONAL':
      return 'Optional'
    default:
      return category
  }
}
