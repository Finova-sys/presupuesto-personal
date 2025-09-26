# app_presupuesto_final.py

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px

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

    # Título y saldo debajo
    saldo_top_html = f"""
    <div style="text-align:center; margin:10px 0;">
        <h1 style="font-size:48px;">💰 Presupuesto Personal</h1>
        <h2 style="color:#1E90FF; font-size:38px; font-weight:bold; margin-top:10px;">
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

    if movimientos_filtrados:
        df_filtrado = pd.DataFrame(movimientos_filtrados)
        df_filtrado = df_filtrado.sort_values(by="fecha", ascending=False)
        # Formato moneda
        df_filtrado["monto"] = df_filtrado["monto"].apply(lambda x: f"${x:,.2f}")
        st.subheader("📋 Movimientos filtrados")
        st.dataframe(df_filtrado, use_container_width=True, height=300)
    else:
        st.info("No hay movimientos en el rango de fechas seleccionado.")

    # -------------------------------
    # Totales detallados
    # -------------------------------
    st.subheader("💵 Resumen")
    st.markdown(f"- **Total Ingresos:** ${total_ingresos:,.2f}")
    st.markdown(f"- **Total Gastos:** ${total_gastos:,.2f}")
    st.markdown(f"- **Total Ahorro:** ${total_ahorro:,.2f}")
    st.markdown(f"- **Total Inversión:** ${total_inversion:,.2f}")

    # Gráfica de barras colorida
    resumen = {
        "Ingresos": total_ingresos,
        "Gastos": total_gastos,
        "Ahorro": total_ahorro,
        "Inversión": total_inversion
    }
    df_resumen = pd.DataFrame(list(resumen.items()), columns=["Categoría", "Monto"])
    colores = {"Ingresos": "#00B140", "Gastos": "#FF4C4C", "Ahorro": "#1E90FF", "Inversión": "#FFD700"}

    fig = px.bar(df_resumen, x="Categoría", y="Monto", text="Monto", height=500)
    fig.update_traces(marker=dict(color=[colores[c] for c in df_resumen["Categoría"]]))
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Saldo debajo de la gráfica en grande
    saldo_bottom_html = f"""
    <div style="text-align:center; margin:20px 0;">
        <h2 style="color:#1E90FF; font-size:40px; font-weight:bold;">
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



















