from dataclasses import dataclass
from typing import Type


@dataclass
class ProcessSchemaModel:
    """Process Schema State Machine Input model

    Selection of important keys used across logging and tracing

    Parameters
    ----------
    schema_id: str
        Unique schema identifier, by default "UNDEFINED"
    schema_description: str
        Unique schema description, by default "UNDEFINED"
    schema_version: str
        Unique schema version, by default "UNDEFINED"
    schema_definition: str
        Unique schema definition, by default "UNDEFINED"
    created_at: str
        Unique schema creation date, by default "UNDEFINED"
    updated_at: str
        Unique schema update date, by default "UNDEFINED"
    number_of_tokens: str
        Unique schema number of tokens, by default "UNDEFINED"
    state_machine_execution_id: str
        Unique process schema state machine execution identifier, by default "UNDEFINED"
    """

    schema_id: str
    schema_description: str
    schema_version: str
    schema_definition: str
    created_at: str
    updated_at: str
    number_of_tokens: str
    state_machine_execution_id: str


ProcessSchemaState = Type[ProcessSchemaModel]
