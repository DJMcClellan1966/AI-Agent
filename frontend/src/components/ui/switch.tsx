'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface SwitchProps {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
  label?: string;
  description?: string;
  className?: string;
}

const Switch = React.forwardRef<HTMLButtonElement, SwitchProps>(
  ({ checked = false, onCheckedChange, disabled, label, description, className }, ref) => {
    const id = React.useId();
    
    return (
      <div className={cn('flex items-center', className)}>
        <button
          ref={ref}
          role="switch"
          id={id}
          aria-checked={checked}
          disabled={disabled}
          onClick={() => onCheckedChange?.(!checked)}
          className={cn(
            'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            checked ? 'bg-indigo-600' : 'bg-gray-200'
          )}
        >
          <span
            className={cn(
              'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition-transform',
              checked ? 'translate-x-5' : 'translate-x-0'
            )}
          />
        </button>
        {(label || description) && (
          <div className="ml-3">
            {label && (
              <label htmlFor={id} className="text-sm font-medium text-gray-900 cursor-pointer">
                {label}
              </label>
            )}
            {description && <p className="text-sm text-gray-500">{description}</p>}
          </div>
        )}
      </div>
    );
  }
);
Switch.displayName = 'Switch';

export { Switch };
