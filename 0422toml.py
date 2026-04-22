from pathlib import Path
from toml import load
from types import SimpleNamespace
from typing import Union, List


def get_paths(toml_file: str, keys: Union[str, List[str]]) -> SimpleNamespace:
    """
    Devuelve rutas como objetos accesibles por punto:
    paths.inventory.motortrade.descarga
    """

    if isinstance(keys, str):
        keys = [keys]

    config = load(toml_file)

    # Bases
    bases = {k: Path(v).resolve() for k, v in config["ruta"].items()}

    def build_node(node: dict) -> SimpleNamespace:
        """Convierte dict de rutas en objeto accesible por punto"""
        data = {}

        for name, info in node.items():

            if isinstance(info, dict) and "base" in info and "path" in info:
                base = bases[info["base"]]
                data[name] = (base / info["path"]).resolve()

            elif isinstance(info, dict):
                data[name] = build_node(info)

        return SimpleNamespace(**data)

    result = {}

    for key in keys:
        current = config

        for part in key.split("."):
            current = current[part]

        result[key.split(".")[-1]] = build_node(current)

    return SimpleNamespace(**result)