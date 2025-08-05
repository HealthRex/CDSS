from pydantic import BaseModel, Field
from typing import List, Optional

class SubdomainLabel(BaseModel):
    subdomain: str
    yes: bool
    rationale: Optional[str]
    confidence: float

class ErrorCodeLabel(BaseModel):
    subdomain: str
    error_code: str
    yes: bool
    rationale: Optional[str]
    confidence: float


class ErrorIdentifierOutput(BaseModel):
    index: int
    patient_message: str
    llm_response: str
    patient_info: str
    clinical_notes: str
    previous_messages: str
    retrieved_pairs: Optional[str] = None
    error_present: bool
    error_summary: Optional[str]  # e.g., "Omitted new diagnosis"
    reasoning: Optional[str]      # e.g., "The response failed to mention a key clinical fact"


# class ErrorLabelerOutput(BaseModel):
#     index: int
#     domain: str
#     # error_present: bool
#     error_summary: Optional[str]
#     subdomains: List[SubdomainLabel]
#     error_codes: List[ErrorCodeLabel]
#     no_matching_subdomain: bool = Field(default=False)
#     no_matching_error_code: bool = Field(default=False)

class ErrorCodeLabel(BaseModel):
    error_code: str
    yes: bool
    rationale: Optional[str]
    confidence: float

class SubdomainLabel(BaseModel):
    subdomain: str
    yes: bool
    rationale: Optional[str]
    confidence: float
    error_codes: List[ErrorCodeLabel]

class ErrorLabelerOutput(BaseModel):
    index: int
    domain: str
    error_summary: Optional[str]
    subdomains: List[SubdomainLabel]
