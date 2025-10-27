def cerrar_powerpo(pres, cerrar=True, matar=True):
    time.sleep(5)
    pres.Save()
    if cerrar: pres.Close()
    if matar:
        win32.Dispatch("PowerPoint.Application").Quit()
        os.system("taskkill /f /im POWERPNT.exe")

def borrar_imagen(presentacion, num_diapo):
    slide = presentacion.Slides(num_diapo)
    for shape in list(slide.Shapes):
        if shape.Type == 13:
            shape.Delete()

def pegar_imagen(presentacion, num_diapo, ruta_imagen, izquierda, arriba):
    time.sleep(3)
    slide = presentacion.Slides(num_diapo)
    slide.Shapes.AddPicture(FileName=ruta_imagen, LinkToFile=False, SaveWithDocument=True,
                            Left=izquierda, Top=arriba)

def copiar_celda(wb, pres, hoja, slide, vinculos):
    hoja_inicio = wb.Sheets(hoja)
    destino = pres.Slides(slide)
    for objeto_ppt, celda_excel in vinculos.items():
        valor = str(hoja_inicio.Range(celda_excel).Value)
        for shape in destino.Shapes:
            if shape.Name == objeto_ppt:
                shape.TextFrame.TextRange.Text = valor
                break

def consola_barra(tiempo, color='green', mensaje='EN PROCESO...'):
    with Progress() as progress:
        task = progress.add_task(f"[{color}]{mensaje}", total=tiempo)
        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(1)

# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE PRINCIPAL DE EJECUCIÓN
# ─────────────────────────────────────────────────────────────────────────────
imp_mensaje_inicial('REPORTE RESULTADO LISTAS EXCLUSIVAS')
console = Console()

# Ejecutar formulario para obtener los datos de todas las marcas
seleccionadas = ejecutar_formulario()

# Bucle por cada marca seleccionada
for marca, datos in seleccionadas.items():
    lista_exclusiva = datos['exclusiva']
    lista_abierta = datos['abierta']
    fecha_subasta = datos['fecha']
    nombre_archivo = f'{fecha_subasta}_{marca}'

    mensaje_imprimir(f'INICIANDO PROCESO PARA {marca}')

    # 1. Escribir datos en Excel
    mensaje_imprimir('INICIANDO ESCRIBIR DATOS EN EXCEL')
    wb = iniciar_excel(ruta_ataque_xlsx)
    wb.Sheets('N_listas').Range('A2').Value = lista_exclusiva
    wb.Sheets('N_listas').Range('B2').Value = lista_abierta
    cerrar_excel(wb)

    # 2. Actualizar consultas PowerQuery
    mensaje_imprimir('INICIANDO ACTUALIZAR POWERQUERY')
    wb = iniciar_excel(ruta_ataque_xlsx)
    wb.RefreshAll()
    consola_barra(60, 'green', 'ACTUALIZANDO EXCEL...')
    mensaje_imprimir('PREPARADO PARA GUARDAR Y HACER COPIA DE ARCHIVO EXCEL?\nRECUERDA ACTUALIZAR TABLA DINAMICA','bright_yellow')
    input()
    cerrar_excel(wb)
    ruta_xlsx_guardado = os.path.join(ruta_descarga_archivos, f'{nombre_archivo}.xlsx')
    shutil.copy2(ruta_ataque_xlsx, ruta_xlsx_guardado)

    # 3. Generar dashboards
    mensaje_imprimir('INICIANDO COPIADO DE DASHBOARDS A IMAGEN')
    dashboards = dashboards_por_marca[marca]
    exportador = Tableau(dashboards)
    imagenes = exportador.imagenes_to_archivo(ruta_imagenes_temp)

    # 4. Pegar dashboards en PowerPoint
    mensaje_imprimir('INICIANDO COPIADO DE IMAGENES A POWERPOINT')
    pres = iniciar_powerpow(ruta_ataque_ppt)
    for i, clave in enumerate(dashboards.keys(), start=3):
        nombre_imagen = f'Z_{clave}.png'
        borrar_imagen(pres, i)
        pegar_imagen(pres, i, imagenes[nombre_imagen], 0, 0 if i < 5 else 10)

    # 5. Pegar datos en PowerPoint
    mensaje_imprimir('INICIANDO COPIA DE DATOS EXCEL A POWERPOINT')
    wb = iniciar_excel(ruta_ataque_xlsx)
    copiar_celda(wb, pres, 'DATOS_LISTA', 1, {'PA2': 'A2', 'PC2': 'C2'})
    copiar_celda(wb, pres, 'DATOS_LISTA', 2, {
        'PB2': 'B2','PD2': 'D2','PE2': 'E2','PF2': 'F2','PG2': 'G2',
        'PH2': 'H2','PI2': 'I2','PJ2': 'J2','PK2': 'K2','PL2': 'L2'
    })
    cerrar_excel(wb)

    # 6. Guardar como PDF
    mensaje_imprimir('INICIANDO GUARDAR COMO PDF')
    ruta_pdf = os.path.join(ruta_descarga_archivos, f'{nombre_archivo}.pdf')
    pres.SaveAs(ruta_pdf, 32)
    cerrar_powerpo(pres)

    # 7. Asignar sensibilidad al Excel
    mensaje_imprimir('ASIGNANDO SENSIBILIDAD A ARCHIVO EXCEL')
    archivo_sensi = ExcelSensibilidad(ruta_xlsx_guardado)
    archivo_sensi.to_sensibilidad('CONFIDENTIAL_EXTERNAL_INTRA')

    # 8. Enviar correo
    mensaje_imprimir('SE INICIA ENVÍO POR MAIL')
    config = config_email_por_marca.get(marca)
    if config:
        correo = EnvioCorreo(
            ruta_msg_outlook,
            [ruta_pdf, ruta_xlsx_guardado],
            f'{fecha_subasta} RESULTADO SUBASTA EXCLUSIVA {marca}',
            config['to'],
            config['cc']
        )
        correo.to_correo()
    else:
        mensaje_imprimir(f'[red]NO SE ENCONTRÓ CONFIGURACIÓN DE CORREO PARA LA MARCA {marca}[/red]')

# 9. Confirmar envío
imp_mensaje_final('REPORTE RESULTADO LISTAS EXCLUSIVAS')