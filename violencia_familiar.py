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
    df['MOTIVO'] = df.apply(obtener_tipo_buaso, axis=1)
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

# ============================================================
    # DESCARGAS — VIOLENCIA FAMILIAR
    # Se conserva TODO lo que aparece en el sistema:
    #   TABLA 1 + TABLA 2 + 5 GRÁFICOS.
    # Se mantienen únicamente las hojas que ya utiliza el módulo:
    #   DATOS y GRUPO_ETARIO.
    # NO se modifica lectura, filtros ni cálculos.
    # NO se congelan paneles.
    # ============================================================

    def _vf_write_df(ws, df, startrow, hdr, cell):
        for c, v in enumerate(df.columns):
            ws.write(startrow, c, str(v), hdr)
        for r in range(len(df)):
            for c in range(len(df.columns)):
                ws.write(startrow + 1 + r, c, df.iloc[r, c], cell)

    def to_excel_pro():
        output = BytesIO()

        df_datos = df_f[columnas_finales].replace(
            [np.inf, -np.inf], np.nan
        ).fillna('')
        df_grupo = tabla_grupo.replace(
            [np.inf, -np.inf], np.nan
        ).fillna(0)

        with pd.ExcelWriter(
            output,
            engine='xlsxwriter',
            engine_kwargs={'options': {'nan_inf_to_errors': True}}
        ) as writer:

            wb = writer.book

            title = wb.add_format({
                'bold': True, 'font_size': 15, 'font_color': 'white',
                'bg_color': '#1C2E4A', 'align': 'left', 'valign': 'vcenter'
            })
            sub = wb.add_format({
                'bold': True, 'font_size': 10, 'font_color': '#1C2E4A',
                'bg_color': '#D9E1F2', 'align': 'left', 'valign': 'vcenter'
            })
            sec = wb.add_format({
                'bold': True, 'font_size': 11, 'font_color': 'white',
                'bg_color': '#4472C4', 'align': 'left', 'valign': 'vcenter'
            })
            hdr = wb.add_format({
                'bold': True, 'bg_color': '#1C2E4A', 'font_color': 'white',
                'border': 1, 'align': 'center', 'valign': 'vcenter',
                'text_wrap': True
            })
            cell = wb.add_format({
                'border': 1, 'align': 'center', 'valign': 'vcenter'
            })
            cell_red = wb.add_format({
                'border': 1, 'align': 'center', 'valign': 'vcenter',
                'bg_color': '#FFCCCB'
            })

            # ----------------------------------------------------
            # HOJA EXISTENTE 1 — DATOS
            # Tabla 1 + gráficos 1, 2 y 5
            # ----------------------------------------------------
            df_datos.to_excel(writer, sheet_name='DATOS',
                              index=False, startrow=5)
            ws = writer.sheets['DATOS']
            ws.hide_gridlines(2)
            ws.set_zoom(80)

            ws.merge_range(
                0, 0, 0, max(0, len(df_datos.columns)-1),
                'MÓDULO VIOLENCIA FAMILIAR — ANÁLISIS NOTIWEB',
                title
            )
            ws.merge_range(
                1, 0, 1, max(0, len(df_datos.columns)-1),
                f'Año: {año_sel} | Provincia: {prov_sel} | '
                f'Distrito: {dist_sel} | Total: {total} casos | '
                f'Archivos: {len(lista_df)} | '
                f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                sub
            )
            ws.merge_range(
                3, 0, 3, min(max(0, len(df_datos.columns)-1), 9),
                'TABLA 1 — CASOS DE VIOLENCIA FAMILIAR',
                sec
            )

            for c, v in enumerate(df_datos.columns):
                ws.write(5, c, str(v), hdr)
            for r in range(len(df_datos)):
                for c in range(len(df_datos.columns)):
                    valor = df_datos.iloc[r, c]
                    es_muerte = (
                        'MUERTES' in df_datos.columns
                        and str(df_datos.iloc[r]['MUERTES']) == 'Sí'
                    )
                    ws.write(r + 6, c, valor, cell_red if es_muerte else cell)

            ws.set_column(0, max(0, len(df_datos.columns)-1), 17)
            ws.autofilter(
                5, 0, len(df_datos)+5,
                max(0, len(df_datos.columns)-1)
            )

            # ---------------- GRÁFICO 1: AÑO ----------------
            fila = len(df_datos) + 9
            ws.merge_range(
                fila, 0, fila, min(max(0, len(df_datos.columns)-1), 9),
                'GRÁFICO 1 — CASOS POR AÑO',
                sec
            )
            aux = fila + 2
            ws.write(aux, 0, 'AÑO', hdr)
            ws.write(aux, 1, 'Casos', hdr)
            for i, (_, r) in enumerate(data_año.iterrows(), start=aux+1):
                ws.write(i, 0, str(r['AÑO']), cell)
                ws.write(i, 1, int(r['Casos']), cell)

            ch1 = wb.add_chart({'type': 'column'})
            n = len(data_año)
            if n:
                ch1.add_series({
                    'name': 'Casos',
                    'categories': f"='DATOS'!$A${aux+2}:$A${aux+n+1}",
                    'values': f"='DATOS'!$B${aux+2}:$B${aux+n+1}",
                    'fill': {'color': '#4472C4'},
                    'border': {'color': '#4472C4'},
                    'data_labels': {'value': True}
                })
            ch1.set_title({'name': 'Casos por AÑO'})
            ch1.set_legend({'none': True})
            ch1.set_x_axis({'name': 'Año'})
            ch1.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            ch1.set_style(10)
            ch1.set_size({'width': 620, 'height': 320})
            ws.insert_chart(aux, 3, ch1, {'object_position': 1})

            # ---------------- GRÁFICO 2: TIPO ----------------
            data_tipo_excel = data_tipo.copy()
            fila2 = aux + max(n, 1) + 14
            ws.merge_range(
                fila2, 0, fila2, min(max(0, len(df_datos.columns)-1), 9),
                'GRÁFICO 2 — TIPO DE VIOLENCIA',
                sec
            )
            aux2 = fila2 + 2
            ws.write(aux2, 0, 'TIPO DE VIOLENCIA', hdr)
            ws.write(aux2, 1, 'Casos', hdr)
            for i, (_, r) in enumerate(data_tipo_excel.iterrows(), start=aux2+1):
                ws.write(i, 0, str(r['TIPO DE VIOLENCIA']), cell)
                ws.write(i, 1, int(r['Casos']), cell)

            ch2 = wb.add_chart({'type': 'column'})
            n2 = len(data_tipo_excel)
            colores_tipo = {
                'Psicológica': '#1F77B4',
                'Física': '#7BC043',
                'Sexual': '#FF0000',
                'Abandono': '#FFFF00',
                'Propio Cuerpo': '#FF8C00'
            }
            puntos2 = [
                {'fill': {'color': colores_tipo.get(str(x), '#808080')}}
                for x in data_tipo_excel['TIPO DE VIOLENCIA']
            ]
            if n2:
                ch2.add_series({
                    'name': 'Casos',
                    'categories': f"='DATOS'!$A${aux2+2}:$A${aux2+n2+1}",
                    'values': f"='DATOS'!$B${aux2+2}:$B${aux2+n2+1}",
                    'points': puntos2,
                    'data_labels': {'value': True}
                })
            ch2.set_title({'name': 'TIPO DE VIOLENCIA'})
            ch2.set_legend({'none': True})
            ch2.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            ch2.set_style(10)
            ch2.set_size({'width': 620, 'height': 320})
            ws.insert_chart(aux2, 3, ch2, {'object_position': 1})

            # ---------------- GRÁFICO 5: TORTA ----------------
            fila5 = aux2 + max(n2, 1) + 14
            ws.merge_range(
                fila5, 0, fila5, min(max(0, len(df_datos.columns)-1), 9),
                'GRÁFICO 5 — DISTRIBUCIÓN TIPO DE VIOLENCIA',
                sec
            )
            aux5 = fila5 + 2
            ws.write(aux5, 0, 'TIPO DE VIOLENCIA', hdr)
            ws.write(aux5, 1, 'Casos', hdr)
            for i, (_, r) in enumerate(data_torta.iterrows(), start=aux5+1):
                ws.write(i, 0, str(r['TIPO DE VIOLENCIA']), cell)
                ws.write(i, 1, int(r['Casos']), cell)

            ch5 = wb.add_chart({'type': 'pie'})
            n5 = len(data_torta)
            colores_torta = {
                'Psicológica': '#1F77B4',
                'Física': '#7BC043',
                'Sexual': '#FF0000',
                'Abandono': '#FFFF00',
                'Propio Cuerpo': '#FF8C00',
                'Arma de Fuego': '#8B0000',
                'Arma Blanca': '#DC143C',
                'Objeto Contundente': '#A0522D',
                'Otros': '#808080'
            }
            puntos5 = [
                {'fill': {'color': colores_torta.get(str(x), '#808080')}}
                for x in data_torta['TIPO DE VIOLENCIA']
            ]
            if n5:
                ch5.add_series({
                    'name': 'Casos',
                    'categories': f"='DATOS'!$A${aux5+2}:$A${aux5+n5+1}",
                    'values': f"='DATOS'!$B${aux5+2}:$B${aux5+n5+1}",
                    'points': puntos5,
                    'data_labels': {'percentage': True, 'category': True}
                })
            ch5.set_title({
                'name': f'{prov_sel if prov_sel != "TODAS" else "HUACAYBAMBA"} '
                        f'{año_sel if año_sel != "TODOS" else "(2021-2026)"}'
            })
            ch5.set_legend({'position': 'right'})
            ch5.set_style(10)
            ch5.set_size({'width': 620, 'height': 360})
            ws.insert_chart(aux5, 3, ch5, {'object_position': 1})

            # ----------------------------------------------------
            # HOJA EXISTENTE 2 — GRUPO_ETARIO
            # Tabla 2 + gráficos 3 y 4
            # ----------------------------------------------------
            df_grupo.to_excel(writer, sheet_name='GRUPO_ETARIO',
                              index=False, startrow=5)
            ws2 = writer.sheets['GRUPO_ETARIO']
            ws2.hide_gridlines(2)
            ws2.set_zoom(90)
            ws2.merge_range(
                0, 0, 0, max(1, len(df_grupo.columns)-1),
                'MÓDULO VIOLENCIA FAMILIAR — TABLA 2',
                title
            )
            ws2.merge_range(
                1, 0, 1, max(1, len(df_grupo.columns)-1),
                f'Año: {año_sel} | Provincia: {prov_sel} | '
                f'Distrito: {dist_sel} | Total: {total} casos',
                sub
            )
            ws2.merge_range(
                3, 0, 3, max(1, len(df_grupo.columns)-1),
                'TABLA 2 — CASOS POR GRUPO ETARIO Y SEXO',
                sec
            )
            _vf_write_df(ws2, df_grupo, 5, hdr, cell)
            ws2.set_column(0, max(0, len(df_grupo.columns)-1), 18)
            ws2.set_column(0, 0, 28)

            # Gráfico 3
            fila3 = len(df_grupo) + 9
            ws2.merge_range(
                fila3, 0, fila3, max(1, len(df_grupo.columns)-1),
                'GRÁFICO 3 — CASOS POR GRUPO ETARIO Y SEXO',
                sec
            )
            aux3 = fila3 + 2
            ws2.write(aux3, 0, 'SEXO', hdr)
            grupos = orden_grupos
            for j, g in enumerate(grupos, start=1):
                ws2.write(aux3, j, str(g), hdr)

            for i, sexo in enumerate(sorted(data_grupo_sexo['SEXO'].dropna().unique()), start=aux3+1):
                ws2.write(i, 0, str(sexo), cell)
                for j, g in enumerate(grupos, start=1):
                    m = data_grupo_sexo[
                        (data_grupo_sexo['SEXO'] == sexo) &
                        (data_grupo_sexo['GRUPO ETARIO'] == g)
                    ]
                    valor = int(m['Casos'].iloc[0]) if not m.empty else 0
                    ws2.write(i, j, valor, cell)

            ch3 = wb.add_chart({'type': 'column'})
            sexos = sorted(data_grupo_sexo['SEXO'].dropna().unique())
            for idx_s, sexo in enumerate(sexos):
                color_map3 = {
                    '0-11 NIÑO/A': '#87CEEB',
                    '12-17 ADOLESCENTE': '#90EE90',
                    '18-29 JOVEN': '#FF0000',
                    '30-59 ADULTO/A': '#FFFF00',
                    '60+ ADULTO MAYOR': '#9370DB'
                }
                # En Excel cada serie representa un grupo etario.
            for j, g in enumerate(grupos, start=1):
                color = {
                    '0-11 NIÑO/A': '#87CEEB',
                    '12-17 ADOLESCENTE': '#90EE90',
                    '18-29 JOVEN': '#FF0000',
                    '30-59 ADULTO/A': '#FFFF00',
                    '60+ ADULTO MAYOR': '#9370DB'
                }.get(g, '#808080')
                ch3.add_series({
                    'name': str(g),
                    'categories': f"='GRUPO_ETARIO'!$A${aux3+2}:$A${aux3+1+len(sexos)}",
                    'values': f"='GRUPO_ETARIO'!${chr(65+j)}${aux3+2}:${chr(65+j)}${aux3+1+len(sexos)}",
                    'fill': {'color': color},
                    'data_labels': {'value': True}
                })
            ch3.set_title({'name': titulo_dinamico})
            ch3.set_x_axis({'name': 'Sexo'})
            ch3.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            ch3.set_style(10)
            ch3.set_size({'width': 650, 'height': 350})
            ws2.insert_chart(aux3, 7, ch3, {'object_position': 1})

            # Gráfico 4
            fila4 = aux3 + max(len(sexos), 1) + 15
            ws2.merge_range(
                fila4, 0, fila4, max(1, len(df_grupo.columns)-1),
                'GRÁFICO 4 — CASOS POR GRUPO ETARIO',
                sec
            )
            aux4 = fila4 + 2
            ws2.write(aux4, 0, 'GRUPO ETARIO', hdr)
            ws2.write(aux4, 1, 'FEMENINO', hdr)
            ws2.write(aux4, 2, 'MASCULINO', hdr)

            for i, g in enumerate(orden_grupos, start=aux4+1):
                ws2.write(i, 0, str(g), cell)
                mf = data_grupo_sexo[
                    (data_grupo_sexo['GRUPO ETARIO'] == g) &
                    (data_grupo_sexo['SEXO'] == 'FEMENINO')
                ]
                mm = data_grupo_sexo[
                    (data_grupo_sexo['GRUPO ETARIO'] == g) &
                    (data_grupo_sexo['SEXO'] == 'MASCULINO')
                ]
                ws2.write(i, 1, int(mf['Casos'].iloc[0]) if not mf.empty else 0, cell)
                ws2.write(i, 2, int(mm['Casos'].iloc[0]) if not mm.empty else 0, cell)

            ch4 = wb.add_chart({'type': 'column'})
            ch4.add_series({
                'name': 'FEMENINO',
                'categories': f"='GRUPO_ETARIO'!$A${aux4+2}:$A${aux4+1+len(orden_grupos)}",
                'values': f"='GRUPO_ETARIO'!$B${aux4+2}:$B${aux4+1+len(orden_grupos)}",
                'fill': {'color': '#FF0000'},
                'data_labels': {'value': True}
            })
            ch4.add_series({
                'name': 'MASCULINO',
                'categories': f"='GRUPO_ETARIO'!$A${aux4+2}:$A${aux4+1+len(orden_grupos)}",
                'values': f"='GRUPO_ETARIO'!$C${aux4+2}:$C${aux4+1+len(orden_grupos)}",
                'fill': {'color': '#00BFFF'},
                'data_labels': {'value': True}
            })
            ch4.set_title({'name': titulo_dinamico})
            ch4.set_x_axis({'name': 'Grupo Etario'})
            ch4.set_y_axis({'name': 'Casos', 'major_gridlines': {'visible': False}})
            ch4.set_style(10)
            ch4.set_size({'width': 650, 'height': 350})
            ws2.insert_chart(aux4, 7, ch4, {'object_position': 1})

        return output.getvalue()

    def to_pdf_completo():
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=30, leftMargin=30,
            topMargin=30, bottomMargin=30
        )
        styles = getSampleStyleSheet()
        title_p = ParagraphStyle(
            'VFTitulo', parent=styles['Heading1'], fontSize=13,
            textColor=colors.HexColor('#1C2E4A'), alignment=1,
            spaceAfter=8
        )
        h2 = ParagraphStyle(
            'VFH2', parent=styles['Heading2'], fontSize=10,
            textColor=colors.HexColor('#1C2E4A'),
            spaceBefore=9, spaceAfter=5
        )
        desc = ParagraphStyle(
            'VFDesc', parent=styles['Normal'], fontSize=8,
            leading=11, textColor=colors.HexColor('#334155'),
            backColor=colors.HexColor('#F8FAFC'),
            borderPadding=6, spaceAfter=7
        )

        story = [
            Paragraph(
                f"<b>ANÁLISIS NOTIWEB — VIOLENCIA FAMILIAR</b><br/>"
                f"Año: {año_sel} | Provincia: {prov_sel} | Distrito: {dist_sel}<br/>"
                f"Total: <b>{total}</b> casos | Archivos: {len(lista_df)} | "
                f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                title_p
            )
        ]

        # 1. Tabla 1
        story.append(Paragraph("<b>1. TABLA 1 — CASOS DE VIOLENCIA FAMILIAR</b>", h2))
        cols = list(columnas_finales)
        data = [[str(c)[:18] for c in cols]]
        for _, r in df_f[cols].iterrows():
            data.append([str(r.get(c, ''))[:18] for c in cols])
        ancho = max(28, (A4[0] - 60) / max(1, len(cols)))
        t = Table(data, colWidths=[ancho] * len(cols), repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1C2E4A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#B8C0CC')),
            ('FONTSIZE', (0,0), (-1,-1), 5.2),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(t)
        story.append(Paragraph(
            f"La tabla reproduce los registros del sistema para los filtros seleccionados. "
            f"Total: <b>{total}</b> casos.",
            desc
        ))

        # 2. Tabla 2
        story.append(Paragraph("<b>2. TABLA 2 — CASOS POR GRUPO ETARIO</b>", h2))
        data2 = [list(map(str, tabla_grupo.reset_index().columns))]
        for _, r in tabla_grupo.reset_index().iterrows():
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

        # Gráfico 1
        fig, ax = plt.subplots(figsize=(6, 2.5))
        ax.bar(data_año['AÑO'].astype(str), data_año['Casos'], color='#4472C4')
        ax.set_title('Casos por AÑO', fontsize=10)
        ax.set_ylabel('Casos', fontsize=8)
        ax.tick_params(labelsize=7)
        for i, v in enumerate(data_año['Casos']):
            ax.text(i, v, str(v), ha='center', va='bottom', fontsize=7)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        b1 = BytesIO()
        plt.savefig(b1, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b1.seek(0)
        story += [
            Paragraph("<b>3. GRÁFICO 1 — CASOS POR AÑO</b>", h2),
            Image(b1, width=430, height=180),
            Paragraph(
                "Interpretación: permite observar cómo se distribuyen los casos "
                "registrados por año en el sistema.",
                desc
            )
        ]

        # Gráfico 2
        fig, ax = plt.subplots(figsize=(6, 2.7))
        dt = data_tipo.copy()
        cmap = {
            'Psicológica': '#1F77B4',
            'Física': '#7BC043',
            'Sexual': '#FF0000',
            'Abandono': '#FFFF00',
            'Propio Cuerpo': '#FF8C00'
        }
        ax.bar(
            dt['TIPO DE VIOLENCIA'].astype(str),
            dt['Casos'],
            color=[cmap.get(str(x), '#808080') for x in dt['TIPO DE VIOLENCIA']]
        )
        ax.set_title('TIPO DE VIOLENCIA', fontsize=10)
        ax.set_ylabel('Casos', fontsize=8)
        ax.tick_params(axis='x', labelrotation=20, labelsize=6)
        for i, v in enumerate(dt['Casos']):
            ax.text(i, v, str(v), ha='center', va='bottom', fontsize=6)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        b2 = BytesIO()
        plt.savefig(b2, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b2.seek(0)
        story += [
            Paragraph("<b>4. GRÁFICO 2 — TIPO DE VIOLENCIA</b>", h2),
            Image(b2, width=430, height=195),
            Paragraph(
                "Interpretación: compara los tipos de violencia registrados y "
                "permite identificar cuáles concentran mayor número de casos.",
                desc
            )
        ]

        # Gráfico 3
        fig, ax = plt.subplots(figsize=(6, 2.8))
        for g in orden_grupos:
            subdf = data_grupo_sexo[data_grupo_sexo['GRUPO ETARIO'] == g]
            if not subdf.empty:
                ax.bar(
                    subdf['SEXO'].astype(str),
                    subdf['Casos'],
                    label=g
                )
        ax.set_title(titulo_dinamico, fontsize=10)
        ax.set_ylabel('Casos', fontsize=8)
        ax.tick_params(labelsize=7)
        ax.legend(fontsize=5, ncol=2)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        b3 = BytesIO()
        plt.savefig(b3, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b3.seek(0)
        story += [
            Paragraph("<b>5. GRÁFICO 3 — CASOS POR GRUPO ETARIO Y SEXO</b>", h2),
            Image(b3, width=430, height=200),
            Paragraph(
                "Interpretación: cruza sexo y grupo etario para mostrar la "
                "distribución de los casos en cada grupo.",
                desc
            )
        ]

        # Gráfico 4
        fig, ax = plt.subplots(figsize=(6, 2.8))
        pivot = data_grupo_sexo.pivot_table(
            index='GRUPO ETARIO', columns='SEXO',
            values='Casos', aggfunc='sum', fill_value=0
        ).reindex(orden_grupos, fill_value=0)
        if 'FEMENINO' in pivot.columns:
            ax.bar(
                pivot.index.astype(str), pivot['FEMENINO'],
                label='FEMENINO', color='#FF0000'
            )
        if 'MASCULINO' in pivot.columns:
            ax.bar(
                pivot.index.astype(str),
                pivot['MASCULINO'],
                bottom=pivot['FEMENINO'] if 'FEMENINO' in pivot.columns else 0,
                label='MASCULINO', color='#00BFFF'
            )
        ax.set_title(titulo_dinamico, fontsize=10)
        ax.set_ylabel('Casos', fontsize=8)
        ax.tick_params(axis='x', labelrotation=15, labelsize=6)
        ax.legend(fontsize=6)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        b4 = BytesIO()
        plt.savefig(b4, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b4.seek(0)
        story += [
            Paragraph("<b>6. GRÁFICO 4 — CASOS POR GRUPO ETARIO</b>", h2),
            Image(b4, width=430, height=200),
            Paragraph(
                "Interpretación: muestra la distribución de los casos por grupo "
                "etario y permite comparar la participación de cada sexo.",
                desc
            )
        ]

        # Gráfico 5
        fig, ax = plt.subplots(figsize=(6, 3.2))
        labels = data_torta['TIPO DE VIOLENCIA'].astype(str).tolist()
        vals = data_torta['Casos'].tolist()
        cmap5 = {
            'Psicológica': '#1F77B4',
            'Física': '#7BC043',
            'Sexual': '#FF0000',
            'Abandono': '#FFFF00',
            'Propio Cuerpo': '#FF8C00',
            'Arma de Fuego': '#8B0000',
            'Arma Blanca': '#DC143C',
            'Objeto Contundente': '#A0522D',
            'Otros': '#808080'
        }
        if vals and sum(vals) > 0:
            ax.pie(
                vals, labels=labels, autopct='%1.1f%%',
                colors=[cmap5.get(x, '#808080') for x in labels],
                startangle=90, textprops={'fontsize': 6}
            )
        ax.set_title(
            f'{prov_sel if prov_sel != "TODAS" else "HUACAYBAMBA"} '
            f'{año_sel if año_sel != "TODOS" else "(2021-2026)"}',
            fontsize=10
        )
        plt.tight_layout()
        b5 = BytesIO()
        plt.savefig(b5, format='png', dpi=180, bbox_inches='tight')
        plt.close()
        b5.seek(0)
        story += [
            Paragraph("<b>7. GRÁFICO 5 — DISTRIBUCIÓN TIPO DE VIOLENCIA</b>", h2),
            Image(b5, width=430, height=225),
            Paragraph(
                "Interpretación: representa proporcionalmente todos los tipos "
                "de violencia registrados por el sistema, incluyendo las "
                "categorías adicionales cuando existen.",
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
            file_name=f"VIOLENCIA_FAMILIAR_COMPLETO_{año_sel}_{prov_sel}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
    with c2:
        st.download_button(
            "📄 DESCARGAR PDF",
            data=to_pdf_completo(),
            file_name=f"VIOLENCIA_FAMILIAR_COMPLETO_{año_sel}_{prov_sel}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
