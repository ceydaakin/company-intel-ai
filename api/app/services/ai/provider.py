from typing import Protocol
from app.schemas.company import CompanyCreate
from app.schemas.report import CompanyReport


class AIProvider(Protocol):
    async def generate_report(self, payload: CompanyCreate) -> CompanyReport: ...
