from dotenv import load_dotenv
import logging
import os
from pypdf import PdfReader
import gradio as gr
from strands import Agent
from strands.models import BedrockModel

from tools import record_user_details, record_unknown_question

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

load_dotenv(override=True)


class Me:

    def __init__(self):
        self.name = os.getenv('ASSISTANT_NAME', 'Byoungsoo Ko')
        self.model_id = os.getenv('MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        logger.info(f"Initializing Me: name={self.name}, model={self.model_id}, region={self.region}")

        self.documents = {}
        me_dir = os.getenv('ME_DIR', 'me')
        for filename in sorted(os.listdir(me_dir)):
            filepath = os.path.join(me_dir, filename)
            doc_name = os.path.splitext(filename)[0]
            if filename.endswith('.pdf'):
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                self.documents[doc_name] = text
                logger.info(f"Loaded PDF: {filename} ({len(text)} chars)")
            elif filename.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.documents[doc_name] = f.read()
                logger.info(f"Loaded TXT: {filename}")
        logger.info(f"Documents loaded: {list(self.documents.keys())}")

    def system_prompt(self):
        prompt = (
            f"You are acting as {self.name}. You are answering questions on {self.name}'s website, "
            f"particularly questions related to {self.name}'s career, background, skills and experience. "
            f"Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. "
            f"You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. "
            f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
            f"If you don't know the answer to any question, use your record_unknown_question tool to record the question. "
            f"If the user is engaging in discussion, try to steer them towards getting in touch via email; "
            f"ask for their email and record it using your record_user_details tool."
        )
        for doc_name, content in self.documents.items():
            prompt += f"\n\n## {doc_name}:\n{content}"
        prompt += f"\n\nWith this context, please chat with the user, always staying in character as {self.name}."
        return prompt

    def chat(self, message, history):
        model = BedrockModel(
            model_id=self.model_id,
            region_name=self.region,
        )
        agent = Agent(
            model=model,
            system_prompt=self.system_prompt(),
            tools=[record_user_details, record_unknown_question],
        )

        for msg in history:
            content = msg.get("content") or ""
            if isinstance(content, list):
                content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            agent.messages.append({
                "role": msg["role"],
                "content": [{"text": str(content)}],
            })

        response = agent(message)
        return str(response)


if __name__ == "__main__":
    logger.info("Starting career-chatbot...")
    me = Me()
    logger.info("Me initialized, building Gradio UI...")

    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .header-text {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .info-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    """

    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple",
        neutral_hue="slate",
    )

    with gr.Blocks(title=f"{me.name} - AI Assistant") as demo:

        gr.HTML(f"""
        <div class="header-text">
            <h1>💼 {me.name}</h1>
            <h3>AI-Powered Career Assistant</h3>
            <p>Kubernetes | AWS | DevOps | Cloud Architecture</p>
        </div>
        """)

        with gr.Tabs():

            with gr.Tab("💬 Chat with AI"):
                gr.Markdown(f"""
                <div class="info-box">
                    <strong>👋 환영합니다!</strong><br>
                    저는 {me.name}를 대신하여 질문에 답변하는 AI 어시스턴트입니다.<br>
                    경력, 기술 스택, 프로젝트 경험 등 무엇이든 물어보세요!
                </div>
                """)

                chatbot = gr.Chatbot(
                    height=500,
                    placeholder="👋 안녕하세요! 무엇을 도와드릴까요?",
                    avatar_images=(
                        None,
                        "https://api.dicebear.com/7.x/bottts/svg?seed=Byoungsoo"
                    )
                )

                msg = gr.Textbox(
                    placeholder="메시지를 입력하세요...",
                    container=False,
                    submit_btn="전송 📤",
                )

                gr.ChatInterface(
                    fn=me.chat,
                    chatbot=chatbot,
                    textbox=msg,
                    examples=[
                        "당신의 주요 기술 스택은 무엇인가요?",
                        "Kubernetes 경험에 대해 알려주세요",
                        "AWS 관련 프로젝트가 있나요?",
                        "CI/CD 파이프라인 구축 경험은?",
                        "연락처를 남기고 싶어요"
                    ],
                )

            with gr.Tab("🛠️ Tech Stack"):
                gr.Markdown("""
                ## Technology Stack

                ### ☁️ Cloud & Infrastructure
                - **AWS**: EKS, EC2, S3, Lambda, CloudFormation, IAM
                - **Kubernetes**: Cluster management, Helm, Operators
                - **Docker**: Container orchestration, multi-stage builds

                ### 🔄 DevOps & CI/CD
                - **GitLab CI/CD**: Pipeline design and optimization
                - **Jenkins**: Automation and integration
                - **ArgoCD**: GitOps deployment

                ### 📊 Monitoring & Logging
                - **Prometheus**: Metrics collection
                - **Grafana**: Visualization and dashboards
                - **ELK Stack**: Centralized logging

                ### 💻 Programming & Scripting
                - **Python**: Automation, scripting
                - **Bash**: System administration
                - **YAML/JSON**: Configuration management
                """)

            with gr.Tab("📧 Contact"):
                gr.Markdown(f"""
                ## 📬 Let's Connect!

                <div class="info-box">

                ### 💡 Interested in collaboration?

                채팅 탭으로 돌아가서 다음과 같이 말씀해주세요:
                - "연락처를 남기고 싶어요"
                - "이메일을 남기겠습니다"
                - "협업 문의드립니다"

                AI 어시스턴트가 정보를 수집하고 {me.name}에게 즉시 알림을 보냅니다! 📧

                </div>

                ### 🔔 Real-time Notifications

                이 시스템은 다음과 같은 기능을 제공합니다:
                - ✅ 실시간 이메일 알림 (Mailgun)
                - ✅ 연락처 자동 기록
                - ✅ 질문 추적 및 분석
                - ✅ 24/7 자동 응답
                """)

        gr.HTML(f"""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <p style="color: #666; margin: 5px;">
                🤖 <strong>Powered by AWS Bedrock</strong>
            </p>
            <p style="color: #666; margin: 5px;">
                💡 Built with <strong>Gradio</strong> |
                📧 Notifications via <strong>Mailgun</strong>
            </p>
            <p style="color: #999; font-size: 0.9em; margin-top: 10px;">
                © 2026 {me.name} | AI Career Assistant
            </p>
        </div>
        """)

    logger.info("Launching Gradio on 0.0.0.0:7860...")
    demo.launch(theme=theme, css=custom_css, server_name="0.0.0.0", server_port=7860)
