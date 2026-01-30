import { useNavigate } from 'react-router-dom'
import Button from './ui/Button'
import { Shield, Zap, Brain } from 'lucide-react'

export default function Hero() {
  const navigate = useNavigate()

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 text-white">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left content */}
          <div className="animate-fade-in">
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 mb-6">
              <Brain className="w-4 h-4" />
              <span className="text-sm font-medium">Powered by XGBoost ML</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6">
              AI-Powered Tenant Screening
              <span className="block text-emerald-400">in Seconds</span>
            </h1>

            <p className="text-xl text-slate-200 mb-8 max-w-lg">
              Make smarter rental decisions with our machine learning risk assessment.
              Reduce defaults, save time, and protect your investments.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                size="lg"
                onClick={() => navigate('/score')}
                className="bg-white text-primary-600 hover:bg-slate-100"
              >
                Try Demo Now
              </Button>
              <Button
                variant="ghost"
                size="lg"
                onClick={() => navigate('/dashboard')}
                className="text-white border-white/30 border hover:bg-white/10"
              >
                View Dashboard
              </Button>
            </div>

            {/* Quick stats */}
            <div className="flex flex-wrap gap-6 mt-10 pt-10 border-t border-white/20">
              <div>
                <div className="text-3xl font-bold">87%</div>
                <div className="text-sm text-slate-300">Model Accuracy</div>
              </div>
              <div>
                <div className="text-3xl font-bold">&lt;2s</div>
                <div className="text-sm text-slate-300">Response Time</div>
              </div>
              <div>
                <div className="text-3xl font-bold">50K+</div>
                <div className="text-sm text-slate-300">Data Points</div>
              </div>
            </div>
          </div>

          {/* Right illustration */}
          <div className="hidden lg:block animate-slide-up">
            <div className="relative">
              {/* Main card */}
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Shield className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <div className="font-semibold">Risk Assessment</div>
                    <div className="text-sm text-slate-300">Analyzing applicant...</div>
                  </div>
                </div>

                {/* Simulated score display */}
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">Risk Score</span>
                    <span className="text-2xl font-bold text-emerald-400">24</span>
                  </div>
                  <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full w-1/4 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full" />
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">Category</span>
                    <span className="text-emerald-400 font-semibold">LOW RISK</span>
                  </div>
                  <div className="pt-4 border-t border-white/10">
                    <div className="flex items-center gap-2 text-emerald-400">
                      <Zap className="w-4 h-4" />
                      <span className="text-sm font-medium">Recommendation: APPROVE</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating badge */}
              <div className="absolute -bottom-4 -right-4 bg-emerald-500 text-white rounded-lg px-4 py-2 shadow-lg">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  <span className="font-medium">Scored in 1.2s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Wave decoration */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
            fill="#f8fafc"
          />
        </svg>
      </div>
    </section>
  )
}
