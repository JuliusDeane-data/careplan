/**
 * Employee module configuration
 */

export const EMPLOYEE_CONFIG = {
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,

  // Search
  MIN_SEARCH_LENGTH: 2,
  SEARCH_DEBOUNCE_MS: 300,

  // Filters
  MAX_LOCATION_FILTERS: 10,

  // Caching
  QUERY_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  QUERY_CACHE_TIME: 10 * 60 * 1000, // 10 minutes

  // Images
  AVATAR_THUMBNAIL_SIZE: 100,
  AVATAR_FULL_SIZE: 400,

  // Validation
  MAX_NAME_LENGTH: 100,
  MAX_EMAIL_LENGTH: 255,
  MIN_PHONE_LENGTH: 10,
} as const
