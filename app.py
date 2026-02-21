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

st.sidebar.subheader("Tokenização (GPT-5 mini)")
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
price_in_per_1m_usd = col_in.number_input("Input (US$)", value=0.25, step=0.05)
price_out_per_1m_usd = col_out.number_input("Output (US$)", value=2.00, step=0.10)

# --- NOVA SEÇÃO: ACESSIBILIDADE VIA ÁUDIO ---
st.sidebar.header("4. Acessibilidade e Inclusão (Áudio)")
usar_audio = st.sidebar.checkbox("Habilitar Recepção por Áudio (Whisper)", value=False, help="Permite ao cidadão enviar mensagens de voz em vez de digitar, mitigando o analfabetismo funcional.")

custo_audio_usd = 0.0
tempo_audio = 0.0
if usar_audio:
    tempo_audio = st.sidebar.number_input("Duração Média do Áudio (minutos)", value=1.0, step=0.5)
    preco_whisper = st.sidebar.number_input("Custo Transcrição (US$/min)", value=0.006, step=0.001, format="%.3f")
    custo_audio_usd = tempo_audio * preco_whisper
    st.sidebar.caption(f"Custo adicional do áudio: US$ {custo_audio_usd:.4f} por atendimento")

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

# 3) Custo IA (Município) — tokens de entrada, saída e áudio
custo_ia_texto_usd = (tokens_in / 1_000_000) * price_in_per_1m_usd + (tokens_out / 1_000_000) * price_out_per_1m_usd
custo_ia_total_usd = custo_ia_texto_usd + custo_audio_usd
custo_atendimento_ia = custo_ia_total_usd * dolar  # convertendo para R$

# 4) Economia (Município)
economia_unitaria = custo_atendimento_trad - custo_atendimento_ia
economia_percentual = (economia_unitaria / custo_atendimento_trad) * 100 if custo_atendimento_trad > 0 else 0

# --- EXIBIÇÃO DOS RESULTADOS (DASHBOARD) ---
col1, col2, col3 = st.columns(3)

with col1:
    titulo_ia = "🤖 Custo via IA (Texto + Áudio)" if usar_audio else "🤖 Custo via IA (Apenas Texto)"
    st.success(titulo_ia)
    st.metric(label="Custo Unitário p/ Município", value=f"R$ {custo_atendimento_ia:.4f}")
    
    detalhe_tokens = f"Tokens: in={tokens_in} | out={tokens_out}"
    if usar_audio:
        detalhe_tokens += f" | Áudio={tempo_audio}min"
    
    st.caption(f"{detalhe_tokens} | dólar={dolar:.2f}")
    st.metric(label="Tempo Gasto pelo Cidadão", value="~1 a 2 min")

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
    title="Custo Unitário para os Cofres Públicos",
    color_discrete_map={"Tradicional (Presencial)": "#ff4b4b", "Governança Digital (IA)": "#00CC96"}
)

fig.update_traces(width=0.4, texttemplate='R$ %{y:.2f}', textposition='outside')
fig.update_layout(showlegend=False, yaxis_title="Custo (R$)", xaxis_title="", yaxis_range=[0, max(custo_atendimento_trad, custo_atendimento_ia) * 1.2])

st.plotly_chart(fig, use_container_width=True)

# --- Parecer automático ---
st.markdown("### 📝 Parecer Técnico da Simulação")

texto_audio_inclusao = "A inclusão do módulo de reconhecimento de voz (Áudio) reforça a mitigação do analfabetismo funcional sem impactar negativamente a viabilidade orçamentária. " if usar_audio else ""

if custo_atendimento_trad > custo_atendimento_ia:
    parecer_html = f"""
    <div style="font-size: 18px; line-height: 1.6; padding: 20px; background-color: #e6f4ea; border-left: 6px solid #34a853; border-radius: 5px; color: #1e4620; margin-bottom: 20px;">
        <strong style="font-size: 20px;">✅ PARECER TÉCNICO FAVORÁVEL: VIABILIDADE CONFIRMADA</strong><br><br>
        A simulação demonstra a <b>alta viabilidade econômica e operacional</b> da adoção de Agentes de Inteligência Artificial para a prestação de serviços informacionais. Observa-se uma redução substancial nas despesas de custeio da máquina pública municipal.<br><br>
        {texto_audio_inclusao}
        Sob a ótica do bem-estar social e do Princípio da Eficiência, a solução tecnológica elimina um encargo financeiro de deslocamento estimado em <b>R$ {custo_deslocamento:.2f}</b> para o munícipe, mitigando o histórico gargalo geográfico de <b>{distancia} km</b>. Conclui-se que a medida promove uma <b>Governança Digital verdadeiramente inclusiva</b>, ampliando a transparência e efetivando o acesso aos serviços essenciais com zelo ao erário.
    </div>
    """
    st.markdown(parecer_html, unsafe_allow_html=True)
else:
    parecer_html = f"""
    <div style="font-size: 18px; line-height: 1.6; padding: 20px; background-color: #fce8e6; border-left: 6px solid #ea4335; border-radius: 5px; color: #681d15; margin-bottom: 20px;">
        <strong style="font-size: 20px;">⚠️ ALERTA TÉCNICO: REVISÃO DE PARÂMETROS NECESSÁRIA</strong><br><br>
        Considerando o atual arranjo de custos de processamento em nuvem (tokenização) frente aos custos operacionais presenciais, a transição digital <b>não apresenta</b>, neste cenário específico, vantagem financeira imediata para o erário.<br><br>
        Recomenda-se à Gestão Municipal a reavaliação do desenho institucional, a negociação de contratos de infraestrutura tecnológica ou a otimização do fluxo de atendimento para garantir a eficiência econômica do projeto antes de sua plena expansão.
    </div>
    """
    st.markdown(parecer_html, unsafe_allow_html=True)

# --- Transparência metodológica (opcional, mas ajuda MUITO banca) ---
with st.expander("🔍 Ver fórmulas (transparência metodológica)"):
    st.markdown("""
**Custo humano (município):**
- `custo_minuto_humano = salario / 160 / 60`
- `custo_atendimento_trad = tempo_atendimento (min) × custo_minuto_humano`

**Custo deslocamento (cidadão):**
- `custo_deslocamento = (distância × 2 / km_por_litro) × preço_combustível`
- `tempo_total = (distância × 2 / velocidade_média) + tempo_atendimento/60`

**Custo IA (município) – GPT-5 mini + Áudio (opcional):**
- `custo_texto_usd = (tokens_in/1e6) × preco_input + (tokens_out/1e6) × preco_output`
- `custo_audio_usd = tempo_audio (min) × preco_whisper_minuto`
- `custo_ia_brl = (custo_texto_usd + custo_audio_usd) × dólar`
""")
