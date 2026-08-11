import json
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from app.agents.coupon_kock_agent import root_agent
from app.core.config import settings
from app.models.schemas import AgentRecommendationRequest, AgentRecommendationResponse


class AgentExecutionError(RuntimeError):
    """Raised when ADK cannot produce a final response."""


class CouponKockAdkService:
    def __init__(self) -> None:
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name=settings.adk_app_name,
            agent=root_agent,
            session_service=self.session_service,
        )

    async def run(self, request: AgentRecommendationRequest) -> AgentRecommendationResponse:
        request_id = str(uuid4())
        session_id = f"recommendation-{uuid4()}"
        await self.session_service.create_session(
            app_name=settings.adk_app_name,
            user_id=request.user_id,
            session_id=session_id,
            state={"request_id": request_id},
        )

        prompt = json.dumps(
            {
                "user_id": request.user_id,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "purchase_amount": request.purchase_amount,
                "store_id": request.store_id or "",
                "card_product": request.card_product or settings.demo_card_product,
            },
            ensure_ascii=False,
        )
        answer = ""
        tool_trace: list[str] = []
        try:
            async for event in self.runner.run_async(
                user_id=request.user_id,
                session_id=session_id,
                new_message=Content(role="user", parts=[Part(text=prompt)]),
            ):
                for part in event.content.parts if event.content and event.content.parts else []:
                    if part.function_call:
                        tool_trace.append(f"{part.function_call.name}:called")
                    if part.function_response:
                        tool_trace.append(f"{part.function_response.name}:completed")
                if event.is_final_response() and event.content and event.content.parts:
                    answer = "".join(part.text or "" for part in event.content.parts).strip()
        except Exception as error:
            raise AgentExecutionError("ADK 에이전트 실행에 실패했습니다.") from error
        finally:
            await self.session_service.delete_session(
                app_name=settings.adk_app_name,
                user_id=request.user_id,
                session_id=session_id,
            )

        if not answer:
            raise AgentExecutionError("ADK 에이전트가 최종 응답을 생성하지 못했습니다.")
        return AgentRecommendationResponse(
            request_id=request_id,
            session_id=session_id,
            agent_name=root_agent.name,
            model=settings.gemini_model,
            answer=answer,
            tool_trace=tool_trace,
        )


agent_service = CouponKockAdkService()
