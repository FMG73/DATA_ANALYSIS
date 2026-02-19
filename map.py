df["estado_90_dias"] = (
    ((pd.Timestamp.today() - df["fecha"]).dt.days > 90)
    .map({True: "Mayor de 90", False: "Menor o igual a 90"})
)