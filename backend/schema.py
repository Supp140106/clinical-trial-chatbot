from pydantic import BaseModel, Field
from typing import List, Optional

class Trial(BaseModel):
    trial_id: int
    trial_code: str
    trial_title: str
    cancer_type: str
    trial_phase: str
    recruitment_status: str
    city: str
    province: str
    country: str
    latitude: float
    longitude: float
    hospital_name: str
    summary: str
    eligibility_summary: str
    trial_link: str

class SearchFilters(BaseModel):
    is_off_topic: bool = Field(description="Set to true if the user's query is completely unrelated to cancer, clinical trials, or medical help.", default=False)
    cancer_type: Optional[str] = Field(description="The type of cancer the user is asking about, e.g., 'Breast Cancer', 'Lung Cancer', 'Melanoma', 'Leukemia', 'Prostate Cancer', 'Colon Cancer'.", default=None)
    cancer_stage: Optional[str] = Field(description="The stage of the cancer if specified, e.g., 'Stage I', 'Stage II', 'Stage III', 'Stage IV'.", default=None)
    prior_treatments: Optional[str] = Field(description="Any prior treatments the user has undergone, e.g., 'Surgery', 'Chemotherapy', 'Radiation', 'Immunotherapy'.", default=None)
    trial_phase: Optional[str] = Field(description="The phase of the clinical trial if specified, e.g., 'Phase I', 'Phase II', 'Phase III'.", default=None)
    recruitment_status: Optional[str] = Field(description="The recruitment status if specified, e.g., 'Recruiting', 'Not Recruiting'.", default=None)
    location: Optional[str] = Field(description="The generic location, city, or province the user is asking about, e.g., 'Montreal', 'Ontario', 'Toronto'.", default=None)

class SuggestionItem(BaseModel):
    label: str = Field(description="The readable label of the suggestion chip.")
    value: str = Field(description="The value to be sent back if clicked.")

class SuggestionList(BaseModel):
    suggestions: List[SuggestionItem] = Field(description="A list of 3-4 suggestions.")
class MapboxTrial(BaseModel):
    trial_code: str
    trial_title: str
    hospital: str
    latitude: float
    longitude: float

class MapboxOutput(BaseModel):
    trials: List[MapboxTrial]
