import os
import io
import pandas as pd
import streamlit as st
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(
    page_title="Gerador de Etiquetas - New Post",
    page_icon="✈️",
    layout="centered"
)

CSV_PATH = 'destinos.csv'

# --- CONFIGURAÇÕES DE FONTE ---
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
except Exception as e:
    pass

# --- FUNÇÕES DE MANIPULAÇÃO DE DADOS ---
def carregar_dataframe():
    if not os.path.exists(CSV_PATH):
        colunas = ['sigla', 'nome_recebedor', 'cnpj_recebedor', 'endereco_recebedor', 'cidade_recebedor', 'uf_recebedor', 'cep_recebedor', 'pais_recebedor']
        return pd.DataFrame(columns=colunas)
    
    df = pd.read_csv(CSV_PATH, sep=';')
    df.columns = df.columns.str.lower()
    
    colunas_obrigatorias = ['sigla', 'nome_recebedor', 'cnpj_recebedor', 'endereco_recebedor', 'cidade_recebedor', 'uf_recebedor', 'cep_recebedor', 'pais_recebedor']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = ""
    return df

def salvar_dataframe(df):
    df.to_csv(CSV_PATH, index=False, sep=';')

# --- GERAÇÃO DA ETIQUETA EM 150mm x 100mm ---
def gerar_etiquetas_pdf(sigla, quantidade, dados_recebedor):
    buffer = io.BytesIO()
    
    # Tamanho exato: 150mm x 100mm
    c = canvas.Canvas(buffer, pagesize=(150 * mm, 100 * mm))
    styles = getSampleStyleSheet()
    
    style_normal = ParagraphStyle(
        name='Normal', 
        parent=styles['Normal'], 
        fontName='Arial', 
        fontSize=11, 
        leading=13, 
        alignment=TA_LEFT
    )
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    for i in range(1, quantidade + 1):
        margem_h = 5 * mm
        largura_maxima = 140 * mm
        
        # Cabeçalho exato solicitado
        c.setFont('Arial-Bold', 56)
        c.drawString(margem_h, 75 * mm, sigla)
        
        numero_str = f"#{i}"
        c.setFont('Arial-Bold', 49)
        largura_texto_num = c.stringWidth(numero_str, 'Arial-Bold', 49)
        c.drawString((150 * mm) - margem_h - largura_texto_num, 75 * mm, numero_str)
        
        c.setFont('Arial-Bold', 46)
        c.drawString(margem_h, 55 * mm, "Overpack used")
        
        # Textos dos blocos
        expedidor_text = "<b>EXPEDIDOR:</b> NEW POST LOGISTICA ENDEREÇO: R UBALDO FAGGEANI, 355,0 - JARDIM RESIDENCIAL LAS PALMAS MUNICÍPIO: PORTO FERREIRA - SP CEP: 13660-000 CNPJ/CPF: 28.678.104/0001-79 IE: 555074223110 UF: SP PAÍS: BRASIL"
        recebedor_text = f"<b>RECEBEDOR:</b> {dados_recebedor['nome_recebedor']} CNPJ {dados_recebedor['cnpj_recebedor']} ENDEREÇO: {dados_recebedor['endereco_recebedor']}, {dados_recebedor['cidade_recebedor']} - {dados_recebedor['uf_recebedor']} CEP: {dados_recebedor['cep_recebedor']}"
        data_text = f"<b>DATA DE EXPEDIÇÃO:</b> {data_atual}"
        
        p_expedidor = Paragraph(expedidor_text, style_normal)
        p_recebedor = Paragraph(recebedor_text, style_normal)
        p_data = Paragraph(data_text, style_normal)
        
        # Coordenadas calibradas para evitar colisões e cortes:
        # EXPEDIDOR posicionado em 26mm de altura (deixando espaço livre para quebra de linhas)
        p_expedidor.wrapOn(c, largura_maxima, 20 * mm)
        p_expedidor.drawOn(c, margem_h, 26 * mm)
        
        # RECEBEDOR posicionado em 10mm de altura
        p_recebedor.wrapOn(c, largura_maxima, 15 * mm)
        p_recebedor.drawOn(c, margem_h, 10 * mm)
        
        # DATA DE EXPEDIÇÃO fixada no rodapé a 4mm da base
        p_data.wrapOn(c, largura_maxima, 5 * mm)
        p_data.drawOn(c, margem_h, 4 * mm)
        
        c.showPage()
        
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO (STREAMLIT) ---
st.title("✈️ Emissor de Etiquetas de Embarque")

df_destinos = carregar_dataframe()
df_destinos = df_destinos.dropna(subset=['sigla'])
df_destinos['sigla'] = df_destinos['sigla'].str.upper()
destinos_dict = df_destinos.set_index('sigla').to_dict('index')

aba_gerar, aba_admin = st.tabs(["📄 Gerar Etiquetas", "⚙️ Configurar Aeroportos/Destinos"])

with aba_gerar:
    st.write("Insira as informações abaixo para gerar o PDF:")
    opcoes_destinos = list(destinos_dict.keys())
    
    if not opcoes_destinos:
        st.info("Nenhum destino configurado. Acesse a aba ao lado para cadastrar.")
    else:
        with st.form("form_geracao"):
            sigla_selecionada = st.selectbox("Destino:", opcoes_destinos)
            quantidade_sacas = st.number_input("Quantidade de Sacas:", min_value=1, value=1, step=1)
            botao_preparar = st.form_submit_button("Gerar Etiquetas")

        if botao_preparar:
            dados_recebedor = destinos_dict[sigla_selecionada]
            
            # Correção do erro: variável passada corretamente aqui
            pdf_buffer = gerar_etiquetas_pdf(sigla_selecionada, quantidade_sacas, dados_recebedor)
            
            st.success(f"Etiquetas para {sigla_selecionada} geradas com sucesso!")
            st.download_button(
                label="📥 Baixar Etiquetas (PDF)",
                data=pdf_buffer,
                file_name=f"etiquetas_{sigla_selecionada}.pdf",
                mime="application/pdf"
            )

with aba_admin:
    st.subheader("Gerenciar Dados dos Recebedores")
    
    with st.expander("➕ Cadastrar Novo Aeroporto/Destino"):
        with st.form("form_novo_destino", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nova_sigla = st.text_input("Sigla (Ex: CWB):").upper().strip()
                nome_recebedor = st.text_input("Nome do Recebedor:")
                cnpj_recebedor = st.text_input("CNPJ:")
                endereco_recebedor = st.text_input("Endereço:")
            with col2:
                cidade_recebedor = st.text_input("Município/Cidade:")
                uf_recebedor = st.text_input("UF:").upper().strip()
                cep_recebedor = st.text_input("CEP:")
                pais_recebedor = st.text_input("País:", value="BRASIL")
            
            botao_salvar = st.form_submit_button("Salvar")
            
            if botao_salvar:
                if not nova_sigla:
                    st.error("A sigla é obrigatória!")
                elif nova_sigla in destinos_dict:
                    st.error(f"A sigla {nova_sigla} já existe!")
                else:
                    novo_registro = pd.DataFrame([{
                        'sigla': nova_sigla, 'nome_recebedor': nome_recebedor, 'cnpj_recebedor': cnpj_recebedor,
                        'endereco_recebedor': endereco_recebedor, 'cidade_recebedor': cidade_recebedor,
                        'uf_recebedor': uf_recebedor, 'cep_recebedor': cep_recebedor, 'pais_recebedor': pais_recebedor
                    }])
                    df_atualizado = pd.concat([df_destinos, novo_registro], ignore_index=True)
                    salvar_dataframe(df_atualizado)
                    st.success(f"Destino {nova_sigla} adicionado!")
                    st.rerun()

    st.write("### Destinos Salvos")
    if df_destinos.empty:
        st.write("Nenhum item encontrado.")
    else:
        st.dataframe(df_destinos.set_index('sigla'), use_container_width=True)
        st.write("---")
        sigla_para_remover = st.selectbox("Remover Destino:", [""] + list(destinos_dict.keys()))
        if sigla_para_remover:
            if st.button(f"Confirmar Exclusão de {sigla_para_remover}"):
                df_restante = df_destinos[df_destinos.sigla != sigla_para_remover]
                salvar_dataframe(df_restante)
                st.success(f"{sigla_para_remover} removido.")
                st.rerun()
