package org.psicoia.android

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import com.arm.aichat.AiChat
import com.arm.aichat.InferenceEngine
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.psicoia.android.core.CatalogIndex
import org.psicoia.android.core.ChatCoordinator
import org.psicoia.android.core.ChatSession
import org.psicoia.android.core.ConversationStore
import org.psicoia.android.core.LocalChatEngine
import java.io.File
import java.io.FileOutputStream
import java.util.LinkedHashMap
import java.util.UUID
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : ComponentActivity() {
    private val executor: ExecutorService = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private val prefs by lazy { getSharedPreferences("psicoia_offline", Activity.MODE_PRIVATE) }

    private var catalog: CatalogIndex? = null
    private var store: ConversationStore? = null
    private var session: ChatSession? = null
    private var coordinator: ChatCoordinator? = null
    private var engine: InferenceEngine? = null
    private var modelReady = false
    private var busy = false

    private lateinit var status: TextView
    private lateinit var transcript: TextView
    private lateinit var prompt: EditText
    private lateinit var sendButton: Button
    private lateinit var modelButton: Button
    private lateinit var approachSpinner: Spinner
    private lateinit var stageSpinner: Spinner

    private val approaches = listOf(
        Approach("Terapia comportamental", "bt"),
        Approach("Terapia cognitivo-comportamental", "cbt"),
        Approach("Humanista-existencial", "het"),
        Approach("Psicodinâmica", "pdt"),
        Approach("Pós-moderna", "pmt"),
    )
    private val stages = listOf("Avaliação", "Intervenção", "Consolidação")

    private val modelPicker = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) importAndLoadModel(uri)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        buildInterface()
        initializeOfflineData()
    }

    private fun buildInterface() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(20, 18, 20, 16)
            setBackgroundColor(0xFFF7F8FA.toInt())
        }
        root.addView(TextView(this).apply {
            text = "PsicoIA offline — protótipo de pesquisa"
            textSize = 20f
            setTextColor(0xFF182235.toInt())
        }, matchWrap())

        status = TextView(this).apply {
            text = "Carregando catálogo local…"
            textSize = 13f
            setPadding(0, 8, 0, 8)
        }
        root.addView(status, matchWrap())

        modelButton = Button(this).apply {
            text = "Importar modelo GGUF local"
            isEnabled = false
            setOnClickListener { modelPicker.launch(arrayOf("application/octet-stream", "*/*")) }
        }
        root.addView(modelButton, matchWrap())

        val selectors = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        approachSpinner = Spinner(this).apply { adapter = spinnerAdapter(approaches.map { it.label }) }
        stageSpinner = Spinner(this).apply { adapter = spinnerAdapter(stages) }
        selectors.addView(approachSpinner, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.4f))
        selectors.addView(stageSpinner, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        root.addView(selectors, matchWrap())

        val scroll = ScrollView(this)
        transcript = TextView(this).apply {
            textSize = 15f
            setTextColor(0xFF182235.toInt())
            setPadding(8, 8, 8, 8)
        }
        scroll.addView(transcript)
        root.addView(scroll, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))

        val inputRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        prompt = EditText(this).apply {
            hint = "Escreva uma mensagem"
            minLines = 1
            maxLines = 4
            isEnabled = false
        }
        sendButton = Button(this).apply {
            text = "Enviar"
            isEnabled = false
            setOnClickListener { sendMessage() }
        }
        inputRow.addView(prompt, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        inputRow.addView(sendButton, LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        root.addView(inputRow, matchWrap())
        setContentView(root)
    }

    private fun spinnerAdapter(values: List<String>): ArrayAdapter<String> = ArrayAdapter(
        this, android.R.layout.simple_spinner_item, values
    ).also { it.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item) }

    private fun matchWrap() = LinearLayout.LayoutParams(
        ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
    )

    private fun initializeOfflineData() {
        executor.execute {
            try {
                val files = LinkedHashMap<String, String>()
                for (approach in approaches) {
                    for (stage in 1..3) {
                        for (type in listOf("meta", "micro")) {
                            val relative = "${approach.sect}/stage$stage/${type}_skills.pt-BR.json"
                            val asset = "catalog/sect/$relative"
                            files["sect/$relative"] = assets.open(asset).bufferedReader(Charsets.UTF_8).use { it.readText() }
                        }
                    }
                }
                val loadedCatalog = CatalogIndex.fromJsonFiles(files)
                val conversationStore = ConversationStore(filesDir)
                val savedId = prefs.getString("session_id", null)
                val restored = try {
                    if (savedId == null) null else conversationStore.load(savedId)
                } catch (_: Exception) { null }
                val activeSession = restored ?: conversationStore.create("bt", 1)
                if (restored == null) prefs.edit().putString("session_id", activeSession.sessionId).apply()

                catalog = loadedCatalog
                store = conversationStore
                session = activeSession
                coordinator = ChatCoordinator(loadedCatalog, conversationStore)
                mainHandler.post {
                    status.text = "Catálogo PT-BR carregado: ${loadedCatalog.getSourceRecordCount()} registros; busca local BM25."
                    modelButton.isEnabled = true
                    prompt.isEnabled = true
                    approachSpinner.setSelection(approaches.indexOfFirst { it.sect == activeSession.sect }.coerceAtLeast(0))
                    stageSpinner.setSelection((activeSession.stage - 1).coerceIn(0, 2))
                    renderConversation()
                    restoreModelIfPresent()
                }
            } catch (e: Exception) {
                mainHandler.post {
                    status.text = "Falha ao carregar o catálogo local: ${e.message ?: "arquivo inválido"}"
                    modelButton.isEnabled = false
                    sendButton.isEnabled = false
                }
            }
        }
    }

    private fun restoreModelIfPresent() {
        val name = prefs.getString("model_file", null) ?: return
        val file = File(File(filesDir, "models"), name)
        if (file.isFile) loadLocalModelAsync(file)
    }

    private fun importAndLoadModel(uri: Uri) {
        if (busy) return
        busy = true
        modelButton.isEnabled = false
        status.text = "Importando modelo para o armazenamento privado…"
        executor.execute {
            try {
                val directory = File(filesDir, "models")
                if (!directory.exists() && !directory.mkdirs()) throw IllegalStateException("Não foi possível criar o armazenamento local")
                val fileName = "${UUID.randomUUID()}.gguf"
                val finalFile = File(directory, fileName)
                val temporary = File(directory, "$fileName.tmp")
                contentResolver.openInputStream(uri)?.use { input ->
                    FileOutputStream(temporary).use { output ->
                        input.copyTo(output)
                        output.fd.sync()
                    }
                } ?: throw IllegalStateException("Não foi possível abrir o arquivo selecionado")
                val header = temporary.inputStream().use { it.readNBytes(4) }
                if (!header.contentEquals(byteArrayOf('G'.code.toByte(), 'G'.code.toByte(), 'U'.code.toByte(), 'F'.code.toByte()))) {
                    temporary.delete()
                    throw IllegalArgumentException("O arquivo selecionado não tem cabeçalho GGUF")
                }
                if (!temporary.renameTo(finalFile)) throw IllegalStateException("Não foi possível finalizar a cópia do modelo")
                prefs.edit().putString("model_file", fileName).apply()
                loadLocalModelBlocking(finalFile)
            } catch (e: Exception) {
                mainHandler.post { modelLoadFailed(e) }
            }
        }
    }

    private fun loadLocalModelAsync(file: File) {
        if (busy) return
        busy = true
        status.text = "Carregando modelo GGUF no aparelho…"
        executor.execute { loadLocalModelBlocking(file) }
    }

    private fun loadLocalModelBlocking(file: File) {
        try {
            val activeSession = session ?: throw IllegalStateException("Conversa local ainda não foi inicializada")
            val localEngine = engine ?: AiChat.getInferenceEngine(applicationContext).also { engine = it }
            runBlocking {
                var state = localEngine.state.first {
                    it is InferenceEngine.State.Initialized || it is InferenceEngine.State.Error || it is InferenceEngine.State.ModelReady
                }
                if (state is InferenceEngine.State.Error || state is InferenceEngine.State.ModelReady) {
                    localEngine.cleanUp()
                    state = localEngine.state.first { it is InferenceEngine.State.Initialized || it is InferenceEngine.State.Error }
                }
                if (state is InferenceEngine.State.Error) throw state.exception
                localEngine.loadModel(file.absolutePath)
                localEngine.setSystemPrompt(buildSystemPrompt(activeSession))
            }
            modelReady = true
            busy = false
            mainHandler.post {
                status.text = "Modelo GGUF carregado localmente. Conversas e catálogo permanecem no aparelho."
                modelButton.text = "Modelo local: ${file.name}"
                modelButton.isEnabled = false
                prompt.isEnabled = true
                sendButton.isEnabled = true
            }
        } catch (e: Exception) {
            modelLoadFailed(e)
        }
    }

    private fun buildSystemPrompt(activeSession: ChatSession): String {
        val history = activeSession.messages.filter { it.role == "user" || it.role == "assistant" }.takeLast(12)
        val prior = if (history.isEmpty()) "" else history.joinToString("\n") { "${it.role}: ${it.text.take(700)}" }.takeLast(6000)
        return buildString {
            append("Você é o assistente local PsicoIA para pesquisa. Responda em português brasileiro. ")
            append("Use o contexto de catálogo enviado a cada turno sem expor IDs internos. ")
            append("Não se apresente como profissional de saúde nem diagnostique.\n")
            if (prior.isNotBlank()) append("Histórico anterior da conversa:\n").append(prior)
        }
    }

    private fun sendMessage() {
        val userText = prompt.text?.toString()?.trim().orEmpty()
        if (userText.isBlank()) return
        val activeSession = session ?: return
        val approach = approaches.getOrNull(approachSpinner.selectedItemPosition) ?: return
        val stage = stageSpinner.selectedItemPosition + 1
        busy = true
        prompt.setText("")
        prompt.isEnabled = false
        sendButton.isEnabled = false
        modelButton.isEnabled = false
        status.text = "Recuperando habilidades locais e gerando resposta…"
        executor.execute {
            try {
                store?.updateContext(activeSession.sessionId, approach.sect, stage)
                activeSession.sect = approach.sect
                activeSession.stage = stage
                val localEngine = if (modelReady) engine else null
                val adapter = localEngine?.let { runtime ->
                    LocalChatEngine { text ->
                        val answer = StringBuilder()
                        runBlocking {
                            runtime.sendUserPrompt(text, 512).collect { token -> answer.append(token) }
                        }
                        answer.toString()
                    }
                }
                val result = coordinator?.send(activeSession.sessionId, userText, adapter)
                    ?: throw IllegalStateException("Serviços locais ainda não estão prontos")
                mainHandler.post {
                    status.text = if (result.success) {
                        "Resposta gerada no aparelho; recuperadas ${result.retrievedSkills.size} habilidades locais."
                    } else result.text
                    busy = false
                    prompt.isEnabled = true
                    sendButton.isEnabled = modelReady
                    modelButton.isEnabled = !modelReady
                    renderConversation()
                }
            } catch (e: Exception) {
                mainHandler.post {
                    status.text = "Falha local: ${e.message ?: "erro inesperado"}"
                    busy = false
                    prompt.isEnabled = true
                    sendButton.isEnabled = modelReady
                    modelButton.isEnabled = !modelReady
                }
            }
        }
    }

    private fun renderConversation() {
        val active = session ?: return
        val loaded = try { store?.load(active.sessionId) } catch (_: Exception) { null } ?: active
        session = loaded
        transcript.text = loaded.messages.joinToString("\n\n") { message ->
            val label = when (message.role) {
                "user" -> "Você"
                "assistant" -> "PsicoIA"
                else -> "Falha local"
            }
            "$label: ${message.text}"
        }.ifBlank { "Importe um modelo GGUF compatível para ativar a conversação offline.\n\nA recuperação do catálogo funciona sem modelo." }
    }

    private fun modelLoadFailed(error: Exception) {
        busy = false
        modelReady = false
        mainHandler.post {
            status.text = "Não foi possível carregar o modelo local: ${error.message ?: error.javaClass.simpleName}"
            modelButton.text = "Importar modelo GGUF local"
            modelButton.isEnabled = true
            prompt.isEnabled = true
            sendButton.isEnabled = false
            Toast.makeText(this, "Falha no modelo local; nenhum serviço remoto será usado.", Toast.LENGTH_LONG).show()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdown()
    }

    private data class Approach(val label: String, val sect: String)
}
