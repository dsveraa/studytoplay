from datetime import timedelta
from app.models import Nivel, Trofeo, Premio, Usuario, Estrella, AcumulacionTiempo, Tiempo, NuevaNotificacion, Notificaciones, SolicitudVinculacion, SupervisorEstudiante, Asignatura, RegistroNotas

from .. import db
from functools import wraps
from flask import session, jsonify, url_for
from sqlalchemy.orm import aliased
from sqlalchemy import desc
from app.utils.debugging import printn

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'status': 'unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapped

def supervisor_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'supervisor_id' not in session:
            return jsonify({'status': 'unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapped

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
# HORA = 500
CHECKPOINT = HORA * 2 # suma una estrella
TIEMPO_MAXIMO = CHECKPOINT * 5 # pasa de nivel
BONIFICACION = CHECKPOINT // 2  # resultado para aplicar multiplicador 

def asignar_estrellas(id: int) -> int:
    tiempo_acumulado = revisar_acumulacion_tiempo(id)
    tiempo_ciclo = tiempo_acumulado.cantidad
    print(f'{tiempo_ciclo=}')
    estrellas_obj = revisar_estrellas(id)
    nivel_estrellas = [5, 4, 3, 2, 1]


    for estrellas in nivel_estrellas:
        if tiempo_ciclo >= CHECKPOINT * estrellas:
            ''' CP * 5 = 36_000_000
                CP * 4 = 28_800_000
                CP * 3 = 21_600_000
                CP * 2 = 14_400_000
                CP * 1 = 7_200_000 
            '''
            estrellas_obj.cantidad = estrellas
            print(f'{estrellas=}')
            db.session.commit()
            break


def asignar_nivel(id: int) -> int:
    estrellas_obj = revisar_estrellas(id)
    nivel_obj = revisar_nivel(id)
    tiempo_obj = revisar_acumulacion_tiempo(id)
        
    if estrellas_obj.cantidad > 4:
        estrellas_obj.cantidad = 0
        nuevo_nivel = nivel_obj.nivel + 1
        nivel_obj.nivel = nuevo_nivel
        tiempo_obj.cantidad -= TIEMPO_MAXIMO
        # tiempo_total_obj = revisar_tiempo_total(id)
        # tiempo_total_obj.tiempo += BONIFICACION * nuevo_nivel
        db.session.commit()
        # return print(f'Has pasado a nivel {nivel_obj.nivel} y tienes una nueva bonificación de tiempo!')
        return print(f'Has pasado a nivel {nivel_obj.nivel}!') if nivel_obj.nivel < 4 else None

def asignar_trofeos(id: int) -> int:
    nivel_obj = revisar_nivel(id)
    trofeos_obj = revisar_trofeos(id)

    if nivel_obj.nivel > 3:
        trofeos_obj.cantidad += 1
        nivel_obj.nivel = 0
        db.session.commit()
        return print(f'Has ganado un nuevo trofeo! Tienes {trofeos_obj.cantidad} en total.')
    
def revisar_nuevas_notificaciones(id):
    nueva_notificacion = NuevaNotificacion.query.filter_by(usuario_id=id).first()
    session['nueva_notificacion'] = nueva_notificacion.estado
    return

def enviar_notificacion_link_request(sid, uid): # "nombre@email.com" solicita supervisar tu cuenta [aceptar] [rechazar]
    
    supervisor = Usuario.query.get_or_404(sid)
    email = supervisor.correo

    query = (
        SolicitudVinculacion.query
        .filter_by(estudiante_id=uid)
        .order_by(desc(SolicitudVinculacion.id))
        .first()
    )
    
    id_solicitud = query.id

    mensaje_html = f'''
<div id="solicitud-{id_solicitud}">
    <b>{email}</b> requests to supervise your account.
    <span id="acciones-{id_solicitud}">
        <iconify-icon 
            icon="ix:thumb-up-filled" 
            width="24" 
            height="24" 
            style="cursor: pointer; margin-right: 4px; vertical-align: middle; color: #beda23" 
            onclick="responderSolicitud({id_solicitud}, 'aceptada')">
        </iconify-icon>
        <iconify-icon 
            icon="ix:thumb-down-filled" 
            width="24" 
            height="24" 
            style="cursor: pointer; vertical-align: middle; color: #fb7833" 
            onclick="responderSolicitud({id_solicitud}, 'rechazada')">
        </iconify-icon>
    </span>
</div>
'''
   
    notificacion_lr = Notificaciones(usuario_id=uid, notificacion=mensaje_html, leida=False)
    nueva_notificacion = NuevaNotificacion.query.filter_by(usuario_id=uid).first()
    nueva_notificacion.estado = True
    
    db.session.add(notificacion_lr)
    db.session.commit()

def enviar_notificacion_respuesta_lr(s_correo, respuesta, uid):
    if respuesta == 'aceptada':
        mensaje_html = f'''
The <b>{s_correo}</b> request has been accepted.
'''
    else:
        mensaje_html = f'''
The <b>{s_correo}</b> request has been declined.
'''
    notificacion_respuesta = Notificaciones(usuario_id=uid, notificacion=mensaje_html)
    db.session.add(notificacion_respuesta)
    db.session.commit()

def listar_asignaturas(id):
    asignaturas_obj = Asignatura.query.filter_by(usuario_id=id).all()
    return [
        {
            'id': asignatura.id, 
            'nombre': asignatura.nombre
        } 
        for asignatura in asignaturas_obj
    ]

def listar_registro_notas(id):
    return RegistroNotas.query.filter_by(usuario_id=id).order_by(desc(RegistroNotas.id)).all()
