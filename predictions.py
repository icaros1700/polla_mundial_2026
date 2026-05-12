import streamlit as st

def mostrar_carteleras_partidos(supabase, user_id):
    st.markdown("<h2 style='text-align: center;'>🗓️ Cartelera Oficial</h2>", unsafe_allow_html=True)
    
    # 1. Traer todos los partidos
    res_partidos = supabase.table("partidos").select("*").order("id").execute()
    partidos = res_partidos.data
    
    # 2. Traer las predicciones que ya hizo ESTE usuario
    res_preds = supabase.table("predicciones").select("*").eq("user_id", user_id).execute()
    predicciones_usuario = res_preds.data
    
    # Diccionario para buscar rápido si el partido ya está bloqueado
    mapa_predicciones = {p["partido_id"]: p for p in predicciones_usuario}
    
    if not partidos:
        st.info("La FIFA aún no ha cargado los partidos en la Matrix.")
        return

    # 3. Dibujar la cuadrícula (2 columnas para que se vea mejor)
    col1, col2 = st.columns(2)
    
    for index, partido in enumerate(partidos):
        partido_id = partido["id"]
        equipo_a = partido["equipo_a"]
        equipo_b = partido["equipo_b"]
        
        # Alternar entre la columna 1 y 2
        col_actual = col1 if index % 2 == 0 else col2
        
        with col_actual:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align: center;'>⚽ {equipo_a} vs {equipo_b}</h4>", unsafe_allow_html=True)
                
                # --- CONDICIÓN: ¿YA LO JUGÓ? ---
                if partido_id in mapa_predicciones:
                    pred = mapa_predicciones[partido_id]
                    st.success("🔒 Marcador Guardado")
                    
                    c1, c2 = st.columns(2)
                    c1.number_input(equipo_a, value=pred["goles_a_pred"], disabled=True, key=f"dis_a_{partido_id}")
                    c2.number_input(equipo_b, value=pred["goles_b_pred"], disabled=True, key=f"dis_b_{partido_id}")
                    
                else:
                    # --- MODO ACTIVO (Formulario) ---
                    with st.form(key=f"form_partido_{partido_id}"):
                        c1, c2 = st.columns(2)
                        goles_a = c1.number_input(equipo_a, min_value=0, step=1, key=f"a_{partido_id}")
                        goles_b = c2.number_input(equipo_b, min_value=0, step=1, key=f"b_{partido_id}")
                        
                        if st.form_submit_button("💾 Guardar", type="primary", use_container_width=True):
                            resultado = "Gana A" if goles_a > goles_b else ("Gana B" if goles_b > goles_a else "Empate")
                            
                            payload = {
                                "user_id": user_id,
                                "partido_id": partido_id,
                                "goles_a_pred": goles_a,
                                "goles_b_pred": goles_b,
                                "resultado_pred": resultado
                            }
                            
                            try:
                                supabase.table("predicciones").insert(payload).execute()
                                st.rerun() 
                            except Exception as e:
                                st.error("Error al guardar la predicción.")