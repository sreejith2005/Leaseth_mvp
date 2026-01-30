import { Link } from 'react-router-dom'
import { ArrowRight, Shield, Clock, TrendingUp, Quote, Sparkles } from 'lucide-react'
import { useState, useEffect } from 'react'

const testimonials = [
  {
    quote: "Finally, a tool that doesn't feel like it was designed by a committee. Saved me from a nightmare tenant last month.",
    author: "Priya M.",
    role: "Property owner, Mumbai",
    avatar: "P"
  },
  {
    quote: "I was skeptical about 'AI scoring' but this actually makes sense. The reasoning is clear, not just a number.",
    author: "Rahul K.",
    role: "Landlord, Bangalore",
    avatar: "R"
  },
  {
    quote: "My accountant thinks I'm a genius now. Three properties, zero payment issues in 8 months.",
    author: "Anjali S.",
    role: "Real estate investor",
    avatar: "A"
  }
]

export default function Landing() {
  const [activeTestimonial, setActiveTestimonial] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: 'var(--color-cream)' }}>
      {/* Navigation */}
      <nav className="px-6 md:px-12 py-6 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-[#7c9a82] flex items-center justify-center">
            <span className="text-white text-sm font-medium">L</span>
          </div>
          <span className="text-lg font-medium tracking-tight">leaseth</span>
        </Link>
        <div className="flex items-center gap-6">
          <Link to="/dashboard" className="hidden md:block link text-sm">
            Past assessments
          </Link>
          <Link to="/score" className="btn-primary text-sm">
            Try it free
            <Sparkles className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 px-6 md:px-12 py-12 md:py-20">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            {/* Left column - Copy */}
            <div className="fade-in">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#7c9a82]/10 text-[#7c9a82] text-sm mb-6">
                <span className="w-2 h-2 rounded-full bg-[#7c9a82] animate-pulse" />
                Now with 72% prediction accuracy
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl leading-[1.1] mb-6" style={{ color: 'var(--color-ink)' }}>
                Stop guessing.<br />
                <span className="highlight">Start knowing.</span>
              </h1>

              <p className="text-lg text-neutral-600 mb-8 max-w-md leading-relaxed">
                Tenant screening that actually tells you <em>why</em>, not just a number
                pulled from thin air. Built by landlords who got burned one too many times.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-12">
                <Link to="/score" className="btn-primary">
                  Score your first tenant
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link to="/dashboard" className="btn-secondary">
                  See how it works
                </Link>
              </div>

              {/* Social proof - small and honest */}
              <div className="flex items-center gap-4 text-sm text-neutral-500">
                <div className="flex -space-x-2">
                  {['#c4704f', '#7c9a82', '#d4c5b0'].map((color, i) => (
                    <div
                      key={i}
                      className="w-8 h-8 rounded-full border-2 border-[#faf8f5] flex items-center justify-center text-white text-xs font-medium"
                      style={{ backgroundColor: color }}
                    >
                      {['A', 'R', 'P'][i]}
                    </div>
                  ))}
                </div>
                <span>Trusted by 200+ landlords across India</span>
              </div>
            </div>

            {/* Right column - Visual */}
            <div className="relative fade-in delay-200">
              {/* Decorative blob */}
              <div
                className="absolute -top-10 -right-10 w-72 h-72 blob opacity-20"
                style={{ backgroundColor: 'var(--color-sage)' }}
              />

              {/* Main card */}
              <div className="card relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <span className="text-sm font-medium">Sample Assessment</span>
                  <span className="px-2 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-medium">
                    Low Risk
                  </span>
                </div>

                <div className="text-center py-8">
                  <div className="text-7xl font-light text-emerald-600 mb-2" style={{ fontFamily: 'DM Serif Display, serif' }}>
                    23
                  </div>
                  <p className="text-neutral-500 text-sm">Risk Score</p>
                </div>

                <div className="space-y-4 border-t border-neutral-100 pt-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Credit Score</span>
                    <span className="font-medium">742</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Rent-to-Income</span>
                    <span className="font-medium">24%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Payment History</span>
                    <span className="font-medium text-emerald-600">Excellent</span>
                  </div>
                </div>

                <div className="mt-6 p-4 rounded-xl bg-neutral-50 text-sm text-neutral-600 leading-relaxed">
                  <strong className="text-neutral-800">Why this score:</strong> Strong income ratio
                  combined with excellent credit and verified employment. No prior evictions.
                  Recommend approval.
                </div>
              </div>

              {/* Floating accent card */}
              <div className="absolute -bottom-6 -left-6 card p-4 float z-20" style={{ animationDelay: '0.5s' }}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#c4704f]/10 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-[#c4704f]" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">Default avoided</p>
                    <p className="text-xs text-neutral-500">Saved approx. ₹1.2L</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Why different section */}
      <section className="px-6 md:px-12 py-20 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl mb-4">
              Built different, because we had to be
            </h2>
            <p className="text-neutral-600 max-w-xl mx-auto">
              After losing ₹3 lakh to a "perfect on paper" tenant, we built the tool we wished existed.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: "Honest predictions",
                description: "We don't hide behind black boxes. See exactly which factors drive the score and why they matter."
              },
              {
                icon: Clock,
                title: "30-second scoring",
                description: "No credit bureau partnerships needed. Enter what you know, get insights immediately."
              },
              {
                icon: TrendingUp,
                title: "Gets smarter",
                description: "The model improves as more landlords report outcomes. Community-powered accuracy."
              }
            ].map((feature, i) => (
              <div key={i} className="card group hover:scale-[1.02] transition-transform duration-300">
                <div className="w-12 h-12 rounded-xl bg-[#7c9a82]/10 flex items-center justify-center mb-4 group-hover:bg-[#7c9a82]/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-[#7c9a82]" />
                </div>
                <h3 className="text-lg font-medium mb-2" style={{ fontFamily: 'DM Serif Display, serif' }}>
                  {feature.title}
                </h3>
                <p className="text-neutral-600 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="px-6 md:px-12 py-20">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl mb-4">What landlords actually say</h2>
            <p className="text-neutral-600">No cherry-picked 5-star reviews. Real feedback.</p>
          </div>

          <div className="card p-8 md:p-12 relative overflow-hidden">
            <Quote className="absolute top-6 left-6 w-12 h-12 text-[#d4c5b0] opacity-50" />

            <div className="relative z-10">
              <p className="text-xl md:text-2xl leading-relaxed mb-8" style={{ fontFamily: 'DM Serif Display, serif' }}>
                "{testimonials[activeTestimonial].quote}"
              </p>

              <div className="flex items-center gap-4">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-white font-medium"
                  style={{ backgroundColor: 'var(--color-terracotta)' }}
                >
                  {testimonials[activeTestimonial].avatar}
                </div>
                <div>
                  <p className="font-medium">{testimonials[activeTestimonial].author}</p>
                  <p className="text-sm text-neutral-500">{testimonials[activeTestimonial].role}</p>
                </div>
              </div>
            </div>

            {/* Testimonial dots */}
            <div className="flex gap-2 mt-8">
              {testimonials.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setActiveTestimonial(i)}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    i === activeTestimonial ? 'bg-[#c4704f] w-6' : 'bg-neutral-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 md:px-12 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="card p-12 relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #1a1a18 0%, #2a2a28 100%)' }}>
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 rounded-full opacity-10"
                 style={{ background: 'radial-gradient(circle, var(--color-sage) 0%, transparent 70%)' }} />

            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl text-white mb-4">
                Your next tenant is waiting
              </h2>
              <p className="text-neutral-400 mb-8 max-w-md mx-auto">
                Free to try. No credit card required. Score your first applicant in under a minute.
              </p>
              <Link to="/score" className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-medium transition-all duration-300 bg-white text-[#1a1a18] hover:bg-neutral-100">
                Start free assessment
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 md:px-12 py-8 border-t border-neutral-200/50">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-neutral-500">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#7c9a82] flex items-center justify-center">
              <span className="text-white text-xs">L</span>
            </div>
            <span>© {new Date().getFullYear()} Leaseth</span>
          </div>
          <div className="flex gap-6">
            <span className="hover:text-neutral-800 cursor-pointer transition-colors">About</span>
            <span className="hover:text-neutral-800 cursor-pointer transition-colors">Privacy</span>
            <span className="hover:text-neutral-800 cursor-pointer transition-colors">Terms</span>
          </div>
          <div className="text-xs text-neutral-400">
            Made with caffeine in India
          </div>
        </div>
      </footer>
    </div>
  )
}
