import React from 'react'
import { cn } from '@/lib/utils'

export interface LoadingProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'spinner' | 'dots' | 'pulse' | 'bars'
  className?: string
  text?: string
  fullScreen?: boolean
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
}

const dotSizeClasses = {
  sm: 'w-2 h-2',
  md: 'w-3 h-3',
  lg: 'w-4 h-4',
  xl: 'w-5 h-5',
}

export const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  variant = 'spinner',
  className,
  text,
  fullScreen = false,
}) => {
  const renderLoader = () => {
    switch (variant) {
      case 'spinner':
        return (
          <svg
            className={cn(
              'animate-spin text-blue-600',
              sizeClasses[size],
              className
            )}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )

      case 'dots':
        return (
          <div className={cn('flex items-center gap-2', className)}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={cn(
                  'rounded-full bg-blue-600 animate-pulse',
                  dotSizeClasses[size]
                )}
                style={{
                  animationDelay: `${i * 150}ms`,
                  animationDuration: '1s',
                }}
                aria-hidden="true"
              />
            ))}
          </div>
        )

      case 'pulse':
        return (
          <div
            className={cn(
              'rounded-full bg-blue-600 animate-ping opacity-75',
              sizeClasses[size],
              className
            )}
            aria-hidden="true"
          />
        )

      case 'bars':
        return (
          <div className={cn('flex items-center gap-1', className)}>
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className={cn('w-1 bg-blue-600 rounded-full animate-pulse', {
                  'h-6': size === 'sm',
                  'h-8': size === 'md',
                  'h-12': size === 'lg',
                  'h-16': size === 'xl',
                })}
                style={{
                  animationDelay: `${i * 100}ms`,
                  animationDuration: '1.2s',
                }}
                aria-hidden="true"
              />
            ))}
          </div>
        )

      default:
        return null
    }
  }

  const content = (
    <div
      className={cn('flex flex-col items-center justify-center gap-3', {
        'fixed inset-0 z-50 bg-white/80 backdrop-blur-sm': fullScreen,
      })}
      role="status"
      aria-live="polite"
    >
      {renderLoader()}
      {text && (
        <p className="text-sm font-medium text-slate-600">{text}</p>
      )}
      <span className="sr-only">Loading...</span>
    </div>
  )

  return content
}

// Skeleton Component for content placeholders
export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  animation?: 'pulse' | 'wave' | 'none'
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  animation = 'pulse',
  className,
  ...props
}) => {
  return (
    <div
      className={cn(
        'bg-slate-200',
        {
          'rounded-lg': variant === 'rectangular',
          'rounded-full': variant === 'circular',
          'rounded h-4': variant === 'text',
          'animate-pulse': animation === 'pulse',
          'animate-wave': animation === 'wave',
        },
        className
      )}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
      aria-hidden="true"
      {...props}
    />
  )
}

// Loading Overlay for specific sections
export interface LoadingOverlayProps {
  loading: boolean
  children: React.ReactNode
  text?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'spinner' | 'dots' | 'pulse' | 'bars'
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  loading,
  children,
  text,
  size = 'md',
  variant = 'spinner',
}) => {
  return (
    <div className="relative">
      {children}
      {loading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-lg">
          <Loading size={size} variant={variant} text={text} />
        </div>
      )}
    </div>
  )
}

// Inline loader for buttons and small spaces
export const InlineLoader: React.FC<{ className?: string }> = ({
  className,
}) => {
  return (
    <svg
      className={cn('animate-spin h-4 w-4', className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )
}
