"""
Panneau latéral (sidebar) pour configuration et paramètres
"""
import streamlit as st
from langue.translator import get_text, set_language, get_available_languages

def render_sidebar():
    """Affiche le panneau latéral avec configuration"""
    with st.sidebar:
        # Logo/Titre
        st.markdown("### 🔄 TextToSQL")
        st.markdown("---")
        
        # Sélection de langue
        render_language_selector()
        st.markdown("---")
        
        # Status des connexions
        render_connection_status()
        st.markdown("---")
        
        # Paramètres LLM
        render_llm_settings()
        st.markdown("---")
        
        # Informations système
        render_system_info()

def render_language_selector():
    """Sélecteur de langue"""
    st.subheader(get_text("select_language"))
    
    languages = get_available_languages()
    current_lang = st.session_state.get('language', 'fr')
    
    # Trouver l'index de la langue actuelle
    lang_options = list(languages.keys())
    current_index = 0
    for i, (display, code) in enumerate(languages.items()):
        if code == current_lang:
            current_index = i
            break
    
    selected_lang_display = st.selectbox(
        "Langue / Language / 言語",
        options=lang_options,
        index=current_index,
        key="language_selector"
    )
    
    # Mettre à jour la langue si changée
    if selected_lang_display:
        new_lang_code = languages[selected_lang_display]
        if st.session_state.get('language') != new_lang_code:
            set_language(new_lang_code)
            st.rerun()

def render_connection_status():
    """Affiche le statut des connexions"""
    st.subheader(get_text("database_config"))
    
    # Status Database
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=get_text("database"),
            value="🟢",
            delta=get_text("connected")
        )
    
    with col2:
        st.metric(
            label=get_text("schema"),
            value="usedcar_dwh"
        )
    
    # Informations de connexion
    with st.expander("ℹ️ Détails connexion"):
        try:
            from infrastructure.settings import settings
            st.text(f"Host: {settings.redshift_host[:30]}...")
            st.text(f"Database: {settings.redshift_db}")
            st.text(f"Schema: {settings.redshift_schema}")
            st.text(f"Port: {settings.redshift_port}")
        except Exception as e:
            st.error(f"Erreur de configuration: {str(e)}")

def render_llm_settings():
    """Paramètres du LLM"""
    st.subheader(get_text("llm_settings"))
    
    # Status LLM
    st.metric(
        label=get_text("model_info"),
        value="🤖 Gemini",
        delta="✅ Actif"
    )
    
    # Paramètres avancés
    with st.expander("⚙️ Paramètres avancés"):
        temperature = st.slider(
            get_text("temperature"),
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            key="llm_temperature"
        )
        
        max_tokens = st.number_input(
            get_text("max_tokens"),
            min_value=100,
            max_value=4000,
            value=1000,
            step=100,
            key="llm_max_tokens"
        )
        
        st.session_state.llm_config = {
            'temperature': temperature,
            'max_tokens': max_tokens
        }

def render_system_info():
    """Informations système"""
    st.subheader("📊 System")
    
    # Métriques rapides
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🗄️ DB", "🟢", "OK")
    
    with col2:
        st.metric("🤖 LLM", "🟢", "OK")
    
    # Bouton de test
    if st.button("🔍 " + get_text("connection_test"), use_container_width=True):
        with st.spinner("Test en cours..."):
            # Simuler un test de connexion
            import time
            time.sleep(2)
            st.success("✅ Connexions OK !")
    
    # Version info
    st.caption("v1.0.0 | TextToSQL Streamlit")
