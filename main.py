import streamlit as st
from pages import verificador, comprobaciones

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Verificación",
    page_icon="🍇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados - Compatible con modo claro y oscuro
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .sidebar-content {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    .menu-item {
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .menu-item:hover {
        background-color: rgba(128, 128, 128, 0.1);
        transform: translateX(5px);
    }
    
    .success-box {
        background-color: #d4edda !important;
        border: 2px solid #28a745 !important;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #155724 !important;
    }
    
    .error-box {
        background-color: #f8d7da !important;
        border: 2px solid #dc3545 !important;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #721c24 !important;
    }
    
    .warning-box {
        background-color: #fff3cd !important;
        border: 2px solid #ffc107 !important;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #856404 !important;
    }
    
    .info-box {
        background-color: #e7f3ff !important;
        border: 2px solid #007bff !important;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #004085 !important;
    }
    
    /* Asegurar que los textos sean visibles */
    .success-box h3, .success-box p, .success-box div, .success-box li {
        color: #155724 !important;
    }
    
    .error-box h3, .error-box p, .error-box div, .error-box li {
        color: #721c24 !important;
    }
    
    .warning-box h3, .warning-box p, .warning-box div, .warning-box li {
        color: #856404 !important;
    }
    
    .info-box h3, .info-box p, .info-box div, .info-box li {
        color: #004085 !important;
    }
    
    /* Asegurar que las listas se vean correctamente */
    .custom-list {
        color: inherit !important;
        padding-left: 20px;
    }
    
    .custom-list li {
        margin: 8px 0;
        color: inherit !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🍇 Sistema de Verificación</h1>
        <p>Herramientas para el análisis y control de declaraciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para navegación
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-content">
            <h2>📋 Menú Principal</h2>
            <p>Selecciona la herramienta que necesitas:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menú de navegación
        opciones = {
            "🏠 Inicio": "inicio",
            "🔍 Verificador": "verificador", 
            "✅ Comprobaciones": "comprobaciones"
        }
        
        # Usar session_state para mantener la selección
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = "inicio"
        
        # Radio buttons para navegación
        seleccion = st.radio(
            "Navegación:",
            list(opciones.keys()),
            index=list(opciones.values()).index(st.session_state.pagina_actual)
        )
        
        # Actualizar página actual
        st.session_state.pagina_actual = opciones[seleccion]
        
        # Información adicional en sidebar
        st.markdown("---")
        st.markdown("""
        <div class="sidebar-content">
            <h4>ℹ️ Información</h4>
            <p><strong>Versión:</strong> 1.0.0</p>
            <p><strong>Última actualización:</strong> Julio 2025</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enrutamiento de páginas
    if st.session_state.pagina_actual == "inicio":
        mostrar_inicio()
    elif st.session_state.pagina_actual == "verificador":
        verificador.mostrar_pagina()
    elif st.session_state.pagina_actual == "comprobaciones":
        comprobaciones.mostrar_pagina()

def mostrar_inicio():
    """Página de inicio con información general"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🔍 Analizador de Verificador</h3>
            <p>Herramienta para detectar y corregir errores en las declaraciones de verificador:</p>
            <ul class="custom-list">
                <li>✅ Validación de NIFs de viticultores</li>
                <li>🔧 Corrección automática de guiones</li>
                <li>🗑️ Eliminación de registros con Kg = 0</li>
                <li>📊 Informes detallados de errores</li>
                <li>💾 Descarga de archivos corregidos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
            <h3>✅ Comprobaciones</h3>
            <p>Próximamente: Herramientas adicionales de verificación y control de calidad.</p>
            <p><em>Esta sección estará disponible en futuras actualizaciones.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Instrucciones generales
    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        <h3>📋 Instrucciones Generales</h3>
        <ol class="custom-list">
            <li><strong>Selecciona una herramienta</strong> del menú lateral</li>
            <li><strong>Sube tu archivo Excel</strong> con las declaraciones</li>
            <li><strong>Revisa los errores</strong> detectados antes de corregir</li>
            <li><strong>Aplica las correcciones</strong> automáticas</li>
            <li><strong>Descarga el archivo</strong> corregido</li>
        </ol>
        
        <h4>🔧 Funcionalidades:</h4>
        <ul class="custom-list">
            <li><strong>Análisis sin modificaciones:</strong> Ve todos los errores antes de hacer cambios</li>
            <li><strong>Correcciones inteligentes:</strong> Arregla automáticamente errores comunes</li>
            <li><strong>Preservación de formato:</strong> Mantiene el diseño original del Excel</li>
            <li><strong>Proceso interactivo:</strong> Control total sobre cada paso</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()