/**
 * Error Boundary component to catch React errors and prevent full app crashes
 */

import { Component, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle } from 'lucide-react'
import { logError } from '@/utils/errorHandler'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error to console/service
    logError(error, 'ErrorBoundary')
    console.error('Error Info:', errorInfo)

    // Update state
    this.setState({
      errorInfo,
    })

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo)
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  handleReload = (): void => {
    window.location.reload()
  }

  render(): ReactNode {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-6">
          <Card className="max-w-2xl w-full">
            <CardHeader>
              <div className="flex items-center gap-3">
                <AlertCircle className="h-8 w-8 text-red-600" />
                <div>
                  <CardTitle className="text-2xl">Something went wrong</CardTitle>
                  <CardDescription>
                    An unexpected error occurred. Our team has been notified.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Error details (only in development) */}
              {import.meta.env.DEV && this.state.error && (
                <div className="rounded-lg bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800">
                  <p className="text-sm font-medium text-red-900 dark:text-red-200 mb-2">
                    Error Details (Development Only):
                  </p>
                  <p className="text-xs text-red-700 dark:text-red-300 font-mono break-all">
                    {this.state.error.toString()}
                  </p>
                  {this.state.errorInfo && (
                    <details className="mt-2">
                      <summary className="text-xs text-red-600 dark:text-red-400 cursor-pointer">
                        Stack Trace
                      </summary>
                      <pre className="text-xs text-red-600 dark:text-red-400 mt-2 overflow-auto max-h-48">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              {/* User guidance */}
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  You can try the following:
                </p>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  <li>Click "Try Again" to attempt recovery</li>
                  <li>Reload the page to start fresh</li>
                  <li>Contact support if the problem persists</li>
                </ul>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button onClick={this.handleReset} variant="default">
                  Try Again
                </Button>
                <Button onClick={this.handleReload} variant="outline">
                  Reload Page
                </Button>
                <Button onClick={() => window.location.href = '/dashboard'} variant="outline">
                  Go to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Smaller error fallback for individual components
 */
export function ErrorFallback({ error, reset }: { error: Error; reset?: () => void }) {
  return (
    <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-4">
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1 space-y-2">
          <p className="text-sm font-medium text-red-900 dark:text-red-200">
            Failed to load this section
          </p>
          <p className="text-xs text-red-700 dark:text-red-300">
            {error.message}
          </p>
          {reset && (
            <Button size="sm" variant="outline" onClick={reset} className="mt-2">
              Try Again
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
