import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { FileText } from 'lucide-react'
import { Navbar, Footer } from '@/components/layout'

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#020617] flex flex-col">
      <Navbar />
      <main className="flex-grow pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full">
        <div className="glass-card p-8 md:p-12 space-y-8 border border-white/20 dark:border-[#252E8A]/20">
          <div className="flex items-center space-x-3 mb-6">
            <FileText className="h-10 w-10 text-primary dark:text-[#6EB8E1]" />
            <h1 className="text-3xl font-display font-bold text-gray-900 dark:text-white">Terms of Service</h1>
          </div>

          <div className="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-400 space-y-6">
            <p className="text-lg">Last updated: January 3, 2026</p>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">1. Agreement to Terms</h2>
              <p>By accessing or using TodoBoard, you agree to be bound by these Terms of Service. If you disagree with any part of these terms, you may not access our service.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">2. User Accounts</h2>
              <p>When you create an account with us, you must provide information that is accurate, complete, and current. Failure to do so constitutes a breach of the Terms, which may result in immediate termination of your account.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">3. Intellectual Property</h2>
              <p>The Service and its original content, features, and functionality are and will remain the exclusive property of TodoBoard and its licensors.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">4. Termination</h2>
              <p>We may terminate or suspend your account immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">5. Limitation of Liability</h2>
              <p>In no event shall TodoBoard, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages resulting from your use of the service.</p>
            </section>
          </div>

          <div className="pt-8 border-t border-gray-200 dark:border-gray-800">
            <Link href="/">
              <Button variant="outline">
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
