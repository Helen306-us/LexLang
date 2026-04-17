# LexLang — Especificación Formal del Lenguaje

> Documento técnico formal que define la **Gramática**, los **Tokens / Patrones / Lexemas** y las **Reglas Semánticas** del lenguaje LexLang v2.0.

---

## Tabla de Contenidos

1. [Tokens, Patrones y Lexemas](#1-tokens-patrones-y-lexemas)
2. [Gramática Formal (BNF / EBNF)](#2-gramática-formal-bnf--ebnf)
3. [Reglas Semánticas](#3-reglas-semánticas)

---

## 1. Tokens, Patrones y Lexemas

Un **token** es la unidad mínima reconocida por el analizador léxico.  
Un **patrón** es la regla (expresión regular) que describe qué cadenas forman ese token.  
Un **lexema** es el fragmento concreto del código fuente que coincide con el patrón.

| Token          | Patrón (Expresión Regular)                      | Ejemplos de Lexema         |
|----------------|-------------------------------------------------|----------------------------|
| `NUMBER`       | `-?[0-9]+(\.[0-9]+)?`                           | `5`, `3.14`, `-7`, `0`     |
| `STRING`       | `"[^"]*"`                                       | `"hola"`, `"mundo"`        |
| `BOOL`         | `verdadero \| falso`                            | `verdadero`, `falso`       |
| `NULL`         | `nulo`                                          | `nulo`                     |
| `KW`           | `var\|si\|sino\|mientras\|repetir\|funcion\|retornar` | `var`, `si`, `funcion`|
| `ID`           | `[a-zA-Z_][a-zA-Z0-9_]*`                       | `x`, `contador`, `suma`    |
| `OP_ARIT`      | `[+\-*/%^]`                                     | `+`, `-`, `*`, `/`, `%`, `^` |
| `OP_COMP`      | `==\|!=\|>=\|<=\|>\|<`                          | `==`, `!=`, `>=`, `<`     |
| `EQ`           | `=`                                             | `=`                        |
| `DCOLON`       | `::`                                            | `::`                       |
| `LPAREN`       | `\(`                                            | `(`                        |
| `RPAREN`       | `\)`                                            | `)`                        |
| `LBRACE`       | `\{`                                            | `{`                        |
| `RBRACE`       | `\}`                                            | `}`                        |
| `LBRACKET`     | `\[`                                            | `[`                        |
| `RBRACKET`     | `\]`                                            | `]`                        |
| `COMMA`        | `,`                                             | `,`                        |
| `NEWLINE`      | `\n`                                            | *(salto de línea)*         |
| `COMMENT`      | `#[^\n]*`                                       | `# esto es comentario`     |
| `EOF`          | `\$`                                            | `$`                        |

> **Nota**: Los comentarios (`#...`) y los espacios en blanco (` `, `\t`, `\r`) son reconocidos pero **descartados** por el Lexer; no generan tokens que lleguen al Parser.

---

## 2. Gramática Formal (BNF / EBNF)

Se usa notación **EBNF** (Extended Backus-Naur Form):
- `{ x }` → cero o más repeticiones de x  
- `[ x ]` → x es opcional (cero o una vez)  
- `( x | y )` → alternativa: x ó y  
- Las cadenas entre comillas dobles son terminales literales

---

### 2.1 Programa

```
programa     ::= { sentencia } EOF
```

---

### 2.2 Sentencias

```
sentencia    ::= declaracion_var
              |  asignacion
              |  concat_def
              |  sentencia_si
              |  sentencia_mientras
              |  sentencia_repetir
              |  declaracion_funcion
              |  sentencia_retornar
              |  sentencia_impr
              |  sentencia_expr
```

---

### 2.3 Declaración de Variable

```
declaracion_var ::= "var" ID "=" expresion
```

**Ejemplo:**
```
var x = 10
var nombre = "Hola"
```

---

### 2.4 Asignación

```
asignacion   ::= ID "=" expresion
```

**Ejemplo:**
```
x = x 1 +
```

---

### 2.5 Concatenación de Cadenas

```
concat_def   ::= def_letra { def_letra } "::" ID
def_letra    ::= ID_MAYUSCULA "=" expresion_atomo
```

> `ID_MAYUSCULA` es un identificador de exactamente una letra en mayúscula.

**Ejemplo:**
```
A="Hola " B="Mundo" :: AB
```

---

### 2.6 Condicional

```
sentencia_si ::= "si" "(" condicion ")" "{" bloque "}"
                 [ "sino" ( sentencia_si | "{" bloque "}" ) ]
```

**Ejemplo:**
```
si (x > 5) {
  impr("mayor")
} sino si (x == 5) {
  impr("igual")
} sino {
  impr("menor")
}
```

---

### 2.7 Bucle Mientras

```
sentencia_mientras ::= "mientras" "(" condicion ")" "{" bloque "}"
```

**Ejemplo:**
```
mientras (i < 10) {
  i = i 1 +
}
```

---

### 2.8 Bucle Repetir

```
sentencia_repetir ::= "repetir" expresion_atomo "{" bloque "}"
```

**Ejemplo:**
```
repetir 3 {
  impr("hola")
}
```

---

### 2.9 Declaración de Función

```
declaracion_funcion ::= "funcion" ID "(" [ lista_params ] ")" "{" bloque "}"
lista_params        ::= ID { "," ID }
```

**Ejemplo:**
```
funcion suma(a, b) {
  retornar a b +
}
```

---

### 2.10 Retorno

```
sentencia_retornar ::= "retornar" expresion
```

---

### 2.11 Impresión

```
sentencia_impr ::= "impr" "(" [ lista_args ] ")"
lista_args     ::= expresion { "," expresion }
```

---

### 2.12 Bloque

```
bloque ::= { NEWLINE } { sentencia { NEWLINE } }
```

---

### 2.13 Condición

```
condicion    ::= expresion OP_COMP expresion
              |  expresion
```

---

### 2.14 Expresión

```
expresion    ::= repeticion_cadena
              |  notacion_postfija
              |  notacion_infija
              |  expresion_atomo

repeticion_cadena ::= NUMBER "*" expresion_atomo

notacion_postfija ::= expresion_atomo expresion_atomo OP_ARIT

notacion_infija   ::= expresion_atomo OP_ARIT expresion_atomo
```

---

### 2.15 Átomo (valor mínimo)

```
expresion_atomo ::= NUMBER
                 |  STRING
                 |  BOOL
                 |  NULL
                 |  ID
                 |  llamada_funcion
                 |  lista_literal
                 |  "(" expresion ")"

llamada_funcion ::= ID "(" [ lista_args ] ")"

lista_literal   ::= "[" [ expresion { "," expresion } ] "]"
```

---

## 3. Reglas Semánticas

Las reglas semánticas definen el **significado** de cada construcción y las restricciones que deben cumplirse en tiempo de ejecución.

---

### 3.1 Tipos de Datos

LexLang maneja los siguientes tipos de datos de forma dinámica (tipado dinámico):

| Tipo       | Descripción                          | Ejemplo                 |
|------------|--------------------------------------|-------------------------|
| `NUMBER`   | Entero o decimal (float de Python)   | `5`, `3.14`, `-7`       |
| `STRING`   | Cadena de texto                      | `"hola"`                |
| `BOOL`     | Booleano                             | `verdadero`, `falso`    |
| `NULL`     | Valor nulo / ausencia de valor       | `nulo`                  |
| `LISTA`    | Colección ordenada de valores        | `[1, 2, 3]`             |
| `FUNCION`  | Función definida por el usuario      | *(objeto interno)*      |

---

### 3.2 Reglas de Declaración y Alcance (Scope)

| Regla | Descripción |
|-------|-------------|
| **R1** | `var x = expr` crea una **nueva** variable en el scope **actual**. Si ya existe en el scope actual, la sobreescribe. |
| **R2** | `x = expr` modifica una variable **ya existente**. Busca en el scope actual y luego en los padres. Si no existe en ninguno, la crea en el scope actual. |
| **R3** | Cada bloque `{ }` (si, mientras, repetir, funcion) crea un **scope hijo** que puede leer variables del padre, pero el padre no puede acceder a las del hijo. |
| **R4** | Las funciones se ejecutan en un scope hijo del **scope global** (no del scope donde se llamaron), por lo que no capturan cierres (*closures*). |
| **R5** | Los parámetros de una función se crean como variables locales en el scope de la función. |

---

### 3.3 Reglas Aritméticas

| Regla | Operador | Tipos permitidos | Resultado |
|-------|----------|-----------------|-----------|
| **R6** | `+` | NUMBER + NUMBER | NUMBER (suma) |
| **R7** | `+` | STRING + cualquiera | STRING (concatenación) |
| **R8** | `-` | NUMBER - NUMBER | NUMBER |
| **R9** | `*` | NUMBER * NUMBER | NUMBER |
| **R10** | `/` | NUMBER / NUMBER | NUMBER — **Error** si divisor == 0 |
| **R11** | `%` | NUMBER % NUMBER | NUMBER (módulo) |
| **R12** | `^` | NUMBER ^ NUMBER | NUMBER (potencia) |

---

### 3.4 Reglas de Comparación

Todos los operadores de comparación devuelven un **BOOL**.

| Operador | Semántica              |
|----------|------------------------|
| `==`     | Igualdad de valor      |
| `!=`     | Diferencia de valor    |
| `>`      | Mayor que              |
| `<`      | Menor que              |
| `>=`     | Mayor o igual que      |
| `<=`     | Menor o igual que      |

---

### 3.5 Reglas de Cadenas

| Regla | Construcción | Semántica |
|-------|--------------|-----------|
| **R13** | `N*"texto"` | Repite la cadena `"texto"` exactamente `N` veces. `N` debe ser NUMBER ≥ 0. |
| **R14** | `A="x" B="y" :: AB` | Concatena las partes en el orden especificado por `AB`. Las letras no presentes en las definiciones se omiten. |

---

### 3.6 Reglas de Control de Flujo

| Regla | Descripción |
|-------|-------------|
| **R15** | La condición de `si` y `mientras` puede ser cualquier expresión. Si no es una comparación explícita, se convierte a BOOL usando las reglas de Python (`0`, `""`, `nulo`, `falso` → falso; cualquier otro valor → verdadero). |
| **R16** | El bucle `mientras` tiene un límite de **1000 iteraciones** para evitar bucles infinitos. Superado ese límite, lanza un error. |
| **R17** | El bucle `repetir N` ejecuta el bloque exactamente `N` veces. Si `N > 1000`, se limita a 1000. |

---

### 3.7 Reglas de Funciones

| Regla | Descripción |
|-------|-------------|
| **R18** | Una función debe ser **declarada antes de ser llamada** en el mismo flujo de ejecución. |
| **R19** | El número de **argumentos** en la llamada debe coincidir exactamente con el número de **parámetros** en la declaración; de lo contrario, se lanza un error. |
| **R20** | Si una función no ejecuta `retornar`, devuelve `nulo` implícitamente. |
| **R21** | `retornar` finaliza inmediatamente la ejecución de la función y devuelve el valor de la expresión. |
| **R22** | Las funciones soportan **recursividad**, pero están sujetas al límite de recursión de Python. Si se excede, se lanza un error controlado. |

---

### 3.8 Reglas de Listas

| Regla | Descripción |
|-------|-------------|
| **R23** | Una lista puede contener valores de **cualquier tipo**, incluyendo otras listas. |
| **R24** | `elemento(lista, i)` accede al elemento en la posición `i` (base 0). Si `i` está fuera de rango, lanza un error de Python. |
| **R25** | `agregar(lista, val)` añade `val` al **final** de la lista y retorna la lista modificada. |
| **R26** | `quitar(lista, i)` elimina y retorna el elemento en la posición `i`. Si no se da `i`, elimina el último. |

---

### 3.9 Reglas del Símbolo de Fin (`$`)

| Regla | Descripción |
|-------|-------------|
| **R27** | Todo programa LexLang **debe terminar** con el símbolo `$`. Si no se encuentra, el Lexer lanza un error léxico antes de comenzar el análisis sintáctico. |
| **R28** | El símbolo `$` solo es válido al final del código. Si aparece en el medio del programa, los tokens posteriores no serán procesados. |

---

### 3.10 Funciones Integradas (Built-ins)

Estas funciones están disponibles sin necesidad de declararlas:

| Función           | Parámetros       | Tipo retorno | Semántica                          |
|-------------------|------------------|--------------|------------------------------------|
| `raiz(n)`         | NUMBER           | NUMBER       | Raíz cuadrada de `n`               |
| `abs(n)`          | NUMBER           | NUMBER       | Valor absoluto de `n`              |
| `redondear(n)`    | NUMBER           | NUMBER       | Redondea al entero más cercano     |
| `piso(n)`         | NUMBER           | NUMBER       | Redondea hacia abajo               |
| `techo(n)`        | NUMBER           | NUMBER       | Redondea hacia arriba              |
| `max(a, b)`       | NUMBER, NUMBER   | NUMBER       | Mayor entre `a` y `b`             |
| `min(a, b)`       | NUMBER, NUMBER   | NUMBER       | Menor entre `a` y `b`             |
| `potencia(b, e)`  | NUMBER, NUMBER   | NUMBER       | `b` elevado a `e`                 |
| `logaritmo(n)`    | NUMBER           | NUMBER       | Logaritmo natural de `n`           |
| `seno(n)`         | NUMBER           | NUMBER       | Seno de `n` (en radianes)          |
| `coseno(n)`       | NUMBER           | NUMBER       | Coseno de `n` (en radianes)        |
| `longitud(s)`     | STRING o LISTA   | NUMBER       | Longitud de la cadena o lista      |
| `mayusculas(s)`   | STRING           | STRING       | Convierte a mayúsculas             |
| `minusculas(s)`   | STRING           | STRING       | Convierte a minúsculas             |
| `numero(v)`       | STRING           | NUMBER       | Convierte texto a número           |
| `texto(v)`        | cualquiera       | STRING       | Convierte valor a cadena           |
| `tipo(v)`         | cualquiera       | STRING       | Nombre del tipo Python del valor   |
| `agregar(l, v)`   | LISTA, cualquiera| LISTA        | Agrega `v` al final de la lista    |
| `elemento(l, i)`  | LISTA, NUMBER    | cualquiera   | Accede al elemento en posición `i` |
| `quitar(l [,i])`  | LISTA [, NUMBER] | cualquiera   | Elimina y retorna el elemento      |

---

## Resumen Visual

```
PROGRAMA LexLang
│
├─ ANÁLISIS LÉXICO
│   ├─ Tokens: NUMBER, STRING, BOOL, NULL, ID, KW, OP, EQ, DCOLON...
│   ├─ Patrones: expresiones regulares que reconocen cada token
│   └─ Fin de programa: símbolo obligatorio '$'
│
├─ ANÁLISIS SINTÁCTICO (Gramática EBNF)
│   ├─ Sentencias: var, si/sino, mientras, repetir, funcion, retornar, impr
│   ├─ Expresiones: postfija (a b +), infija (a + b), repetición (N*"txt"), concat (:: AB)
│   └─ Átomos: literales, variables, llamadas a función, listas, sub-expresiones
│
└─ ANÁLISIS SEMÁNTICO (Reglas)
    ├─ Tipos dinámicos: NUMBER, STRING, BOOL, NULL, LISTA
    ├─ Scope: scopes anidados, funciones en scope global
    ├─ Aritmética: operaciones por tipo, error en división por cero
    ├─ Control de flujo: límite 1000 iter. en bucles
    └─ Funciones: aridad exacta, retorno implícito nulo, recursividad
```

---

## 4. Justificación: Equivalencia entre la Gramática de LexLang y el Árbol de Derivación Clásico

### 4.1 El modelo de referencia

En la teoría de compiladores, una gramática libre de contexto define cómo se pueden derivar cadenas del lenguaje. El árbol de derivación (o árbol sintáctico) es la representación visual de ese proceso. Un ejemplo clásico es la gramática para expresiones aritméticas:

```
cadena → cadena + cadena
       | cadena - cadena
       | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

Para la expresión `9 - 5 + 2`, esta gramática produce el siguiente árbol de derivación:

```
           cadena
          /   |   \
       cadena  +  cadena
      /  |  \         |
  cadena  -  cadena   2
     |           |
     9            5
```

Cada nodo interno es un **no-terminal** (como `cadena`) y cada hoja es un **terminal** (como `9`, `5`, `2`, `+`, `-`).

---

### 4.2 La gramática equivalente en LexLang

LexLang define el mismo concepto a través de su regla `expresion` en la sección 2.14:

```
expresion         → notacion_postfija
                  | notacion_infija
                  | expresion_atomo

notacion_postfija → expresion_atomo expresion_atomo OP_ARIT

expresion_atomo   → NUMBER | STRING | BOOL | NULL | ID
                  | llamada_funcion | lista_literal
```

Reescrita de forma simplificada para la parte aritmética, es **estructuralmente equivalente** a la gramática de referencia:

```
expresion → átomo OP_ARIT átomo       (un nivel)
átomo     → NUMBER | ID | ...
```

La diferencia es únicamente **notacional**: LexLang usa notación **postfija** (el operador va al final), mientras que la gramática de referencia usa notación **infija** (el operador va en el medio). La **estructura del árbol generado es idéntica** en ambos casos.

---

### 4.3 Demostración con un ejemplo concreto

**Entrada en notación infija (gramática de referencia):**
```
9 - 5 + 2
```

**Entrada equivalente en LexLang (notación postfija):**
```
9 5 - 2 +
$
```

**Árbol AST que LexLang construye internamente:**

```
         BinOp( + )
        /           \
   BinOp( - )     Literal(2)
   /         \
Literal(9)  Literal(5)
```

**Árbol de derivación de la gramática de referencia:**

```
           cadena
          /   |   \
       cadena  +  cadena
      /  |  \         |
  cadena  -  cadena   2
     |           |
     9            5
```

Ambos árboles representan **exactamente la misma jerarquía de operaciones**: primero se computa `9 - 5`, y ese resultado se suma con `2`. La estructura de nodos, la profundidad del árbol y el orden de evaluación son **iguales**.

---

### 4.4 Justificación formal

La equivalencia se sostiene sobre tres principios:

| Principio | Gramática de referencia | LexLang |
|-----------|------------------------|---------|
| **No-terminales** | `cadena` (se puede expandir) | Nodos `BinOp`, `Literal`, `Var`, `CallExpr`... |
| **Terminales** | `0`, `1`, `+`, `-` ... | Tokens `NUMBER`, `OP`, `ID`... |
| **Regla de producción** | `cadena → cadena OP cadena` | `notacion_postfija → átomo átomo OP` |
| **Árbol resultante** | Árbol de derivación con nodos internos y hojas | AST con nodos `BinOp` como internos y `Literal`/`Var` como hojas |

En ambas gramáticas se cumple la propiedad fundamental de los árboles de derivación:

> **Los nodos internos corresponden a reglas gramaticales (no-terminales) y los nodos hoja corresponden a los valores atómicos del lenguaje (terminales).**

La única diferencia entre el árbol de LexLang y el árbol de la gramática de referencia es que LexLang **no incluye el operador como nodo hoja separado**: en lugar de eso, el operador es un atributo del nodo `BinOp`. Esto es la diferencia entre un **árbol de derivación concreto** (que incluye todos los símbolos) y un **árbol de sintaxis abstracta (AST)** (que comprime la información, guardando el operador como dato del nodo).

---

### 4.5 Resumen de la equivalencia

```
GRAMÁTICA CLÁSICA              LEXLANG (AST)
─────────────────────────────────────────────────────
cadena → cadena OP cadena  ≡  BinOp(op, left, right)
cadena → dígito            ≡  Literal(value)
cadena → variable          ≡  Var(name)
cadena → f(args)           ≡  CallExpr(name, args)

Árbol de derivación        ≡  Árbol AST de LexLang
(incluye el OP como hoja)      (OP como atributo del nodo)
```

**Conclusión:** El árbol que LexLang genera y visualiza con D3.js sigue el mismo principio teórico que los árboles de derivación de la teoría formal de lenguajes y compiladores. La única diferencia es que LexLang genera un **AST** (forma comprimida y práctica), mientras que el árbol de referencia es un **árbol de derivación concreto** (forma expandida y pedagógica). Ambas representaciones son matemáticamente equivalentes y derivan de la misma gramática subyacente.
