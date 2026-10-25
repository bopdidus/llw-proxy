from fastapi import FastAPI, Body
import re
from utils import analyse_text, replace, get_response

app = FastAPI()


@app.post("/")
def read_root(prompt: str = Body(...)):
    build_regex = analyse_text(prompt)
    new_prompt = replace(prompt, build_regex)
    print(new_prompt)
    res = get_response(new_prompt)
    return res




