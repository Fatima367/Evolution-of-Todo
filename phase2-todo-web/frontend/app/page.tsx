"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Target,
  Zap,
  BarChart3,
  CheckCircle2,
  ArrowRight,
  Calendar,
  Bell,
  Users,
  TrendingUp,
  Shield,
  Sparkles,
  Layers,
  Clock,
  Pencil,
  CalendarCheck,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useUIStore } from "@/store";
import { Button } from "@/components/ui/Button";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

const features = [
  {
    icon: Target,
    title: "Smart Prioritization",
    description:
      "AI-powered task prioritization helps you focus on what matters most.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description:
      "Blazing fast performance with instant updates and real-time sync.",
  },
  {
    icon: BarChart3,
    title: "Insightful Analytics",
    description:
      "Track your productivity with beautiful charts and actionable insights.",
  },
  {
    icon: CheckCircle2,
    title: "Never Miss a Beat",
    description:
      "Smart reminders and recurring tasks keep you on track effortlessly.",
  },
];

const howItWorks = [
  {
    step: "01",
    title: "Create Your Tasks",
    description:
      "Quickly add tasks with priorities, due dates, and tags in seconds.",
    icon: Layers,
  },
  {
    step: "02",
    title: "Organize & Prioritize",
    description:
      "Let our smart system help you organize and prioritize your workload.",
    icon: Target,
  },
  {
    step: "03",
    title: "Track Progress",
    description:
      "Monitor your productivity with real-time analytics and insights.",
    icon: TrendingUp,
  },
  {
    step: "04",
    title: "Achieve Your Goals",
    description:
      "Complete tasks efficiently and celebrate your accomplishments.",
    icon: CheckCircle2,
  },
];

const benefits = [
  {
    icon: Clock,
    title: "Save Time",
    description: "Reduce planning time by 50% with intelligent automation",
    color: "blue",
  },
  {
    icon: Shield,
    title: "Stay Secure",
    description: "Enterprise-grade security keeps your data safe and private",
    color: "purple",
  },
  {
    icon: Users,
    title: "Collaborate",
    description: "Work together seamlessly with your team in real-time",
    color: "teal",
  },
  {
    icon: Bell,
    title: "Never Forget",
    description:
      "Smart notifications ensure you never miss important deadlines",
    color: "pink",
  },
];

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
            className="absolute inset-0 opacity-[0.02] dark:opacity-[0.05]"
            style={{
              backgroundImage:
                "linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)",
              backgroundSize: "50px 50px",
            }}
          />
          <motion.div
            animate={{
              y: [0, -15, 0],
              opacity: [0.15, 0.25, 0.15],
            }}
            transition={{
              duration: 12,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="absolute top-20 right-[10%] w-96 h-96 rounded-full"
            style={{
              background:
                "radial-gradient(circle, rgba(110,184,225,0.1) 0%, transparent 70%)",
            }}
          />
          <motion.div
            animate={{
              y: [0, 20, 0],
              opacity: [0.1, 0.2, 0.1],
            }}
            transition={{
              duration: 15,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 3,
            }}
            className="absolute bottom-20 left-[8%] w-80 h-80 rounded-full"
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
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="space-y-6 text-center lg:text-left"
            >
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-extrabold leading-[1.1] tracking-tight">
                <span className="text-foreground">Organize Your World,</span>
                <br />
                <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
                  Evolve Your Workflow
                </span>
              </h1>

              <p className="text-base sm:text-lg text-muted-foreground leading-relaxed max-w-2xl mx-auto lg:mx-0">
                From simple lists to intelligent insights, the last todo app
                you'll ever need. Stay focused, get organized, and achieve more
                every day.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-4">
                <button
                  onClick={handleCTAClick}
                  className="btn-primary-gradient group w-full sm:w-auto"
                >
                  Create Your First Task
                  <ArrowRight className="inline-block ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </motion.div>

            {/* Right Column - Visual Element */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
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
                    className="absolute top-0 left-0 right-12 glass-card p-6 rounded-2xl border-2 shadow-2xl"
                    style={{
                      borderColor: "#6EB8E1",
                      boxShadow: "0 20px 60px rgba(110, 184, 225, 0.2)",
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
                        <div
                          className="h-3 rounded w-3/4"
                          style={{ backgroundColor: "#D6E6F2" }}
                        ></div>
                        <div
                          className="h-2 rounded w-full"
                          style={{ backgroundColor: "#E6E5E1" }}
                        ></div>
                        <div
                          className="h-2 rounded w-2/3"
                          style={{ backgroundColor: "#E6E5E1" }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 2 - Purple */}
                  <div
                    className="absolute top-24 left-12 right-0 glass-card p-6 rounded-2xl border-2 shadow-2xl"
                    style={{
                      borderColor: "#C8ABE6",
                      boxShadow: "0 20px 60px rgba(200, 171, 230, 0.2)",
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
                        <div
                          className="h-3 rounded w-2/3"
                          style={{ backgroundColor: "#DBD6F4" }}
                        ></div>
                        <div
                          className="h-2 rounded w-full"
                          style={{ backgroundColor: "#E6E5E1" }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 3 - Teal */}
                  <div
                    className="absolute top-44 left-0 right-12 glass-card p-6 rounded-2xl border-2 shadow-2xl"
                    style={{
                      borderColor: "#4EB5A9",
                      boxShadow: "0 20px 60px rgba(78, 181, 169, 0.2)",
                    }}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="mt-1">
                        <Zap className="h-6 w-6" style={{ color: "#4EB5A9" }} />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div
                          className="h-3 rounded w-1/2"
                          style={{ backgroundColor: "#BAD0CC" }}
                        ></div>
                        <div
                          className="h-2 rounded w-5/6"
                          style={{ backgroundColor: "#E6E5E1" }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Card 4 - Purple */}
                  <div
                    className="absolute top-64 left-8 right-0 glass-card p-6 rounded-2xl border-2 shadow-2xl"
                    style={{
                      borderColor: "#C8ABE6",
                      boxShadow: "0 20px 60px rgba(200, 171, 230, 0.2)",
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
                        <div
                          className="h-3 rounded w-2/3"
                          style={{ backgroundColor: "#DBD6F4" }}
                        ></div>
                        <div
                          className="h-2 rounded w-full"
                          style={{ backgroundColor: "#E6E5E1" }}
                        ></div>
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
      <section
        id="features"
        className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-white to-[#FBE5E7] dark:from-[#0E0E34] dark:to-[#252E8A]"
      >
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16 space-y-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="inline-block"
            >
              <span
                className="text-sm font-bold uppercase tracking-wider"
                style={{ color: "#5A7FC8" }}
              >
                Features
              </span>
            </motion.div>
            <h2 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground tracking-tight">
              Everything You Need
            </h2>
            <p className="text-base text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed to supercharge your productivity
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="group relative"
                >
                  <motion.div
                    whileHover={{ y: -4, transition: { duration: 0.2 } }}
                    className="h-full bg-white dark:bg-[#252E8A]/30 p-8 rounded-xl border shadow-sm hover:shadow-lg transition-all duration-300"
                    style={{ borderColor: "#BAD0CC" }}
                  >
                    <div className="relative space-y-4">
                      <motion.div
                        whileHover={{ scale: 1.05, rotate: 5 }}
                        transition={{ duration: 0.2 }}
                        className="inline-flex p-3 rounded-lg border"
                        style={{
                          backgroundColor: "rgba(110, 184, 225, 0.1)",
                          borderColor: "#6EB8E1",
                        }}
                      >
                        <Icon
                          className="h-6 w-6"
                          style={{ color: "#6EB8E1" }}
                        />
                      </motion.div>

                      <h3 className="text-lg font-display font-bold text-foreground group-hover:text-primary transition-colors">
                        {feature.title}
                      </h3>

                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </div>

                    <div
                      className="absolute bottom-0 left-0 right-0 h-1 rounded-b-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{
                        background:
                          "linear-gradient(90deg, #6EB8E1 0%, #4EB5A9 100%)",
                      }}
                    />
                  </motion.div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-white via-[#F7F6F7] to-[#E6E5E1] dark:from-[#252E8A] dark:to-[#0E0E34]">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16 space-y-4"
          >
            <span
              className="text-sm font-bold uppercase tracking-wider"
              style={{ color: "#C8ABE6" }}
            >
              How It Works
            </span>
            <h2 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground tracking-tight">
              Get Started in Minutes
            </h2>
            <p className="text-base text-muted-foreground max-w-2xl mx-auto">
              Four simple steps to transform your productivity
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {howItWorks.map((item, index) => {
              const Icon = item.icon;
              const colors = [
                {
                  gradient: "linear-gradient(135deg, #6EB8E1 0%, #5A7FC8 100%)",
                  shadow: "rgba(110, 184, 225, 0.25)",
                  border: "#6EB8E1",
                },
                {
                  gradient: "linear-gradient(135deg, #C8ABE6 0%, #DBD6F4 100%)",
                  shadow: "rgba(200, 171, 230, 0.25)",
                  border: "#C8ABE6",
                },
                {
                  gradient: "linear-gradient(135deg, #4EB5A9 0%, #48ADB7 100%)",
                  shadow: "rgba(78, 181, 169, 0.25)",
                  border: "#4EB5A9",
                },
                {
                  gradient: "linear-gradient(135deg, #5A7FC8 0%, #252E8A 100%)",
                  shadow: "rgba(90, 127, 200, 0.25)",
                  border: "#5A7FC8",
                },
              ];
              const colorSet = colors[index];

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="relative group"
                >
                  <motion.div
                    whileHover={{ y: -8, scale: 1.02 }}
                    className="relative bg-white dark:bg-[#252E8A]/30 p-8 rounded-2xl border-2 shadow-lg hover:shadow-2xl transition-all duration-300"
                    style={{ borderColor: colorSet.border }}
                  >
                    {/* Step Number Badge */}
                    <div
                      className="absolute -top-4 -left-4 w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg"
                      style={{ background: colorSet.gradient }}
                    >
                      {item.step}
                    </div>

                    {/* Icon Container */}
                    <motion.div
                      whileHover={{ rotate: 360, scale: 1.1 }}
                      transition={{ duration: 0.6 }}
                      className="w-16 h-16 rounded-2xl mx-auto mb-6 flex items-center justify-center"
                      style={{
                        background: colorSet.gradient,
                        boxShadow: `0 10px 40px ${colorSet.shadow}`,
                      }}
                    >
                      <Icon className="h-8 w-8 text-white" />
                    </motion.div>

                    {/* Content */}
                    <div className="space-y-3 text-center">
                      <h3 className="text-lg font-display font-bold text-foreground group-hover:text-primary transition-colors">
                        {item.title}
                      </h3>

                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {item.description}
                      </p>
                    </div>

                    {/* Animated Bottom Border */}
                    <div
                      className="absolute bottom-0 left-0 right-0 h-1 rounded-b-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ background: colorSet.gradient }}
                    />
                  </motion.div>

                  {/* Connection Line */}
                  {index < howItWorks.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-current to-transparent opacity-20" />
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-[#E6E5E1] via-[#F7F6F7] to-white dark:from-[#0E0E34] dark:to-[#252E8A]">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16 space-y-4"
          >
            <span
              className="text-sm font-bold uppercase tracking-wider"
              style={{ color: "#48ADB7" }}
            >
              Benefits
            </span>
            <h2 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground tracking-tight">
              Why Choose TodoEvo
            </h2>
            <p className="text-base text-muted-foreground max-w-2xl mx-auto">
              Experience the difference with our powerful platform
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              const colors = {
                blue: {
                  gradient: "linear-gradient(135deg, #D6E6F2 0%, #6EB8E1 100%)",
                  border: "#6EB8E1",
                  icon: "#5A7FC8",
                  shadow: "rgba(110, 184, 225, 0.2)",
                },
                purple: {
                  gradient: "linear-gradient(135deg, #DBD6F4 0%, #C8ABE6 100%)",
                  border: "#C8ABE6",
                  icon: "#252E8A",
                  shadow: "rgba(200, 171, 230, 0.2)",
                },
                teal: {
                  gradient: "linear-gradient(135deg, #BAD0CC 0%, #4EB5A9 100%)",
                  border: "#4EB5A9",
                  icon: "#48ADB7",
                  shadow: "rgba(78, 181, 169, 0.2)",
                },
                pink: {
                  gradient: "linear-gradient(135deg, #FBE5E7 0%, #F8CEC0 100%)",
                  border: "#F8CEC0",
                  icon: "#C8ABE6",
                  shadow: "rgba(248, 206, 192, 0.2)",
                },
              };
              const colorSet = colors[benefit.color as keyof typeof colors];

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="group"
                >
                  <motion.div
                    whileHover={{ y: -8, scale: 1.02 }}
                    className="relative h-full p-8 rounded-2xl border-2 shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden"
                    style={{
                      background: "white",
                      borderColor: colorSet.border,
                    }}
                  >
                    {/* Gradient Overlay on Hover */}
                    <div
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ background: colorSet.gradient }}
                    />

                    {/* Content */}
                    <div className="relative z-10">
                      {/* Icon with Gradient Background */}
                      <motion.div
                        whileHover={{
                          rotate: [0, -10, 10, -10, 0],
                          scale: 1.1,
                        }}
                        transition={{ duration: 0.5 }}
                        className="w-14 h-14 rounded-xl mb-6 mx-auto flex items-center justify-center shadow-lg group-hover:shadow-xl"
                        style={{
                          background: colorSet.gradient,
                          boxShadow: `0 8px 32px ${colorSet.shadow}`,
                        }}
                      >
                        <Icon className="h-7 w-7 text-white" />
                      </motion.div>

                      <h3 className="text-lg font-display font-bold text-center mb-3 text-[#201761] group-hover:text-white transition-colors duration-300">
                        {benefit.title}
                      </h3>

                      <p className="text-sm text-center leading-relaxed text-[#201761]/80 group-hover:text-white transition-colors duration-300">
                        {benefit.description}
                      </p>
                    </div>

                    {/* Decorative Corner Element */}
                    <div
                      className="absolute -bottom-8 -right-8 w-24 h-24 rounded-full opacity-10 group-hover:opacity-20 transition-opacity"
                      style={{ background: colorSet.gradient }}
                    />
                  </motion.div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 relative overflow-hidden bg-gradient-to-b from-white to-[#D6E6F2] dark:from-[#252E8A] dark:to-[#0E0E34]">
        <div className="absolute inset-0 pointer-events-none">
          <div
            className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
            style={{
              backgroundImage:
                "radial-gradient(circle, currentColor 2px, transparent 2px)",
              backgroundSize: "40px 40px",
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
          <div
            className="bg-white/80 dark:bg-[#252E8A]/80 backdrop-blur-xl p-12 lg:p-16 rounded-2xl border shadow-xl"
            style={{ borderColor: "#6EB8E1" }}
          >
            <motion.div
              initial={{ scale: 0.95 }}
              whileInView={{ scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="space-y-6"
            >
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-extrabold tracking-tight mb-4">
                  <span className="text-foreground">Ready to Get </span>
                  <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
                    Started?
                  </span>
                </h2>
              </motion.div>

              <motion.p
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="text-base text-muted-foreground max-w-2xl mx-auto"
              >
                Join thousands of productive people who transformed their
                workflow. Start organizing today.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.5 }}
                className="pt-4"
              >
                <button
                  onClick={openSignUpModal}
                  className="btn-primary-gradient group"
                >
                  Start For Free
                  <ArrowRight className="inline-block ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.6 }}
                className="text-sm font-medium text-muted-foreground flex items-center justify-center gap-2 flex-wrap"
              >
                <CheckCircle2
                  className="h-4 w-4"
                  style={{ color: "#4EB5A9" }}
                />
                No credit card required
                <span className="text-gray-400">•</span>
                <CheckCircle2
                  className="h-4 w-4"
                  style={{ color: "#4EB5A9" }}
                />
                Free forever
              </motion.p>
            </motion.div>
          </div>
        </motion.div>
      </section>

      <Footer />
    </div>
  );
}
