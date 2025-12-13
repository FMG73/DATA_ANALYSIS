import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import win32com.client as win32

# ---------------- 1️⃣ Leer CSV ----------------
df = pd.read_csv("ventas.csv", parse_dates=["fecha"])

# ---------------- 2️⃣ Calcular KPIs ----------------
vendidos_mes = df["vendido"].sum()
facturacion_total = df["importe"].sum()
pct_adjudicados = round((df["adjudicado"]=="Sí").sum() / len(df) * 100, 1)

# ---------------- 3️⃣ Función para convertir Plotly a PNG base64 ----------------
def plotly_to_base64(fig, scale=3):
    buf = BytesIO()
    fig.write_image(buf, format="png", scale=scale)  # escala alta
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

# ---------------- 4️⃣ Gráficos Ultra-Premium ----------------

# 4a. Ventas diarias con línea degradada y sombreado
ventas_dia = df.groupby("fecha")["vendido"].sum().reset_index()
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=ventas_dia["fecha"],
    y=ventas_dia["vendido"],
    mode='lines+markers',
    line=dict(color='royalblue', width=4),
    marker=dict(size=8, color='deepskyblue', line=dict(width=1, color='darkblue')),
    fill='tozeroy',
    fillcolor='rgba(30,144,255,0.2)',
    name='Ventas'
))
fig1.update_layout(
    title="Ventas diarias",
    template="plotly_white",
    font=dict(family="Segoe UI", size=12, color="#1f2937"),
    xaxis_title="Fecha",
    yaxis_title="Unidades",
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=50,b=40,l=40,r=40)
)
grafico1 = plotly_to_base64(fig1)

# 4b. Top 3 modelos vendidos con barras degradadas
top_modelos = df.groupby("modelo")["vendido"].sum().sort_values(ascending=False).head(3).reset_index()
fig2 = px.bar(top_modelos, x="modelo", y="vendido",
              title="Top 3 modelos vendidos",
              color="vendido",
              color_continuous_scale=px.colors.sequential.Blues,
              text="vendido")
fig2.update_traces(marker_line_color='darkblue', marker_line_width=1.5, textposition='outside')
fig2.update_layout(template="plotly_white", plot_bgcolor='rgba(0,0,0,0)',
                   font=dict(family="Segoe UI", size=12, color="#1f2937"),
                   xaxis_title="", yaxis_title="Unidades", showlegend=False, margin=dict(t=50,b=40,l=40,r=40))
grafico2 = plotly_to_base64(fig2)

# 4c. % adjudicados por marca con colores vibrantes y efecto 3D
adjud_por_marca = df.groupby("marca")["adjudicado"].apply(lambda x: (x=="Sí").sum()).reset_index(name="adjudicados")
fig3 = px.pie(adjud_por_marca, names="marca", values="adjudicados",
              title="% Adjudicados por marca",
              color_discrete_sequence=px.colors.qualitative.Pastel)
fig3.update_traces(textinfo='percent+label', pull=[0.05]*len(adjud_por_marca), marker=dict(line=dict(color='#ffffff', width=2)))
fig3.update_layout(template="plotly_white", font=dict(family="Segoe UI", size=12, color="#1f2937"), margin=dict(t=50,b=40,l=40,r=40))
grafico3 = plotly_to_base64(fig3)

# ---------------- 5️⃣ Estilos Dashboard Premium ----------------
estilo_dashboard = {
    "ancho": "1000px",
    "fondo": "#f0f4f8",
    "padding": "24px",
    "border_radius": "16px",
    "fuente": "Segoe UI, Arial, sans-serif",
    "card": {
        "kpi": {
            "fondo": "linear-gradient(135deg, #ffffff, #e0e7ff)",
            "padding": "22px",
            "border_radius": "14px",
            "sombra": "0 8px 20px rgba(0,0,0,0.12)",
            "titulo_color": "#4b5563",
            "titulo_size": "14px",
            "valor_color": "#111827",
            "valor_size": "36px"
        },
        "grafico": {
            "fondo": "linear-gradient(135deg, #ffffff, #f3f4f6)",
            "padding": "16px",
            "border_radius": "14px",
            "sombra": "0 8px 20px rgba(0,0,0,0.12)",
            "titulo_color": "#1f2937",
            "titulo_size": "16px"
        }
    }
}

# ---------------- 6️⃣ Estructura filas y cards ----------------
filas = [
    {"tipo": "kpi",
     "cards":[
         {"titulo": "Vendidos mes", "valor": vendidos_mes},
         {"titulo": "Facturación", "valor": f"{facturacion_total} €"},
         {"titulo": "% Adjudicados", "valor": f"{pct_adjudicados}%"}
     ]},
    {"tipo": "grafico",
     "cards":[
         {"titulo": "Ventas diarias", "imagen": grafico1},
         {"titulo": "Top 3 modelos", "imagen": grafico2},
         {"titulo": "% Adjudicados por marca", "imagen": grafico3}
     ]}
]

# ---------------- 7️⃣ Función generar dashboard HTML ----------------
def generar_dashboard(filas, estilos):
    html = f"""<div style="
        width:{estilos['ancho']};
        margin:0 auto;
        background-color:{estilos['fondo']};
        padding:{estilos['padding']};
        border-radius:{estilos['border_radius']};
        font-family:{estilos['fuente']};
    ">"""
    
    # Título general
    html += f"""
    <div style="width:100%; margin-bottom:24px;">
        <div style="
            background-color:#ffffff;
            padding:24px;
            border-radius:{estilos['border_radius']};
            box-shadow:0 8px 20px rgba(0,0,0,0.12);
            text-align:center;">
            <div style="font-size:28px;font-weight:700;color:#1f2937;margin-bottom:6px;">
                Dashboard Ventas Coches
            </div>
            <div style="font-size:16px;color:#4b5563;">
                Resumen de ventas mensual
            </div>
        </div>
    </div>
    """
    
    # Filas dinámicas
    for fila in filas:
        html += '<div style="width:100%; margin-bottom:24px;">'
        html += '<table width="100%" cellspacing="0" cellpadding="0" style="table-layout:fixed;"><tr>'
        for card in fila["cards"]:
            if fila["tipo"]=="kpi":
                c = estilos['card']['kpi']
                html += f"""
                <td style="padding:10px;vertical-align:top;">
                    <div style="
                        background:{c['fondo']};
                        padding:{c['padding']};
                        border-radius:{c['border_radius']};
                        box-shadow:{c['sombra']};
                        text-align:center;">
                        <div style="
                            font-size:{c['titulo_size']};
                            color:{c['titulo_color']};
                            margin-bottom:8px;
                            text-transform:uppercase;">
                            {card['titulo']}
                        </div>
                        <div style="
                            font-size:{c['valor_size']};
                            font-weight:700;
                            color:{c['valor_color']};">
                            {card['valor']}
                        </div>
                    </div>
                </td>
                """
            elif fila["tipo"]=="grafico":
                c = estilos['card']['grafico']
                html += f"""
                <td style="padding:10px;vertical-align:top;">
                    <div style="
                        background:{c['fondo']};
                        padding:{c['padding']};
                        border-radius:{c['border_radius']};
                        box-shadow:{c['sombra']};
                        text-align:center;">
                        <div style="
                            font-size:{c['titulo_size']};
                            font-weight:600;
                            color:{c['titulo_color']};
                            margin-bottom:12px;">
                            {card['titulo']}
                        </div>
                        <div><img src="{card['imagen']}" style="max-width:100%;border-radius:10px;"></div>
                    </div>
                </td>
                """
        html += '</tr></table></div>'
    html += '</div>'
    return html

# ---------------- 8️⃣ Generar dashboard ----------------
dashboard_html = generar_dashboard(filas, estilo_dashboard)

# ---------------- 9️⃣ Insertar en .msg Outlook ----------------
outlook = win32.Dispatch("Outlook.Application")
msg = outlook.CreateItemFromTemplate(r"C:\ruta\plantilla.msg")  # Cambia por tu ruta
msg.HTMLBody = msg.HTMLBody.replace("#DASHBOARD#", dashboard_html)
msg.Display()  # Muestra el mensaje

print("✅ Dashboard ultra-premium generado e insertado correctamente")