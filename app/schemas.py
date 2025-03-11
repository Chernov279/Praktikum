from typing import Optional, Union

from pydantic import BaseModel


class Params(BaseModel):
    keyword: str
    page: int = 0
    experience: Optional[str] = "doesNotMatter"
    employment: Optional[str]
    schedule: Optional[str]
    part_time: Optional[str]
    salary: Union[str, int, None]