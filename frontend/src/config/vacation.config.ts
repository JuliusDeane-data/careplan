/**
 * Vacation module configuration
 * Centralizes all vacation-related constants and settings
 */

export const VACATION_CONFIG = {
  /** Minimum days in advance a vacation must be requested */
  MIN_ADVANCE_DAYS: Number(import.meta.env.VITE_MIN_VACATION_ADVANCE_DAYS) || 14,

  /** Maximum days per single vacation request */
  MAX_DAYS_PER_REQUEST: Number(import.meta.env.VITE_MAX_VACATION_DAYS) || 30,

  /** Maximum length for reason field */
  MAX_REASON_LENGTH: 500,

  /** Items per page for vacation list */
  ITEMS_PER_PAGE: 20,

  /** Stale time for vacation data (ms) */
  QUERY_STALE_TIME: 60 * 1000, // 1 minute

  /** Cache time for vacation data (ms) */
  QUERY_CACHE_TIME: 5 * 60 * 1000, // 5 minutes
} as const

export const VALIDATION_MESSAGES = {
  START_DATE_REQUIRED: 'Start date is required',
  END_DATE_REQUIRED: 'End date is required',
  END_BEFORE_START: 'End date must be on or after start date',
  MIN_ADVANCE_NOTICE: `Vacation must be requested at least ${VACATION_CONFIG.MIN_ADVANCE_DAYS} days in advance`,
  INSUFFICIENT_BALANCE: 'Insufficient vacation days',
  REASON_TOO_LONG: `Reason must be less than ${VACATION_CONFIG.MAX_REASON_LENGTH} characters`,
} as const
