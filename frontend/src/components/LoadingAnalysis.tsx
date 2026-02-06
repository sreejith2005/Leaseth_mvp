import { useState, useEffect } from 'react'
import { Building2, CreditCard, History, Calculator, Sparkles } from 'lucide-react'

const analysisSteps = [
  { icon: Building2, text: 'Evaluating rental income...', detail: 'Property & lease analysis' },
  { icon: CreditCard, text: 'Checking tenant financials...', detail: 'Credit & income verification' },
  { icon: History, text: 'Reviewing payment history...', detail: 'On-time payment patterns' },
  { icon: Calculator, text: 'Generating your offer...', detail: 'AI offer calculation' },
]

const funFacts = [
  "Did you know? Landlords with verified tenants get up to 20% better offer rates.",
  "Tip: Longer lease terms often mean higher offer amounts.",
  "Fun fact: 85% of our offers are accepted within 24 hours!",
  "Properties with on-time payment history above 90% get the best rates.",
]

export default function LoadingAnalysis() {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [funFact] = useState(() => funFacts[Math.floor(Math.random() * funFacts.length)])

  useEffect(() => {
    const duration = 2000 // Total animation time
    const stepDuration = duration / analysisSteps.length

    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 2, 100))
    }, duration / 50)

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => Math.min(prev + 1, analysisSteps.length - 1))
    }, stepDuration)

    return () => {
      clearInterval(progressInterval)
      clearInterval(stepInterval)
    }
  }, [])

  const CurrentIcon = analysisSteps[currentStep].icon

  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 max-w-md mx-auto">
      {/* Animated icon */}
      <div className="relative mb-10">
        <div className="w-28 h-28 rounded-2xl bg-[#7c9a82]/10 flex items-center justify-center">
          <CurrentIcon className="w-12 h-12 text-[#7c9a82]" />
        </div>
        {/* Pulsing rings */}
        <div className="absolute inset-0 rounded-2xl border-2 border-[#7c9a82]/20 animate-ping" style={{ animationDuration: '2s' }} />
        <div className="absolute inset-0 rounded-2xl border-2 border-[#7c9a82]/10 animate-ping" style={{ animationDuration: '2s', animationDelay: '0.5s' }} />

        {/* Sparkle decorations */}
        <Sparkles className="absolute -top-2 -right-2 w-5 h-5 text-[#c4704f] animate-pulse" />
        <Sparkles className="absolute -bottom-1 -left-1 w-4 h-4 text-[#d4c5b0] animate-pulse" style={{ animationDelay: '0.3s' }} />
      </div>

      {/* Current step */}
      <div className="text-center mb-8">
        <h2 className="text-xl font-medium mb-2" style={{ fontFamily: 'DM Serif Display, serif' }}>
          {analysisSteps[currentStep].text}
        </h2>
        <p className="text-sm text-neutral-500">{analysisSteps[currentStep].detail}</p>
      </div>

      {/* Progress bar */}
      <div className="w-full mb-6">
        <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-100 ease-out"
            style={{
              width: `${progress}%`,
              background: 'linear-gradient(90deg, #7c9a82 0%, #9ab5a0 100%)'
            }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-neutral-400">
          <span>Analyzing...</span>
          <span>{Math.round(progress)}%</span>
        </div>
      </div>

      {/* Step indicators */}
      <div className="flex gap-3 mb-10">
        {analysisSteps.map((step, index) => (
          <div
            key={index}
            className={`flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ${
              index < currentStep
                ? 'bg-[#7c9a82] text-white'
                : index === currentStep
                ? 'bg-[#7c9a82]/20 text-[#7c9a82] ring-2 ring-[#7c9a82]/30'
                : 'bg-neutral-100 text-neutral-400'
            }`}
          >
            <step.icon className="w-4 h-4" />
          </div>
        ))}
      </div>

      {/* Fun fact */}
      <div className="p-4 rounded-xl bg-white border border-neutral-100 text-center">
        <p className="text-sm text-neutral-600 italic">"{funFact}"</p>
      </div>
    </div>
  )
}
