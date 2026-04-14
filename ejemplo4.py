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


def exportar_datos(kpis, logger):
    logger.info("Exportando datos")
    print("EXPORT OK:", kpis)


# =========================================================
# MAIN (PIPELINE)
# =========================================================

def ejecutar_pipeline(logger):

    logger.step("INICIO PIPELINE")

    # -------------------------
    # CARGA (CRÍTICO)
    # -------------------------
    try:
        logger.step("CARGA DATOS")
        datos = cargar_datos(logger)

    except Exception as e:
        logger.error(f"Error crítico en carga: {e}")
        raise

    # -------------------------
    # LIMPIEZA (NO CRÍTICO)
    # -------------------------
    try:
        logger.step("LIMPIEZA DATOS")
        datos = limpiar_datos(datos, logger)

    except Exception as e:
        logger.error(f"Error en limpieza: {e}")

    # -------------------------
    # KPIS (CRÍTICO)
    # -------------------------
    try:
        logger.step("CÁLCULO KPIs")
        kpis = calcular_kpis(datos, logger)

    except Exception as e:
        logger.error(f"Error KPIs: {e}")
        raise

    # -------------------------
    # EXPORTACIÓN (CRÍTICO)
    # -------------------------
    try:
        logger.step("EXPORTACIÓN")
        exportar_datos(kpis, logger)

    except Exception as e:
        logger.error(f"Error exportación: {e}")
        raise

    logger.success("PIPELINE FINALIZADO")


# =========================================================
# EJECUCIÓN BASE (SIN DECORADOR)
# =========================================================

def ejecutar_base(logger):
    ejecutar_pipeline(logger)


# =========================================================
# CONFIGURADOR DE EJECUCIÓN (ANTES get_run)
# =========================================================

def configurar_ejecucion(
    alerta=True,
    cerrar_auto=True,
    delay_cierre=5
):
    """
    Devuelve una función de ejecución configurada dinámicamente
    """

    @ejecutar_con_log(
        alerta=alerta,
        cerrar_auto=cerrar_auto,
        delay_cierre=delay_cierre
    )
    def ejecutar(logger):
        ejecutar_base(logger)

    return ejecutar


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    ejecutar = configurar_ejecucion(
        alerta=True,
        cerrar_auto=True,
        delay_cierre=5
    )

    ejecutar()