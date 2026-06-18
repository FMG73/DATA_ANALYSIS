def _build_pages(self) -> List[Dict[str, Any]]:
    """
    Construye el diccionario de páginas completo.

    IMPORTANTE:
    - Aquí va tu estructura original sin cambios
    - Separado para mantener el __init__ limpio
    """

    return [
        {
            "title": "1: FRECUENTES",
            "columns": [
                {
                    "title": "OAS",
                    "style": {"column_bg": "#E8F5E9", "bg": "#4CAF50", "hover": "#45A049"},
                    "scripts": [
                        {
                            "name": "3 OAS 025 + RED",
                            "path": oas_025_red,
                            "tooltip": "Descarga y copia datos de OAS 025",
                            "right_click_description":
                                "Script para descargar datos de OAS 025 y copiarlos a la red.\n\n"
                                "Detalles:\n"
                                "1. Conecta al servidor\n"
                                "2. Descarga datos\n"
                                "3. Copia a red",
                            "style": {"bg": "#7AA86F"}
                        },
                        {
                            "name": "1 OAS 940",
                            "path": oas_940,
                            "tooltip": "Descarga datos de OAS 940"
                        },
                        {
                            "name": "4 OAS 505",
                            "path": oas_505_current,
                            "tooltip": "Descarga datos de OAS 505"
                        },
                        {
                            "name": "3 OAS 713",
                            "path": oas_713,
                            "tooltip": "Descarga datos de OAS 713"
                        }
                    ]
                },
                {
                    "title": "SCRIPTS",
                    "style": {"column_bg": "#E3F2FD"},
                    "scripts": [
                        {
                            "name": "ACCESO REDES",
                            "path": red,
                            "tooltip": "Configura acceso a redes"
                        },
                        {
                            "name": "REDES VPN",
                            "path": vpn,
                            "tooltip": "Configura VPN"
                        }
                    ]
                }
            ]
        }
    ]