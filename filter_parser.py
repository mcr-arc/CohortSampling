import os
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class FiltersModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    DxDate: Optional[Union[str, List[str]]] = Field("Diagnosis year values, such as '2015' or ['2015', '2016']")
    Race1: Optional[Union[int, List[int]]] = Field("Race code values")
    DxCounty: Optional[Union[int, str, List[Union[int,str]]]] = Field("Diagnosis County values")
    AgeGroup: Optional[Union[str, List[str]]] = "Age bracket, such as '50s', '60s', or ['60s', '70s']."
    AgeDx: Optional[Union[int, List[int]]] = "age at diagnosis"
    HistTypeICDO3: Optional[Union[int, List[int]]] = "Histology ICD-O-3 code"
    PSite: Optional[Union[str, List[str]]] = "Primary Site or PSite"
    SiteGroup: Optional[Union[str, List[str]]] = "Cancer site group"
    Recode: Optional[Union[int, List[int]]] = "site recode"

class DataModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    n: int = Field(description="Requested sample size")

    # filters: Dict[str, Union[str, int, float, List[Union[str, int, float]]]] = Field(
    #     default_factory=dict,
    #     description="Filters to apply before sampling. Keys must match valid dataset columns."
    # )

    filters: Optional[FiltersModel] = Field(
        description="Filters to apply before sampling. Use null for filters not requested."
    )

    explanation: str = Field(
        description="Short explanation of how the natural language request was converted."
    )


class FilterParser:
    def __init__(self, model: str = "gpt-4.1-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def parse_request(
        self,
        user_query: str,
        valid_columns: List[str],
    ) -> DataModel:
        """
        Converts researcher natural language into structured JSON filters.
        """

        system_prompt = f"""
        You convert researcher cohort/sample requests into JSON.

        Only use these valid columns:
        {valid_columns}

        Rules:
        - Return only filters that are explicitly requested or strongly implied.
        - Do not invent columns.
        - Do not invent values.
        - If user asks for years, map them to DxDate as strings.
        - If user asks for race values, map them to Race1.
        - If user asks for counties, map them to DxCounty.
        - If user asks for age groups like 50s or 60s, map them to AgeGroup.
        - If no sample size is mentioned, use n=200.
        """

        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            text_format=DataModel
        )

        return response.output_parsed
    
if __name__ == "__main__":
    sampler = FilterParser()
    
