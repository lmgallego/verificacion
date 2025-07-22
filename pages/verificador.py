import streamlit as st
import io
from utils.analyzer import VerificadorAnalyzer
from utils.ui_components import (
    mostrar_mensaje_error, mostrar_mensaje_advertencia,
    mostrar_resumen_errores_originales, mostrar_tabla_errores_originales,
    mostrar_resumen_errores_post_correccion, mostrar_tabla_errores_post_correccion,
    mostrar_datos_completos_errores, crear_boton_descarga, mostrar_instrucciones
)

def mostrar_pagina():
    """Página principal del analizador de verificador"""
    
    # Header de la página
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; text-align: center; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            🔍 Analizador de Verificador
        </h1>
        <p style="color: white; text-align: center; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
            Análisis interactivo con correcciones automáticas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar instrucciones
    mostrar_instrucciones()
    
    # Inicializar session_state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = VerificadorAnalyzer()
    
    if 'paso_actual' not in st.session_state:
        st.session_state.paso_actual = 1
    
    if 'archivo_analizado' not in st.session_state:
        st.session_state.archivo_analizado = False
    
    if 'correcciones_aplicadas' not in st.session_state:
        st.session_state.correcciones_aplicadas = False
    
    # Área de subida de archivos
    st.markdown("### 📁 Subir Archivo Excel")
    
    uploaded_file = st.file_uploader(
        "Selecciona el archivo de declaraciones del verificador",
        type=['xlsx', 'xls'],
        help="Formato soportado: Excel (.xlsx, .xls). Las primeras 6 filas serán ignoradas automáticamente."
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Archivo cargado: **{uploaded_file.name}** ({uploaded_file.size} bytes)")
    
    # Botones de acción en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btn_analizar = st.button(
            "🔍 1. Analizar Errores", 
            disabled=(uploaded_file is None),
            use_container_width=True,
            help="Analiza el archivo original sin hacer modificaciones"
        )
    
    with col2:
        btn_corregir = st.button(
            "🔧 2. Aplicar Correcciones", 
            disabled=(not st.session_state.archivo_analizado),
            use_container_width=True,
            help="Aplica correcciones automáticas a los errores detectados"
        )
    
    with col3:
        btn_descargar = st.button(
            "💾 3. Generar Descarga", 
            disabled=(not st.session_state.correcciones_aplicadas),
            use_container_width=True,
            help="Genera el archivo Excel corregido para descarga"
        )
    
    # Separador
    st.markdown("---")
    
    # PASO 1: Analizar errores originales
    if btn_analizar and uploaded_file is not None:
        with st.spinner("🔍 Analizando archivo original..."):
            # Leer archivo
            archivo_bytes = uploaded_file.read()
            
            # Reset del estado
            st.session_state.analyzer = VerificadorAnalyzer()
            st.session_state.archivo_analizado = False
            st.session_state.correcciones_aplicadas = False
            
            # Crear contenedor para output en tiempo real
            output_container = st.container()
            
            with output_container:
                st.markdown("### 🚀 PASO 1: Analizando errores originales...")
                
                # Capturar output del análisis
                old_stdout = st.session_state.get('stdout_capture', None)
                
                # Analizar errores
                if st.session_state.analyzer.analizar_errores_originales(archivo_bytes, uploaded_file.name):
                    st.session_state.archivo_analizado = True
                    st.session_state.paso_actual = 1
                    
                    st.success("✅ Análisis completado")
                    
                    # Mostrar resultados del análisis - SOLO componentes nuevos
                    mostrar_resumen_errores_originales(st.session_state.analyzer.errores_originales)
                    mostrar_tabla_errores_originales(st.session_state.analyzer.errores_originales)
                    
                    # NO llamar a analyzer.mostrar_resultados() o funciones similares
                    
                    # Mostrar datos completos si hay errores
                    if st.session_state.analyzer.errores_originales:
                        if st.checkbox("📄 Mostrar datos completos de filas con errores", key="mostrar_datos_originales"):
                            mostrar_datos_completos_errores(st.session_state.analyzer.errores_originales)
                    
                else:
                    mostrar_mensaje_error("Error al analizar el archivo. Verifica que sea un archivo Excel válido.")
    
    # PASO 2: Aplicar correcciones
    elif btn_corregir and st.session_state.archivo_analizado:
        with st.spinner("🔧 Aplicando correcciones automáticas..."):
            st.markdown("### 🚀 PASO 2: Aplicando correcciones automáticas...")
            
            if st.session_state.analyzer.aplicar_correcciones():
                st.session_state.correcciones_aplicadas = True
                st.session_state.paso_actual = 2
                
                st.success("✅ Correcciones aplicadas")
                
                # Mostrar resultados post-corrección
                mostrar_resumen_errores_post_correccion(st.session_state.analyzer.errores_post_correccion)
                mostrar_tabla_errores_post_correccion(st.session_state.analyzer.errores_post_correccion)
                
                # Mostrar datos completos si quedan errores
                if st.session_state.analyzer.errores_post_correccion:
                    if st.checkbox("📄 Mostrar datos completos de errores restantes", key="mostrar_datos_post"):
                        mostrar_datos_completos_errores(st.session_state.analyzer.errores_post_correccion)
            else:
                mostrar_mensaje_error("Error al aplicar las correcciones.")
    
    # PASO 3: Generar descarga
    elif btn_descargar and st.session_state.correcciones_aplicadas:
        with st.spinner("💾 Generando archivo corregido..."):
            st.markdown("### 🚀 PASO 3: Generando archivo corregido...")
            
            archivo_corregido = st.session_state.analyzer.generar_archivo_corregido()
            
            if archivo_corregido:
                # Crear botón de descarga
                nombre_archivo = f"declaracion_corregida_{uploaded_file.name}" if uploaded_file else "declaracion_corregida.xlsx"
                crear_boton_descarga(archivo_corregido, nombre_archivo)
                
                # Limpiar archivos temporales
                st.session_state.analyzer.cleanup()
                
                st.success("✅ Archivo generado exitosamente")
            else:
                mostrar_mensaje_error("Error al generar el archivo corregido.")
    
    # Mostrar estado actual del proceso
    if st.session_state.archivo_analizado or st.session_state.correcciones_aplicadas:
        st.markdown("---")
        st.markdown("### 📊 Estado del Proceso")
        
        # Indicadores de progreso
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.archivo_analizado:
                st.markdown("✅ **Paso 1:** Análisis completado")
            else:
                st.markdown("⏳ **Paso 1:** Pendiente")
        
        with col2:
            if st.session_state.correcciones_aplicadas:
                st.markdown("✅ **Paso 2:** Correcciones aplicadas")
            elif st.session_state.archivo_analizado:
                st.markdown("🔄 **Paso 2:** Listo para corregir")
            else:
                st.markdown("⏳ **Paso 2:** Pendiente")
        
        with col3:
            if st.session_state.correcciones_aplicadas:
                st.markdown("🔄 **Paso 3:** Listo para descargar")
            else:
                st.markdown("⏳ **Paso 3:** Pendiente")
    
    # Botón para reiniciar el proceso
    if st.session_state.archivo_analizado:
        st.markdown("---")
        if st.button("🔄 Reiniciar Proceso", help="Limpia todos los datos y permite analizar un nuevo archivo"):
            # Limpiar session_state
            if hasattr(st.session_state.analyzer, 'cleanup'):
                st.session_state.analyzer.cleanup()
            
            st.session_state.analyzer = VerificadorAnalyzer()
            st.session_state.archivo_analizado = False
            st.session_state.correcciones_aplicadas = False
            st.session_state.paso_actual = 1
            
            st.rerun()