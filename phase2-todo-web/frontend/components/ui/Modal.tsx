'use client'

import React, { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { Button } from './Button'

export interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  description?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
  closeOnOverlayClick?: boolean
  closeOnEscape?: boolean
  footer?: React.ReactNode
  className?: string
}

const sizeClasses = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-[95vw]',
}

export const Modal = React.forwardRef<HTMLDivElement, ModalProps>(
  (
    {
      open,
      onClose,
      title,
      description,
      children,
      size = 'md',
      showCloseButton = true,
      closeOnOverlayClick = true,
      closeOnEscape = true,
      footer,
      className,
    },
    ref
  ) => {
    const modalRef = useRef<HTMLDivElement>(null)
    const previousFocusRef = useRef<HTMLElement | null>(null)

    // Handle escape key
    useEffect(() => {
      if (!closeOnEscape) return

      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape' && open) {
          onClose()
        }
      }

      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }, [open, onClose, closeOnEscape])

    // Handle focus trap and restoration
    useEffect(() => {
      if (open) {
        previousFocusRef.current = document.activeElement as HTMLElement
        modalRef.current?.focus()

        // Prevent body scroll
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = 'unset'
        previousFocusRef.current?.focus()
      }

      return () => {
        document.body.style.overflow = 'unset'
      }
    }, [open])

    if (!open) return null

    const handleOverlayClick = (e: React.MouseEvent) => {
      if (closeOnOverlayClick && e.target === e.currentTarget) {
        onClose()
      }
    }

    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
        aria-describedby={description ? 'modal-description' : undefined}
      >
        {/* Backdrop with animation */}
        <div
          className={cn(
            'absolute inset-0 bg-slate-900/60 backdrop-blur-sm',
            'animate-in fade-in duration-200'
          )}
          onClick={handleOverlayClick}
          aria-hidden="true"
        />

        {/* Modal content */}
        <div
          ref={modalRef}
          className={cn(
            'relative w-full bg-white rounded-2xl shadow-2xl',
            'animate-in fade-in zoom-in-95 duration-300',
            'max-h-[90vh] overflow-hidden flex flex-col',
            sizeClasses[size],
            className
          )}
          tabIndex={-1}
        >
          {/* Header */}
          {(title || description || showCloseButton) && (
            <div className="flex items-start justify-between p-6 border-b border-slate-200">
              <div className="flex-1">
                {title && (
                  <h2
                    id="modal-title"
                    className="text-2xl font-semibold text-slate-900 leading-tight"
                  >
                    {title}
                  </h2>
                )}
                {description && (
                  <p
                    id="modal-description"
                    className="mt-2 text-sm text-slate-600"
                  >
                    {description}
                  </p>
                )}
              </div>

              {showCloseButton && (
                <button
                  onClick={onClose}
                  className={cn(
                    'ml-4 p-2 rounded-lg text-slate-400',
                    'hover:text-slate-600 hover:bg-slate-100',
                    'focus:outline-none focus:ring-2 focus:ring-blue-500',
                    'transition-all duration-200'
                  )}
                  aria-label="Close modal"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>
          )}

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-6">{children}</div>

          {/* Footer */}
          {footer && (
            <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-200 bg-slate-50">
              {footer}
            </div>
          )}
        </div>
      </div>
    )
  }
)

Modal.displayName = 'Modal'

// Confirmation Modal Helper
export interface ConfirmModalProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  confirmVariant?: 'primary' | 'danger' | 'success'
  loading?: boolean
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'primary',
  loading = false,
}) => {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      description={description}
      size="sm"
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={loading}>
            {cancelText}
          </Button>
          <Button
            variant={confirmVariant}
            onClick={onConfirm}
            loading={loading}
          >
            {confirmText}
          </Button>
        </>
      }
    >
      <div className="py-4">
        <p className="text-slate-600">{description}</p>
      </div>
    </Modal>
  )
}
