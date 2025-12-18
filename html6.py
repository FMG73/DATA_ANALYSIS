def preparar_mail(self):
    outlook = win32.Dispatch('outlook.application')

    ruta_msg = (
        self.ruta_mensaje
        if os.path.isabs(self.ruta_mensaje)
        else os.path.join(os.getcwd(), self.ruta_mensaje)
    )

    # 1️⃣ Abrir plantilla .msg
    plantilla = outlook.Session.OpenSharedItem(ruta_msg)

    # 2️⃣ Crear mail nuevo
    self.mail = outlook.CreateItem(0)

    # 3️⃣ Copiar HTML
    self.mail.HTMLBody = plantilla.HTMLBody

    # 4️⃣ Copiar ADJUNTOS (incluye imágenes inline)
    for adj in plantilla.Attachments:
        adj_copy = self.mail.Attachments.Add(adj.FileName)
        try:
            cid = adj.PropertyAccessor.GetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F"
            )
            adj_copy.PropertyAccessor.SetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
                cid
            )
        except:
            pass  # adjunto normal, sin CID

    # 5️⃣ Asignar asunto y destinatarios
    self.mail.Subject = self.asunto_mensaje
    self.mail.To = self.para_destinatarios
    if self.copia_destinatarios:
        self.mail.CC = self.copia_destinatarios

    # 6️⃣ Cerrar plantilla
    plantilla.Close(0)

    return self.mail