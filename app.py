from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import Optional

app = FastAPI()

# simple in-memory sessions
sessions = {}

class SessionCreate(BaseModel):
    patientId: Optional[str] = None

class InputData(BaseModel):
    digit: Optional[str] = None
    text: Optional[str] = None
    intent: Optional[str] = None
    currentMenu: Optional[str] = None

# menu definitions
MENUS = {
    "main": {
        "prompt": "Welcome to the hospital lab system. Press 1 for latest report, 2 to repeat.",
        "options": {
            "1": {"action": "goto", "target": "report"},
            "2": {"action": "goto", "target": "main"}
        }
    },
    "report": {
        "prompt": "Your last lab result is Normal. Press 0 to go back or # to end.",
        "options": {
            "0": {"action": "goto", "target": "main"},
            "#": {"action": "end", "message": "Thank you, goodbye."}
        }
    }
}

@app.post("/session")
def create_session(body: SessionCreate):
    rid = str(uuid.uuid4())
    sessions[rid] = {"state": "started", "data": {}, "currentMenu": "main"}
    return {"sessionId": rid, "prompt": MENUS["main"]["prompt"], "menu": "main"}

@app.post("/session/{id}/input")
def session_input(id: str, data: InputData):
    sess = sessions.get(id)
    if not sess:
        raise HTTPException(status_code=404, detail="session not found")
    if data.digit:
        key = data.digit
    elif data.text:
        key = data.text
    elif data.intent:
        key = data.intent
    else:
        key = None
    menu_name = data.currentMenu or sess.get("currentMenu", "main")
    menu = MENUS.get(menu_name)
    if not menu:
        return {"prompt": "Invalid menu."}
    option = menu["options"].get(key)
    if not option:
        return {"prompt": f"Invalid option. {menu['prompt']}"}
    if option["action"] == "goto":
        sess["currentMenu"] = option["target"]
        return {"prompt": MENUS[option["target"]]["prompt"], "menu": option["target"]}
    elif option["action"] == "end":
        del sessions[id]
        return {"action": "hangup", "message": option.get("message")}
    return {"prompt": "OK"}

@app.post("/session/{id}/end")
def end_session(id: str):
    sessions.pop(id, None)
    return {"ok": True}
