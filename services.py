from typing import List

from .models import LabReport, Patient


def get_patient_by_mrn(mrn: str) -> Patient:
    """
    Placeholder implementation that simulates a lookup to ACS/BAP or EMR.
    Replace this with real API calls or database queries.
    """
    # In a real system, map MRN to patient ID and other attributes.
    return Patient(
        id="patient-123",
        mrn=mrn,
        name="John Doe",
        language="en",
    )


def list_lab_reports(patient_id: str) -> List[LabReport]:
    """
    Placeholder implementation that returns static sample lab reports.
    Replace with calls to ACS/BAP or LIS.
    """
    return [
        LabReport(
            id="report-1",
            patient_id=patient_id,
            title="Complete Blood Count",
            summary="Your blood counts are within the normal range.",
        ),
        LabReport(
            id="report-2",
            patient_id=patient_id,
            title="Lipid Panel",
            summary="Your cholesterol levels are mildly elevated. Lifestyle changes are recommended.",
            is_critical=False,
        ),
    ]


def explain_lab_report(report_id: str) -> LabReport:
    """
    Placeholder implementation that returns a single lab report explanation.
    In a real system, fetch detailed result values and explanation text.
    """
    # For now, re-use the sample list and find by ID.
    sample_reports = list_lab_reports(patient_id="patient-123")
    for report in sample_reports:
        if report.id == report_id:
            return report

    # Fallback: return a generic placeholder.
    return LabReport(
        id=report_id,
        patient_id="patient-123",
        title="Unknown Report",
        summary="The details for this lab report are not available in the demo system.",
        is_critical=False,
    )

