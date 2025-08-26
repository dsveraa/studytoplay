import datetime
import markdown

def register_filters(app):
    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown.markdown(text or "", extensions=["extra", "fenced_code", "tables"])

    @app.template_filter('ms_to_hms')
    def ms_to_hms_filter(ms):
        segundos = ms // 1000 if ms else 0
        return str(datetime.timedelta(seconds=segundos))
