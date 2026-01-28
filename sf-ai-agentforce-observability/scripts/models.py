"""
Pydantic models and PyArrow schemas for Session Tracing Data Model (STDM).

Provides type-safe models for:
- AIAgentSession (Session level)
- AIAgentInteraction (Turn/Session end)
- AIAgentInteractionStep (LLM/Action steps)
- AIAgentMoment (Messages)

Usage:
    from models import AIAgentSession, SCHEMAS

    # Validate API response
    session = AIAgentSession(**api_record)

    # Get PyArrow schema for Parquet writing
    schema = SCHEMAS["sessions"]
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

import pyarrow as pa


# ============================================================================
# Pydantic Models
# ============================================================================

class AIAgentSession(BaseModel):
    """
    Session-level record from ssot__AIAgentSession__dlm.

    Represents a complete agent conversation from start to finish.
    Contains metadata about the session but not the actual messages.

    Attributes:
        id: Unique session identifier
        agent_api_name: API name of the agent handling this session
        start_timestamp: When the session started
        end_timestamp: When the session ended (null if ongoing)
        end_type: How the session ended (Completed, Abandoned, Escalated, etc.)
        messaging_session_id: Related messaging session (if applicable)
        organization_id: Salesforce org ID
    """

    id: str = Field(alias="ssot__Id__c")
    agent_api_name: Optional[str] = Field(default=None, alias="ssot__AIAgentApiName__c")
    start_timestamp: Optional[str] = Field(default=None, alias="ssot__StartTimestamp__c")
    end_timestamp: Optional[str] = Field(default=None, alias="ssot__EndTimestamp__c")
    end_type: Optional[str] = Field(default=None, alias="ssot__AIAgentSessionEndType__c")
    messaging_session_id: Optional[str] = Field(default=None, alias="ssot__RelatedMessagingSessionId__c")
    organization_id: Optional[str] = Field(default=None, alias="ssot__OrganizationId__c")

    class Config:
        populate_by_name = True  # Allow both alias and field name


class AIAgentInteraction(BaseModel):
    """
    Turn-level record from ssot__AIAgentInteraction__dlm.

    Represents a single turn in the conversation (user input → agent response)
    or a session end event.

    Attributes:
        id: Unique interaction identifier
        session_id: Foreign key to parent session
        interaction_type: Type of interaction (TURN or SESSION_END)
        topic_api_name: Which topic handled this turn
        start_timestamp: When this turn started
        end_timestamp: When this turn completed
    """

    id: str = Field(alias="ssot__Id__c")
    session_id: str = Field(alias="ssot__aiAgentSessionId__c")
    interaction_type: Optional[str] = Field(default=None, alias="ssot__InteractionType__c")
    topic_api_name: Optional[str] = Field(default=None, alias="ssot__TopicApiName__c")
    start_timestamp: Optional[str] = Field(default=None, alias="ssot__StartTimestamp__c")
    end_timestamp: Optional[str] = Field(default=None, alias="ssot__EndTimestamp__c")

    class Config:
        populate_by_name = True


class AIAgentInteractionStep(BaseModel):
    """
    Step-level record from ssot__AIAgentInteractionStep__dlm.

    Represents an individual step within a turn, either:
    - LLM_STEP: Language model reasoning/generation
    - ACTION_STEP: Flow/Apex action execution

    Attributes:
        id: Unique step identifier
        interaction_id: Foreign key to parent interaction
        step_type: Type of step (LLM_STEP or ACTION_STEP)
        name: Action name or step description
        input_value: Input to this step (may be JSON)
        output_value: Output from this step (may be JSON)
        pre_step_variables: Variable state before step
        post_step_variables: Variable state after step
        generation_id: LLM generation identifier
    """

    id: str = Field(alias="ssot__Id__c")
    interaction_id: str = Field(alias="ssot__AIAgentInteractionId__c")
    step_type: Optional[str] = Field(default=None, alias="ssot__AIAgentInteractionStepType__c")
    name: Optional[str] = Field(default=None, alias="ssot__Name__c")
    input_value: Optional[str] = Field(default=None, alias="ssot__InputValueText__c")
    output_value: Optional[str] = Field(default=None, alias="ssot__OutputValueText__c")
    pre_step_variables: Optional[str] = Field(default=None, alias="ssot__PreStepVariableText__c")
    post_step_variables: Optional[str] = Field(default=None, alias="ssot__PostStepVariableText__c")
    generation_id: Optional[str] = Field(default=None, alias="ssot__GenerationId__c")

    class Config:
        populate_by_name = True


class AIAgentMoment(BaseModel):
    """
    Message-level record from ssot__AIAgentMoment__dlm.

    Represents a single message in the conversation (either user input
    or agent output).

    Attributes:
        id: Unique message identifier
        interaction_id: Foreign key to parent interaction
        content: Message text content
        message_type: Type of message (INPUT or OUTPUT)
        sent_timestamp: When the message was sent
    """

    id: str = Field(alias="ssot__Id__c")
    interaction_id: str = Field(alias="ssot__AIAgentInteractionId__c")
    content: Optional[str] = Field(default=None, alias="ssot__ContentText__c")
    message_type: Optional[str] = Field(default=None, alias="ssot__AIAgentInteractionMessageType__c")
    sent_timestamp: Optional[str] = Field(default=None, alias="ssot__MessageSentTimestamp__c")

    class Config:
        populate_by_name = True


# ============================================================================
# PyArrow Schemas
# ============================================================================

SESSION_SCHEMA = pa.schema([
    pa.field("ssot__Id__c", pa.string(), nullable=False),
    pa.field("ssot__AIAgentApiName__c", pa.string(), nullable=True),
    pa.field("ssot__StartTimestamp__c", pa.string(), nullable=True),
    pa.field("ssot__EndTimestamp__c", pa.string(), nullable=True),
    pa.field("ssot__AIAgentSessionEndType__c", pa.string(), nullable=True),
    pa.field("ssot__RelatedMessagingSessionId__c", pa.string(), nullable=True),
    pa.field("ssot__OrganizationId__c", pa.string(), nullable=True),
])

INTERACTION_SCHEMA = pa.schema([
    pa.field("ssot__Id__c", pa.string(), nullable=False),
    pa.field("ssot__aiAgentSessionId__c", pa.string(), nullable=False),
    pa.field("ssot__InteractionType__c", pa.string(), nullable=True),
    pa.field("ssot__TopicApiName__c", pa.string(), nullable=True),
    pa.field("ssot__StartTimestamp__c", pa.string(), nullable=True),
    pa.field("ssot__EndTimestamp__c", pa.string(), nullable=True),
])

STEP_SCHEMA = pa.schema([
    pa.field("ssot__Id__c", pa.string(), nullable=False),
    pa.field("ssot__AIAgentInteractionId__c", pa.string(), nullable=False),
    pa.field("ssot__AIAgentInteractionStepType__c", pa.string(), nullable=True),
    pa.field("ssot__Name__c", pa.string(), nullable=True),
    pa.field("ssot__InputValueText__c", pa.string(), nullable=True),
    pa.field("ssot__OutputValueText__c", pa.string(), nullable=True),
    pa.field("ssot__PreStepVariableText__c", pa.string(), nullable=True),
    pa.field("ssot__PostStepVariableText__c", pa.string(), nullable=True),
    pa.field("ssot__GenerationId__c", pa.string(), nullable=True),
])

MESSAGE_SCHEMA = pa.schema([
    pa.field("ssot__Id__c", pa.string(), nullable=False),
    pa.field("ssot__AIAgentInteractionId__c", pa.string(), nullable=False),
    pa.field("ssot__ContentText__c", pa.string(), nullable=True),
    pa.field("ssot__AIAgentInteractionMessageType__c", pa.string(), nullable=True),
    pa.field("ssot__MessageSentTimestamp__c", pa.string(), nullable=True),
])


# Schema registry for easy access
SCHEMAS = {
    "sessions": SESSION_SCHEMA,
    "interactions": INTERACTION_SCHEMA,
    "steps": STEP_SCHEMA,
    "messages": MESSAGE_SCHEMA,
}

# DMO name mapping
DMO_NAMES = {
    "sessions": "ssot__AIAgentSession__dlm",
    "interactions": "ssot__AIAgentInteraction__dlm",
    "steps": "ssot__AIAgentInteractionStep__dlm",
    "messages": "ssot__AIAgentMoment__dlm",
}

# Model class mapping
MODELS = {
    "sessions": AIAgentSession,
    "interactions": AIAgentInteraction,
    "steps": AIAgentInteractionStep,
    "messages": AIAgentMoment,
}


# ============================================================================
# Utility Functions
# ============================================================================

def validate_record(record: dict, entity_type: str) -> BaseModel:
    """
    Validate a record against its Pydantic model.

    Args:
        record: Raw record dictionary from API
        entity_type: One of 'sessions', 'interactions', 'steps', 'messages'

    Returns:
        Validated Pydantic model instance

    Raises:
        ValueError: If entity_type is invalid
        ValidationError: If record fails validation
    """
    if entity_type not in MODELS:
        raise ValueError(f"Unknown entity type: {entity_type}")

    model_class = MODELS[entity_type]
    return model_class(**record)


def get_field_mapping(entity_type: str) -> dict:
    """
    Get field alias mapping for an entity type.

    Args:
        entity_type: One of 'sessions', 'interactions', 'steps', 'messages'

    Returns:
        Dict mapping alias (API name) to field name (Python name)
    """
    if entity_type not in MODELS:
        raise ValueError(f"Unknown entity type: {entity_type}")

    model_class = MODELS[entity_type]
    mapping = {}

    for field_name, field_info in model_class.model_fields.items():
        alias = field_info.alias or field_name
        mapping[alias] = field_name

    return mapping


def get_required_fields(entity_type: str) -> List[str]:
    """
    Get list of required field API names for an entity type.

    Args:
        entity_type: One of 'sessions', 'interactions', 'steps', 'messages'

    Returns:
        List of required field API names
    """
    if entity_type not in SCHEMAS:
        raise ValueError(f"Unknown entity type: {entity_type}")

    schema = SCHEMAS[entity_type]
    return [field.name for field in schema if not field.nullable]


def build_select_clause(entity_type: str) -> str:
    """
    Build SELECT clause with all fields for an entity type.

    Args:
        entity_type: One of 'sessions', 'interactions', 'steps', 'messages'

    Returns:
        SQL SELECT clause string (without SELECT keyword)
    """
    if entity_type not in SCHEMAS:
        raise ValueError(f"Unknown entity type: {entity_type}")

    schema = SCHEMAS[entity_type]
    fields = [field.name for field in schema]
    return ", ".join(fields)
