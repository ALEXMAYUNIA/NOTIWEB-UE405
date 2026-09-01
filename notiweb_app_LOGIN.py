import streamlit as st
import os

st.set_page_config(page_title="NOTIWEB UE 405 - Huacaybamba", layout="wide", page_icon="🏥", initial_sidebar_state="expanded")

# --- BLOQUEAR QUE EL SIDEBAR SE PUEDA OCULTAR/DESLIZAR ---
st.markdown("""
<style>
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

# --- LOGIN BONITO - DISEÑO ORIGINAL ---
def login():
    st.markdown("""
    <style>
    .stApp {
        background-color: #0a1931 !important;
    }
    /* Tarjeta principal */
    .login-card {
        background: linear-gradient(180deg, #132347 0%, #0f1c3a 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        padding: 40px 35px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        max-width: 420px;
        margin: 40px auto 20px auto;
    }
    .login-logo {
        width: 80px;
        height: 80px;
        background: white;
        border-radius: 16px;
        margin: 0 auto 20px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        box-shadow: 0 0 20px rgba(59,130,246,0.5);
    }
    .login-title {
        color: white !important;
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .login-subtitle {
        color: #94a3b8 !important;
        font-size: 13px;
        margin-bottom: 25px;
    }
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: white !important;
        border-radius: 10px !important;
        color: #1e293b !important;
        border: none !important;
        padding: 14px !important;
    }
    label {
        color: #cbd5e1 !important;
        font-size: 13px !important;
    }
    /* Boton */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Contenedor centrado
    col1, col2, col3 = st.columns([1,1.1,1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo">🏥</div>
            <div class="login-title">Sistema NOTIWEB<br>UE 405 Huamalíes</div>
            <div class="login-subtitle">Red de Salud Huamalíes - Huacaybamba</div>
        </div>
        """, unsafe_allow_html=True)
        
        usuario = st.text_input("Usuario", value="admin", key="user")
        clave = st.text_input("Contraseña", type="password", value="1234", key="pass")
        
        if st.button("Iniciar sesión →", use_container_width=True):
            if (usuario == "admin" and clave == "1234") or (usuario == "licenciada" and clave == "licenciada"):
                st.session_state['logado'] = True
                st.session_state['usuario'] = usuario
                st.rerun()
            else:
                st.error("Usuario o clave incorrecta")
        
        st.markdown("<p style='text-align:center; color:#64748b; font-size:11px; margin-top:15px;'>Usuario técnico: admin / 1234 | licenciada / licenciada</p>", unsafe_allow_html=True)

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
