import tableauserverclient as TSC
import os

class Tableau:
    def __init__(self, dashboards):

        self.dashboards = dashboards
        self.imagenes_exportadas = {}

        self.server_url = "DIRECCION SERVER"
        self.token_name = "NOMBRE_TOKEN"
        self.token_secret = "CODIGO_TOKEN"
        self.site_id = "EMPRESA"

        self.cert_path = r"C:\REMARKETING\TABLEAU\CERTIFICADO.cer"


    def _crear_server(self):
        """Crea el objeto server configurado y con SSL correcto."""
        server = TSC.Server(self.server_url, use_server_version=True)
        server.add_http_options({'verify': self.cert_path})
        return server


    def exportar_imagenes(self):
        auth = TSC.PersonalAccessTokenAuth(
            self.token_name,
            self.token_secret,
            self.site_id
        )

        server = self._crear_server()

        with server.auth.sign_in(auth):
            all_views, _ = server.views.get()
            all_workbooks, _ = server.workbooks.get()

            workbook_id_to_name = {
                wb.id: wb.name for wb in all_workbooks if wb.id
            }

            for marcador, (workbook_name, vista_nombre) in self.dashboards.items():

                vista = next(
                    (v for v in all_views
                     if v.name == vista_nombre
                     and workbook_id_to_name.get(v.workbook_id) == workbook_name),
                    None
                )

                if not vista:
                    print(f"❌ Vista {vista_nombre} en {workbook_name} NO encontrada")
                    continue

                server.views.populate_image(vista)

                nombre_imagen = f"Z_{marcador.lower()}.png"

                with open(nombre_imagen, "wb") as f:
                    f.write(vista.image)

                self.imagenes_exportadas[marcador] = os.path.abspath(nombre_imagen)

                print(f"✔ {workbook_name} -> {vista_nombre} exportado como {nombre_imagen}")

        return self.imagenes_exportadas



    def reemplazar_marcadores_html(self, mail):
        for marcador, ruta_imagen in self.imagenes_exportadas.items():
            cid = f"cid_{marcador.lower()}"

            if f"#{marcador}#" in mail.HTMLBody:
                mail.HTMLBody = mail.HTMLBody.replace(
                    f"#{marcador}#", f'<img src="cid:{cid}">'
                )
            else:
                print(f"⚠ Marcador #{marcador}# no encontrado en la plantilla.")

            adjunto = mail.Attachments.Add(ruta_imagen)
            adjunto.PropertyAccessor.SetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
                cid
            )



    def imagenes_to_archivo(self, directorio_destino):

        import shutil

        auth = TSC.PersonalAccessTokenAuth(
            self.token_name,
            self.token_secret,
            self.site_id
        )

        server = self._crear_server()

        imagenes_guardadas = {}

        with server.auth.sign_in(auth):
            all_views, _ = server.views.get()
            all_workbooks, _ = server.workbooks.get()

            workbook_id_to_name = {
                wb.id: wb.name for wb in all_workbooks if wb.id
            }

            for workbook_name, vista_nombre in self.dashboards.values():

                vista = next(
                    (v for v in all_views
                     if v.name == vista_nombre
                     and workbook_id_to_name.get(v.workbook_id) == workbook_name),
                    None
                )

                if not vista:
                    print(f"❌ Vista {vista_nombre} en {workbook_name} NO encontrada")
                    continue

                server.views.populate_image(vista)

                nombre_imagen = f"Z_{vista_nombre}.png"
                ruta_destino = os.path.join(directorio_destino, nombre_imagen)

                with open(ruta_destino, 'wb') as f:
                    f.write(vista.image)

                print(f"✔ {workbook_name} → {vista_nombre} guardado en {ruta_destino}")

                imagenes_guardadas[nombre_imagen] = ruta_destino

        return imagenes_guardadas