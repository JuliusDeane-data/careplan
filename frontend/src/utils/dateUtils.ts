/**
 * Date utilities for vacation system
 * Uses date-fns for reliable date handling
 */

import {
  differenceInCalendarDays,
  parseISO,
  format as formatDate,
  isAfter,
  isBefore,
  isValid,
  addDays,
  startOfDay,
} from 'date-fns'

/**
 * Calculates the number of days between two dates (inclusive)
 * @param startDate - Start date (ISO string or Date)
 * @param endDate - End date (ISO string or Date)
 * @returns Number of calendar days (inclusive of both start and end)
 */
export function calculateVacationDays(
  startDate: string | Date,
  endDate: string | Date
): number {
  try {
    const start = typeof startDate === 'string' ? parseISO(startDate) : startDate
    const end = typeof endDate === 'string' ? parseISO(endDate) : endDate

    if (!isValid(start) || !isValid(end)) {
      return 0
    }

    // +1 because both start and end dates are inclusive
    return differenceInCalendarDays(end, start) + 1
  } catch {
    return 0
  }
}

/**
 * Calculates days until a future date from today
 * @param date - Future date (ISO string or Date)
 * @returns Number of days until date (0 if date is in past)
 */
export function calculateDaysUntil(date: string | Date): number {
  try {
    const targetDate = typeof date === 'string' ? parseISO(date) : date
    const today = startOfDay(new Date())

    if (!isValid(targetDate)) {
      return 0
    }

    const days = differenceInCalendarDays(targetDate, today)
    return Math.max(0, days)
  } catch {
    return 0
  }
}

/**
 * Validates that a date range is valid (end >= start)
 * @param startDate - Start date (ISO string or Date)
 * @param endDate - End date (ISO string or Date)
 * @returns true if range is valid
 */
export function isValidDateRange(
  startDate: string | Date,
  endDate: string | Date
): boolean {
  try {
    const start = typeof startDate === 'string' ? parseISO(startDate) : startDate
    const end = typeof endDate === 'string' ? parseISO(endDate) : endDate

    if (!isValid(start) || !isValid(end)) {
      return false
    }

    return !isBefore(end, start)
  } catch {
    return false
  }
}

/**
 * Checks if a date is in the past
 * @param date - Date to check (ISO string or Date)
 * @returns true if date is before today
 */
export function isInPast(date: string | Date): boolean {
  try {
    const targetDate = typeof date === 'string' ? parseISO(date) : date
    const today = startOfDay(new Date())

    if (!isValid(targetDate)) {
      return false
    }

    return isBefore(targetDate, today)
  } catch {
    return false
  }
}

/**
 * Checks if a date is in the future
 * @param date - Date to check (ISO string or Date)
 * @returns true if date is after today
 */
export function isInFuture(date: string | Date): boolean {
  try {
    const targetDate = typeof date === 'string' ? parseISO(date) : date
    const today = startOfDay(new Date())

    if (!isValid(targetDate)) {
      return false
    }

    return isAfter(targetDate, today)
  } catch {
    return false
  }
}

/**
 * Formats a date to a readable string
 * @param date - Date to format (ISO string or Date)
 * @param formatStr - Format string (default: 'MMM d, yyyy')
 * @returns Formatted date string
 */
export function formatVacationDate(
  date: string | Date,
  formatStr: string = 'MMM d, yyyy'
): string {
  try {
    const targetDate = typeof date === 'string' ? parseISO(date) : date

    if (!isValid(targetDate)) {
      return typeof date === 'string' ? date : 'Invalid Date'
    }

    return formatDate(targetDate, formatStr)
  } catch {
    return typeof date === 'string' ? date : 'Invalid Date'
  }
}

/**
 * Gets the minimum start date based on advance notice requirement
 * @param advanceDays - Number of days advance notice required
 * @returns Minimum allowed start date
 */
export function getMinStartDate(advanceDays: number): Date {
  return addDays(startOfDay(new Date()), advanceDays)
}

/**
 * Formats a date range to a readable string
 * @param startDate - Start date (ISO string or Date)
 * @param endDate - End date (ISO string or Date)
 * @returns Formatted date range (e.g., "Dec 20, 2025 - Dec 27, 2025")
 */
export function formatDateRange(
  startDate: string | Date,
  endDate: string | Date
): string {
  const start = formatVacationDate(startDate)
  const end = formatVacationDate(endDate)
  return `${start} - ${end}`
}

/**
 * Converts a date to ISO string format for API submission
 * @param date - Date to convert
 * @returns ISO date string (YYYY-MM-DD)
 */
export function toISODateString(date: Date): string {
  try {
    if (!isValid(date)) {
      throw new Error('Invalid date')
    }
    return formatDate(date, 'yyyy-MM-dd')
  } catch {
    return ''
  }
}
