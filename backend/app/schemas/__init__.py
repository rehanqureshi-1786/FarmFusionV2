from .user import UserBase, UserCreate, UserResponse, Token
from .semantic_frame import (
    CanonicalIntent,
    CapabilityType,
    RequiredInput,
    ActionIntent,
    NavigationDestination,
    ANDROID_ROUTE_MAP,
    ConfidenceSet,
    SoilValues,
    FarmLocation,
    EntitySet,
    UserContext,
    ConversationContext,
    FarmerRequest,
    SemanticFrame,
    NavigationAction,
    CallingAction,
    ToolInvocation,
    ToolResultReference,
    ResponseEnvelope,
)


def __getattr__(name: str):
    # F7 orchestration schemas are loaded lazily to break the import cycle:
    # planner/schemas.py -> app.schemas.semantic_frame (package __init__)
    #   -> orchestration.py -> planner/schemas.py (partially initialized).
    if name in ("ObjectiveStatus", "ReplanReason", "OrchestrationState", "ExecutionTrace"):
        from . import orchestration as _orch
        return getattr(_orch, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

