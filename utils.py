from ollama import chat
from ollama import ChatResponse
import re
from dsl_compiler import DSLTransformer, PatternDSLCompiler

def get_response(prompt:str) -> str:
    response: ChatResponse = chat(
    model='gemma4:e2b',
    messages=[
            {
            'role': 'user',
            'content': prompt,
            },
        ],
    )
    return response.message.content


def analyse_text(text:str) -> dict:
    compiler = PatternDSLCompiler("grammar.lark")
    regexes = compiler.compile_file("policy.cfg")
    theDict={}
    for name, pattern in regexes.items():
        theDict[name] = pattern.pattern
    return theDict

def replace(text: str, rules: dict) -> str:
    for name, pattern in rules.items():
        text = re.sub(pattern, f"[{name.upper()}]", text)
    return text