from log3 import ejecutar_con_log


# =========================================================
# FUNCIONES DE NEGOCIO
# =========================================================

def cargar_datos(logger):
    logger.info("Cargando datos")
    return {"ventas": [10, 20, 30, None, 50]}


def limpiar_datos(datos, logger):
    logger.info("Limpiando datos")

    try:
        datos["ventas"] = [v for v in datos["ventas"] if v is not None]
    except Exception as e:
        logger.error(f"Error limpieza: {e}")

    return datos


def calcular_kpis(datos, logger):
    logger.info("Calculando KPIs")

    total = sum(datos["ventas"])
    media = total / len(datos["ventas"])

    return {"total": total, "media": media}


def exportar(kpis, logger):
    logger.info("Exportando")

    print("EXPORT OK:", kpis)


# =========================================================
# MAIN (PIPELINE - SOLO LÓGICA)
# =========================================================

def main(logger):

    logger.step("INICIO PIPELINE")

    # -------------------------
    # CARGA (CRÍTICO)
    # -------------------------
    try:
        logger.step("CARGA")
        datos = cargar_datos(logger)

    except Exception as e:
        logger.error(f"Error crítico carga: {e}")
        raise

    # -------------------------
    # LIMPIEZA (NO CRÍTICO)
    # -------------------------
    try:
        logger.step("LIMPIEZA")
        datos = limpiar_datos(datos, logger)

    except Exception as e:
        logger.error(f"Error limpieza: {e}")

    # -------------------------
    # KPIS (CRÍTICO)
    # -------------------------
    try:
        logger.step("KPIS")
        kpis = calcular_kpis(datos, logger)

    except Exception as e:
        logger.error(f"Error KPIs: {e}")
        raise

    # -------------------------
    # EXPORT (CRÍTICO)
    # -------------------------
    try:
        logger.step("EXPORT")
        exportar(kpis, logger)

    except Exception as e:
        logger.error(f"Error exportación: {e}")
        raise

    logger.success("PIPELINE FINALIZADO")


# =========================================================
# RUN (DECORADOR + CONTROL EJECUCIÓN)
# =========================================================

@ejecutar_con_log(
    alerta=True,
    cerrar_auto=True,
    delay_cierre=5
)
def run(logger):
    """
    Punto de entrada del script
    """
    main(logger)


# =========================================================
# ENTRY POINT PYTHON
# =========================================================

if __name__ == "__main__":
    run()