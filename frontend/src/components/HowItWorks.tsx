import { ClipboardList, Brain, CheckCircle, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Button from './ui/Button'

const steps = [
  {
    icon: ClipboardList,
    number: '01',
    title: 'Enter Applicant Data',
    description: 'Input key information about your tenant: income, credit score, rental history, and employment details.',
  },
  {
    icon: Brain,
    number: '02',
    title: 'AI Analyzes Risk',
    description: 'Our XGBoost model evaluates 21 risk factors using patterns learned from 50,000+ data points.',
  },
  {
    icon: CheckCircle,
    number: '03',
    title: 'Get Instant Decision',
    description: 'Receive a risk score, category, and clear recommendation (Approve, Review, or Reject) in under 2 seconds.',
  },
]

export default function HowItWorks() {
  const navigate = useNavigate()

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">
            How It Works
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Three simple steps to transform your tenant screening process
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          {steps.map((step, index) => (
            <div key={step.number} className="relative">
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-primary-200 to-transparent z-0" />
              )}

              <div className="relative bg-slate-50 rounded-2xl p-8 hover:bg-slate-100 transition-colors duration-300">
                {/* Step number */}
                <div className="absolute -top-4 left-8 bg-primary-500 text-white text-sm font-bold px-3 py-1 rounded-full">
                  {step.number}
                </div>

                {/* Icon */}
                <div className="w-16 h-16 rounded-xl bg-primary-100 flex items-center justify-center mb-6 mt-2">
                  <step.icon className="w-8 h-8 text-primary-500" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-semibold text-slate-900 mb-3">
                  {step.title}
                </h3>
                <p className="text-slate-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-12 text-white">
          <h3 className="text-2xl font-bold mb-4">
            Ready to streamline your tenant screening?
          </h3>
          <p className="text-lg text-slate-200 mb-8 max-w-xl mx-auto">
            Try our AI-powered risk assessment now. No signup required for the demo.
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/score')}
            className="bg-white text-primary-600 hover:bg-slate-100"
          >
            Start Free Assessment
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </div>
    </section>
  )
}
