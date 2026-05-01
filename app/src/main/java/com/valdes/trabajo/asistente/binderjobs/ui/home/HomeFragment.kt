package com.valdes.trabajo.asistente.binderjobs.ui.home

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.valdes.trabajo.asistente.binderjobs.R
import com.valdes.trabajo.asistente.binderjobs.databinding.FragmentHomeBinding
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()
    private lateinit var adapter: JobOfferAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupRecyclerView()
        setupSearchBar()
        setupFilterChips()
        setupLocationDisplay()
        observeUiState()
        
        viewModel.search("")
    }

    private fun setupRecyclerView() {
        adapter = JobOfferAdapter(
            onOpenClick = { job ->
                viewModel.recordClick(job.id)
                val args = Bundle().apply {
                    putString(getString(R.string.job_url_arg), job.url)
                    putString(getString(R.string.job_title_arg), job.title)
                }
                findNavController().navigate(R.id.action_home_to_webView, args)
            },
            onSaveClick = { job ->
                viewModel.saveJob(job)
                Toast.makeText(requireContext(), R.string.saved, Toast.LENGTH_SHORT).show()
            },
        )
        binding.jobsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        binding.jobsRecyclerView.adapter = adapter
    }

    private fun setupSearchBar() {
        binding.searchEditText.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                binding.clearSearchButton.visibility = 
                    if (s.isNullOrEmpty()) View.GONE else View.VISIBLE
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.searchEditText.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                performSearch()
                true
            } else {
                false
            }
        }

        binding.clearSearchButton.setOnClickListener {
            binding.searchEditText.text?.clear()
            binding.clearSearchButton.visibility = View.GONE
        }

        binding.searchButton.setOnClickListener {
            performSearch()
        }

        binding.retryButton.setOnClickListener {
            performSearch()
        }
    }

    private fun setupFilterChips() {
        binding.chipRemote.setOnCheckedChangeListener { _, isChecked ->
            viewModel.setRemoteFilter(isChecked)
            performSearch()
        }

        binding.chipNearby.setOnCheckedChangeListener { _, isChecked ->
            viewModel.setNearbyFilter(isChecked)
            performSearch()
        }

        binding.chipWithSalary.setOnCheckedChangeListener { _, isChecked ->
            viewModel.setWithSalaryFilter(isChecked)
            performSearch()
        }

        binding.chipFullTime.setOnCheckedChangeListener { _, isChecked ->
            viewModel.setFullTimeFilter(isChecked)
            performSearch()
        }
    }

    private fun setupLocationDisplay() {
        lifecycleScope.launch {
            val prefs = viewModel.getCurrentPreferences()
            val location = buildString {
                if (prefs.city.isNotBlank()) append(prefs.city)
                if (prefs.state.isNotBlank()) {
                    if (isNotBlank()) append(", ")
                    append(prefs.state)
                }
                if (prefs.country.isNotBlank()) {
                    if (isNotBlank()) append(", ")
                    append(prefs.country)
                }
            }
            binding.locationText.text = location.ifBlank { "Sin ubicación configurada" }
        }

        binding.changeLocationButton.setOnClickListener {
            findNavController().navigate(R.id.navigation_dashboard)
        }
    }

    private fun performSearch() {
        val query = binding.searchEditText.text?.toString().orEmpty()
        viewModel.search(query)
        viewModel.addToSearchHistory(query)
    }

    private fun observeUiState() {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    HomeUiState.Loading -> showLoadingState()
                    is HomeUiState.Success -> showSuccessState(state)
                    is HomeUiState.Empty -> showEmptyState(state.message)
                    is HomeUiState.Error -> showErrorState(state.message)
                }
            }
        }
    }

    private fun showLoadingState() {
        binding.loadingState.visibility = View.VISIBLE
        binding.emptyState.visibility = View.GONE
        binding.resultsContainer.visibility = View.GONE
    }

    private fun showSuccessState(state: HomeUiState.Success) {
        binding.loadingState.visibility = View.GONE
        binding.emptyState.visibility = View.GONE
        binding.resultsContainer.visibility = View.VISIBLE
        
        adapter.submitList(state.jobs)
        
        val count = state.jobs.size
        binding.resultsCount.visibility = View.VISIBLE
        binding.resultsCount.text = if (count == 1) {
            getString(R.string.results_count_singular)
        } else {
            getString(R.string.results_count, count)
        }
    }

    private fun showEmptyState(message: String) {
        binding.loadingState.visibility = View.GONE
        binding.emptyState.visibility = View.VISIBLE
        binding.resultsContainer.visibility = View.GONE
        binding.emptyMessage.text = message
    }

    private fun showErrorState(message: String) {
        binding.loadingState.visibility = View.GONE
        binding.emptyState.visibility = View.VISIBLE
        binding.resultsContainer.visibility = View.GONE
        binding.emptyTitle.text = getString(R.string.error_network)
        binding.emptyMessage.text = message
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
