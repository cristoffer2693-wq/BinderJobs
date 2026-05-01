package com.valdes.trabajo.asistente.binderjobs.data

import android.content.Context
import androidx.datastore.preferences.preferencesDataStore

val Context.dataStore by preferencesDataStore(name = "binder_jobs_prefs")
