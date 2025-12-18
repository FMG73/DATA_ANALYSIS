def redimensionar_multiples_png(
    rutas: list[str],
    porcentaje: float,
    sobrescribir: bool = True
) -> list[str]:
    """
    Redimensiona múltiples imágenes PNG aplicando el mismo porcentaje.

    Parámetros:
        rutas (list[str]): Lista de rutas de archivos PNG.
        porcentaje (float): Porcentaje de reducción.
        sobrescribir (bool): Si True, reemplaza cada archivo original.
                             Si False, genera copias con _resize.

    Retorna:
        list[str]: Lista de rutas de salida generadas.
    """
    rutas_salida = []

    for ruta in rutas:
        ruta_salida = redimensionar_png(
            ruta_imagen=ruta,
            porcentaje=porcentaje,
            sobrescribir=sobrescribir
        )
        rutas_salida.append(ruta_salida)

    return rutas_salida
