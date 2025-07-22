import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
# Asumo que tienes este archivo de utilidades, si no, puedes eliminar la línea
# from utils.ui_components import mostrar_mensaje_error, mostrar_mensaje_exito, mostrar_mensaje_info

def mostrar_pagina():
    """Página de comprobaciones CAT"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; text-align: center; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            ✅ Comprobaciones CAT
        </h1>
        <p style="color: white; text-align: center; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
            Verificación cruzada de pesadas entre Extranet y eRVC
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instrucciones
    st.markdown("""
    **📋 Proceso de Comprobaciones:**
    
    1. **Subir 3 archivos:** Pesadas Extranet (limpio), Base de Datos NIPD, y Pesadas eRVC
    2. **Enriquecimiento:** Añadir NIPD del archivo de bodegas al archivo limpio
    3. **Filtrado:** Solo registros CAT (excluyendo Almendralejo, Cariñena, Requena)
    4. **Agrupación:** Comparar pesadas por NIPD y NIF entre sistemas
    5. **Reporte:** Excel con diferencias y incidencias por NIPD y NIF
    """)
    
    st.info("🔧 **Nuevo proceso:** Reporte agrupado por NIPD y NIF con análisis de diferencias")
    
    # Subida de archivos
    st.markdown("### 📁 Subir Archivos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Pesadas Extranet (Limpio)**")
        archivo_extranet = st.file_uploader(
            "Archivo verificador corregido",
            type=['xlsx', 'xls'],
            key="extranet",
            help="Archivo generado en el paso de verificación (declaracion_corregida.xlsx)"
        )
    
    with col2:
        st.markdown("**🏭 Base de Datos NIPD**")
        archivo_bbdd = st.file_uploader(
            "Base de datos de bodegas",
            type=['xlsx', 'xls'],
            key="bbdd",
            help="Archivo BBDD_FINAL.xlsx con datos de bodegas y NIPD"
        )
    
    with col3:
        st.markdown("**⚖️ Pesadas eRVC**")
        archivo_ervc = st.file_uploader(
            "Archivo de pesadas eRVC",
            type=['xlsx', 'xls'],
            key="ervc",
            help="Archivo eRVC.xlsx con pesadas oficiales"
        )
    
    # Botones de procesamiento
    if archivo_extranet and archivo_bbdd and archivo_ervc:
        st.markdown("---")
        
        # Inicializar estados si no existen
        if 'nipd_enriquecido' not in st.session_state:
            st.session_state.nipd_enriquecido = False
        
        # Botón Paso 1: Enriquecer
        if not st.session_state.nipd_enriquecido:
            if st.button("🔍 Enriquecer con NIPD (Paso 1)", use_container_width=True):
                enriquecer_declaracion_nipd(archivo_extranet, archivo_bbdd, archivo_ervc)
        
        # Botón Paso 2: Generar Reporte (solo visible después del enriquecimiento)
        if st.session_state.nipd_enriquecido:
            if st.button("✅ Confirmar y continuar con Reporte Agrupado (Paso 2)", use_container_width=True):
                generar_reporte_agrupado()
            
            # Botón para reiniciar si es necesario
            if st.button("🔄 Reiniciar Proceso", help="Volver al paso 1"):
                st.session_state.nipd_enriquecido = False
                if 'df_enriquecido' in st.session_state:
                    del st.session_state.df_enriquecido
                if 'archivo_ervc' in st.session_state:
                    del st.session_state.archivo_ervc
                st.rerun()

def enriquecer_declaracion_nipd(archivo_extranet, archivo_bbdd, archivo_ervc):
    """Enriquecer declaracion_corregida con NIPD - PASO 1"""
    
    try:
        with st.spinner("📊 Procesando archivos..."):
            
            # 1. CARGAR ARCHIVOS
            st.write("### 📥 1. Cargando archivos...")
            
            # Cargar Extranet (saltar 6 filas, usar fila 7 como header)
            df_extranet = pd.read_excel(archivo_extranet, skiprows=6, header=0)
            st.success(f"✅ Extranet: {df_extranet.shape[0]} registros cargados")
            
            # Cargar BBDD (pestaña CAT)
            df_bbdd = pd.read_excel(archivo_bbdd, sheet_name='CAT')
            st.success(f"✅ BBDD CAT: {df_bbdd.shape[0]} registros cargados")
            
            # 2. FILTRAR EXTRANET POR ZONA
            st.write("### 🏷️ 2. Filtrando por zona...")
            
            # Detectar columna de zona
            col_zona = None
            for col in df_extranet.columns:
                if 'zona' in str(col).lower():
                    col_zona = col
                    break
            
            if col_zona is None:
                st.error("❌ No se encontró columna 'Zona' en Extranet")
                st.write("**Columnas disponibles:** ", list(df_extranet.columns))
                return
            
            st.info(f"📍 Usando columna zona: '{col_zona}'")
            
            # Filtrar por zona (excluir Almendralejo, Cariñena, Requena)
            zonas_excluir = ['Almendralejo', 'Cariñena', 'Requena']
            df_extranet_filtrado = df_extranet[~df_extranet[col_zona].isin(zonas_excluir)]
            
            st.success(f"✅ Filtrado por zona: {df_extranet_filtrado.shape[0]} registros (excluidos: {df_extranet.shape[0] - df_extranet_filtrado.shape[0]})")
            
            # 3. ENRIQUECER CON NIPD
            st.write("### 🏭 3. Añadiendo NIPD...")
            
            df_extranet_enriquecido = enriquecer_con_nipd_mejorado(df_extranet_filtrado, df_bbdd)
            
            nipd_encontrados = df_extranet_enriquecido['NIPD'].notna().sum()
            st.success(f"✅ NIPD encontrados: {nipd_encontrados}/{df_extranet_enriquecido.shape[0]} registros")
            
            # 4. MOSTRAR RESULTADO PARA VERIFICACIÓN
            st.write("### 📊 4. Resultado para verificación")
            
            st.info("🔍 **Archivo declaracion_corregida enriquecido con NIPD:**")
            
            # Mostrar estadísticas por NIPD
            nipd_stats = df_extranet_enriquecido.groupby('NIPD', dropna=False).size().reset_index(name='registros')
            st.write("**📈 Distribución por NIPD:**")
            st.dataframe(nipd_stats, use_container_width=True)
            
            # Mostrar el DataFrame completo
            st.write("**📋 DataFrame completo enriquecido:**")
            st.dataframe(df_extranet_enriquecido, use_container_width=True, height=400)
            
            # Guardar en session_state para siguiente paso
            st.session_state['df_enriquecido'] = df_extranet_enriquecido
            st.session_state['archivo_ervc'] = archivo_ervc
            st.session_state.nipd_enriquecido = True  # Marcar como completado
            
            st.markdown("---")
            st.success("✅ **Enriquecimiento completado. Usa el botón de abajo para continuar al Paso 2.**")
            st.info("🔄 La página se recargará automáticamente para mostrar el siguiente paso.")
            
            # Recargar página para mostrar el botón del paso 2
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def enriquecer_con_nipd_mejorado(df_extranet, df_bbdd):
    """Añade NIPD al DataFrame de extranet - VERSIÓN MEJORADA"""
    
    df_resultado = df_extranet.copy()
    df_resultado['NIPD'] = None
    
    # Detectar columnas en extranet
    col_bodega = None
    col_zona = None
    
    for col in df_extranet.columns:
        col_lower = str(col).lower()
        if 'razón' in col_lower and 'social' in col_lower:
            col_bodega = col
        elif 'zona' in col_lower:
            col_zona = col
    
    if col_bodega is None or col_zona is None:
        st.error(f"❌ Columnas no encontradas - Bodega: {col_bodega}, Zona: {col_zona}")
        st.write("**Columnas disponibles:** ", list(df_extranet.columns))
        return df_resultado
    
    st.info(f"🔍 Detectadas - Bodega: '{col_bodega}', Zona: '{col_zona}'")
    
    # Crear diccionario usando columnas EXTRANET y RVC del BBDD
    bodegas_dict = {}
    for _, row in df_bbdd.iterrows():
        nombre_extranet = str(row['EXTRANET']).strip().upper()
        nombre_rvc = str(row['RVC']).strip().upper()
        nipd = row['NIPD']
        zona_bbdd = str(row.get('ZONA', '')).strip().upper()
        
        # Agregar ambos nombres al diccionario
        bodegas_dict[nombre_extranet] = {
            'nipd': nipd,
            'zona_bbdd': zona_bbdd
        }
        
        if nombre_rvc != nombre_extranet:
            bodegas_dict[nombre_rvc] = {
                'nipd': nipd,
                'zona_bbdd': zona_bbdd
            }
    
    # Estadísticas de matching
    matches = 0
    codorniu_casos = 0
    matches_exactos = 0
    matches_parciales = 0
    sin_match = 0
    
    # Procesar cada registro
    for index, row in df_resultado.iterrows():
        bodega_extranet = str(row[col_bodega]).strip().upper()
        zona_extranet = str(row[col_zona]).strip().upper()
        
        nipd_asignado = None
        
        # CASO ESPECIAL: CODORNIU, S.A.
        if bodega_extranet == 'CODORNIU, S.A.':
            codorniu_casos += 1
            
            if zona_extranet == 'LLEIDA':
                nipd_asignado = '2501200003'
                st.write(f"🎯 CODORNIU Lleida → NIPD: {nipd_asignado}")
            elif zona_extranet == 'PENEDÈS':
                nipd_asignado = '802400022'
                st.write(f"🎯 CODORNIU Penedès → NIPD: {nipd_asignado}")
            else:
                st.warning(f"⚠️ CODORNIU zona desconocida: '{zona_extranet}'")
        
        # BÚSQUEDA NORMAL
        else:
            # Búsqueda exacta primero
            if bodega_extranet in bodegas_dict:
                nipd_asignado = bodegas_dict[bodega_extranet]['nipd']
                matches_exactos += 1
            
            # Búsqueda parcial si no hay match exacto
            else:
                for nombre_bbdd, datos in bodegas_dict.items():
                    if bodega_extranet in nombre_bbdd or nombre_bbdd in bodega_extranet:
                        nipd_asignado = datos['nipd']
                        matches_parciales += 1
                        st.write(f"🔍 Match parcial: '{bodega_extranet}' ≈ '{nombre_bbdd}' → NIPD: {nipd_asignado}")
                        break
        
        # Asignar NIPD
        if nipd_asignado:
            df_resultado.at[index, 'NIPD'] = nipd_asignado
            matches += 1
        else:
            sin_match += 1
            if sin_match <= 5:  # Mostrar solo los primeros 5 para no saturar
                st.write(f"❌ Sin match: '{bodega_extranet}' (Zona: '{zona_extranet}')")
    
    # Mostrar estadísticas
    st.write(f"📊 **Estadísticas de matching:**")
    st.write(f"• **Total registros:** {len(df_resultado)}")
    st.write(f"• **Matches totales:** {matches}")
    st.write(f"• **Matches exactos:** {matches_exactos}")
    st.write(f"• **Matches parciales:** {matches_parciales}")
    st.write(f"• **Casos CODORNIU:** {codorniu_casos}")
    st.write(f"• **Sin match:** {sin_match}")
    
    return df_resultado

def generar_reporte_agrupado():
    """Genera reporte agrupado por NIPD y NIF con Excel de 2 pestañas"""
    
    if 'df_enriquecido' not in st.session_state:
        st.error("❌ No se encontró el DataFrame enriquecido")
        return
    
    st.write("### 📊 5. Generando Reporte Agrupado...")
    
    try:
        # Cargar eRVC
        archivo_ervc = st.session_state['archivo_ervc']
        df_ervc = pd.read_excel(archivo_ervc)
        st.success(f"✅ eRVC: {df_ervc.shape[0]} registros cargados")
        
        # Filtrar eRVC
        df_ervc_filtrado = df_ervc[df_ervc['dos'] == 'CV']
        st.info(f"📊 eRVC después de filtro 'dos'='CV': {df_ervc_filtrado.shape[0]} registros")
        
        # Solo NIPD que existen en extranet
        df_enriquecido = st.session_state['df_enriquecido']
        nipd_validos = df_enriquecido['NIPD'].dropna().unique()
        df_ervc_final = df_ervc_filtrado[df_ervc_filtrado['nipd'].isin(nipd_validos)]
        
        st.success(f"✅ eRVC final: {df_ervc_final.shape[0]} registros")
        st.info(f"🎯 NIPD a analizar: {len(nipd_validos)}")
        
        # Preparar datos con fechas
        with st.spinner("📅 Preparando datos y comparando fechas..."):
            df_extranet_prep, df_ervc_prep = preparar_datos_fechas(df_enriquecido, df_ervc_final)
            
        # DEBUG: Verificar columnas después del procesamiento de fechas
        st.write("**🔍 DEBUG - Columnas Extranet después de preparar fechas:**", list(df_extranet_prep.columns))
        st.write("**🔍 DEBUG - Columnas eRVC después de preparar fechas:**", list(df_ervc_prep.columns))
        
        # Verificar que NIPD existe en Extranet
        if 'NIPD' not in df_extranet_prep.columns:
            st.error("❌ CRÍTICO: La columna NIPD se perdió durante el procesamiento de fechas")
            st.write("Columnas disponibles:", list(df_extranet_prep.columns))
            return
        
        # Verificar que nipd existe en eRVC
        if 'nipd' not in df_ervc_prep.columns:
            st.error("❌ CRÍTICO: La columna nipd no existe en eRVC")
            st.write("Columnas disponibles:", list(df_ervc_prep.columns))
            return
        
        # Agrupar por NIPD
        with st.spinner("🏭 Agrupando por NIPD..."):
            df_nipd = agrupar_por_nipd(df_extranet_prep, df_ervc_prep)
        
        # Agrupar por NIF
        with st.spinner("👤 Agrupando por NIF..."):
            df_nif = agrupar_por_nif(df_extranet_prep, df_ervc_prep)
        
        # Generar Excel
        with st.spinner("📋 Generando archivo Excel..."):
            archivo_excel = crear_excel_agrupado(df_nipd, df_nif)
        
        if archivo_excel:
            st.success("✅ Reporte generado exitosamente")
            
            # Mostrar resúmenes
            mostrar_resumen_nipd(df_nipd)
            mostrar_resumen_nif(df_nif)
            
            # Botón de descarga
            st.download_button(
                label="📥 Descargar Reporte Completo (Excel)",
                data=archivo_excel,
                file_name="reporte_agrupado_pesadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga el Excel con pestañas NIPD y NIF Viticultor"
            )
        else:
            st.error("❌ Error al generar el archivo Excel")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def preparar_datos_fechas(df_extranet, df_ervc):
    """Prepara datos y convierte fechas para comparación"""
    
    # Detectar columnas
    col_fecha_extranet = 'Día y hora:'
    col_fecha_ervc = None
    
    # Buscar columna de fecha en eRVC  
    posibles_fecha = ['dataPesada', 'dataPesai', 'fecha', 'dataGravacio']
    for posible in posibles_fecha:
        if posible in df_ervc.columns:
            col_fecha_ervc = posible
            break
    
    if not col_fecha_ervc:
        st.error(f"❌ No se encontró columna fecha en eRVC")
        return df_extranet, df_ervc
    
    st.info(f"📅 Usando fechas: Extranet='{col_fecha_extranet}', eRVC='{col_fecha_ervc}'")
    
    # Preparar Extranet
    df_extranet_prep = df_extranet.copy()
    try:
        # Convertir fecha extranet - MEJORADO para manejar múltiples formatos
        fechas_str = df_extranet_prep[col_fecha_extranet].astype(str).str.split(' ').str[0]
        
        # Primero intentar formato dd/mm/yyyy
        try:
            df_extranet_prep['fecha_pesada'] = pd.to_datetime(fechas_str, format='%d/%m/%Y').dt.date
            st.success("✅ Fechas Extranet procesadas con formato dd/mm/yyyy")
        except:
            # Si falla, intentar formato yyyy-mm-dd (ISO)
            try:
                df_extranet_prep['fecha_pesada'] = pd.to_datetime(fechas_str, format='%Y-%m-%d').dt.date
                st.success("✅ Fechas Extranet procesadas con formato yyyy-mm-dd")
            except:
                # Como último recurso, usar formato automático
                df_extranet_prep['fecha_pesada'] = pd.to_datetime(fechas_str, dayfirst=True, errors='coerce').dt.date
                st.warning("⚠️ Fechas Extranet procesadas con detección automática")
                
    except Exception as e:
        st.error(f"❌ Error al procesar fechas Extranet: {str(e)}")
        # Crear columna vacía para evitar el error posterior
        df_extranet_prep['fecha_pesada'] = pd.NaT
        return df_extranet_prep, df_ervc
    
    # Preparar eRVC
    df_ervc_prep = df_ervc.copy()
    try:
        df_ervc_prep['fecha_pesada'] = pd.to_datetime(df_ervc_prep[col_fecha_ervc], errors='coerce').dt.date
        st.success("✅ Fechas eRVC procesadas correctamente")
    except Exception as e:
        st.error(f"❌ Error al procesar fechas eRVC: {str(e)}")
        # Crear columna vacía para evitar el error posterior
        df_ervc_prep['fecha_pesada'] = pd.NaT
        return df_extranet_prep, df_ervc_prep
    
    # Verificar que se crearon las columnas
    if 'fecha_pesada' not in df_extranet_prep.columns or 'fecha_pesada' not in df_ervc_prep.columns:
        st.error("❌ Error: No se pudieron crear las columnas de fecha")
        return df_extranet, df_ervc
    
    # Filtrar por fechas válidas primero
    df_extranet_prep = df_extranet_prep.dropna(subset=['fecha_pesada'])
    df_ervc_prep = df_ervc_prep.dropna(subset=['fecha_pesada'])
    
    # Filtrar por fechas coincidentes
    fechas_extranet = set(df_extranet_prep['fecha_pesada'])
    fechas_ervc = set(df_ervc_prep['fecha_pesada'])
    fechas_comunes = fechas_extranet.intersection(fechas_ervc)
    
    st.info(f"📊 Fechas válidas - Extranet: {len(fechas_extranet)}, eRVC: {len(fechas_ervc)}")
    st.info(f"📊 Fechas comunes encontradas: {len(fechas_comunes)}")
    
    if len(fechas_comunes) == 0:
        st.warning("⚠️ No se encontraron fechas comunes. Procesando todos los datos...")
        # Si no hay fechas comunes, usar todos los datos
        st.success(f"✅ Datos preparados - Extranet: {len(df_extranet_prep)}, eRVC: {len(df_ervc_prep)}")
        return df_extranet_prep, df_ervc_prep
    
    # Filtrar por fechas comunes
    df_extranet_prep = df_extranet_prep[df_extranet_prep['fecha_pesada'].isin(fechas_comunes)]
    df_ervc_prep = df_ervc_prep[df_ervc_prep['fecha_pesada'].isin(fechas_comunes)]
    
    st.success(f"✅ Datos filtrados por fechas comunes - Extranet: {len(df_extranet_prep)}, eRVC: {len(df_ervc_prep)}")
    
    return df_extranet_prep, df_ervc_prep

def agrupar_por_nipd(df_extranet, df_ervc):
    """Agrupa datos por NIPD y calcula diferencias"""
    
    # Asegurarse de que las columnas NIPD son de tipo string en ambos DataFrames
    df_extranet['NIPD'] = df_extranet['NIPD'].astype(str) # <-- CORRECCIÓN AÑADIDA
    df_ervc['nipd'] = df_ervc['nipd'].astype(str) # <-- CORRECCIÓN AÑADIDA
    
    # Agrupar Extranet por NIPD
    extranet_nipd = df_extranet.groupby('NIPD').agg({
        'Total Kg:': 'sum',
        'fecha_pesada': 'nunique'  # Contar días únicos como "número de pesadas"
    }).rename(columns={
        'Total Kg:': 'kg_extranet',
        'fecha_pesada': 'num_pesadas_extranet'
    }).reset_index()
    
    # Agrupar eRVC por NIPD
    ervc_nipd = df_ervc.groupby('nipd').agg({
        'kgTotals': 'sum',
        'fecha_pesada': 'nunique'  # Contar días únicos como "número de pesadas"
    }).rename(columns={
        'kgTotals': 'kg_ervc',
        'fecha_pesada': 'num_pesadas_ervc'
    }).reset_index()
    
    # Renombrar nipd a NIPD después del groupby para el merge
    ervc_nipd = ervc_nipd.rename(columns={'nipd': 'NIPD'})
    
    # Merge
    df_nipd = pd.merge(ervc_nipd, extranet_nipd, on='NIPD', how='outer')
    df_nipd = df_nipd.fillna(0)
    
    # Calcular diferencias y porcentajes
    df_nipd['diferencia'] = df_nipd['kg_extranet'] - df_nipd['kg_ervc']
    df_nipd['porcentaje_diferencia'] = np.where(
        df_nipd['kg_ervc'] != 0,
        (df_nipd['diferencia'] / df_nipd['kg_ervc']) * 100,
        np.inf
    )
    
    # Calcular incidencias
    df_nipd['incidencia_pesadas'] = np.where(
        df_nipd['num_pesadas_ervc'] != df_nipd['num_pesadas_extranet'],
        'SI', 'NO'
    )
    
    df_nipd['incidencia_kg'] = np.where(
        (df_nipd['kg_ervc'] != df_nipd['kg_extranet']) & 
        (abs(df_nipd['porcentaje_diferencia']) > 15),
        'SI', 'NO'
    )
    
    # Renombrar columnas para Excel
    df_nipd = df_nipd.rename(columns={
        'NIPD': 'nipd',
        'kg_ervc': 'kgtotales rvc',
        'kg_extranet': 'kgtotales extranet',
        'diferencia': 'diferencia',
        'porcentaje_diferencia': 'porcentaje diferencia',
        'num_pesadas_ervc': 'cantidad pesadas rvc',
        'num_pesadas_extranet': 'cantidad pesadas extranet',
        'incidencia_pesadas': 'incidencia pesadas',
        'incidencia_kg': 'incidencias kg'
    })
    
    # Reordenar columnas según imagen
    columnas_orden = [
        'nipd', 'kgtotales rvc', 'kgtotales extranet', 'diferencia',
        'porcentaje diferencia', 'cantidad pesadas rvc', 'cantidad pesadas extranet',
        'incidencia pesadas', 'incidencias kg'
    ]
    
    df_nipd = df_nipd[columnas_orden]
    
    return df_nipd

def agrupar_por_nif(df_extranet, df_ervc):
    """Agrupa datos por NIF y calcula diferencias"""
    
    # Asegurarse de que las columnas NIF también son de tipo string
    df_extranet['Nif Viticultor'] = df_extranet['Nif Viticultor'].astype(str)
    df_ervc['nifLLiurador'] = df_ervc['nifLLiurador'].astype(str)
    
    # Agrupar Extranet por NIF
    extranet_nif = df_extranet.groupby('Nif Viticultor').agg({
        'Total Kg:': 'sum',
        'fecha_pesada': 'nunique',
        'NIPD': 'first'  # Para mantener referencia al NIPD
    }).rename(columns={
        'Total Kg:': 'kg_extranet',
        'fecha_pesada': 'num_pesadas_extranet'
    }).reset_index()
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Se corrige el orden de las operaciones: groupby -> reset_index -> rename
    
    # Agrupar eRVC por NIF
    ervc_nif = df_ervc.groupby('nifLLiurador').agg({
        'kgTotals': 'sum',
        'fecha_pesada': 'nunique',
        'nipd': 'first'
    }).reset_index().rename(columns={  # Renombrar DESPUÉS de reset_index
        'kgTotals': 'kg_ervc',
        'fecha_pesada': 'num_pesadas_ervc',
        'nifLLiurador': 'nif' # Ahora sí renombra la columna correctamente
    })
    # --- FIN DE LA CORRECCIÓN ---
    
    # Merge por NIF (Ahora 'nif' sí existe en ervc_nif)
    df_nif = pd.merge(
        ervc_nif, extranet_nif, 
        left_on='nif', right_on='Nif Viticultor', 
        how='outer'
    )
    df_nif = df_nif.fillna(0)
    
    # Usar el NIF de la columna que no sea 0
    df_nif['nif_final'] = np.where(
        df_nif['nif'] != 0, df_nif['nif'], df_nif['Nif Viticultor']
    )
    
    # Usar el NIPD de la columna que no sea 0
    df_nif['nipd_final'] = np.where(
        df_nif['nipd'] != 0, df_nif['nipd'], df_nif['NIPD']
    )
    
    # Calcular diferencias y porcentajes
    df_nif['diferencia'] = df_nif['kg_extranet'] - df_nif['kg_ervc']
    df_nif['porcentaje_diferencia'] = np.where(
        df_nif['kg_ervc'] != 0,
        (df_nif['diferencia'] / df_nif['kg_ervc']) * 100,
        np.inf
    )
    
    # Calcular incidencias
    df_nif['incidencia_pesadas'] = np.where(
        df_nif['num_pesadas_ervc'] != df_nif['num_pesadas_extranet'],
        'SI', 'NO'
    )
    
    # Limpiar y renombrar columnas para Excel
    df_nif = df_nif[[
        'nipd_final', 'nif_final', 'kg_ervc', 'kg_extranet', 'diferencia',
        'porcentaje_diferencia', 'num_pesadas_ervc', 'num_pesadas_extranet',
        'incidencia_pesadas'
    ]].rename(columns={
        'nipd_final': 'nipd',
        'nif_final': 'nif',
        'kg_ervc': 'KgTotales RVC',
        'kg_extranet': 'KgTotales Extranet',
        'diferencia': 'diferencia porcentual',
        'porcentaje_diferencia': 'porcentaje diferencia pesadas',
        'num_pesadas_ervc': 'numero pesadas viticultor rvc',
        'num_pesadas_extranet': 'numero pesadas viticultor extranet',
        'incidencia_pesadas': 'incidencia pesadas'
    })
    
    return df_nif

def crear_excel_agrupado(df_nipd, df_nif):
    """Crea archivo Excel con 2 pestañas"""
    
    try:
        from io import BytesIO
        import pandas as pd
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Pestaña NIPD
            df_nipd.to_excel(writer, sheet_name='nipd', index=False)
            
            # Pestaña NIF
            df_nif.to_excel(writer, sheet_name='nifViticultor', index=False)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        st.error(f"❌ Error al crear Excel: {str(e)}")
        return None

def mostrar_resumen_nipd(df_nipd):
    """Muestra resumen de agrupación por NIPD"""
    st.markdown("#### 🏭 Resumen por NIPD")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total NIPD", len(df_nipd))
    
    with col2:
        incidencias_kg = (df_nipd['incidencias kg'] == 'SI').sum()
        st.metric("⚠️ Incidencias Kg", incidencias_kg)
    
    with col3:
        incidencias_pesadas = (df_nipd['incidencia pesadas'] == 'SI').sum()
        st.metric("📋 Inc. Pesadas", incidencias_pesadas)
    
    with col4:
        diferencia_total = df_nipd['diferencia'].sum()
        st.metric("⚖️ Diferencia Total", f"{diferencia_total:,.0f} kg")
    
    # Mostrar tabla resumida
    st.dataframe(df_nipd, use_container_width=True, height=300)

def mostrar_resumen_nif(df_nif):
    """Muestra resumen de agrupación por NIF"""
    st.markdown("#### 👤 Resumen por NIF Viticultor")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total NIFs", len(df_nif))
    
    with col2:
        incidencias_pesadas = (df_nif['incidencia pesadas'] == 'SI').sum()
        st.metric("📋 Inc. Pesadas", incidencias_pesadas)
    
    with col3:
        diferencia_total = df_nif['diferencia porcentual'].sum()
        st.metric("⚖️ Diferencia Total", f"{diferencia_total:,.0f} kg")
    
    # Mostrar tabla resumida
    st.dataframe(df_nif, use_container_width=True, height=300)

# Para poder ejecutar este script directamente (si es necesario)
if __name__ == '__main__':
    mostrar_pagina()