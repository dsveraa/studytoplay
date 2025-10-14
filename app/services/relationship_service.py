from flask import session

from app.repositories.relationship_repository import RelationsRepository


class RelationsService:
    @staticmethod
    def get_supervisor_student_relation():
        user_id = session.get('usuario_id')
        return RelationsRepository.get_supervisor_student_relation(user_id)
    
    @staticmethod
    def get_link_request(request_id, student_id, response):
        if not request_id or response not in ('aceptada', 'rechazada'):
            raise ValueError("Invalid params")

        request = RelationsRepository.get_link_request(request_id, student_id)

        if not request:
            raise ValueError("Link request not found")
        
        request.estado = response

        if response == 'aceptada':
            existing_relationship = RelationsRepository.check_existing_relationship(request)

            if not existing_relationship:
                new_relationship = RelationsRepository.create_relationship(request)
                RelationsRepository.add(new_relationship)
                # RelationsRepository.commit()
        else:
            request.estado = 'rechazada'
        
        return request
        