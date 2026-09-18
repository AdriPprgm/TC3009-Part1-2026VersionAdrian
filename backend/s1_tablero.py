"""Sesion 1: los datos del tablero.

Sirve agregados y registros del dataset. Todavia no hay modelo.
El contrato que implementa este archivo esta en docs/api-contrato.md.
"""

import os
import pathlib

import pandas as pd
from flask import Blueprint, jsonify, request

bp = Blueprint("s1_tablero", __name__)

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Las diez features que consume el modelo desde la sesion 2, mas Id y el target.
# El tablero y el predictor hablan del mismo vocabulario desde el dia uno.
FEATURE_COLUMNS = [
    "GrLivArea",
    "OverallQual",
    "YearBuilt",
    "TotalBsmtSF",
    "GarageCars",
    "FullBath",
    "BedroomAbvGr",
    "Neighborhood",
    "LotArea",
    "KitchenQual",
]
TARGET_COLUMN = "SalePrice"
EXPOSED_COLUMNS = ["Id"] + FEATURE_COLUMNS + [TARGET_COLUMN]

DEFAULT_LIMIT = 20
MAX_LIMIT = 200

DATA_PATH = os.environ.get("DATA_PATH", str(RAIZ / "data" / "train.csv"))

# ATAJO-P1: el CSV se carga completo en memoria al arrancar y nunca se recarga.
#           Alcanza para 1460 filas y hace la sesion 1 legible.
#           Parte 2 -> base de datos, consultas, paginacion real.
df = pd.read_csv(DATA_PATH)


# ---------------------------------------------------------------------------
# Endpoints del tablero
# ---------------------------------------------------------------------------

FEATURE_COLUMNS = [
    "GrLivArea",
    "OverallQual",
    "YearBuilt",
    "TotalBsmtSF",
    "GarageCars",
    "FullBath",
    "BedroomAbvGr",
    "Neighborhood",
    "LotArea",
    "KitchenQual",
]
TARGET_COLUMN = "SalePrice"
EXPOSED_COLUMNS = ["Id"] + FEATURE_COLUMNS + [TARGET_COLUMN]

DEFAULT_LIMIT = 20
MAX_LIMIT = 200


def _redondear(v):
    if pd.isna(v):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return v


@bp.get("/api/stats")
def stats():
    """Agregados del dataset para el tablero."""
    neighborhood = request.args.get("neighborhood", "").strip()
    alcance = df if not neighborhood else df[df["Neighborhood"] == neighborhood]

    if neighborhood and alcance.empty:
        return jsonify(
            {
                "count": 0,
                "scope": neighborhood,
                "target": None,
                "by_neighborhood": [
                    {
                        "neighborhood": row["Neighborhood"],
                        "count": int(row["count"]),
                        "mean_price": float(row["mean_price"]),
                    }
                    for row in (
                        df.groupby("Neighborhood")["SalePrice"]
                        .agg(["count", "mean"])
                        .reset_index()
                        .rename(columns={"mean": "mean_price"})
                        .sort_values("mean_price", ascending=False)
                        .to_dict(orient="records")
                    )
                ],
                "by_overall_qual": [],
            }
        )

    by_neighborhood = (
        df.groupby("Neighborhood")["SalePrice"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"mean": "mean_price"})
        .sort_values("mean_price", ascending=False)
    )

    by_overall_qual = (
        alcance.groupby("OverallQual")["SalePrice"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"mean": "mean_price"})
        .sort_values("OverallQual", ascending=True)
    )

    response = {
        "count": int(len(alcance)),
        "scope": neighborhood or None,
        "target": None,
        "by_neighborhood": [
            {
                "neighborhood": row["Neighborhood"],
                "count": int(row["count"]),
                "mean_price": float(row["mean_price"]),
            }
            for row in by_neighborhood.to_dict(orient="records")
        ],
        "by_overall_qual": [
            {
                "overall_qual": int(row["OverallQual"]),
                "count": int(row["count"]),
                "mean_price": float(row["mean_price"]),
            }
            for row in by_overall_qual.to_dict(orient="records")
        ],
    }

    if not alcance.empty:
        target = alcance[TARGET_COLUMN]
        response["target"] = {
            "name": TARGET_COLUMN,
            "min": float(target.min()),
            "mean": float(target.mean()),
            "median": float(target.median()),
            "max": float(target.max()),
        }

    return jsonify(response)


@bp.get("/api/data")
def data():
    """Registros individuales con filtro opcional por colonia y limite."""
    neighborhood = request.args.get("neighborhood", "").strip()
    try:
        limite = int(request.args.get("limit", DEFAULT_LIMIT))
    except ValueError:
        limite = DEFAULT_LIMIT
    limite = max(1, min(limite, MAX_LIMIT))

    filtrado = df if not neighborhood else df[df["Neighborhood"] == neighborhood]
    filas = filtrado.head(limite)

    return jsonify(
        {
            "count": int(len(filas)),
            "total_matching": int(len(filtrado)),
            "rows": filas[EXPOSED_COLUMNS].where(pd.notna(filas[EXPOSED_COLUMNS]), None).to_dict(orient="records"),
        }
    )


def estado():
    """Lo que este modulo aporta a /api/health."""
    return {"filas_en_datos": int(len(df)), "target": TARGET_COLUMN}
