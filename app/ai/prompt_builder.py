import json

from app.core.enums import IntentType, LeadStage

PROMPT_VERSION = "v1"


def build_system_prompt() -> str:
    intents = [intent.value for intent in IntentType]
    stages = [stage.value for stage in LeadStage]

    return (
        "Ты AI Sales Manager. Отвечай только на русском языке. "
        "Твоя задача: помочь клиенту выбрать услугу, не выдумывать факты, цены и услуги. "
        "Используй только предоставленный каталог услуг и историю диалога. "
        "Если данных недостаточно, честно скажи об этом и задай уточняющий вопрос. "
        "Ответ верни строго JSON-объектом без markdown, полями: "
        "intent, stage, reply_text, confidence. "
        f"Допустимые intent: {intents}. "
        f"Допустимые stage: {stages}. "
        "confidence должен быть числом 0..1."
    )


def build_user_prompt(message_text: str, current_stage: str, history: list[dict], services: list[dict]) -> str:
    payload = {
        "current_stage": current_stage,
        "incoming_message": message_text,
        "history": history,
        "services": services,
        "requirements": {
            "no_hallucinations": True,
            "language": "ru",
            "concise": True,
        },
    }
    return json.dumps(payload, ensure_ascii=False)


def build_first_touch_intro(service_names: list[str]) -> str:
    listed = ", ".join(service_names[:4]) if service_names else "AI-решения для бизнеса"
    return (
        "Здравствуйте. Я AI Sales Manager и помогаю подобрать и оформить AI-услугу под вашу задачу. "
        f"Сейчас у нас доступны: {listed}. "
        "Чтобы предложить лучший вариант, кратко опишите ваш бизнес-процесс, цель и желаемый результат."
    )
