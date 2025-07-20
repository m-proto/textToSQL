"""
Module de health checks pour surveiller l'état des services
"""
import time
from typing import Dict, Tuple
import streamlit as st

# Cache des statuts avec TTL de 30 secondes
CACHE_TTL = 30
_status_cache = {}

def get_cached_status(service_name: str, check_function) -> Tuple[str, str]:
    """
    Récupère le statut d'un service avec mise en cache
    
    Args:
        service_name: Nom du service (db, llm)
        check_function: Fonction de vérification à appeler
        
    Returns:
        Tuple (status, message) où status = "OK", "WARNING", "ERROR"
    """
    current_time = time.time()
    cache_key = f"{service_name}_status"
    cache_time_key = f"{service_name}_time"
    
    # Vérifier si le cache est encore valide
    if (cache_key in _status_cache and 
        cache_time_key in _status_cache and
        current_time - _status_cache[cache_time_key] < CACHE_TTL):
        return _status_cache[cache_key]
    
    # Exécuter le check et mettre en cache
    try:
        status, message = check_function()
        _status_cache[cache_key] = (status, message)
        _status_cache[cache_time_key] = current_time
        return status, message
    except Exception as e:
        error_result = ("ERROR", f"Check failed: {str(e)}")
        _status_cache[cache_key] = error_result
        _status_cache[cache_time_key] = current_time
        return error_result

def check_database_connection() -> Tuple[str, str]:
    """
    Vérifie la connexion à la base de données Redshift
    
    Returns:
        Tuple (status, message)
    """
    try:
        from infrastructure.database import connect_to_redshift
        
        start_time = time.time()
        db = connect_to_redshift()
        
        # Test simple de connexion
        result = db.execute("SELECT 1 as test_connection")
        if result:
            connection_time = round((time.time() - start_time) * 1000)
            
            if connection_time < 500:  # < 500ms = OK
                return "OK", f"Connected ({connection_time}ms)"
            elif connection_time < 2000:  # < 2s = WARNING
                return "WARNING", f"Slow ({connection_time}ms)"
            else:  # > 2s = ERROR
                return "ERROR", f"Too slow ({connection_time}ms)"
        else:
            return "ERROR", "No response"
            
    except Exception as e:
        return "ERROR", f"Connection failed: {str(e)[:50]}"

def check_llm_availability() -> Tuple[str, str]:
    """
    Vérifie la disponibilité du LLM Gemini
    
    Returns:
        Tuple (status, message)
    """
    try:
        from infrastructure.llm import init_llm
        
        start_time = time.time()
        llm = init_llm()
        
        # Test simple avec une requête courte
        response = llm.invoke("SELECT 1")
        
        if response and len(str(response).strip()) > 0:
            response_time = round((time.time() - start_time) * 1000)
            
            if response_time < 1000:  # < 1s = OK
                return "OK", f"Responsive ({response_time}ms)"
            elif response_time < 5000:  # < 5s = WARNING
                return "WARNING", f"Slow ({response_time}ms)"
            else:  # > 5s = ERROR
                return "ERROR", f"Too slow ({response_time}ms)"
        else:
            return "ERROR", "No valid response"
            
    except Exception as e:
        return "ERROR", f"LLM unavailable: {str(e)[:50]}"

def get_system_status() -> Dict[str, Tuple[str, str]]:
    """
    Récupère l'état de tous les services système
    
    Returns:
        Dict avec les statuts de chaque service
    """
    return {
        "database": get_cached_status("database", check_database_connection),
        "llm": get_cached_status("llm", check_llm_availability)
    }

def get_status_emoji(status: str) -> str:
    """
    Retourne l'emoji correspondant au statut
    
    Args:
        status: "OK", "WARNING", "ERROR"
        
    Returns:
        Emoji correspondant
    """
    emoji_map = {
        "OK": "🟢",
        "WARNING": "🟡", 
        "ERROR": "🔴"
    }
    return emoji_map.get(status, "⚫")

def clear_health_cache():
    """Vide le cache des statuts (utile pour forcer un refresh)"""
    global _status_cache
    _status_cache.clear()
