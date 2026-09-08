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

    # ============================================================
    # DESCARGAS PROFESIONALES
    # IMPORTANTE: esta sección NO modifica ningún cálculo del módulo.
    # Solo organiza la información que ya se muestra arriba para que
    # Excel y PDF conserven tablas, gráficos, títulos y colores.
    # ============================================================

    def to_excel_pro():
        df_exp = df_f[columnas_finales].replace([np.inf, -np.inf], np.nan).fillna('')
        output = BytesIO()

        with pd.ExcelWriter(
            output, engine='xlsxwriter',
            engine_kwargs={'options': {'nan_inf_to_errors': True}}
        ) as writer:
            wb = writer.book

            # ----- Colores iguales a los gráficos del sistema -----
            azul = '#4472C4'
            azul_oscuro = '#1c2e4a'
            azul_claro = '#D9E1F2'
            celeste = '#0EA5E9'
            rosado = '#FF6FB5'
            naranja = '#FF8C00'
            verde = '#90EE90'
            gris = '#F3F4F6'
            borde = '#D0D7DE'
            blanco = '#FFFFFF'

            titulo = wb.add_format({
                'bold': True, 'font_size': 16, 'font_color': blanco,
                'bg_color': azul_oscuro, 'align': 'left',
                'valign': 'vcenter'
            })
            subtitulo = wb.add_format({
                'bold': True, 'font_size': 10, 'font_color': azul_oscuro,
                'bg_color': azul_claro, 'align': 'left',
                'valign': 'vcenter'
            })
            seccion = wb.add_format({
                'bold': True, 'font_size': 12, 'font_color': blanco,
                'bg_color': azul, 'align': 'left', 'valign': 'vcenter'
            })
            encabezado = wb.add_format({
                'bold': True, 'font_color': blanco, 'bg_color': azul_oscuro,
                'border': 1, 'border_color': borde, 'align': 'center',
                'valign': 'vcenter', 'text_wrap': True
            })
            celda = wb.add_format({
                'border': 1, 'border_color': borde,
                'align': 'center', 'valign': 'vcenter'
            })
            texto = wb.add_format({
                'border': 1, 'border_color': borde,
                'align': 'left', 'valign': 'vcenter'
            })
            nota = wb.add_format({
                'italic': True, 'font_color': '#64748B', 'font_size': 9
            })
            kpi_t = wb.add_format({
                'bold': True, 'font_color': azul_oscuro,
                'bg_color': gris, 'border': 1, 'border_color': borde,
                'align': 'center'
            })
            kpi_v = wb.add_format({
                'bold': True, 'font_size': 18, 'font_color': azul_oscuro,
                'bg_color': blanco, 'border': 1, 'border_color': borde,
                'align': 'center', 'valign': 'vcenter'
            })

            # ========================================================
            # HOJA 1 - RESUMEN
            # ========================================================
            ws = wb.add_worksheet('RESUMEN')
            ws.hide_gridlines(2)
            ws.set_zoom(95)
            ws.set_tab_color(azul)

            ws.set_row(0, 30)
            ws.merge_range('A1:H1', 'MÓDULO TUBERCULOSIS — ANÁLISIS NOTIWEB', titulo)
            ws.merge_range(
                'A2:H2',
                f'Año: {año_sel}  |  Provincia: {prov_sel}  |  Establecimiento: {estab_sel}  |  Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                subtitulo
            )

            ws.merge_range('A4:H4', 'INDICADORES DEL REPORTE', seccion)

            indicadores = [
                ('A5:B5', 'A6:B7', 'TOTAL DE CASOS', total),
                ('C5:D5', 'C6:D7', 'ARCHIVOS LEÍDOS', len(lista_df)),
                ('E5:F5', 'E6:F7', 'AÑO', año_sel),
                ('G5:H5', 'G6:H7', 'ESTABLECIMIENTO', estab_sel),
            ]
            for lr, vr, label, value in indicadores:
                ws.merge_range(lr, label, kpi_t)
                ws.merge_range(vr, value, kpi_v)

            ws.merge_range('A9:H9', 'GRÁFICO 1 — CASOS POR AÑO', seccion)

            # Datos del gráfico exactamente como se muestran arriba
            ws.write('A10', 'AÑO', encabezado)
            ws.write('B10', 'Casos', encabezado)
            for r, row in data_año.iterrows():
                ws.write(r + 10, 0, row['AÑO'], celda)
                ws.write(r + 10, 1, row['Casos'], celda)

            chart1 = wb.add_chart({'type': 'column'})
            chart1.add_series({
                'name': 'Casos',
                'categories': f'=RESUMEN!$A$11:$A${10 + len(data_año)}',
                'values': f'=RESUMEN!$B$11:$B${10 + len(data_año)}',
                'fill': {'color': azul},
                'border': {'color': azul},
                'data_labels': {'value': True}
            })
            chart1.set_title({'name': 'Casos por AÑO'})
            chart1.set_x_axis({'name': 'AÑO'})
            chart1.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            chart1.set_legend({'none': True})
            chart1.set_style(10)
            chart1.set_size({'width': 650, 'height': 350})
            ws.insert_chart('D10', chart1, {'object_position': 1})

            ws.merge_range('A25:H25', 'DISTRIBUCIÓN POR SEXO', seccion)
            ws.write('A26', 'SEXO', encabezado)
            ws.write('B26', 'Casos', encabezado)

            for r, row in data_sexo.iterrows():
                ws.write(r + 26, 0, row['SEXO'], celda)
                ws.write(r + 26, 1, row['Casos'], celda)

            chart2 = wb.add_chart({'type': 'doughnut'})
            chart2.add_series({
                'name': 'Sexo',
                'categories': f'=RESUMEN!$A$27:$A${26 + len(data_sexo)}',
                'values': f'=RESUMEN!$B$27:$B${26 + len(data_sexo)}',
                'points': [
                    {'fill': {'color': celeste}},
                    {'fill': {'color': rosado}}
                ],
                'data_labels': {'percentage': True, 'category': True}
            })
            chart2.set_title({'name': 'Distribución por SEXO'})
            chart2.set_legend({'position': 'bottom'})
            chart2.set_style(10)
            chart2.set_size({'width': 550, 'height': 340})
            ws.insert_chart('D26', chart2, {'object_position': 1})

            ws.set_column('A:A', 22)
            ws.set_column('B:B', 14)
            ws.set_column('C:C', 3)
            ws.set_column('D:H', 15)

            # ========================================================
            # HOJA 2 - TABLA 1 DETALLADA
            # ========================================================
            s1 = 'TABLA_1_DETALLE'
            df_exp.to_excel(writer, sheet_name=s1, index=False, startrow=3)
            ws1 = writer.sheets[s1]
            ws1.hide_gridlines(2)
            ws1.set_zoom(90)
            ws1.set_tab_color(azul_oscuro)

            ws1.set_row(0, 30)
            ws1.merge_range(
                0, 0, 0, len(columnas_finales) - 1,
                'TABLA 1 — CASOS DE TUBERCULOSIS DETALLADO',
                titulo
            )
            ws1.merge_range(
                1, 0, 1, len(columnas_finales) - 1,
                f'Filtros: Año = {año_sel}  |  Provincia = {prov_sel}  |  Establecimiento = {estab_sel}  |  Total = {total}',
                subtitulo
            )
            ws1.merge_range(
                2, 0, 2, len(columnas_finales) - 1,
                f'Archivos utilizados: {len(lista_df)} de {len(archivos)}',
                nota
            )

            for c, v in enumerate(df_exp.columns):
                ws1.write(3, c, v, encabezado)

            for r in range(len(df_exp)):
                for c in range(len(df_exp.columns)):
                    val = df_exp.iloc[r, c]
                    ws1.write(r + 4, c, val, texto if isinstance(val, str) else celda)

            ws1.autofilter(3, 0, len(df_exp) + 3, len(df_exp.columns) - 1)
            ws1.set_row(3, 32)
            ws1.set_column('A:A', 10)
            ws1.set_column('B:D', 22)
            ws1.set_column('E:E', 13)
            ws1.set_column('F:F', 10)
            ws1.set_column('G:G', 24)
            ws1.set_column('H:I', 22)

            # ========================================================
            # HOJA 3 - TIPO DE TUBERCULOSIS
            # ========================================================
            s_tipo = 'TIPO_TUBERCULOSIS'
            data_tipo.to_excel(writer, sheet_name=s_tipo, index=False, startrow=3)
            ws_tipo = writer.sheets[s_tipo]
            ws_tipo.hide_gridlines(2)
            ws_tipo.set_tab_color(naranja)

            ws_tipo.merge_range('A1:F1', 'TIPO DE TUBERCULOSIS', titulo)
            ws_tipo.merge_range(
                'A2:F2',
                f'Correspondiente a los filtros seleccionados — Total: {total} casos',
                subtitulo
            )
            ws_tipo.write('A4', data_tipo.columns[0], encabezado)
            ws_tipo.write('B4', data_tipo.columns[1], encabezado)

            for r in range(len(data_tipo)):
                ws_tipo.write(r + 4, 0, data_tipo.iloc[r, 0], texto)
                ws_tipo.write(r + 4, 1, data_tipo.iloc[r, 1], celda)

            chart_tipo = wb.add_chart({'type': 'column'})
            chart_tipo.add_series({
                'name': 'Casos',
                'categories': f'=TIPO_TUBERCULOSIS!$A$5:$A${4 + len(data_tipo)}',
                'values': f'=TIPO_TUBERCULOSIS!$B$5:$B${4 + len(data_tipo)}',
                'fill': {'color': naranja},
                'border': {'color': naranja},
                'data_labels': {'value': True}
            })
            chart_tipo.set_title({'name': 'TIPO DE TUBERCULOSIS'})
            chart_tipo.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            chart_tipo.set_legend({'none': True})
            chart_tipo.set_style(10)
            chart_tipo.set_size({'width': 650, 'height': 350})
            ws_tipo.insert_chart('D4', chart_tipo, {'object_position': 1})
            ws_tipo.set_column('A:A', 32)
            ws_tipo.set_column('B:B', 14)
            ws_tipo.set_column('C:C', 3)
            ws_tipo.set_column('D:H', 15)

            # ========================================================
            # HOJA 4 - GRUPO ETARIO
            # ========================================================
            s2 = 'GRUPO_ETARIO'
            tabla_etario_det.to_excel(writer, sheet_name=s2, index=False, startrow=3)
            ws2 = writer.sheets[s2]
            ws2.hide_gridlines(2)
            ws2.set_tab_color('#8BC34A')

            ws2.merge_range('A1:H1', 'TABLA 2 — GRUPO ETARIO', titulo)
            ws2.merge_range(
                'A2:H2',
                'NIÑO, ADOLESCENTE, JOVEN, ADULTO Y ADULTO MAYOR',
                subtitulo
            )
            for c, v in enumerate(tabla_etario_det.columns):
                ws2.write(3, c, v, encabezado)
            for r in range(len(tabla_etario_det)):
                for c in range(len(tabla_etario_det.columns)):
                    ws2.write(r + 4, c, tabla_etario_det.iloc[r, c], celda)

            ws2.set_column('A:A', 28)
            ws2.set_column('B:D', 14)

            chart_et = wb.add_chart({'type': 'bar'})
            chart_et.add_series({
                'name': 'TOTAL',
                'categories': f'=GRUPO_ETARIO!$A$5:$A${4 + len(tabla_etario)}',
                'values': f'=GRUPO_ETARIO!$D$5:$D${4 + len(tabla_etario)}',
                'fill': {'color': verde},
                'border': {'color': verde},
                'data_labels': {'value': True}
            })
            chart_et.set_title({'name': 'Casos por Grupo Etario (Barras)'})
            chart_et.set_x_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            chart_et.set_legend({'none': True})
            chart_et.set_style(10)
            chart_et.set_size({'width': 680, 'height': 380})
            ws2.insert_chart('F4', chart_et, {'object_position': 1})

            # ========================================================
            # HOJA 5 - DATOS POR AÑO
            # ========================================================
            s3 = 'POR_AÑO'
            data_año.to_excel(writer, sheet_name=s3, index=False, startrow=3)
            ws3 = writer.sheets[s3]
            ws3.hide_gridlines(2)
            ws3.set_tab_color(azul)
            ws3.merge_range('A1:F1', 'DATOS — CASOS POR AÑO', titulo)
            ws3.merge_range(
                'A2:F2',
                'Datos utilizados para reproducir el gráfico mostrado en el sistema',
                subtitulo
            )
            for c, v in enumerate(data_año.columns):
                ws3.write(3, c, v, encabezado)
            for r in range(len(data_año)):
                for c in range(len(data_año.columns)):
                    ws3.write(r + 4, c, data_año.iloc[r, c], celda)
            ws3.set_column('A:A', 14)
            ws3.set_column('B:B', 14)

        return output.getvalue()

    def to_pdf_3d():
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=30, leftMargin=30, topMargin=38, bottomMargin=42
        )

        styles = getSampleStyleSheet()
        titulo_pdf = ParagraphStyle(
            'TituloPDF', parent=styles['Heading1'], fontSize=15,
            leading=19, textColor=colors.HexColor('#1c2e4a'),
            alignment=1, spaceAfter=4
        )
        subtitulo_pdf = ParagraphStyle(
            'SubPDF', parent=styles['Normal'], fontSize=8.5,
            leading=11, textColor=colors.HexColor('#64748B'),
            alignment=1, spaceAfter=8
        )
        h2 = ParagraphStyle(
            'H2PDF', parent=styles['Heading2'], fontSize=10.5,
            leading=13, textColor=colors.HexColor('#1c2e4a'),
            spaceBefore=8, spaceAfter=5
        )
        desc = ParagraphStyle(
            'DescPDF', parent=styles['Normal'], fontSize=8.2,
            leading=11.5, textColor=colors.HexColor('#334155'),
            backColor=colors.HexColor('#F8FAFC'),
            borderPadding=6, spaceAfter=7
        )
        story = []

        # ----- ENCABEZADO -----
        story.append(Paragraph(
            '<b>ANÁLISIS NOTIWEB 2026 — TUBERCULOSIS</b><br/>'
            '<b>RED DE SALUD HUAMALIES — UE 405</b>',
            titulo_pdf
        ))
        story.append(Paragraph(
            f'Año: <b>{año_sel}</b> &nbsp;|&nbsp; '
            f'Provincia: <b>{prov_sel}</b> &nbsp;|&nbsp; '
            f'Establecimiento: <b>{estab_sel}</b><br/>'
            f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")} '
            f'&nbsp;|&nbsp; Archivos: {len(lista_df)} de {len(archivos)}',
            subtitulo_pdf
        ))

        # ----- INDICADORES -----
        kpi = Table([
            ['TOTAL DE CASOS', 'ARCHIVOS LEÍDOS', 'AÑO'],
            [str(total), str(len(lista_df)), str(año_sel)]
        ], colWidths=[170, 170, 170], rowHeights=[20, 28])
        kpi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D9E1F2')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1c2e4a')),
            ('BACKGROUND', (0,1), (-1,1), colors.white),
            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#B8C4D3')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D7DE')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('FONTSIZE', (0,1), (-1,1), 15),
        ]))
        story.append(kpi)
        story.append(Spacer(1, 7))

        # ----- DESCRIPCIÓN -----
        grupo_top = tabla_etario.iloc[0]['GRUPO_ETARIO'] if not tabla_etario.empty else 'S/D'
        grupo_top_n = tabla_etario.iloc[0]['TOTAL'] if not tabla_etario.empty else 0

        story.append(Paragraph(
            f'<b>Descripción del reporte:</b> Se registraron <b>{total} casos</b> '
            f'de tuberculosis según los filtros seleccionados. El grupo etario '
            f'con mayor número de registros es <b>{grupo_top}</b>, con '
            f'<b>{grupo_top_n} casos</b>. El presente informe conserva la '
            f'información mostrada en el módulo y presenta sus tablas y gráficos '
            f'para facilitar la revisión y presentación institucional.',
            desc
        ))

        # ----- TABLA 1 -----
        story.append(Paragraph('1. TABLA 1 — CASOS DE TUBERCULOSIS DETALLADO', h2))
        data = [list(columnas_finales)]
        for _, r in df_f.head(25).iterrows():
            data.append([str(r.get(c, ''))[:18] for c in columnas_finales])

        # Si hay muchas columnas, mantenerlas legibles.
        ancho_total = 535
        ancho = ancho_total / max(len(columnas_finales), 1)
        t = Table(data, colWidths=[ancho] * len(columnas_finales), repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1c2e4a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.35, colors.HexColor('#CBD5E1')),
            ('FONTSIZE', (0,0), (-1,-1), 5.4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.white, colors.HexColor('#F3F4F6')]),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t)
        story.append(Paragraph(
            f'Se muestran los primeros {min(25, len(df_f))} registros como vista resumida. '
            f'El Excel contiene el detalle completo de los {total} casos.',
            desc
        ))

        # ----- GRÁFICO AÑO -----
        story.append(Paragraph('2. GRÁFICO — CASOS POR AÑO', h2))
        fig, ax = plt.subplots(figsize=(5.5, 2.3))
        ax.bar(data_año['AÑO'].astype(str), data_año['Casos'], color='#4472C4')
        ax.set_title('Casos por AÑO', fontsize=10, fontweight='bold')
        ax.set_xlabel('AÑO', fontsize=8)
        ax.set_ylabel('Casos', fontsize=8)
        ax.tick_params(axis='both', labelsize=7)
        ax.spines[['top','right']].set_visible(False)
        for i, v in enumerate(data_año['Casos']):
            ax.text(i, v, str(v), ha='center', va='bottom', fontsize=7)
        plt.tight_layout()
        img1 = BytesIO()
        plt.savefig(img1, format='png', dpi=170, bbox_inches='tight')
        plt.close()
        img1.seek(0)
        story.append(Image(img1, width=430, height=180))
        story.append(Paragraph(
            'Descripción: este gráfico representa la cantidad de casos registrados '
            'por año, manteniendo el mismo conjunto de datos utilizado en el sistema.',
            desc
        ))

        # ----- SEXO -----
        story.append(Paragraph('3. GRÁFICO — DISTRIBUCIÓN POR SEXO', h2))
        fig, ax = plt.subplots(figsize=(4.8, 2.4))
        vals = data_sexo['Casos'].tolist()
        labels = data_sexo['SEXO'].tolist()
        ax.pie(
            vals, labels=labels, autopct='%1.1f%%',
            colors=['#0EA5E9', '#FF6FB5'][:len(vals)],
            startangle=90,
            wedgeprops={'width': 0.38}
        )
        ax.set_title('Distribución por SEXO', fontsize=10, fontweight='bold')
        plt.tight_layout()
        img2 = BytesIO()
        plt.savefig(img2, format='png', dpi=170, bbox_inches='tight')
        plt.close()
        img2.seek(0)
        story.append(Image(img2, width=350, height=175))
        story.append(Paragraph(
            'Descripción: muestra proporcionalmente la distribución de los casos '
            'entre masculino y femenino según los registros filtrados.',
            desc
        ))

        # ----- TIPO TB -----
        story.append(Paragraph('4. GRÁFICO — TIPO DE TUBERCULOSIS', h2))
        fig, ax = plt.subplots(figsize=(5.5, 2.3))
        ax.bar(
            data_tipo['TIPO DE TUBERCULOSIS'].astype(str),
            data_tipo['Casos'],
            color='#FF8C00'
        )
        ax.set_title('TIPO DE TUBERCULOSIS', fontsize=10, fontweight='bold')
        ax.tick_params(axis='x', labelrotation=25, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.spines[['top','right']].set_visible(False)
        for i, v in enumerate(data_tipo['Casos']):
            ax.text(i, v, str(v), ha='center', va='bottom', fontsize=7)
        plt.tight_layout()
        img3 = BytesIO()
        plt.savefig(img3, format='png', dpi=170, bbox_inches='tight')
        plt.close()
        img3.seek(0)
        story.append(Image(img3, width=430, height=180))
        story.append(Paragraph(
            'Descripción: presenta los casos agrupados según el tipo de tuberculosis '
            'registrado en la base filtrada.',
            desc
        ))

        # ----- GRUPO ETARIO -----
        story.append(Paragraph('5. TABLA 2 — GRUPO ETARIO', h2))
        data_et = [['GRUPO ETARIO', 'MASCULINO', 'FEMENINO', 'TOTAL']]
        for _, r in tabla_etario_det.iterrows():
            data_et.append([
                str(r.get('GRUPO_ETARIO', '')),
                str(r.get('Masculino', 0)),
                str(r.get('Femenino', 0)),
                str(r.get('TOTAL', 0))
            ])
        te = Table(data_et, colWidths=[220, 90, 90, 90], repeatRows=1)
        te.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1c2e4a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.35, colors.HexColor('#CBD5E1')),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.white, colors.HexColor('#F3F4F6')]),
        ]))
        story.append(te)

        fig, ax = plt.subplots(figsize=(5.5, 2.4))
        et = tabla_etario.sort_values('TOTAL')
        ax.barh(et['GRUPO_ETARIO'], et['TOTAL'], color='#90EE90')
        ax.set_title('Casos por Grupo Etario (Barras)', fontsize=10, fontweight='bold')
        ax.tick_params(axis='y', labelsize=7)
        ax.tick_params(axis='x', labelsize=7)
        ax.spines[['top','right']].set_visible(False)
        for i, v in enumerate(et['TOTAL']):
            ax.text(v, i, f' {v}', va='center', fontsize=7)
        plt.tight_layout()
        img4 = BytesIO()
        plt.savefig(img4, format='png', dpi=170, bbox_inches='tight')
        plt.close()
        img4.seek(0)
        story.append(Image(img4, width=430, height=185))
        story.append(Paragraph(
            f'Descripción: el grupo con mayor registro es <b>{grupo_top}</b> '
            f'con <b>{grupo_top_n} casos</b>. La tabla y gráfico permiten identificar '
            f'rápidamente la concentración por edad.',
            desc
        ))

        # ----- PIE DE PÁGINA -----
        def pie_pagina(canvas, doc):
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor('#CBD5E1'))
            canvas.line(30, 30, A4[0] - 30, 30)
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#64748B'))
            canvas.drawString(
                30, 19,
                'ANÁLISIS NOTIWEB 2026 — TUBERCULOSIS — RED DE SALUD HUAMALIES UE 405'
            )
            canvas.drawRightString(A4[0] - 30, 19, f'Página {doc.page}')
            canvas.restoreState()

        doc.build(story, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
        return buffer.getvalue()

    # Botones: SOLO 2 descargas, como solicitó el usuario.
    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "📊 DESCARGAR EXCEL",
            data=to_excel_pro(),
            file_name=f"TUBERCULOSIS_PRO_{año_sel}_{prov_sel}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

    with c2:
        st.download_button(
            "📄 DESCARGAR PDF",
            data=to_pdf_3d(),
            file_name=f"TUBERCULOSIS_INFORME_{año_sel}_{prov_sel}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
