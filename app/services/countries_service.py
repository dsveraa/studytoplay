from app.models import Pais
from app.models import Monedas
from sqlalchemy.orm import joinedload


def get_countries() -> list:
    '''
    Devuelve una lista de paises con su Id, Nombre, Moneda y Símbolo.
    '''
    countries = (
        Pais.query
        .options(
            joinedload(Pais.moneda).joinedload(Monedas.simbolo)
        )
        .all()
    )
    return [
        {
            "id": pais.id,
            "pais": pais.nombre,
            "moneda": pais.moneda.nombre,
            "simbolo": pais.moneda.simbolo.simbolo,
        }
        for pais in countries
    ]
