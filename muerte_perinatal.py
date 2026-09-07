
# LIBRERIAS A USAR
import streamlit as st
import pandas as pd
import os
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from io import BytesIO
import xlsxwriter
from plotly.subplots import make_subplots
from datetime import datetime
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

def mostrar_pagina():
    st.subheader("Módulo MUERTE PERINATAL - Análisis")

    try:
        modo = st.segmented_control("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], key="mp_modo", default="📁 Carpeta automática")
    except Exception:
        try:
            modo = st.pills("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], key="mp_modo", default="📁 Carpeta automática")
        except Exception:
            modo = st.radio("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], horizontal=True, key="mp_modo")

    if not modo:
        modo = "📁 Carpeta automática"

    lista_df = []
    archivos = []
    archivos_fallidos = []

    if "Subir" in modo:
        uploaded = st.file_uploader("📂 Arrastra aquí tus archivos Excel de MUERTE PERINATAL", type=['xlsx','xls','csv'], accept_multiple_files=True, key="mp_upload")
        if not uploaded:
            st.info("👆 Sube tus archivos Excel para empezar")
            return
        archivos = [f.name for f in uploaded]
        progress = st.progress(0)
        for idx, f in enumerate(uploaded):
            progress.progress((idx+1)/len(uploaded))
            df_temp = None
            try:
                if f.name.lower().endswith('.csv'):
                    df_temp = pd.read_csv(f, encoding='utf-8', low_memory=False)
                else:
                    try:
                        df_temp = pd.read_excel(f, engine='openpyxl', header=0)
                    except:
                        try:
                            df_temp = pd.read_excel(f, engine='xlrd', header=0)
                        except:
                            df_temp = pd.read_excel(f, header=0)
            except Exception as e:
                archivos_fallidos.append(f.name)
                continue

            if df_temp is not None and not df_temp.empty:
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                df_temp = df_temp.dropna(how='all')
                df_temp = df_temp.dropna(axis=1, how='all')
                lista_df.append(df_temp)
            else:
                archivos_fallidos.append(f.name)
        progress.empty()
    else:
        RUTA_BASE = os.path.dirname(__file__)
        ruta_carpeta = os.path.join(RUTA_BASE, 'MUERTE PERINATAL')
        
        if not os.path.exists(ruta_carpeta):
            st.warning(f"⚠️ No existe la carpeta MUERTE PERINATAL")
            return

        archivos_raw = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
        archivos = archivos_raw
        
        if not archivos:
            st.warning("La carpeta MUERTE PERINATAL está vacía")
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
            except Exception as e:
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

    df = pd.concat(lista_df, ignore_index=True, sort=False)
    df.columns = df.columns.astype(str).str.lower().str.strip()

    # MAPEO - DE DATOS DE EXCEL


    df['ANIO'] = pd.to_numeric(df.get('anio', 0), errors='coerce')
    df['ANIO'] = df['ANIO'].fillna(0).astype(int).astype(str)
    df.loc[df['ANIO'] == '0', 'ANIO'] = 'S/D'

    df['DEPARTAMEN'] = df.get('departamen', df.get('depar', 'SIN DATO')).fillna('SIN DATO')
    df['PROVINCIA'] = df.get('provincia', df.get('prov', 'SIN DATO')).fillna('SIN DATO')
    df['DISTRITO'] = df.get('distrito', df.get('dis', 'SIN DATO')).fillna('SIN DATO')
    df['MICROREDES'] = df.get('microredes', df.get('microred', 'SIN DATO')).fillna('SIN DATO')
    df['ESTABLECIMINETO'] = df.get('establecimineto', df.get('eess', df.get('establecimiento', 'SIN DATO'))).fillna('SIN DATO')
    
    sexo = df.get('sexo', pd.Series(['']*len(df))).astype(str).str.upper().str.strip()
    df['SEXO'] = 'INDETERMINADO'
    df.loc[sexo == 'M', 'SEXO'] = 'MASCULINO'
    df.loc[sexo == 'F', 'SEXO'] = 'FEMENINO'
    
    df['FECHA_NAC'] = pd.to_datetime(df.get('fecha_nac'), errors='coerce').dt.strftime('%d/%m/%Y')
    df['FECHA_NAC'] = df['FECHA_NAC'].fillna('S/D')
    df['FECHA_MTE'] = pd.to_datetime(df.get('fecha_mte'), errors='coerce').dt.strftime('%d/%m/%Y')
    df['FECHA_MTE'] = df['FECHA_MTE'].fillna('S/D')

    tipo = df.get('tipo_mte', pd.Series(['']*len(df))).astype(str).str.upper().str.strip()
    df['TIPO_MTE'] = 'SIN DATO'
    df.loc[tipo == 'F', 'TIPO_MTE'] = 'MTE FETAL'
    df.loc[tipo == 'N', 'TIPO_MTE'] = 'MTE NEONATAL'

    st.subheader("2. Filtros:")
    col1, col2, col3 = st.columns(3)
    with col1:
        anos_raw = [str(x) for x in df['ANIO'].astype(str).unique().tolist() if str(x).lower() not in ['nan','s/d','']]
        anos_disponibles = ['TODOS'] + sorted(anos_raw, key=lambda x: int(x) if x.isdigit() else x)
        ano_filtro = st.selectbox("Filtrar por AÑO:", anos_disponibles, key='mp_ano')
    with col2:
        prov_raw = [str(x).strip() for x in df['PROVINCIA'].astype(str).unique().tolist() if str(x).lower() not in ['nan','sin dato','']]
        prov_disponibles = ['TODAS'] + sorted(prov_raw)
        prov_filtro = st.selectbox("Filtrar por PROVINCIA:", prov_disponibles, key='mp_prov')
    with col3:
        if prov_filtro != 'TODAS':
            distritos_filtrados = df[df['PROVINCIA'].astype(str) == prov_filtro]['DISTRITO'].astype(str).unique().tolist()
        else:
            distritos_filtrados = df['DISTRITO'].astype(str).unique().tolist()
        dis_raw = [str(x).strip() for x in distritos_filtrados if str(x).lower() not in ['nan','sin dato','']]
        dis_disponibles = ['TODOS'] + sorted(dis_raw)
        dis_filtro = st.selectbox("Filtrar por DISTRITO:", dis_disponibles, key='mp_dis')

    df_filtrado = df.copy()
    if ano_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['ANIO'].astype(str) == str(ano_filtro)]
    if prov_filtro!= 'TODAS': df_filtrado = df_filtrado[df_filtrado['PROVINCIA'].astype(str) == str(prov_filtro)]
    if dis_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['DISTRITO'].astype(str) == str(dis_filtro)]

    st.subheader("TABLA 1: Casos de MUERTE PERINATAL")
    columnas_tabla1 = ['ANIO', 'DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'MICROREDES', 'ESTABLECIMINETO','SEXO', 'FECHA_NAC', 'FECHA_MTE', 'TIPO_MTE']
    for c in columnas_tabla1:
        if c not in df_filtrado.columns:
            df_filtrado[c]='S/D'
    tabla1 = df_filtrado[columnas_tabla1].copy()
    tabla1['TOTAL'] = 1
    total_general = len(tabla1)
    if total_general == 0:
        st.warning("No se registraron casos con los filtros seleccionados")
        return
    fila_total = {col: '' for col in columnas_tabla1}
    fila_total['ANIO'] = 'TOTAL GENERAL'
    fila_total['TOTAL'] = total_general
    tabla1_final = pd.concat([tabla1, pd.DataFrame([fila_total])], ignore_index=True)
    def colorear_tabla(row):
        if row['ANIO'] == 'TOTAL GENERAL':
            return ['background-color: #FFD700; font-weight: bold'] * len(row)
        return [''] * len(row)
    st.dataframe(tabla1_final.style.apply(colorear_tabla, axis=1), use_container_width=True, hide_index=True)

    # TABLAS PARA GRAFICOS
    tabla_graf = df_filtrado.groupby('ANIO').size().reset_index(name='TOTAL').sort_values('ANIO')
    tabla_tipo = df_filtrado.groupby('TIPO_MTE').size().reset_index(name='TOTAL').sort_values('TOTAL', ascending=False)
    tabla2 = df_filtrado.groupby('SEXO').size().reset_index(name='TOTAL').sort_values('TOTAL', ascending=False)

    # GRAFICOS
    c1_g, c2_g = st.columns(2)
    with c1_g:
        fig1 = px.bar(tabla_graf, x='ANIO', y='TOTAL', title='Muerte Perinatal por Año', text='TOTAL', color='ANIO')
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)
    with c2_g:
        fig2 = px.pie(tabla_tipo, names='TIPO_MTE', values='TOTAL', title='Distribución MTE FETAL vs NEONATAL (3D)', hole=0.3, color='TIPO_MTE', color_discrete_map={'MTE FETAL': '#0052CC', 'MTE NEONATAL': '#5FA8FF', 'SIN DATO': '#D3D3D3'})
        fig2.update_traces(textinfo='percent+label', pull=[0.1 if 'FETAL' in str(x) else 0 for x in tabla_tipo['TIPO_MTE']])
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(tabla2, x='SEXO', y='TOTAL', title='Distribución por Sexo', text='TOTAL', color='SEXO', color_discrete_sequence=['#FF6FB5','#0EA5E9','#9E9E9E'])
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

    # DESCARGAS

    def to_excel_pro():
        df_exp = tabla1_final.replace([np.inf, -np.inf], np.nan).fillna('')
        tabla_tipo_exp = tabla_tipo.copy()
        tabla2_exp = tabla2.copy()

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine='xlsxwriter',
            engine_kwargs={'options': {'nan_inf_to_errors': True}}
        ) as writer:

            wb = writer.book

            # COLORES DEL PANTALLA

            navy = '#1C2E4A'
            blue = '#4472C4'
            light_blue = '#D9E1F2'
            pink = '#FF6FB5'
            cyan = '#0EA5E9'
            gray = '#F5F5F5'
            gold = '#FFD700'
            border = '#D0D7DE'
            fetal_blue = '#0052CC'
            neonatal_blue = '#5FA8FF'
            unknown = '#D3D3D3'

            title = wb.add_format({
                'bold': True,
                'font_size': 15,
                'font_color': 'white',
                'bg_color': navy,
                'align': 'left',
                'valign': 'vcenter'
            })
            subtitle = wb.add_format({
                'bold': True,
                'font_size': 10,
                'font_color': navy,
                'bg_color': light_blue,
                'align': 'left',
                'valign': 'vcenter'
            })
            section = wb.add_format({
                'bold': True,
                'font_size': 11,
                'font_color': 'white',
                'bg_color': blue,
                'align': 'left',
                'valign': 'vcenter'
            })
            hdr = wb.add_format({
                'bold': True,
                'bg_color': navy,
                'font_color': 'white',
                'border': 1,
                'border_color': border,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            })
            cell = wb.add_format({
                'border': 1,
                'border_color': border,
                'align': 'center',
                'valign': 'vcenter'
            })
            cell_left = wb.add_format({
                'border': 1,
                'border_color': border,
                'align': 'left',
                'valign': 'vcenter'
            })
            total_fmt = wb.add_format({
                'bold': True,
                'bg_color': gold,
                'border': 2,
                'border_color': '#B7A000',
                'align': 'center',
                'valign': 'vcenter'
            })
            kpi_label = wb.add_format({
                'bold': True,
                'bg_color': gray,
                'font_color': navy,
                'border': 1,
                'border_color': border,
                'align': 'center',
                'valign': 'vcenter'
            })
            kpi_value = wb.add_format({
                'bold': True,
                'font_size': 18,
                'font_color': navy,
                'border': 1,
                'border_color': border,
                'align': 'center',
                'valign': 'vcenter'
            })

            #HOJA 1, TABLA 1, GRAFICO 1, EXCEL
            df_exp.to_excel(
                writer,
                sheet_name='TABLA_1',
                index=False,
                startrow=9
            )
            ws = writer.sheets['TABLA_1']
            ws.hide_gridlines(2)
            ws.set_zoom(85)
            ws.set_tab_color(blue)
            ws.set_row(0, 30)

            ultima_col = len(df_exp.columns) - 1

            ws.merge_range(
                0, 0, 0, ultima_col,
                'MÓDULO MUERTE PERINATAL — ANÁLISIS NOTIWEB',
                title
            )
            ws.merge_range(
                1, 0, 1, ultima_col,
                f'Año: {ano_filtro}  |  Provincia: {prov_filtro}  |  '
                f'Distrito: {dis_filtro}  |  Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                subtitle
            )

            ws.merge_range(
                3, 0, 3, min(ultima_col, 9),
                'INDICADORES DEL REPORTE',
                section
            )

            # INDICADORES LEIDOS 

            ws.merge_range('A5:B5', 'TOTAL DE CASOS', kpi_label)
            ws.merge_range('A6:B7', total_general, kpi_value)

            ws.merge_range('C5:D5', 'ARCHIVOS LEÍDOS', kpi_label)
            ws.merge_range('C6:D7', len(lista_df), kpi_value)

            ws.merge_range('E5:F5', 'AÑO', kpi_label)
            ws.merge_range('E6:F7', ano_filtro, kpi_value)

            ws.merge_range('G5:H5', 'PROVINCIA', kpi_label)
            ws.merge_range('G6:H7', prov_filtro, kpi_value)

            if ultima_col >= 8:
                ws.merge_range('I5:J5', 'DISTRITO', kpi_label)
                ws.merge_range('I6:J7', dis_filtro, kpi_value)

            # ENCABEZADO DE TABLA FILA 10.
            for c, v in enumerate(df_exp.columns):
                ws.write(9, c, v, hdr)

            # DATOS REALES.
            for r in range(len(df_exp)):
                for c in range(len(df_exp.columns)):
                    valor = df_exp.iloc[r, c]
                    fmt = (
                        total_fmt
                        if str(df_exp.iloc[r]['ANIO']) == 'TOTAL GENERAL'
                        else cell
                    )
                    ws.write(r + 10, c, valor, fmt)

            ws.set_column('A:A', 14)
            ws.set_column('B:D', 20)
            ws.set_column('E:F', 20)
            ws.set_column('G:G', 18)
            ws.set_column('H:K', 18)
            ws.autofilter(
                9, 0,
                len(df_exp) + 9,
                len(df_exp.columns) - 1
            )

            # GRÁFICO 1 
            row_g1 = len(df_exp) + 13

            ws.merge_range(
                row_g1, 0, row_g1, min(ultima_col, 9),
                'GRÁFICO 1 — MUERTE PERINATAL POR AÑO',
                section
            )

            data_start = row_g1 + 2
            ws.write(data_start, 0, 'AÑO', hdr)
            ws.write(data_start, 1, 'Casos', hdr)

            for r, (_, row) in enumerate(tabla_graf.iterrows(), start=data_start + 1):
                ws.write(r, 0, str(row['ANIO']), cell)
                ws.write(r, 1, int(row['TOTAL']), cell)

            n1 = len(tabla_graf)
            chart1 = wb.add_chart({'type': 'column'})

            if n1 > 0:
                chart1.add_series({
                    'name': 'Casos',
                    'categories': f'=TABLA_1!$A${data_start+2}:$A${data_start+1+n1}',
                    'values': f'=TABLA_1!$B${data_start+2}:$B${data_start+1+n1}',
                    'fill': {'color': pink},
                    'border': {'color': pink},
                    'data_labels': {'value': True}
                })

            chart1.set_title({'name': 'Muerte Perinatal por Año'})
            chart1.set_legend({'none': True})
            chart1.set_x_axis({'name': 'Año'})
            chart1.set_y_axis({
                'name': 'Casos',
                'major_gridlines': {'visible': False}
            })
            chart1.set_style(10)
            chart1.set_size({'width': 650, 'height': 340})
            ws.insert_chart(
                data_start,
                3,
                chart1,
                {'object_position': 1}
            )

            # GRÁFICO 3 
        
            row_g3 = data_start + max(n1, 1) + 19

            ws.merge_range(
                row_g3, 0, row_g3, min(ultima_col, 9),
                'GRÁFICO 3 — DISTRIBUCIÓN POR SEXO',
                section
            )

            data3_start = row_g3 + 2
            ws.write(data3_start, 0, 'SEXO', hdr)
            ws.write(data3_start, 1, 'Casos', hdr)

            for r, (_, row) in enumerate(tabla2_exp.iterrows(), start=data3_start + 1):
                ws.write(r, 0, str(row['SEXO']), cell)
                ws.write(r, 1, int(row['TOTAL']), cell)

            n3 = len(tabla2_exp)
            chart3 = wb.add_chart({'type': 'column'})

            if n3 > 0:
                puntos = []
                for _, row in tabla2_exp.iterrows():
                    sexo_val = str(row['SEXO']).upper()
                    if sexo_val == 'FEMENINO':
                        color = pink
                    elif sexo_val == 'MASCULINO':
                        color = cyan
                    else:
                        color = '#9E9E9E'
                    puntos.append({'fill': {'color': color}})

                chart3.add_series({
                    'name': 'Casos',
                    'categories': f'=TABLA_1!$A${data3_start+2}:$A${data3_start+1+n3}',
                    'values': f'=TABLA_1!$B${data3_start+2}:$B${data3_start+1+n3}',
                    'points': puntos,
                    'data_labels': {'value': True}
                })

            chart3.set_title({'name': 'Distribución por Sexo'})
            chart3.set_legend({'none': True})
            chart3.set_y_axis({
                'name': 'Casos',
                'major_gridlines': {'visible': False}
            })
            chart3.set_style(10)
            chart3.set_size({'width': 650, 'height': 340})

            ws.insert_chart(
                data3_start,
                3,
                chart3,
                {'object_position': 1}
            )

            # HOJA 2 — POR_TIPO + GRÁFICO 2

            tabla_tipo_exp.to_excel(
                writer,
                sheet_name='POR_TIPO',
                index=False,
                startrow=3
            )
            ws2 = writer.sheets['POR_TIPO']
            ws2.hide_gridlines(2)
            ws2.set_zoom(90)
            ws2.set_tab_color(fetal_blue)
            ws2.set_row(0, 30)

            ws2.merge_range(
                'A1:F1',
                'DISTRIBUCIÓN DE MUERTE PERINATAL POR TIPO',
                title
            )
            ws2.merge_range(
                'A2:F2',
                f'Año: {ano_filtro}  |  Provincia: {prov_filtro}  |  Distrito: {dis_filtro}',
                subtitle
            )

            for c, v in enumerate(tabla_tipo_exp.columns):
                ws2.write(3, c, v, hdr)

            for r in range(len(tabla_tipo_exp)):
                for c in range(len(tabla_tipo_exp.columns)):
                    ws2.write(r + 4, c, tabla_tipo_exp.iloc[r, c], cell)

            ws2.set_column('A:A', 32)
            ws2.set_column('B:B', 14)

            # Gráfico 2 

            row_tipo_chart = len(tabla_tipo_exp) + 7
            ws2.merge_range(
                row_tipo_chart, 0, row_tipo_chart, 5,
                'GRÁFICO 2 — MTE FETAL VS MTE NEONATAL',
                section
            )

            chart2 = wb.add_chart({'type': 'doughnut'})
            n2 = len(tabla_tipo_exp)

            if n2 > 0:
                puntos2 = []
                for _, row in tabla_tipo_exp.iterrows():
                    tipo_val = str(row['TIPO_MTE'])
                    if tipo_val == 'MTE FETAL':
                        c = fetal_blue
                    elif tipo_val == 'MTE NEONATAL':
                        c = neonatal_blue
                    else:
                        c = unknown
                    puntos2.append({'fill': {'color': c}})

                chart2.add_series({
                    'name': 'Tipo de Muerte',
                    'categories': f'=POR_TIPO!$A$5:$A${4+n2}',
                    'values': f'=POR_TIPO!$B$5:$B${4+n2}',
                    'points': puntos2,
                    'data_labels': {
                        'percentage': True,
                        'category': True
                    }
                })

            chart2.set_title({
                'name': 'Distribución MTE FETAL vs MTE NEONATAL'
            })
            chart2.set_legend({'position': 'bottom'})
            chart2.set_style(10)
            chart2.set_size({'width': 650, 'height': 360})

            ws2.insert_chart(
                row_tipo_chart + 2,
                0,
                chart2,
                {'object_position': 1}
            )

        return output.getvalue()

    def to_pdf_3d():
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()
        stt = ParagraphStyle(
            'T',
            parent=styles['Heading1'],
            fontSize=12,
            textColor=colors.HexColor('#1c2e4a'),
            alignment=1,
            spaceAfter=8
        )
        sh2 = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontSize=10,
            textColor=colors.HexColor('#1c2e4a'),
            spaceAfter=4,
            spaceBefore=10
        )
        s_desc = ParagraphStyle(
            'Desc',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#334155'),
            leftIndent=6,
            borderPadding=6,
            backColor=colors.HexColor('#f8fafc'),
            spaceAfter=6
        )

        story = []

        story.append(Paragraph(
            f"<b>ANÁLISIS NOTIWEB 2026 - MUERTE PERINATAL UE 405</b><br/>"
            f"Filtros: {ano_filtro}/{prov_filtro}/{dis_filtro} - "
            f"Total: {total_general} casos - {len(lista_df)} archivos - "
            f"{datetime.now().strftime('%d/%m/%Y')}",
            stt
        ))
        story.append(Spacer(1, 8))

        fetal = len(
            df_filtrado[df_filtrado['TIPO_MTE'] == 'MTE FETAL']
        )
        neonatal = len(
            df_filtrado[df_filtrado['TIPO_MTE'] == 'MTE NEONATAL']
        )
        porc_fetal = fetal / total_general * 100 if total_general > 0 else 0
        porc_neonatal = neonatal / total_general * 100 if total_general > 0 else 0

        story.append(Paragraph(
            "<b>1. RESUMEN EJECUTIVO</b>",
            sh2
        ))
        story.append(Paragraph(
            f"Se registraron <b>{total_general} casos</b> de "
            f"{len(lista_df)} archivos (de {len(archivos)}). "
            f"<b>MTE FETAL: {fetal} casos ({porc_fetal:.1f}%)</b> y "
            f"<b>MTE NEONATAL: {neonatal} casos ({porc_neonatal:.1f}%)</b>. "
            f"Provincia mayor carga: "
            f"<b>{df_filtrado['PROVINCIA'].value_counts().index[0] if not df_filtrado.empty else 'S/D'}</b>. "
            f"Predominio sexo: "
            f"<b>{df_filtrado['SEXO'].value_counts().index[0] if not df_filtrado.empty else 'S/D'}</b>. "
            f"Requiere fortalecimiento de control prenatal y atención neonatal.",
            s_desc
        ))

        # TABLA 1 
        story.append(Paragraph(
            "<b>2. TABLA 1: Detalle</b>",
            sh2
        ))

        data = [[
            'AÑO','PROV','DISTRITO','MICRORED','EESS','SEXO','TIPO_MTE'
        ]]

        for _, r in tabla1.sort_values('ANIO').head(20).iterrows():
            data.append([
                str(r['ANIO']),
                str(r['PROVINCIA'])[:8],
                str(r['DISTRITO'])[:8],
                str(r['MICROREDES'])[:8],
                str(r['ESTABLECIMINETO'])[:12],
                str(r['SEXO'])[:1],
                str(r['TIPO_MTE'])
            ])

        t = Table(
            data,
            colWidths=[30,45,45,45,70,25,60]
        )
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('GRID',(0,0),(-1,-1),0.4,colors.grey),
            ('FONTSIZE',(0,0),(-1,-1),6)
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

        story.append(Paragraph(
            f"Tabla muestra 20 casos de {total_general}. "
            f"Total general incluye todos los filtros. La distribución por "
            f"provincia y distrito permite identificar zonas de mayor riesgo perinatal.",
            s_desc
        ))

        #  GRÁFICO 1 
        fig, ax = plt.subplots(figsize=(5,2))
        ax.bar(
            tabla_graf['ANIO'].astype(str),
            tabla_graf['TOTAL'],
            color='#FF6FB5'
        )
        ax.set_title('Muerte Perinatal por Año', fontsize=9)
        ax.set_ylabel('Casos', fontsize=7)
        ax.tick_params(labelsize=7)
        ax.spines[['top','right']].set_visible(False)

        for i, v in enumerate(tabla_graf['TOTAL']):
            ax.text(i, v, str(v), ha='center', va='bottom', fontsize=7)

        plt.tight_layout()
        b = BytesIO()
        plt.savefig(b, format='png', dpi=170, bbox_inches='tight')
        plt.close()
        b.seek(0)

        story.append(Paragraph(
            "<b>3. GRÁFICO 1: Tendencia Anual</b>",
            sh2
        ))
        story.append(Image(b, width=400, height=130))
        story.append(Paragraph(
            f"Año con mayor registro: "
            f"<b>{tabla_graf.loc[tabla_graf['TOTAL'].idxmax(),'ANIO'] if not tabla_graf.empty else 'S/D'} "
            f"con {tabla_graf['TOTAL'].max() if not tabla_graf.empty else 0} casos</b>.",
            s_desc
        ))

        # GRÁFICO 2 
        fig = plt.figure(figsize=(5,2.5))
        ax = fig.add_subplot(111)

        labels = tabla_tipo['TIPO_MTE'].tolist()
        sizes = tabla_tipo['TOTAL'].tolist()
        colors_pie = []

        for label in labels:
            if label == 'MTE FETAL':
                colors_pie.append('#0052CC')
            elif label == 'MTE NEONATAL':
                colors_pie.append('#5FA8FF')
            else:
                colors_pie.append('#D3D3D3')

        explode = [
            0.1 if 'FETAL' in str(l) else 0
            for l in labels
        ]

        if sizes and sum(sizes) > 0:
            ax.pie(
                sizes,
                explode=explode,
                labels=labels,
                autopct='%1.1f%%',
                colors=colors_pie,
                shadow=True,
                startangle=90,
                pctdistance=0.6
            )

        ax.set_title(
            'Distribución MTE FETAL vs MTE NEONATAL',
            fontsize=9
        )
        plt.tight_layout()

        b2 = BytesIO()
        plt.savefig(b2, format='png', dpi=170, bbox_inches='tight')
        plt.close()
        b2.seek(0)

        story.append(Paragraph(
            "<b>4. GRÁFICO 2: MTE FETAL vs NEONATAL</b>",
            sh2
        ))
        story.append(Image(b2, width=380, height=180))
        story.append(Paragraph(
            f"Distribución: <b>MTE FETAL {fetal} casos "
            f"({porc_fetal:.1f}%) y MTE NEONATAL {neonatal} casos "
            f"({porc_neonatal:.1f}%)</b>. Predominio fetal indica necesidad "
            f"de mejorar control prenatal y detección de riesgo. Neonatal "
            f"requiere fortalecimiento de atención inmediata del recién nacido.",
            s_desc
        ))

        # GRÁFICO 3 

        fig, ax = plt.subplots(figsize=(5,2))
        tabla2_sorted = tabla2.sort_values('TOTAL')

        colores_sexo = []
        for sexo_val in tabla2_sorted['SEXO']:
            if str(sexo_val) == 'FEMENINO':
                colores_sexo.append('#FF6FB5')
            elif str(sexo_val) == 'MASCULINO':
                colores_sexo.append('#0EA5E9')
            else:
                colores_sexo.append('#9E9E9E')

        ax.bar(
            tabla2_sorted['SEXO'],
            tabla2_sorted['TOTAL'],
            color=colores_sexo
        )
        ax.set_title('Por Sexo', fontsize=9)
        ax.set_ylabel('Casos', fontsize=7)
        ax.tick_params(labelsize=7)
        ax.spines[['top','right']].set_visible(False)

        for i, v in enumerate(tabla2_sorted['TOTAL']):
            ax.text(i, v, str(v), ha='center', va='bottom', fontsize=7)

        plt.tight_layout()

        b3 = BytesIO()
        plt.savefig(b3, format='png', dpi=170, bbox_inches='tight')
        plt.close()
        b3.seek(0)

        story.append(Paragraph(
            "<b>5. GRÁFICO 3: Por Sexo</b>",
            sh2
        ))
        story.append(Image(b3, width=400, height=130))
        story.append(Paragraph(
            f"El gráfico presenta la distribución de los casos según sexo. "
            f"Predominio registrado: "
            f"<b>{df_filtrado['SEXO'].value_counts().index[0] if not df_filtrado.empty else 'S/D'}</b>.",
            s_desc
        ))

        doc.build(story)
        return buffer.getvalue()

    # DESCARGAS DE ARCHIVOS
    
    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "📊 DESCARGAR EXCEL",
            data=to_excel_pro(),
            file_name=f"MUERTE_PERINATAL_PRO_{ano_filtro}_{prov_filtro}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

    with c2:
        st.download_button(
            "📄 DESCARGAR PDF",
            data=to_pdf_3d(),
            file_name=f"MUERTE_PERINATAL_3D_{ano_filtro}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

