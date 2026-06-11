import streamlit as st
import pandas as pd
from ui import page_header, section_title

def mostrar_panel_admin(supabase):
    page_header(
        "Panel del Arquitecto",
        "Publica resultados oficiales y recalcula puntos sin salir del flujo de administracion.",
        "Administracion",
    )
    st.info("Solo tu tienes acceso a este panel. Aqui ingresas los resultados reales.")

    # 1. Traer SOLO los partidos que aún no tienen resultado oficial
    res = supabase.table("partidos").select("*").is_("goles_a_real", "null").execute()
    df_partidos = pd.DataFrame(res.data)

    if df_partidos.empty:
        st.success("✅ Todos los partidos actuales ya tienen su resultado oficial cargado.")
        return

    section_title("Cargar resultado oficial", "Selecciona un partido finalizado y confirma el marcador real.")

    with st.container(border=True):
        
        # 2. Selector de partido (formato: "Equipo A vs Equipo B")
        opciones_partidos = df_partidos["id"].tolist()
        formato_opciones = lambda x: f"{df_partidos[df_partidos['id']==x]['equipo_a'].values[0]} vs {df_partidos[df_partidos['id']==x]['equipo_b'].values[0]}"
        
        partido_sel = st.selectbox("Seleccionar Partido Finalizado", options=opciones_partidos, format_func=formato_opciones)
        
        # 3. Inputs para el resultado REAL
        c1, c2 = st.columns(2)
        equipo_a_nombre = df_partidos[df_partidos['id']==partido_sel]['equipo_a'].values[0]
        equipo_b_nombre = df_partidos[df_partidos['id']==partido_sel]['equipo_b'].values[0]
        
        goles_a = c1.number_input(f"Goles Oficiales: {equipo_a_nombre}", min_value=0, step=1)
        goles_b = c2.number_input(f"Goles Oficiales: {equipo_b_nombre}", min_value=0, step=1)

        # 4. Botón de Ejecución Maestra
        if st.button("🏆 PUBLICAR RESULTADO Y CALCULAR PUNTOS", type="primary", use_container_width=True):
            with st.spinner("Procesando datos en la Matrix..."):
                actualizar_y_calificar(supabase, partido_sel, goles_a, goles_b)

def actualizar_y_calificar(supabase, partido_id, g_a, g_b):
    # A. Determinar estado real del partido
    estado_oficial = "Gana A" if g_a > g_b else ("Gana B" if g_b > g_a else "Empate")
    
    try:
        # B. Guardar resultado oficial en la tabla 'partidos'
        supabase.table("partidos").update({
            "goles_a_real": g_a,
            "goles_b_real": g_b,
            "estado_real": estado_oficial
        }).eq("id", partido_id).execute()
        
        # C. Traer TODAS las predicciones hechas para este partido
        preds = supabase.table("predicciones").select("*").eq("partido_id", partido_id).execute()
        
        usuarios_procesados = 0
        puntos_totales_repartidos = 0
        
        for p in preds.data:
            puntos_ganados = 0
            
            # REGLA 1: Adivinó quién ganaba o si empataban (+1 punto)
            if p["resultado_pred"] == estado_oficial:
                puntos_ganados += 1
                
                # REGLA 2: Adivinó el marcador exacto (+1 punto extra)
                if p["goles_a_pred"] == g_a and p["goles_b_pred"] == g_b:
                    puntos_ganados += 1
            
            if puntos_ganados > 0:
                # 1. Guardamos cuántos puntos ganó en esta predicción específica
                supabase.table("predicciones").update({"puntos_ganados": puntos_ganados}).eq("id", p["id"]).execute()
                
                # 2. Llamamos a la función mágica (RPC) que creamos en SQL para sumar a su total
                supabase.rpc('incrementar_puntos_usuario', {'user_id_input': p['user_id'], 'puntos_input': puntos_ganados}).execute()
                puntos_totales_repartidos += puntos_ganados
                
            usuarios_procesados += 1
            
        st.success(f"¡Cálculo Finalizado! Se procesaron {usuarios_procesados} usuarios y se repartieron {puntos_totales_repartidos} puntos.")
        st.cache_data.clear()
        st.rerun() # Refresca para que el partido desaparezca de la lista
        
    except Exception as e:
        st.error(f"Error crítico durante el cálculo: {e}")
