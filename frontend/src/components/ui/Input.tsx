import { clsx } from 'clsx'
import { InputHTMLAttributes, SelectHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  prefix?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, prefix, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-neutral-700 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {prefix && (
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none">
              {prefix}
            </span>
          )}
          <input
            ref={ref}
            id={inputId}
            className={clsx(
              'w-full px-4 py-3 border border-neutral-200 rounded-lg bg-white/80',
              'focus:outline-none focus:border-[#7c9a82] focus:ring-2 focus:ring-[#7c9a82]/10',
              'placeholder:text-neutral-400 text-neutral-900 transition-all duration-200',
              'hover:border-neutral-300',
              prefix && 'pl-8',
              error && 'border-red-400 focus:border-red-400 focus:ring-red-400/10',
              className
            )}
            {...props}
          />
        </div>
        {hint && !error && (
          <p className="text-xs text-neutral-400 mt-2">{hint}</p>
        )}
        {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
      </div>
    )
  }
)

Input.displayName = 'Input'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: { value: string; label: string }[]
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className, id, ...props }, ref) => {
    const selectId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={selectId} className="block text-sm font-medium text-neutral-700 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            className={clsx(
              'w-full px-4 py-3 border border-neutral-200 rounded-lg bg-white/80',
              'focus:outline-none focus:border-[#7c9a82] focus:ring-2 focus:ring-[#7c9a82]/10',
              'text-neutral-900 appearance-none cursor-pointer transition-all duration-200',
              'hover:border-neutral-300',
              error && 'border-red-400 focus:border-red-400 focus:ring-red-400/10',
              className
            )}
            {...props}
          >
            <option value="" className="text-neutral-400">Choose one...</option>
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg className="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
      </div>
    )
  }
)

Select.displayName = 'Select'

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string
  sublabel?: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, sublabel, className, id, ...props }, ref) => {
    const checkboxId = id || label.toLowerCase().replace(/\s+/g, '-')

    return (
      <label htmlFor={checkboxId} className="flex items-start gap-3 cursor-pointer group">
        <div className="pt-0.5">
          <input
            ref={ref}
            type="checkbox"
            id={checkboxId}
            className={clsx(
              'w-5 h-5 border-2 border-neutral-300 rounded bg-transparent',
              'checked:bg-[#7c9a82] checked:border-[#7c9a82]',
              'focus:ring-2 focus:ring-[#7c9a82]/20 focus:ring-offset-0',
              'transition-all duration-200 cursor-pointer',
              className
            )}
            {...props}
          />
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-neutral-700 group-hover:text-neutral-900 transition-colors">
            {label}
          </span>
          {sublabel && (
            <span className="text-xs text-neutral-500 mt-0.5">{sublabel}</span>
          )}
        </div>
      </label>
    )
  }
)

Checkbox.displayName = 'Checkbox'

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
  showValue?: boolean
  suffix?: string
}

export const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ label, showValue = true, suffix = '', className, value, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <div className="flex justify-between items-center mb-3">
            <label className="text-sm font-medium text-neutral-700">{label}</label>
            {showValue && (
              <span className="text-sm font-medium text-[#7c9a82]">
                {value}{suffix}
              </span>
            )}
          </div>
        )}
        <input
          ref={ref}
          type="range"
          value={value}
          className={clsx(
            'w-full h-2 bg-neutral-200 rounded-full appearance-none cursor-pointer',
            '[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5',
            '[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[#7c9a82]',
            '[&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:transition-transform',
            '[&::-webkit-slider-thumb]:hover:scale-110',
            '[&::-moz-range-thumb]:w-5 [&::-moz-range-thumb]:h-5',
            '[&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-[#7c9a82]',
            '[&::-moz-range-thumb]:border-0',
            className
          )}
          {...props}
        />
      </div>
    )
  }
)

Slider.displayName = 'Slider'

export default Input
