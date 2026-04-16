import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(
    page_title="Aurum MX",
    page_icon="",
    layout="wide",
)

# ----------------------------
# Datos base del deal
# ----------------------------
PROJECT_NAME = "Aurum MX"
DEAL_NAME = "Deal #001 - Compra de Oro Físico"
TARGET_AMOUNT = 270_000
GOLD_GRAMS = 100
EXPECTED_RETURN = "Indicativo: 3% - 5% por operación"
EXPECTED_DURATION = "Variable, sujeto a originación de oportunidad"
MIN_TICKET = 10_000
FUNDED_PERCENT = 42
DEAL_STAGE = "En búsqueda de oportunidad"
CETES_ANNUAL_RATE = 0.0660  # 6.60%
EXECUTION_NOTE = (
    "El capital comprometido se asigna únicamente cuando se identifica una operación "
    "que cumple con los criterios de precio, validación y salida comercial."
)

# ----------------------------
# Estilos
# ----------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1.05rem;
            color: #666666;
            margin-bottom: 1.5rem;
        }
        .hero-box {
            padding: 1.5rem;
            border: 1px solid #E6E6E6;
            border-radius: 16px;
            background-color: #FAFAFA;
        }
        .section-title {
            font-size: 1.35rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }
        .small-muted {
            color: #777777;
            font-size: 0.95rem;
        }
        .cta-box {
            padding: 1.6rem;
            border-radius: 16px;
            background-color: #111111;
            color: white;
            text-align: center;
            border: 1px solid #1f1f1f;
        }
        .criteria-card {
            padding: 1rem;
            border: 1px solid #E6E6E6;
            border-radius: 14px;
            background-color: #FFFFFF;
            height: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Funciones
# ----------------------------
@st.cache_data(ttl=3600)
def load_gold_vs_cetes():
    df = yf.download("GC=F", period="1y", interval="1d", auto_adjust=False, progress=False)

    if df.empty:
        return None

    df = df.reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    if "Date" not in df.columns or "Close" not in df.columns:
        return None

    df = df[["Date", "Close"]].copy()
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna(subset=["Close"]).sort_values("Date").reset_index(drop=True)

    gold_start = float(df["Close"].iloc[0])
    gold_end = float(df["Close"].iloc[-1])
    df["Oro"] = (df["Close"] / gold_start) * 100

    daily_rate = (1 + CETES_ANNUAL_RATE) ** (1 / 365) - 1
    df["day_number"] = range(len(df))
    df["CETES 28d"] = 100 * ((1 + daily_rate) ** df["day_number"])

    gold_return = ((gold_end / gold_start) - 1) * 100
    cetes_return = (df["CETES 28d"].iloc[-1] / 100 - 1) * 100

    plot_df = df[["Date", "Oro", "CETES 28d"]].melt(
        id_vars="Date",
        var_name="Activo",
        value_name="Índice base 100"
    )

    return plot_df, gold_return, cetes_return, gold_start, gold_end


def build_sample_deals():
    df = pd.DataFrame(
        [
            {
                "Deal": "Operación A",
                "Tipo": "Scrap urbano",
                "Dias_originacion": 18,
                "Dias_ejecucion": 6,
                "Retorno_pct": 3.2,
                "Monto_mxn": 180000,
            },
            {
                "Deal": "Operación B",
                "Tipo": "Compra puntual",
                "Dias_originacion": 27,
                "Dias_ejecucion": 9,
                "Retorno_pct": 4.1,
                "Monto_mxn": 250000,
            },
            {
                "Deal": "Operación C",
                "Tipo": "Lote validado",
                "Dias_originacion": 12,
                "Dias_ejecucion": 5,
                "Retorno_pct": 2.8,
                "Monto_mxn": 140000,
            },
            {
                "Deal": "Operación D",
                "Tipo": "Scrap premium",
                "Dias_originacion": 34,
                "Dias_ejecucion": 8,
                "Retorno_pct": 5.0,
                "Monto_mxn": 310000,
            },
        ]
    )
    df["Dias_totales"] = df["Dias_originacion"] + df["Dias_ejecucion"]
    return df


# ----------------------------
# Header
# ----------------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"<div class='main-title'>{PROJECT_NAME}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>"
        "Participación en operaciones privadas de compra y venta de oro físico de corto plazo."
        "</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.metric("Fondeado", f"{FUNDED_PERCENT}%")

st.divider()

# ----------------------------
# Hero principal
# ----------------------------
left, right = st.columns([1.7, 1])

with left:
    st.markdown("<div class='section-title'>Resumen del deal activo</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='hero-box'>
            <h3 style='margin-top:0;'>{DEAL_NAME}</h3>
            <p>
                Este vehículo busca fondear la compra de <b>{GOLD_GRAMS} gramos de oro físico</b>
                por un monto objetivo de <b>${TARGET_AMOUNT:,.0f} MXN</b>.
            </p>
            <p>
                La ejecución de la operación depende de la identificación de una oportunidad
                que cumpla criterios mínimos de precio, validación y salida comercial.
                Una vez activada la compra, la liquidación esperada es de corto plazo.
            </p>
            <p>
                <b>Retorno objetivo por operación:</b> {EXPECTED_RETURN}
            </p>
            <p class='small-muted'>
                {EXECUTION_NOTE}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("<div class='section-title'>Indicadores clave</div>", unsafe_allow_html=True)
    st.metric("Capital objetivo", f"${TARGET_AMOUNT:,.0f} MXN")
    st.metric("Oro objetivo", f"{GOLD_GRAMS} g")
    st.metric("Retorno objetivo", EXPECTED_RETURN)
    st.metric("Horizonte", EXPECTED_DURATION)
    st.metric("Ticket mínimo", f"${MIN_TICKET:,.0f} MXN")
    st.metric("Estado del deal", DEAL_STAGE)

st.divider()

# ----------------------------
# Progreso de fondeo
# ----------------------------
st.markdown("<div class='section-title'>Progreso de fondeo</div>", unsafe_allow_html=True)
st.progress(FUNDED_PERCENT / 100)
remaining_capital = TARGET_AMOUNT * (1 - FUNDED_PERCENT / 100)
c1, c2 = st.columns([1, 2])
with c1:
    st.metric("Capital disponible", f"${remaining_capital:,.0f} MXN")
with c2:
    st.caption(
        f"Actualmente el deal se encuentra al {FUNDED_PERCENT}% del objetivo de fondeo. "
        "La asignación final depende de la originación de una oportunidad elegible."
    )

# ----------------------------
# Oro vs CETES
# ----------------------------
st.markdown("<div class='section-title'>Oro vs CETES en los últimos 12 meses</div>", unsafe_allow_html=True)

result = load_gold_vs_cetes()

if result is not None:
    plot_df, gold_return, cetes_return, gold_start, gold_end = result

    m1, m2, m3 = st.columns(3)
    m1.metric("Oro 12 meses", f"{gold_return:,.2f}%")
    m2.metric("CETES 12 meses", f"{cetes_return:,.2f}%")
    m3.metric("Diferencia", f"{(gold_return - cetes_return):,.2f} pp")

    fig = px.line(
        plot_df,
        x="Date",
        y="Índice base 100",
        color="Activo",
        title="Comparación de crecimiento: Oro vs CETES 28 días",
        labels={"Date": "Fecha", "Índice base 100": "Base 100"}
    )

    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title_text=""
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Comparación visual con base 100 al inicio del periodo. "
        "La curva de CETES usa como benchmark una tasa anual de 6.60%."
    )
else:
    st.error("No se pudo cargar la comparación Oro vs CETES.")

# ----------------------------
# Histórico ilustrativo
# ----------------------------
st.divider()
st.markdown("<div class='section-title'>Histórico ilustrativo de operaciones</div>", unsafe_allow_html=True)

st.caption(
    "Ejemplos ilustrativos para mostrar la mecánica del vehículo. "
    "No representan operaciones ejecutadas ni constituyen promesa de plazo o rendimiento."
)

sample_deals = build_sample_deals()

m1, m2, m3 = st.columns(3)
m1.metric("Retorno promedio ilustrativo", f"{sample_deals['Retorno_pct'].mean():.2f}%")
m2.metric("Originación promedio", f"{sample_deals['Dias_originacion'].mean():.0f} días")
m3.metric("Ejecución promedio", f"{sample_deals['Dias_ejecucion'].mean():.0f} días")

tab1, tab2 = st.tabs(["Tabla resumen", "Visualización"])

with tab1:
    display_df = sample_deals.rename(
        columns={
            "Deal": "Operación",
            "Tipo": "Tipo",
            "Dias_originacion": "Días de originación",
            "Dias_ejecucion": "Días de ejecución",
            "Dias_totales": "Días totales",
            "Retorno_pct": "Retorno (%)",
            "Monto_mxn": "Monto (MXN)",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    chart_df = sample_deals.melt(
        id_vars=["Deal"],
        value_vars=["Dias_originacion", "Dias_ejecucion"],
        var_name="Fase",
        value_name="Días",
    )

    chart_df["Fase"] = chart_df["Fase"].replace(
        {
            "Dias_originacion": "Originación",
            "Dias_ejecucion": "Ejecución",
        }
    )

    fig_ops = px.bar(
        chart_df,
        x="Deal",
        y="Días",
        color="Fase",
        title="Tiempo por fase en operaciones ilustrativas",
        barmode="stack",
        labels={"Deal": "Operación", "Días": "Días"},
    )
    fig_ops.update_layout(height=420, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_ops, use_container_width=True)

    fig_ret = px.scatter(
        sample_deals,
        x="Dias_totales",
        y="Retorno_pct",
        size="Monto_mxn",
        hover_name="Deal",
        title="Retorno ilustrativo vs duración total",
        labels={
            "Dias_totales": "Días totales",
            "Retorno_pct": "Retorno (%)",
            "Monto_mxn": "Monto (MXN)",
        },
    )
    fig_ret.update_layout(height=420, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_ret, use_container_width=True)

# ----------------------------
# Estructura de la operación
# ----------------------------
st.divider()
st.markdown("<div class='section-title'>Estructura de la operación</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.info(
        """
        **Fase 1: Originación**

        - Identificación de oportunidades en mercado físico
        - Evaluación de precio y pureza
        - No hay ejecución hasta encontrar condiciones favorables
        """
    )

with col2:
    st.info(
        """
        **Fase 2: Ejecución**

        - Compra del oro
        - Venta a contraparte identificada
        - Liquidación de corto plazo una vez activado el deal
        """
    )

# ----------------------------
# Criterios de inversión
# ----------------------------
st.markdown("<div class='section-title'>Criterios de inversión</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class='criteria-card'>
            <h4>Descuento mínimo</h4>
            <p>La operación solo se activa si existe una ventana atractiva de precio frente a la referencia de mercado.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class='criteria-card'>
            <h4>Validación de pureza</h4>
            <p>El activo debe pasar un proceso mínimo de validación antes de ser considerado elegible.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class='criteria-card'>
            <h4>Salida identificada</h4>
            <p>No se ejecuta una compra sin tener ruta comercial clara para la venta y liquidación de la operación.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------
# Cómo funciona
# ----------------------------
st.divider()
st.markdown("<div class='section-title'>Cómo funciona</div>", unsafe_allow_html=True)

step1, step2, step3, step4 = st.columns(4)

with step1:
    st.info("1. Se identifica una oportunidad de compra de oro físico.")

with step2:
    st.info("2. Se valida precio, pureza y salida comercial.")

with step3:
    st.info("3. Se ejecuta la compra y posterior venta del activo.")

with step4:
    st.info("4. Se distribuye el capital y el resultado de la operación.")

# ----------------------------
# CTA
# ----------------------------
st.divider()
st.markdown(
    """
    <div class="cta-box">
        <h2 style="margin-bottom: 0.5rem;">Solicitar acceso al deal</h2>
        <p style="margin-bottom: 1rem;">
            Cupo limitado. Registro de interés para recibir la ficha de operación y prioridad de asignación.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Los espacios se asignan por orden de confirmación. "
    "Este formulario no representa una inversión formal, solo registro de interés."
)

with st.form("interest_form"):
    st.subheader("Registrar interés")

    name = st.text_input("Nombre")
    email = st.text_input("Correo electrónico")
    phone = st.text_input("Teléfono")
    amount = st.number_input("Monto de interés (MXN)", min_value=1000, step=1000)
    comments = st.text_area("Comentarios", placeholder="Ej. Me interesa recibir más detalles del vehículo.")

    submitted = st.form_submit_button("Recibir ficha de operación")

    if submitted:
        st.success(
            "Gracias. Tu registro fue recibido correctamente. "
            "Te contactaremos para compartir la información del deal."
        )
        st.write("Resumen del registro")
        st.write(
            {
                "nombre": name,
                "email": email,
                "telefono": phone,
                "monto_interes_mxn": amount,
                "comentarios": comments,
            }
        )

# ----------------------------
# Nota legal
# ----------------------------
st.divider()
st.markdown("<div class='section-title'>Nota importante</div>", unsafe_allow_html=True)
st.warning(
    "La información mostrada es preliminar e ilustrativa. No constituye una oferta pública de inversión, "
    "promesa de rendimiento garantizado ni asesoría financiera. Toda participación debe evaluarse de forma privada "
    "y con documentación contractual correspondiente."
)