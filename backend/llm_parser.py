from abc import ABC, abstractmethod
from typing import Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from schema import SearchFilters

class BaseLLMAdapter(ABC):
    """
    Abstract adapter for LLM interactions.
    """
    @abstractmethod
    def extract_filters(self, user_query: str) -> SearchFilters:
        """
        Extracts structured search filters from the user's query.
        Returns a SearchFilters Pydantic object.
        """
        pass
        
    @abstractmethod
    def get_missing_info_suggestions(self, filters: SearchFilters) -> List[str]:
        """
        Returns a list of suggested questions to ask the user to fill in missing info.
        """
        pass

class GroqLLMAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str = "llama-3.1-8b-instant", temperature: float = 0.0):
        # We assume GROQ_API_KEY is available in the environment
        self.llm = ChatGroq(model=model_name, temperature=temperature)
        
        # We tell the model to extract SearchFilters.
        self.structured_llm = self.llm.with_structured_output(SearchFilters)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant helping cancer patients find clinical trials. "
                       "Extract the patient's cancer type, clinical trial phase, recruitment status, and location (city or province) from their message. "
                       "If their message is completely unrelated to cancer, medical treatments, or clinical trials, set 'is_off_topic' to true, but do your best to help them if it is even loosely related."),
            ("human", "{user_query}")
        ])
        
        self.chain = self.prompt | self.structured_llm

    def extract_filters(self, user_query: str) -> SearchFilters:
        """
        Runs the LangChain pipeline to parse the user query.
        """
        return self.chain.invoke({"user_query": user_query})

    def get_missing_info_suggestions(self, filters: SearchFilters) -> List[str]:
        missing = []
        if not filters.cancer_type:
            missing.append("What type of cancer are you looking for trials for?")
        if not filters.location:
            missing.append("Where are you located (City/Province)?")
        if not filters.phase:
            missing.append("Are you looking for a specific clinical trial phase (e.g., Phase 1, Phase 2)?")
            
        return missing[:3]
