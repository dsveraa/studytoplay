from datetime import timedelta
from app.models import Nivel, Trofeo, Premio, Usuario, Estrella
from typing import List, Dict, Tuple
from sqlalchemy.orm import sessionmaker
from .. import db

def agrupar_tiempos(estudios, asignatura):
    return [{
        'fecha_inicio': estudio['fecha_inicio'],
        'fecha_fin': estudio['fecha_fin']
    }
    for estudio in estudios if estudio['asignatura'] == asignatura]

def sumar_tiempos(datos_estudio, asignatura):
    tiempos = agrupar_tiempos(datos_estudio, asignatura)
    tiempo_total = timedelta()

    for tiempo in tiempos:
        nuevo_tiempo = tiempo['fecha_fin'] - tiempo['fecha_inicio']
        tiempo_total += nuevo_tiempo

    return tiempo_total

def porcentaje_tiempos(tiempo_asignatura, tiempo_total):
    return (tiempo_asignatura / tiempo_total) * 100

def revisar_nivel(id: int) -> bool:
    return Nivel.query.filter_by(usuario_id=id).first()

def asignar_nivel(id: int) -> int:
    nivel_existente = revisar_nivel(id)
    if not nivel_existente:
        nuevo_nivel = Nivel(usuario_id=id, nivel=0)
        db.session.add(nuevo_nivel)
        db.session.commit()
        return 0
    return nivel_existente.nivel

def revisar_estrellas(id: int) -> int:
    return Estrella.query.filter_by(usuario_id=id).first()

def asignar_estrellas(id: int) -> int:
    estrellas_existentes = revisar_estrellas(id)
    if not estrellas_existentes:
        nueva_estrella = Estrella(usuario_id=id, cantidad=0)
        db.session.add(nueva_estrella)
        db.session.commit()
        return 0
    return estrellas_existentes.cantidad

def revisar_trofeos(id: int) -> int:
    return Trofeo.query.filter_by(usuario_id=id).first()

def asignar_trofeos(id: int) -> int:
    trofeos_existentes = revisar_trofeos(id)
    if not trofeos_existentes:
        nuevo_trofeo = Trofeo(usuario_id=id, cantidad=0)
        db.session.add(nuevo_trofeo)
        db.session.commit()
        return 0
    return trofeos_existentes.cantidad
