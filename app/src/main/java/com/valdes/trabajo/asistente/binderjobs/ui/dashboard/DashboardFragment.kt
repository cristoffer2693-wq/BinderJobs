package com.valdes.trabajo.asistente.binderjobs.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import com.valdes.trabajo.asistente.binderjobs.R
import com.valdes.trabajo.asistente.binderjobs.databinding.FragmentDashboardBinding
import kotlinx.coroutines.launch

class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DashboardViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.detectLocationButton.setOnClickListener {
            viewModel.detectLocationIfMissing()
        }

        binding.saveSettingsButton.setOnClickListener {
            val radius = binding.radiusInput.text?.toString()?.toIntOrNull() ?: 50
            viewModel.updateLocation(
                country = binding.countryInput.text?.toString().orEmpty(),
                state = binding.stateInput.text?.toString().orEmpty(),
                city = binding.cityInput.text?.toString().orEmpty(),
                radiusKm = radius,
            )
            viewModel.updateSwitches(
                backgroundEnabled = binding.backgroundSwitch.isChecked,
                notificationsEnabled = binding.notificationsSwitch.isChecked,
            )
            Toast.makeText(requireContext(), getString(R.string.settings_saved), Toast.LENGTH_SHORT).show()
        }

        lifecycleScope.launch {
            viewModel.preferences.collect { prefs ->
                if (binding.countryInput.text.isNullOrBlank()) binding.countryInput.setText(prefs.country)
                if (binding.stateInput.text.isNullOrBlank()) binding.stateInput.setText(prefs.state)
                if (binding.cityInput.text.isNullOrBlank()) binding.cityInput.setText(prefs.city)
                if (binding.radiusInput.text.isNullOrBlank()) binding.radiusInput.setText(prefs.radiusKm.toString())
                binding.backgroundSwitch.isChecked = prefs.backgroundSearchEnabled
                binding.notificationsSwitch.isChecked = prefs.notificationsEnabled
            }
        }

        viewModel.detectLocationIfMissing()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}