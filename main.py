from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .models import (
    ExplainReportRequest,
    IVRMenuOption,
    IVRResponse,
    ListReportsRequest,
    StartSessionRequest,
)
from .services import explain_lab_report, get_patient_by_mrn, list_lab_reports

app = FastAPI(
    title="Lab‑Report Delivery & Explanation IVR – Python Middleware",
    description="FastAPI middleware that exposes IVR-friendly APIs for lab report flows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ivr/session/start", response_model=IVRResponse)
def start_session(payload: StartSessionRequest) -> IVRResponse:
    """
    Start an IVR session by MRN.
    A VXML app or web simulator calls this endpoint first.
    """
    patient = get_patient_by_mrn(payload.mrn)

    prompt = (
        f"Hello {patient.name}. "
        "Welcome to the hospital lab‑report service. "
        "Press 1 to hear a list of your available lab reports. "
        "Press 2 to end this call."
    )

    options = [
        IVRMenuOption(key="1", description="List available lab reports", next_action="LIST_REPORTS"),
        IVRMenuOption(key="2", description="End call", next_action="END_CALL"),
    ]

    return IVRResponse(prompt=prompt, options=options, end_call=False)


@app.post("/ivr/lab-reports/list", response_model=IVRResponse)
def list_reports(payload: ListReportsRequest) -> IVRResponse:
    """
    Return a menu-style list of lab reports for the patient.
    """
    reports = list_lab_reports(patient_id=payload.patient_id)
    if not reports:
        return IVRResponse(
            prompt="There are no lab reports available at this time. Thank you for calling.",
            options=[],
            end_call=True,
        )

    # Build a spoken prompt enumerating the reports.
    parts = ["You have the following lab reports available."]
    options: list[IVRMenuOption] = []
    for idx, report in enumerate(reports, start=1):
        key = str(idx)
        parts.append(f"For {report.title}, press {key}.")
        options.append(
            IVRMenuOption(
                key=key,
                description=report.title,
                next_action=f"EXPLAIN_REPORT:{report.id}",
            )
        )

    prompt = " ".join(parts)
    return IVRResponse(prompt=prompt, options=options, end_call=False)


@app.post("/ivr/lab-reports/explain", response_model=IVRResponse)
def explain_report(payload: ExplainReportRequest) -> IVRResponse:
    """
    Return a spoken explanation of a single lab report.
    """
    report = explain_lab_report(payload.report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    prompt = (
        f"This is your {report.title} report. "
        f"{report.summary} "
        "If you have questions, please contact your physician. "
        "Press 1 to repeat this explanation, or press 2 to end the call."
    )

    options = [
        IVRMenuOption(key="1", description="Repeat explanation", next_action=f"EXPLAIN_REPORT:{report.id}"),
        IVRMenuOption(key="2", description="End call", next_action="END_CALL"),
    ]

    return IVRResponse(prompt=prompt, options=options, end_call=False)


@app.get("/sim", response_class=HTMLResponse)
def simulator_page() -> str:
    """
    Very simple HTML page that acts as a web-based IVR simulator.
    This is intentionally minimal so you can extend or restyle it.
    """
    return """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Lab‑Report IVR Simulator</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; }
      .prompt { border: 1px solid #ccc; padding: 1rem; min-height: 4rem; margin-bottom: 1rem; }
      .digits button { margin: 0.25rem; width: 3rem; height: 3rem; }
      .log { margin-top: 1rem; font-size: 0.9rem; color: #555; white-space: pre-wrap; }
    </style>
  </head>
  <body>
    <h1>Lab‑Report IVR Web Simulator</h1>
    <label>
      MRN:
      <input id="mrnInput" value="123456" />
    </label>
    <button onclick="startCall()">Start Call</button>

    <h2>Prompt</h2>
    <div id="prompt" class="prompt">Press "Start Call" to begin.</div>

    <h2>Digits</h2>
    <div class="digits">
      <button onclick="sendDigit('1')">1</button>
      <button onclick="sendDigit('2')">2</button>
      <button onclick="sendDigit('3')">3</button><br />
      <button onclick="sendDigit('4')">4</button>
      <button onclick="sendDigit('5')">5</button>
      <button onclick="sendDigit('6')">6</button><br />
      <button onclick="sendDigit('7')">7</button>
      <button onclick="sendDigit('8')">8</button>
      <button onclick="sendDigit('9')">9</button><br />
      <button onclick="sendDigit('*')">*</button>
      <button onclick="sendDigit('0')">0</button>
      <button onclick="sendDigit('#')">#</button>
    </div>

    <div class="log" id="log"></div>

    <script>
      let currentPatientId = "patient-123";
      let currentOptions = [];

      function log(message) {
        const logEl = document.getElementById("log");
        logEl.textContent += message + "\\n";
      }

      async function startCall() {
        const mrn = document.getElementById("mrnInput").value;
        log("Starting call for MRN " + mrn + "...");
        const res = await fetch("/ivr/session/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mrn }),
        });
        const data = await res.json();
        document.getElementById("prompt").textContent = data.prompt;
        currentOptions = data.options || [];
        log("Options: " + JSON.stringify(currentOptions, null, 2));
      }

      async function sendDigit(digit) {
        if (!currentOptions.length) {
          log("No options available. Start a call first.");
          return;
        }

        const selected = currentOptions.find((o) => o.key === digit);
        if (!selected) {
          log("Digit " + digit + " not valid for current menu.");
          return;
        }

        log("Pressed " + digit + " (" + selected.description + "), action=" + selected.next_action);

        if (selected.next_action === "END_CALL") {
          document.getElementById("prompt").textContent =
            "The call has ended. Thank you for using the lab‑report service.";
          currentOptions = [];
          return;
        }

        if (selected.next_action === "LIST_REPORTS") {
          await listReports();
          return;
        }

        if (selected.next_action.startsWith("EXPLAIN_REPORT:")) {
          const reportId = selected.next_action.split(":")[1];
          await explainReport(reportId);
          return;
        }
      }

      async function listReports() {
        const res = await fetch("/ivr/lab-reports/list", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ patient_id: currentPatientId }),
        });
        const data = await res.json();
        document.getElementById("prompt").textContent = data.prompt;
        currentOptions = data.options || [];
        log("Report options: " + JSON.stringify(currentOptions, null, 2));
      }

      async function explainReport(reportId) {
        const res = await fetch("/ivr/lab-reports/explain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ report_id: reportId }),
        });
        const data = await res.json();
        document.getElementById("prompt").textContent = data.prompt;
        currentOptions = data.options || [];
        log("Explain options: " + JSON.stringify(currentOptions, null, 2));
      }
    </script>
  </body>
</html>
    """
