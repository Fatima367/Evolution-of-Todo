# Evolution of Todo - Agents & Skills Overview

This document provides an overview of all specialized subagents and skills created for the Evolution of Todo hackathon project.

## Subagents

Subagents are specialized AI agents that handle specific domains of the project. They have access to all tools and deep expertise in their area.

### 1. **Spec-Driven Architect Agent**
**Location:** `.claude/agents/spec-driven-architect/`

**Purpose:** Orchestrates the complete Spec-Driven Development workflow using SpecKit Plus.

**When to Use:**
- Starting a new hackathon phase
- Implementing features using SDD workflow (Specify → Plan → Tasks → Implement)
- Creating constitution, specifications, plans, and tasks
- Managing PHRs and ADRs

**Key Capabilities:**
- Constitution management
- Feature specification (WHAT)
- Technical planning (HOW)
- Task breakdown
- Implementation orchestration
- PHR and ADR creation
- Phase-specific guidance (I through V)

**Hackathon Integration:**
- Understands all 5 phases
- Knows scoring criteria
- Follows Nine Pillars of AI-Driven Development
- Enforces "no code without spec" rule

---

### 2. **Kubernetes Deployment Agent**
**Location:** `.claude/agents/kubernetes-deploy-agent/`

**Purpose:** Handles all containerization, orchestration, and cloud-native infrastructure.

**When to Use:**
- Phase IV (Minikube deployment)
- Phase V (cloud deployment with Kafka and Dapr)
- Containerizing applications
- Creating Helm charts
- Setting up event-driven architecture

**Key Capabilities:**
- Docker and containerization (Docker AI/Gordon)
- Kubernetes orchestration (Minikube, DOKS, GKE, AKS, OKE)
- Helm chart creation
- Kafka integration (Redpanda, Strimzi, Confluent)
- Dapr integration (Pub/Sub, State, Jobs, Secrets)
- AIOps (kubectl-ai, kagent)

**Cloud Providers Supported:**
- DigitalOcean Kubernetes (DOKS) - Recommended
- Google Kubernetes Engine (GKE)
- Azure Kubernetes Service (AKS)
- Oracle Kubernetes Engine (OKE) - Always Free

---

### 3. **BetterAuth Subagent** (Updated)
**Location:** `.claude/agents/betterauth-subagent/`

**Purpose:** Authentication, user management, and JWT-secured API access.

**When to Use:**
- Phase II and beyond
- Implementing user signup/signin
- JWT token management
- Securing REST API endpoints

**Key Capabilities:**
- Better Auth configuration
- JWT token generation and verification
- Next.js frontend authentication
- FastAPI backend JWT middleware
- User isolation in database
- Protected routes and middleware

**Security Features:**
- Shared JWT secret management
- Token expiration handling
- User data isolation
- CORS configuration

---

### 4. **ChatKit Expert Agent** (Existing - Keep)
**Location:** `.claude/agents/chatkit-expert-agent/`

**Purpose:** OpenAI ChatKit and Agents SDK integration expertise.

**When to Use:**
- Phase III (AI Chatbot)
- Implementing chat interface
- Integrating OpenAI Agents SDK
- Fixing LiteLLM/Gemini ID collisions

---

## Skills

Skills are focused, reusable expertise modules for specific technologies or patterns.

### 1. **FastAPI SQLModel Neon Skill** (New)
**Location:** `.claude/skills/fastapi-sqlmodel-neon/`

**Purpose:** Building RESTful APIs with FastAPI, SQLModel ORM, and Neon Serverless PostgreSQL.

**Key Features:**
- Complete FastAPI project structure
- SQLModel database models
- Neon PostgreSQL connection handling
- CRUD endpoint implementations
- JWT authentication integration
- Pydantic schemas for validation
- Error handling patterns

**Use Cases:**
- Phase II: Full-stack web app backend
- Phase III: Chat API endpoints
- Phase V: Advanced features backend

---

### 2. **Next.js App Router Skill** (New)
**Location:** `.claude/skills/nextjs-app-router/`

**Purpose:** Modern Next.js 16+ applications using App Router, Server Components, and TypeScript.

**Key Features:**
- App Router project structure
- Server vs Client Components
- API client with JWT integration
- Better Auth frontend integration
- Task management UI components
- Tailwind CSS styling patterns
- TypeScript type definitions

**Use Cases:**
- Phase II: Full-stack web app frontend
- Phase III: ChatKit integration
- Phase V: Advanced features UI

---

### 3. **MCP Server Tools Skill** (New)
**Location:** `.claude/skills/mcp-server-tools/`

**Purpose:** Building Model Context Protocol servers with tool definitions for AI agents.

**Key Features:**
- Official MCP SDK (Python) implementation
- Tool schema design with Pydantic
- 5 required tools: add_task, list_tasks, complete_task, delete_task, update_task
- OpenAI Agents SDK integration
- Stateless tool design (database-backed)
- Natural language command handling

**Use Cases:**
- Phase III: AI Chatbot with MCP tools
- Natural language task management
- Agent-based interactions

---

### 4. **BetterAuth Integration Skill** (Existing - Keep)
**Location:** `.claude/skills/betterauth-integration/`

**Purpose:** Better Auth setup and configuration.

---

### 5. **MCP Builder Skill** (Existing - Keep)
**Location:** `.claude/skills/mcp-builder/`

**Purpose:** General MCP server creation guidance.

---

### 6. **Frontend Design Skill** (Existing - Keep)
**Location:** `.claude/skills/frontend-design/`

**Purpose:** Production-grade frontend design patterns.

---

### 7. **Skill Creator Skill** (Existing - Keep)
**Location:** `.claude/skills/skill-creator/`

**Purpose:** Creating new Claude Code skills.

---

### 8. **Doc Co-authoring Skill** (Existing - Keep)
**Location:** `.claude/skills/doc-coauthoring/`

**Purpose:** Structured documentation workflow.

---

### 9. **Web Artifacts Builder Skill** (Existing - Keep)
**Location:** `.claude/skills/web-artifacts-builder/`

**Purpose:** Complex React artifacts with shadcn/ui.

---

### 10. **WebApp Testing Skill** (Existing - Keep)
**Location:** `.claude/skills/webapp-testing/`

**Purpose:** Playwright-based frontend testing.

---

## Phase-by-Phase Agent/Skill Usage Guide

### Phase I: Python Console App
**Primary Resources:**
- Spec-Driven Architect Agent (workflow orchestration)
- SpecKit Plus commands (/sp.specify, /sp.plan, /sp.tasks, /sp.implement)

**Skills Needed:**
- Python basics
- CLI interface design
- In-memory data structures

---

### Phase II: Full-Stack Web Application
**Primary Resources:**
- Spec-Driven Architect Agent (workflow)
- BetterAuth Subagent (authentication)
- Next.js App Router Skill (frontend)
- FastAPI SQLModel Neon Skill (backend)

**Key Integration:**
- JWT tokens connecting frontend and backend
- Neon Serverless PostgreSQL
- RESTful API design

---

### Phase III: AI Chatbot
**Primary Resources:**
- Spec-Driven Architect Agent (workflow)
- ChatKit Expert Agent (chat interface)
- MCP Server Tools Skill (AI tools)
- BetterAuth Subagent (user authentication)
- FastAPI SQLModel Neon Skill (conversation storage)

**Key Integration:**
- OpenAI Agents SDK + MCP tools
- Stateless chat endpoint
- Natural language processing

---

### Phase IV: Local Kubernetes (Minikube)
**Primary Resources:**
- Spec-Driven Architect Agent (workflow)
- Kubernetes Deployment Agent (containerization and deployment)

**Skills Needed:**
- Docker containerization
- Helm chart creation
- kubectl-ai and kagent usage
- Docker AI (Gordon) integration

---

### Phase V: Advanced Cloud Deployment
**Primary Resources:**
- Spec-Driven Architect Agent (workflow)
- Kubernetes Deployment Agent (cloud deployment)
- FastAPI SQLModel Neon Skill (advanced features backend)
- Next.js App Router Skill (advanced features frontend)

**Key Technologies:**
- Kafka (Redpanda Cloud or Strimzi)
- Dapr (Pub/Sub, State, Jobs, Secrets)
- Cloud Kubernetes (DOKS/GKE/AKS/OKE)
- Event-driven architecture

---

## How to Use This Structure

### 1. Starting a New Feature
```bash
# 1. Invoke Spec-Driven Architect Agent
# 2. Follow SDD workflow:
#    - /sp.specify (write requirements)
#    - /sp.plan (design architecture)
#    - /sp.tasks (break into tasks)
#    - /sp.implement (generate code)
# 3. Use relevant skills during implementation
# 4. Create PHR after completion: /sp.phr
# 5. Document significant decisions: /sp.adr
```

### 2. Phase-Specific Work
- **Phase I-II:** Focus on Spec-Driven Architect + FastAPI/Next.js skills
- **Phase III:** Add ChatKit Expert + MCP Server Tools skill
- **Phase IV-V:** Heavily use Kubernetes Deployment Agent

### 3. Authentication Work
- Always use BetterAuth Subagent for auth-related tasks
- Ensure JWT secrets are consistent across frontend/backend
- Follow user isolation patterns in all API endpoints

### 4. Deployment Work
- Use Kubernetes Deployment Agent as primary guide
- Start with Minikube (Phase IV)
- Progress to cloud (Phase V)
- Leverage AIOps tools (kubectl-ai, kagent, Gordon)

---

## Bonus Points Opportunities

### Reusable Intelligence (+200 points)
**How to Achieve:**
- Create custom Claude Code subagents for repeated patterns
- Build Agent Skills for deployment blueprints
- Document reusable workflows in .claude/

**Suggested Areas:**
- Cloud-native deployment blueprints
- MCP tool templates
- Testing automation patterns

---

### Cloud-Native Blueprints (+200 points)
**How to Achieve:**
- Create Agent Skills for Kubernetes deployment patterns
- Build reusable Helm chart templates
- Document Dapr integration patterns
- Create spec-driven infrastructure automation

**Reference:**
- [Is Spec-Driven Development Key for Infrastructure Automation?](https://thenewstack.io/is-spec-driven-development-key-for-infrastructure-automation/)

---

## Quick Reference

### Invoke an Agent
```bash
# In Claude Code, reference the agent
@.claude/agents/spec-driven-architect/AGENT.md

# Or use Task tool with subagent_type parameter
```

### Use a Skill
```bash
# Reference the skill in your prompt
@.claude/skills/fastapi-sqlmodel-neon/SKILL.md

# Or use the Skill tool
```

### Run Slash Commands
```bash
/sp.specify      # Create specification
/sp.plan         # Generate plan
/sp.tasks        # Break into tasks
/sp.implement    # Execute implementation
/sp.phr          # Create Prompt History Record
/sp.adr          # Document Architecture Decision
/sp.analyze      # Cross-artifact consistency check
/sp.clarify      # Identify underspecified areas
```

---

## File Organization

```
.claude/
├── agents/
│   ├── spec-driven-architect/      # NEW: SDD workflow orchestration
│   ├── kubernetes-deploy-agent/    # NEW: K8s and cloud deployment
│   ├── betterauth-subagent/        # UPDATED: JWT authentication
│   └── chatkit-expert-agent/       # EXISTING: ChatKit integration
├── skills/
│   ├── fastapi-sqlmodel-neon/      # NEW: Backend API development
│   ├── nextjs-app-router/          # NEW: Frontend development
│   ├── mcp-server-tools/           # NEW: MCP server creation
│   ├── betterauth-integration/     # EXISTING: Auth setup
│   ├── mcp-builder/                # EXISTING: General MCP
│   ├── frontend-design/            # EXISTING: Design patterns
│   ├── skill-creator/              # EXISTING: Create skills
│   ├── doc-coauthoring/            # EXISTING: Documentation
│   ├── web-artifacts-builder/      # EXISTING: React artifacts
│   └── webapp-testing/             # EXISTING: Testing
└── commands/
    ├── sp.specify.md
    ├── sp.plan.md
    ├── sp.tasks.md
    ├── sp.implement.md
    ├── sp.phr.md
    ├── sp.adr.md
    └── ... (other SpecKit Plus commands)
```

---

## Success Metrics

Your agents and skills are working well when:
- ✅ Specs are written before code
- ✅ Tasks map back to plans and specs
- ✅ Code references task IDs
- ✅ PHRs are created after implementation
- ✅ ADRs document significant decisions
- ✅ Deployments follow cloud-native patterns
- ✅ Authentication is secure and consistent
- ✅ MCP tools work seamlessly with AI agents

---

## Next Steps

1. **Read this overview** to understand agent/skill organization
2. **Review individual agent files** for detailed capabilities
3. **Start with Spec-Driven Architect Agent** for workflow guidance
4. **Use phase-specific agents/skills** as you progress through hackathon
5. **Create custom agents/skills** for bonus points (reusable intelligence)

**Good luck with the project! 🚀**
