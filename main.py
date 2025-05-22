import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from fpdf import FPDF
import tempfile
from datetime import datetime

st.set_page_config(page_title="GastosAnalyzer", page_icon="📊")
st.title("📊 GastosAnalyzer - Análisis de Gastos Personales")
st.subheader("📂 Carga tu archivo CSV de gastos")

archivo = st.file_uploader("Arrastra tu archivo aquí o haz clic para buscar", type=["csv"])

if archivo is not None:
    df = pd.read_csv(archivo)
    st.write("🧾 Columnas detectadas en el CSV:")
    st.write(df.columns.tolist())

    st.markdown("### 📋 Datos cargados:")
    st.dataframe(df)

    # Conversión de tipos
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Filtro por fechas
    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()
    rango = st.date_input("📅 Filtra por rango de fechas:", [fecha_min, fecha_max], key="filtro_fechas")

    if rango:
        df = df[(df["Fecha"] >= pd.to_datetime(rango[0])) & (df["Fecha"] <= pd.to_datetime(rango[1]))]

    # Cálculo
    gastos_por_categoria = df.groupby("Categoría")["Monto"].sum()
    total = gastos_por_categoria.sum()

    st.markdown(f"### 💰 Total gastado: **${total:.2f}**")

    # Gráfico de pastel
    st.markdown("### 📊 Distribución de Gastos por Categoría")
    fig1, ax1 = plt.subplots()
    ax1.pie(gastos_por_categoria, labels=gastos_por_categoria.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

    # Gráfico de líneas
    st.markdown("### 📈 Evolución de Gastos por Fecha")
    gastos_diarios = df.groupby("Fecha")["Monto"].sum()
    fig2, ax2 = plt.subplots()
    gastos_diarios.plot(ax=ax2, marker="o")
    ax2.set_ylabel("Monto ($)")
    ax2.set_xlabel("Fecha")
    ax2.set_title("Gastos en el tiempo")
    st.pyplot(fig2)

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Reporte de Gastos", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    pdf.ln(5)
    for _, row in df.iterrows():
        pdf.cell(0, 8, f"{row['Fecha'].date()} - {row['Categoría']}: ${row['Monto']:.2f}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total gastado: ${total:.2f}", ln=True)

    # Guardar gráficos
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp1, \
         tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp2:
        fig1.savefig(tmp1.name, bbox_inches="tight")
        fig2.savefig(tmp2.name, bbox_inches="tight")
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Gráfico por Categoría", ln=True)
        pdf.image(tmp1.name, x=10, y=30, w=160)
        pdf.ln(100)
        pdf.cell(0, 10, "Gráfico por Fecha", ln=True)
        pdf.image(tmp2.name, x=10, y=140, w=160)

    # Descargar PDF
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    st.download_button(
        label="📄 Descargar Informe PDF",
        data=pdf_bytes,
        file_name="reporte_gastos.pdf",
        mime="application/pdf"
    )
