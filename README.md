---
title: Evolution of Todo
emoji: 🚀
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

# The Evolution of Todo Project

This project, "The Evolution of Todo," is designed to foster mastery in Spec-Driven Development and Cloud-Native AI by iteratively building a Todo application. Starting from a simple in-memory console application, the project evolves into a sophisticated, cloud-native AI chatbot deployed on Kubernetes.

## What You Will Learn

You will gain hands-on experience and master key areas in modern software development:

*   **Spec-Driven Development**: Utilizing Claude Code and Spec-Kit Plus for defining and implementing features.
*   **Reusable Intelligence**: Developing Agents, Skills, and Subagents.
*   **Full-Stack Development**: Building with Next.js, FastAPI, SQLModel, and Neon Serverless Database.
*   **AI Agent Development**: Leveraging OpenAI Agents SDK and Official MCP SDK.
*   **Cloud-Native Deployment**: Docker, Kubernetes (Minikube, DOKS), Helm Charts, Kafka, and Dapr.
*   **AIOps**: Using tools like `kubectl-ai` and `kagent`.
*   **Cloud-Native Blueprints**: Developing blueprints for spec-driven deployment.

## Project Phases Overview

The project is structured into five progressive phases, each building upon the last:

### Phase I: Todo In-Memory Python Console App

*   **Objective**: Build a command-line todo application that stores tasks in memory.
*   **Functionality**: Add, Delete, Update, View, Mark Complete tasks.
*   **Technology Stack**: Python 3.13+, UV, Claude Code, Spec-Kit Plus.
*   **Development Approach**: Strictly spec-driven; no manual coding allowed, Claude Code generates implementation from refined specs.

### Phase II: Todo Full-Stack Web Application

*   **Objective**: Transform the console app into a modern multi-user web application with persistent storage.
*   **Functionality**: All Basic Level features as a web application, RESTful API, responsive frontend, persistent storage.
*   **Technology Stack**: Frontend (Next.js 16+ App Router), Backend (Python FastAPI), ORM (SQLModel), Database (Neon Serverless PostgreSQL), Authentication (Better Auth with JWT).

### Phase III: Todo AI Chatbot

*   **Objective**: Create an AI-powered chatbot interface for managing todos through natural language.
*   **Functionality**: Conversational interface for all Basic Level features, AI agents use MCP tools to manage tasks, stateless chat endpoint persisting conversation state to database.
*   **Technology Stack**: Frontend (OpenAI ChatKit), Backend (Python FastAPI), AI Framework (OpenAI Agents SDK), MCP Server (Official MCP SDK), ORM (SQLModel), Database (Neon Serverless PostgreSQL), Authentication (Better Auth).

### Phase IV: Local Kubernetes Deployment

*   **Objective**: Deploy the Todo Chatbot on a local Kubernetes cluster using Minikube and Helm Charts.
*   **Functionality**: Containerize frontend and backend (using Docker AI Agent - Gordon if available), create Helm charts, deploy on Minikube.
*   **Technology Stack**: Containerization (Docker), Docker AI (Gordon), Orchestration (Kubernetes - Minikube), Package Manager (Helm Charts), AI DevOps (`kubectl-ai`, `kagent`).

### Phase V: Advanced Cloud Deployment

*   **Objective**: Implement advanced features and deploy to a production-grade Kubernetes cluster on Azure (AKS)/Google Cloud (GKE)/Oracle.
*   **Functionality**: Implement Advanced Level (Recurring Tasks, Due Dates & Reminders) and Intermediate Level (Priorities, Tags, Search, Filter, Sort) features, add event-driven architecture with Kafka, implement Dapr for distributed application runtime, CI/CD, monitoring, and logging.
*   **Technology Stack**: Azure/Google Cloud/Oracle Kubernetes, Kafka (Confluent/Redpanda Cloud or Self-hosted Strimzi), Dapr, GitHub Actions.

## Core Principles

This project emphasizes two main principles:

*   **Spec-Driven Development (SDD)**: No code is written until the specification is complete and approved. This workflow follows a strict cycle: Specify → Plan → Tasks → Implement.
*   **Agentic Dev Stack**: This integrates `AGENTS.md` (the "Constitution" for agent behavior), Spec-KitPlus (the "Architect" for managing spec artifacts), and Claude Code (the "Executor" that reads project memory and executes Spec-Kit tools via MCP).

## Submission Requirements

For each phase, developers are required to submit:
1.  A Public GitHub Repository with all source code, specification files, `CLAUDE.md`, and a comprehensive `README.md`.
2.  Deployed Application Links (Vercel/frontend URL, Backend API URL, Chatbot URL, Minikube setup instructions, DigitalOcean deployment URL, depending on the phase).
3.  A Demo Video (maximum 90 seconds).
4.  A WhatsApp number for presentation invitations.

This project provides a comprehensive journey through modern software engineering, from basic application development to advanced cloud-native, AI-powered systems.