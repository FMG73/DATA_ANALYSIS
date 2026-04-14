from log3 import ejecutar_con_log


# =========================================================
# FUNCIONES (SIN LOGGER)
# =========================================================

def cargar_datos():
    return {"ventas": [10, 20, 30]}


def transformar_datos(datos):
    # error controlado
    datos["ventas"] = datos["ventas"]
    return datos


# =========================================================
# PIPELINE (CON LOGGER)
# =========================================================

def ejecutar_pipeline(logger):

    logger.step("INICIO")

    # -------------------------
    # CARGA (CRÍTICO)
    # -------------------------
    try:
        logger.step("CARGA DATOS")
        datos = cargar_datos()

    except Exception as e:
        logger.error(f"Error crítico en carga: {e}")
        raise

    # -------------------------
    # TRANSFORMACIÓN (NO CRÍTICO)
    # -------------------------
    try:
        logger.step("TRANSFORMACIÓN")
        datos = transformar_datos(datos)

    except Exception as e:
        logger.error(f"Error transformación: {e}")

    logger.success("FIN PIPELINE")


# =========================================================
# MAIN
# =========================================================

def main(logger):
    ejecutar_pipeline(logger)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main_decorado = ejecutar_con_log(
        alerta=True,
        cerrar_auto=True,
        delay_cierre=5
    )(main)

    main_decorado()