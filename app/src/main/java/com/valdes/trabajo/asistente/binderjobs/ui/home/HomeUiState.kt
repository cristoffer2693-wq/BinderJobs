package com.valdes.trabajo.asistente.binderjobs.ui.home

import com.valdes.trabajo.asistente.binderjobs.data.model.JobOffer

sealed class HomeUiState {
    data object Loading : HomeUiState()

    data class Success(val jobs: List<JobOffer>) : HomeUiState()

    data class Empty(val message: String) : HomeUiState()

    data class Error(val message: String) : HomeUiState()
}
