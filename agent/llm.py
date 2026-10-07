"""One place to switch models. Every node calls get_llm() and never imports a provider directly."""
from langchain_core.language_models.chat_models import BaseChatModel

from agent import config


def get_llm() -> BaseChatModel | None:
    """Return the chat model for MODEL_PROVIDER, or None in mock mode."""
    if config.MODEL_PROVIDER == "mock":
        return None
    if config.MODEL_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        # The free tier allows about 15 requests a minute, so retry with backoff on 429s.
        return ChatGoogleGenerativeAI(model=config.GEMINI_MODEL, temperature=0, max_retries=4)
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=config.CLAUDE_MODEL, max_retries=4, max_tokens=4096)
