package com.valdes.trabajo.asistente.binderjobs.ui.home

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.valdes.trabajo.asistente.binderjobs.data.JobRepository
import com.valdes.trabajo.asistente.binderjobs.data.UserPreferencesRepository
import com.valdes.trabajo.asistente.binderjobs.data.model.JobOffer
import com.valdes.trabajo.asistente.binderjobs.data.model.UserPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class HomeViewModel(application: Application) : AndroidViewModel(application) {
    
    private val userPreferencesRepository = UserPreferencesRepository(application)
    private val jobRepository = JobRepository()

    private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    private val _savedJobs = MutableStateFlow<List<JobOffer>>(emptyList())
    val savedJobs: StateFlow<List<JobOffer>> = _savedJobs.asStateFlow()

    // Filtros activos
    private var remoteFilter = false
    private var nearbyFilter = false
    private var withSalaryFilter = false
    private var fullTimeFilter = false
    private var lastQuery = ""

    fun search(query: String) {
        lastQuery = query
        viewModelScope.launch {
            _uiState.value = HomeUiState.Loading
            
            runCatching {
                val currentPrefs = userPreferencesRepository.preferences.first()
                
                withContext(Dispatchers.IO) {
                    val jobs = if (nearbyFilter && currentPrefs.city.isNotBlank()) {
                        jobRepository.searchNearbyJobs(currentPrefs, query)
                    } else {
                        jobRepository.searchJobs(query, currentPrefs)
                    }
                    
                    applyFilters(jobs, currentPrefs)
                }
            }.onSuccess { jobs ->
                _uiState.value = if (jobs.isEmpty()) {
                    HomeUiState.Empty("No se encontraron empleos con estos criterios. Intenta con otros términos.")
                } else {
                    HomeUiState.Success(jobs)
                }
            }.onFailure { error ->
                _uiState.value = HomeUiState.Error(
                    "Error buscando empleos: ${error.message ?: "Verifica tu conexión a internet"}"
                )
            }
        }
    }

    private fun applyFilters(jobs: List<JobOffer>, prefs: UserPreferences): List<JobOffer> {
        var filtered = jobs
        
        if (remoteFilter) {
            filtered = filtered.filter { it.isRemote }
        }
        
        if (nearbyFilter && prefs.city.isNotBlank()) {
            filtered = filtered.filter { job ->
                job.city.contains(prefs.city, ignoreCase = true) ||
                job.city.contains(prefs.state, ignoreCase = true) ||
                job.isRemote
            }
        }
        
        if (withSalaryFilter) {
            filtered = filtered.filter { !it.salary.isNullOrBlank() }
        }
        
        if (fullTimeFilter) {
            filtered = filtered.filter { job ->
                val text = "${job.title} ${job.summary}".lowercase()
                !text.contains("part-time") && 
                !text.contains("medio tiempo") && 
                !text.contains("freelance")
            }
        }
        
        return filtered
    }

    fun setRemoteFilter(enabled: Boolean) {
        remoteFilter = enabled
    }

    fun setNearbyFilter(enabled: Boolean) {
        nearbyFilter = enabled
    }

    fun setWithSalaryFilter(enabled: Boolean) {
        withSalaryFilter = enabled
    }

    fun setFullTimeFilter(enabled: Boolean) {
        fullTimeFilter = enabled
    }

    fun saveJob(jobOffer: JobOffer) {
        viewModelScope.launch {
            userPreferencesRepository.saveOffer(jobOffer.id)
            _savedJobs.value = (_savedJobs.value + jobOffer).distinctBy { it.id }
        }
    }

    fun recordClick(offerId: String) {
        viewModelScope.launch {
            userPreferencesRepository.recordOfferClick(offerId)
        }
    }

    fun addToSearchHistory(query: String) {
        if (query.isBlank()) return
        viewModelScope.launch {
            userPreferencesRepository.addSearchToHistory(query)
        }
    }

    suspend fun getCurrentPreferences(): UserPreferences {
        return userPreferencesRepository.preferences.first()
    }

    fun refreshWithCurrentFilters() {
        search(lastQuery)
    }
}
