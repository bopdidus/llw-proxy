from lark import Lark, Transformer
import yaml


class PolicyInterpreter(Transformer):
    def __init__(self):
        super().__init__()
        self.allowed_rules = []
        self.blocked_rules = []

    def allow_section(self, items):
        # The intepreter knows the allow section
        self.allowed_rules.extend([str(item) for item in items])

    def block_section(self, items):
        # The interpreter knows to block section
        self.blocked_rules.extend([str(item) for item in items])

    def item_list(self, args):
        return args


'''
read policy from the policy file
params:
 - file_path : file path with extension
'''
def read_policy(file_path:str):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()



def parsed(policies: str):
    parser = Lark(open("grammar.lark").read(), parser="lalr")
    tree = parser.parse(policies)
    interpreter = PolicyInterpreter()
    interpreter.transform(tree)
    print(interpreter.allowed_rules)
