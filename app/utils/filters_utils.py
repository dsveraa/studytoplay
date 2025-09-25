import datetime
import markdown

def register_filters(app):
    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown.markdown(text or "", extensions=["extra", "fenced_code", "tables"])

    @app.template_filter('ms_to_hms')
    def ms_to_hms_filter(ms):
        if ms is None:
            ms = 0
        segundos_totales = int(abs(ms) // 1000)
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60

        signo = '-' if ms < 0 else ''
        return f"{signo}{int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}"


