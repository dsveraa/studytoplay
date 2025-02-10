from datetime import timedelta

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