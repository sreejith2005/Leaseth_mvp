import { Link } from 'react-router-dom'
import { ArrowRight, Shield, Clock, TrendingUp, Quote, Sparkles, DollarSign, Building2, Zap } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useCurrency } from '../contexts/CurrencyContext'
import CurrencySelector from '../components/CurrencySelector'

const testimonials = [
  {
    quote: "Got 12 months of rent upfront in 48 hours. No paperwork nightmare, no loan. Just clean cash.",
    author: "James W.",
    role: "Property owner, London",
    avatar: "J"
  },
  {
    quote: "I needed capital for a new investment but didn't want more loan installments. Leaseth bought my rental income — brilliant concept.",
    author: "Carlos M.",
    role: "Landlord, Dubai",
    avatar: "C"
  },
  {
    quote: "Three properties, three offers accepted. Best way to unlock liquidity without selling or borrowing.",
    author: "Sophie L.",
    role: "Real estate investor, Berlin",
    avatar: "S"
  }
]

export default function Landing() {
  const [activeTestimonial, setActiveTestimonial] = useState(0)
  const { formatCurrency, symbol } = useCurrency()

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
          <CurrencySelector />
          <Link to="/dashboard" className="hidden md:block link text-sm">
            My offers
          </Link>
          <Link to="/score" className="btn-primary text-sm">
            Get a cash offer
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
                AI-powered rental income valuation
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl leading-[1.1] mb-6" style={{ color: 'var(--color-ink)' }}>
                Get cash now.<br />
                <span className="highlight">Keep your property.</span>
              </h1>

              <p className="text-lg text-neutral-600 mb-8 max-w-md leading-relaxed">
                Sell your future rental income for upfront cash. No debt, no loan installments,
                no selling your property. Just <em>instant liquidity</em> from your rental stream.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-12">
                <Link to="/score" className="btn-primary">
                  Get your cash offer
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link to="/dashboard" className="btn-secondary">
                  See how it works
                </Link>
              </div>

              {/* Social proof */}
              <div className="flex items-center gap-4 text-sm text-neutral-500">
                <div className="flex -space-x-2">
                  {['#c4704f', '#7c9a82', '#d4c5b0'].map((color, i) => (
                    <div
                      key={i}
                      className="w-8 h-8 rounded-full border-2 border-[#faf8f5] flex items-center justify-center text-white text-xs font-medium"
                      style={{ backgroundColor: color }}
                    >
                      {['J', 'C', 'S'][i]}
                    </div>
                  ))}
                </div>
                <span>1,200+ rental income streams purchased globally</span>
              </div>
            </div>

            {/* Right column - Sample Offer Card */}
            <div className="relative fade-in delay-200">
              {/* Decorative blob */}
              <div
                className="absolute -top-10 -right-10 w-72 h-72 blob opacity-20"
                style={{ backgroundColor: 'var(--color-sage)' }}
              />

              {/* Main card */}
              <div className="card relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <span className="text-sm font-medium">Sample Offer</span>
                  <span className="px-2 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-medium">
                    Offer Available
                  </span>
                </div>

                <div className="text-center py-6">
                  <p className="text-neutral-500 text-sm mb-1">Your cash offer</p>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-6xl font-light text-emerald-600" style={{ fontFamily: 'DM Serif Display, serif' }}>
                      {formatCurrency(252000)}
                    </span>
                  </div>
                  <p className="text-neutral-400 text-sm mt-2">for 12 months of rental income</p>
                </div>

                <div className="space-y-4 border-t border-neutral-100 pt-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Monthly Rent</span>
                    <span className="font-medium">{formatCurrency(25000)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Total Rental Value</span>
                    <span className="font-medium">{formatCurrency(300000)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Reliability Score</span>
                    <span className="font-medium text-emerald-600">82/100</span>
                  </div>
                </div>

                <div className="mt-6 p-4 rounded-xl bg-neutral-50 text-sm text-neutral-600 leading-relaxed">
                  <strong className="text-neutral-800">How it works:</strong> You get {formatCurrency(252000)} upfront.
                  We collect the {formatCurrency(25000)}/month rent for 12 months. You keep your property. Zero debt created.
                </div>
              </div>

              {/* Floating accent card */}
              <div className="absolute -bottom-6 -left-6 card p-4 float z-20" style={{ animationDelay: '0.5s' }}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">Cash in 48 hours</p>
                    <p className="text-xs text-neutral-500">No loan. No debt.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* How It Works section */}
      <section className="px-6 md:px-12 py-20 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl mb-4">
              Three steps to cash in your pocket
            </h2>
            <p className="text-neutral-600 max-w-xl mx-auto">
              No banks, no paperwork nightmare, no waiting months. Get liquidity from what you already own.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Building2,
                title: "Submit your property",
                description: "Tell us about your rental property and existing tenant. Monthly rent, lease term, payment history — takes 2 minutes."
              },
              {
                icon: Zap,
                title: "Get an instant offer",
                description: "Our AI evaluates the rental income reliability and generates a cash offer in seconds. No obligation."
              },
              {
                icon: DollarSign,
                title: "Receive your cash",
                description: "Accept the offer and get cash in your account within 48 hours. Keep your property. No debt created."
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

      {/* Why Leaseth section */}
      <section className="px-6 md:px-12 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl mb-4">
              Why property owners choose Leaseth
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: "Keep your property",
                description: "This isn't a loan and you're not selling your property. You're simply selling future rent payments for cash now."
              },
              {
                icon: Clock,
                title: "Cash in 48 hours",
                description: "No bank approvals, no lengthy paperwork. Submit your property, accept the offer, get paid."
              },
              {
                icon: TrendingUp,
                title: "Fair, transparent pricing",
                description: "Our AI evaluates your rental income stream honestly. Better tenant reliability = better rates for you."
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
      <section className="px-6 md:px-12 py-20 bg-white/50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl mb-4">What property owners say</h2>
            <p className="text-neutral-600">Real feedback from landlords who've used Leaseth.</p>
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
                Your rental income is worth cash today
              </h2>
              <p className="text-neutral-400 mb-8 max-w-md mx-auto">
                Free to check. No obligation. See your offer in under a minute.
              </p>
              <Link to="/score" className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-medium transition-all duration-300 bg-white text-[#1a1a18] hover:bg-neutral-100">
                Get your cash offer
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
            Empowering landlords worldwide
          </div>
        </div>
      </footer>
    </div>
  )
}
