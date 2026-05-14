import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-95 hover:scale-105',
  {
    variants: {
      variant: {
        primary:
          'relative overflow-hidden bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] text-white shadow-lg hover:shadow-xl focus-visible:ring-[#6EB8E1] dark:focus-visible:ring-[#5A7FC8]',
        secondary:
          'bg-gradient-to-br from-[#D6E6F2] to-[#BAD0CC] dark:from-[#252E8A]/50 dark:to-[#5A7FC8]/30 text-[#5A7FC8] dark:text-[#6EB8E1] border-2 border-[#6EB8E1] dark:border-[#5A7FC8] shadow-md hover:shadow-lg focus-visible:ring-[#6EB8E1] dark:focus-visible:ring-[#5A7FC8]',
        success:
          'relative overflow-hidden bg-gradient-to-r from-[#4EB5A9] to-[#48ADB7] text-white shadow-lg hover:shadow-xl focus-visible:ring-[#4EB5A9] dark:focus-visible:ring-[#48ADB7]',
        danger:
          'bg-gradient-to-br from-red-600 to-red-700 text-white shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40 focus-visible:ring-red-500',
        ghost:
          'text-[#252E3F] dark:text-[#F7F6F7] hover:bg-[#D6E6F2] dark:hover:bg-[#252E8A]/30 focus-visible:ring-[#6EB8E1] dark:focus-visible:ring-[#5A7FC8]',
        outline:
          'border-2 border-[#6EB8E1] dark:border-[#5A7FC8] text-[#5A7FC8] dark:text-[#6EB8E1] hover:bg-[#6EB8E1] dark:hover:bg-[#5A7FC8] hover:text-white focus-visible:ring-[#6EB8E1] dark:focus-visible:ring-[#5A7FC8]',
      },
      size: {
        sm: 'h-9 px-4 text-sm',
        md: 'h-11 px-6 text-base',
        lg: 'h-14 px-8 text-lg',
        icon: 'h-11 w-11',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      loading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        aria-busy={loading}
        {...props}
      >
        {loading && (
          <svg
            className="animate-spin h-4 w-4"
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
        )}
        {!loading && leftIcon && <span aria-hidden="true">{leftIcon}</span>}
        {children}
        {!loading && rightIcon && <span aria-hidden="true">{rightIcon}</span>}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button, buttonVariants }
