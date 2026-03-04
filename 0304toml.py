import tomllib
from datetime import datetime
from calendar import month_name

# -----------------------------
# Función helper para cargar TOML
# -----------------------------
def cargar_config(ruta="config.toml"):
    """
    Carga un archivo TOML y lo devuelve como diccionario.
    """
    with open(ruta, "rb") as f:
        return tomllib.load(f)

# -----------------------------
# Cargar configuración
# -----------------------------
config = cargar_config()
calendario = config["calendario_factura"]

# -----------------------------
# Obtener fecha actual
# -----------------------------
hoy = datetime.now()
mes_actual = hoy.month  # 1 = enero, 2 = febrero ...
dia_actual = hoy.day

# -----------------------------
# Crear lista de meses en orden
# -----------------------------
# month_name devuelve tupla: [0] vacío, [1] = enero ...
meses = [month_name[i].lower() for i in range(1, 13)]

# -----------------------------
# Determinar mes y día a usar
# -----------------------------
# Obtener día de facturación del mes actual
mes_nombre = meses[mes_actual - 1]  # ejemplo: "febrero"
dia_mes = calendario[mes_nombre]

if dia_actual < dia_mes:
    # Hoy es antes del día del mes en el calendario
    dia_a_usar = dia_mes
    mes_a_usar = mes_nombre
else:
    # Hoy ya pasó, usar el mes siguiente
    mes_siguiente_index = (mes_actual) % 12  # %12 para volver a enero si es diciembre
    mes_a_usar = meses[mes_siguiente_index]
    dia_a_usar = calendario[mes_a_usar]

# -----------------------------
# Simular HTML de mail con marcador
# -----------------------------
html_msg = """
<html>
<body>
<p>Hola,</p>
<p>El próximo día de facturación es: #DIA_MES#</p>
<p>Saludos</p>
</body>
</html>
"""

# -----------------------------
# Reemplazar marcador
# -----------------------------
# El formato que queremos: "día mes" (ej: "21 febrero")
reemplazo = f"{dia_a_usar} {mes_a_usar}"
html_msg_final = html_msg.replace("#DIA_MES#", reemplazo)

# -----------------------------
# Mostrar resultado final
# -----------------------------
print(html_msg_final)