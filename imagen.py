from PIL import Image

def redimensionar_png(ruta_imagen: str, porcentaje: float) -> None:
    factor = porcentaje / 100

    with Image.open(ruta_imagen) as img:
        nuevo_ancho = int(img.width * factor)
        nuevo_alto = int(img.height * factor)

        img_redimensionada = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        img_redimensionada.save(ruta_imagen)
