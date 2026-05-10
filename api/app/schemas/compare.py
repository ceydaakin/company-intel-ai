import uuid
from pydantic import BaseModel
from app.schemas.company import CompanyDetail


class CompareRequest(BaseModel):
    a_id: uuid.UUID
    b_id: uuid.UUID


class CompareResponse(BaseModel):
    a: CompanyDetail
    b: CompanyDetail
