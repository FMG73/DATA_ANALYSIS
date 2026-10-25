def comprobar_valores_nuevos(ruta: str, columna: str, grupos_ref: Dict[str, List[str]]) -> None:
    try:
        df = pd.read_excel(ruta, usecols=[columna])
        # OBTENER TODOS LOS STAGES INDIVIDUALES DEL EXCEL
        valores_excel = {
            stage.strip()
            for valor in df[columna].dropna()
            for stage in valor.split(",")
            if stage.strip()
        }
        # OBTENER LOS STAGES PERMITIDOS EN EL DICCIONARIO
        permitidos = obtener_valores_permitidos(grupos_ref)
        # IDENTIFICAR LOS STAGES QUE NO ESTÁN DEFINIDOS
        nuevos = valores_excel - permitidos
        if nuevos:
            print(f"ATENCIÓN: SE HAN ENCONTRADO {len(nuevos)} STAGE(S) NUEVO(S):")
            for valor in sorted(nuevos):
                print(f"- {valor}")
        else:
            print("NO SE HAN ENCONTRADO STAGES NUEVOS.")
    except FileNotFoundError:
        print(f"ERROR: NO SE ENCONTRÓ EL ARCHIVO EN LA RUTA: {ruta}")
    except KeyError:
        print(f"ERROR: LA COLUMNA '{columna}' NO EXISTE EN EL ARCHIVO.")
    except Exception as e:
        print(f"OCURRIÓ UN ERROR INESPERADO: {e}")