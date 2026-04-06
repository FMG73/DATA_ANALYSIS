import pandas as pd
import os
from pathlib import Path
from typing import Union

def guardar_excel_ultra_rapido(df: pd.DataFrame, ruta_guardado: Union[str, Path]) -> None:
    ruta = Path(ruta_guardado)

    with open(ruta, 'wb') as f:
        with pd.ExcelWriter(
            f,
            engine='xlsxwriter',
            engine_kwargs={'options': {'constant_memory': True}}
        ) as writer:
            
            # Escritura directa (MUY optimizada internamente)
            df.to_excel(writer, index=False, sheet_name='Datos')

        # Seguridad en disco
        f.flush()
        os.fsync(f.fileno())

    print(f"Archivo guardado ULTRA rápido y seguro: {ruta.absolute()}")