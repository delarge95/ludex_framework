from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

class BaseContract(BaseModel):
    """
    Base class for all data contracts.
    """
    pass

def validate_input(data: Dict[str, Any], schema: Type[T]) -> T:
    """
    Validates input data against a schema before agent execution.
    Raises ValidationError if data is invalid.
    """
    try:
        return schema(**data)
    except ValidationError as e:
        logger.error("input_contract_violation", schema=schema.__name__, error=str(e))
        raise e

def validate_output(data: Dict[str, Any], schema: Type[T]) -> T:
    """
    Validates output data against a schema after agent execution.
    Raises ValidationError if data is invalid.
    """
    try:
        return schema(**data)
    except ValidationError as e:
        logger.error("output_contract_violation", schema=schema.__name__, error=str(e))
        raise e

# Example Contract: Narrative -> Audio
class NarrativeContext(BaseContract):
    tone: str
    themes: list[str]
    key_events: list[str]

# Example Contract: Art -> Audio
class ArtContext(BaseContract):
    art_style: str
    visual_mood: str
