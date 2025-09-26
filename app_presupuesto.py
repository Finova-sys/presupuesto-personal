# app_presupuesto.py

import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

# -------------------------------
# Configuración inicial
# -------------------------------
st.set_page_config(page_title="Presupuesto Personal", page_icon="💰", layout="wide")

st.title("💰 Presupuesto Personal")

# -------------------------------
# Nombre de usuario
# -------------------------------
usuario = st.text_input("Ingresa tu nombre (para guardar tus datos)", "")

if usuario:
    archivo_usuario = f"{usuario}.json"
    if os.path.exists(archivo_usuario):
        with open(archivo_usuario, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"ingresos": [], "gastos": [], "ahorro": [], "inversion": []}

    # -------------------------------
    # Categorías comunes
    # -------------------------------
    categorias_gasto = ["Alimentos", "Transporte", "Servicios", "Entretenimiento", "Salud", "Educación", "Otros"]
    categorias_ingreso = ["Salario", "Freelance", "Negocio", "Otros"]

    # -------------------------------
    # Registrar Movimientos
    # -------------------------------
    st.subheader("📥 Agregar Ingreso")
    ingreso_cat = st.selectbox("Categoría", categorias_ingreso, key="ingreso_cat")
    ingreso_monto = st.number_input("Monto", min_value=0.0, step=10.0, key="ingreso_monto")
    if st.button("Agregar Ingreso", key="btn_ingreso"):
        data["ingresos"].append({"categoria": ingreso_cat, "monto": ingreso_monto})
        st.success(f"Ingreso de {ingreso_monto} agregado en {ingreso_cat}")

    st.subheader("📤 Agregar Gasto")
    gasto_cat = st.selectbox("Categoría", categorias_gasto, key="gasto_cat")
    gasto_monto = st.number_input("Monto", min_value=0.0, step=10.0, key="gasto_monto")
    if st.button("Agregar Gasto", key="btn_gasto"):
        data["gastos"].append({"categoria": gasto_cat, "monto": gasto_monto})
        st.success(f"Gasto de {gasto_monto} agregado en {gasto_cat}")

    st.subheader("💾 Agregar Ahorro")
    ahorro_monto = st.number_input("Monto de ahorro", min_value=0.0, step=10.0, key="ahorro_monto")
    if st.button("Agregar Ahorro", key="btn_ahorro"):
        data["ahorro"].append({"monto": ahorro_monto})
        st.success(f"Ahorro de {ahorro_monto} agregado")

    st.subheader("📈 Agregar Inversión")
    inversion_monto = st.number_input("Monto de inversión", min_value=0.0, step=10.0, key="inversion_monto")
    if st.button("Agregar Inversión", key="btn_inversion"):
        data["inversion"].append({"monto": inversion_monto})
        st.success(f"Inversión de {inversion_monto} agregada")

    # -------------------------------
    # Guardar datos automáticamente
    # -------------------------------
    with open(archivo_usuario, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # -------------------------------
    # Mostrar saldo disponible
    # -------------------------------
    total_ingresos = sum([i["monto"] for i in data["ingresos"]])
    total_gastos = sum([g["monto"] for g in data["gastos"]])
    total_ahorro = sum([a["monto"] for a in data["ahorro"]])
    total_inversion = sum([inv["monto"] for inv in data["inversion"]])
    saldo = total_ingresos - total_gastos - total_ahorro - total_inversion

    st.subheader("💵 Resumen")
    st.write(f"**Total Ingresos:** {total_ingresos}")
    st.write(f"**Total Gastos:** {total_gastos}")
    st.write(f"**Total Ahorro:** {total_ahorro}")
    st.write(f"**Total Inversión:** {total_inversion}")
    st.write(f"**Saldo Disponible:** {saldo}")

    # -------------------------------
    # Gráfica de barras
    # -------------------------------
    resumen = {
        "Ingresos": total_ingresos,
        "Gastos": total_gastos,
        "Ahorro": total_ahorro,
        "Inversión": total_inversion
    }
    df = pd.DataFrame(list(resumen.items()), columns=["Categoría", "Monto"])
    fig = px.bar(df, x="Categoría", y="Monto", color="Categoría", text="Monto")
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Botón de donación
    # -------------------------------
    st.subheader("☕ Donar un café")
    st.markdown(
        "[Pagar a mi Nequi](https://nequi.com/3248580136) 🔗",
        unsafe_allow_html=True
    )
else:
    st.warning("Por favor ingresa tu nombre para iniciar la app.")
