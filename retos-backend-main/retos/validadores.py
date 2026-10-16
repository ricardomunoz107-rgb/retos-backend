import ast
import operator


class CodigoNoPermitido(ValueError):
    pass


OPERADORES_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

OPERADORES_UNARIOS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
}

OPERADORES_COMPARACION = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

FUNCIONES_PERMITIDAS = {
    "abs": abs,
    "len": len,
    "max": max,
    "min": min,
}


def _contabilizar(presupuesto):
    presupuesto[0] -= 1
    if presupuesto[0] < 0:
        raise CodigoNoPermitido("El programa supera el límite de operaciones.")


def _limitar_valor(valor):
    if isinstance(valor, int) and valor.bit_length() > 256:
        raise CodigoNoPermitido("El resultado numérico es demasiado grande.")
    if isinstance(valor, (str, list, tuple)) and len(valor) > 1000:
        raise CodigoNoPermitido("El resultado es demasiado grande.")
    return valor


def _evaluar_expresion(nodo, variables, presupuesto):
    _contabilizar(presupuesto)

    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float, str, bool)):
        return nodo.value
    if isinstance(nodo, ast.Name) and nodo.id in variables:
        return variables[nodo.id]
    if isinstance(nodo, (ast.List, ast.Tuple)):
        valores = [_evaluar_expresion(item, variables, presupuesto) for item in nodo.elts]
        return _limitar_valor(valores if isinstance(nodo, ast.List) else tuple(valores))
    if isinstance(nodo, ast.Subscript):
        contenedor = _evaluar_expresion(nodo.value, variables, presupuesto)
        indice = _evaluar_expresion(nodo.slice, variables, presupuesto)
        if not isinstance(contenedor, (str, list, tuple)) or not isinstance(indice, int):
            raise CodigoNoPermitido("Solo se permite indexar textos o listas con números.")
        return contenedor[indice]
    if isinstance(nodo, ast.BinOp) and type(nodo.op) in OPERADORES_BINARIOS:
        izquierdo = _evaluar_expresion(nodo.left, variables, presupuesto)
        derecho = _evaluar_expresion(nodo.right, variables, presupuesto)
        if isinstance(nodo.op, ast.Pow):
            if not isinstance(derecho, (int, float)) or abs(derecho) > 10:
                raise CodigoNoPermitido("El exponente debe estar entre -10 y 10.")
        return _limitar_valor(OPERADORES_BINARIOS[type(nodo.op)](izquierdo, derecho))
    if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in OPERADORES_UNARIOS:
        valor = _evaluar_expresion(nodo.operand, variables, presupuesto)
        return _limitar_valor(OPERADORES_UNARIOS[type(nodo.op)](valor))
    if isinstance(nodo, ast.BoolOp):
        valores = [_evaluar_expresion(item, variables, presupuesto) for item in nodo.values]
        if isinstance(nodo.op, ast.And):
            return all(valores)
        if isinstance(nodo.op, ast.Or):
            return any(valores)
    if isinstance(nodo, ast.Compare):
        izquierdo = _evaluar_expresion(nodo.left, variables, presupuesto)
        for operador, comparador in zip(nodo.ops, nodo.comparators):
            if type(operador) not in OPERADORES_COMPARACION:
                break
            derecho = _evaluar_expresion(comparador, variables, presupuesto)
            if not OPERADORES_COMPARACION[type(operador)](izquierdo, derecho):
                return False
            izquierdo = derecho
        else:
            return True
    if isinstance(nodo, ast.IfExp):
        rama = nodo.body if _evaluar_expresion(nodo.test, variables, presupuesto) else nodo.orelse
        return _evaluar_expresion(rama, variables, presupuesto)
    if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
        funcion = FUNCIONES_PERMITIDAS.get(nodo.func.id)
        if funcion is not None and not nodo.keywords:
            argumentos = [_evaluar_expresion(arg, variables, presupuesto) for arg in nodo.args]
            return _limitar_valor(funcion(*argumentos))
    raise CodigoNoPermitido("Usa solo operaciones, variables, comparaciones y funciones básicas permitidas.")


def _ejecutar_bloque(instrucciones, variables, salida, presupuesto):
    for instruccion in instrucciones:
        _contabilizar(presupuesto)

        if isinstance(instruccion, ast.Assign) and len(instruccion.targets) == 1:
            destino = instruccion.targets[0]
            if not isinstance(destino, ast.Name) or destino.id.startswith("_"):
                raise CodigoNoPermitido("Solo se permiten asignaciones a variables simples.")
            variables[destino.id] = _evaluar_expresion(instruccion.value, variables, presupuesto)
        elif isinstance(instruccion, ast.AugAssign):
            if not isinstance(instruccion.target, ast.Name) or type(instruccion.op) not in OPERADORES_BINARIOS:
                raise CodigoNoPermitido("Esa asignación no está permitida.")
            actual = variables.get(instruccion.target.id)
            if actual is None:
                raise CodigoNoPermitido("Asigna un valor a la variable antes de modificarla.")
            valor = _evaluar_expresion(instruccion.value, variables, presupuesto)
            if isinstance(instruccion.op, ast.Pow) and (
                not isinstance(valor, (int, float)) or abs(valor) > 10
            ):
                raise CodigoNoPermitido("El exponente debe estar entre -10 y 10.")
            variables[instruccion.target.id] = _limitar_valor(
                OPERADORES_BINARIOS[type(instruccion.op)](actual, valor)
            )
        elif isinstance(instruccion, ast.Expr) and isinstance(instruccion.value, ast.Call):
            llamada = instruccion.value
            if (
                not isinstance(llamada.func, ast.Name)
                or llamada.func.id != "print"
                or len(llamada.args) != 1
                or llamada.keywords
            ):
                raise CodigoNoPermitido("Usa print() con un solo valor para mostrar la respuesta.")
            valor = _evaluar_expresion(llamada.args[0], variables, presupuesto)
            if not isinstance(valor, (int, float, str, bool)):
                raise CodigoNoPermitido("print() solo puede mostrar un número, texto o valor lógico.")
            salida.append(str(valor))
            if sum(map(len, salida)) > 1000:
                raise CodigoNoPermitido("La salida del programa es demasiado grande.")
        elif isinstance(instruccion, ast.If):
            condicion = _evaluar_expresion(instruccion.test, variables, presupuesto)
            bloque = instruccion.body if condicion else instruccion.orelse
            _ejecutar_bloque(bloque, variables, salida, presupuesto)
        elif isinstance(instruccion, ast.For):
            if (
                not isinstance(instruccion.target, ast.Name)
                or not isinstance(instruccion.iter, ast.Call)
                or not isinstance(instruccion.iter.func, ast.Name)
                or instruccion.iter.func.id != "range"
                or instruccion.iter.keywords
                or not 1 <= len(instruccion.iter.args) <= 3
            ):
                raise CodigoNoPermitido("Los ciclos permitidos deben usar range() con límites pequeños.")
            argumentos = [
                _evaluar_expresion(arg, variables, presupuesto)
                for arg in instruccion.iter.args
            ]
            if any(not isinstance(arg, int) for arg in argumentos):
                raise CodigoNoPermitido("range() solo acepta límites enteros.")
            iteraciones = range(*argumentos)
            if len(iteraciones) > 100:
                raise CodigoNoPermitido("Cada ciclo puede tener como máximo 100 iteraciones.")
            for valor in iteraciones:
                variables[instruccion.target.id] = valor
                _ejecutar_bloque(instruccion.body, variables, salida, presupuesto)
            if instruccion.orelse:
                _ejecutar_bloque(instruccion.orelse, variables, salida, presupuesto)
        else:
            raise CodigoNoPermitido("Esa instrucción de Python no está permitida.")


def ejecutar_codigo_restringido(codigo):
    if not codigo.strip() or len(codigo) > 2000:
        raise CodigoNoPermitido("Escribe una solución de hasta 2000 caracteres.")

    try:
        arbol = ast.parse(codigo, mode="exec")
    except SyntaxError as error:
        raise CodigoNoPermitido("Hay un error de sintaxis en tu código.") from error

    if sum(1 for _ in ast.walk(arbol)) > 250:
        raise CodigoNoPermitido("El código es demasiado complejo para este editor.")

    salida = []
    _ejecutar_bloque(arbol.body, {}, salida, [500])
    return "\n".join(salida)
