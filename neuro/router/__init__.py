"""
Neuro Router - Smart API routing across multiple providers
Provides intelligent model selection and fallback handling
"""

from neuro.router.smart_router import (
    SmartRouter,
    Provider,
    ProviderConfig,
    RouterStats,
    complete,
    health_check,
    get_stats,
    get_provider_keys,
    has_provider,
    available_providers,
    reload_keys,
    _router,
)

__all__ = [
    "SmartRouter",
    "Provider",
    "ProviderConfig",
    "RouterStats", 
    "complete",
    "health_check",
    "get_stats",
    "get_provider_keys",
    "has_provider",
    "available_providers",
    "reload_keys",
    "_router",
]