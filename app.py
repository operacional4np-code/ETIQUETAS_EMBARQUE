import os
import io
import pandas as pd
import streamlit as st
from datetime import datetime  # <-- Importamos para capturar a data atual
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(
    page_title="Gerador de Etiquetas de Embarque",
    page_icon="✈️",
    layout="centered"
)

CSV_PATH = 'destinos.csv'

# --- CONFIGURAÇÕES DE FONTE ---
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
except Exception as e:
    st.warning(f"Aviso: Não foi possível carregar as fontes Arial: {e}. Usando fontes padrão do ReportLab.")

# --- FUNÇÕES DE MANIPULAÇÃO DE DADOS ---
def carregar_dataframe():
    colunas = ['sigla', 'nome_recebedor', 'cnpj_recebedor', 'endereco_recebedor', 'cidade_recebedor', 'uf_recebedor', 'cep_recebedor', 'pais_recebedor']
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(CSV_PATH)
    for col in colunas:
        if col not in df.columns:
            df[col] = ""
    return df

def salvar_dataframe(df):
    df.to_csv(CSV_PATH, index=False)

# --- FUNÇÃO DE GERAÇÃO DO PDF ---
def gerar_etiquetas_pdf(sigla, quantidade, dados_recebedor):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(150 * mm, 100 * mm))
    styles = getSampleStyleSheet()
    
    font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    font_bold = 'Arial-Bold' if 'Arial-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
    
    style_normal = ParagraphStyle(
        name='Normal', 
        parent=styles['Normal'], 
        fontName=font_name, 
        fontSize=11, 
        leading=13, 
        alignment=TA_LEFT
    )
    
    # Captura a data atual no formato DD/MM/AAAA
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    for i in range(1, quantidade + 1):
        margem_h = 5 * mm
        largura_maxima = 140 * mm
        
        c.setFont(font_bold, 56)
        c.drawString(margem_h, 75 * mm, sigla)
        
        numero_str = f"#{i}"
        c.setFont(font_bold, 49)
        largura_texto_num = c.stringWidth(numero_str, font_bold, 49)
        c.drawString((150 * mm) - margem_h - largura_texto_num, 75 * mm, numero_str)
        
        c.setFont(font_bold, 46)
        c.drawString(margem_h, 55 * mm, "Overpack used")
        
        # Adicionada a informação "Data de expedição:" no final do texto do expedidor
        expedidor_text = (
            f"<b>EXPEDIDOR:</b> NEW POST LOGISTICA ENDEREÇO: R UBALDO FAGGEANI, 355,0 - "
            f"JARDIM RESIDENCIAL LAS PALMAS MUNICÍPIO: PORTO FERREIRA - SP CEP: 13660-000 "
            f"CNPJ/CPF: 28.678.104/0001-79 IE: 555074223110 UF: SP PAÍS: BRASIL "
            f"<b>Data de expedição:</b> {data_atual}"
        )
        
        recebedor_text = f"<b>RECEBEDOR:</b> {dados_recebedor['nome_recebedor']} CNPJ {dados_recebedor['cnpj_recebedor']} ENDEREÇO: {dados_recebedor['endereco_recebedor']}, {dados_recebedor['cidade_recebedor']} - {dados_recebedor['uf_recebedor']} CEP: {dados_recebedor['cep_recebedor']}"
        
        p_expedidor = Paragraph(expedidor_text, style_normal)
        p_expedidor.wrapOn(c, largura_maxima, 40 * mm)
        p_expedidor.drawOn(c, margem_h, 28 * mm)
        
        p_recebedor = Paragraph(recebedor_text, style_normal)
        p_recebedor.wrapOn(c, largura_maxima, 20 * mm)
        p_recebedor.drawOn(c, margem_h, 5 * mm)
        
        c.showPage()
        
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO (STREAMLIT) ---
st.title("✈️ Sistema de Etiquetas de Embarque")

df_destinos = carregar_dataframe()
df_destinos = df_destinos.dropna(subset=['sigla'])
df_destinos['sigla'] = df_destinos['sigla'].str.upper()
destinos_dict = df_destinos.set_index('sigla').to_dict('index')

aba_gerar, aba_admin = st.tabs(["📄 Gerar Etiquetas", "⚙️ Gerenciar Destinos"])

# --- ABA 1: GERAR ETIQUETAS ---
with aba_gerar:
    st.subheader("Emissão de Etiquetas")
    
    opcoes_destinos = list(destinos_dict.keys())
    
    if not opcoes_destinos:
        st.info("Nenhum destino cadastrado ainda. Vá até a aba 'Gerenciar Destinos' para adicionar.")
    else:
        with st.form("form_geracao"):
            sigla_selecionada = st.selectbox("Selecione o Destino (Aeroporto):", opcoes_destinos)
            quantidade_sacas = st.number_input("Quantidade de Sacas:", min_value=1, value=1, step=1)
            botao_preparar = st.form_submit_button("Preparar PDF")

        if botao_preparar:
            dados_recebedor = destinos_dict[sigla_selecionada]
            pdf_buffer = gerar_etiquetas_pdf(sigla_selecionada, quantidade_sacas, dados_recebedor)
            st.success(f"PDF pronto para o destino {sigla_selecionada} ({quantidade_sacas} etiqueta(s))!")
            
            st.download_button(
                label="📥 Baixar Arquivo PDF",
                data=pdf_buffer,
                file_name=f"etiquetas_{sigla_selecionada}.pdf",
                mime="application/pdf"
            )

# --- ABA 2: GERENCIAR DESTINOS (ADMIN) ---
with aba_admin:
    st.subheader("Painel Administrativo")
    
    with st.expander("➕ Adicionar Novo Destino"):
        with st.form("form_novo_destino", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nova_sigla = st.text_input("Sigla (Ex: CWB):").upper().strip()
                nome_recebedor = st.text_input("Nome do Recebedor:")
                cnpj_recebedor = st.text_input("CNPJ do Recebedor:")
                endereco_recebedor = st.text_input("Endereço Completo:")
            with col2:
                cidade_recebedor = st.text_input("Cidade:")
                uf_recebedor = st.text_input("UF (Ex: PR):").upper().strip()
                cep_recebedor = st.text_input("CEP:")
                pais_recebedor = st.text_input("País:", value="BRASIL")
            
            botao_salvar = st.form_submit_button("Salvar Destino")
            
            if botao_salvar:
                if not nova_sigla:
                    st.error("A sigla do destino é obrigatória!")
                elif nova_sigla in destinos_dict:
                    st.error(f"O destino {nova_sigla} já está cadastrado!")
                else:
                    novo_registro = pd.DataFrame([{
                        'sigla': nova_sigla, 'nome_recebedor': nome_recebedor, 'cnpj_recebedor': cnpj_recebedor,
                        'endereco_recebedor': endereco_recebedor, 'cidade_recebedor': cidade_recebedor,
                        'uf_recebedor': uf_recebedor, 'cep_recebedor': cep_recebedor, 'pais_recebedor': pais_recebedor
                    }])
                    df_atualizado = pd.concat([df_destinos, novo_registro], ignore_index=True)
                    salvar_dataframe(df_atualizado)
                    st.success(f"Destino {nova_sigla} cadastrado com sucesso!")
                    st.rerun()

    st.write("### Destinos Cadastrados")
    if df_destinos.empty:
        st.write("Nenhum destino na base de dados.")
    else:
        st.dataframe(df_destinos.set_index('sigla'), use_container_width=True)
        st.write("---")
        st.write("#### Remover Destino")
        sigla_para_remover = st.selectbox("Selecione qual deseja remover:", [""] + list(destinos_dict.keys()))
        
        if sigla_para_remover:
            confirmar_exclusao = st.button(f"❌ Confirmar Exclusão de {sigla_para_remover}")
            if confirmar_exclusao:
                df_restante = df_destinos[df_destinos.sigla != sigla_para_remover]
                salvar_dataframe(df_restante)
                st.success(f"Destino {sigla_para_remover} removido.")
                st.rerun()
