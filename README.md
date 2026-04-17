# Career Chatbot

AI-powered personal career assistant chatbot built with AWS Bedrock and Gradio.

## Prerequisites

### 1. External Secrets Operator (ESO)

클러스터에 ESO와 `ClusterSecretStore`가 설치/구성되어 있어야 합니다. `values.yaml`의 `externalSecret.secretStoreName`이 ClusterSecretStore 이름과 일치해야 합니다.

### 2. AWS Secrets Manager

애플리케이션에서 사용하는 시크릿을 Secrets Manager에 등록합니다.

```bash
aws secretsmanager create-secret \
  --name career-chatbot \
  --secret-string '{"MAILGUN_API_KEY":"<YOUR_API_KEY>"}'
```

### 3. IAM Role (IRSA or Pod Identity)

Pod가 Secrets Manager에 접근할 수 있도록 IAM Role을 생성하고 아래 권한을 부여합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:career-chatbot-*"
    }
  ]
}
```

생성한 IAM Role ARN을 helm 배포 시 `serviceAccount.annotations."eks.amazonaws.com/role-arn"`에 지정합니다.

## Deployment

### Build & Push Image

```bash
docker build -t <ECR_URI>:<TAG> .
docker push <ECR_URI>:<TAG>
```

### Helm Install

```bash
helm upgrade --install career-chatbot ./helm/career-chatbot \
  --namespace bys \
  --set image.repository=<ECR_URI> \
  --set image.tag=<TAG> \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=<IAM_ROLE_ARN>
```

## Local Development

```bash
# 의존성 설치
uv sync

# 실행
uv run python app_bedrock_advanced.py
```

`.env` 파일에 필요한 환경변수를 설정합니다 (`.env` 참고).
