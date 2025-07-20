"""
Zone de contenu principal de l'application
"""
import streamlit as st
from langue.translator import get_text

def render_main_content():
    """Affiche le contenu principal de l'application"""
    
    # Navigation par onglets
    tab1, tab2, tab3 = st.tabs([
        get_text("tab_generator"),
        get_text("tab_history"),
        get_text("tab_settings")
    ])
    
    with tab1:
        render_sql_generator()
    
    with tab2:
        render_query_history()
    
    with tab3:
        render_advanced_settings()

def render_sql_generator():
    """Interface principale de génération SQL"""
    
    # Zone de saisie de la question
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_area(
            get_text("question_label"),
            placeholder=get_text("question_placeholder"),
            height=120,
            key="question_input"
        )
    
    with col2:
        st.markdown(f"### {get_text('examples_title')}")
        
        # Boutons d'exemples
        if st.button("📊 " + get_text("example_sales"), use_container_width=True):
            st.session_state.question_input = "Combien de voitures ont été vendues au total ?"
            st.rerun()
        
        if st.button("📅 " + get_text("example_monthly"), use_container_width=True):
            st.session_state.question_input = "Montrez-moi les ventes par mois cette année"
            st.rerun()
        
        if st.button("🏆 " + get_text("example_brands"), use_container_width=True):
            st.session_state.question_input = "Quelles sont les 10 marques les plus vendues ?"
            st.rerun()
    
    # Boutons d'action
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        generate_clicked = st.button(
            get_text("generate_button"),
            type="primary",
            use_container_width=True,
            disabled=not question
        )
    
    with col2:
        if st.button(get_text("clear_button"), use_container_width=True):
            st.session_state.question_input = ""
            if 'generated_sql' in st.session_state:
                del st.session_state.generated_sql
            st.rerun()
    
    # Génération SQL
    if generate_clicked and question:
        generate_sql_query(question)
    
    # Affichage du résultat
    if 'generated_sql' in st.session_state and st.session_state.generated_sql:
        render_sql_result(st.session_state.generated_sql)

def generate_sql_query(question):
    """Génère la requête SQL"""
    try:
        with st.spinner(get_text("generating")):
            # Import seulement quand nécessaire
            from domain.sql.service import generate_sql_query_only
            from infrastructure.llm import init_llm
            from infrastructure.database import connect_to_redshift
            
            # Utilisation de votre code existant
            llm = init_llm()
            db = connect_to_redshift()
            sql = generate_sql_query_only(question, llm, db)
            
            if sql:
                st.session_state.generated_sql = sql
                
                # Ajouter à l'historique
                if 'query_history' not in st.session_state:
                    st.session_state.query_history = []
                
                st.session_state.query_history.insert(0, {
                    'question': question,
                    'sql': sql,
                    'timestamp': str(st.session_state.get('current_time', 'now'))
                })
                
                st.success(get_text("success_generated"))
            else:
                st.error(get_text("error_generation"))
                
    except Exception as e:
        st.error(f"{get_text('error_generation')}: {str(e)}")

def render_sql_result(sql):
    """Affiche le résultat SQL généré"""
    st.markdown(f"### {get_text('sql_generated')}")
    
    # Affichage du SQL avec coloration syntaxique
    st.code(sql, language="sql")
    
    # Boutons d'action sur le résultat
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.download_button(
            label=get_text("download_button"),
            data=sql,
            file_name="query.sql",
            mime="text/sql",
            use_container_width=True
        ):
            st.success("📥 SQL téléchargé !")
    
    with col2:
        if st.button(get_text("copy_button"), use_container_width=True):
            # Note: La copie dans le presse-papier nécessite JavaScript
            st.info(get_text("copied"))
    
    with col3:
        if st.button(get_text("execute_button"), use_container_width=True):
            st.info("⚡ Fonctionnalité d'exécution à venir...")

def render_query_history():
    """Affiche l'historique des requêtes"""
    st.markdown(f"### {get_text('query_history')}")
    
    if 'query_history' not in st.session_state or not st.session_state.query_history:
        st.info("Aucune requête dans l'historique")
        return
    
    # Affichage de l'historique
    for i, entry in enumerate(st.session_state.query_history):
        with st.expander(f"Query {i+1}: {entry['question'][:50]}..."):
            st.markdown("**Question:**")
            st.write(entry['question'])
            st.markdown("**SQL:**")
            st.code(entry['sql'], language="sql")
            
            if st.button(f"Réutiliser cette requête", key=f"reuse_{i}"):
                st.session_state.question_input = entry['question']
                st.session_state.generated_sql = entry['sql']
                st.rerun()

def render_advanced_settings():
    """Paramètres avancés"""
    st.markdown(f"### {get_text('tab_settings')}")
    
    # Configuration LLM
    st.subheader("🤖 Configuration LLM")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "Température (créativité)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05
        )
    
    with col2:
        max_tokens = st.number_input(
            "Tokens maximum",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100
        )
    
    # Configuration base de données
    st.subheader("🗄️ Configuration Base de Données")
    
    st.info("Configuration chargée depuis .env")
    
    # Actions
    st.subheader("🔧 Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Vider l'historique", use_container_width=True):
            st.session_state.query_history = []
            st.success("Historique vidé !")
    
    with col2:
        if st.button("🔄 Reset paramètres", use_container_width=True):
            # Reset des paramètres à leurs valeurs par défaut
            for key in list(st.session_state.keys()):
                if key.startswith('llm_'):
                    del st.session_state[key]
            st.success("Paramètres réinitialisés !")
