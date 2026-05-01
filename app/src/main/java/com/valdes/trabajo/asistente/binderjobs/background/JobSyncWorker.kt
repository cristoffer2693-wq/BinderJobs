package com.valdes.trabajo.asistente.binderjobs.background

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.valdes.trabajo.asistente.binderjobs.MainActivity
import com.valdes.trabajo.asistente.binderjobs.R
import com.valdes.trabajo.asistente.binderjobs.data.JobRepository
import com.valdes.trabajo.asistente.binderjobs.data.UserPreferencesRepository
import com.valdes.trabajo.asistente.binderjobs.data.model.JobOffer
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withContext

class JobSyncWorker(
    appContext: Context,
    params: WorkerParameters,
) : CoroutineWorker(appContext, params) {

    companion object {
        private const val CHANNEL_ID = "binder_jobs_updates"
        private const val NOTIFICATION_ID = 1001
        private const val PREFS_LAST_JOB_IDS = "last_notified_job_ids"
    }

    override suspend fun doWork(): Result {
        return withContext(Dispatchers.IO) {
            try {
                val prefsRepo = UserPreferencesRepository(applicationContext)
                val prefs = prefsRepo.preferences.first()
                
                if (!prefs.backgroundSearchEnabled) {
                    return@withContext Result.success()
                }
                
                val jobs = JobRepository().backgroundSearch(prefs)
                
                if (jobs.isEmpty()) {
                    return@withContext Result.success()
                }
                
                val relevantJobs = jobs.filter { it.score >= prefs.minScoreToNotify }
                
                if (relevantJobs.isEmpty()) {
                    return@withContext Result.success()
                }
                
                val newJobs = filterNewJobs(relevantJobs)
                
                if (newJobs.isNotEmpty() && prefs.notificationsEnabled) {
                    saveLastJobIds(newJobs.map { it.id })
                    showNotification(newJobs)
                }
                
                Result.success()
            } catch (e: Exception) {
                Result.retry()
            }
        }
    }

    private fun filterNewJobs(jobs: List<JobOffer>): List<JobOffer> {
        val sharedPrefs = applicationContext.getSharedPreferences(
            "job_sync_prefs", 
            Context.MODE_PRIVATE
        )
        val lastIds = sharedPrefs.getStringSet(PREFS_LAST_JOB_IDS, emptySet()) ?: emptySet()
        
        return jobs.filter { it.id !in lastIds }
    }

    private fun saveLastJobIds(ids: List<String>) {
        val sharedPrefs = applicationContext.getSharedPreferences(
            "job_sync_prefs",
            Context.MODE_PRIVATE
        )
        val currentIds = sharedPrefs.getStringSet(PREFS_LAST_JOB_IDS, emptySet())?.toMutableSet() 
            ?: mutableSetOf()
        
        currentIds.addAll(ids)
        
        val limitedIds = currentIds.toList().takeLast(200).toSet()
        
        sharedPrefs.edit()
            .putStringSet(PREFS_LAST_JOB_IDS, limitedIds)
            .apply()
    }

    private fun showNotification(jobs: List<JobOffer>) {
        createNotificationChannel()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    applicationContext,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                return
            }
        }

        val intent = Intent(applicationContext, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        val pendingIntent = PendingIntent.getActivity(
            applicationContext,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val count = jobs.size
        val topJob = jobs.maxByOrNull { it.score }
        
        val title = if (count == 1) {
            "Nueva oferta de empleo"
        } else {
            "Nuevas ofertas de empleo"
        }
        
        val text = if (count == 1 && topJob != null) {
            "${topJob.title} en ${topJob.company}"
        } else {
            "Se encontraron $count ofertas que coinciden con tu búsqueda"
        }

        val bigText = buildString {
            jobs.take(5).forEach { job ->
                append("• ${job.title}")
                if (job.company.isNotBlank()) {
                    append(" - ${job.company}")
                }
                if (job.city.isNotBlank()) {
                    append(" (${job.city})")
                }
                append("\n")
            }
            if (jobs.size > 5) {
                append("... y ${jobs.size - 5} más")
            }
        }

        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(bigText))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setNumber(count)
            .build()

        NotificationManagerCompat.from(applicationContext).notify(NOTIFICATION_ID, notification)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = applicationContext.getString(R.string.notification_channel_name)
            val description = applicationContext.getString(R.string.notification_channel_description)
            val importance = NotificationManager.IMPORTANCE_DEFAULT
            
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                this.description = description
            }
            
            val manager = applicationContext.getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }
}
