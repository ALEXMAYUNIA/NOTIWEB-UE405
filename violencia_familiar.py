import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import os, glob, numpy as np
from datetime import datetime
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def mostrar_pagina():
    st.subheader("Módulo Violencia Familiar - Análisis NOTIWEB")
    try:
        modo = st.segmented_control("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], default="📁 Carpeta automática", key="vf_modo")
    except AttributeError:
        modo = st.pills("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], default="📁 Carpeta automática", key="vf_modo")
    except Exception:
        modo = st.pills("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], default="📁 Carpeta automática", key="vf_modo")
    if not modo:
        modo = "📁 Carpeta automática"

    lista_df = []
    archivos = []
    
    if "Subir" in modo:
        archivos_subidos = st.file_uploader("📂 Arrastra aquí tus archivos Excel de VIOLENCIA FAMILIAR (120 a la vez)", type=['xlsx','xls','csv'], accept_multiple_files=True, key="vf_upload")
        if not archivos_subidos:
            st.info("👆 Sube tus archivos Excel para empezar")
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
                    lista_df.append(df_temp)
            except: continue
        prog.empty()
    else:
        RUTA_BASE = os.path.dirname(__file__)
        ruta_carpeta = os.path.join(RUTA_BASE, "VIOLENCIA FAMILIAR")
        if not os.path.exists(ruta_carpeta):
            ruta_carpeta = "VIOLENCIA FAMILIAR"
        archivos = glob.glob(os.path.join(ruta_carpeta, "*.xlsx")) + glob.glob(os.path.join(ruta_carpeta, "*.xls")) + glob.glob(os.path.join(ruta_carpeta, "*.csv"))
        if not archivos:
            st.error(f"❌ No se encontraron archivos en {ruta_carpeta}. Usa modo Subir archivos")
            return
        prog = st.progress(0)
        for idx, f in enumerate(archivos):
            prog.progress((idx+1)/len(archivos))
            try:
                if f.lower().endswith('.csv'):
                    df_temp = pd.read_csv(f, dtype=str, encoding='utf-8', low_memory=False)
                else:
                    df_temp = pd.read_excel(f, dtype=str, engine='openpyxl')
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                lista_df.append(df_temp)
            except: continue
        prog.empty()

    df = pd.concat(lista_df, ignore_index=True, sort=False)
    df.columns = df.columns.astype(str).str.lower().str.strip()
    df = df.rename(columns={'ano': 'AÑO','provinci': 'PROVINCIA','distrito': 'DISTRITO','estab_s': 'ESTABLECIMIENTO','sexo': 'SEXO','edad': 'EDAD','defuncion': 'MUERTES'})
    def obtener_tipo_violencia(row):
        if row.get('fisica') == 'S': return 'Psicológica'
        if row.get('psicol') == 'S': return 'Física'
        if row.get('relsex') == 'S': return 'Sexual'
        if row.get('aband') == 'S': return 'Abandono'
        if row.get('propiocuer') == 'S': return 'Propio Cuerpo'
        if row.get('armafuego') == 'S': return 'Arma de Fuego'
        if row.get('armablan') == 'S': return 'Arma Blanca'
        if row.get('objcontun') == 'S': return 'Objeto Contundente'
        if row.get('otros01') == 'S': return 'Otros'
        return 'No Especificado'
    df['TIPO DE VIOLENCIA'] = df.apply(obtener_tipo_violencia, axis=1)
    def obtener_tipo_buaso(row):
        if row.get('familiar') == 'S': return 'Familiar'
        if row.get('celos') == 'S': return 'Celos'
        if row.get('economicos') == 'S': return 'Económicos'
        if row.get('laborales') == 'S': return 'Laborales'
        if row.get('sinmotivo') == 'S': return 'Sin Motivo'
        return 'No Especificado'
    df['TIPO DE BUASO'] = df.apply(obtener_tipo_buaso, axis=1)
    df['SEXO'] = df['SEXO'].astype(str).str.upper()
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce').astype('Int64')
    df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce').astype('Int64')
    df['MUERTES'] = df['MUERTES'].map({'S': 'Sí', 'N': 'No', 's': 'Sí', 'n': 'No'})
    def obtener_grupo_etario(edad):
        if pd.isna(edad): return 'SIN DATO'
        if edad <= 11: return '0-11 NIÑO/A'
        elif edad <= 17: return '12-17 ADOLESCENTE'
        elif edad <= 29: return '18-29 JOVEN'
        elif edad <= 59: return '30-59 ADULTO/A'
        else: return '60+ ADULTO MAYOR'
    df['GRUPO ETARIO'] = df['EDAD'].apply(obtener_grupo_etario)
    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)}")
    st.subheader("2. Filtros:")
    col1, col2, col3 = st.columns(3)
    with col1:
        años = ["TODOS"] + sorted(df['AÑO'].dropna().unique().tolist(), reverse=True)
        año_sel = st.selectbox("Filtrar por AÑO:", años, key="vf_año")
    df_f = df if año_sel == "TODOS" else df[df['AÑO'] == año_sel]
    with col2:
        provs = ["TODAS"] + sorted(df_f['PROVINCIA'].dropna().unique().tolist())
        prov_sel = st.selectbox("Filtrar por PROVINCIA:", provs, key="vf_prov")
    if prov_sel != "TODAS": df_f = df_f[df_f['PROVINCIA'] == prov_sel]
    with col3:
        dists = ["TODOS"] + sorted(df_f['DISTRITO'].dropna().unique().tolist())
        dist_sel = st.selectbox("Filtrar por DISTRITO:", dists, key="vf_dist")
    if dist_sel != "TODOS": df_f = df_f[df_f['DISTRITO'] == dist_sel]
    st.subheader("TABLA 1 — Casos de VIOLENCIA FAMILIAR Detallado")
    total = len(df_f); fallecidos = len(df_f[df_f['MUERTES'] == 'Sí']) if 'MUERTES' in df_f.columns else 0
    st.warning(f"⚠ Total de casos: {total} | Fallecidos registrados: {fallecidos}")
    columnas_mostrar = ['AÑO', 'PROVINCIA', 'DISTRITO', 'ESTABLECIMIENTO', 'SEXO', 'EDAD', 'TIPO DE VIOLENCIA', 'TIPO DE BUASO', 'MUERTES']
    columnas_finales = [col for col in columnas_mostrar if col in df_f.columns]
    def resaltar_fallecidos(row):
        if 'MUERTES' in row and row['MUERTES'] == 'Sí': return ['background-color: #FFCCCB'] * len(row)
        return [''] * len(row)
    if 'MUERTES' in df_f.columns:
        st.dataframe(df_f[columnas_finales].style.apply(resaltar_fallecidos, axis=1), use_container_width=True, height=400)
    else:
        st.dataframe(df_f[columnas_finales], use_container_width=True, height=400)
    st.subheader("TABLA 2 — Casos por GRUPO ETARIO")
    orden_grupos = ['0-11 NIÑO/A', '12-17 ADOLESCENTE', '18-29 JOVEN', '30-59 ADULTO/A', '60+ ADULTO MAYOR']
    tabla_grupo = pd.crosstab(df_f['GRUPO ETARIO'], df_f['SEXO'], margins=True, margins_name='TOTAL').reindex(orden_grupos + ['TOTAL'], fill_value=0)
    tabla_grupo = tabla_grupo.rename(columns={'FEMENINO': 'MUJER', 'MASCULINO': 'VARÓN'})
    st.dataframe(tabla_grupo, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        data_año = df['AÑO'].value_counts().sort_index().reset_index()
        data_año.columns = ['AÑO', 'Casos']
        fig1 = px.bar(data_año, x='AÑO', y='Casos', title='Casos por AÑO', text='Casos', color_discrete_sequence=["#4472C4"])
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        if 'TIPO DE VIOLENCIA' in df_f.columns:
            data_tipo = df_f['TIPO DE VIOLENCIA'].value_counts().reset_index()
            data_tipo.columns = ['TIPO DE VIOLENCIA', 'Casos']
            fig2 = px.bar(data_tipo, x='TIPO DE VIOLENCIA', y='Casos', title='TIPO DE VIOLENCIA', text='Casos', color='TIPO DE VIOLENCIA', color_discrete_map={'Psicológica': '#1F77B4','Física': '#7BC043','Sexual': '#FF0000','Abandono': '#FFFF00','Propio Cuerpo': '#FF8C00'})
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)
    st.subheader("GRÁFICA — Casos por GRUPO ETARIO y SEXO")
    data_grupo_sexo = df_f.groupby(['GRUPO ETARIO', 'SEXO']).size().reset_index(name='Casos')
    data_grupo_sexo['GRUPO ETARIO'] = pd.Categorical(data_grupo_sexo['GRUPO ETARIO'], categories=orden_grupos, ordered=True)
    data_grupo_sexo = data_grupo_sexo.sort_values('GRUPO ETARIO')
    titulo_dinamico = f"VIOLENCIA FAMILIAR {prov_sel if prov_sel != 'TODAS' else ''} {año_sel if año_sel != 'TODOS' else '(2021-2026)'}"
    fig3 = px.bar(data_grupo_sexo, x='SEXO', y='Casos', color='GRUPO ETARIO', title=titulo_dinamico, barmode='group', text='Casos', color_discrete_map={'0-11 NIÑO/A': '#87CEEB','12-17 ADOLESCENTE': '#90EE90','18-29 JOVEN': '#FF0000','30-59 ADULTO/A': '#FFFF00','60+ ADULTO MAYOR': '#9370DB'})
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)
    st.subheader("GRÁFICA — Casos por GRUPO ETARIO")
    fig4 = px.bar(data_grupo_sexo, x='GRUPO ETARIO', y='Casos', color='SEXO', title=titulo_dinamico, barmode='group', text='Casos', color_discrete_map={'FEMENINO': '#FF0000', 'MASCULINO': '#00BFFF'})
    fig4.update_xaxes(tickangle=0)
    fig4.update_traces(textposition='outside')
    st.plotly_chart(fig4, use_container_width=True)
    st.subheader("GRÁFICA — Distribución TIPO DE VIOLENCIA")
    if 'TIPO DE VIOLENCIA' in df_f.columns:
        data_torta = df_f['TIPO DE VIOLENCIA'].value_counts().reset_index()
        data_torta.columns = ['TIPO DE VIOLENCIA', 'Casos']
        fig5 = px.pie(data_torta, names='TIPO DE VIOLENCIA', values='Casos', title=f'{prov_sel if prov_sel != "TODAS" else "HUACAYBAMBA"} {año_sel if año_sel != "TODOS" else "(2021-2026)"}', color='TIPO DE VIOLENCIA', color_discrete_map={'Psicológica': '#1F77B4','Física': '#7BC043','Sexual': '#FF0000','Abandono': '#FFFF00','Propio Cuerpo': '#FF8C00','Arma de Fuego': '#8B0000','Arma Blanca': '#DC143C','Objeto Contundente': '#A0522D','Otros': '#808080'})
        fig5.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14, textfont_color='white', pull=[0.05 if x == 'Psicológica' else 0 for x in data_torta['TIPO DE VIOLENCIA']])
        fig5.update_layout(showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05))
        st.plotly_chart(fig5, use_container_width=True)

    def to_excel_pro():
        out=BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            wb=writer.book; hdr=wb.add_format({'bold':True,'bg_color':'#1c2e4a','font_color':'white','border':1,'align':'center'}); cell=wb.add_format({'border':1,'align':'center'}); title=wb.add_format({'bold':True,'bg_color':'#D9E1F2','border':1})
            s1='DATOS'; df_f[columnas_finales].to_excel(writer, sheet_name=s1, index=False, startrow=1); ws=writer.sheets[s1]
            for c,v in enumerate(columnas_finales): ws.write(1,c,v,hdr)
            for r in range(len(df_f)):
                for c in range(len(columnas_finales)): ws.write(r+2,c,str(df_f.iloc[r][columnas_finales[c]]),cell)
            s2='GRUPO_ETARIO'; tabla_grupo.to_excel(writer, sheet_name=s2, startrow=1); ws2=writer.sheets[s2]; ws2.write(0,0,"Grupo Etario",title)
        return out.getvalue()

    def to_pdf_completo():
        buffer=BytesIO(); doc=SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles=getSampleStyleSheet(); stt=ParagraphStyle('T', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#1c2e4a'), alignment=1)
        story=[Paragraph(f"<b>VIOLENCIA FAMILIAR UE 405 - {año_sel}/{prov_sel}/{dist_sel} - Total {total} - {len(lista_df)} archivos - {datetime.now().strftime('%d/%m/%Y')}</b>", stt), Spacer(1,8)]
        data=[['AÑO','PROV','DISTRITO','SEXO','EDAD','TIPO VIOL','MUERTE']]+[[str(r.get('AÑO','')),str(r.get('PROVINCIA',''))[:8],str(r.get('DISTRITO',''))[:8],str(r.get('SEXO','')),str(r.get('EDAD','')),str(r.get('TIPO DE VIOLENCIA',''))[:10],str(r.get('MUERTES',''))] for _,r in df_f.head(20).iterrows()]
        t=Table(data, colWidths=[25,35,35,25,20,50,25]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),6)])); story.append(t)
        doc.build(story); return buffer.getvalue()

    c1,c2,c3=st.columns(3)
    with c1: st.download_button("📊 EXCEL PRO", data=to_excel_pro(), file_name=f"VIOLENCIA_FAMILIAR_PRO_{año_sel}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    with c2: st.download_button("📄 PDF CON GRAFICOS", data=to_pdf_completo(), file_name=f"VIOLENCIA_FAMILIAR_3D_{año_sel}.pdf", mime="application/pdf", use_container_width=True)
    with c3: st.download_button("📑 PDF COMPLETO", data=to_pdf_completo(), file_name=f"VIOLENCIA_FAMILIAR_COMPLETO_{len(archivos)}archivos.pdf", mime="application/pdf", use_container_width=True)