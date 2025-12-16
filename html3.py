import os
import win32com.client as win32
import tableauserverclient as TSC


class ReporteTableauOutlook:
    """
    Clase unificada para el envío de correos Outlook con contenido opcional de Tableau.

    Permite:
    - Enviar un correo simple (solo texto / HTML)
    - Enviar correo con dashboards de Tableau embebidos en el HTML
    - Enviar correo con archivos adjuntos
    - Enviar correo con dashboards + adjuntos

    Los dashboards y los adjuntos son completamente opcionales.
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
        """
        Constructor de la clase.

        :param ruta_mensaje: Ruta al archivo .msg de Outlook
        :param asunto_mensaje: Asunto del correo
        :param para_destinatarios: Destinatarios en PARA
        :param dashboards: (opcional) dict con estructura:
            {
                "MARCADOR_HTML": ("Nombre Workbook", "Nombre Vista")
            }
        :param archivos_adjuntos: (opcional) lista de rutas a archivos
        :param copia_destinatarios: (opcional) destinatarios en CC
        """

        # ---------------------------
        # Validación mínima obligatoria
        # ---------------------------
        if not all([ruta_mensaje, asunto_mensaje, para_destinatarios]):
            raise ValueError(
                "Los parámetros ruta_mensaje, asunto_mensaje y para_destinatarios son obligatorios"
            )

        # ---------------------------
        # Configuración correo
        # ---------------------------
        self.ruta_mensaje = ruta_mensaje
        self.asunto_mensaje = asunto_mensaje
        self.para_destinatarios = para_destinatarios
        self.copia_destinatarios = copia_destinatarios

        # ---------------------------
        # Contenido opcional
        # ---------------------------
        self.dashboards = dashboards or {}
        self.archivos_adjuntos = archivos_adjuntos or []

        # ---------------------------
        # Estado interno
        # ---------------------------
        self.imagenes_exportadas = {}   # {MARCADOR: ruta_imagen}
        self.mail = None                # Objeto MailItem de Outlook

        # ---------------------------
        # Configuración segura Tableau
        # (definida en tu entorno)
        # ---------------------------
        self.server_url = server_url
        self.token_name = token_name
        self.token_secret = token_id
        self.site_id = sitio_path
        self.cert_path = certificado_path

    # ======================================================================
    # =========================== BLOQUE TABLEAU ===========================
    # ======================================================================

    def _crear_server_tableau(self):
        """
        Crea y devuelve el objeto Server de Tableau configurado
        con verificación SSL mediante certificado corporativo.
        """
        server = TSC.Server(self.server_url, use_server_version=True)
        server.add_http_options({'verify': self.cert_path})
        return server

    def exportar_imagenes_tableau(self):
        """
        Exporta las vistas de Tableau definidas en self.dashboards.

        - Si no hay dashboards definidos, no hace nada.
        - Las imágenes se guardan como PNG en disco.
        - Se asocian a su marcador HTML correspondiente.

        :return: dict {MARCADOR: ruta_absoluta_imagen}
        """

        if not self.dashboards:
            print("ℹ No hay dashboards definidos. Se omite exportación Tableau.")
            return {}

        auth = TSC.PersonalAccessTokenAuth(
            self.token_name,
            self.token_secret,
            self.site_id
        )

        server = self._crear_server_tableau()

        with server.auth.sign_in(auth):
            all_views, _ = server.views.get()
            all_workbooks, _ = server.workbooks.get()

            # Mapa auxiliar: workbook_id -> workbook_name
            workbook_id_to_name = {
                wb.id: wb.name for wb in all_workbooks if wb.id
            }

            for marcador, (workbook_name, vista_nombre) in self.dashboards.items():

                # Buscar la vista exacta
                vista = next(
                    (
                        v for v in all_views
                        if v.name == vista_nombre
                        and workbook_id_to_name.get(v.workbook_id) == workbook_name
                    ),
                    None
                )

                if not vista:
                    print(f"❌ Vista {vista_nombre} en {workbook_name} NO encontrada")
                    continue

                # Exportar imagen
                server.views.populate_image(vista)

                nombre_imagen = f"Z_{marcador.lower()}.png"
                ruta_imagen = os.path.abspath(nombre_imagen)

                with open(ruta_imagen, "wb") as f:
                    f.write(vista.image)

                self.imagenes_exportadas[marcador] = ruta_imagen

                print(f"✔ {workbook_name} -> {vista_nombre} exportado")

        return self.imagenes_exportadas

    # ======================================================================
    # ============================ BLOQUE OUTLOOK ==========================
    # ======================================================================

    def preparar_mail(self):
        """
        Abre la plantilla .msg de Outlook y prepara el objeto MailItem.
        """

        outlook = win32.Dispatch('outlook.application')

        ruta_msg = (
            self.ruta_mensaje
            if os.path.isabs(self.ruta_mensaje)
            else os.path.join(os.getcwd(), self.ruta_mensaje)
        )

        self.mail = outlook.Session.OpenSharedItem(ruta_msg)

        # Configuración básica del correo
        self.mail.To = self.para_destinatarios
        self.mail.Subject = self.asunto_mensaje

        if self.copia_destinatarios:
            self.mail.CC = self.copia_destinatarios

        return self.mail

    def insertar_dashboards_en_mail(self):
        """
        Reemplaza los marcadores #MARCADOR# del HTML del correo
        por imágenes embebidas (CID).

        Si no hay imágenes exportadas, no hace nada.
        """

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

            # Adjuntar imagen como CID
            adjunto = self.mail.Attachments.Add(ruta_imagen)
            adjunto.PropertyAccessor.SetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
                cid
            )

    def adjuntar_archivos(self):
        """
        Adjunta archivos adicionales al correo.

        Si no hay archivos definidos, no hace nada.
        """

        if not self.archivos_adjuntos:
            print("ℹ No hay archivos adjuntos para añadir.")
            return

        for archivo in self.archivos_adjuntos:
            self.mail.Attachments.Add(archivo)

    def enviar_mail(self, mostrar=False):
        """
        Envía el correo o lo muestra en pantalla.

        :param mostrar: True → Display | False → Send
        """

        if not self.mail:
            raise RuntimeError("El mail no está preparado.")

        if mostrar:
            self.mail.Display()
        else:
            self.mail.Send()
            print("✔ CORREO ENVIADO")