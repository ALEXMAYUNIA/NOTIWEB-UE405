import streamlit as st
import os

st.set_page_config(page_title="NOTIWEB UE 405 - Huacaybamba", layout="wide", page_icon="🏥", initial_sidebar_state="expanded")

# --- BLOQUEAR QUE EL SIDEBAR SE PUEDA OCULTAR/DESLIZAR ---
st.markdown("""
<style>
/* Oculta el botón X y la flecha > para que nunca se pueda cerrar */
button[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="header"] {
    display: none !important;
}
section[data-testid="stSidebar"] {
    transform: none !important;
    visibility: visible !important;
}
</style>
""", unsafe_allow_html=True)

# --- LOGIN SIMPLE ---
def login():
    st.markdown("<h1 style='text-align:center; color:#1c2e4a;'>🏥 NOTIWEB UE 405 - HUACAYBAMBA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Sistema de Análisis Epidemiológico</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("🔐 Ingreso al sistema - Modo Licenciada y Técnico")
        usuario = st.text_input("Usuario", value="admin", key="user")
        clave = st.text_input("Contraseña", type="password", value="1234", key="pass")
        if st.button("INGRESAR", type="primary", use_container_width=True):
            # Login simple - puedes cambiar usuario/clave
            if (usuario == "admin" and clave == "1234") or (usuario == "licenciada" and clave == "licenciada"):
                st.session_state['logado'] = True
                st.session_state['usuario'] = usuario
                st.rerun()
            else:
                st.error("Usuario o clave incorrecta - Usa admin/1234 o licenciada/licenciada")
        st.caption("Usuario técnico: admin / 1234 | Usuario licenciada: licenciada / licenciada")

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    login()
    st.stop()

# --- APP PRINCIPAL ---
st.sidebar.markdown(f"👤 Usuario: **{st.session_state.get('usuario','')}**")
if st.sidebar.button("Cerrar sesión"):
    st.session_state['logado'] = False
    st.rerun()

st.sidebar.title("📋 MÓDULOS NOTIWEB")
modulo = st.sidebar.selectbox("Selecciona módulo:", [
    "DIABETES - (Excel diferente: tdiabetes, redes)",
    "TUBERCULOSIS - (Excel diferente: ano_fis, localiza1)",
    "VIOLENCIA FAMILIAR - (Excel diferente: fisica, psicol, defuncion)",
    "PLAGUICIDAS",
    "MORTALIDAD MATERNA",
    "LESIONES",
    "MUERTE PERINATAL"
], key="modulo_principal")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Modo Licenciada:** Cada módulo tiene 2 modos:\n📁 Carpeta automática (técnico)\n📤 Subir archivos (arrastra 120 excels)")

# Importar y mostrar modulo seleccionado
try:
    if "DIABETES" in modulo:
        import diabetes
        diabetes.mostrar_pagina()
    elif "TUBERCULOSIS" in modulo:
        import tuberculosis
        tuberculosis.mostrar_pagina()
    elif "VIOLENCIA" in modulo:
        import violencia_familiar
        violencia_familiar.mostrar_pagina()
    else:
        st.warning(f"Módulo {modulo} aún no tiene archivo .py. Crea {modulo.split(' - ')[0].lower().replace(' ', '_')}.py con función mostrar_pagina()")
        st.info("Por ahora usa DIABETES, TUBERCULOSIS o VIOLENCIA FAMILIAR que ya están con modo licenciada")
except Exception as e:
    st.error(f"Error cargando módulo {modulo}: {e}")
    import traceback
    st.code(traceback.format_exc())
