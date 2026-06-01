from jira import JIRA

# =========================
# CONFIGURACIÓN
# =========================

JIRA_URL = "https://tuempresa.atlassian.net"
EMAIL = "tu_correo@empresa.com"
API_TOKEN = "tu_token"

# =========================
# CONEXIÓN
# =========================

jira = JIRA(
    server=JIRA_URL,
    basic_auth=(EMAIL, API_TOKEN)
)

# =========================
# PROBAR CONEXIÓN
# =========================

usuario = jira.myself()

print(usuario["displayName"])