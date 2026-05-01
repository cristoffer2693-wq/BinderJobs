package com.valdes.trabajo.asistente.binderjobs.data.model

data class JobOffer(
    val id: String,
    val title: String,
    val company: String,
    val country: String,
    val city: String,
    val modality: String,
    val salary: String?,
    val summary: String,
    val sourceName: String,
    val url: String,
    val publishedAt: String,
    val score: Double = 0.0,
    val relevanceScore: Double = 0.0,
    val locationScore: Double = 0.0,
    val preferenceScore: Double = 0.0,
) {
    val displayLocation: String
        get() = when {
            city.isNotBlank() && country.isNotBlank() -> "$city, $country"
            city.isNotBlank() -> city
            country.isNotBlank() -> country
            else -> "Ubicación no especificada"
        }
    
    val isRemote: Boolean
        get() = modality.equals("Remoto", ignoreCase = true) || 
                city.equals("Remoto", ignoreCase = true) ||
                city.equals("Remote", ignoreCase = true)
    
    val hasHighRelevance: Boolean
        get() = score >= 0.6
    
    val isNearby: Boolean
        get() = locationScore >= 0.5
    
    val scorePercentage: Int
        get() = (score * 100).toInt()
}
