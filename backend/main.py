from urllib import response

from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import functions

class Machine(BaseModel):
    name: str
    block: str
    kind: str
    cycle_minutes: int

class Users(BaseModel):
    user_name: str
    password : str
    user_type: str

app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost:5173"],
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.patch("/collect/{machine_id}")
def collect(machine_id: str, roll_no: str,token = Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.collect_cloth(machine_id, roll_no)
    code = response["code"]
    if code == 200:
        return response["run"]
    raise HTTPException(code, detail=response["msg"])


@app.patch("/clear/{machine_id}")
def clear(machine_id: str, roll_no: str,token = Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.clear_machine(machine_id, roll_no)
    code = response["code"]
    if code == 200:
        return response["run"]
    raise HTTPException(code, detail=response["msg"])

@app.get("/runs/{roll_no}")
def running_run(roll_no: str,token = Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.get_running_runs(roll_no)
    code = response["code"]
    if code == 200:
        return response["runs"]
    raise HTTPException(code, detail=response["msg"])

@app.get("/machines/{id}")
def get_machine_by_id(id: int,token = Header(None)): #E2
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.get_machine_by_id(id=id)
    code = response["code"]
    if code == 200:
        return response["machine"]
    raise HTTPException(code, detail=response["msg"])

@app.post("/machines")
def add_machine(machine:Machine,token = Header(None)): #E3
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    if payload.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    response = functions.add_a_machine(machine.name,machine.block,machine.kind,machine.cycle_minutes)
    code = response["code"]
    if code == 200:
        return response["machine"]
    raise HTTPException(code,detail=response["msg"])

@app.get("/machines")
def get_all_machines(block=None,kind=None,token = Header(None)): #E1
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    if block not in ["a","b","c","d", None]:
        raise HTTPException(status_code=422, detail="Invalid block")
    if kind not in ["washer","dryer",None]:
        raise HTTPException(status_code=422, detail="Invalid kind of machine")
    response = functions.get_all_machines(block=block,kind=kind)
    return response

@app.get("/attention")
def get_machines_needing_attention(token = Header(None)): #E9
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.get_machines_that_need_attention()
    return response

@app.post("/runs/{machine_id}")
def starting(machine_id,roll_no,token = Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    if payload.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    response = functions.start_machine(machine_id=machine_id,roll_no=roll_no)
    code = response["code"]
    if code == 200:
        return response["run"]
    raise HTTPException(code, detail=response["msg"])
@app.get("/usage")
def usage(token = Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.get_today_usage()
    code = response["code"]
    if code == 200:
        return response["usage"]
    raise HTTPException(code, detail=response["msg"])

@app.patch("/service/{machine_id}")
def changeservice(machine_id: str, in_service: int,token = Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    if payload.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    response = functions.change_service(machine_id, in_service)
    code = response["code"]
    if code == 200:
        return response["machine"]

    raise HTTPException(code, detail=response["msg"])

@app.post("/login")
def login(username = Body(),password = Body()):
    tokens = functions.verify_login(username=username,password=password)
    if not tokens:
        raise HTTPException(status_code=401,detail="Invalid credentials")
    return tokens

@app.post("/refresh")
def refresh(refresh_token):
    payload = functions.verify_token(token=refresh_token,token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token")
    username= payload.get("username")
    user_type = payload.get("user_type","user")

    access_token = functions.create_token(username=username,token_type="access",user_type=user_type)
    return {"access_token":access_token}

@app.post("/register")
def register_user(user:Users):
    if functions.register_user(user_name=user.user_name,password=user.password,user_type=user.user_type) is True:
        return {"message": "user registered successfully"}
    raise HTTPException(status_code=400,detail="Username already exists")
