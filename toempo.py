df["CONTROL"] = (
    (pd.Timestamp.today() - 
     df[["FECHA_1", "FECHA_2"]].apply(pd.to_datetime).max(axis=1)
    ).dt.days > 21
).map({True: "mayor 21", False: "menor 21"})