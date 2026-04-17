# LexLang  — Documentación del Intérprete

> Documentación técnica de `lexlang.py`: cómo funciona cada componente del intérprete, siguiendo la arquitectura clásica **Lexer → Parser → AST → Intérprete**.https://ruslanspivak.com/lsbasi-part1/
>https://ruslanspivak.com/lsbasi-part2/
>https://ruslanspivak.com/lsbasi-part3/
....

---

## Tabla de Contenidos

1. [Visión General](#1-visión-general)
2. [Flujo de Ejecución](#2-flujo-de-ejecución)
3. [Tokens](#3-tokens)
4. [Lexer](#4-lexer)
5. [Nodos AST](#5-nodos-ast)
6. [Parser](#6-parser)
7. [Environment (Scopes)](#7-environment-scopes)
8. [Intérprete / Evaluador](#8-intérprete--evaluador)
9. [ReturnValue](#9-returnvalue)
10. [Interfaz de Terminal](#10-interfaz-de-terminal)

---

## 1. Visión General

LexLang es un intérprete escrito en Python para un lenguaje de programación personalizado en español. Sigue la arquitectura clásica de tres fases:

```
Código fuente (texto)
        │
        ▼
    [ LEXER ]          → Convierte caracteres en Tokens
        │
        ▼
    [ PARSER ]         → Convierte Tokens en un Árbol AST
        │
        ▼
  [ INTÉRPRETE ]       → Recorre el AST y ejecuta las instrucciones
        │
        ▼
     Resultado
```

---

## 2. Flujo de Ejecución

El punto de entrada principal es el método `Interpreter.run(source)`:

```python
def run(self, source):
    tokens = Lexer(source).tokenize()       # Fase 1: Lexer
    ast    = Parser(tokens).parse_program() # Fase 2: Parser
    self.exec_block(ast.body, self.global_env) # Fase 3: Ejecución
```

Ejemplo con `var x = 5`:

```
"var x = 5"
    │
    ▼ Lexer
[Token(KW,'var'), Token(ID,'x'), Token(EQ,'='), Token(NUMBER,5), Token(EOF,None)]
    │
    ▼ Parser
VarDecl(name='x', value=Literal(5))
    │
    ▼ Intérprete
env.define('x', 5)   →   emite [VARIABLE] x = 5
```

---

## 3. Tokens

### Clase `Token`

```python
class Token:
    def __init__(self, type_, value, line=0):
        self.type  = type_   # Categoría del token (ej: "NUMBER", "KW")
        self.value = value   # Valor real (ej: 5, "var", "+")
        self.line  = line    # Número de línea (para mensajes de error)
```

Un Token es la unidad mínima de información. El Lexer convierte cada parte del código fuente en uno de estos objetos.

### Tipos de Token disponibles

| Constante     | Descripción                          | Ejemplos              |
|---------------|--------------------------------------|-----------------------|
| `TK_NUMBER`   | Número entero o decimal              | `5`, `3.14`, `-7`     |
| `TK_STRING`   | Cadena de texto entre comillas       | `"hola"`              |
| `TK_BOOL`     | Valor booleano                       | `verdadero`, `falso`  |
| `TK_NULL`     | Valor nulo                           | `nulo`                |
| `TK_ID`       | Identificador (nombre de variable)   | `x`, `contador`       |
| `TK_KW`       | Palabra clave del lenguaje           | `var`, `si`, `funcion`|
| `TK_OP`       | Operador aritmético o comparación    | `+`, `-`, `>=`, `==`  |
| `TK_EQ`       | Signo de asignación                  | `=`                   |
| `TK_DCOLON`   | Doble dos puntos (concatenación)     | `::`                  |
| `TK_LPAREN`   | Paréntesis izquierdo                 | `(`                   |
| `TK_RPAREN`   | Paréntesis derecho                   | `)`                   |
| `TK_LBRACE`   | Llave izquierda                      | `{`                   |
| `TK_RBRACE`   | Llave derecha                        | `}`                   |
| `TK_LBRACKET` | Corchete izquierdo                   | `[`                   |
| `TK_RBRACKET` | Corchete derecho                     | `]`                   |
| `TK_COMMA`    | Coma                                 | `,`                   |
| `TK_NEWLINE`  | Salto de línea (separador)           | `\n`                  |
| `TK_EOF`      | Símbolo de fin de código fuente      | `$`                   |

### Palabras clave (`KEYWORDS`)

```python
KEYWORDS = {
    "var", "si", "sino", "mientras", "repetir",
    "funcion", "retornar", "verdadero", "falso", "nulo"
}
```

Cuando el Lexer encuentra una de estas palabras, crea un `TK_KW` en lugar de un `TK_ID`.

---

## 4. Lexer

### Propósito

El Lexer (también llamado *tokenizador* o *scanner*) lee el código fuente carácter por carácter y lo convierte en una lista de Tokens. Es la **Fase 1** del intérprete.

### Clase `Lexer`

```python
class Lexer:
    def __init__(self, source):
        self.source = source  # El código fuente completo como string
        self.pos    = 0       # Posición actual en el string
        self.line   = 1       # Línea actual (para errores)
```

### Métodos principales

#### `peek(offset=0)`
Mira el carácter en la posición actual **sin avanzar**. Con `offset=1` mira el siguiente sin consumir nada.

```python
def peek(self, offset=0):
    p = self.pos + offset
    return self.source[p] if p < len(self.source) else "\0"
```

#### `advance()`
Lee el carácter actual y **avanza** la posición. Si el carácter es `\n`, incrementa el contador de línea.

```python
def advance(self):
    ch = self.source[self.pos]
    self.pos += 1
    if ch == "\n":
        self.line += 1
    return ch
```

#### `tokenize()`
Método central. Recorre todo el código fuente con un `while` y decide qué token crear según el carácter actual. Retorna la lista completa de tokens.

**Reglas que aplica en orden:**

1. **`#`** → Ignora todo hasta el fin de línea (comentario)
2. **`\n`** → Crea `TK_NEWLINE` (separador de instrucciones)
3. **` \t\r`** → Ignora espacios y tabulaciones
4. **`"`** → Lee hasta el siguiente `"` y crea `TK_STRING`
5. **Dígito o `-` seguido de dígito** → Lee el número completo y crea `TK_NUMBER`
6. **Letra o `_`** → Lee la palabra completa; si es keyword crea `TK_KW`, si es `verdadero`/`falso`/`nulo` crea el token correspondiente, si no crea `TK_ID`
7. **`::`, `>=`, `<=`, `!=`, `==`** → Operadores dobles (lookahead con `peek(1)`)
8. **`+-*/%^><`** → Operadores simples → `TK_OP`
9. **`=`** → `TK_EQ`
Al terminar, busca el símbolo especial `$` para indicar el final del código fuente y agrega `Token(TK_EOF, "$")` al final de la lista. Si el signo especial `$` no se encuentra posicionado al final, el Lexer lanzará un error indicando que se esperaba el fin de cadena `$` al final del código.

### Clase `LexLangError`

```python
class LexLangError(Exception):
    def __init__(self, msg, line=None):
        self.msg  = msg
        self.line = line
```

Error personalizado que guarda el mensaje y la línea donde ocurrió el problema.

---

## 5. Nodos AST

El **AST (Abstract Syntax Tree)** es la representación estructurada del código. En lugar de una lista plana de tokens, es un árbol donde cada nodo describe una operación o declaración.

Todos los nodos heredan de la clase base vacía `Node`.

### Nodos de Instrucciones (Statements)

| Clase        | Qué representa              | Atributos principales              |
|--------------|-----------------------------|------------------------------------|
| `Program`    | El programa completo        | `body` (lista de statements)       |
| `VarDecl`    | `var x = expr`              | `name`, `value`, `line`            |
| `Assign`     | `x = expr`                  | `name`, `value`, `line`            |
| `ConcatDef`  | `A="x" B="y" :: AB`         | `defs`, `order`, `line`            |
| `IfStmt`     | `si (...) { } sino { }`     | `cond`, `consequent`, `alternate`  |
| `WhileStmt`  | `mientras (...) { }`        | `cond`, `body`, `line`             |
| `RepeatStmt` | `repetir N { }`             | `times`, `body`, `line`            |
| `FunDecl`    | `funcion nombre(p) { }`     | `name`, `params`, `body`, `line`   |
| `ReturnStmt` | `retornar expr`             | `value`, `line`                    |
| `PrintStmt`  | `impr(...)`                 | `args`, `line`                     |
| `ExprStmt`   | Expresión como instrucción  | `expr`, `line`                     |

### Nodos de Expresiones

| Clase       | Qué representa                     | Atributos                   |
|-------------|------------------------------------|-----------------------------|
| `Literal`   | Valor directo: número, texto, bool | `value`                     |
| `Var`       | Referencia a variable              | `name`, `line`              |
| `BinOp`     | Operación aritmética `a b +`       | `op`, `left`, `right`       |
| `BinCond`   | Comparación `a > b`                | `op`, `left`, `right`       |
| `RepeatStr` | Repetición de texto `3*"hola"`     | `times`, `text`             |
| `CallExpr`  | Llamada a función `suma(a, b)`     | `name`, `args`, `line`      |
| `ArrayLit`  | Lista literal `[1, 2, 3]`          | `items`                     |

### Integración con Lark (Representación Visual del AST)

Como requisito adicional, para visualizar de manera detallada el Árbol de Sintaxis Abstracta, se ha añadido la función `Interpreter.build_lark_tree(node)`. Esta función toma los nodos personalizados creados por el `Parser` y los traduce a objetos de clase `Tree` importados de la librería de terceros **Lark**. Luego, se hace uso de su método `.pretty()` para generar e imprimir de forma ordenada y de fácil visualización la jerarquía completa del AST, permitiendo a los desarrolladores y usuarios visualizar cómo el programa es estructurado sintácticamente antes de ser evaluado.

---

## 6. Parser

### Propósito

El Parser toma la lista de Tokens del Lexer y construye el AST. Es la **Fase 2** del intérprete. Verifica que la estructura del código sea válida según la gramática de LexLang.

### Clase `Parser`

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # Lista de tokens del Lexer
        self.pos    = 0       # Posición actual en la lista
```

### Métodos de navegación

#### `peek(offset=0)`
Mira el token en la posición actual sin consumirlo.

#### `consume()`
Retorna el token actual y avanza `pos` en 1. Equivalente al `eat()` del artículo de Ruslan.

#### `skip_newlines()`
Avanza mientras el token actual sea `TK_NEWLINE`. Los saltos de línea se usan como separadores pero no tienen significado dentro de una expresión.

#### `expect(ttype, val=None)`
Consume el token actual y lanza error si no es del tipo esperado. Se usa para verificar tokens obligatorios como `(`, `)`, `{`.

```python
self.expect(TK_LPAREN)   # Debe venir un '('
self.expect(TK_KW, "si") # Debe venir la palabra 'si'
```

### Métodos de parseo

#### `parse_program()`
Punto de entrada. Llama `parse_statement()` en bucle hasta llegar a `TK_EOF`. Devuelve un nodo `Program`.

#### `parse_statement()`
Detecta qué tipo de instrucción viene según el token actual y delega:

- `var` → `parse_var()`
- `si` → `parse_if()`
- `mientras` → `parse_while()`
- `repetir` → `parse_repeat()`
- `funcion` → `parse_funcion()`
- `retornar` → `parse_return()`
- `impr(` → `parse_print()`
- `ID =` → `parse_assign()` o `parse_concat_or_assign()`
- Cualquier otra cosa → `parse_expr_stmt()`

#### `parse_var()`
Parsea `var nombre = expresión`. Consume `var`, luego espera un `TK_ID`, luego `=`, luego una expresión.

#### `parse_assign()`
Parsea `nombre = expresión`. Consume el nombre, el `=`, y luego la expresión.

#### `parse_concat_or_assign()`
Detecta si la instrucción es una concatenación estilo `A="hola" B=" mundo" :: AB` o una asignación normal. Si falla la detección de concat, restaura la posición (`self.pos = saved`) y lo trata como asignación.

#### `parse_if()`
Parsea `si (condición) { bloque } sino { bloque }`. Soporta `sino si` encadenado mediante `_parse_sino_si()`.

#### `parse_while()`
Parsea `mientras (condición) { bloque }`.

#### `parse_repeat()`
Parsea `repetir N { bloque }`. `N` es una expresión atómica.

#### `parse_funcion()`
Parsea `funcion nombre(param1, param2) { bloque }`. Lee la lista de parámetros separados por comas.

#### `parse_block()`
Lee instrucciones hasta encontrar `}` o `TK_EOF`. Retorna lista de nodos.

#### `parse_cond_expr()`
Parsea una condición: una expresión, opcionalmente seguida de un operador de comparación (`>`, `<`, `>=`, `<=`, `==`, `!=`) y otra expresión. Retorna `BinCond` o simplemente la expresión.

#### `parse_expr()`
El corazón del parser de expresiones. Maneja:

1. **Asignación inline** `x = expr` dentro de una expresión
2. **Repetición de cadena** `N*"texto"`
3. **Notación postfija** `a b +` (estilo RPN: operando operando operador)
4. **Notación infija** `a + b`

#### `parse_atom()`
Parsea el elemento más pequeño posible: un número, string, bool, null, lista `[...]`, llamada a función `nombre(args)`, variable `nombre`, o una expresión entre paréntesis `(expr)`.

---

## 7. Environment (Scopes)

### Propósito

El `Environment` almacena las variables en un ámbito (scope) determinado. Cada bloque `{ }` crea un nuevo Environment hijo que puede acceder al padre, pero no al revés.

```python
class Environment:
    def __init__(self, parent=None):
        self.vars   = {}      # Diccionario nombre → valor
        self.parent = parent  # Referencia al scope padre
```

### Ejemplo de scopes anidados

```
global_env  { x: 10 }
    └── if_env  { y: 5 }         ← puede leer x del padre
            └── while_env  { i: 0 }  ← puede leer x e y
```

### Métodos

#### `get(name)`
Busca la variable en el scope actual. Si no la encuentra, la busca recursivamente en el padre. Lanza `LexLangError` si no existe en ningún nivel.

#### `set(name, value)`
Modifica el valor de una variable existente. Busca en el scope actual y luego en los padres. Si no la encuentra en ninguno, la crea en el scope actual.

#### `define(name, value)`
Crea una variable nueva **siempre en el scope actual**, sin buscar en los padres. Usado por `var` y para parámetros de funciones.

#### `has(name)`
Verifica si la variable existe en algún nivel del scope, sin lanzar error.

---

## 8. Intérprete / Evaluador

### Propósito

El `Interpreter` recorre el AST y **ejecuta** cada nodo. Es la **Fase 3** del intérprete.

### Clase `Interpreter`

```python
class Interpreter:
    def __init__(self):
        self.global_env = Environment()  # Scope global
        self.functions  = {}             # Funciones definidas por el usuario
        self.output     = []             # Lista de resultados emitidos
```

### Método `run(source)`

Orquesta las tres fases. Reinicia el estado interno, ejecuta, y captura errores para incluirlos en el output en lugar de hacer crash. Además, retorna un diccionario con tres elementos de gran valor para su visualización y depuración en sistemas externos:

```python
{
    "operations": self.output,   # Operaciones evaluadas (IMPRIMIR, SUMA, etc.) 
    "tokens": tokens_info,       # Lista serializada de todos los tokens encontrados
    "tree": tree_str             # Representación en string estructurado (Lark) del AST generada 
}
```

### Método `emit(op_label, display, raw, color)`

Agrega un resultado al output. Cada resultado es un diccionario:

```python
{"op": "SUMA", "display": "8", "raw": 8, "color": Color.BLUE}
```

Esto permite que la interfaz web o terminal muestre los resultados con etiquetas y colores.

### Método `exec_block(stmts, env)`

Recorre una lista de statements y ejecuta cada uno con `exec_stmt`.

### Método `exec_stmt(node, env)`

Gran condicional que despacha según el tipo de nodo:

| Nodo         | Qué hace                                                              |
|--------------|-----------------------------------------------------------------------|
| `VarDecl`    | Evalúa la expresión, define la variable en `env`, emite `[VARIABLE]` |
| `Assign`     | Evalúa la expresión, modifica la variable en `env`, emite `[ASIGNAR]`|
| `ConcatDef`  | Evalúa cada parte, concatena según el orden, emite `[CONCAT]`        |
| `PrintStmt`  | Evalúa los argumentos, imprime en terminal, emite `[IMPRIMIR]`       |
| `ExprStmt`   | Evalúa la expresión, emite el resultado con la etiqueta inferida      |
| `IfStmt`     | Evalúa la condición, ejecuta `consequent` o `alternate` según el caso |
| `WhileStmt`  | Repite el bloque mientras la condición sea verdadera (máx 1000 iter) |
| `RepeatStmt` | Ejecuta el bloque exactamente N veces (máx 1000)                     |
| `FunDecl`    | Registra la función en `self.functions`, emite `[FUNCION]`           |
| `ReturnStmt` | Lanza `ReturnValue(val)` para salir de la función actual             |

### Método `eval_expr(node, env)`

Evalúa un nodo de expresión y retorna su valor en Python:

| Nodo        | Resultado                                              |
|-------------|--------------------------------------------------------|
| `Literal`   | Retorna `node.value` directamente                      |
| `Var`       | Busca el nombre en `env` y retorna su valor            |
| `ArrayLit`  | Evalúa cada item y retorna una lista Python            |
| `BinOp`     | Evalúa `left` y `right`, aplica el operador           |
| `RepeatStr` | Repite el texto N veces con `texto * n`               |
| `BinCond`   | Delega a `eval_cond`                                   |
| `CallExpr`  | Delega a `call_fn`                                     |

**Operadores de `BinOp`:**

| Operador | Operación              | Nota                          |
|----------|------------------------|-------------------------------|
| `+`      | Suma o concatenación   | Si alguno es string, concatena|
| `-`      | Resta                  |                               |
| `*`      | Multiplicación         |                               |
| `/`      | División               | Error si divisor es 0         |
| `%`      | Módulo                 |                               |
| `^`      | Potencia               |                               |

### Método `eval_cond(node, env)`

Evalúa una condición. Si el nodo es `BinCond`, compara los dos lados con el operador (`>`, `<`, `>=`, `<=`, `==`, `!=`). Si no es `BinCond`, convierte el valor a booleano Python con `bool()`.

### Método `call_fn(name, arg_nodes, env, line)`

Maneja llamadas a función en dos pasos:

1. **Funciones integradas (built-ins):** Busca el nombre en un diccionario de lambdas. Incluye funciones matemáticas, de cadena, conversión y listas.

2. **Funciones de usuario:** Busca en `self.functions`. Crea un `Environment` hijo del scope global, asigna los argumentos como variables locales, ejecuta el bloque con `exec_block`, y captura `ReturnValue` si se usa `retornar`.

**Built-ins disponibles:**

| Categoría    | Funciones                                                   |
|--------------|-------------------------------------------------------------|
| Matemáticas  | `raiz`, `abs`, `redondear`, `piso`, `techo`, `max`, `min`, `potencia`, `logaritmo`, `seno`, `coseno` |
| Cadenas      | `longitud`, `mayusculas`, `minusculas`                      |
| Conversión   | `numero`, `texto`, `tipo`                                   |
| Listas       | `agregar`, `elemento`, `quitar`                             |

---

## 9. ReturnValue

```python
class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value
```

Un truco clásico en intérpretes: usar una excepción para implementar el `return`. Cuando el intérprete ejecuta `ReturnStmt`, lanza `ReturnValue`. El método `call_fn` lo captura con `except ReturnValue as rv` y extrae el valor de retorno. Si no hay `retornar`, la función devuelve `None`.

---

## 10. Interfaz de Terminal

### `print_banner()`
Imprime el logo ASCII de LexLang con colores ANSI al iniciar.

### `print_results(results)`
Recorre la lista de resultados del intérprete y los muestra formateados con etiqueta y color.

```
[VARIABLE]     => x = 10
[SUMA]         => 13
[IMPRIMIR]     => hola mundo
```

### `run_file(filepath)`
Lee un archivo `.lx`, ejecuta el intérprete, imprime el banner y los resultados, y muestra un resumen de errores al final.

### `repl()`
Modo interactivo. Lee líneas del usuario con `input()`. Acumula líneas en un buffer hasta que el número de `{` sea igual al de `}` (depth ≤ 0), momento en que ejecuta el bloque completo. Comandos especiales:

| Comando    | Función                                  |
|------------|------------------------------------------|
| `.salir`   | Termina el intérprete                    |
| `.limpiar` | Reinicia el entorno (nueva sesión)       |
| `.ayuda`   | Muestra referencia rápida de sintaxis    |
| `.ejemplo` | Carga y ejecuta un programa de ejemplo   |

### `main()`
Punto de entrada del script. Si se ejecuta sin argumentos lanza el REPL; si se pasa un archivo como argumento, lo ejecuta con `run_file`.

```bash
python lexlang.py            # Modo REPL
python lexlang.py mi_prog.lx # Ejecutar archivo
```

---

## Resumen de la arquitectura

```
lexlang.py
│
├── Token / Tipos TK_*         → Unidades mínimas del lenguaje
│
├── Lexer                      → FASE 1: texto → lista de Tokens
│   ├── peek() / advance()
│   └── tokenize()
│
├── Nodos AST (Node y subclases) → Representación estructurada
│   ├── Statements: VarDecl, IfStmt, WhileStmt, FunDecl...
│   └── Expresiones: Literal, Var, BinOp, CallExpr...
│
├── Parser                     → FASE 2: Tokens → AST
│   ├── peek() / consume() / expect()
│   ├── parse_program() / parse_statement()
│   ├── parse_expr() / parse_atom()
│   └── parse_if() / parse_while() / parse_funcion()...
│
├── Environment                → Almacén de variables con scopes
│   ├── get() / set() / define()
│   └── Encadenamiento padre → hijo
│
├── ReturnValue (Exception)    → Mecanismo de retorno de funciones
│
├── Interpreter                → FASE 3: ejecuta el AST
│   ├── run(source)
│   ├── exec_block() / exec_stmt()
│   ├── eval_expr() / eval_cond()
│   └── call_fn() + built-ins
│
└── Interfaz Terminal
    ├── repl()
    ├── run_file()
    └── main()


## 11. Backend Flask y Aplicación Web

El proyecto se puede servir desde un entorno web corriendo `app.py`. Este hace uso de la herramienta `Flask` para exponer un servidor local.

Al enviar peticiones a `/run` a través de la herramienta web proveída y visible en `lexlang.html`, el código proporcionado por el usuario es evaluado. La vista interfaz no solo expone un editor y la salida, sino que además gracias a la respuesta detallada de nuestra versión más moderna de `lexlang.py`, captura e imprime la tabla analítica completa del Lexer y expone de forma directa la organización textual del Ast conformada con la librería de Lark.

Para asegurar que todo funcione, corre el comando: `pip install -r requirements.txt`.
