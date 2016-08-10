from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)


@main.app_context_processor # make variables grlobally availabl to all templates
def inject_permissions():
	return dict(Permission = Permission)


from . import views, errors # import here to avoid circular dependencies