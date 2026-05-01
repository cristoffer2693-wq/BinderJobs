package com.valdes.trabajo.asistente.binderjobs.data

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import com.valdes.trabajo.asistente.binderjobs.data.model.UserPreferences
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class UserPreferencesRepository(private val context: Context) {
    
    private object Keys {
        // Ubicación
        val country = stringPreferencesKey("country")
        val state = stringPreferencesKey("state")
        val city = stringPreferencesKey("city")
        val radiusKm = intPreferencesKey("radius_km")
        
        // Preferencias de búsqueda
        val preferredRole = stringPreferencesKey("preferred_role")
        val preferredModality = stringPreferencesKey("preferred_modality")
        val preferredLanguage = stringPreferencesKey("preferred_language")
        val salaryMin = intPreferencesKey("salary_min")
        
        // Configuración de segundo plano
        val backgroundSearchEnabled = booleanPreferencesKey("background_search_enabled")
        val notificationsEnabled = booleanPreferencesKey("notifications_enabled")
        val searchFrequencyMinutes = intPreferencesKey("search_frequency_minutes")
        val minScoreToNotify = floatPreferencesKey("min_score_to_notify")
        
        // Aprendizaje
        val searchHistory = stringSetPreferencesKey("search_history")
        val clickedOfferIds = stringSetPreferencesKey("clicked_offer_ids")
        val savedOfferIds = stringSetPreferencesKey("saved_offer_ids")
        val excludedCompanies = stringSetPreferencesKey("excluded_companies")
        val preferredSources = stringSetPreferencesKey("preferred_sources")
        val recentSearches = stringSetPreferencesKey("recent_searches")
        
        // Estado
        val isFirstLaunch = booleanPreferencesKey("is_first_launch")
        val locationDetectedAutomatically = booleanPreferencesKey("location_detected_auto")
    }
    
    val preferences: Flow<UserPreferences> = context.dataStore.data.map { prefs ->
        UserPreferences(
            country = prefs[Keys.country] ?: "Bolivia",
            state = prefs[Keys.state].orEmpty(),
            city = prefs[Keys.city].orEmpty(),
            radiusKm = prefs[Keys.radiusKm] ?: 50,
            preferredRole = prefs[Keys.preferredRole].orEmpty(),
            preferredModality = prefs[Keys.preferredModality].orEmpty(),
            preferredLanguage = prefs[Keys.preferredLanguage] ?: "es",
            salaryMin = prefs[Keys.salaryMin] ?: 0,
            backgroundSearchEnabled = prefs[Keys.backgroundSearchEnabled] ?: true,
            notificationsEnabled = prefs[Keys.notificationsEnabled] ?: true,
            searchFrequencyMinutes = prefs[Keys.searchFrequencyMinutes] ?: 30,
            minScoreToNotify = prefs[Keys.minScoreToNotify] ?: 0.3f,
            searchHistory = prefs[Keys.searchHistory]?.toList() ?: emptyList(),
            clickedOfferIds = prefs[Keys.clickedOfferIds]?.toList() ?: emptyList(),
            savedOfferIds = prefs[Keys.savedOfferIds]?.toList() ?: emptyList(),
            excludedCompanies = prefs[Keys.excludedCompanies]?.toList() ?: emptyList(),
            preferredSources = prefs[Keys.preferredSources]?.toList() ?: emptyList(),
            recentSearches = prefs[Keys.recentSearches]?.toList() ?: emptyList(),
            isFirstLaunch = prefs[Keys.isFirstLaunch] ?: true,
            locationDetectedAutomatically = prefs[Keys.locationDetectedAutomatically] ?: false,
        )
    }
    
    suspend fun update(preferences: UserPreferences) {
        context.dataStore.edit { prefs ->
            prefs[Keys.country] = preferences.country
            prefs[Keys.state] = preferences.state
            prefs[Keys.city] = preferences.city
            prefs[Keys.radiusKm] = preferences.radiusKm
            prefs[Keys.preferredRole] = preferences.preferredRole
            prefs[Keys.preferredModality] = preferences.preferredModality
            prefs[Keys.preferredLanguage] = preferences.preferredLanguage
            prefs[Keys.salaryMin] = preferences.salaryMin
            prefs[Keys.backgroundSearchEnabled] = preferences.backgroundSearchEnabled
            prefs[Keys.notificationsEnabled] = preferences.notificationsEnabled
            prefs[Keys.searchFrequencyMinutes] = preferences.searchFrequencyMinutes
            prefs[Keys.minScoreToNotify] = preferences.minScoreToNotify
            prefs[Keys.searchHistory] = preferences.searchHistory.toSet()
            prefs[Keys.clickedOfferIds] = preferences.clickedOfferIds.toSet()
            prefs[Keys.savedOfferIds] = preferences.savedOfferIds.toSet()
            prefs[Keys.excludedCompanies] = preferences.excludedCompanies.toSet()
            prefs[Keys.preferredSources] = preferences.preferredSources.toSet()
            prefs[Keys.recentSearches] = preferences.recentSearches.toSet()
            prefs[Keys.isFirstLaunch] = preferences.isFirstLaunch
            prefs[Keys.locationDetectedAutomatically] = preferences.locationDetectedAutomatically
        }
    }
    
    suspend fun updateLocation(country: String, state: String, city: String) {
        context.dataStore.edit { prefs ->
            prefs[Keys.country] = country
            prefs[Keys.state] = state
            prefs[Keys.city] = city
            prefs[Keys.locationDetectedAutomatically] = true
            prefs[Keys.isFirstLaunch] = false
        }
    }
    
    suspend fun addSearchToHistory(query: String) {
        if (query.isBlank()) return
        context.dataStore.edit { prefs ->
            val current = prefs[Keys.recentSearches]?.toMutableSet() ?: mutableSetOf()
            current.add(query.trim())
            // Mantener solo las últimas 20 búsquedas
            val limited = current.toList().takeLast(20).toSet()
            prefs[Keys.recentSearches] = limited
        }
    }
    
    suspend fun recordOfferClick(offerId: String) {
        context.dataStore.edit { prefs ->
            val current = prefs[Keys.clickedOfferIds]?.toMutableSet() ?: mutableSetOf()
            current.add(offerId)
            // Mantener solo los últimos 100 clicks
            val limited = current.toList().takeLast(100).toSet()
            prefs[Keys.clickedOfferIds] = limited
        }
    }
    
    suspend fun saveOffer(offerId: String) {
        context.dataStore.edit { prefs ->
            val current = prefs[Keys.savedOfferIds]?.toMutableSet() ?: mutableSetOf()
            current.add(offerId)
            prefs[Keys.savedOfferIds] = current
        }
    }
    
    suspend fun unsaveOffer(offerId: String) {
        context.dataStore.edit { prefs ->
            val current = prefs[Keys.savedOfferIds]?.toMutableSet() ?: mutableSetOf()
            current.remove(offerId)
            prefs[Keys.savedOfferIds] = current
        }
    }
    
    suspend fun isOfferSaved(offerId: String): Boolean {
        var saved = false
        context.dataStore.edit { prefs ->
            saved = prefs[Keys.savedOfferIds]?.contains(offerId) ?: false
        }
        return saved
    }
    
    suspend fun excludeCompany(company: String) {
        context.dataStore.edit { prefs ->
            val current = prefs[Keys.excludedCompanies]?.toMutableSet() ?: mutableSetOf()
            current.add(company.trim().lowercase())
            prefs[Keys.excludedCompanies] = current
        }
    }
    
    suspend fun clearSearchHistory() {
        context.dataStore.edit { prefs ->
            prefs[Keys.recentSearches] = emptySet()
            prefs[Keys.searchHistory] = emptySet()
        }
    }
    
    suspend fun setFirstLaunchComplete() {
        context.dataStore.edit { prefs ->
            prefs[Keys.isFirstLaunch] = false
        }
    }
}
