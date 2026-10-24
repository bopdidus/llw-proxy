from fastapi import FastAPI, Body
import re
from utils import read_policy, parsed

app = FastAPI()


@app.post("/")
def read_root(prompt: str = Body(...)):
    return isThereAnEmail(prompt)


def isThereAnEmail(txt: str) -> bool:
    print(txt)
    x = re.findall("[^@]+@[^@]+\.[^@]+", txt)
    if x:
        return True
    else: 
        return False

@app.get("/test")
def test():
    text=read_policy("policy.yaml")
    parsed(text)
    return "good"
