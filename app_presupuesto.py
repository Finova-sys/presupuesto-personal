# app_presupuesto_final.py

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# Configuración inicial
# -------------------------------
st.set_page_config(
    page_title="💰 Presupuesto Personal",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar menú y footer de Streamlit
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("💰 Presupuesto Personal")

# -------------------------------
# Nombre de usuario
# -------------------------------
usuario = st.text_input("Ingresa tu nombre para guardar tus datos", "")

if usuario:
    archivo_usuario = f"{usuario}.json"
    if os.path.exists(archivo_usuario):
        with open(archivo_usuario, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"ingresos": [], "gastos": [], "ahorro": [], "inversion": []}

    # -------------------------------
    # Categorías y descripciones
    # -------------------------------
    categorias_ingreso = ["Salario", "Freelance", "Negocio", "Otros"]
    categorias_gasto = ["Alimentos", "Transporte", "Servicios",
                        "Entretenimiento", "Salud", "Educación", "Otros"]
    categorias_ahorro = ["Cuenta de ahorros", "Fondo de emergencia", "CDT", "Otros"]
    categorias_inversion = ["Acciones", "Bonos", "Criptomonedas", "Bienes raíces", "Otros"]

    descripciones_comunes = {
        "Alimentos": ["Supermercado", "Restaurante", "Café"],
        "Transporte": ["Taxi", "Gasolina", "Bus", "Metro"],
        "Servicios": ["Luz", "Agua", "Internet", "Teléfono"],
        "Entretenimiento": ["Cine", "Concierto", "Videojuegos"],
        "Salud": ["Medicamentos", "Consultas", "Gym"],
        "Educación": ["Cursos", "Libros", "Talleres"],
        "Salario": ["Mensual", "Extra"],
        "Freelance": ["Proyecto1", "Proyecto2"],
        "Negocio": ["Ventas", "Servicios"],
        "Cuenta de ahorros": ["Mensual", "Automático"],
        "Fondo de emergencia": ["Aporte mensual"],
        "CDT": ["Inversión fija"],
        "Acciones": ["Bolsa", "Dividendos"],
        "Bonos": ["Gobierno", "Empresariales"],
        "Criptomonedas": ["Bitcoin", "Ethereum", "Altcoins"],
        "Bienes raíces": ["Arriendo", "Compra"]
    }

    tipos_movimiento = ["Ingreso", "Gasto", "Ahorro", "Inversión"]
    tipo = st.selectbox("Tipo de Movimiento", tipos_movimiento, key="tipo_mov")

    # Selección de categoría según el tipo
    if tipo == "Ingreso":
        categoria = st.selectbox("Categoría", categorias_ingreso, key="cat_mov")
    elif tipo == "Gasto":
        categoria = st.selectbox("Categoría", categorias_gasto, key="cat_mov")
    elif tipo == "Ahorro":
        categoria = st.selectbox("Categoría", categorias_ahorro, key="cat_mov")
    else:
        categoria = st.selectbox("Categoría", categorias_inversion, key="cat_mov")

    descripcion = st.selectbox("Descripción", descripciones_comunes.get(categoria, ["Otro"]), key="desc_mov")
    monto = st.number_input("Monto", min_value=0.0, step=10.0, key="monto_mov", format="%.2f")

    # Mapeo de tipo a clave correcta
    tipo_key_map = {"Ingreso": "ingresos", "Gasto": "gastos", "Ahorro": "ahorro", "Inversión": "inversion"}
    tipo_key = tipo_key_map[tipo]

    if st.button("Agregar Movimiento"):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data[tipo_key].append({
            "fecha": fecha,
            "categoria": categoria,
            "descripcion": descripcion,
            "monto": monto
        })
        with open(archivo_usuario, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        st.success(f"{tipo} agregado: ${monto:,.2f} en {categoria} ({descripcion})")

    # -------------------------------
    # Resumen y gráfica
    # -------------------------------
    total_ingresos = sum([i["monto"] for i in data["ingresos"]])
    total_gastos = sum([g["monto"] for g in data["gastos"]])
    total_ahorro = sum([a["monto"] for a in data["ahorro"]])
    total_inversion = sum([inv["monto"] for inv in data["inversion"]])
    saldo = total_ingresos - total_gastos - total_ahorro - total_inversion

    # -------------------------------
    # Saldo debajo del título principal
    # -------------------------------
    saldo_top_html = f"""
    <div style="text-align:center; margin:10px 0;">
        <h2 style="color:#1E90FF; font-size:38px; font-weight:bold;">
            💳 Saldo Disponible: ${saldo:,.2f}
        </h2>
    </div>
    """
    st.markdown(saldo_top_html, unsafe_allow_html=True)

    # -------------------------------
    # Filtro por fecha
    # -------------------------------
    st.subheader("📅 Consultar movimientos por fecha")
    fecha_inicio = st.date_input("Desde")
    fecha_fin = st.date_input("Hasta")

    movimientos_filtrados = []
    for t in ["ingresos", "gastos", "ahorro", "inversion"]:
        for mov in data[t]:
            mov_fecha = datetime.strptime(mov["fecha"], "%Y-%m-%d %H:%M:%S").date()
            if fecha_inicio <= mov_fecha <= fecha_fin:
                mov_copy = mov.copy()
                mov_copy["Tipo"] = t.capitalize() if t != "inversion" else "Inversión"
                movimientos_filtrados.append(mov_copy)

    # -------------------------------
    # Tabla con paginación + editar/eliminar
    # -------------------------------
    if movimientos_filtrados:
        df_filtrado = pd.DataFrame(movimientos_filtrados)
        df_filtrado = df_filtrado.sort_values(by="fecha", ascending=False)

        st.subheader("📋 Movimientos filtrados con paginación")

        # Paginación
        page_size = 10
        total_rows = len(df_filtrado)
        total_pages = (total_rows // page_size) + (1 if total_rows % page_size else 0)

        if "page_number" not in st.session_state:
            st.session_state.page_number = 1

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior") and st.session_state.page_number > 1:
                st.session_state.page_number -= 1
        with col3:
            if st.button("➡️ Siguiente") and st.session_state.page_number < total_pages:
                st.session_state.page_number += 1
        with col2:
            st.markdown(f"**Página {st.session_state.page_number} de {total_pages}**")

        start_idx = (st.session_state.page_number - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df_filtrado.iloc[start_idx:end_idx].copy()

        # Formato moneda
        df_page["monto"] = df_page["monto"].apply(lambda x: f"${x:,.2f}")

        st.dataframe(df_page, use_container_width=True, height=350)

        # Selección para editar/eliminar
        idx = st.number_input("Selecciona el número de fila para editar/eliminar", 
                              min_value=0, max_value=len(df_filtrado)-1, step=1)

        if st.button("📝 Editar Movimiento"):
            mov = df_filtrado.iloc[idx]
            nuevo_monto = st.number_input("Nuevo monto", min_value=0.0, step=10.0, value=float(mov["monto"]))
            if st.button("Guardar Cambios"):
                # Buscar y actualizar en JSON
                for t in data:
                    for m in data[t]:
                        if m["fecha"] == mov["fecha"]:
                            m["monto"] = nuevo_monto
                with open(archivo_usuario, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                st.success("Movimiento actualizado.")

        if st.button("🗑️ Eliminar Movimiento"):
            mov = df_filtrado.iloc[idx]
            for t in data:
                data[t] = [m for m in data[t] if m["fecha"] != mov["fecha"]]
            with open(archivo_usuario, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.success("Movimiento eliminado.")

        # -------------------------------
        # Exportar a Excel
        # -------------------------------
        output_excel = BytesIO()
        df_filtrado.to_excel(output_excel, index=False, sheet_name="Movimientos")
        st.download_button(
            label="📊 Exportar a Excel",
            data=output_excel.getvalue(),
            file_name="movimientos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # -------------------------------
        # Exportar a PDF
        # -------------------------------
        def export_pdf(df):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("📋 Reporte de Movimientos", styles["Title"]))
            elements.append(Spacer(1, 12))

            data_table = [df.columns.tolist()] + df.values.tolist()
            table = Table(data_table)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]))
            elements.append(table)
            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()
            return pdf

        pdf_bytes = export_pdf(df_filtrado)
        st.download_button(
            label="📄 Exportar a PDF",
            data=pdf_bytes,
            file_name="movimientos.pdf",
            mime="application/pdf"
        )

    else:
        st.info("No hay movimientos en el rango de fechas seleccionado.")

    # -------------------------------
    # Totales y gráfica
    # -------------------------------
    st.subheader("💵 Resumen")
    st.markdown(f"- **Total Ingresos:** ${total_ingresos:,.2f}")
    st.markdown(f"- **Total Gastos:** ${total_gastos:,.2f}")
    st.markdown(f"- **Total Ahorro:** ${total_ahorro:,.2f}")
    st.markdown(f"- **Total Inversión:** ${total_inversion:,.2f}")

    resumen = {
        "Ingresos": total_ingresos,
        "Gastos": total_gastos,
        "Ahorro": total_ahorro,
        "Inversión": total_inversion
    }
    df_resumen = pd.DataFrame(list(resumen.items()), columns=["Categoría", "Monto"])
    colores = {"Ingresos": "#00B140", "Gastos": "#FF4C4C", "Ahorro": "#1E90FF", "Inversión": "#FFD700"}
    fig = px.bar(df_resumen, x="Categoría", y="Monto", text="Monto", height=500)
    fig.update_traces(marker=dict(color=[colores[c] for c in df_resumen["Categoría"]]),
                      texttemplate="$%{text:,.2f}", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_tickprefix="$", yaxis_tickformat=",")
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Saldo disponible debajo de la gráfica
    # -------------------------------
    saldo_bottom_html = f"""
    <div style="text-align:center; margin:20px 0;">
        <h2 style="color:#1E90FF; font-size:36px; font-weight:bold;">
            💳 Saldo Disponible: ${saldo:,.2f}
        </h2>
    </div>
    """
    st.markdown(saldo_bottom_html, unsafe_allow_html=True)

    # -------------------------------
    # Botón de donación
    # -------------------------------
    donar_html = """
    <div style="display:flex;flex-direction:column;align-items:center;margin-top:10px;">
        <a href="https://clientes.nequi.com.co/recargas" target="_blank" 
           style="text-decoration:none;color:white;
                  background: linear-gradient(135deg, #00B140, #00FF70);
                  padding:20px 40px;border-radius:12px;
                  font-weight:bold;font-size:18px;
                  box-shadow: 2px 4px 10px rgba(0,0,0,0.2);
                  transition: all 0.3s ease;">
            ☕ Donar un café
        </a>
        <span style="margin-top:10px;font-weight:bold;font-size:16px;color:#333;
                     background-color:#f0f0f0;padding:5px 10px;
                     border-radius:8px;box-shadow: 1px 2px 5px rgba(0,0,0,0.1);">
            📱 Nequi 3248580136
        </span>
    </div>
    """
    st.markdown(donar_html, unsafe_allow_html=True)

else:
    st.warning("Por favor ingresa tu nombre para iniciar la app.")
























