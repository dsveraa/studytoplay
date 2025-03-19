from datetime import timedelta
from app.models import Nivel, Trofeo, Premio, Usuario, Estrella, AcumulacionTiempo, Tiempo
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
    return (tiempo_asignatura / tiempo_total) * 100 if tiempo_asignatura and tiempo_total else 0

def revisar_nivel(id: int) -> int:
    nivel = Nivel.query.filter_by(usuario_id=id).first() 
    if nivel is None:
        print(f"No se encontró nivel con id {id}")
    return nivel

def mostrar_nivel(id: int) -> int:
    nivel_actual = revisar_nivel(id)
    if not nivel_actual:
        nuevo_nivel = Nivel(usuario_id=id, nivel=0)
        db.session.add(nuevo_nivel)
        db.session.commit()
        print(f"Se asignó nivel: 0 al id: {id}")
        return 0
    return nivel_actual.nivel

def revisar_estrellas(id: int) -> int:
    estrellas = Estrella.query.filter_by(usuario_id=id).first()
    if estrellas is None:
        print(f"No se encontraron estrellas con id {id}")
    return estrellas

def mostrar_estrellas(id: int) -> int:
    estrellas_existentes = revisar_estrellas(id)
    if not estrellas_existentes:
        nueva_estrella = Estrella(usuario_id=id, cantidad=0)
        db.session.add(nueva_estrella)
        db.session.commit()
        return 0
    return estrellas_existentes.cantidad

def crear_plantilla_estrellas(estrellas):
    plantilla_estrellas = [1] * estrellas  
    
    while len(plantilla_estrellas) < 5:
        plantilla_estrellas.append(0)
    
    return plantilla_estrellas

def revisar_trofeos(id: int) -> int:
    trofeos = Trofeo.query.filter_by(usuario_id=id).first()
    if trofeos is None:
        print(f"No se encontraron trofeos con id {id}")
    return trofeos

def mostrar_trofeos(id: int) -> int:
    trofeos_existentes = revisar_trofeos(id)
    if not trofeos_existentes:
        nuevo_trofeo = Trofeo(usuario_id=id, cantidad=0)
        db.session.add(nuevo_trofeo)
        db.session.commit()
        return 0
    return trofeos_existentes.cantidad

def revisar_acumulacion_tiempo(id: int) -> float:
    acumulacion_tiempo = AcumulacionTiempo.query.filter_by(usuario_id=id).first()
    if acumulacion_tiempo is None:
        raise ValueError(f"No se encontró acumulación de tiempo con id {id}")
    return acumulacion_tiempo

def revisar_tiempo_total(id: int) -> float:
    tiempo_total = Tiempo.query.filter_by(usuario_id=id).first()
    if tiempo_total is None:
        raise ValueError(f"No se encontró tiempo total con id {id}")
    return tiempo_total

HORA = 3_600_000
CHECKPOINT = HORA * 2
TIEMPO_MAXIMO = CHECKPOINT * 5
BONIFICACION = CHECKPOINT // 2 

def asignar_estrellas(id: int) -> int:
    tiempo_acumulado = revisar_acumulacion_tiempo(id)
    tiempo = tiempo_acumulado.cantidad
    print(f'{tiempo=}')
    estrellas_obj = revisar_estrellas(id)
    estrellas_iniciales = estrellas_obj.cantidad
    nivel_estrellas = [5, 4, 3, 2, 1]

    for estrellas in nivel_estrellas:
        if tiempo >= CHECKPOINT * estrellas:
            estrellas_obj.cantidad = estrellas
            print(f'{estrellas=}')
            db.session.commit()
            print(f'Has ganado una nueva estrella, ¡felicidades!, tienes {estrellas} en total.') if estrellas_iniciales < estrellas_obj.cantidad else None
            break


def asignar_nivel(id: int) -> int:
    estrellas_obj = revisar_estrellas(id)
    nivel_obj = revisar_nivel(id)
    tiempo_obj = revisar_acumulacion_tiempo(id)
        
    if estrellas_obj.cantidad == 5:
        estrellas_obj.cantidad = 0
        nuevo_nivel = nivel_obj.nivel + 1
        nivel_obj.nivel = nuevo_nivel
        tiempo_obj.cantidad -= TIEMPO_MAXIMO
        tiempo_total_obj = revisar_tiempo_total(id)
        tiempo_total_obj.tiempo += BONIFICACION * nuevo_nivel
        db.session.commit()
        return print(f'Has pasado a nivel {nivel_obj.nivel} y tienes una nueva bonificación de tiempo!')

def asignar_trofeos(id: int) -> int:
    nivel_obj = revisar_nivel(id)
    trofeos_obj = revisar_trofeos(id)

    if nivel_obj.nivel == 4:
        trofeos_obj.cantidad += 1
        nivel_obj.nivel = 0
        db.session.commit()
        return print(f'Has ganado un nuevo trofeo! Tienes {trofeos_obj.cantidad} en total.')