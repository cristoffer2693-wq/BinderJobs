package com.valdes.trabajo.asistente.binderjobs.data.model

data class UserPreferences(
    // Ubicación del usuario
    val country: String = "Bolivia",
    val state: String = "",  // Departamento (ej: "Tarija")
    val city: String = "",   // Ciudad (ej: "Tarija")
    val radiusKm: Int = 50,
    
    // Preferencias de búsqueda
    val preferredRole: String = "",
    val preferredModality: String = "",  // Remoto, Presencial, Híbrido, o vacío para todos
    val preferredLanguage: String = "es",
    val salaryMin: Int = 0,
    
    // Configuración de búsqueda en segundo plano
    val backgroundSearchEnabled: Boolean = true,
    val notificationsEnabled: Boolean = true,
    val searchFrequencyMinutes: Int = 30,
    val minScoreToNotify: Float = 0.3f,
    
    // Aprendizaje de preferencias
    val searchHistory: List<String> = emptyList(),
    val clickedOfferIds: List<String> = emptyList(),
    val savedOfferIds: List<String> = emptyList(),
    val excludedCompanies: List<String> = emptyList(),
    val preferredSources: List<String> = emptyList(),
    
    // Últimas búsquedas exitosas (para sugerencias)
    val recentSearches: List<String> = emptyList(),
    
    // Flag para detectar si es primera vez
    val isFirstLaunch: Boolean = true,
    val locationDetectedAutomatically: Boolean = false,
)

data class SearchHistoryItem(
    val query: String,
    val timestamp: Long,
    val resultsCount: Int,
)

data class LearnedPreference(
    val keyword: String,
    val weight: Float,  // 0.0 a 1.0, mayor = más preferido
    val source: String, // "search", "click", "save"
)
