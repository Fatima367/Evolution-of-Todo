'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Sparkles, Target, Zap, BarChart3, CheckCircle2, ArrowRight, CheckSquare } from 'lucide-react'
import { useAuthStore, useUIStore } from '@/store'
import { Button } from '@/components/ui/Button'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'

const features = [
  {
    icon: Target,
    title: 'Smart Prioritization',
    description: 'AI-powered task prioritization helps you focus on what matters most.',
    color: 'primary',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Blazing fast performance with instant updates and real-time sync.',
    color: 'accent',
  },
  {
    icon: BarChart3,
    title: 'Insightful Analytics',
    description: 'Track your productivity with beautiful charts and actionable insights.',
    color: 'success',
  },
  {
    icon: CheckCircle2,
    title: 'Never Miss a Beat',
    description: 'Smart reminders and recurring tasks keep you on track effortlessly.',
    color: 'primary',
  },
]

export default function LandingPage() {
  const { isAuthenticated } = useAuthStore()
  const { openSignUpModal } = useUIStore()

  const handleCTAClick = () => {
    if (isAuthenticated) {
      window.location.href = '/dashboard/tasks'
    } else {
      openSignUpModal()
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <Navbar />

      {/* Hero Section - Asymmetric Two-Column Layout */}
      <section className="relative flex-1 flex items-center px-4 sm:px-6 lg:px-8 pt-32 pb-20 overflow-hidden">
        {/* Animated Geometric Background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {/* Subtle Grid Pattern */}
          <div className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
            style={{
              backgroundImage: 'linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)',
              backgroundSize: '80px 80px'
            }}
          />

          {/* Floating Geometric Shapes */}
          <motion.div
            animate={{
              y: [0, -20, 0],
              rotate: [0, 5, 0],
              opacity: [0.4, 0.6, 0.4],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            className="absolute top-20 right-[10%] w-64 h-64 border-2 border-primary/20 rounded-3xl blur-sm"
          />
          <motion.div
            animate={{
              y: [0, 30, 0],
              rotate: [0, -10, 0],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 12,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1,
            }}
            className="absolute bottom-32 left-[8%] w-72 h-72 border-2 border-accent/20 rounded-full blur-sm"
          />
          <motion.svg
            className="absolute top-1/2 right-[20%] w-48 h-48 text-primary/10"
            viewBox="0 0 200 200"
            animate={{
              rotate: [0, 360],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: 'linear',
            }}
          >
            <path
              fill="currentColor"
              d="M100,0 L125,50 L175,50 L137.5,87.5 L150,150 L100,112.5 L50,150 L62.5,87.5 L25,50 L75,50 Z"
            />
          </motion.svg>
        </div>

        <div className="relative max-w-7xl mx-auto w-full">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left Column - Content */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, ease: 'easeOut' }}
              className="space-y-8"
            >
              <div className="inline-flex items-center space-x-2 glass-card px-4 py-2 rounded-full border border-primary/20">
                <Sparkles className="h-4 w-4 text-accent" />
                <span className="text-sm font-medium text-foreground">Powered by AI</span>
              </div>

              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-display font-bold leading-tight">
                <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                  Organize Your World,
                </span>
                <br />
                <span className="text-foreground">
                  Evolve Your Workflow
                </span>
              </h1>

              <p className="text-xl sm:text-2xl text-muted-foreground leading-relaxed">
                From simple lists to intelligent insights, the last todo app you'll ever need.
              </p>

              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 pt-4">
                <Button
                  size="lg"
                  onClick={handleCTAClick}
                  className="glow-primary group text-lg px-8 py-6 bg-primary hover:bg-primary/90"
                >
                  Create Your First Task
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
                <Button variant="outline" size="lg" asChild className="text-lg px-8 py-6">
                  <Link href="/#features">Learn More</Link>
                </Button>
              </div>

              {/* Inline Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.3 }}
                className="flex flex-wrap gap-8 pt-8"
              >
                {[
                  { label: 'Active Users', value: '10K+' },
                  { label: 'Tasks Done', value: '1M+' },
                  { label: 'Hours Saved', value: '50K+' },
                ].map((stat, index) => (
                  <div key={index} className="flex flex-col">
                    <div className="text-3xl font-display font-bold text-primary">
                      {stat.value}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </motion.div>
            </motion.div>

            {/* Right Column - Visual Element */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, delay: 0.2, ease: 'easeOut' }}
              className="relative hidden lg:block"
            >
              <div className="relative aspect-square max-w-lg mx-auto">
                {/* Decorative Card Stack */}
                <motion.div
                  animate={{
                    y: [0, -10, 0],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                  className="absolute inset-0"
                >
                  {/* Card 1 */}
                  <div className="absolute top-0 left-0 right-12 glass-card p-6 rounded-2xl border-2 border-primary/30 shadow-2xl shadow-primary/20">
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <CheckSquare className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="h-3 bg-primary/20 rounded w-3/4"></div>
                        <div className="h-2 bg-muted rounded w-full"></div>
                        <div className="h-2 bg-muted rounded w-2/3"></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 2 */}
                  <div className="absolute top-24 left-12 right-0 glass-card p-6 rounded-2xl border-2 border-accent/30 shadow-2xl shadow-accent/20">
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <Target className="h-6 w-6 text-accent" />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="h-3 bg-accent/20 rounded w-2/3"></div>
                        <div className="h-2 bg-muted rounded w-full"></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 3 */}
                  <div className="absolute top-48 left-0 right-12 glass-card p-6 rounded-2xl border-2 border-green-500/30 shadow-2xl shadow-green-500/20">
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <Zap className="h-6 w-6 text-green-500" />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="h-3 bg-green-500/20 rounded w-1/2"></div>
                        <div className="h-2 bg-muted rounded w-5/6"></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl sm:text-5xl font-display font-bold mb-4 text-foreground">
              Everything You Need
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed to supercharge your productivity
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ y: -8, transition: { duration: 0.2 } }}
                  className="group relative"
                >
                  <div className="h-full glass-card p-8 rounded-2xl border border-transparent hover:border-primary/20 transition-all duration-300">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <div className="relative space-y-4">
                      <div className="inline-flex p-3 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20">
                        <Icon className="h-7 w-7 text-primary" />
                      </div>
                      <h3 className="text-xl font-display font-semibold text-foreground">
                        {feature.title}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-accent/5" />
          <div className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: 'radial-gradient(circle, currentColor 1px, transparent 1px)',
              backgroundSize: '40px 40px'
            }}
          />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto text-center relative"
        >
          <div className="glass-card p-12 lg:p-16 rounded-3xl border-2 border-primary/20 shadow-2xl">
            <motion.div
              initial={{ scale: 0.9 }}
              whileInView={{ scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="space-y-6"
            >
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold">
                <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                  Ready to Get Started?
                </span>
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Join thousands of productive people who transformed their workflow
              </p>
              <div className="pt-4">
                <Button
                  size="lg"
                  onClick={openSignUpModal}
                  className="glow-primary group text-lg px-10 py-6 bg-primary hover:bg-primary/90"
                >
                  Start For Free
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                No credit card required • Free forever
              </p>
            </motion.div>
          </div>
        </motion.div>
      </section>

      <Footer />
    </div>
  )
}
