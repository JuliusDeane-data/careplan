/**
 * ActivityItem Component
 * Displays a single activity in the activity feed
 */

import type { Activity, ActivityType } from '@/types/dashboard'
import { formatDistanceToNow } from 'date-fns'
import {
  CheckCircle2,
  XCircle,
  Calendar,
  UserPlus,
  Clock,
  AlertCircle,
} from 'lucide-react'

interface ActivityItemProps {
  activity: Activity
}

const ACTIVITY_CONFIG: Record<
  ActivityType,
  {
    icon: typeof CheckCircle2
    iconColor: string
    bgColor: string
  }
> = {
  vacation_requested: {
    icon: Clock,
    iconColor: 'text-yellow-600',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/20',
  },
  vacation_approved: {
    icon: CheckCircle2,
    iconColor: 'text-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/20',
  },
  vacation_denied: {
    icon: XCircle,
    iconColor: 'text-red-600',
    bgColor: 'bg-red-100 dark:bg-red-900/20',
  },
  vacation_cancelled: {
    icon: AlertCircle,
    iconColor: 'text-gray-600',
    bgColor: 'bg-gray-100 dark:bg-gray-900/20',
  },
  employee_created: {
    icon: UserPlus,
    iconColor: 'text-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/20',
  },
  employee_updated: {
    icon: UserPlus,
    iconColor: 'text-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/20',
  },
  employee_deleted: {
    icon: UserPlus,
    iconColor: 'text-red-600',
    bgColor: 'bg-red-100 dark:bg-red-900/20',
  },
  location_created: {
    icon: Calendar,
    iconColor: 'text-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/20',
  },
  location_updated: {
    icon: Calendar,
    iconColor: 'text-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/20',
  },
  system_notification: {
    icon: AlertCircle,
    iconColor: 'text-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/20',
  },
  user_login: {
    icon: UserPlus,
    iconColor: 'text-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/20',
  },
}

export default function ActivityItem({ activity }: ActivityItemProps) {
  const config = ACTIVITY_CONFIG[activity.type]
  const Icon = config.icon

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="flex items-start gap-4 py-3">
      {/* Activity Icon */}
      <div className={`rounded-full p-2 ${config.bgColor}`}>
        <Icon className={`w-4 h-4 ${config.iconColor}`} />
      </div>

      {/* Activity Content */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{activity.title}</p>
        <p className="text-sm text-muted-foreground">{activity.description}</p>

        {/* Actor and timestamp */}
        <div className="flex items-center gap-2 mt-1">
          {/* Actor avatar */}
          {activity.actor.avatar ? (
            <img
              src={activity.actor.avatar}
              alt={activity.actor.name}
              className="w-5 h-5 rounded-full"
            />
          ) : (
            <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
              {getInitials(activity.actor.name)}
            </div>
          )}
          <span className="text-xs text-muted-foreground">
            {activity.actor.name}
          </span>
          <span className="text-xs text-muted-foreground">•</span>
          <span className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(activity.timestamp), {
              addSuffix: true,
            })}
          </span>
        </div>
      </div>
    </div>
  )
}
