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
{{ include "todoboard.labels" . }}
app: todoboard-backend
component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todoboard.backend.selectorLabels" -}}
{{ include "todoboard.selectorLabels" . }}
app: todoboard-backend
component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todoboard.frontend.labels" -}}
{{ include "todoboard.labels" . }}
app: todoboard-frontend
component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todoboard.frontend.selectorLabels" -}}
{{ include "todoboard.selectorLabels" . }}
app: todoboard-frontend
component: frontend
{{- end }}

{{/*
PostgreSQL labels
*/}}
{{- define "todoboard.postgresql.labels" -}}
{{ include "todoboard.labels" . }}
app: todoboard-postgres
component: database
{{- end }}

{{/*
PostgreSQL selector labels
*/}}
{{- define "todoboard.postgresql.selectorLabels" -}}
{{ include "todoboard.selectorLabels" . }}
app: todoboard-postgres
component: database
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
{{- $tag := .Values.backend.image.tag | default .Chart.AppVersion }}
{{- printf "%s:%s" .Values.backend.image.repository $tag }}
{{- end }}

{{/*
Frontend image
*/}}
{{- define "todoboard.frontend.image" -}}
{{- $tag := .Values.frontend.image.tag | default .Chart.AppVersion }}
{{- printf "%s:%s" .Values.frontend.image.repository $tag }}
{{- end }}

{{/*
PostgreSQL image
*/}}
{{- define "todoboard.postgresql.image" -}}
{{- printf "%s:%s" .Values.postgresql.image.repository .Values.postgresql.image.tag }}
{{- end }}
