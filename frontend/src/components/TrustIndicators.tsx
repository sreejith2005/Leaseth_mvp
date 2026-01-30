import { Target, Database, Zap, Cpu } from 'lucide-react'

const indicators = [
  {
    icon: Target,
    value: '87%',
    label: 'Model Accuracy',
    description: 'Precision in risk prediction',
  },
  {
    icon: Database,
    value: '50K+',
    label: 'Data Points Trained',
    description: 'Comprehensive dataset',
  },
  {
    icon: Zap,
    value: '<2s',
    label: 'Scoring Speed',
    description: 'Instant risk assessment',
  },
  {
    icon: Cpu,
    value: 'XGBoost',
    label: 'ML Engine',
    description: 'Industry-leading algorithm',
  },
]

export default function TrustIndicators() {
  return (
    <section className="py-16 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">
            Built for Accuracy & Speed
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Our platform combines cutting-edge machine learning with comprehensive data analysis
            to deliver reliable tenant risk assessments.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {indicators.map((indicator, index) => (
            <div
              key={indicator.label}
              className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300 animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="w-12 h-12 rounded-lg bg-primary-100 flex items-center justify-center mb-4">
                <indicator.icon className="w-6 h-6 text-primary-500" />
              </div>
              <div className="text-3xl font-bold text-primary-500 mb-1">
                {indicator.value}
              </div>
              <div className="font-semibold text-slate-900 mb-1">
                {indicator.label}
              </div>
              <p className="text-sm text-slate-500">
                {indicator.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
