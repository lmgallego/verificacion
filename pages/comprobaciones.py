import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils.ui_components import mostrar_mensaje_error, mostrar_mensaje_exito, mostrar_mensaje_info

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
    4. **Matching:** Comparar pesadas por NIPD + NIF + FECHA + KG + GRADO
    5. **Reporte:** Identificar discrepancias y coincidencias
    """)
    
    st.info("🔧 **Criterios de matching:** NIPD → NIF → FECHA → KG (semejanza absoluta) → GRADO")
    
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
    
    # Botón de procesamiento
    if archivo_extranet and archivo_bbdd and archivo_ervc:
        st.markdown("---")
        if st.button("🔍 Enriquecer con NIPD (Paso 1)", use_container_width=True):
            enriquecer_declaracion_nipd(archivo_extranet, archivo_bbdd, archivo_ervc)

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
            
            st.markdown("---")
            st.success("✅ **Enriquecimiento completado. Revisa los datos y confirma para continuar.**")
            
            # Botón para continuar
            if st.button("✅ Confirmar y continuar con matching eRVC", use_container_width=True):
                continuar_con_matching()
                
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

def continuar_con_matching():
    """Continúa con el proceso de matching con eRVC"""
    
    if 'df_enriquecido' not in st.session_state:
        st.error("❌ No se encontró el DataFrame enriquecido")
        return
    
    st.write("### ⚖️ 5. Continuando con matching eRVC...")
    
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
    st.info(f"🎯 NIPD a analizar: {len(nipd_validos)} → {list(nipd_validos)}")
    
    # Realizar matching
    resultados = realizar_matching(df_enriquecido, df_ervc_final)
    
    # Mostrar resultados
    st.write("### 📊 6. Resultados finales")
    mostrar_resultados(resultados)

def realizar_matching(df_extranet, df_ervc):
    """Realiza matching entre extranet y eRVC"""
    
    resultados = {
        'matches_perfectos': [],
        'grado_diferente': [],
        'kg_aproximado': [],
        'sin_match': [],
        'estadisticas': {}
    }
    
    # Columnas específicas basadas en las imágenes
    col_nif = 'Nif Viticultor'  # Sin dos puntos
    col_fecha = 'Día y hora:'   # Con tilde y dos puntos
    col_kg = 'Total Kg:'        # Con dos puntos
    col_grado = 'Grado:'        # Con dos puntos
    
    # Verificar que existan las columnas en Extranet
    columnas_faltantes = []
    if col_nif not in df_extranet.columns:
        columnas_faltantes.append(f"'{col_nif}'")
    if col_fecha not in df_extranet.columns:
        columnas_faltantes.append(f"'{col_fecha}'")
    if col_kg not in df_extranet.columns:
        columnas_faltantes.append(f"'{col_kg}'")
    if col_grado not in df_extranet.columns:
        columnas_faltantes.append(f"'{col_grado}'")
    
    if columnas_faltantes:
        st.error(f"❌ Columnas no encontradas en Extranet: {', '.join(columnas_faltantes)}")
        st.write("**Columnas disponibles en Extranet:** ", list(df_extranet.columns))
        return resultados
    
    st.info(f"✅ Columnas Extranet encontradas")
    
    # Detectar columnas en eRVC
    st.write("**🔍 Detectando columnas en eRVC:**")
    st.write("Columnas eRVC:", list(df_ervc.columns))
    
    # Buscar columna del NIF en eRVC
    col_nif_ervc = None
    posibles_nif = ['nifLLiurador', 'nifLliurador', 'nif', 'NIF', 'nifProductor', 'nomCelLliur']
    
    for posible in posibles_nif:
        if posible in df_ervc.columns:
            col_nif_ervc = posible
            break
    
    if col_nif_ervc is None:
        st.error(f"❌ No se encontró columna NIF en eRVC. Columnas disponibles: {list(df_ervc.columns)}")
        # Retornar resultado vacío pero válido
        return {
            'matches_perfectos': [],
            'grado_diferente': [],
            'kg_aproximado': [],
            'sin_match': [],
            'estadisticas': {
                'procesados': 0,
                'perfectos': 0,
                'grado_diff': 0,
                'kg_aprox': 0,
                'sin_match': 0
            }
        }
    
    # Buscar columna de fecha en eRVC  
    col_fecha_ervc = None
    posibles_fecha = ['dataPesada', 'dataPesai', 'fecha', 'dataGravacio']
    
    for posible in posibles_fecha:
        if posible in df_ervc.columns:
            col_fecha_ervc = posible
            break
    
    if col_fecha_ervc is None:
        st.error(f"❌ No se encontró columna fecha en eRVC. Columnas disponibles: {list(df_ervc.columns)}")
        # Retornar resultado vacío pero válido
        return {
            'matches_perfectos': [],
            'grado_diferente': [],
            'kg_aproximado': [],
            'sin_match': [],
            'estadisticas': {
                'procesados': 0,
                'perfectos': 0,
                'grado_diff': 0,
                'kg_aprox': 0,
                'sin_match': 0
            }
        }
    
    st.success(f"✅ Columnas eRVC detectadas: NIF='{col_nif_ervc}', Fecha='{col_fecha_ervc}'")
    
    # Preparar eRVC
    df_ervc_prep = df_ervc.copy()
    
    try:
        df_ervc_prep['fecha_pesada'] = pd.to_datetime(df_ervc_prep[col_fecha_ervc]).dt.date
    except Exception as e:
        st.error(f"❌ Error al convertir fechas en eRVC: {str(e)}")
        return resultados
    
    # Procesar registros
    procesados = 0
    
    for index, row in df_extranet.iterrows():
        if pd.isna(row.get('NIPD')):
            continue
            
        procesados += 1
        
        # Convertir fecha extranet - formato: 12/08/2024 23:59
        try:
            fecha_str = str(row[col_fecha]).split(' ')[0]  # Solo la parte de fecha
            fecha_extranet = datetime.strptime(fecha_str, '%d/%m/%Y').date()
        except Exception as e:
            resultados['sin_match'].append({
                'fila': index + 7 + 1,
                'nipd': row['NIPD'],
                'nif': row[col_nif],
                'error': f'Fecha inválida: {row[col_fecha]} ({str(e)})'
            })
            continue
        
        # Buscar candidatos en eRVC usando las columnas detectadas
        candidatos = df_ervc_prep[
            (df_ervc_prep['nipd'] == row['NIPD']) &
            (df_ervc_prep[col_nif_ervc] == row[col_nif]) &
            (df_ervc_prep['fecha_pesada'] == fecha_extranet)
        ]
        
        if len(candidatos) == 0:
            resultados['sin_match'].append({
                'fila': index + 7 + 1,
                'nipd': row['NIPD'],
                'nif': row[col_nif],
                'fecha': fecha_extranet,
                'kg_extranet': row[col_kg],
                'grado_extranet': row[col_grado],
                'error': 'No encontrado en eRVC (NIPD + NIF + FECHA)'
            })
            continue
        
        # Buscar mejor match por kg
        try:
            kg_extranet = float(row[col_kg])
            grado_extranet = float(row[col_grado])
        except (ValueError, TypeError):
            resultados['sin_match'].append({
                'fila': index + 7 + 1,
                'nipd': row['NIPD'],
                'nif': row[col_nif],
                'error': f'Valores no numéricos: kg={row[col_kg]}, grado={row[col_grado]}'
            })
            continue
        
        mejor_match = None
        min_diff_kg = float('inf')
        
        for _, candidato in candidatos.iterrows():
            try:
                kg_ervc = float(candidato['kgTotals'])
                diff_kg = abs(kg_extranet - kg_ervc)
                
                if diff_kg < min_diff_kg:
                    min_diff_kg = diff_kg
                    mejor_match = candidato
            except (ValueError, TypeError):
                continue
        
        if mejor_match is not None:
            try:
                kg_ervc = float(mejor_match['kgTotals'])
                grado_ervc = float(mejor_match['grau'])
                
                match_info = {
                    'fila': index + 7 + 1,
                    'nipd': row['NIPD'],
                    'nif': row[col_nif],
                    'fecha': fecha_extranet,
                    'kg_extranet': kg_extranet,
                    'kg_ervc': kg_ervc,
                    'diff_kg': min_diff_kg,
                    'grado_extranet': grado_extranet,
                    'grado_ervc': grado_ervc,
                    'diff_grado': abs(grado_extranet - grado_ervc)
                }
                
                # Clasificar match
                if min_diff_kg == 0 and grado_extranet == grado_ervc:
                    resultados['matches_perfectos'].append(match_info)
                elif min_diff_kg == 0:
                    resultados['grado_diferente'].append(match_info)
                else:
                    resultados['kg_aproximado'].append(match_info)
                    
            except (ValueError, TypeError):
                resultados['sin_match'].append({
                    'fila': index + 7 + 1,
                    'nipd': row['NIPD'],
                    'nif': row[col_nif],
                    'error': 'Valores no numéricos en eRVC'
                })
    
    # Estadísticas finales
    resultados['estadisticas'] = {
        'procesados': procesados,
        'perfectos': len(resultados['matches_perfectos']),
        'grado_diff': len(resultados['grado_diferente']),
        'kg_aprox': len(resultados['kg_aproximado']),
        'sin_match': len(resultados['sin_match'])
    }
    
    return resultados

def mostrar_resultados(resultados):
    """Muestra resultados de comprobaciones"""
    
    stats = resultados.get('estadisticas', {})
    
    # Valores por defecto si no existen
    perfectos = stats.get('perfectos', 0)
    grado_diff = stats.get('grado_diff', 0) 
    kg_aprox = stats.get('kg_aprox', 0)
    sin_match = stats.get('sin_match', 0)
    procesados = stats.get('procesados', 0)
    
    # Métricas
    st.markdown("#### 📊 Resumen")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("✅ Perfectos", perfectos)
    with col2:
        st.metric("⚠️ Grado Diff", grado_diff)
    with col3:
        st.metric("🔶 Kg Aprox", kg_aprox)
    with col4:
        st.metric("❌ Sin Match", sin_match)
    
    # Porcentaje éxito
    if procesados > 0:
        exito = (perfectos / procesados) * 100
        st.progress(exito / 100)
        st.write(f"**Tasa éxito:** {exito:.1f}% ({perfectos}/{procesados})")
    else:
        st.warning("No se procesaron registros")
    
    # Detalles expandibles
    if resultados.get('matches_perfectos', []):
        with st.expander(f"✅ Matches Perfectos ({len(resultados['matches_perfectos'])})", expanded=False):
            df = pd.DataFrame(resultados['matches_perfectos'])
            st.dataframe(df, use_container_width=True)
    
    if resultados.get('grado_diferente', []):
        with st.expander(f"⚠️ Grado Diferente ({len(resultados['grado_diferente'])})", expanded=True):
            df = pd.DataFrame(resultados['grado_diferente'])
            st.dataframe(df, use_container_width=True)
    
    if resultados.get('kg_aproximado', []):
        with st.expander(f"🔶 Kg Aproximado ({len(resultados['kg_aproximado'])})", expanded=True):
            df = pd.DataFrame(resultados['kg_aproximado'])
            st.dataframe(df, use_container_width=True)
    
    if resultados.get('sin_match', []):
        with st.expander(f"❌ Sin Match ({len(resultados['sin_match'])})", expanded=True):
            df = pd.DataFrame(resultados['sin_match'])
            st.dataframe(df, use_container_width=True)