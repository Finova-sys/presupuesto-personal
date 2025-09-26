# app_presupuesto_final.py

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.graph_objects as go

# -------------------------------
# Configuración inicial
# -------------------------------
st.set_page_config(page_title="💰 Presupuesto Personal",
                   page_icon="💸",
                   layout="wide",
                   initial_sidebar_state="collapsed")

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
    descripciones_comunes = {
        "Alimentos": ["Supermercado", "Restaurante", "Café"],
        "Transporte": ["Taxi", "Gasolina", "Bus", "Metro"],
        "Servicios": ["Luz", "Agua", "Internet", "Teléfono"],
        "Entretenimiento": ["Cine", "Concierto", "Videojuegos"],
        "Salud": ["Medicamentos", "Consultas", "Gym"],
        "Educación": ["Cursos", "Libros", "Talleres"],
        "Otros": ["Varios"],
        "Salario": ["Mensual", "Extra"],
        "Freelance": ["Proyecto1", "Proyecto2"],
        "Negocio": ["Ventas", "Servicios"],
    }

    tipos_movimiento = ["Ingreso", "Gasto", "Ahorro", "Inversión"]
    tipo = st.selectbox("Tipo de Movimiento", tipos_movimiento, key="tipo_mov")

    if tipo == "Ingreso":
        categoria = st.selectbox("Categoría", categorias_ingreso, key="cat_mov")
    else:
        categoria = st.selectbox("Categoría", categorias_gasto, key="cat_mov")

    descripcion = st.selectbox("Descripción", descripciones_comunes.get(categoria, ["Otro"]), key="desc_mov")
    monto = st.number_input("Monto", min_value=0.0, step=10.0, key="monto_mov")

    if st.button("Agregar Movimiento"):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data[tipo.lower()].append({
            "fecha": fecha,
            "categoria": categoria,
            "descripcion": descripcion,
            "monto": monto
        })
        # Guardar automáticamente
        with open(archivo_usuario, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        st.success(f"{tipo} agregado: {monto} en {categoria} ({descripcion})")

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

    if movimientos_filtrados:
        df_filtrado = pd.DataFrame(movimientos_filtrados)
        df_filtrado = df_filtrado.sort_values(by="fecha", ascending=False)
        st.subheader("📋 Movimientos filtrados")
        st.dataframe(df_filtrado, use_container_width=True, height=300)
    else:
        st.info("No hay movimientos en el rango de fechas seleccionado.")

    # -------------------------------
    # Resumen y gráfica 3D
    # -------------------------------
    total_ingresos = sum([i["monto"] for i in data["ingresos"]])
    total_gastos = sum([g["monto"] for g in data["gastos"]])
    total_ahorro = sum([a["monto"] for a in data["ahorro"]])
    total_inversion = sum([inv["monto"] for inv in data["inversion"]])
    saldo = total_ingresos - total_gastos - total_ahorro - total_inversion

    st.subheader("💵 Resumen")
    st.markdown(f"- **Total Ingresos:** {total_ingresos}")
    st.markdown(f"- **Total Gastos:** {total_gastos}")
    st.markdown(f"- **Total Ahorro:** {total_ahorro}")
    st.markdown(f"- **Total Inversión:** {total_inversion}")
    st.markdown(f"- **Saldo Disponible:** {saldo}")

    # Gráfica 3D
    resumen = {
        "Ingresos": total_ingresos,
        "Gastos": total_gastos,
        "Ahorro": total_ahorro,
        "Inversión": total_inversion
    }
    categorias = list(resumen.keys())
    montos = list(resumen.values())
    colores = ["green", "red", "blue", "orange"]

    fig = go.Figure(data=[go.Bar3d(
        x=categorias,
        y=["Total"]*len(categorias),
        z=[0]*len(categorias),
        dx=0.5,
        dy=0.5,
        dz=montos,
        marker=dict(color=colores),
    )])

    fig.update_layout(scene=dict(
        xaxis_title='Categoría',
        yaxis_title='',
        zaxis_title='Monto'
    ))
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Botón de donación bonito
    # -------------------------------
    st.subheader("☕ Donar un café")
    donar_html = f"""
    <a href="https://nequi.com/3248580136" target="_blank" style="
        text-decoration:none;
        color:white;
        background-color:#00B140; 
        padding:10px 20px; 
        border-radius:8px; 
        font-weight:bold;
        display:inline-block;">
        ☕ Donar un café
    </a>
    """
    st.markdown(donar_html, unsafe_allow_html=True)

else:
    st.warning("Por favor ingresa tu nombre para iniciar la app.")
