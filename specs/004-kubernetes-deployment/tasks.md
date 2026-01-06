# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-kubernetes-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/, quickstart.md

**Tests**: No test tasks included - feature spec does not request testing

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (k8s Directory Structure)

**Purpose**: Create the Kubernetes directory structure and Helm chart scaffolding

- [X] T001 Create k8s/charts/todoboard/ directory structure
- [X] T002 [P] Create Chart.yaml with todoboard chart metadata in k8s/charts/todoboard/Chart.yaml
- [X] T003 [P] Create _helpers.tpl template functions in k8s/charts/todoboard/templates/_helpers.tpl
- [X] T004 Create NOTES.txt with Helm install instructions in k8s/charts/todoboard/templates/NOTES.txt

---

## Phase 2: Foundational (Kubernetes Config Resources)

**Purpose**: Create ConfigMap, Secret, and PVC templates - required by all deployments

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create configmap.yaml template in k8s/charts/todoboard/templates/configmap.yaml
- [X] T006 [P] Create secret.yaml template in k8s/charts/todoboard/templates/secret.yaml
- [X] T007 [P] Create pvc.yaml template for PostgreSQL data in k8s/charts/todoboard/templates/pvc.yaml

**Checkpoint**: Foundational resources ready - Helm chart development can now begin

---

## Phase 3: User Story 1 - Containerize Applications (Priority: P1) 🎯 MVP

**Goal**: Verify Docker images can be built for Kubernetes deployment

**Independent Test**: Run `eval $(minikube docker-env)` and build images successfully

**Note**: Phase III Dockerfiles should already exist at phase3-todo-ai-chatbot/frontend/Dockerfile and phase3-todo-ai-chatbot/backend/Dockerfile

- [X] T008 [US1] Verify frontend Dockerfile exists at phase3-todo-ai-chatbot/frontend/Dockerfile
- [X] T009 [US1] Verify backend Dockerfile exists at phase3-todo-ai-chatbot/backend/Dockerfile
- [X] T010 [US1] Build frontend Docker image with todoboard-frontend:latest tag
- [X] T011 [US1] Build backend Docker image with todoboard-backend:latest tag
- [X] T012 [US1] Verify both images appear in docker images output

**Checkpoint**: User Story 1 complete - Docker images built successfully

---

## Phase 4: User Story 2 - Create Helm Charts (Priority: P1)

**Goal**: Create all Helm templates for frontend, backend, and PostgreSQL deployments

**Independent Test**: Run `helm template ./k8s/charts/todoboard` and verify valid YAML output

### Frontend Templates

- [X] T013 [P] [US2] Create deployment-frontend.yaml template in k8s/charts/todoboard/templates/deployment-frontend.yaml
- [X] T014 [P] [US2] Create service-frontend.yaml template with LoadBalancer type in k8s/charts/todoboard/templates/service-frontend.yaml

### Backend Templates

- [X] T015 [P] [US2] Create deployment-backend.yaml template in k8s/charts/todoboard/templates/deployment-backend.yaml
- [X] T016 [P] [US2] Create service-backend.yaml template with ClusterIP type in k8s/charts/todoboard/templates/service-backend.yaml

### PostgreSQL Templates

- [X] T017 [P] [US2] Create deployment-postgres.yaml template in k8s/charts/todoboard/templates/deployment-postgres.yaml
- [X] T018 [US2] Create service-postgres.yaml template with ClusterIP type in k8s/charts/todoboard/templates/service-postgres.yaml

### Values Configuration

- [X] T019 [US2] Create values.yaml with default configurations in k8s/charts/todoboard/values.yaml
- [X] T020 [US2] Create values-minikube.yaml with Minikube-specific overrides in k8s/charts/todoboard/values-minikube.yaml

### Validation

- [X] T021 [US2] Run helm template ./k8s/charts/todoboard and verify valid output
- [X] T022 [US2] Run helm lint ./k8s/charts/todoboard and fix any errors

**Checkpoint**: User Story 2 complete - Helm charts render and pass lint

---

## Phase 5: User Story 3 - Deploy to Minikube (Priority: P1)

**Goal**: Deploy the complete stack to Minikube and verify pods are running

**Independent Test**: All pods show Running status after deployment

### Pre-Deployment

- [ ] T023 [US3] Start Minikube cluster with 2 CPUs and 4GB RAM
- [ ] T024 [US3] Create todoboard namespace in Kubernetes
- [ ] T025 [US3] Create todoboard-secrets secret with postgres-password and openai-api-key

### Deployment

- [ ] T026 [US3] Run helm install todoboard ./k8s/charts/todoboard --namespace=todoboard
- [ ] T027 [US3] Wait for frontend pod to reach Ready state
- [ ] T028 [US3] Wait for backend pod to reach Ready state
- [ ] T029 [US3] Wait for postgres pod to reach Ready state

### Verification

- [ ] T030 [US3] Verify all pods show Running status with kubectl get pods -n todoboard
- [ ] T031 [US3] Start minikube tunnel in background
- [ ] T032 [US3] Verify frontend service has external IP assigned
- [ ] T033 [US3] Test backend health endpoint with curl

**Checkpoint**: User Story 3 complete - All pods running and accessible

---

## Phase 6: User Story 4 - Use kubectl-ai for Operations (Priority: P2)

**Goal**: Enable natural language Kubernetes operations

**Independent Test**: kubectl-ai commands execute successfully for common operations

- [X] T034 [US4] Install kubectl-ai CLI tool
- [X] T035 [US4] Test kubectl-ai "scale the frontend to 3 replicas" command
- [X] T036 [US4] Test kubectl-ai "check why pods are not starting" command
- [X] T037 [US4] Test kubectl-ai "show me recent errors in logs" command
- [X] T038 [US4] Create kubectl-ai examples documentation in k8s/charts/todoboard/KUBECTL_AI.md

**Checkpoint**: User Story 4 complete - kubectl-ai commands work for 3+ operations

---

## Phase 7: User Story 5 - Use Kagent for Cluster Management (Priority: P2)

**Goal**: Enable AI-assisted cluster health monitoring and optimization

**Independent Test**: Kagent commands return health reports and optimization suggestions

- [X] T039 [US5] Install Kagent CLI tool
- [X] T040 [US5] Test Kagent "analyze cluster health" command
- [X] T041 [US5] Test Kagent "optimize resource allocation" command
- [X] T042 [US5] Test Kagent "what's my current capacity" command
- [X] T043 [US5] Create Kagent examples documentation in k8s/charts/todoboard/KAGENT.md

**Checkpoint**: User Story 5 complete - Kagent provides health analysis

---

## Phase 8: User Story 6 - Verify Full Stack Functionality (Priority: P1)

**Goal**: Verify complete application functionality through the deployed stack

**Independent Test**: Create task via UI, interact with chatbot, verify persistence

### End-to-End Verification

- [X] T044 [US6] Access frontend URL and verify UI loads
- [X] T045 [US6] Create a new task through the web interface
- [X] T046 [US6] Verify task appears in the task list
- [X] T047 [US6] Send a message to the chatbot and receive AI response
- [X] T048 [US6] Refresh page and verify tasks persist (database connectivity)
- [X] T049 [US6] Test update and delete operations on tasks

**Checkpoint**: User Story 6 complete - Full stack functionality verified

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, optimization, and final validation

- [X] T050 [P] Update QUICK_SETUP.md with Kubernetes deployment instructions
- [X] T051 [P] Create KUBERNETES.md with architecture overview and troubleshooting
- [X] T052 Test Helm rollback capability with helm rollback command
- [X] T053 Verify all quickstart.md commands work as documented
- [X] T054 [P] Document resource usage metrics in k8s/charts/todoboard/RESOURCES.md

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|------------|--------|
| Phase 1: Setup | None | Phase 2 |
| Phase 2: Foundational | Phase 1 | All User Stories |
| Phase 3: US1 Containerize | Phase 2 | US2, US3 |
| Phase 4: US2 Helm Charts | Phase 2 + US1 | US3 |
| Phase 5: US3 Deploy | Phase 2 + US2 | US4, US5, US6 |
| Phase 6: US4 kubectl-ai | Phase 5 | Polish |
| Phase 7: US5 Kagent | Phase 5 | Polish |
| Phase 8: US6 Verify | Phase 5 | Polish |
| Phase 9: Polish | All prior | None |

### User Story Dependencies

| User Story | Can Start After | Dependencies |
|------------|-----------------|--------------|
| US1: Containerize | Phase 2 | None |
| US2: Helm Charts | Phase 2 + US1 | Builds on US1 images |
| US3: Deploy | Phase 2 + US2 | Builds on US2 charts |
| US4: kubectl-ai | Phase 3 | Requires running cluster |
| US5: Kagent | Phase 3 | Requires running cluster |
| US6: Verify | Phase 3 | Requires running cluster |

### Within Each User Story

- Setup tasks (T001-T004) must complete before foundational
- Foundational tasks (T005-T007) must complete before all stories
- US1 (T008-T012): Docker image build order
- US2 (T013-T022): Templates before values, then validation
- US3 (T023-T033): Pre-deployment before deployment, then verification
- US4-US6: Each has independent verification criteria

### Parallel Opportunities

- T001-T004: Setup tasks can run in parallel
- T005-T007: Foundational tasks can run in parallel
- T008-T009: US1 verification tasks can run in parallel
- T013-T018: US2 templates can run in parallel (frontend/backend/postgres pairs)
- T034-T038: US4 tasks can run in parallel
- T039-T043: US5 tasks can run in parallel
- T044-T049: US6 verification tasks can run in parallel
- T050-T051: Polish documentation can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all template creation tasks for US2 together:
Task: "Create deployment-frontend.yaml template"
Task: "Create deployment-backend.yaml template"
Task: "Create deployment-postgres.yaml template"
Task: "Create service-frontend.yaml template"
Task: "Create service-backend.yaml template"
Task: "Create service-postgres.yaml template"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T007)
3. Complete Phase 3: User Story 1 (T008-T012)
4. **STOP and VALIDATE**: Docker images build successfully
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test Docker images → Verify (MVP!)
3. Add User Story 2 → Test Helm templates → Deploy locally
4. Add User Story 3 → Full deployment → Test end-to-end
5. Add User Story 4-5 → AI tools integration
6. Final polish and documentation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Docker images)
   - Developer B: User Story 2 (Helm templates)
   - Developer C: User Story 6 (Verification tests)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
