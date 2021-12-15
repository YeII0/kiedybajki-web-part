from flask import Blueprint

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates", url_prefix="/admin")

from animechecker.admin import routes_anime
from animechecker.admin import routes_wbijam
from animechecker.admin import routes_ao
from animechecker.admin import routes_okami_subs
from animechecker.admin import routes_animesub
from animechecker.admin import routes_animesub_forum
