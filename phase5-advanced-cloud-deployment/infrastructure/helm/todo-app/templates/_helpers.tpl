{{/*
Expand the name of the chart.
*/}}
{{- define "todoboard.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todoboard.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todoboard.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todoboard.labels" -}}
helm.sh/chart: {{ include "todoboard.chart" . }}
{{ include "todoboard.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todoboard.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todoboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todoboard.backend.labels" -}}
helm.sh/chart: {{ include "todoboard.chart" . }}
{{ include "todoboard.backend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: backend
{{- end }}

{{- define "todoboard.backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todoboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todoboard.frontend.labels" -}}
helm.sh/chart: {{ include "todoboard.chart" . }}
{{ include "todoboard.frontend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: frontend
{{- end }}

{{- define "todoboard.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todoboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Notification Service labels
*/}}
{{- define "todoboard.notificationService.labels" -}}
helm.sh/chart: {{ include "todoboard.chart" . }}
{{ include "todoboard.notificationService.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: notification-service
{{- end }}

{{- define "todoboard.notificationService.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todoboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: notification-service
{{- end }}

{{/*
Recurring Task Service labels
*/}}
{{- define "todoboard.recurringTaskService.labels" -}}
helm.sh/chart: {{ include "todoboard.chart" . }}
{{ include "todoboard.recurringTaskService.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: recurring-task-service
{{- end }}

{{- define "todoboard.recurringTaskService.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todoboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: recurring-task-service
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "todoboard.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "todoboard.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend image
*/}}
{{- define "todoboard.backend.image" -}}
{{- if .Values.global.registry }}
{{- printf "%s/%s:%s" .Values.global.registry .Values.backend.image.repository (.Values.backend.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.backend.image.repository (.Values.backend.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}

{{/*
Frontend image
*/}}
{{- define "todoboard.frontend.image" -}}
{{- if .Values.global.registry }}
{{- printf "%s/%s:%s" .Values.global.registry .Values.frontend.image.repository (.Values.frontend.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.frontend.image.repository (.Values.frontend.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}

{{/*
Notification Service image
*/}}
{{- define "todoboard.notificationService.image" -}}
{{- if .Values.global.registry }}
{{- printf "%s/%s:%s" .Values.global.registry .Values.notificationService.image.repository (.Values.notificationService.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.notificationService.image.repository (.Values.notificationService.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}

{{/*
Recurring Task Service image
*/}}
{{- define "todoboard.recurringTaskService.image" -}}
{{- if .Values.global.registry }}
{{- printf "%s/%s:%s" .Values.global.registry .Values.recurringTaskService.image.repository (.Values.recurringTaskService.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.recurringTaskService.image.repository (.Values.recurringTaskService.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}

{{/*
Audit Service labels
*/}}
{{- define "todoboard.auditService.labels" -}}
helm.sh/chart: {{ include "todoboard.chart" . }}
{{ include "todoboard.auditService.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: audit-service
{{- end }}

{{- define "todoboard.auditService.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todoboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: audit-service
{{- end }}

{{/*
Audit Service image
*/}}
{{- define "todoboard.auditService.image" -}}
{{- if .Values.global.registry }}
{{- printf "%s/%s:%s" .Values.global.registry .Values.auditService.image.repository (.Values.auditService.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.auditService.image.repository (.Values.auditService.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}
