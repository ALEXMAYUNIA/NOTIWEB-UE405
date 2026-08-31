import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os, glob
import numpy as np
from datetime import datetime
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def mostrar_pagina():
    st.subheader("Módulo Tuberculosis - Análisis NOTIWEB")
    if hasattr(st, "segmented_control"):
        modo = st.segmented_control("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], default="📁 Carpeta automática", key="tb_modo")
    else:
        modo = st.pills("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], default="📁 Carpeta automática", key="tb_modo")

    lista_df = []
    archivos = []
    
    if "Subir" in modo:
        archivos_subidos = st.file_uploader("📂 Arrastra aquí tus archivos Excel de TUBERCULOSIS (puedes seleccionar 120 a la vez)", type=['xlsx','xls','csv'], accept_multiple_files=True, key="tb_upload")
        if not archivos_subidos:
            st.info("👆 Sube tus archivos Excel para empezar - Puedes arrastrar 120 archivos de golpe")
            return
        archivos = [f.name for f in archivos_subidos]
        prog = st.progress(0)
        for idx, f in enumerate(archivos_subidos):
            prog.progress((idx+1)/len(archivos_subidos))
            try:
                if f.name.lower().endswith('.csv'):
                    df_temp = pd.read_csv(f, dtype=str, encoding='utf-8', low_memory=False)
                else:
                    try:
                        df_temp = pd.read_excel(f, dtype=str, engine='openpyxl')
                    except:
                        df_temp = pd.read_excel(f, dtype=str)
                if df_temp is not None and not df_temp.empty:
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                    df_temp = df_temp.dropna(how='all')
                    lista_df.append(df_temp)
            except Exception as e:
                continue
        prog.empty()
    else:
        RUTA_BASE = os.path.dirname(__file__)
        ruta_carpeta = os.path.join(RUTA_BASE, "TUBERCULOSIS")
        if not os.path.exists(ruta_carpeta):
            ruta_carpeta = "TUBERCULOSIS"
        archivos = glob.glob(os.path.join(ruta_carpeta, "*.xlsx")) + glob.glob(os.path.join(ruta_carpeta, "*.xls")) + glob.glob(os.path.join(ruta_carpeta, "*.csv"))
        if not archivos:
            st.error(f"❌ No se encontraron archivos en {ruta_carpeta}. Usa el modo 'Subir archivos'")
            return
        prog = st.progress(0)
        for idx, f in enumerate(archivos):
            prog.progress((idx+1)/len(archivos))
            try:
                if f.lower().endswith('.csv'):
                    df_temp = pd.read_csv(f, dtype=str, encoding='utf-8', low_memory=False)
                else:
                    try:
                        df_temp = pd.read_excel(f, dtype=str, engine='openpyxl')
                    except:
                        df_temp = pd.read_excel(f, dtype=str)
                if df_temp is not None and not df_temp.empty:
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                    df_temp = df_temp.dropna(how='all')
                    lista_df.append(df_temp)
            except:
                continue
        prog.empty()

    if not lista_df:
        st.error("No se pudo leer ningun archivo")
        return
    df = pd.concat(lista_df, ignore_index=True, sort=False)
    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)}")
    df.columns = df.columns.astype(str).str.lower().str.strip()
    df = df.rename(columns={'ano_fis': 'AÑO', 'ano': 'AÑO', 'año': 'AÑO','anio': 'AÑO','red_not': 'PROVINCIA', 'dis_res': 'DISTRITO','establec_noti': 'ESTABLECIMIENTO','sexo': 'SEXO','localiza1': 'TIPO DE TUBERCULOSIS','vih': 'VIH','edad': 'EDAD','edad_anios': 'EDAD'})
    df['AÑO'] = pd.to_numeric(df.get('AÑO', 0), errors='coerce').fillna(0).astype(int).astype(str)
    df.loc[df['AÑO']=='0','AÑO']='S/D'
    df['SEXO'] = df['SEXO'].astype(str).str.strip()
    df['SEXO'] = df['SEXO'].map({'1': 'Masculino', '2': 'Femenino', 'M': 'Masculino', 'F': 'Femenino', '1.0': 'Masculino', '2.0': 'Femenino'}).fillna(df['SEXO'])
    df.loc[~df['SEXO'].isin(['Masculino','Femenino']), 'SEXO'] = 'Masculino'
    df['EDAD'] = pd.to_numeric(df.get('EDAD', 0), errors='coerce').fillna(0).astype(int)
    condiciones = [(df['EDAD']>=0)&(df['EDAD']<=11),(df['EDAD']>=12)&(df['EDAD']<=17),(df['EDAD']>=18)&(df['EDAD']<=29),(df['EDAD']>=30)&(df['EDAD']<=59),(df['EDAD']>=60)]
    categorias = ['NIÑO (0-11)','ADOLESCENTE (12-17)','JOVEN (18-29)','ADULTO (30-59)','ADULTO MAYOR (60+)']
    df['GRUPO_ETARIO'] = np.select(condiciones, categorias, default='SIN DATO')
    for col in ['PROVINCIA','DISTRITO','ESTABLECIMIENTO','TIPO DE TUBERCULOSIS','VIH']:
        if col not in df.columns: df[col]='SIN DATO'

    st.subheader("2. Filtros:")
    col1, col2, col3 = st.columns(3)
    with col1:
        anos_raw = [str(x) for x in df['AÑO'].astype(str).unique().tolist() if str(x).lower() not in ['nan','s/d','']]
        anos = ["TODOS"] + sorted(anos_raw, key=lambda x: int(x) if x.isdigit() else x, reverse=True)
        año_sel = st.selectbox("Filtrar por AÑO:", anos, key="tb_año")
    df_f = df if año_sel == "TODOS" else df[df['AÑO'].astype(str) == str(año_sel)]
    with col2:
        provs = ["TODAS"] + sorted([str(x) for x in df_f['PROVINCIA'].astype(str).unique().tolist() if str(x).lower()!='nan'])
        prov_sel = st.selectbox("Filtrar por PROVINCIA:", provs, key="tb_prov")
    if prov_sel != "TODAS":
        df_f = df_f[df_f['PROVINCIA'].astype(str) == str(prov_sel)]
    with col3:
        estabs = ["TODOS"] + sorted([str(x) for x in df_f['ESTABLECIMIENTO'].astype(str).unique().tolist() if str(x).lower()!='nan'])
        estab_sel = st.selectbox("Filtrar por ESTABLECIMIENTO:", estabs, key="tb_estab")
    if estab_sel != "TODOS":
        df_f = df_f[df_f['ESTABLECIMIENTO'].astype(str) == str(estab_sel)]

    st.subheader("TABLA 1 — Casos de TUBERCULOSIS Detallado")
    total = len(df_f)
    st.info(f"Total: {total} | Archivos: {len(lista_df)}/{len(archivos)}")
    columnas_mostrar = ['AÑO', 'PROVINCIA', 'DISTRITO', 'ESTABLECIMIENTO', 'SEXO', 'EDAD', 'GRUPO_ETARIO', 'TIPO DE TUBERCULOSIS', 'VIH']
    columnas_finales = [col for col in columnas_mostrar if col in df_f.columns]
    st.dataframe(df_f[columnas_finales], use_container_width=True, height=400)

    c1, c2 = st.columns(2)
    with c1:
        data_año = df['AÑO'].value_counts().sort_index().reset_index()
        data_año.columns = ['AÑO', 'Casos']
        data_año = data_año[data_año['AÑO']!='S/D']
        fig1 = px.bar(data_año, x='AÑO', y='Casos', title='Casos por AÑO', text='Casos', color_discrete_sequence=["#4472C4"])
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        data_sexo = df_f['SEXO'].value_counts().reset_index()
        data_sexo.columns = ['SEXO', 'Casos']
        fig2 = px.pie(data_sexo, names='SEXO', values='Casos', title='Distribución por SEXO (3D)', hole=0.3, color='SEXO', color_discrete_map={'Masculino': '#0EA5E9', 'Femenino': '#FF6FB5'})
        fig2.update_traces(textinfo='percent', textfont=dict(size=18, color='white'), pull=[0.05]*len(data_sexo))
        st.plotly_chart(fig2, use_container_width=True)

    if 'TIPO DE TUBERCULOSIS' in df_f.columns:
        data_tipo = df_f['TIPO DE TUBERCULOSIS'].value_counts().reset_index()
        data_tipo.columns = ['TIPO DE TUBERCULOSIS', 'Casos']
        fig3 = px.bar(data_tipo, x='TIPO DE TUBERCULOSIS', y='Casos', title='TIPO DE TUBERCULOSIS', text='Casos', color='TIPO DE TUBERCULOSIS', color_discrete_sequence=['#FF8C00', '#90EE90'])
        fig3.update_traces(textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("TABLA 2: Grupo Etario - NIÑO, ADOLESCENTE, JOVEN, ADULTO, ADULTO MAYOR")
    tabla_etario = df_f.groupby('GRUPO_ETARIO').size().reset_index(name='TOTAL')
    tabla_etario_det = df_f.groupby(['GRUPO_ETARIO','SEXO']).size().unstack(fill_value=0).reset_index()
    for col in ['Masculino','Femenino']:
        if col not in tabla_etario_det.columns:
            tabla_etario_det[col]=0
    tabla_etario_det['TOTAL'] = tabla_etario_det.get('Masculino',0) + tabla_etario_det.get('Femenino',0)
    tabla_etario = tabla_etario.sort_values('TOTAL', ascending=False)
    st.dataframe(tabla_etario_det, use_container_width=True, hide_index=True)
    colores_etario = {'NIÑO (0-11)': '#8BC34A', 'ADOLESCENTE (12-17)': '#00BCD4', 'JOVEN (18-29)': '#FF9800','ADULTO (30-59)': '#FFEB3B', 'ADULTO MAYOR (60+)': '#E91E63', 'SIN DATO': '#9E9E9E'}
    fig4 = px.bar(tabla_etario, x='GRUPO_ETARIO', y='TOTAL', title='Casos por Grupo Etario (Barras)', color='GRUPO_ETARIO', color_discrete_map=colores_etario, text='TOTAL')
    fig4.update_traces(textposition='outside')
    fig4.update_layout(template='plotly_white', showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

    def to_excel_pro():
        df_exp = df_f[columnas_finales].replace([np.inf, -np.inf], np.nan).fillna('')
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            wb=writer.book
            hdr=wb.add_format({'bold':True,'bg_color':'#1c2e4a','font_color':'white','border':1,'align':'center'})
            cell=wb.add_format({'border':1,'align':'center'})
            title=wb.add_format({'bold':True,'font_size':12,'bg_color':'#D9E1F2','border':1})
            s1='TABLA_1_DETALLE'; df_exp.to_excel(writer, sheet_name=s1, index=False, startrow=1)
            ws=writer.sheets[s1]; ws.write(0,0,f"TUBERCULOSIS - {año_sel}/{prov_sel}/{estab_sel} - {total} casos - {len(lista_df)} archivos",title)
            for c,v in enumerate(df_exp.columns): ws.write(1,c,v,hdr)
            for r in range(len(df_exp)):
                for c in range(len(df_exp.columns)): ws.write(r+2,c,str(df_exp.iloc[r,c]),cell)
            ws.set_column('A:I',16)
            s2='GRUPO_ETARIO'; tabla_etario_det.to_excel(writer, sheet_name=s2, index=False, startrow=1)
            ws2=writer.sheets[s2]; ws2.write(0,0,"Grupo Etario",title)
            for c,v in enumerate(tabla_etario_det.columns): ws2.write(1,c,v,hdr)
            for r in range(len(tabla_etario_det)):
                for c in range(len(tabla_etario_det.columns)): ws2.write(r+2,c,tabla_etario_det.iloc[r,c],cell)
            s3='POR_AÑO'; data_año.to_excel(writer, sheet_name=s3, index=False, startrow=1)
            ws3=writer.sheets[s3]
            for c,v in enumerate(data_año.columns): ws3.write(1,c,v,hdr)
            for r in range(len(data_año)):
                for c in range(len(data_año.columns)): ws3.write(r+2,c,data_año.iloc[r,c],cell)
        return output.getvalue()

    def to_pdf_3d():
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles=getSampleStyleSheet()
        stt=ParagraphStyle('T', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#1c2e4a'), alignment=1, spaceAfter=8)
        sh2=ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1c2e4a'), spaceAfter=4, spaceBefore=10)
        s_desc=ParagraphStyle('Desc', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor('#334155'), leftIndent=6, borderPadding=6, backColor=colors.HexColor('#f8fafc'), spaceAfter=6)
        story=[]
        story.append(Paragraph(f"<b>ANALISIS NOTIWEB 2026 - TUBERCULOSIS UE 405</b><br/>Filtros: {año_sel}/{prov_sel}/{estab_sel} - Total: {total} casos - {len(lista_df)} archivos de {len(archivos)} - {datetime.now().strftime('%d/%m/%Y')}", stt))
        story.append(Spacer(1,8))
        grupo_top = tabla_etario.iloc[0]['GRUPO_ETARIO'] if not tabla_etario.empty else "S/D"
        grupo_top_n = tabla_etario.iloc[0]['TOTAL'] if not tabla_etario.empty else 0
        story.append(Paragraph(f"Se registraron <b>{total} casos</b> de {len(lista_df)} archivos. Grupo mas afectado: <b>{grupo_top} {grupo_top_n} casos</b>.", s_desc))
        data=[['AÑO','PROV','DISTRITO','EESS','SEXO','EDAD','GRUPO','TIPO TB']]
        for _,r in df_f.head(20).iterrows():
            data.append([str(r.get('AÑO','')),str(r.get('PROVINCIA',''))[:8],str(r.get('DISTRITO',''))[:8],str(r.get('ESTABLECIMIENTO',''))[:10],str(r.get('SEXO',''))[:1],str(r.get('EDAD','')),str(r.get('GRUPO_ETARIO',''))[:8],str(r.get('TIPO DE TUBERCULOSIS',''))[:10]])
        t=Table(data, colWidths=[25,35,35,50,20,20,35,50])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),6)]))
        story.append(t)
        doc.build(story)
        return buffer.getvalue()

    c1,c2,c3=st.columns(3)
    with c1:
        st.download_button("📊 EXCEL PRO", data=to_excel_pro(), file_name=f"TUBERCULOSIS_PRO_{año_sel}_{prov_sel}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    with c2:
        st.download_button("📄 PDF 3D", data=to_pdf_3d(), file_name=f"TUBERCULOSIS_3D_{año_sel}.pdf", mime="application/pdf", use_container_width=True)
    with c3:
        st.download_button("📑 PDF COMPLETO", data=to_pdf_3d(), file_name=f"TUBERCULOSIS_COMPLETO_{len(archivos)}archivos.pdf", mime="application/pdf", use_container_width=True)