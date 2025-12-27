import Link from 'next/link'
import { ArrowRight, BarChart3, Target, Brain, TrendingUp } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-indigo-500" />
              <span className="text-xl font-bold text-white">Alpha Intelligence</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-gray-300 hover:text-white transition">
                Login
              </Link>
              <Link href="/signup" className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition">
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Your AI-Powered
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-purple-500">
              Financial Intelligence Terminal
            </span>
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Build investment theses. Track financial goals. Make smarter decisions with AI-powered insights for both US and Indian markets.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/signup" className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg font-semibold flex items-center space-x-2 transition">
              <span>Get Started Free</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link href="#features" className="border border-slate-700 hover:border-slate-600 text-white px-8 py-4 rounded-lg font-semibold transition">
              Learn More
            </Link>
          </div>
        </div>

        {/* Dashboard Preview */}
        <div className="mt-16 rounded-xl border border-slate-800 bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="aspect-video bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg flex items-center justify-center">
            <p className="text-gray-500 text-lg">Dashboard Preview Coming Soon</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Everything You Need to Invest Smarter
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Brain className="h-8 w-8 text-indigo-500" />}
            title="AI-Powered Analysis"
            description="Deep market intelligence with 60-day narrative tracking and AI commentary for every stock."
          />
          <FeatureCard
            icon={<Target className="h-8 w-8 text-purple-500" />}
            title="Goal Tracking"
            description="Set financial goals, track progress, and get AI recommendations to stay on target."
          />
          <FeatureCard
            icon={<TrendingUp className="h-8 w-8 text-green-500" />}
            title="Thesis Builder"
            description="Build and track investment theses with AI-powered insights and performance analytics."
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Investing?
          </h2>
          <p className="text-indigo-100 mb-8 text-lg">
            Join thousands of investors making smarter decisions with Alpha Intelligence.
          </p>
          <Link href="/signup" className="bg-white text-indigo-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold inline-flex items-center space-x-2 transition">
            <span>Start Your Free Trial</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center text-gray-400">
            <p>&copy; 2024 Alpha Intelligence. Built for serious investors.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="border border-slate-800 rounded-xl p-6 bg-slate-900/50 backdrop-blur-sm hover:border-slate-700 transition">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}
