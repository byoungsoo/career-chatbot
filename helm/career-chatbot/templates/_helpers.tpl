{{- define "career-chatbot.fullname" -}}
{{ .Release.Name }}
{{- end }}

{{- define "career-chatbot.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
