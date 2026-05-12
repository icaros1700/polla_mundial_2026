# 🏆 Polla Mundial 2026

Una aplicación web Full-Stack diseñada para gestionar predicciones futbolísticas, calcular puntuaciones y administrar las tablas de posiciones del Mundial de la FIFA 2026. 

Construida con Python, Streamlit y Supabase.

## ✨ Características Principales

* **🔐 Autenticación Segura:** Sistema de registro e inicio de sesión para usuarios.
* **🏟️ Motor de Predicciones:** Interfaz dinámica para guardar marcadores (bloqueo automático post-guardado).
* **👨‍💻 Panel del Arquitecto (Admin):** Consola oculta con permisos basados en roles (RLS) para inyectar resultados oficiales de la vida real.
* **⚙️ Algoritmo de Puntuación:** Cálculo automático (RPC en Supabase) que otorga +1 punto por adivinar al ganador y +1 punto extra por el marcador exacto.
* **📊 Tablas Dinámicas:** Generación automática de las posiciones de la Fase de Grupos basada en resultados reales.
* **🔍 Transparencia Total:** Ranking global y sistema de auditoría donde los jugadores pueden verificar las predicciones de sus rivales.

## 🛠️ Stack Tecnológico

* **Frontend & Lógica de Servidor:** [Streamlit](https://streamlit.io/) (Python)
* **Manipulación de Datos:** [Pandas](https://pandas.pydata.org/)
* **Backend & Base de Datos:** [Supabase](https://supabase.com/) (PostgreSQL)
* **Seguridad:** Row Level Security (RLS) y Triggers SQL.

## 🚀 Instalación Local

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/icaros1700/polla_mundial_2026.git](https://github.com/icaros1700/polla_mundial_2026.git)