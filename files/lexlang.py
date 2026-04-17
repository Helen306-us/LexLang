import re
import sys
import math
import os

# ─────────────────────────────────────────────
#  COLORES PARA LA TERMINAL
# ─────────────────────────────────────────────
class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    RED     = "\033[91m"
    BLUE    = "\033[94m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    BG_DARK = "\033[40m"

def c(text, color):
    return f"{color}{text}{Color.RESET}"

# ─────────────────────────────────────────────
#  TOKENS
# ─────────────────────────────────────────────
TK_NUMBER   = "NUMBER"
TK_STRING   = "STRING"
TK_BOOL     = "BOOL"
TK_NULL     = "NULL"
TK_ID       = "ID"
TK_KW       = "KW"
TK_OP       = "OP"
TK_EQ       = "EQ"
TK_DCOLON   = "DCOLON"
TK_LPAREN   = "LPAREN"
TK_RPAREN   = "RPAREN"
TK_LBRACE   = "LBRACE"
TK_RBRACE   = "RBRACE"
TK_LBRACKET = "LBRACKET"
TK_RBRACKET = "RBRACKET"
TK_COMMA    = "COMMA"
TK_NEWLINE  = "NEWLINE"
TK_EOF      = "EOF"

KEYWORDS = {
    "var", "si", "sino", "mientras", "repetir",
    "funcion", "retornar", "verdadero", "falso", "nulo"
}

class Token:
    def __init__(self, type_, value, line=0):
        self.type  = type_
        self.value = value
        self.line  = line
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

# ─────────────────────────────────────────────
#  LEXER
# ─────────────────────────────────────────────
class LexLangError(Exception):
    def __init__(self, msg, line=None):
        self.msg  = msg
        self.line = line
        super().__init__(msg)

class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos    = 0
        self.line   = 1

    def error(self, msg):
        raise LexLangError(msg, self.line)

    def peek(self, offset=0):
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else "\0"

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def tokenize(self):
        tokens = []
        while self.pos < len(self.source):
            ch = self.peek()

            # Comentario
            if ch == "#":
                while self.pos < len(self.source) and self.peek() != "\n":
                    self.advance()
                continue

            # Salto de linea
            if ch == "\n":
                self.advance()
                tokens.append(Token(TK_NEWLINE, "\n", self.line))
                continue

            # Espacios
            if ch in " \t\r":
                self.advance()
                continue

            # Cadena
            if ch == '"':
                self.advance()
                s = ""
                while self.pos < len(self.source) and self.peek() != '"':
                    s += self.advance()
                if self.pos >= len(self.source):
                    self.error("Cadena sin cerrar")
                self.advance()  # cierre "
                tokens.append(Token(TK_STRING, s, self.line))
                continue

            # Numero (incluyendo negativos solos: -7)
            if ch.isdigit() or (ch == "-" and self.peek(1).isdigit() and
                                (not tokens or tokens[-1].type in (TK_NEWLINE, TK_OP, TK_EQ, TK_LPAREN, TK_COMMA, TK_LBRACKET))):
                num = ""
                if ch == "-":
                    num += self.advance()
                while self.pos < len(self.source) and (self.peek().isdigit() or self.peek() == "."):
                    num += self.advance()
                val = float(num) if "." in num else int(num)
                tokens.append(Token(TK_NUMBER, val, self.line))
                continue

            # Identificadores / palabras clave
            if ch.isalpha() or ch == "_":
                word = ""
                while self.pos < len(self.source) and (self.peek().isalpha() or self.peek().isdigit() or self.peek() == "_"):
                    word += self.advance()
                if word == "verdadero":
                    tokens.append(Token(TK_BOOL, True, self.line))
                elif word == "falso":
                    tokens.append(Token(TK_BOOL, False, self.line))
                elif word == "nulo":
                    tokens.append(Token(TK_NULL, None, self.line))
                elif word in KEYWORDS:
                    tokens.append(Token(TK_KW, word, self.line))
                else:
                    tokens.append(Token(TK_ID, word, self.line))
                continue

            # Operadores dobles
            if ch == ":" and self.peek(1) == ":":
                self.advance(); self.advance()
                tokens.append(Token(TK_DCOLON, "::", self.line))
                continue
            if ch == ">" and self.peek(1) == "=":
                self.advance(); self.advance()
                tokens.append(Token(TK_OP, ">=", self.line))
                continue
            if ch == "<" and self.peek(1) == "=":
                self.advance(); self.advance()
                tokens.append(Token(TK_OP, "<=", self.line))
                continue
            if ch == "!" and self.peek(1) == "=":
                self.advance(); self.advance()
                tokens.append(Token(TK_OP, "!=", self.line))
                continue
            if ch == "=" and self.peek(1) == "=":
                self.advance(); self.advance()
                tokens.append(Token(TK_OP, "==", self.line))
                continue

            # Operadores simples
            if ch in "+-*/%^><":
                self.advance()
                tokens.append(Token(TK_OP, ch, self.line))
                continue

            if ch == "=":
                self.advance()
                tokens.append(Token(TK_EQ, "=", self.line))
                continue

            # Puntuacion
            simple = {"(": TK_LPAREN, ")": TK_RPAREN,
                      "{": TK_LBRACE,  "}": TK_RBRACE,
                      "[": TK_LBRACKET, "]": TK_RBRACKET,
                      ",": TK_COMMA}
            if ch in simple:
                tokens.append(Token(simple[ch], ch, self.line))
                self.advance()
                continue

            if ch == "$":
                self.advance()
                tokens.append(Token(TK_EOF, "$", self.line))
                break

            self.error(f"Caracter desconocido: '{ch}'")

        if not tokens or tokens[-1].type != TK_EOF:
            self.error("Se esperaba el fin de cadena '$' al final del código")

        return tokens

# ─────────────────────────────────────────────
#  NODOS AST
# ─────────────────────────────────────────────
class Node:
    pass

class Program(Node):
    def __init__(self, body): self.body = body

class VarDecl(Node):
    def __init__(self, name, value, line): self.name = name; self.value = value; self.line = line

class Assign(Node):
    def __init__(self, name, value, line): self.name = name; self.value = value; self.line = line

class ConcatDef(Node):
    def __init__(self, defs, order, line): self.defs = defs; self.order = order; self.line = line

class IfStmt(Node):
    def __init__(self, cond, consequent, alternate, line):
        self.cond = cond; self.consequent = consequent; self.alternate = alternate; self.line = line

class WhileStmt(Node):
    def __init__(self, cond, body, line): self.cond = cond; self.body = body; self.line = line

class RepeatStmt(Node):
    def __init__(self, times, body, line): self.times = times; self.body = body; self.line = line

class FunDecl(Node):
    def __init__(self, name, params, body, line):
        self.name = name; self.params = params; self.body = body; self.line = line

class ReturnStmt(Node):
    def __init__(self, value, line): self.value = value; self.line = line

class PrintStmt(Node):
    def __init__(self, args, line): self.args = args; self.line = line

class ExprStmt(Node):
    def __init__(self, expr, line): self.expr = expr; self.line = line

class Literal(Node):
    def __init__(self, value): self.value = value

class Var(Node):
    def __init__(self, name, line): self.name = name; self.line = line

class BinOp(Node):
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right

class BinCond(Node):
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right

class RepeatStr(Node):
    def __init__(self, times, text): self.times = times; self.text = text

class CallExpr(Node):
    def __init__(self, name, args, line): self.name = name; self.args = args; self.line = line

class ArrayLit(Node):
    def __init__(self, items): self.items = items

# ─────────────────────────────────────────────
#  PARSER
# ─────────────────────────────────────────────
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def peek(self, offset=0):
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else Token(TK_EOF, None)

    def consume(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def skip_newlines(self):
        while self.peek().type == TK_NEWLINE:
            self.consume()

    def expect(self, ttype, val=None):
        t = self.consume()
        if t.type != ttype or (val is not None and t.value != val):
            raise LexLangError(f"Se esperaba {val or ttype}, se obtuvo {t.value!r}", t.line)
        return t

    def parse_program(self):
        body = []
        while self.peek().type != TK_EOF:
            self.skip_newlines()
            if self.peek().type == TK_EOF:
                break
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        return Program(body)

    def parse_statement(self):
        self.skip_newlines()
        t = self.peek()

        if t.type == TK_KW and t.value == "var":
            return self.parse_var()
        if t.type == TK_KW and t.value == "si":
            return self.parse_if()
        if t.type == TK_KW and t.value == "mientras":
            return self.parse_while()
        if t.type == TK_KW and t.value == "repetir":
            return self.parse_repeat()
        if t.type == TK_KW and t.value == "funcion":
            return self.parse_funcion()
        if t.type == TK_KW and t.value == "retornar":
            return self.parse_return()

        # impr(...)
        if t.type == TK_ID and t.value == "impr" and self.peek(1).type == TK_LPAREN:
            return self.parse_print()

        # Asignacion: nombre = expr
        if t.type == TK_ID and self.peek(1).type == TK_EQ:
            # Puede ser concat: A="x" B="y" :: AB
            if len(t.value) == 1 and t.value.isupper():
                return self.parse_concat_or_assign()
            return self.parse_assign()

        return self.parse_expr_stmt()

    def parse_var(self):
        line = self.peek().line
        self.consume()  # var
        name = self.expect(TK_ID).value
        self.expect(TK_EQ)
        val = self.parse_expr()
        return VarDecl(name, val, line)

    def parse_assign(self):
        line = self.peek().line
        name = self.consume().value
        self.consume()  # =
        val = self.parse_expr()
        return Assign(name, val, line)

    def parse_concat_or_assign(self):
        line = self.peek().line
        # Detectar si es concat: A="..." B="..." :: ORDEN
        saved = self.pos
        defs = []
        try:
            while (self.peek().type == TK_ID and len(self.peek().value) == 1
                   and self.peek().value.isupper() and self.peek(1).type == TK_EQ):
                letter = self.consume().value
                self.consume()  # =
                val = self.parse_atom()
                defs.append((letter, val))
            if self.peek().type == TK_DCOLON:
                self.consume()
                order = self.expect(TK_ID).value
                return ConcatDef(defs, order, line)
        except:
            pass
        # No es concat, restaurar y tratar como asignacion
        self.pos = saved
        return self.parse_assign()

    def parse_if(self):
        line = self.peek().line
        self.consume()  # si
        self.expect(TK_LPAREN)
        cond = self.parse_cond_expr()
        self.expect(TK_RPAREN)
        self.skip_newlines()
        self.expect(TK_LBRACE)
        body = self.parse_block()
        self.expect(TK_RBRACE)
        alternate = None
        self.skip_newlines()
        if self.peek().type == TK_KW and self.peek().value == "sino":
            self.consume()  # sino
            self.skip_newlines()
            if self.peek().type == TK_KW and self.peek().value == "si":
                alternate = self._parse_sino_si(line)
            else:
                self.expect(TK_LBRACE)
                body3 = self.parse_block()
                self.expect(TK_RBRACE)
                alternate = Program(body3)
        return IfStmt(cond, body, alternate, line)

    def _parse_sino_si(self, parent_line):
        self.consume()  # si
        line = self.peek().line
        self.expect(TK_LPAREN)
        cond = self.parse_cond_expr()
        self.expect(TK_RPAREN)
        self.skip_newlines()
        self.expect(TK_LBRACE)
        body = self.parse_block()
        self.expect(TK_RBRACE)
        alternate = None
        self.skip_newlines()
        if self.peek().type == TK_KW and self.peek().value == "sino":
            self.consume()
            self.skip_newlines()
            if self.peek().type == TK_KW and self.peek().value == "si":
                alternate = self._parse_sino_si(line)
            else:
                self.expect(TK_LBRACE)
                b = self.parse_block()
                self.expect(TK_RBRACE)
                alternate = Program(b)
        return IfStmt(cond, body, alternate, line)

    def parse_while(self):
        line = self.peek().line
        self.consume()  # mientras
        self.expect(TK_LPAREN)
        cond = self.parse_cond_expr()
        self.expect(TK_RPAREN)
        self.skip_newlines()
        self.expect(TK_LBRACE)
        body = self.parse_block()
        self.expect(TK_RBRACE)
        return WhileStmt(cond, body, line)

    def parse_repeat(self):
        line = self.peek().line
        self.consume()  # repetir
        times = self.parse_atom()
        self.skip_newlines()
        self.expect(TK_LBRACE)
        body = self.parse_block()
        self.expect(TK_RBRACE)
        return RepeatStmt(times, body, line)

    def parse_funcion(self):
        line = self.peek().line
        self.consume()  # funcion
        name = self.expect(TK_ID).value
        self.expect(TK_LPAREN)
        params = []
        while self.peek().type != TK_RPAREN:
            params.append(self.expect(TK_ID).value)
            if self.peek().type == TK_COMMA:
                self.consume()
        self.expect(TK_RPAREN)
        self.skip_newlines()
        self.expect(TK_LBRACE)
        body = self.parse_block()
        self.expect(TK_RBRACE)
        return FunDecl(name, params, body, line)

    def parse_return(self):
        line = self.peek().line
        self.consume()  # retornar
        val = self.parse_expr()
        return ReturnStmt(val, line)

    def parse_print(self):
        line = self.peek().line
        self.consume()  # impr
        self.expect(TK_LPAREN)
        args = []
        while self.peek().type != TK_RPAREN:
            args.append(self.parse_expr())
            if self.peek().type == TK_COMMA:
                self.consume()
        self.expect(TK_RPAREN)
        return PrintStmt(args, line)

    def parse_block(self):
        stmts = []
        self.skip_newlines()
        while self.peek().type not in (TK_RBRACE, TK_EOF):
            self.skip_newlines()
            if self.peek().type in (TK_RBRACE, TK_EOF):
                break
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
            self.skip_newlines()
        return stmts

    def parse_expr_stmt(self):
        line = self.peek().line
        expr = self.parse_expr()
        return ExprStmt(expr, line)

    def parse_cond_expr(self):
        left = self.parse_expr()
        comp_ops = {">", "<", ">=", "<=", "==", "!="}
        if self.peek().type == TK_OP and self.peek().value in comp_ops:
            op = self.consume().value
            right = self.parse_expr()
            return BinCond(op, left, right)
        return left

    def parse_expr(self):
        arith = {"+", "-", "*", "/", "%", "^"}

        # Verificar si es ConcatDef o Asignacion: A="..." B="..." :: ORDEN  O  x = exp
        t = self.peek()
        if t.type == TK_ID and self.peek(1).type == TK_EQ:
            # Puede ser ConcatDef o Asignacion
            saved = self.pos
            try:
                # Usar la logica existente pero como expresion
                node = self.parse_concat_or_assign()
                if isinstance(node, (ConcatDef, Assign)):
                    return node
            except:
                pass
            self.pos = saved

        # N*"texto" o N*variable (repeticion de cadena)
        if (self.peek().type == TK_NUMBER and
                self.peek(1).type == TK_OP and self.peek(1).value == "*" and
                self.peek(2).type in (TK_STRING, TK_ID)):
            n = Literal(self.consume().value)
            self.consume()  # *
            text = self.parse_atom()
            return RepeatStr(n, text)

        left = self.parse_atom()

        # Notacion postfija: left right op
        # right puede ser: numero, variable, o llamada a funcion
        def next_is_operand():
            t0 = self.peek()
            if t0.type == TK_NUMBER:
                return True
            if t0.type == TK_ID:
                # variable o llamada a funcion seguida de (
                return True
            return False

        def next_after_operand_is_arith():
            # guarda posicion, parsea atom, verifica si sigue OP aritmetico
            saved = self.pos
            try:
                self.parse_atom()
                result = self.peek().type == TK_OP and self.peek().value in arith
            except:
                result = False
            self.pos = saved
            return result

        if next_is_operand() and next_after_operand_is_arith():
            right = self.parse_atom()
            op    = self.consume().value
            return BinOp(op, left, right)

        if self.peek().type == TK_OP and self.peek().value in arith:
            op    = self.consume().value
            right = self.parse_atom()
            return BinOp(op, left, right)

        return left

    def parse_atom(self):
        t = self.peek()

        if t.type == TK_NUMBER:
            self.consume()
            return Literal(t.value)
        if t.type == TK_STRING:
            self.consume()
            return Literal(t.value)
        if t.type == TK_BOOL:
            self.consume()
            return Literal(t.value)
        if t.type == TK_NULL:
            self.consume()
            return Literal(None)

        if t.type == TK_LBRACKET:
            self.consume()
            items = []
            while self.peek().type != TK_RBRACKET:
                items.append(self.parse_expr())
                if self.peek().type == TK_COMMA:
                    self.consume()
            self.expect(TK_RBRACKET)
            return ArrayLit(items)

        if t.type == TK_ID:
            # Llamada a funcion
            if self.peek(1).type == TK_LPAREN:
                name = self.consume().value
                self.consume()  # (
                args = []
                while self.peek().type != TK_RPAREN:
                    args.append(self.parse_expr())
                    if self.peek().type == TK_COMMA:
                        self.consume()
                self.expect(TK_RPAREN)
                return CallExpr(name, args, t.line)
            self.consume()
            return Var(t.value, t.line)

        if t.type == TK_LPAREN:
            self.consume()
            expr = self.parse_expr()
            self.expect(TK_RPAREN)
            return expr

        raise LexLangError(f"Expresion inesperada: {t.value!r}", t.line)

# ─────────────────────────────────────────────
#  VALOR DE RETORNO
# ─────────────────────────────────────────────
class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

# ─────────────────────────────────────────────
#  ENTORNO (SCOPES)
# ─────────────────────────────────────────────
class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise LexLangError(f"Variable '{name}' no definida")

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value)
            return
        self.vars[name] = value

    def define(self, name, value):
        self.vars[name] = value

    def has(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False

# ─────────────────────────────────────────────
#  INTERPRETE / EVALUADOR
# ─────────────────────────────────────────────
class Interpreter:
    OP_LABELS = {
        "+": "SUMA", "-": "RESTA", "*": "MULTIPLICAR",
        "/": "DIVIDIR", "%": "MODULO", "^": "POTENCIA"
    }

    def __init__(self):
        self.global_env = Environment()
        self.functions  = {}
        self.output     = []

    # ── Utilidades ──
    def fmt(self, v):
        if v is None:           return "nulo"
        if v is True:           return "verdadero"
        if v is False:          return "falso"
        if isinstance(v, list): return "[" + ", ".join(self.fmt(i) for i in v) + "]"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)

    def emit(self, op_label, display, raw=None, color=Color.GREEN):
        self.output.append({"op": op_label, "display": display, "raw": raw, "color": color})

    def run(self, source):
        self.output    = []
        self.functions = {}
        self.global_env = Environment()
        tokens_info = []
        tree_str = ""
        mermaid_str = ""
        try:
            tokens = Lexer(source).tokenize()
            for t in tokens:
                if t.type not in (TK_NEWLINE, TK_EOF):
                    tokens_info.append({"line": t.line, "type": t.type, "value": t.value})
            ast    = Parser(tokens).parse_program()
            try:
                tree_obj = self.build_lark_tree(ast)
                tree_str = tree_obj.pretty()
                mermaid_str = self.generate_mermaid(tree_obj)
            except ImportError:
                tree_str = "Error: El módulo lark no está instalado."
            except Exception as ex:
                tree_str = f"Error al construir el árbol: {ex}"
            self.exec_block(ast.body, self.global_env)
        except LexLangError as e:
            line_info = f" (linea {e.line})" if e.line else ""
            self.emit("ERROR", f"{e.msg}{line_info}", raw=None, color=Color.RED)
        except RecursionError:
            self.emit("ERROR", "Demasiada recursion — revisa tu funcion recursiva", raw=None, color=Color.RED)
        
        tree_json = {}
        try:
            if tree_str:
                tree_json = self.build_json_tree(self.build_lark_tree(Parser(Lexer(source).tokenize()).parse_program()))
        except:
            pass

        return {
            "operations": self.output,
            "tokens": tokens_info,
            "tree": tree_str,
            "mermaid": mermaid_str,
            "tree_json": tree_json
        }

    def build_json_tree(self, tree):
        from lark import Tree
        if isinstance(tree, Tree):
            node = {"name": str(tree.data).upper()}
            children = [self.build_json_tree(c) for c in tree.children]
            if children:
                node["children"] = children
            return node
        else:
            return {"name": str(tree)}

    def generate_mermaid(self, tree):
        lines = ["graph LR"]
        lines.append("classDef rectNode fill:#e2e8f0,stroke:#64748b,stroke-width:2px,color:#0f172a;")
        lines.append("classDef ellipseNode fill:#bbf7d0,stroke:#22c55e,stroke-width:2px,color:#0f172a;")
        self._mermaid_id = 0
        def traverse(node):
            self._mermaid_id += 1
            node_id = f"N{self._mermaid_id}"
            from lark import Tree
            if isinstance(node, Tree):
                label = str(node.data).upper()
                lines.append(f'{node_id}["{label}"]:::rectNode')
                for child in node.children:
                    child_id = traverse(child)
                    lines.append(f"{node_id} --> {child_id}")
            else:
                label = str(node).replace('"', "'")
                label = label.replace('\\', '\\\\')
                lines.append(f'{node_id}(("{label}")):::ellipseNode')
            return node_id
            
        traverse(tree)
        return "\\n".join(lines)

    def build_lark_tree(self, node):
        from lark import Tree
        if isinstance(node, Program):
            return Tree("program", [self.build_lark_tree(s) for s in node.body if s is not None])
        if isinstance(node, VarDecl):
            return Tree("var_decl", [Tree("id", [str(node.name)]), self.build_lark_tree(node.value)])
        if isinstance(node, Assign):
            return Tree("assign", [Tree("id", [str(node.name)]), self.build_lark_tree(node.value)])
        if isinstance(node, ConcatDef):
            defs = [Tree("def", [Tree("id", [k]), self.build_lark_tree(v)]) for k, v in node.defs]
            return Tree("concat_def", defs + [Tree("order", [node.order])])
        if isinstance(node, IfStmt):
            children = [self.build_lark_tree(node.cond), Tree("block", [self.build_lark_tree(s) for s in node.consequent])]
            if node.alternate:
                if isinstance(node.alternate, IfStmt):
                    children.append(self.build_lark_tree(node.alternate))
                else:
                    children.append(Tree("block", [self.build_lark_tree(s) for s in node.alternate.body]))
            return Tree("if_stmt", children)
        if isinstance(node, WhileStmt):
            return Tree("while_stmt", [self.build_lark_tree(node.cond), Tree("block", [self.build_lark_tree(s) for s in node.body])])
        if isinstance(node, RepeatStmt):
            return Tree("repeat_stmt", [self.build_lark_tree(node.times), Tree("block", [self.build_lark_tree(s) for s in node.body])])
        if isinstance(node, FunDecl):
            return Tree("fun_decl", [Tree("id", [node.name]), Tree("params", [Tree("id", [p]) for p in node.params]), Tree("block", [self.build_lark_tree(s) for s in node.body])])
        if isinstance(node, ReturnStmt):
            return Tree("return", [self.build_lark_tree(node.value)])
        if isinstance(node, PrintStmt):
            return Tree("print", [self.build_lark_tree(a) for a in node.args])
        if isinstance(node, ExprStmt):
            return self.build_lark_tree(node.expr)
        if isinstance(node, Literal):
            return Tree("literal", [str(node.value)])
        if isinstance(node, Var):
            return Tree("var", [str(node.name)])
        if isinstance(node, BinOp):
            return Tree("bin_op", [Tree("op", [node.op]), self.build_lark_tree(node.left), self.build_lark_tree(node.right)])
        if isinstance(node, BinCond):
            return Tree("bin_cond", [Tree("op", [node.op]), self.build_lark_tree(node.left), self.build_lark_tree(node.right)])
        if isinstance(node, RepeatStr):
            return Tree("repeat_str", [self.build_lark_tree(node.times), self.build_lark_tree(node.text)])
        if isinstance(node, CallExpr):
            return Tree("call", [Tree("id", [node.name]), Tree("args", [self.build_lark_tree(a) for a in node.args])])
        if isinstance(node, ArrayLit):
            return Tree("array", [self.build_lark_tree(i) for i in node.items])
        return Tree("unknown", [str(type(node).__name__)])

    # ── Ejecucion de bloques ──
    def exec_block(self, stmts, env):
        for stmt in stmts:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, node, env):
        if isinstance(node, VarDecl):
            val = self.eval_expr(node.value, env)
            env.define(node.name, val)
            self.emit("VARIABLE", f"{node.name} = {self.fmt(val)}", raw=val, color=Color.CYAN)

        elif isinstance(node, Assign):
            val = self.eval_expr(node.value, env)
            env.set(node.name, val)
            self.emit("ASIGNAR", f"{node.name} = {self.fmt(val)}", raw=val, color=Color.CYAN)

        elif isinstance(node, ConcatDef):
            mapping = {}
            for letter, val_node in node.defs:
                mapping[letter] = self.fmt(self.eval_expr(val_node, env))
            result = "".join(mapping.get(ch, "") for ch in node.order)
            self.emit("CONCAT", result, raw=result, color=Color.MAGENTA)

        elif isinstance(node, PrintStmt):
            vals = [self.eval_expr(a, env) for a in node.args]
            text = " ".join(self.fmt(v) for v in vals)
            self.emit("IMPRIMIR", text, raw=text, color=Color.YELLOW)
            print(c("  >> ", Color.GRAY) + c(text, Color.WHITE))

        elif isinstance(node, ExprStmt):
            val = self.eval_expr(node.expr, env)
            label = self.infer_label(node.expr)
            self.emit(label, self.fmt(val), raw=val, color=Color.GREEN)

        elif isinstance(node, IfStmt):
            cond = self.eval_cond(node.cond, env)
            if cond:
                child_env = Environment(env)
                self.exec_block(node.consequent, child_env)
            elif node.alternate is not None:
                child_env = Environment(env)
                if isinstance(node.alternate, IfStmt):
                    self.exec_stmt(node.alternate, child_env)
                else:
                    self.exec_block(node.alternate.body, child_env)

        elif isinstance(node, WhileStmt):
            guard = 0
            while self.eval_cond(node.cond, env):
                guard += 1
                if guard > 1000:
                    raise LexLangError("Limite de iteraciones alcanzado (max 1000)")
                child_env = Environment(env)
                try:
                    self.exec_block(node.body, child_env)
                except ReturnValue:
                    break
                # Propagar cambios al entorno padre
                for k, v in child_env.vars.items():
                    if env.has(k):
                        env.set(k, v)

        elif isinstance(node, RepeatStmt):
            times = int(self.eval_expr(node.times, env))
            for _ in range(min(times, 1000)):
                child_env = Environment(env)
                self.exec_block(node.body, child_env)

        elif isinstance(node, FunDecl):
            self.functions[node.name] = node
            self.emit("FUNCION", f"{node.name}({', '.join(node.params)}) definida", raw=None, color=Color.BLUE)

        elif isinstance(node, ReturnStmt):
            val = self.eval_expr(node.value, env)
            raise ReturnValue(val)

    # ── Evaluacion de expresiones ──
    def eval_expr(self, node, env):
        if isinstance(node, Literal):
            return node.value

        if isinstance(node, Var):
            if node.name == "verdadero": return True
            if node.name == "falso":     return False
            if node.name == "nulo":      return None
            # intenta numero
            try:
                return int(node.name)
            except ValueError:
                try:
                    return float(node.name)
                except ValueError:
                    pass
            return env.get(node.name)

        if isinstance(node, ArrayLit):
            return [self.eval_expr(i, env) for i in node.items]

        if isinstance(node, BinOp):
            l = self.eval_expr(node.left,  env)
            r = self.eval_expr(node.right, env)
            op = node.op
            if op == "+":
                if isinstance(l, str) or isinstance(r, str):
                    return str(l) + str(r)
                return l + r
            if op == "-": return l - r
            if op == "*": return l * r
            if op == "/":
                if r == 0:
                    raise LexLangError("Division por cero")
                return l / r
            if op == "%": return l % r
            if op == "^": return l ** r

        if isinstance(node, RepeatStr):
            n    = int(self.eval_expr(node.times, env))
            text = str(self.eval_expr(node.text,  env))
            return text * max(0, n)

        if isinstance(node, BinCond):
            return self.eval_cond(node, env)

        if isinstance(node, ConcatDef):
            mapping = {}
            for letter, val_node in node.defs:
                mapping[letter] = self.fmt(self.eval_expr(val_node, env))
            result = "".join(mapping.get(ch, "") for ch in node.order)
            self.emit("CONCAT", result, raw=result, color=Color.MAGENTA)
            return result

        if isinstance(node, Assign):
            val = self.eval_expr(node.value, env)
            env.set(node.name, val)
            self.emit("ASIGNAR", f"{node.name} = {self.fmt(val)}", raw=val, color=Color.CYAN)
            return val

        if isinstance(node, CallExpr):
            return self.call_fn(node.name, node.args, env, node.line)

        raise LexLangError(f"Nodo desconocido: {type(node).__name__}")

    def eval_cond(self, node, env):
        if not isinstance(node, BinCond):
            return bool(self.eval_expr(node, env))
        l  = self.eval_expr(node.left,  env)
        r  = self.eval_expr(node.right, env)
        op = node.op
        if op == ">":  return l > r
        if op == "<":  return l < r
        if op == ">=": return l >= r
        if op == "<=": return l <= r
        if op == "==": return l == r
        if op == "!=": return l != r
        return False

    # ── Funciones integradas y de usuario ──
    def call_fn(self, name, arg_nodes, env, line):
        args = [self.eval_expr(a, env) for a in arg_nodes]

        builtins = {
            # Matematicas
            "raiz":      lambda a: math.sqrt(a[0]),
            "abs":       lambda a: abs(a[0]),
            "redondear": lambda a: round(a[0]),
            "piso":      lambda a: math.floor(a[0]),
            "techo":     lambda a: math.ceil(a[0]),
            "max":       lambda a: max(a[0], a[1]),
            "min":       lambda a: min(a[0], a[1]),
            "potencia":  lambda a: a[0] ** a[1],
            "logaritmo": lambda a: math.log(a[0]),
            "seno":      lambda a: math.sin(a[0]),
            "coseno":    lambda a: math.cos(a[0]),
            # Cadenas
            "longitud":   lambda a: len(a[0]) if isinstance(a[0], (str, list)) else 0,
            "mayusculas": lambda a: str(a[0]).upper(),
            "minusculas": lambda a: str(a[0]).lower(),
            # Conversion
            "numero":    lambda a: float(a[0]) if "." in str(a[0]) else int(a[0]),
            "texto":     lambda a: str(a[0]),
            "tipo":      lambda a: type(a[0]).__name__,
            # Listas
            "agregar":   lambda a: a[0].append(a[1]) or a[0],
            "elemento":  lambda a: a[0][int(a[1])],
            "quitar":    lambda a: a[0].pop(int(a[1])) if a[1:] else a[0].pop(),
        }

        if name in builtins:
            try:
                return builtins[name](args)
            except Exception as e:
                raise LexLangError(f"Error en funcion '{name}': {e}", line)

        if name in self.functions:
            fn = self.functions[name]
            if len(args) != len(fn.params):
                raise LexLangError(
                    f"'{name}' espera {len(fn.params)} argumento(s), recibio {len(args)}", line)
            local_env = Environment(self.global_env)
            for param, val in zip(fn.params, args):
                local_env.define(param, val)
            try:
                self.exec_block(fn.body, local_env)
            except ReturnValue as rv:
                return rv.value
            return None

        raise LexLangError(f"Funcion '{name}' no definida", line)

    def infer_label(self, node):
        if isinstance(node, BinOp):
            return self.OP_LABELS.get(node.op, "RESULTADO")
        if isinstance(node, RepeatStr):
            return "REPETICION"
        if isinstance(node, CallExpr):
            return "LLAMADA"
        return "RESULTADO"

# ─────────────────────────────────────────────
#  INTERFAZ DE TERMINAL (REPL + ARCHIVO)
# ─────────────────────────────────────────────
OP_COLORS = {
    "SUMA":        Color.BLUE,
    "RESTA":       Color.GREEN,
    "MULTIPLICAR": Color.GREEN,
    "DIVIDIR":     Color.GREEN,
    "MODULO":      Color.GREEN,
    "POTENCIA":    Color.GREEN,
    "REPETICION":  Color.YELLOW,
    "CONCAT":      Color.MAGENTA,
    "IMPRIMIR":    Color.CYAN,
    "VARIABLE":    Color.CYAN,
    "ASIGNAR":     Color.CYAN,
    "FUNCION":     Color.BLUE,
    "LLAMADA":     Color.BLUE,
    "RESULTADO":   Color.WHITE,
    "ERROR":       Color.RED,
}

def print_banner():
    print()
    print(c("  ██╗     ███████╗██╗  ██╗██╗      █████╗ ███╗   ██╗ ██████╗ ", Color.CYAN))
    print(c("  ██║     ██╔════╝╚██╗██╔╝██║     ██╔══██╗████╗  ██║██╔════╝ ", Color.CYAN))
    print(c("  ██║     █████╗   ╚███╔╝ ██║     ███████║██╔██╗ ██║██║  ███╗", Color.CYAN))
    print(c("  ██║     ██╔══╝   ██╔██╗ ██║     ██╔══██║██║╚██╗██║██║   ██║", Color.CYAN))
    print(c("  ███████╗███████╗██╔╝ ██╗███████╗██║  ██║██║ ╚████║╚██████╔╝", Color.CYAN))
    print(c("  ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ", Color.CYAN))
    print()
    print(c("  Interprete de LexLang— Lenguaje en Español", Color.WHITE))
    print(c("  Proyecto: Diseño de Compiladores", Color.GRAY))
    print()

def print_results(results):
    for r in results:
        op = r["op"]
        display = r["display"]
        col = OP_COLORS.get(op, Color.WHITE)
        label = f"[{op}]".ljust(14)
        print(c(label, col) + c(" => ", Color.GRAY) + c(display, Color.WHITE))

def run_file(filepath):
    if not os.path.exists(filepath):
        print(c(f"Error: Archivo '{filepath}' no encontrado.", Color.RED))
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    interp  = Interpreter()
    print_banner()
    print(c(f"  Ejecutando: {filepath}", Color.GRAY))
    print(c("  " + "─" * 50, Color.GRAY))
    print()
    res_dict = interp.run(source)
    results = res_dict["operations"]
    print_results(results)
    errors = sum(1 for r in results if r["op"] == "ERROR")
    print()
    print(c("  " + "─" * 50, Color.GRAY))
    total = len(results)
    if errors == 0:
        print(c(f"  ✓ {total} instruccion(es) ejecutadas sin errores.", Color.GREEN))
    else:
        print(c(f"  {total - errors} ok / {errors} error(es).", Color.RED))
    print()

def repl():
    print_banner()
    print(c("  Modo REPL — Escribe instrucciones LexLang.", Color.WHITE))
    print(c("  Comandos especiales:", Color.GRAY))
    print(c("    .salir   — Termina el interprete", Color.GRAY))
    print(c("    .limpiar — Reinicia el entorno", Color.GRAY))
    print(c("    .ayuda   — Muestra referencia de sintaxis", Color.GRAY))
    print(c("    .ejemplo — Carga un programa de ejemplo", Color.GRAY))
    print()

    interp = Interpreter()
    AYUDA = """
  ┌─────────────────────────────────────────────────┐
  │           REFERENCIA RAPIDA DE LEXLANG          │
  ├─────────────────────────────────────────────────┤
  │  VARIABLES      var x = 10                      │
  │  ARITMETICA     5 2 +  /  9 3 -  /  4 3 *       │
  │                 10 2 /  /  10 3 %  /  2 8 ^      │
  │  REPETICION     3*"hola"                         │
  │  CONCAT         A="Hi" B=" Mundo" :: AB          │
  │  IMPRIMIR       impr("texto")  /  impr(5 2 +)    │
  │  IF/ELSE        si (x > 5) { } sino { }          │
  │  MIENTRAS       mientras (i < 10) { }            │
  │  REPETIR        repetir 3 { }                    │
  │  FUNCION        funcion suma(a,b) { retornar a b + } │
  │  COMENTARIO     # esto es un comentario          │
  └─────────────────────────────────────────────────┘
"""
    EJEMPLO = """var x = 10
var y = 3
impr(x y +)
impr(3*"ja")
A="Hola " B="Mundo" :: AB
si (x > y) {
  impr("x es mayor")
} sino {
  impr("y es mayor")
}
funcion cuadrado(n) {
  retornar n n *
}
impr(cuadrado(7))
$"""

    buffer = []
    depth  = 0  # cuenta llaves abiertas

    while True:
        try:
            prompt = c("  ... " if depth > 0 else "  >>> ", Color.GREEN)
            line   = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            print(c("  Hasta luego!", Color.CYAN))
            break

        cmd = line.strip()

        if cmd == ".salir":
            print(c("  Hasta luego!", Color.CYAN))
            break
        if cmd == ".limpiar":
            interp = Interpreter()
            buffer = []
            depth  = 0
            print(c("  Entorno reiniciado.", Color.GREEN))
            continue
        if cmd == ".ayuda":
            print(c(AYUDA, Color.CYAN))
            continue
        if cmd == ".ejemplo":
            print(c("  Ejecutando programa de ejemplo...\n", Color.GRAY))
            res_dict = interp.run(EJEMPLO)
            results = res_dict["operations"]
            print_results(results)
            print()
            continue

        buffer.append(line)
        depth += line.count("{") - line.count("}")

        if depth <= 0:
            # En REPL aseguramos que asimile el $ al evaluar
            if buffer[-1].strip() != "$" and not any(l.strip() == "$" for l in buffer):
                buffer.append("$")
            source  = "\n".join(buffer)
            buffer  = []
            depth   = 0
            res_dict = interp.run(source)
            results = res_dict["operations"]
            # Mostrar solo los nuevos resultados (impr ya imprime en run)
            for r in results:
                op = r["op"]
                display = r["display"]
                if op not in ("IMPRIMIR",):
                    col   = OP_COLORS.get(op, Color.WHITE)
                    label = f"[{op}]".ljust(14)
                    print(c(label, col) + c(" => ", Color.GRAY) + c(display, Color.WHITE))
            print()

# ─────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────
def main():
    if len(sys.argv) == 1:
        repl()
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        print(c("Uso: python lexlang.py [archivo.lx]", Color.YELLOW))
        sys.exit(1)

if __name__ == "__main__":
    main()
