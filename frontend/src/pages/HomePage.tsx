/**
 * Public HomePage - Landing page for all visitors
 * Shows general information without sensitive data
 * Includes login in header
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Heart,
  Users,
  Calendar,
  Award,
  MapPin,
  Clock,
  Shield,
  ChevronRight,
  Loader2,
} from 'lucide-react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/utils/errorHandler'

export default function HomePage() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  const [showLogin, setShowLogin] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  })

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate('/dashboard')
    return null
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await login(credentials)
      toast.success('Login successful!')
      navigate('/dashboard')
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Header with Login */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Heart className="w-8 h-8 text-blue-600" fill="currentColor" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                CarePlan
              </h1>
            </div>

            {!showLogin ? (
              <Button onClick={() => setShowLogin(true)} size="lg">
                Employee Login
              </Button>
            ) : (
              <div className="flex items-center gap-4">
                <form onSubmit={handleLogin} className="flex items-center gap-3">
                  <Input
                    type="email"
                    placeholder="Email"
                    autoComplete="email"
                    value={credentials.email}
                    onChange={(e) =>
                      setCredentials({ ...credentials, email: e.target.value })
                    }
                    className="w-48"
                    required
                  />
                  <Input
                    type="password"
                    placeholder="Password"
                    autoComplete="current-password"
                    value={credentials.password}
                    onChange={(e) =>
                      setCredentials({ ...credentials, password: e.target.value })
                    }
                    className="w-48"
                    required
                  />
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      'Login'
                    )}
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setShowLogin(false)}
                  >
                    Cancel
                  </Button>
                </form>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Professional Care Management
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            Streamlining operations for care facilities across Germany with
            comprehensive employee management, vacation planning, and shift
            scheduling solutions.
          </p>
          <div className="flex justify-center gap-4">
            <Button size="lg" onClick={() => setShowLogin(true)}>
              Get Started
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
            <Button size="lg" variant="outline" asChild>
              <a href="#features">Learn More</a>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h3 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
          Comprehensive Care Management Features
        </h3>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {/* Employee Management */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Users className="w-12 h-12 text-blue-600 mb-4" />
              <CardTitle>Employee Management</CardTitle>
              <CardDescription>
                Comprehensive employee directory with profiles, qualifications, and
                contact information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>• Complete employee profiles</li>
                <li>• Certification tracking</li>
                <li>• Multi-location support</li>
                <li>• Role-based access control</li>
              </ul>
            </CardContent>
          </Card>

          {/* Vacation Planning */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Calendar className="w-12 h-12 text-green-600 mb-4" />
              <CardTitle>Vacation Planning</CardTitle>
              <CardDescription>
                Streamlined vacation request and approval workflow with balance
                tracking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>• Easy request submission</li>
                <li>• Manager approval workflow</li>
                <li>• Automatic balance calculation</li>
                <li>• Public holiday integration</li>
              </ul>
            </CardContent>
          </Card>

          {/* Shift Scheduling */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Clock className="w-12 h-12 text-purple-600 mb-4" />
              <CardTitle>Shift Management</CardTitle>
              <CardDescription>
                Intelligent shift scheduling with coverage optimization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>• Automated scheduling</li>
                <li>• Coverage analytics</li>
                <li>• Shift swap requests</li>
                <li>• Real-time updates</li>
              </ul>
            </CardContent>
          </Card>

          {/* Compliance */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Shield className="w-12 h-12 text-red-600 mb-4" />
              <CardTitle>Compliance & Security</CardTitle>
              <CardDescription>
                GDPR compliant with robust security measures
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>• GDPR compliance</li>
                <li>• Secure authentication</li>
                <li>• Audit logging</li>
                <li>• Data encryption</li>
              </ul>
            </CardContent>
          </Card>

          {/* Qualifications */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Award className="w-12 h-12 text-yellow-600 mb-4" />
              <CardTitle>Qualifications Tracking</CardTitle>
              <CardDescription>
                Monitor certifications and training requirements
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>• Certification management</li>
                <li>• Expiry notifications</li>
                <li>• Training records</li>
                <li>• Compliance reports</li>
              </ul>
            </CardContent>
          </Card>

          {/* Multi-Location */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <MapPin className="w-12 h-12 text-indigo-600 mb-4" />
              <CardTitle>Multi-Location Support</CardTitle>
              <CardDescription>
                Manage multiple care facilities from one platform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>• Centralized management</li>
                <li>• Location-specific data</li>
                <li>• Cross-location reporting</li>
                <li>• Flexible assignment</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-blue-600 dark:bg-blue-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-4 text-center text-white">
            <div>
              <div className="text-4xl font-bold mb-2">4+</div>
              <div className="text-blue-100">Care Facilities</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">200+</div>
              <div className="text-blue-100">Employees</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">99.9%</div>
              <div className="text-blue-100">Uptime</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-blue-100">Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <Card className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl text-white">
              Ready to Get Started?
            </CardTitle>
            <CardDescription className="text-blue-100 text-lg">
              Join our platform and experience efficient care management
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button
              size="lg"
              variant="secondary"
              onClick={() => setShowLogin(true)}
            >
              Employee Login
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-3">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Heart className="w-6 h-6 text-blue-500" fill="currentColor" />
                <span className="text-white font-bold text-lg">CarePlan</span>
              </div>
              <p className="text-sm">
                Professional care management solutions for modern healthcare
                facilities across Germany.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="#features" className="hover:text-white transition">
                    Features
                  </a>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => setShowLogin(true)}
                    className="hover:text-white transition bg-transparent border-none p-0 m-0 cursor-pointer"
                  >
                    Employee Login
                  </button>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-sm">
                <li>Email: info@careplan.de</li>
                <li>Phone: +49 (0) 30 1234567</li>
                <li>Support: 24/7 Available</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; 2025 CarePlan. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
