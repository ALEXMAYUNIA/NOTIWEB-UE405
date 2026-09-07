import streamlit as st
import pandas as pd
import os
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from io import BytesIO
import xlsxwriter
from datetime import datetime
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

def mostrar_pagina():
    st.subheader("Módulo PLAGUICIDAS - Análisis")
    try:
        modo = st.segmented_control("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], key="plag_modo", default="📁 Carpeta automática")
    except AttributeError:
        modo = st.pills("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], key="plag_modo", default="📁 Carpeta automática")
    if modo is None:
        modo = "📁 Carpeta automática"

    RUTA_BASE = os.path.dirname(__file__)
    ruta_carpeta = os.path.join(RUTA_BASE, 'PLAGUICIDAS')

    lista_df = []
    archivos_fallidos = []
    archivos = []

    if "Subir" in modo:
        uploaded_files = st.file_uploader("Sube archivos Excel/CSV de PLAGUICIDAS (puede ser diferente formato - se adapta)", type=['xlsx','xls','csv'], accept_multiple_files=True, key="plag_uploader")
        if not uploaded_files:
            st.info("👆 Sube uno o más archivos para procesar")
            return
        archivos = [f.name for f in uploaded_files]
        progress = st.progress(0)
        for idx, archivo_obj in enumerate(uploaded_files):
            progress.progress((idx+1)/len(uploaded_files))
            df_temp = None
            nombre = archivo_obj.name
            try:
                if nombre.lower().endswith('.csv'):
                    archivo_obj.seek(0)
                    df_temp = pd.read_csv(archivo_obj, encoding='utf-8', low_memory=False)
                else:
                    archivo_obj.seek(0)
                    try:
                        df_temp = pd.read_excel(archivo_obj, engine='openpyxl', header=0)
                    except:
                        try:
                            archivo_obj.seek(0)
                            df_temp = pd.read_excel(archivo_obj, engine='xlrd', header=0)
                        except:
                            archivo_obj.seek(0)
                            df_temp = pd.read_excel(archivo_obj, header=0)
            except:
                archivos_fallidos.append(nombre)
                continue

            if df_temp is not None and not df_temp.empty:
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                df_temp = df_temp.dropna(how='all')
                df_temp = df_temp.dropna(axis=1, how='all')
                lista_df.append(df_temp)
            else:
                archivos_fallidos.append(nombre)
        progress.empty()
    else:
        # MODO CARPETA AUTOMATICA
        if not os.path.exists(ruta_carpeta):
            st.error(f"No existe la carpeta: {ruta_carpeta}")
            st.warning("Usa modo Subir archivos")
            return

        archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
        
        if not archivos:
            st.warning("La carpeta PLAGUICIDAS esta vacia")
            st.warning("Usa modo Subir archivos")
            return

        progress = st.progress(0)
        
        for idx, archivo in enumerate(archivos):
            progress.progress((idx+1)/len(archivos))
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            df_temp = None
            try:
                if archivo.lower().endswith('.csv'):
                    df_temp = pd.read_csv(ruta_archivo, encoding='utf-8', low_memory=False)
                else:
                    try:
                        df_temp = pd.read_excel(ruta_archivo, engine='openpyxl', header=0)
                    except:
                        try:
                            df_temp = pd.read_excel(ruta_archivo, engine='xlrd', header=0)
                        except:
                            df_temp = pd.read_excel(ruta_archivo, header=0)
            except:
                archivos_fallidos.append(archivo)
                continue

            if df_temp is not None and not df_temp.empty:
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                df_temp = df_temp.dropna(how='all')
                df_temp = df_temp.dropna(axis=1, how='all')
                lista_df.append(df_temp)
            else:
                archivos_fallidos.append(archivo)

        progress.empty()

    if not lista_df:
        st.error("No se pudo leer ningun archivo valido")
        return

    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)}")
    if archivos_fallidos:
        with st.expander(f"{len(archivos_fallidos)} archivos no leidos"):
            st.write(archivos_fallidos)

    df = pd.concat(lista_df, ignore_index=True, sort=False)
    df.columns = df.columns.astype(str).str.lower().str.strip()

    def col(*nombres):
        for nombre in nombres:
            if nombre in df.columns:
                return df[nombre]
        return pd.Series([None] * len(df))

    df['ANIO'] = pd.to_numeric(col('año', 'anio', 'ano', 'year'), errors='coerce')
    df['ANIO'] = df['ANIO'].fillna(0).astype(int).astype(str)
    df.loc[df['ANIO'] == '0', 'ANIO'] = 'S/D'

    df['DEPARTAMEN'] = col('disa', 'departamen').astype(str).str.strip()
    df['DEPARTAMEN'] = df['DEPARTAMEN'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    df['PROVINCIA'] = col('red', 'provincia').astype(str).str.strip()
    df['PROVINCIA'] = df['PROVINCIA'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    df['DISTRITO'] = col('microredes', 'microred', 'distrito').astype(str).str.strip()
    df['DISTRITO'] = df['DISTRITO'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    df['MICROREDES'] = df['DISTRITO']
    df['ESTABLECIMINETO'] = col('raz_soc', 'eess', 'establecimiento').astype(str).str.strip()
    df['ESTABLECIMINETO'] = df['ESTABLECIMINETO'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    
    sexo = col('sexo', '').astype(str).str.upper().str.strip()
    df['SEXO'] = 'INDETERMINADO'
    df.loc[sexo == 'M', 'SEXO'] = 'MASCULINO'
    df.loc[sexo == 'F', 'SEXO'] = 'FEMENINO'

    df['EDAD'] = pd.to_numeric(col('edad', 0), errors='coerce').fillna(0).astype(int)
    # GRUPO ETARIO
    condiciones = [(df['EDAD']>=0)&(df['EDAD']<=11),(df['EDAD']>=12)&(df['EDAD']<=17),(df['EDAD']>=18)&(df['EDAD']<=29),(df['EDAD']>=30)&(df['EDAD']<=59),(df['EDAD']>=60)]
    categorias = ['NIÑO (0-11)','ADOLESCENTE (12-17)','JOVEN (18-29)','ADULTO (30-59)','ADULTO MAYOR (60+)']
    df['GRUPO_ETARIO'] = np.select(condiciones, categorias, default='SIN DATO')
    
    df['FECHA_NOTIF'] = pd.to_datetime(col('fecha_not', 'fecha_notif'), errors='coerce').dt.strftime('%d/%m/%Y')
    df['FECHA_NOTIF'] = df['FECHA_NOTIF'].fillna('S/D')
    df['CAUSA'] = col('causa_bas', 'causa').astype(str).str.strip().replace(['', 'nan', 'None', '0'], '')
    df['FALLECIDA'] = col('otro9', '').astype(str).str.upper().str.strip().replace(['', 'nan', 'None', '0'], 'NO')
    df.loc[df['FALLECIDA']!= 'FALLECIDA', 'FALLECIDA'] = 'NO'

    tipo = pd.to_numeric(col('tipo_intox', 0), errors='coerce').fillna(0).astype(int)
    df['TIPO_INTOX'] = tipo
    condiciones_gravedad = [(tipo == 1), (tipo == 2), (tipo == 3), (tipo == 4)]
    categorias_gravedad = ['EXTREMADAMENTE Y MUY PELIGROSOS (BANDA ROJA)','MODERADAMENTE PELIGROSOS (BANDA AMARILLA)','LIGERAMENTE PELIGROSOS (BANDA AZUL)','NORMALMENTE NO OFRECEN PELIGRO (BANDA VERDE)']
    df['DESC_GRAVEDAD'] = np.select(condiciones_gravedad, categorias_gravedad, default='')

    st.subheader("2. Filtros:")
    col1, col2, col3 = st.columns(3)
    with col1:
        anos_raw = [str(x) for x in df['ANIO'].astype(str).unique().tolist() if str(x).lower() not in ['nan','s/d','']]
        anos_disponibles = ['TODOS'] + sorted(anos_raw, key=lambda x: int(x) if x.isdigit() else x)
        ano_filtro = st.selectbox("Filtrar por AÑO:", anos_disponibles, key='pla_ano')
    with col2:
        prov_raw = [str(x).strip() for x in df['PROVINCIA'].astype(str).unique().tolist() if str(x).lower() not in ['nan','sin dato','']]
        prov_disponibles = ['TODAS'] + sorted(prov_raw)
        prov_filtro = st.selectbox("Filtrar por PROVINCIA:", prov_disponibles, key='pla_prov')
    with col3:
        if prov_filtro!= 'TODAS':
            distritos_filtrados = df[df['PROVINCIA'].astype(str) == prov_filtro]['DISTRITO'].astype(str).unique().tolist()
        else:
            distritos_filtrados = df['DISTRITO'].astype(str).unique().tolist()
        dis_raw = [str(x).strip() for x in distritos_filtrados if str(x).lower() not in ['nan','sin dato','']]
        dis_disponibles = ['TODOS'] + sorted(dis_raw)
        dis_filtro = st.selectbox("Filtrar por DISTRITO:", dis_disponibles, key='pla_dis')

    df_filtrado = df.copy()
    if ano_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['ANIO'].astype(str) == str(ano_filtro)]
    if prov_filtro!= 'TODAS': df_filtrado = df_filtrado[df_filtrado['PROVINCIA'].astype(str) == str(prov_filtro)]
    if dis_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['DISTRITO'].astype(str) == str(dis_filtro)]

    st.subheader("TABLA 1: Casos de INTOXICACION POR PLAGUICIDAS")
    columnas_tabla1 = ['ANIO', 'DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'MICROREDES', 'ESTABLECIMINETO','SEXO', 'EDAD', 'GRUPO_ETARIO', 'FECHA_NOTIF', 'CAUSA', 'FALLECIDA', 'TIPO_INTOX', 'DESC_GRAVEDAD']
    for c in columnas_tabla1:
        if c not in df_filtrado.columns:
            df_filtrado[c]='S/D'
    tabla1 = df_filtrado[columnas_tabla1].copy()
    tabla1['TOTAL'] = 1
    total_general = len(tabla1)
    total_fallecidos = (df_filtrado['FALLECIDA'] == 'FALLECIDA').sum()
    st.info(f"Total de casos: {total_general} | **Fallecidos registrados: {total_fallecidos}**")
    if total_general == 0:
        st.warning("No se registraron casos")
        return
    fila_total = {col: '' for col in columnas_tabla1}
    fila_total['ANIO'] = 'TOTAL GENERAL'
    fila_total['FALLECIDA'] = f'{total_fallecidos} FALLECIDOS' if total_fallecidos > 0 else ''
    fila_total['TOTAL'] = total_general
    tabla1_final = pd.concat([tabla1, pd.DataFrame([fila_total])], ignore_index=True)
    def colorear_tabla(row):
        if row['ANIO'] == 'TOTAL GENERAL':
            return ['background-color: #FFD700; font-weight: bold; border: 2px solid black'] * len(row)
        elif row['FALLECIDA'] == 'FALLECIDA':
            return ['background-color: #FFCCCB; font-weight: bold; border: 1px solid red'] * len(row)
        else:
            return ['border: 1px solid #ddd'] * len(row)
    st.dataframe(tabla1_final.style.apply(colorear_tabla, axis=1), use_container_width=True, hide_index=True)

    tabla_graf = df_filtrado.groupby('ANIO').size().reset_index(name='TOTAL')
    tabla_graf = tabla_graf[tabla_graf['ANIO']!= 'S/D']
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=tabla_graf['ANIO'], y=tabla_graf['TOTAL'], marker_color='#32CD32', text=tabla_graf['TOTAL'], textposition='outside'))
    fig1.update_layout(title=f'PLAGUICIDAS por AÑO - {total_general} casos', plot_bgcolor='#F5F5F5', paper_bgcolor='white', template='plotly_white')
    st.plotly_chart(fig1, use_container_width=True)

    tabla_gravedad = df_filtrado.groupby('DESC_GRAVEDAD').size().reset_index(name='TOTAL')
    tabla_gravedad = tabla_gravedad[tabla_gravedad['DESC_GRAVEDAD']!= '']
    colores_banda = {'EXTREMADAMENTE Y MUY PELIGROSOS (BANDA ROJA)': '#FF0000','MODERADAMENTE PELIGROSOS (BANDA AMARILLA)': '#FFD700','LIGERAMENTE PELIGROSOS (BANDA AZUL)': '#0000FF','NORMALMENTE NO OFRECEN PELIGRO (BANDA VERDE)': '#00FF00'}
    fig2 = go.Figure(data=[go.Pie(labels=tabla_gravedad['DESC_GRAVEDAD'], values=tabla_gravedad['TOTAL'], hole=0.3, pull=[0.05]*len(tabla_gravedad),
                                  marker=dict(colors=[colores_banda.get(x,'#888') for x in tabla_gravedad['DESC_GRAVEDAD']], line=dict(color='#000', width=1)),
                                  textinfo='percent', 
                                  textposition='inside',
                                  textfont=dict(size=16, color='white', family='Arial Black'),
                                  insidetextorientation='horizontal')])
    fig2.update_layout(title='Distribucion por Banda Toxicologica', template='plotly_white')
    st.plotly_chart(fig2, use_container_width=True)

    # TABLA 2 GRUPO ETARIO
    st.subheader("TABLA 2: GRUPO ETARIO")
    tabla_etario = df_filtrado.groupby('GRUPO_ETARIO').size().reset_index(name='TOTAL')
    tabla_etario = tabla_etario.sort_values('TOTAL', ascending=False)
    # Calcula sexo dentro
    tabla_etario_det = df_filtrado.groupby(['GRUPO_ETARIO','SEXO']).size().unstack(fill_value=0).reset_index()
    for col in ['MASCULINO','FEMENINO','INDETERMINADO']:
        if col not in tabla_etario_det.columns:
            tabla_etario_det[col]=0
    tabla_etario_det['TOTAL']=tabla_etario_det.get('MASCULINO',0)+tabla_etario_det.get('FEMENINO',0)+tabla_etario_det.get('INDETERMINADO',0)
    st.dataframe(tabla_etario_det, use_container_width=True, hide_index=True)

    colores_etario = {'NIÑO (0-11)': '#8BC34A', 'ADOLESCENTE (12-17)': '#00BCD4', 'JOVEN (18-29)': '#FF9800','ADULTO (30-59)': '#FFEB3B', 'ADULTO MAYOR (60+)': '#E91E63', 'SIN DATO': '#F44336'}
    fig3 = px.bar(tabla_etario, x='GRUPO_ETARIO', y='TOTAL', title='Casos por Grupo Etario', color='GRUPO_ETARIO', color_discrete_map=colores_etario, text='TOTAL')
    fig3.update_traces(textposition='outside')
    fig3.update_layout(template='plotly_white', showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # DESCARGAS
# ============================================================
    # DESCARGAS — PLAGUICIDAS
    # Se conserva TODO lo que aparece en el sistema:
    #   TABLA 1 + TABLA 2 + 3 GRÁFICOS.
    # Se mantienen las hojas correspondientes del módulo.
    # NO se modifica lectura, filtros ni cálculos.
    # NO se congelan paneles.
    # ============================================================

    def _limpiar_df_excel(df):
        return df.replace([np.inf, -np.inf], np.nan).fillna('')

    def _escribir_tabla(ws, df, fila_inicio, fmt_hdr, fmt_cell, fmt_total=None):
        for c, v in enumerate(df.columns):
            ws.write(fila_inicio, c, str(v), fmt_hdr)
        for r in range(len(df)):
            for c in range(len(df.columns)):
                valor = df.iloc[r, c]
                fmt = fmt_cell
                if fmt_total is not None and 'ANIO' in df.columns and str(df.iloc[r]['ANIO']) == 'TOTAL GENERAL':
                    fmt = fmt_total
                ws.write(fila_inicio + 1 + r, c, valor, fmt)

    def to_excel_pro():
        output = BytesIO()

        df_det = _limpiar_df_excel(tabla1_final).astype(str)
        df_grav = _limpiar_df_excel(tabla_gravedad)
        df_edad = _limpiar_df_excel(tabla_etario_det)
        df_anio = _limpiar_df_excel(tabla_graf)

        with pd.ExcelWriter(
            output,
            engine='xlsxwriter',
            engine_kwargs={'options': {'nan_inf_to_errors': True}}
        ) as writer:

            wb = writer.book

            fmt_title = wb.add_format({
                'bold': True, 'font_size': 15, 'font_color': 'white',
                'bg_color': '#1C2E4A', 'align': 'left', 'valign': 'vcenter'
            })
            fmt_sub = wb.add_format({
                'bold': True, 'font_size': 10, 'font_color': '#1C2E4A',
                'bg_color': '#D9E1F2', 'align': 'left', 'valign': 'vcenter'
            })
            fmt_sec = wb.add_format({
                'bold': True, 'font_size': 11, 'font_color': 'white',
                'bg_color': '#4472C4', 'align': 'left', 'valign': 'vcenter'
            })
            fmt_hdr = wb.add_format({
                'bold': True, 'bg_color': '#1C2E4A', 'font_color': 'white',
                'border': 1, 'align': 'center', 'valign': 'vcenter',
                'text_wrap': True
            })
            fmt_cell = wb.add_format({
                'border': 1, 'align': 'center', 'valign': 'vcenter'
            })
            fmt_total = wb.add_format({
                'bold': True, 'bg_color': '#FFD700', 'border': 2,
                'align': 'center', 'valign': 'vcenter'
            })

            # ----------------------------------------------------
            # HOJA EXISTENTE 1 — TABLA_1_DETALLE
            # Tabla 1 + Gráfico 1
            # ----------------------------------------------------
            df_det.to_excel(writer, sheet_name='TABLA_1_DETALLE',
                            index=False, startrow=5)
            ws1 = writer.sheets['TABLA_1_DETALLE']
            ws1.hide_gridlines(2)
            ws1.set_zoom(85)
            ws1.merge_range(
                0, 0, 0, max(0, len(df_det.columns)-1),
                'MÓDULO PLAGUICIDAS — TABLA 1: CASOS DE INTOXICACIÓN',
                fmt_title
            )
            ws1.merge_range(
                1, 0, 1, max(0, len(df_det.columns)-1),
                f'Año: {ano_filtro} | Provincia: {prov_filtro} | '
                f'Distrito: {dis_filtro} | Total: {total_general} casos | '
                f'Fallecidos: {total_fallecidos} | '
                f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                fmt_sub
            )
            ws1.merge_range(
                3, 0, 3, min(max(0, len(df_det.columns)-1), 9),
                'TABLA 1 — DETALLE COMPLETO',
                fmt_sec
            )
            _escribir_tabla(ws1, df_det, 5, fmt_hdr, fmt_cell, fmt_total)
            ws1.set_column(0, max(0, len(df_det.columns)-1), 16)
            if len(df_det.columns) > 0:
                ws1.set_column(0, 0, 10)
            if len(df_det.columns) > 4:
                ws1.set_column(4, 4, 18)
            ws1.autofilter(5, 0, len(df_det)+5, max(0, len(df_det.columns)-1))

            # Gráfico 1: mismo contenido y color del sistema.
            fila_g1 = len(df_det) + 9
            ws1.merge_range(
                fila_g1, 0, fila_g1, min(max(0, len(df_det.columns)-1), 9),
                'GRÁFICO 1 — PLAGUICIDAS POR AÑO',
                fmt_sec
            )
            aux1 = fila_g1 + 2
            ws1.write(aux1, 0, 'ANIO', fmt_hdr)
            ws1.write(aux1, 1, 'TOTAL', fmt_hdr)
            for i, (_, r) in enumerate(df_anio.iterrows(), start=aux1+1):
                ws1.write(i, 0, str(r['ANIO']), fmt_cell)
                ws1.write(i, 1, int(r['TOTAL']), fmt_cell)

            chart1 = wb.add_chart({'type': 'column'})
            n = len(df_anio)
            if n:
                chart1.add_series({
                    'name': 'TOTAL',
                    'categories': f"='TABLA_1_DETALLE'!$A${aux1+2}:$A${aux1+n+1}",
                    'values': f"='TABLA_1_DETALLE'!$B${aux1+2}:$B${aux1+n+1}",
                    'fill': {'color': '#32CD32'},
                    'border': {'color': '#32CD32'},
                    'data_labels': {'value': True}
                })
            chart1.set_title({'name': 'PLAGUICIDAS por AÑO'})
            chart1.set_x_axis({'name': 'Año'})
            chart1.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            chart1.set_legend({'none': True})
            chart1.set_style(10)
            chart1.set_size({'width': 650, 'height': 330})
            ws1.insert_chart(aux1, 3, chart1, {'object_position': 1})

            # ----------------------------------------------------
            # HOJA EXISTENTE 2 — BANDA_TOXICOLOGICA
            # Tabla + Gráfico 2
            # ----------------------------------------------------
            df_grav.to_excel(writer, sheet_name='BANDA_TOXICOLOGICA',
                             index=False, startrow=5)
            ws2 = writer.sheets['BANDA_TOXICOLOGICA']
            ws2.hide_gridlines(2)
            ws2.set_zoom(90)
            ws2.merge_range(
                0, 0, 0, max(1, len(df_grav.columns)-1),
                'MÓDULO PLAGUICIDAS — BANDA TOXICOLÓGICA',
                fmt_title
            )
            ws2.merge_range(
                1, 0, 1, max(1, len(df_grav.columns)-1),
                f'Año: {ano_filtro} | Provincia: {prov_filtro} | '
                f'Distrito: {dis_filtro} | Total: {total_general} casos',
                fmt_sub
            )
            ws2.merge_range(
                3, 0, 3, max(1, len(df_grav.columns)-1),
                'TABLA — DISTRIBUCIÓN POR BANDA TOXICOLÓGICA',
                fmt_sec
            )
            _escribir_tabla(ws2, df_grav, 5, fmt_hdr, fmt_cell)
            ws2.set_column(0, max(0, len(df_grav.columns)-1), 24)
            ws2.set_column(0, 0, 58)

            fila_g2 = len(df_grav) + 9
            ws2.merge_range(
                fila_g2, 0, fila_g2, max(1, len(df_grav.columns)-1),
                'GRÁFICO 2 — DISTRIBUCIÓN POR BANDA TOXICOLÓGICA',
                fmt_sec
            )
            aux2 = fila_g2 + 2

            chart2 = wb.add_chart({'type': 'doughnut'})
            n2 = len(df_grav)
            puntos = []
            for _, r in df_grav.iterrows():
                nombre = str(r.get('DESC_GRAVEDAD', ''))
                if 'BANDA ROJA' in nombre:
                    color = '#FF0000'
                elif 'BANDA AMARILLA' in nombre:
                    color = '#FFD700'
                elif 'BANDA AZUL' in nombre:
                    color = '#0000FF'
                elif 'BANDA VERDE' in nombre:
                    color = '#00FF00'
                else:
                    color = '#888888'
                puntos.append({'fill': {'color': color}})
            if n2:
                chart2.add_series({
                    'name': 'Casos',
                    'categories': f"='BANDA_TOXICOLOGICA'!$A$7:$A${n2+6}",
                    'values': f"='BANDA_TOXICOLOGICA'!$B$7:$B${n2+6}",
                    'points': puntos,
                    'data_labels': {'percentage': True}
                })
            chart2.set_title({'name': 'Distribucion por Banda Toxicologica'})
            chart2.set_legend({'position': 'bottom'})
            chart2.set_style(10)
            chart2.set_size({'width': 650, 'height': 360})
            ws2.insert_chart(aux2, 0, chart2, {'object_position': 1})

            # ----------------------------------------------------
            # HOJA EXISTENTE 3 — GRUPO_ETARIO
            # Tabla + Gráfico 3
            # ----------------------------------------------------
            df_edad.to_excel(writer, sheet_name='GRUPO_ETARIO',
                             index=False, startrow=5)
            ws3 = writer.sheets['GRUPO_ETARIO']
            ws3.hide_gridlines(2)
            ws3.set_zoom(90)
            ws3.merge_range(
                0, 0, 0, max(1, len(df_edad.columns)-1),
                'MÓDULO PLAGUICIDAS — TABLA 2: GRUPO ETARIO',
                fmt_title
            )
            ws3.merge_range(
                1, 0, 1, max(1, len(df_edad.columns)-1),
                f'Año: {ano_filtro} | Provincia: {prov_filtro} | '
                f'Distrito: {dis_filtro} | Total: {total_general} casos',
                fmt_sub
            )
            ws3.merge_range(
                3, 0, 3, max(1, len(df_edad.columns)-1),
                'TABLA 2 — GRUPO ETARIO Y SEXO',
                fmt_sec
            )
            _escribir_tabla(ws3, df_edad, 5, fmt_hdr, fmt_cell)
            ws3.set_column(0, max(0, len(df_edad.columns)-1), 18)
            ws3.set_column(0, 0, 30)

            fila_g3 = len(df_edad) + 9
            ws3.merge_range(
                fila_g3, 0, fila_g3, max(1, len(df_edad.columns)-1),
                'GRÁFICO 3 — CASOS POR GRUPO ETARIO',
                fmt_sec
            )
            aux3 = fila_g3 + 2
            ws3.write(aux3, 0, 'GRUPO ETARIO', fmt_hdr)
            ws3.write(aux3, 1, 'TOTAL', fmt_hdr)
            for i, (_, r) in enumerate(tabla_etario.iterrows(), start=aux3+1):
                ws3.write(i, 0, str(r['GRUPO_ETARIO']), fmt_cell)
                ws3.write(i, 1, int(r['TOTAL']), fmt_cell)

            chart3 = wb.add_chart({'type': 'column'})
            n3 = len(tabla_etario)
            puntos3 = []
            for _, r in tabla_etario.iterrows():
                puntos3.append({
                    'fill': {
                        'color': colores_etario.get(
                            str(r['GRUPO_ETARIO']), '#F44336'
                        )
                    }
                })
            if n3:
                chart3.add_series({
                    'name': 'TOTAL',
                    'categories': f"='GRUPO_ETARIO'!$A${aux3+2}:$A${aux3+n3+1}",
                    'values': f"='GRUPO_ETARIO'!$B${aux3+2}:$B${aux3+n3+1}",
                    'points': puntos3,
                    'data_labels': {'value': True}
                })
            chart3.set_title({'name': 'Casos por Grupo Etario'})
            chart3.set_legend({'none': True})
            chart3.set_x_axis({'name': 'Grupo Etario'})
            chart3.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            chart3.set_style(10)
            chart3.set_size({'width': 650, 'height': 350})
            ws3.insert_chart(aux3, 3, chart3, {'object_position': 1})

            # ----------------------------------------------------
            # HOJA EXISTENTE 4 — POR_AÑO
            # Tabla de soporte completa + gráfico 1 también visible aquí.
            # No se crea ninguna hoja adicional.
            # ----------------------------------------------------
            df_anio.to_excel(writer, sheet_name='POR_AÑO',
                             index=False, startrow=5)
            ws4 = writer.sheets['POR_AÑO']
            ws4.hide_gridlines(2)
            ws4.set_zoom(90)
            ws4.merge_range(
                0, 0, 0, max(1, len(df_anio.columns)-1),
                'MÓDULO PLAGUICIDAS — POR AÑO',
                fmt_title
            )
            ws4.merge_range(
                1, 0, 1, max(1, len(df_anio.columns)-1),
                f'Año: {ano_filtro} | Provincia: {prov_filtro} | '
                f'Distrito: {dis_filtro}',
                fmt_sub
            )
            ws4.merge_range(
                3, 0, 3, max(1, len(df_anio.columns)-1),
                'TABLA — CASOS POR AÑO',
                fmt_sec
            )
            _escribir_tabla(ws4, df_anio, 5, fmt_hdr, fmt_cell)
            ws4.set_column(0, max(0, len(df_anio.columns)-1), 18)

        return output.getvalue()

    def to_pdf_3d():
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=30, leftMargin=30,
            topMargin=30, bottomMargin=30
        )
        styles = getSampleStyleSheet()
        titulo = ParagraphStyle(
            'PlaTitulo', parent=styles['Heading1'], fontSize=13,
            textColor=colors.HexColor('#1C2E4A'), alignment=1,
            spaceAfter=8
        )
        h2 = ParagraphStyle(
            'PlaH2', parent=styles['Heading2'], fontSize=10,
            textColor=colors.HexColor('#1C2E4A'),
            spaceBefore=9, spaceAfter=5
        )
        desc = ParagraphStyle(
            'PlaDesc', parent=styles['Normal'], fontSize=8,
            leading=11, textColor=colors.HexColor('#334155'),
            backColor=colors.HexColor('#F8FAFC'),
            borderPadding=6, spaceAfter=7
        )

        story = [
            Paragraph(
                f"<b>ANÁLISIS NOTIWEB — PLAGUICIDAS</b><br/>"
                f"Año: {ano_filtro} | Provincia: {prov_filtro} | "
                f"Distrito: {dis_filtro}<br/>"
                f"Total: <b>{total_general}</b> casos | "
                f"Fallecidos: <b>{total_fallecidos}</b> | "
                f"Archivos: {len(lista_df)}/{len(archivos)} | "
                f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                titulo
            )
        ]

        pct_f = (total_fallecidos / total_general * 100) if total_general else 0
        banda_top = (
            tabla_gravedad.loc[
                tabla_gravedad['TOTAL'].idxmax(), 'DESC_GRAVEDAD'
            ] if not tabla_gravedad.empty else 'S/D'
        )
        banda_n = int(tabla_gravedad['TOTAL'].max()) if not tabla_gravedad.empty else 0
        grupo_top = (
            tabla_etario.iloc[0]['GRUPO_ETARIO']
            if not tabla_etario.empty else 'S/D'
        )
        grupo_n = int(tabla_etario.iloc[0]['TOTAL']) if not tabla_etario.empty else 0

        story += [
            Paragraph("<b>1. RESUMEN E INTERPRETACIÓN</b>", h2),
            Paragraph(
                f"El sistema registra <b>{total_general} casos</b> de intoxicación "
                f"por plaguicidas. Se identifican <b>{total_fallecidos} fallecidos</b> "
                f"({pct_f:.1f}% del total). La banda toxicológica con mayor frecuencia "
                f"es <b>{banda_top}</b>, con {banda_n} casos. El grupo etario con "
                f"mayor registro es <b>{grupo_top}</b>, con {grupo_n} casos. "
                f"Esta interpretación se calcula únicamente con los datos y filtros "
                f"del módulo mostrado en pantalla.",
                desc
            )
        ]

        # Tabla 1 completa, distribuida en páginas.
        story.append(Paragraph("<b>2. TABLA 1 — CASOS DE INTOXICACIÓN POR PLAGUICIDAS</b>", h2))
        cols1 = list(tabla1.columns)
        vista1 = tabla1.copy()
        # PDF conserva la información completa; se muestran todas las filas.
        if len(cols1) > 10:
            cols1_pdf = cols1[:10]
        else:
            cols1_pdf = cols1

        data1 = [[str(c)[:18] for c in cols1_pdf]]
        for _, r in vista1.iterrows():
            data1.append([str(r.get(c, ''))[:18] for c in cols1_pdf])

        ancho = max(35, (A4[0] - 60) / max(1, len(cols1_pdf)))
        t1 = Table(data1, colWidths=[ancho] * len(cols1_pdf), repeatRows=1)
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1C2E4A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#B8C0CC')),
            ('FONTSIZE', (0,0), (-1,-1), 5.2),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t1)
        story.append(Paragraph(
            f"La tabla contiene los registros utilizados por el módulo. "
            f"Total general: <b>{total_general}</b>.",
            desc
        ))

        # Gráfico 1
        fig, ax = plt.subplots(figsize=(6, 2.6))
        ax.bar(tabla_graf['ANIO'].astype(str), tabla_graf['TOTAL'], color='#32CD32')
        ax.set_title('PLAGUICIDAS por AÑO', fontsize=10)
        ax.set_xlabel('Año', fontsize=8)
        ax.set_ylabel('Casos', fontsize=8)
        ax.tick_params(labelsize=7)
        for i, v in enumerate(tabla_graf['TOTAL']):
            ax.text(i, v, str(v), ha='center', va='bottom', fontsize=7)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        b1 = BytesIO()
        plt.savefig(b1, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b1.seek(0)
        story += [
            Paragraph("<b>3. GRÁFICO 1 — PLAGUICIDAS POR AÑO</b>", h2),
            Image(b1, width=430, height=185),
            Paragraph(
                "Interpretación: muestra la cantidad de casos registrada en cada año "
                "según los mismos datos utilizados por el gráfico del sistema.",
                desc
            )
        ]

        # Tabla + gráfico 2
        story.append(Paragraph("<b>4. TABLA — BANDA TOXICOLÓGICA</b>", h2))
        data2 = [list(map(str, tabla_gravedad.columns))]
        for _, r in tabla_gravedad.iterrows():
            data2.append([str(x) for x in r.tolist()])
        t2 = Table(data2, repeatRows=1)
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1C2E4A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        story.append(t2)

        fig, ax = plt.subplots(figsize=(6, 3.1))
        labels = tabla_gravedad['DESC_GRAVEDAD'].astype(str).tolist()
        vals = tabla_gravedad['TOTAL'].tolist()
        cmap = []
        for x in labels:
            if 'BANDA ROJA' in x:
                cmap.append('#FF0000')
            elif 'BANDA AMARILLA' in x:
                cmap.append('#FFD700')
            elif 'BANDA AZUL' in x:
                cmap.append('#0000FF')
            elif 'BANDA VERDE' in x:
                cmap.append('#00FF00')
            else:
                cmap.append('#888888')
        if vals and sum(vals) > 0:
            ax.pie(
                vals, labels=labels, autopct='%1.1f%%',
                colors=cmap, startangle=90,
                explode=[0.05] * len(vals),
                textprops={'fontsize': 5}
            )
        ax.set_title('Distribucion por Banda Toxicologica', fontsize=10)
        plt.tight_layout()
        b2 = BytesIO()
        plt.savefig(b2, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b2.seek(0)
        story += [
            Paragraph("<b>5. GRÁFICO 2 — DISTRIBUCIÓN POR BANDA TOXICOLÓGICA</b>", h2),
            Image(b2, width=430, height=220),
            Paragraph(
                f"Interpretación: la categoría con mayor frecuencia es "
                f"<b>{banda_top}</b> ({banda_n} casos). Los colores corresponden "
                f"a las bandas utilizadas por el sistema.",
                desc
            )
        ]

        # Tabla + gráfico 3
        story.append(Paragraph("<b>6. TABLA 2 — GRUPO ETARIO Y SEXO</b>", h2))
        data3 = [list(map(str, tabla_etario_det.columns))]
        for _, r in tabla_etario_det.iterrows():
            data3.append([str(x) for x in r.tolist()])
        t3 = Table(data3, repeatRows=1)
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1C2E4A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        story.append(t3)

        fig, ax = plt.subplots(figsize=(6, 2.8))
        et = tabla_etario.sort_values('TOTAL')
        ax.barh(
            et['GRUPO_ETARIO'].astype(str),
            et['TOTAL'],
            color=[
                colores_etario.get(str(x), '#F44336')
                for x in et['GRUPO_ETARIO']
            ]
        )
        ax.set_title('Casos por Grupo Etario', fontsize=10)
        ax.set_xlabel('Casos', fontsize=8)
        ax.tick_params(labelsize=7)
        for i, v in enumerate(et['TOTAL']):
            ax.text(v, i, str(v), va='center', fontsize=7)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        b3 = BytesIO()
        plt.savefig(b3, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b3.seek(0)
        story += [
            Paragraph("<b>7. GRÁFICO 3 — CASOS POR GRUPO ETARIO</b>", h2),
            Image(b3, width=430, height=200),
            Paragraph(
                f"Interpretación: el grupo con mayor número de casos es "
                f"<b>{grupo_top}</b>, con {grupo_n} registros.",
                desc
            )
        ]

        doc.build(story)
        return buffer.getvalue()

    st.divider()
    st.subheader("📥 Descargas Profesionales")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "📊 DESCARGAR EXCEL",
            data=to_excel_pro(),
            file_name=f"PLAGUICIDAS_COMPLETO_{ano_filtro}_{prov_filtro}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
    with c2:
        st.download_button(
            "📄 DESCARGAR PDF",
            data=to_pdf_3d(),
            file_name=f"PLAGUICIDAS_COMPLETO_{ano_filtro}_{prov_filtro}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
