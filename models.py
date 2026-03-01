from typing import List, Optional

from pydantic import BaseModel


class Patient(BaseModel):
    id: str
    mrn: str
    name: str
    language: str = "en"


class LabReport(BaseModel):
    id: str
    patient_id: str
    title: str
    summary: str
    is_critical: bool = False


class IVRMenuOption(BaseModel):
    key: str
    description: str
    next_action: str


class IVRResponse(BaseModel):
    prompt: str
    options: List[IVRMenuOption] = []
    end_call: bool = False


class StartSessionRequest(BaseModel):
    mrn: str
    language: Optional[str] = "en"


class ListReportsRequest(BaseModel):
    patient_id: str


class ExplainReportRequest(BaseModel):
    report_id: str

