package com.valdes.trabajo.asistente.binderjobs.ui.dashboard

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.valdes.trabajo.asistente.binderjobs.data.LocationDetector
import com.valdes.trabajo.asistente.binderjobs.data.UserPreferencesRepository
import com.valdes.trabajo.asistente.binderjobs.data.model.UserPreferences
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

class DashboardViewModel(application: Application) : AndroidViewModel(application) {
    private val preferencesRepository = UserPreferencesRepository(application)
    private val locationDetector = LocationDetector()

    private val _preferences = MutableStateFlow(UserPreferences())
    val preferences: StateFlow<UserPreferences> = _preferences.asStateFlow()

    init {
        viewModelScope.launch {
            preferencesRepository.preferences.collect { current ->
                _preferences.value = current
            }
        }
    }

    fun detectLocationIfMissing() {
        viewModelScope.launch {
            val current = preferencesRepository.preferences.first()
            if (current.country.isNotBlank() && current.city.isNotBlank()) return@launch
            val detected = locationDetector.detectByIp() ?: return@launch
            preferencesRepository.update(
                current.copy(
                    country = detected.country,
                    state = detected.state,
                    city = detected.city,
                )
            )
        }
    }

    fun updateSwitches(backgroundEnabled: Boolean, notificationsEnabled: Boolean) {
        viewModelScope.launch {
            val current = preferencesRepository.preferences.first()
            preferencesRepository.update(
                current.copy(
                    backgroundSearchEnabled = backgroundEnabled,
                    notificationsEnabled = notificationsEnabled,
                )
            )
        }
    }

    fun updateLocation(country: String, state: String, city: String, radiusKm: Int) {
        viewModelScope.launch {
            val current = preferencesRepository.preferences.first()
            preferencesRepository.update(
                current.copy(
                    country = country,
                    state = state,
                    city = city,
                    radiusKm = radiusKm,
                )
            )
        }
    }
}