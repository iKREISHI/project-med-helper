import os
from .openrouter import OpenRouterProvider
from .gigachat   import GigaChatProvider
from .ollama     import OllamaProvider
from .llmstudio import LMStudioProvider

_PROVIDERS = {
    "openrouter": OpenRouterProvider,
    "gigachat":   GigaChatProvider,
    "ollama":     OllamaProvider,
    "llmstudio":  LMStudioProvider,
}

# читаем однажды при старте приложения;
# .env можно загружать через python-dotenv, django-environ и т.д.
_DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "gigachat").lower()

if _DEFAULT_PROVIDER not in _PROVIDERS:
    raise RuntimeError(f"LLM_PROVIDER «{_DEFAULT_PROVIDER}» не поддерживается: "
                       f"должен быть один из {', '.join(_PROVIDERS)}")

def get_provider(**kw):
    """
    Возвращает singleton-экземпляр выбранного в ENV провайдера.
    Доп. параметры (model=…, system_prompt=…) можно передать вручную.
    """
    ProviderCls = _PROVIDERS[_DEFAULT_PROVIDER]
    # Кэшируем экземпляр, чтобы не создавать клиента SDK на каждый вызов
    if not hasattr(get_provider, "_instance"):
        get_provider._instance = ProviderCls(**kw)
    return get_provider._instance
