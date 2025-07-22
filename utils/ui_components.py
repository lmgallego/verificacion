import streamlit as st
import pandas as pd

def mostrar_mensaje_exito(mensaje, icono="🎉"):
    """Muestra un mensaje de éxito con estilo"""
    st.success(f"{icono} {mensaje}")

def mostrar_mensaje_error(mensaje, icono="❌"):
    """Muestra un mensaje de error con estilo"""
    st.error(f"{icono} {mensaje}")

def mostrar_mensaje_advertencia(mensaje, icono="⚠️"):
    """Muestra un mensaje de advertencia con estilo"""
    st.warning(f"{icono} {mensaje}")

def mostrar_mensaje_info(mensaje, icono="ℹ️"):
    """Muestra un mensaje informativo con estilo"""
    st.info(f"{icono} {mensaje}")

def mostrar_resumen_errores_originales(errores_originales):
    """Muestra el resumen de errores antes de correcciones usando componentes nativos"""
    if not errores_originales:
        st.success("🎉 No se encontraron errores en el archivo original. Todas las declaraciones están correctas.")
        return
    
    # Calcular estadísticas
    total_errores = len(errores_originales)
    verificadores_con_errores = len(set([error['Verificador'] for error in errores_originales]))
    errores_corregibles = sum(1 for error in errores_originales if 'CORREGIBLE' in error['Errores'])
    errores_kg_cero = sum(1 for error in errores_originales if 'se eliminará' in error['Errores'])
    
    # Mostrar resumen usando métricas de Streamlit
    st.markdown("### 📋 Análisis de Errores ANTES de Correcciones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 Total errores",
            value=total_errores,
            delta=None
        )
    
    with col2:
        st.metric(
            label="👤 Verificadores",
            value=verificadores_con_errores,
            delta=None
        )
    
    with col3:
        st.metric(
            label="✅ Corregibles",
            value=errores_corregibles,
            delta=None
        )
    
    with col4:
        st.metric(
            label="🗑️ Kg=0",
            value=errores_kg_cero,
            delta=None
        )

def mostrar_tabla_errores_originales(errores_originales):
    """Muestra la tabla de errores originales usando solo componentes básicos de Streamlit"""
    if not errores_originales:
        return
    
    st.markdown("#### 📋 Errores Detectados y Correcciones Posibles")
    
    # MARCADOR ÚNICO PARA DEBUG
    st.success("🔥 FUNCIÓN NUEVA EJECUTÁNDOSE CORRECTAMENTE - NO HAY HTML AQUÍ")
    
    # Usar expanders para cada error - solución que funciona garantizada
    for i, error in enumerate(errores_originales):
        with st.expander(f"🔍 Fila {error['Fila']} - {error['Verificador']}", expanded=(i < 3)):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**📝 Errores detectados:**")
                st.write(error['Errores'])
            
            with col2:
                st.write("**🔧 Correcciones posibles:**")
                if error['Correcciones_Posibles'] != 'Ninguna':
                    st.success(error['Correcciones_Posibles'])
                else:
                    st.warning("Ninguna corrección automática disponible")
    
    # Mostrar también un resumen en tabla simple si hay muchos errores
    if len(errores_originales) > 5:
        st.markdown("**📊 Resumen rápido:**")
        for error in errores_originales:
            st.write(f"• **Fila {error['Fila']}** ({error['Verificador']}): {error['Errores'][:50]}...")
    
    st.success("✅ FUNCIÓN NUEVA TERMINÓ CORRECTAMENTE - SIN HTML")

def mostrar_resumen_errores_post_correccion(errores_post_correccion):
    """Muestra el resumen de errores después de correcciones usando componentes nativos"""
    if not errores_post_correccion:
        st.success("🎉 Después de las correcciones automáticas, no quedan errores. El archivo está listo para usar.")
        return
    
    # Calcular estadísticas
    total_errores = len(errores_post_correccion)
    verificadores_con_errores = len(set([error['Verificador'] for error in errores_post_correccion]))
    
    # Mostrar resumen usando métricas de Streamlit
    st.markdown("### ⚠️ Errores RESTANTES Después de Correcciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="📝 Errores restantes",
            value=total_errores,
            delta=None
        )
    
    with col2:
        st.metric(
            label="👤 Verificadores afectados",
            value=verificadores_con_errores,
            delta=None
        )
    
    # Mensaje informativo
    st.warning("Estos errores requieren intervención manual para ser corregidos.")

def mostrar_tabla_errores_post_correccion(errores_post_correccion):
    """Muestra la tabla de errores restantes usando solo componentes básicos de Streamlit"""
    if not errores_post_correccion:
        return
    
    st.markdown("#### 📋 Errores que Requieren Intervención Manual")
    
    # Usar expanders para cada error restante
    for i, error in enumerate(errores_post_correccion):
        with st.expander(f"⚠️ Fila {error['Fila']} - {error['Verificador']}", expanded=True):
            st.error(f"**Errores:** {error['Errores']}")
            st.write("**Requiere corrección manual**")

def mostrar_datos_completos_errores(errores):
    """Muestra los datos completos de las filas con errores"""
    if not errores:
        return
    
    st.markdown("---")
    st.markdown("### 📄 Datos Completos de las Filas con Errores")
    
    for error in errores:
        with st.expander(f"🔍 FILA {error['Fila']} - VERIFICADOR: {error['Verificador']}"):
            st.markdown(f"**❌ ERRORES:** {error['Errores']}")
            st.markdown("**📊 Datos completos:**")
            
            # Mostrar datos en formato tabla
            datos_dict = error['Datos_Completos']
            for campo, valor in datos_dict.items():
                st.write(f"• **{campo}:** {valor}")

def crear_boton_descarga(archivo_bytes, nombre_archivo="declaracion_corregida.xlsx"):
    """Crea un botón de descarga para el archivo corregido"""
    if archivo_bytes:
        st.success("💾 Archivo Corregido Listo")
        
        # Botón de descarga nativo de Streamlit
        st.download_button(
            label="📥 Descargar Archivo Corregido",
            data=archivo_bytes,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Descarga el archivo Excel con las correcciones aplicadas"
        )
        
        st.info("""
        ✅ El archivo mantiene el formato original  
        ✅ NIFs con guiones corregidos  
        ✅ Filas con Kg=0 eliminadas
        """)
        
        return True
    else:
        st.error("❌ Error al generar el archivo corregido.")
        return False

def mostrar_instrucciones():
    """Muestra las instrucciones de uso de la herramienta"""
    st.markdown("""
    **📋 Proceso de Análisis:**
    
    1. **Analizar Errores:** Revisa el archivo original y muestra todos los errores detectados
    2. **Aplicar Correcciones:** Corrige automáticamente NIFs con guiones y elimina filas con Kg=0  
    3. **Descargar Corregido:** Descarga el archivo Excel corregido manteniendo el formato original
    
    **💡 Funcionalidades:**
    
    • ✨ Corrección automática de NIFs: L-NNNNNNNN → LNNNNNNNN  
    • 🗑️ Eliminación automática de filas con Kg = 0  
    • 📊 Preservación del formato original del Excel  
    • 👀 Vista previa de errores antes de corregir
    """)
    
    # Usar un info box de Streamlit nativo
    st.info("🔧 **Tip:** El proceso es completamente interactivo. Puedes revisar todos los errores antes de aplicar cualquier corrección.")