import streamlit as st
from datetime import date, timedelta
import calendar
import math

st.set_page_config(
    page_title="Calculadora de Metas - Gestão",
    layout="wide"
)

# ============================
# Política 2026 - Gestão / Time
# ============================
METAS_MENSAIS = {
    "JAN": 76,
    "FEV": 132,
    "MAR": 135,
    "ABR": 193,
    "MAI": 223,
    "JUN": 235,
    "JUL": 241,
    "AGO": 229,
    "SET": 278,
    "OUT": 228,
    "NOV": 202,
    "DEZ": 113,
}

POLITICA_GESTAO = {
    "Supervisor 1 - 40%": {
        "percentual_meta": 0.40,
        "valor_referencia": 4000.0,
    },
    "Supervisor 2 - 60%": {
        "percentual_meta": 0.60,
        "valor_referencia": 4000.0,
    },
    "Gerente": {
        "percentual_meta": 1.00,
        "valor_referencia": 8000.0,
    },
    "LDR": {
        "percentual_meta": 1.00,
        "valor_referencia": 1500.0,
    },
    "Sales Enablement / IM": {
        "percentual_meta": 1.00,
        "valor_referencia": 2000.0,
    },
}

MESES_PT = {
    "JAN": "Janeiro",
    "FEV": "Fevereiro",
    "MAR": "Março",
    "ABR": "Abril",
    "MAI": "Maio",
    "JUN": "Junho",
    "JUL": "Julho",
    "AGO": "Agosto",
    "SET": "Setembro",
    "OUT": "Outubro",
    "NOV": "Novembro",
    "DEZ": "Dezembro",
}

# ============================
# Helpers
# ============================
def ultimo_dia_do_mes(d: date) -> date:
    last_day = calendar.monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last_day)


def dias_uteis(inicio: date, fim: date) -> int:
    if inicio > fim:
        return 0

    qtd = 0
    atual = inicio

    while atual <= fim:
        if atual.weekday() < 5:
            qtd += 1
        atual += timedelta(days=1)

    return qtd


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(v, hi))


def fmt_brl(valor: float) -> str:
    s = f"{valor:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def fmt_pct(valor: float) -> str:
    return f"{valor * 100:.1f}%"


def get_cor_atingimento(pct: float) -> str:
    if pct < 0.75:
        return "#EF4444"
    if pct < 1.0:
        return "#F59E0B"
    return "#10B981"


def mensagem_status(pct: float) -> str:
    if pct < 0.75:
        return "⚠️ Abaixo do mínimo para bonificação"
    if pct < 1.0:
        return "🚀 Já entrou na faixa de bônus e está buscando 100%."
    return "🔥 Meta batida!"


def barra_progresso_html(percent: float, cor: str) -> str:
    p = clamp(percent, 0, 1.2) * 100

    return f"""
    <div style="margin-top:4px;">
        <div style="background:#1F2937;border-radius:12px;height:24px;width:100%;overflow:hidden;">
            <div style="width:{p:.2f}%;background:{cor};height:100%;border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:13px;transition:0.4s;">
                {percent * 100:.1f}%
            </div>
        </div>
    </div>
    """


def card_kpi(label: str, valor: str, cor_valor: str = "#FFFFFF") -> str:
    return f"""
    <div style="padding:10px 0;">
        <div style="font-size:14px;color:#9CA3AF;margin-bottom:4px;">{label}</div>
        <div style="font-size:24px;font-weight:700;color:{cor_valor};line-height:1.1;">{valor}</div>
    </div>
    """


def box_status_html(texto: str, cor: str) -> str:
    return f"""
    <div style="background:#111827;padding:12px 14px;border-radius:10px;margin-top:8px;border-left:4px solid {cor};">
        <div style="font-size:15px;color:#F9FAFB;">{texto}</div>
    </div>
    """


def info_box_html(titulo: str, valor: str, fundo: str, cor_texto: str = "#F9FAFB") -> str:
    return f"""
    <div style="background:{fundo};padding:12px 14px;border-radius:10px;margin-top:8px;">
        <div style="font-size:13px;color:#D1D5DB;margin-bottom:4px;">{titulo}</div>
        <div style="font-size:18px;font-weight:700;color:{cor_texto};">{valor}</div>
    </div>
    """


# ============================
# Cálculos
# ============================
def calcular_bonus_gestao(
    realizado: int,
    meta: int,
    valor_referencia: float
):
    if meta <= 0:
        return {
            "bonus": 0.0,
            "pct": 0.0,
            "faixa": "Sem meta definida",
        }

    pct = realizado / meta

    if pct < 0.75:
        return {
            "bonus": 0.0,
            "pct": pct,
            "faixa": "Abaixo de 75%",
        }

    return {
        "bonus": pct * valor_referencia,
        "pct": pct,
        "faixa": "A partir de 75% proporcional ao atingimento",
    }


def faltam_para_faixa(meta: int, realizado_valido: int, faixa: float) -> int:
    alvo = math.ceil(meta * faixa)
    return max(alvo - realizado_valido, 0)


# ============================
# Datas base
# ============================
hoje = date.today()
inicio_mes = date(hoje.year, hoje.month, 1)
fim_mes = ultimo_dia_do_mes(hoje)

dias_uteis_totais = dias_uteis(inicio_mes, fim_mes)
dias_uteis_restantes = dias_uteis(hoje, fim_mes)
dias_uteis_passados = max(dias_uteis_totais - dias_uteis_restantes, 0)


# ============================
# Header
# ============================
st.title("📈 Calculadora de Metas - Gestão")
st.caption("Política mensal 2026 | Gestão, LDR e Sales Enablement / IM")

colA, colB = st.columns([1, 2], gap="large")


# ============================
# Entradas
# ============================
with colA:
    st.subheader("Entradas")

    cargo_gestao = st.selectbox("Cargo", list(POLITICA_GESTAO.keys()))

    mes = st.selectbox(
        "Mês da meta",
        list(METAS_MENSAIS.keys()),
        format_func=lambda x: f"{x} - {MESES_PT[x]}",
    )

    config_gestao = POLITICA_GESTAO[cargo_gestao]

    meta_geral_mes = int(METAS_MENSAIS[mes])
    percentual_meta = float(config_gestao["percentual_meta"])
    valor_referencia = float(config_gestao["valor_referencia"])

    meta_cargo = math.ceil(meta_geral_mes * percentual_meta)

    st.divider()
    st.markdown("### Produção do mês")

    realizado_mes = st.number_input(
        "Reuniões realizadas",
        min_value=0,
        step=1,
        value=0,
    )

    projetado_mes = st.number_input(
        "Reuniões projetadas / estimadas",
        min_value=0,
        step=1,
        value=int(realizado_mes),
        help="Use este campo para simular o fechamento do mês. Se não quiser projetar, deixe igual ao realizado.",
    )

    st.divider()
    st.subheader("Parâmetros da política")
    st.markdown(card_kpi("Meta geral do mês", str(meta_geral_mes)), unsafe_allow_html=True)
    st.markdown(card_kpi("% da meta aplicado", fmt_pct(percentual_meta)), unsafe_allow_html=True)
    st.markdown(card_kpi("Meta do cargo", str(meta_cargo)), unsafe_allow_html=True)
    st.markdown(card_kpi("Valor de referência", fmt_brl(valor_referencia)), unsafe_allow_html=True)

    st.divider()
    st.caption("Regra: abaixo de 75% não bonifica. A partir de 75%, paga atingimento x valor referência.")


# ============================
# Cálculos
# ============================
atingimento_real = 0.0 if meta_cargo == 0 else int(realizado_mes) / meta_cargo
atingimento_proj = 0.0 if meta_cargo == 0 else int(projetado_mes) / meta_cargo

bonus_real = calcular_bonus_gestao(
    int(realizado_mes),
    meta_cargo,
    valor_referencia
)

bonus_proj = calcular_bonus_gestao(
    int(projetado_mes),
    meta_cargo,
    valor_referencia
)

cor_real = get_cor_atingimento(atingimento_real)
cor_proj = get_cor_atingimento(atingimento_proj)

faltam_75 = faltam_para_faixa(meta_cargo, int(realizado_mes), 0.75)
faltam_100 = faltam_para_faixa(meta_cargo, int(realizado_mes), 1.0)

faltam_proj = max(meta_cargo - int(projetado_mes), 0)

excedente_real = max(int(realizado_mes) - meta_cargo, 0)
excedente_proj = max(int(projetado_mes) - meta_cargo, 0)

if dias_uteis_totais > 0 and meta_cargo > 0:
    ideal_ate_hoje = (meta_cargo / dias_uteis_totais) * dias_uteis_passados
else:
    ideal_ate_hoje = 0.0

pace_diff = int(realizado_mes) - ideal_ate_hoje

if dias_uteis_restantes > 0:
    necessario_por_dia = faltam_proj / dias_uteis_restantes
else:
    necessario_por_dia = float("inf") if faltam_proj > 0 else 0.0

necessario_por_semana = necessario_por_dia * 5 if necessario_por_dia != float("inf") else float("inf")


# ============================
# Painel
# ============================
with colB:
    st.subheader("Painel de Atingimento - Gestão / Time")

    p1, p2, p3, p4 = st.columns(4)
    p1.markdown(card_kpi("Cargo", cargo_gestao), unsafe_allow_html=True)
    p2.markdown(card_kpi("Mês", mes), unsafe_allow_html=True)
    p3.markdown(card_kpi("Meta cargo", str(meta_cargo)), unsafe_allow_html=True)
    p4.markdown(card_kpi("Valor ref.", fmt_brl(valor_referencia)), unsafe_allow_html=True)

    st.divider()

    a1, a2, a3, a4 = st.columns(4)
    a1.markdown(card_kpi("Realizado", str(int(realizado_mes)), cor_real), unsafe_allow_html=True)
    a2.markdown(card_kpi("Projetado", str(int(projetado_mes)), cor_proj), unsafe_allow_html=True)
    a3.markdown(card_kpi("Faltam proj.", str(faltam_proj), "#10B981" if faltam_proj == 0 else "#EF4444"), unsafe_allow_html=True)
    a4.markdown(card_kpi("Excedente proj.", str(excedente_proj), "#10B981"), unsafe_allow_html=True)

    st.divider()

    b1, b2 = st.columns(2)

    with b1:
        st.markdown(card_kpi("Bônus atual", fmt_brl(bonus_real["bonus"]), cor_real), unsafe_allow_html=True)
        st.caption(f"{bonus_real['faixa']} | {fmt_pct(atingimento_real)}")

    with b2:
        st.markdown(card_kpi("Bônus projetado", fmt_brl(bonus_proj["bonus"]), cor_proj), unsafe_allow_html=True)
        st.caption(f"{bonus_proj['faixa']} | {fmt_pct(atingimento_proj)}")

    st.markdown(barra_progresso_html(atingimento_proj, cor_proj), unsafe_allow_html=True)
    st.markdown(box_status_html(mensagem_status(atingimento_proj), cor_proj), unsafe_allow_html=True)

    if excedente_proj > 0:
        valor_acima_100 = bonus_proj["bonus"] - valor_referencia

        st.markdown(
            info_box_html(
                "Excedente projetado",
                f"💰 {excedente_proj} reunião(ões) acima da meta | Valor acima de 100%: {fmt_brl(valor_acima_100)}",
                "#052e16",
                "#86EFAC",
            ),
            unsafe_allow_html=True,
        )

    st.divider()

    r1, r2, r3 = st.columns(3)

    if necessario_por_dia == float("inf"):
        r1.markdown(card_kpi("Necessário por dia útil", "—"), unsafe_allow_html=True)
        r2.markdown(card_kpi("Necessário por semana útil", "—"), unsafe_allow_html=True)
    else:
        r1.markdown(card_kpi("Necessário por dia útil", f"{necessario_por_dia:.2f}"), unsafe_allow_html=True)
        r2.markdown(card_kpi("Necessário por semana útil", f"{necessario_por_semana:.2f}"), unsafe_allow_html=True)

    r3.markdown(card_kpi("Ideal até hoje", f"{ideal_ate_hoje:.1f}"), unsafe_allow_html=True)

    if meta_cargo == 0:
        st.info("Defina uma meta para calcular ritmo e bônus.")
    else:
        if pace_diff >= 0:
            st.success(f"Você está {pace_diff:.1f} reunião(ões) adiantado(a) vs. o ritmo ideal.")
        else:
            st.error(f"Você está {abs(pace_diff):.1f} reunião(ões) atrasado(a) vs. o ritmo ideal.")

    st.divider()

    i1, i2 = st.columns(2)
    i1.markdown(card_kpi("Faltam para 75%", str(faltam_75), "#F59E0B" if faltam_75 > 0 else "#10B981"), unsafe_allow_html=True)
    i2.markdown(card_kpi("Faltam para 100%", str(faltam_100), "#F59E0B" if faltam_100 > 0 else "#10B981"), unsafe_allow_html=True)

    st.caption("Para Gestão / Time, a origem da reunião não importa. O cálculo considera apenas reuniões realizadas contra a meta do cargo.")

    with st.expander("Ver memória de cálculo"):
        st.write(
            {
                "cargo": cargo_gestao,
                "mes": mes,
                "meta_geral_mes": meta_geral_mes,
                "percentual_meta": percentual_meta,
                "meta_cargo": meta_cargo,
                "valor_referencia": valor_referencia,
                "realizado_mes": int(realizado_mes),
                "projetado_mes": int(projetado_mes),
                "atingimento_real": atingimento_real,
                "atingimento_projetado": atingimento_proj,
                "bonus_real": bonus_real["bonus"],
                "bonus_projetado": bonus_proj["bonus"],
                "excedente_real": excedente_real,
                "excedente_projetado": excedente_proj,
            }
        )


st.divider()

st.caption(
    "Gestão/Time: abaixo de 75% sem bônus; a partir de 75% bônus proporcional ao atingimento x valor referência."
)

st.caption(
    "Meta do cargo = meta geral do mês x percentual de responsabilidade."
)
