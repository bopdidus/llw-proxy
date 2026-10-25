import re
from enum import Enum
from pathlib import Path
from lark import Lark, Transformer

class DSLConstants(str, Enum):
    MACRO_OPEN = "["
    MACRO_CLOSE = "]"
    EMPTY_STRING = ""
    QUOTE_SINGLE = "'"
    QUOTE_DOUBLE = '"'
    REGEX_WORD_BOUNDARY = r"\b"


class DSLTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.sets = {}
        self.raw_rules = {}

    def set_definition(self, args):
        name = str(args[0]).strip()
        items = args[1]
        self.sets[name] = f"[{''.join(str(i) for i in items)}]"

    def set_item(self, args):
        return args[0]

    def set_expr(self, items):
        # On filtre les virgules pour ne garder que les éléments valides
        return [i for i in items if str(i) != ","]

    def range_item(self, args):
        bounds = [
            str(a).replace("'", "").replace('"', "")
            for a in args
            if a is not None and str(a) != "..."
        ]
        return f"{re.escape(bounds[0])}-{re.escape(bounds[-1])}"

    def literal_item(self, args):
        token = args[0] if isinstance(args, list) else args
        clean = str(token).replace("'", "").replace('"', "")
        # Référence à un ensemble déjà défini : on insère son contenu
        if clean in self.sets:
            return self.sets[clean][1:-1]
        return re.escape(clean)

    def rule_definition(self, args):
        name = str(args[0]).strip()
        elements = next(arg for arg in args if isinstance(arg, list))
        self.raw_rules[name] = elements

    def rule_expr(self, args):
        return args

    def rule_element(self, args):
        token_or_macro = str(args[0])
        quantifier = "".join(str(arg) for arg in args[1:] if arg is not None)
        return (token_or_macro, quantifier)

    def quantifier(self, args):
        return "".join(str(arg) for arg in args if arg is not None)


class PatternDSLCompiler:
    def __init__(self, grammar_path: str = "grammar.lark"):
        grammar_file = Path(grammar_path)
        if not grammar_file.exists():
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")
        
        self.parser = Lark.open(str(grammar_file), parser="lalr", maybe_placeholders=False)

    def compile_text(self, dsl_text: str) -> dict[str, re.Pattern]:
        tree = self.parser.parse(dsl_text)
        transformer = DSLTransformer()
        transformer.transform(tree)

        compiled_patterns = {}

        for name, elements in transformer.raw_rules.items():
            rule_parts = []
            for item, quantifier in elements:
                # Les macros s'écrivent [nom] ou nom
                if item.startswith(DSLConstants.MACRO_OPEN.value) and item.endswith(DSLConstants.MACRO_CLOSE.value):
                    item = item[1:-1]
                if item in transformer.sets:
                    base_regex = transformer.sets[item]
                else:
                    base_regex = re.escape(item)

                rule_parts.append(f"{base_regex}{quantifier}")

            full_body = "".join(rule_parts)
            rule_name_lower = name.lower()
            compiled_patterns[rule_name_lower] = re.compile(full_body)
        return compiled_patterns

    def compile_file(self, file_path: str) -> dict[str, re.Pattern]:
        with open(file_path, "r", encoding="utf-8") as f:
            return self.compile_text(f.read())