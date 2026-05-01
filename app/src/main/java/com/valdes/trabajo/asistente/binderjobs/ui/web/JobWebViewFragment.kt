package com.valdes.trabajo.asistente.binderjobs.ui.web

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebViewClient
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.valdes.trabajo.asistente.binderjobs.R
import com.valdes.trabajo.asistente.binderjobs.databinding.FragmentJobWebviewBinding

class JobWebViewFragment : Fragment() {
    private var _binding: FragmentJobWebviewBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentJobWebviewBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val url = requireArguments().getString(getString(R.string.job_url_arg)).orEmpty()
        val title = requireArguments().getString(getString(R.string.job_title_arg)).orEmpty()

        binding.titleText.text = title
        binding.backButton.setOnClickListener { findNavController().navigateUp() }
        binding.externalButton.setOnClickListener {
            if (url.isNotBlank()) {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
            }
        }

        with(binding.jobWebView) {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            webViewClient = WebViewClient()
            webChromeClient =
                object : WebChromeClient() {
                    override fun onProgressChanged(view: android.webkit.WebView?, newProgress: Int) {
                        super.onProgressChanged(view, newProgress)
                        binding.webProgress.visibility = if (newProgress < 100) View.VISIBLE else View.GONE
                    }
                }
            if (url.isNotBlank()) {
                loadUrl(url)
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
