import os
import shutil

class ImagenesMail:
    def __init__(self, imagenes):
        """
        imagenes: dict {'MARCADOR': 'ruta_imagen'}
        """
        self.imagenes = imagenes

    def reemplazar_marcadores_html(self, mail):
        """
        Reemplaza los marcadores en HTML y adjunta las imágenes
        """
        for marcador, ruta_imagen in self.imagenes.items():
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

    def copiar_imagenes(self, directorio_destino):
        """
        Copia las imágenes a otro directorio
        """
        if not os.path.exists(directorio_destino):
            os.makedirs(directorio_destino)

        imagenes_guardadas = {}
        for marcador, ruta in self.imagenes.items():
            nombre = os.path.basename(ruta)
            destino = os.path.join(directorio_destino, nombre)
            shutil.copy2(ruta, destino)
            imagenes_guardadas[nombre] = destino

        return imagenes_guardadas