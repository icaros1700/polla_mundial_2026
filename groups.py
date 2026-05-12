import streamlit as st
import pandas as pd

def mostrar_tablas_grupos(supabase):
    st.title("📊 Posiciones de los Grupos")
    
    # 1. Traemos todos los partidos
    res = supabase.table("partidos").select("*").execute()
    partidos = res.data
    
    # 🚨 SENSOR DE DIAGNÓSTICO: Esto te mostrará en pantalla qué está llegando realmente
    # st.write("Datos en crudo desde la Matrix:", partidos)
    
    if not partidos:
        st.error("⚠️ La base de datos devolvió 0 partidos. Las políticas RLS están bloqueando la lectura.")
        return

    # Diccionario para guardar las estadísticas
    stats = {}

    for p in partidos:
        # Extraemos el grupo. Si no tiene, le ponemos uno por defecto.
        grupo_actual = p.get('grupo', 'Sin Grupo')
        
        # OMITIMOS los partidos de la segunda fase para que no rompan las tablas
        if grupo_actual == 'Eliminatoria':
            continue
            
        ea = p['equipo_a']
        eb = p['equipo_b']
        
        for equipo in [ea, eb]:
            if equipo not in stats:
                stats[equipo] = {'Grupo': grupo_actual, 'PJ': 0, 'G': 0, 'E': 0, 'P': 0, 'GF': 0, 'GC': 0, 'Pts': 0}
        
        # Solo calculamos si el partido ya se jugó
        if p.get('goles_a_real') is not None and p.get('goles_b_real') is not None:
            # BLINDAJE: Forzamos a que sean números enteros (int) para evitar errores de tipo texto
            ga = int(p['goles_a_real'])
            gb = int(p['goles_b_real'])
            
            stats[ea]['PJ'] += 1
            stats[eb]['PJ'] += 1
            stats[ea]['GF'] += ga
            stats[ea]['GC'] += gb
            stats[eb]['GF'] += gb
            stats[eb]['GC'] += ga
            
            if ga > gb:
                stats[ea]['G'] += 1; stats[ea]['Pts'] += 3
                stats[eb]['P'] += 1
            elif gb > ga:
                stats[eb]['G'] += 1; stats[eb]['Pts'] += 3
                stats[ea]['P'] += 1
            else:
                stats[ea]['E'] += 1; stats[ea]['Pts'] += 1
                stats[eb]['E'] += 1; stats[eb]['Pts'] += 1

    if not stats:
        st.info("No hay equipos en la fase de grupos para mostrar.")
        return

    # Convertir a DataFrame
    df = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index': 'Equipo'})
    df['DG'] = df['GF'] - df['GC']
    
    grupos = sorted(df['Grupo'].unique())
    
    for g in grupos:
        with st.expander(f"Grupo {g}", expanded=True):
            tabla_g = df[df['Grupo'] == g].sort_values(by=['Pts', 'DG', 'GF'], ascending=False)
            # Usamos st.dataframe que maneja mejor los errores visuales que st.table
            st.dataframe(tabla_g[['Equipo', 'PJ', 'Pts', 'DG', 'GF', 'GC']], hide_index=True, use_container_width=True)