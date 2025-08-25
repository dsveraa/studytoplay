import operator
import re
from app.utils.sistemas_notas_utils import sistemas

OPERADORES = {
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
    "==": operator.eq,
    "=": operator.eq,
}

OP_REGEX = r"(>=|<=|>|<|==|=)(.+)"

def parse_filtro(filtro, sistema_orden):
    if callable(filtro) or not isinstance(filtro, str):
        return filtro

    match = re.match(OP_REGEX, filtro.strip())
    if not match:
        return filtro

    op, val = match.groups()

    def compare(x):
        if sistema_orden:
            try:
                ix_x = sistema_orden.index(x)
                ix_val = sistema_orden.index(val)
                return OPERADORES[op](ix_x, ix_val)
            except ValueError:
                return False
        else:
            try:
                return OPERADORES[op](x, float(val))
            except ValueError:
                return False

    return compare

def elegir_sistema_calificaciones(sistema: str, *filtros) -> list:
    datos_sistema = sistemas.get(sistema)
    if datos_sistema is None:
        raise ValueError(f"Sistema '{sistema}' no encontrado.")

    valores = datos_sistema["valores"]
    orden = datos_sistema["orden"]

    filtros_procesados = [parse_filtro(f, orden) for f in filtros]

    return [
        item for item in valores
        if any(f(item) if callable(f) else item == f for f in filtros_procesados)
    ]

# print(elegir_sistema_calificaciones(1, ">B"))
# print(elegir_sistema_calificaciones(11, ">=6.0", "=7.0"))
# print(elegir_sistema_calificaciones(6, "<=3", "=1"))
