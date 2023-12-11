from pydantic import BaseModel
from typing import Union, List, Dict


class URLParams(BaseModel):
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    hourly: Union[str, List[str]]
    timezone: str


class APIData(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    hourly_units: Dict[str, str]
    hourly: Dict[str, List[Union[str, float]]]
