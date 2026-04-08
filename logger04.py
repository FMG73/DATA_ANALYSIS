# test_melloger.py
from melloger.script_logger import ScriptLogger
import time

# Crear logger con nombre propio
log = ScriptLogger("scripts_ventas")

def main():
    log.step("Inicio del script")
    
    log.info("Leyendo datos del Excel...")
    time.sleep(0.5)  # simula lectura
    
    log.step("Transformando columnas")
    time.sleep(0.5)  # simula transformación
    
    log.warning("Faltan algunas columnas opcionales")
    time.sleep(0.5)
    
    try:
        log.info("Procesando datos...")
        time.sleep(0.5)
        # Simular error
        x = 1 / 0
    except Exception as e:
        log.error(f"Ocurrió un error durante el procesamiento: {e}")
    
    log.success("Script terminado correctamente (excepto errores simulados)")

if __name__ == "__main__":
    main()