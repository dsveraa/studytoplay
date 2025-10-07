from app.repositories.link_request_respository import LinkRequestRepository
from app.repositories.supervisor_student_respository import SupervisorStudentRepository


class LinkRequestService:
    @staticmethod
    def make_link_request(super_id, student_id):
        relation = SupervisorStudentRepository.get_relation(super_id, student_id)
        
        if relation:
            raise ValueError('This supervisor account is already following the student.')
        
        status = LinkRequestRepository.get_status(super_id, student_id)
        
        if status == 'pendiente':
            raise ValueError('There is a pending link request for this student.')
            
        query = LinkRequestRepository.set_query(super_id, student_id)
        LinkRequestRepository.add_link_request(query)
        LinkRequestRepository.commit()
