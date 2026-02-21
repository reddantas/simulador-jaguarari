%%writefile simulador_jaguarari.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador Governança Digital - Jaguarari", layout="wide")

# Cabeçalho
st.title("🏛️ Simulador de Economia: Governança Digital vs. Tradicional")
st.markdown("""
Esta ferramenta simula o impacto financeiro e temporal da implementação de Agentes de IA 
no atendimento ao cidadão em **Jaguarari-BA**, comparado ao modelo presencial tradicional.
""")
st.markdown("---")

# --- BARRA LATERAL (INPUTS DOS VALORES REAIS) ---
st.sidebar.header("1. Parâmetros do Município")
salario_servidor = st.sidebar.number_input(
    "Salário Médio Servidor + Encargos (R$)", value=3000.00, step=100.00
)
tempo_atendimento = st.sidebar.number_input(
    "Tempo Médio de Atendimento Humano (min)", value=20, step=5
)

st.sidebar.header("2. Parâmetros do Cidadão")
distancia = st.sidebar.number_input(
    "Distância do Povoado à Sede (km)", value=70, step=5,
    help="Ex: Pilar fica a ~70 km"
)
custo_combustivel = st.sidebar.number_input(
    "Preço Gasolina/Passagem (R$)", value=6.59, step=0.10
)
veiculo_kml = st.sidebar.number_input(
    "Consumo do Veículo (km/L)", value=12, step=1
)

st.sidebar.header("3. Parâmetros da Tecnologia (IA)")
dolar = st.sidebar.number_input("Cotação Dólar (R$)", value=6.15, step=0.01)

# --- ATUALIZADO PARA GPT-5 E PREÇOS DINÂMICOS ---
st.sidebar.subheader("Tokenização (GPT-5)")
tokens_in = st.sidebar.number_input(
    "Tokens de Entrada (prompt + contexto)", value=900, step=100,
    help="Inclui a pergunta do cidadão + contexto/instruções do sistema"
)
tokens_out = st.sidebar.number_input(
    "Tokens de Saída (resposta)", value=600, step=100,
    help="Tamanho médio da resposta do agente"
)

st.sidebar.caption("Configuração de Preços da API (US$ por 1 Milhão de Tokens):")
col_in, col_out = st.sidebar.columns(2)
price_in_per_1m_usd = col_in.number_input("Input (US$)", value=2.50, step=0.10)
price_out_per_1m_usd = col_out.number_input("Output (US$)", value=10.00, step=0.50)

st.sidebar.markdown("---")
st.sidebar.info("Baseado na metodologia do TCC: 'Governança Digital Inclusiva em Jaguarari-BA'")

# --- CÁLCULOS (MOTOR DA SIMULAÇÃO) ---

# 1) Custo Tradicional (Município) — hora-homem
custo_minuto_humano = salario_servidor / 160 / 60
custo_atendimento_trad = tempo_atendimento * custo_minuto_humano

# 2) Custo Tradicional (Cidadão) — deslocamento ida e volta
custo_deslocamento = (distancia * 2 / veiculo_kml) * custo_combustivel

# Tempo (cidadão): deslocamento (velocidade média 60 km/h) + atendimento
velocidade_media_kmh = 60
tempo_deslocamento_h = (distancia * 2) / velocidade_media_kmh
tempo_total_trad_h = tempo_deslocamento_h + (tempo_atendimento / 60)

# 3) Custo IA (Município) — tokens de entrada e saída (GPT-5)
custo_ia_usd = (tokens_in / 1_000_000) * price_in_per_1m_usd + (tokens_out / 1_000_000) * price_out_per_1m_usd
custo_atendimento_ia = custo_ia_usd * dolar  # convertendo para R$

# 4) Economia (Município)
economia_unitaria = custo_atendimento_trad - custo_atendimento_ia
economia_percentual = (economia_unitaria / custo_atendimento_trad) * 100 if custo_atendimento_trad > 0 else 0

# --- EXIBIÇÃO DOS RESULTADOS (DASHBOARD) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.success("🤖 Custo via IA (Digital)")
    st.metric(label="Custo Unitário p/ Município", value=f"R$ {custo_atendimento_ia:.4f}")
    st.caption(f"Tokens: entrada={tokens_in} | saída={tokens_out} | dólar={dolar:.2f}")
    st.metric(label="Tempo Gasto pelo Cidadão", value="~1 min")

with col2:
    st.error("🏢 Custo Tradicional (Presencial)")
    st.metric(label="Custo Unitário p/ Município", value=f"R$ {custo_atendimento_trad:.2f}")
    st.metric(label="Custo Deslocamento (Cidadão)", value=f"R$ {custo_deslocamento:.2f}")
    st.metric(label="Tempo Total Gasto", value=f"{tempo_total_trad_h:.1f} horas")

with col3:
    st.info("📊 Resultado da Eficiência")
    st.metric(label="Economia por Atendimento", value=f"R$ {economia_unitaria:.2f}", delta=f"{economia_percentual:.1f}%")
    projecao_1000 = economia_unitaria * 1000
    st.write(f"Em **1.000 atendimentos**, o município economizaria: **R$ {projecao_1000:,.2f}**")

# --- GRÁFICOS ---
st.markdown("### Comparativo Visual de Custos")

dados = pd.DataFrame({
    "Método": ["Tradicional (Presencial)", "Governança Digital (IA)"],
    "Custo Operacional (R$)": [custo_atendimento_trad, custo_atendimento_ia]
})

fig = px.bar(
    dados, x="Método", y="Custo Operacional (R$)", color="Método",
    text_auto=".4s", title="Custo Unitário para os Cofres Públicos",
    color_discrete_map={"Tradicional (Presencial)": "#ff4b4b", "Governança Digital (IA)": "#00CC96"}
)
st.plotly_chart(fig, use_container_width=True)

# --- Parecer automático ---
st.markdown("### 📝 Parecer do Simulador")

if custo_atendimento_trad > custo_atendimento_ia:
    st.write(f"""
> **Viabilidade Confirmada:** A implementação da IA reduz drasticamente o custo operacional municipal.
> Além disso, elimina o custo de **R$ {custo_deslocamento:.2f}** para o cidadão que reside a **{distancia} km** da sede,
> ampliando o acesso à informação e reduzindo barreiras geográficas.
""")
else:
    st.write("""
> **Atenção:** Com os parâmetros atuais, o custo calculado da IA não ficou menor que o presencial.
> Revise tokenização, tempo de atendimento, salário/encargos e o preço do modelo atual.
""")
