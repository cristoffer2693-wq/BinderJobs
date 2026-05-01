package com.valdes.trabajo.asistente.binderjobs.ui.home

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.valdes.trabajo.asistente.binderjobs.data.model.JobOffer
import com.valdes.trabajo.asistente.binderjobs.databinding.ItemJobOfferBinding

class JobOfferAdapter(
    private val onOpenClick: (JobOffer) -> Unit,
    private val onSaveClick: (JobOffer) -> Unit,
) : ListAdapter<JobOffer, JobOfferAdapter.JobViewHolder>(DiffCb) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): JobViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        return JobViewHolder(ItemJobOfferBinding.inflate(inflater, parent, false))
    }

    override fun onBindViewHolder(holder: JobViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class JobViewHolder(private val binding: ItemJobOfferBinding) :
        RecyclerView.ViewHolder(binding.root) {
        
        fun bind(item: JobOffer) {
            binding.jobTitle.text = item.title
            binding.jobCompany.text = item.company
            binding.jobLocation.text = item.displayLocation
            binding.jobSummary.text = item.summary
            binding.jobModality.text = item.modality
            
            binding.jobSource.text = buildString {
                append(item.sourceName)
                if (item.publishedAt.isNotBlank()) {
                    append(" · ")
                    append(item.publishedAt)
                }
            }
            
            // Mostrar salario si está disponible
            if (!item.salary.isNullOrBlank()) {
                binding.jobSalary.visibility = View.VISIBLE
                binding.jobSalary.text = item.salary
            } else {
                binding.jobSalary.visibility = View.GONE
            }
            
            // Badge de alta relevancia (score >= 0.6)
            if (item.hasHighRelevance) {
                binding.relevanceBadge.visibility = View.VISIBLE
            } else {
                binding.relevanceBadge.visibility = View.GONE
            }
            
            // Badge de ubicación cercana
            if (item.isNearby && !item.isRemote) {
                binding.nearbyBadge.visibility = View.VISIBLE
            } else {
                binding.nearbyBadge.visibility = View.GONE
            }
            
            // Indicador de score
            val scorePercentage = item.scorePercentage
            if (scorePercentage > 0) {
                binding.scoreContainer.visibility = View.VISIBLE
                binding.scoreProgress.progress = scorePercentage
                binding.scoreText.text = "$scorePercentage%"
            } else {
                binding.scoreContainer.visibility = View.GONE
            }
            
            // Color del chip de modalidad según el tipo
            val modalityBackground = when {
                item.isRemote -> android.R.color.holo_blue_light
                item.modality.equals("Presencial", ignoreCase = true) -> android.R.color.holo_orange_light
                item.modality.equals("Híbrido", ignoreCase = true) -> android.R.color.holo_purple
                else -> android.R.color.darker_gray
            }
            
            // Acciones
            binding.openOfferButton.setOnClickListener { onOpenClick(item) }
            binding.saveOfferButton.setOnClickListener { onSaveClick(item) }
            
            // Click en toda la tarjeta también abre la oferta
            binding.root.setOnClickListener { onOpenClick(item) }
        }
    }

    private object DiffCb : DiffUtil.ItemCallback<JobOffer>() {
        override fun areItemsTheSame(oldItem: JobOffer, newItem: JobOffer): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: JobOffer, newItem: JobOffer): Boolean =
            oldItem == newItem
    }
}
