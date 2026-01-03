import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { ShieldCheck } from 'lucide-react'
import { Navbar, Footer } from '@/components/layout'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#020617] flex flex-col">
      <Navbar />
      <main className="flex-grow pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full">
        <div className="glass-card p-8 md:p-12 space-y-8 border border-white/20 dark:border-[#252E8A]/20">
          <div className="flex items-center space-x-3 mb-6">
            <ShieldCheck className="h-10 w-10 text-primary dark:text-[#6EB8E1]" />
            <h1 className="text-3xl font-display font-bold text-gray-900 dark:text-white">Privacy Policy</h1>
          </div>

          <div className="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-400 space-y-6">
            <p className="text-lg">Last updated: January 3, 2026</p>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">1. Introduction</h2>
              <p>Welcome to TodoEvo. We are committed to protecting your personal information and your right to privacy. If you have any questions or concerns about our policy, or our practices with regards to your personal information, please contact us.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">2. Information We Collect</h2>
              <p>We collect personal information that you provide to us such as name, email address, and passwords when you register on our application. We also collect data about the tasks you create to provide the AI-powered insights service.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">3. How We Use Your Information</h2>
              <p>We use the information we collect or receive to facilitate account creation and logon process, and to provide you with the core functionality of the AI chatbot for task management.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">4. Data Security</h2>
              <p>We use appropriate technical and organizational security measures designed to protect the security of any personal information we process. However, please also remember that we cannot guarantee that the internet itself is 100% secure.</p>
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
