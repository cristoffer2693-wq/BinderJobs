package com.valdes.trabajo.asistente.binderjobs.background

import android.content.Context
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

object SyncScheduler {
    
    private const val WORK_NAME = "binder_jobs_periodic_sync"
    private const val MIN_INTERVAL_MINUTES = 15L
    
    fun schedule(context: Context, frequencyMinutes: Int = 30) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
            
        val interval = frequencyMinutes.toLong().coerceAtLeast(MIN_INTERVAL_MINUTES)
        
        val workRequest = PeriodicWorkRequestBuilder<JobSyncWorker>(
            interval,
            TimeUnit.MINUTES,
        )
            .setConstraints(constraints)
            .setInitialDelay(5, TimeUnit.MINUTES)
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            workRequest,
        )
    }
    
    fun scheduleImmediate(context: Context) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
            
        val workRequest = OneTimeWorkRequestBuilder<JobSyncWorker>()
            .setConstraints(constraints)
            .build()
            
        WorkManager.getInstance(context).enqueue(workRequest)
    }
    
    fun cancel(context: Context) {
        WorkManager.getInstance(context).cancelUniqueWork(WORK_NAME)
    }
    
    fun updateFrequency(context: Context, frequencyMinutes: Int) {
        cancel(context)
        schedule(context, frequencyMinutes)
    }
}
