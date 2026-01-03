"use client";

import { motion } from "framer-motion";
import {
  Target,
  Zap,
  BarChart3,
  CheckCircle2,
  ArrowRight,
  Clock,
  Shield,
  Users,
  Bell,
  TrendingUp,
  Layers,
  Pencil,
  CalendarCheck,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useUIStore } from "@/store";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

// Premium gradient configurations
const gradients = {
  blue: {
    from: "#6EB8E1",
    to: "#5A7FC8",
    accent: "#D6E6F2",
  },
  purple: {
    from: "#C8ABE6",
    to: "#252E8A",
    accent: "#DBD6F4",
  },
  teal: {
    from: "#4EB5A9",
    to: "#48ADB7",
    accent: "#BAD0CC",
  },
  peach: {
    from: "#F8CEC0",
    to: "#FBE5E7",
    accent: "#F8CEC0",
  },
};

const features = [
  {
    icon: Target,
    title: "Smart Prioritization",
    description: "AI-powered task prioritization helps you focus on what matters most.",
    gradient: gradients.blue,
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Blazing fast performance with instant updates and real-time sync.",
    gradient: gradients.teal,
  },
  {
    icon: BarChart3,
    title: "Insightful Analytics",
    description: "Track your productivity with beautiful charts and actionable insights.",
    gradient: gradients.purple,
  },
  {
    icon: CheckCircle2,
    title: "Never Miss a Beat",
    description: "Smart reminders and recurring tasks keep you on track effortlessly.",
    gradient: gradients.blue,
  },
];

const howItWorks = [
  {
    step: "01",
    title: "Create Your Tasks",
    description: "Quickly add tasks with priorities, due dates, and tags in seconds.",
    icon: Layers,
    gradient: gradients.blue,
  },
  {
    step: "02",
    title: "Organize & Prioritize",
    description: "Let our smart system help you organize and prioritize your workload.",
    icon: Target,
    gradient: gradients.purple,
  },
  {
    step: "03",
    title: "Track Progress",
    description: "Monitor your productivity with real-time analytics and insights.",
    icon: TrendingUp,
    gradient: gradients.teal,
  },
  {
    step: "04",
    title: "Achieve Your Goals",
    description: "Complete tasks efficiently and celebrate your accomplishments.",
    icon: CheckCircle2,
    gradient: gradients.purple,
  },
];

const benefits = [
  {
    icon: Clock,
    title: "Save Time",
    description: "Reduce planning time by 50% with intelligent automation",
    gradient: gradients.blue,
  },
  {
    icon: Shield,
    title: "Stay Secure",
    description: "Enterprise-grade security keeps your data safe and private",
    gradient: gradients.purple,
  },
  {
    icon: Users,
    title: "Collaborate",
    description: "Work together seamlessly with your team in real-time",
    gradient: gradients.teal,
  },
  {
    icon: Bell,
    title: "Never Forget",
    description: "Smart notifications ensure you never miss important deadlines",
    gradient: gradients.peach,
  },
];

// Modern premium card with gradient border
function GradientCard({
  children,
  gradient,
  className = "",
}: {
  children: React.ReactNode;
  gradient: { from: string; to: string; accent: string };
  className?: string;
}) {
  return (
    <motion.div
      whileHover={{ y: -6 }}
      transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
      className={`relative group ${className}`}
    >
      {/* Gradient border layer - always visible */}
      <div
        className="absolute inset-0 rounded-2xl transition-opacity duration-500"
        style={{
          background: `linear-gradient(135deg, ${gradient.from}40 0%, ${gradient.to}40 100%)`,
          padding: "1px",
        }}
      />
      {/* Gradient border on hover - brighter */}
      <div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: `linear-gradient(135deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
          padding: "1px",
        }}
      />
      {/* Inner card with shadow */}
      <div className="relative h-full bg-white dark:bg-[#0E0E34] rounded-2xl shadow-md group-hover:shadow-xl transition-shadow duration-300">
        {/* Hover glow overlay */}
        <div
          className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl"
          style={{
            background: `radial-gradient(circle at top right, ${gradient.from}10 0%, transparent 50%)`,
          }}
        />
        {children}
      </div>
    </motion.div>
  );
}

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  const { openSignUpModal } = useUIStore();

  const handleCTAClick = () => {
    if (isAuthenticated) {
      window.location.href = "/dashboard/tasks";
    } else {
      openSignUpModal();
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-[#F7F6F7] via-white to-[#D6E6F2] dark:from-[#0E0E34] dark:via-[#252E8A] dark:to-[#0E0E34]">
      <Navbar />

      {/* Hero Section */}
      <section className="relative flex items-center px-4 sm:px-6 lg:px-8 pt-32 pb-12 min-h-[600px] overflow-hidden">
        {/* Subtle Animated Background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div
            className="absolute inset-0 opacity-[0.02] dark:opacity-[0.04]"
            style={{
              backgroundImage:
                "linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)",
              backgroundSize: "60px 60px",
            }}
          />
          <motion.div
            animate={{
              y: [0, -20, 0],
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="absolute top-20 right-[10%] w-96 h-96 rounded-full blur-3xl"
            style={{
              background:
                "radial-gradient(circle, rgba(110,184,225,0.1) 0%, transparent 70%)",
            }}
          />
          <motion.div
            animate={{
              y: [0, 20, 0],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 12,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 2,
            }}
            className="absolute bottom-20 left-[8%] w-80 h-80 rounded-full blur-3xl"
            style={{
              background:
                "radial-gradient(circle, rgba(200,171,230,0.1) 0%, transparent 70%)",
            }}
          />
        </div>

        <div className="relative max-w-7xl mx-auto w-full">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left Column - Content */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
              className="space-y-6 text-center lg:text-left"
            >
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-extrabold leading-[1.1] tracking-tight">
                <span className="text-foreground dark:text-[#F7F6F7]">Organize Your World,</span>
                <br />
                <span className="bg-gradient-to-r from-[#6EB8E1] via-[#4EB5A9] to-[#5A7FC8] bg-clip-text text-transparent">
                  Evolve Your Workflow
                </span>
              </h1>

              <p className="text-base sm:text-lg text-gray-600 dark:text-gray-400 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                From simple lists to intelligent insights, the last todo app
                you'll ever need. Stay focused, get organized, and achieve more
                every day.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
                <motion.button
                  onClick={handleCTAClick}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="group relative px-8 py-4 bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 w-full sm:w-auto overflow-hidden"
                >
                  <span className="relative z-10 flex items-center justify-center gap-2">
                    Create Your First Task
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                  {/* Subtle shine effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_ease-in-out_infinite]" />
                </motion.button>
              </div>
            </motion.div>

            {/* Right Column - Visual Element */}
            <motion.div
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.15, ease: [0.25, 0.1, 0.25, 1] }}
              className="relative hidden lg:flex lg:items-center lg:justify-center lg:-mb-20 w-full"
            >
              <div className="relative w-full max-w-lg h-[500px]">
                {/* Decorative Card Stack with new colors */}
                <motion.div
                  animate={{
                    y: [0, -10, 0],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                  className="absolute inset-0"
                >
                  {/* Card 1 - Blue */}
                  <div
                    className="absolute top-0 left-0 right-12 bg-white dark:bg-[#1A1A3A] p-6 rounded-2xl border-2 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
                    style={{
                      borderColor: "#6EB8E1",
                    }}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <CheckCircle2
                          className="h-6 w-6"
                          style={{ color: "#6EB8E1" }}
                        />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="h-2.5 rounded w-3/4" style={{ background: "#6EB8E130" }}></div>
                        <div className="h-2 rounded w-full bg-[#E6E5E1] dark:bg-white/10"></div>
                        <div className="h-2 rounded w-1/2 bg-[#E6E5E1] dark:bg-white/10"></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 2 - Purple */}
                  <div
                    className="absolute top-24 left-12 right-0 bg-white dark:bg-[#1A1A3A] p-6 rounded-2xl border-2 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
                    style={{
                      borderColor: "#C8ABE6",
                    }}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <Pencil
                          className="h-6 w-6"
                          style={{ color: "#C8ABE6" }}
                        />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="h-2.5 rounded w-2/3" style={{ background: "#C8ABE630" }}></div>
                        <div className="h-2 rounded w-full bg-[#E6E5E1] dark:bg-white/10"></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 3 - Teal */}
                  <div
                    className="absolute top-44 left-0 right-12 bg-white dark:bg-[#1A1A3A] p-6 rounded-2xl border-2 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
                    style={{
                      borderColor: "#4EB5A9",
                    }}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <Zap className="h-6 w-6" style={{ color: "#4EB5A9" }} />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="h-2.5 rounded w-1/2" style={{ background: "#4EB5A930" }}></div>
                        <div className="h-2 rounded w-4/5 bg-[#E6E5E1] dark:bg-white/10"></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 4 - Purple */}
                  <div
                    className="absolute top-64 left-8 right-0 bg-white dark:bg-[#1A1A3A] p-6 rounded-2xl border-2 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
                    style={{
                      borderColor: "#C8ABE6",
                    }}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <CalendarCheck
                          className="h-6 w-6"
                          style={{ color: "#C8ABE6" }}
                        />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="h-2.5 rounded w-3/4" style={{ background: "#5A7FC830" }}></div>
                        <div className="h-2 rounded w-full bg-[#E6E5E1] dark:bg-white/10"></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section - Premium Design */}
      <section
        id="features"
        className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-white to-[#F7F6F7] dark:from-[#0E0E34] dark:to-[#1A1A4A]"
      >
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6 }}
            className="text-center mb-4"
          >
            <span
              className="inline-block px-4 py-1.5 text-xs font-semibold uppercase tracking-widest rounded-full bg-white dark:bg-white/5 border border-[#6EB8E1]/30 text-[#6EB8E1] shadow-sm"
            >
              Features
            </span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-5xl font-display font-extrabold text-center text-foreground dark:text-[#F7F6F7] tracking-tight mb-4"
          >
            Everything You Need
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="text-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-center mb-16"
          >
            Powerful features designed to supercharge your productivity
          </motion.p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              const gradient = feature.gradient as { from: string; to: string; accent: string };

              return (
                <GradientCard key={index} gradient={gradient} className="h-full">
                  <div className="relative z-10 p-6 space-y-5">
                    {/* Icon with gradient background */}
                    <div
                      className="inline-flex p-4 rounded-2xl shadow-lg opacity-90 group-hover:opacity-100 transition-opacity"
                      style={{
                        background: `linear-gradient(135deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
                      }}
                    >
                      <Icon className="h-6 w-6 text-white" />
                    </div>

                    <div className="space-y-3">
                      <h3 className="text-lg font-display font-bold text-foreground dark:text-[#F7F6F7] tracking-tight">
                        {feature.title}
                      </h3>

                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>

                    {/* Bottom accent line */}
                    <div
                      className="absolute bottom-0 left-6 right-6 h-0.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{ background: `linear-gradient(90deg, ${gradient.from} 0%, ${gradient.to} 100%)` }}
                    />
                  </div>
                </GradientCard>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section - Premium Design */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-white dark:bg-[#0E0E34]">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6 }}
            className="text-center mb-4"
          >
            <span className="inline-block px-4 py-1.5 text-xs font-semibold uppercase tracking-widest rounded-full bg-white dark:bg-white/5 border border-[#C8ABE6]/30 text-[#C8ABE6] shadow-sm">
              How It Works
            </span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-5xl font-display font-extrabold text-center text-foreground dark:text-[#F7F6F7] tracking-tight mb-4"
          >
            Get Started in Minutes
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="text-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-center mb-16"
          >
            Four simple steps to transform your productivity
          </motion.p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {howItWorks.map((item, index) => {
              const Icon = item.icon;
              const gradient = item.gradient as { from: string; to: string; accent: string };

              return (
                <div key={index} className="relative">
                  <GradientCard gradient={gradient} className="h-full">
                    <div className="relative z-10 p-6 space-y-4">
                      {/* Step number badge */}
                      <div
                        className="absolute -top-3 -left-3 w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold text-white shadow-lg"
                        style={{
                          background: `linear-gradient(135deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
                        }}
                      >
                        {item.step}
                      </div>

                      {/* Icon */}
                      <motion.div
                        whileHover={{ rotate: [0, -10, 10, -10, 0] }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex p-4 rounded-2xl shadow-lg ml-8"
                        style={{
                          background: `linear-gradient(135deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
                        }}
                      >
                        <Icon className="h-6 w-6 text-white" />
                      </motion.div>

                      <div className="space-y-3 ml-8">
                        <h3 className="text-base font-display font-bold text-foreground dark:text-[#F7F6F7] tracking-tight">
                          {item.title}
                        </h3>

                        <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                          {item.description}
                        </p>
                      </div>

                      {/* Bottom accent line */}
                      <div
                        className="absolute bottom-0 left-6 right-6 h-0.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                        style={{ background: `linear-gradient(90deg, ${gradient.from} 0%, ${gradient.to} 100%)` }}
                      />
                    </div>
                  </GradientCard>

                  {/* Connection line */}
                  {index < howItWorks.length - 1 && (
                    <div className="hidden lg:flex absolute top-1/2 -right-4 w-8 h-px opacity-30" style={{ background: `linear-gradient(to right, ${gradient.from} 0%, transparent 100%)` }} />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section - Premium Design */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-[#F7F6F7] to-white dark:from-[#1A1A4A] dark:to-[#0E0E34]">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6 }}
            className="text-center mb-4"
          >
            <span className="inline-block px-4 py-1.5 text-xs font-semibold uppercase tracking-widest rounded-full bg-white dark:bg-white/5 border border-[#4EB5A9]/30 text-[#4EB5A9] shadow-sm">
              Benefits
            </span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-5xl font-display font-extrabold text-center text-foreground dark:text-[#F7F6F7] tracking-tight mb-4"
          >
            Why Choose TodoBoard
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="text-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-center mb-16"
          >
            Experience the difference with our powerful platform
          </motion.p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              const gradient = benefit.gradient as { from: string; to: string; accent: string };

              return (
                <GradientCard key={index} gradient={gradient} className="h-full">
                  <div className="relative z-10 p-6 space-y-4">
                    {/* Icon with gradient background */}
                    <div
                      className="inline-flex p-4 rounded-2xl shadow-lg opacity-90 group-hover:opacity-100 transition-opacity"
                      style={{
                        background: `linear-gradient(135deg, ${gradient.from} 0%, ${gradient.to} 100%)`,
                      }}
                    >
                      <Icon className="h-6 w-6 text-white" />
                    </div>

                    <div className="space-y-3">
                      <h3 className="text-lg font-display font-bold text-foreground dark:text-[#F7F6F7] tracking-tight">
                        {benefit.title}
                      </h3>

                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {benefit.description}
                      </p>
                    </div>

                    {/* Bottom accent line */}
                    <div
                      className="absolute bottom-0 left-6 right-6 h-0.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{ background: `linear-gradient(90deg, ${gradient.from} 0%, ${gradient.to} 100%)` }}
                    />
                  </div>
                </GradientCard>
              );
            })}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-28 px-4 sm:px-6 lg:px-8 relative overflow-hidden bg-gradient-to-b from-white to-[#D6E6F2] dark:from-[#0E0E34] dark:to-[#1A1A4A]">
        {/* Subtle pattern */}
        <div className="absolute inset-0 pointer-events-none">
          <div
            className="absolute inset-0 opacity-20"
            style={{
              background:
                "radial-gradient(circle at 50% 0%, #6EB8E1 0%, transparent 50%)",
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
          <div className="relative">
            {/* Ambient glow behind */}
            <div
              className="absolute -inset-8 -z-10 rounded-[2rem] blur-xl"
              style={{
                background:
                  "linear-gradient(135deg, #6EB8E1 0%, #C8ABE6 100%)",
              }}
            />

            {/* Glass card */}
            <div className="relative bg-white/90 dark:bg-[#0E0E34]/90 backdrop-blur-xl p-12 lg:p-16 rounded-3xl border border-white/20 dark:border-white/10 shadow-2xl">
              <motion.div
                initial={{ scale: 0.98 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="space-y-6"
              >
                <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-extrabold tracking-tight">
                  <span className="text-foreground dark:text-[#F7F6F7]">Ready to Get </span>
                  <span className="bg-gradient-to-r from-[#6EB8E1] via-[#4EB5A9] to-[#5A7FC8] bg-clip-text text-transparent">
                    Started?
                  </span>
                </h2>

                <p className="text-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                  Join thousands of productive people who transformed their
                  workflow. Start organizing today.
                </p>

                <motion.div className="pt-4">
                  <motion.button
                    onClick={openSignUpModal}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="group relative px-8 py-4 bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden"
                  >
                    <span className="relative z-10 flex items-center justify-center gap-2">
                      Start For Free
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </span>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_ease-in-out_infinite]" />
                  </motion.button>
                </motion.div>

                <div className="flex items-center justify-center gap-8 text-sm font-medium text-gray-600 dark:text-gray-400 flex-wrap">
                  <span className="flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5" style={{ color: "#4EB5A9" }} />
                    No credit card required
                  </span>
                  <span className="flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5" style={{ color: "#4EB5A9" }} />
                    Free forever
                  </span>
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </section>

      <Footer />
    </div>
  );
}
