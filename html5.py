import os
import win32com.client as win32
import tableauserverclient as TSC

class ReporteTableauOutlook:
    """
    Clase unificada para envío de correos Outlook con:
    - Dashboards de Tableau (opcional)
    - Archivos adjuntos (opcional)
    - Variables dinámicas en HTML (#VARIABLE#)
    - Imágenes en el cuerpo del mensaje (#IMAGEN#)
    """

    def __init__(
        self,
        ruta_mensaje,
        asunto_mensaje,
        para_destinatarios,
        dashboards=None,
        archivos_adjuntos=None,
        copia_destinatarios=None
    ):
        if not all([ruta_mensaje, asunto_mensaje, para_destinatarios]):
            raise ValueError(
                "Los parámetros ruta_mensaje, asunto_mensaje y para_destinatarios son obligatorios"
            )

        self.ruta_mensaje = ruta_mensaje
        self.asunto_mensaje = asunto_mensaje
        self.para_destinatarios = para_destinatarios
        self.copia_destinatarios = copia_destinatarios

        self.dashboards = dashboards or {}
        self.archivos_adjuntos = archivos_adjuntos or []

        self.imagenes_exportadas = {}  # dashboards
        self.mail = None

        # Tableau - variables definidas en entorno seguro
        self.server_url = server_url
        self.token_name = token_name
        self.token_secret = token_id
        self.site_id = sitio_path
        self.cert_path = certificado_path

    # ====================== Tableau ======================
    def _crear_server_tableau(self):
        server = TSC.Server(self.server_url, use_server_version=True)
        server.add_http_options({'verify': self.cert_path})
        return server

    def exportar_imagenes_tableau(self):
        if not self.dashboards:
            print("ℹ No hay dashboards definidos.")
            return {}

        auth = TSC.PersonalAccessTokenAuth(
            self.token_name, self.token_secret, self.site_id
        )
        server = self._crear_server_tableau()

        with server.auth.sign_in(auth):
            all_views, _ = server.views.get()
            all_workbooks, _ = server.workbooks.get()
            workbook_id_to_name = {wb.id: wb.name for wb in all_workbooks if wb.id}

            for marcador, (workbook_name, vista_nombre) in self.dashboards.items():
                vista = next(
                    (
                        v for v in all_views
                        if v.name == vista_nombre
                        and workbook_id_to_name.get(v.workbook_id) == workbook_name
                    ), None
                )
                if not vista:
                    print(f"❌ Vista {vista_nombre} en {workbook_name} NO encontrada")
                    continue

                server.views.populate_image(vista)
                nombre_imagen = f"Z_{marcador.lower()}.png"
                ruta_imagen = os.path.abspath(nombre_imagen)
                with open(ruta_imagen, "wb") as f:
                    f.write(vista.image)
                self.imagenes_exportadas[marcador] = ruta_imagen
                print(f"✔ {workbook_name} -> {vista_nombre} exportado")
        return self.imagenes_exportadas

    # ====================== Outlook ======================
    def preparar_mail(self):
        outlook = win32.Dispatch('outlook.application')
        ruta_msg = (
            self.ruta_mensaje
            if os.path.isabs(self.ruta_mensaje)
            else os.path.join(os.getcwd(), self.ruta_mensaje)
        )
        self.mail = outlook.Session.OpenSharedItem(ruta_msg)
        self.mail.To = self.para_destinatarios
        self.mail.Subject = self.asunto_mensaje
        if self.copia_destinatarios:
            self.mail.CC = self.copia_destinatarios
        return self.mail

    # Reemplazo de variables genéricas en HTML
    def reemplazar_variables_html(self, variables):
        if not self.mail:
            raise RuntimeError("El mail no está preparado.")
        if not variables:
            print("ℹ No hay variables para reemplazar.")
            return
        for clave, valor in variables.items():
            hashtag = f"#{clave}#"
            if hashtag in self.mail.HTMLBody:
                self.mail.HTMLBody = self.mail.HTMLBody.replace(hashtag, str(valor))
            else:
                print(f"⚠ Hashtag {hashtag} no encontrado en la plantilla.")

    # Inserción de dashboards exportados
    def insertar_dashboards_en_mail(self):
        if not self.imagenes_exportadas:
            print("ℹ No hay imágenes de Tableau para insertar en el mail.")
            return
        for marcador, ruta_imagen in self.imagenes_exportadas.items():
            cid = f"cid_{marcador.lower()}"
            if f"#{marcador}#" in self.mail.HTMLBody:
                self.mail.HTMLBody = self.mail.HTMLBody.replace(
                    f"#{marcador}#", f'<img src="cid:{cid}">'
                )
            else:
                print(f"⚠ Marcador #{marcador}# no encontrado en la plantilla.")
            adjunto = self.mail.Attachments.Add(ruta_imagen)
            adjunto.PropertyAccessor.SetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
                cid
            )

    # Inserción de cualquier imagen en HTML mediante hashtags
    def insertar_imagenes_html(self, diccionario_imagenes):
        """
        diccionario_imagenes = { "MARCADOR": "ruta/imagen.png" }
        """
        if not self.mail:
            raise RuntimeError("El mail no está preparado.")
        if not diccionario_imagenes:
            print("ℹ No hay imágenes a insertar.")
            return
        for marcador, ruta_imagen in diccionario_imagenes.items():
            cid = f"cid_{marcador.lower()}"
            if f"#{marcador}#" in self.mail.HTMLBody:
                self.mail.HTMLBody = self.mail.HTMLBody.replace(
                    f"#{marcador}#", f'<img src="cid:{cid}">'
                )
            else:
                print(f"⚠ Marcador #{marcador}# no encontrado en la plantilla.")
            adjunto = self.mail.Attachments.Add(ruta_imagen)
            adjunto.PropertyAccessor.SetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
                cid
            )

    def adjuntar_archivos(self):
        if not self.archivos_adjuntos:
            print("ℹ No hay archivos adjuntos para añadir.")
            return
        for archivo in self.archivos_adjuntos:
            self.mail.Attachments.Add(archivo)

    def enviar_mail(self, mostrar=False):
        if not self.mail:
            raise RuntimeError("El mail no está preparado.")
        if mostrar:
            self.mail.Display()
        else:
            self.mail.Send()
            print("✔ CORREO ENVIADO")