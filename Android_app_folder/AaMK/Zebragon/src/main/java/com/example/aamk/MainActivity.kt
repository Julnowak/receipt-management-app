package com.example.aamk

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity


@Suppress("DEPRECATION")
class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var refresh_btn: Button
    private var mUploadCallback: ValueCallback<Array<Uri>>? = null
    private val FILE_CHOOSER_RESULT_CODE = 1
    var currentUrl="https://eminently-working-lynx.ngrok-free.app"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        refresh()
    }

    fun isConnectedToTheInternet(context: Context): Boolean {
        var isInternetAvailable = false
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager?
        cm?.run {
            cm.getNetworkCapabilities(cm.activeNetwork)?.run {
                isInternetAvailable = hasTransport(NetworkCapabilities.TRANSPORT_WIFI) || hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)
            }
        }
        return isInternetAvailable
    }


    @SuppressLint("SetJavaScriptEnabled")
    fun refresh() {
    if (isConnectedToTheInternet(this@MainActivity)) {
        setContentView(R.layout.app_webview)

        webView = findViewById(R.id.webview)

        // Set up WebView
        webView.settings.javaScriptEnabled = true
        webView.webChromeClient = WebChromeClient()
        webView.settings.setRenderPriority(WebSettings.RenderPriority.HIGH)
        webView.settings.javaScriptEnabled = true
        webView.settings.displayZoomControls = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowContentAccess = true
        webView.settings.cacheMode = WebSettings.LOAD_NO_CACHE
        webView.settings.allowFileAccess = true
        webView.settings.allowFileAccessFromFileURLs = true
        webView.settings.allowUniversalAccessFromFileURLs = true

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView,
                filePathCallback: ValueCallback<Array<Uri>>,
                fileChooserParams: FileChooserParams
            ): Boolean {
                mUploadCallback = filePathCallback
                val intent = fileChooserParams.createIntent()
                startActivityForResult(intent, FILE_CHOOSER_RESULT_CODE)
                return true
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                if (isConnectedToTheInternet(this@MainActivity)) {
                    view?.loadUrl(request?.url.toString())
                } else {
                    setContentView(R.layout.activity_main)
                    refresh_btn = findViewById(R.id.refresh_btn)
                    refresh_btn.setOnClickListener { refresh() }

                }
                currentUrl=request?.url.toString()
                return true
            }
        }
        webView.loadUrl(currentUrl)
    } else {
        setContentView(R.layout.activity_main)
        refresh_btn = findViewById(R.id.refresh_btn)
        refresh_btn.setOnClickListener { refresh() }

    }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == FILE_CHOOSER_RESULT_CODE) {
            if (resultCode == RESULT_OK && data != null) {
                var results: Array<Uri>? = null
                val dataString = data.dataString
                if (dataString != null) {
                    results = arrayOf(Uri.parse(dataString))
                }
                mUploadCallback!!.onReceiveValue(results)
                mUploadCallback = null
            } else {
                mUploadCallback!!.onReceiveValue(null)
                mUploadCallback = null
            }
        }
    }


    @Deprecated("Deprecated")
    override fun onBackPressed() {
        if (isConnectedToTheInternet(this@MainActivity)){
            if (webView.canGoBack()) {
                webView.goBack()
            } else {
                super.onBackPressed()
            }
        }
        else{
            super.onBackPressed()
        }

    }

}

