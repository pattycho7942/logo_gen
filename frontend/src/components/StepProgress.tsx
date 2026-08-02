import type { LogoStep } from '../types'

function CircleIcon({ status, index }: { status: LogoStep['status']; index: number }) {
  if (status === 'done') {
    return (
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-indigo-500 text-white shadow-md shadow-violet-200">
        <svg viewBox="0 0 20 20" fill="none" className="h-5 w-5">
          <path
            d="M5 10.5l3 3 7-7"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    )
  }
  if (status === 'active') {
    return (
      <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-violet-500 bg-white text-violet-600">
        <span className="h-3 w-3 animate-ping rounded-full bg-violet-500" />
      </div>
    )
  }
  return (
    <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-gray-200 bg-white text-sm font-medium text-gray-400">
      {index + 1}
    </div>
  )
}

export default function StepProgress({ steps }: { steps: LogoStep[] }) {
  return (
    <div className="flex w-full items-start">
      {steps.map((step, i) => (
        <div key={step.id} className="flex flex-1 items-center last:flex-none">
          <div className="flex w-20 flex-col items-center gap-2 text-center sm:w-28">
            <CircleIcon status={step.status} index={i} />
            <span
              className={`text-[11px] leading-tight sm:text-xs ${
                step.status === 'pending' ? 'text-gray-400' : 'text-gray-800 font-medium'
              }`}
            >
              {step.label}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div
              className={`mx-1 mt-5 h-0.5 flex-1 rounded sm:mx-2 ${
                step.status === 'done' ? 'bg-violet-400' : 'bg-gray-200'
              }`}
            />
          )}
        </div>
      ))}
    </div>
  )
}
