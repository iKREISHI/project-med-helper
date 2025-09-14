from split_settings.tools import include
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

include("commons.py")
include("auth.py")
include("installed_apps.py")
include("middleware.py")
include("locale.py")
include("templates.py")
include("database.py")
include("rest_framework.py")
include("storage.py")
include("logs.py")