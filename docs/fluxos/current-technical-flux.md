**FrenchTalkIA — Flux Technique Actuel**

**Résumé**
- **Point d'entrée** : `app/main.py` — application FastAPI.
- Objectif : recevoir messages WhatsApp via webhook, traiter texte/voix (STT → LLM → TTS) et répondre via WhatsApp Cloud API.

**Architecture générale**
- FastAPI app (`app/main.py`) initialise objets partagés (storages, services) sur `app.state` au démarrage.
- Routes exposées : router `webhook` inclus depuis `app/routes/webhook.py` (prefix `/webhook`).
- Services principaux : `WhatsAppService`, `GladiaService` (STT), `MistralService` (LLM), `MurfService` (TTS), `UsuarioService`.
- Stockage local JSON thread-safe via `BaseStorage` et classes concrètes : `UsuarioStorage`, `SessaoStorage`, `ConversaStorage`.

**Cycle de vie de l'application**
- `lifespan(app: FastAPI)` (dans `app/main.py`) : wrapper async pour startup/shutdown.
	- Appel `await startup_event()` avant que l'app ne soit disponible.
	- Après `yield`, `await shutdown_event()` à l'arrêt.

- `startup_event()` (dans `app/main.py`) — étapes et responsabilités :
	1. Vérifier que `configuracao` (de `app/config.py`) a été chargée; si `None` lève `RuntimeError` (indique variables d'environnement manquantes ou `.env` absent).
		 - Input indirect : variables d'environnement utilisées par `get_configuracao()` pour construire `ConfiguracaoApp`.
		 - Output : instance `ConfiguracaoApp` (placée en variable globale `configuracao`) ou exception.
	2. Créer répertoires : `configuracao.diretorio_dados`, `configuracao.diretorio_temp_audio` (Paths). But : garantir persistence fichiers JSON et répertoire temporaire pour audio.
	3. Initialiser storages :
		 - `UsuarioStorage(configuracao.diretorio_dados / "usuarios.json")`
		 - `SessaoStorage(configuracao.diretorio_dados / "sessoes.json")`
		 - `ConversaStorage(configuracao.diretorio_dados / "conversas.json")`
		 - Ces classes héritent de `BaseStorage` (`app/storage/base_storage.py`) qui gère lecture/écriture JSON thread-safe et méthodes publiques `obter`, `salvar`, `listar_todos`, `deletar`, etc.
	4. Initialiser services :
		 - `UsuarioService(usuario_storage, sessao_storage)` — gestion utilisateur et sessions (`app/services/usuario_service.py`).
		 - `WhatsAppService(configuracao)` — client pour WhatsApp Cloud API (`app/services/whatsapp_service.py`).
		 - `GladiaService()` — STT (stub) (`app/services/gladia_service.py`).
		 - `MistralService()` — LLM (stub) (`app/services/mistral_service.py`).
		 - `MurfService()` — TTS (stub) (`app/services/murf_service.py`).
	5. Placer toutes les instances sur `app.state` pour usage dans les routes :
		 `app.state.usuario_service`, `usuario_storage`, `sessao_storage`, `conversa_storage`, `whatsapp_service`, `gladia_service`, `mistral_service`, `murf_service`.
	6. Logger informations d'initialisation via `app.utils.logger`.

- `shutdown_event()` (dans `app/main.py`) : log d'arrêt (amélioration recommandée : fermer `WhatsAppService.httpx_client` via `await whatsapp_service.close()`).

**Entrées/sorties & comportements des endpoints principaux**

- `GET /` (dans `app/main.py`) — racine :
	- Input : requête HTTP GET.
	- Output : JSON limité: `{"message": "FrenchTalkIA API", "version": "0.1.0", "status": "operacional"}`.

- `GET /health` (dans `app/main.py`) — health check :
	- Input : requête GET.
	- Output : si `configuracao` non chargée -> message d'erreur; sinon `{"status":"ok","servico":"FrenchTalkIA","ambiente":configuracao.ambiente,"versao":"0.1.0"}`.

- `GET /info` (dans `app/main.py`) — info diagnostic :
	- Input : requête GET.
	- Output : métadonnées de l'API et endpoints exposés.

**Router webhook — `app/routes/webhook.py`**
- `GET /webhook/whatsapp` (fonction `webhook_verify`)
	- Input : query params `hub.mode`, `hub.challenge`, `hub.verify_token`.
	- Utilise `get_configuracao()` (`app/config.py`) pour comparer `hub.verify_token`.
	- Output : si validations ok -> retourne `hub.challenge` (plain text, HTTP 200); sinon `403`.
	- But : endpoint exigé par WhatsApp Cloud API pour vérifier webhook.

- `POST /webhook/whatsapp` (fonction `webhook_receive`) — flux principal
	- Input : payload JSON envoyé par WhatsApp Cloud API (attendu conforme aux modèles dans `app/models/webhook.py`).
	- Étape 1 : `payload_data = await request.json()` puis `payload = WebhookPayload.model_validate(payload_data)`.
		- `WebhookPayload.extrair_mensagem()` renvoie la première `message` (dict) trouvée ou `None`.
	- Si aucune message : retourne `{"status":"error","message":"Nenhuma mensagem encontrada"}`.
	- Branches par `mensagem_tipo = mensagem_dict.get("type")` :
		- `text` :
			- `_processar_texto(mensagem_dict)` (utilise `TextMessage.model_validate`) -> renvoie `dados` = `{telefone, mensagem_id, timestamp, tipo:'text', conteudo}`.
			- Si `config.integration_whatsapp` vrai : `_salvar_integracao(whatsapp_service, "text", dados_extraidos)` -> `WhatsAppService.salvar_resultado_integracao()` sauvegarde artefacts tests dans `tests/integration/results/...`.
			- Planifie traitement en arrière-plan : `background_tasks.add_task(asyncio.create_task, _process_message_bg(mensagem_dict))` et retourne immédiatement `_criar_resposta("received","Mensagem de texto recebida e agendada", dados_extraidos)`.
			- Background (`_process_message_bg`) :
				1. `texto_usuario = dados.get("conteudo")`.
				2. `resposta = await asyncio.to_thread(mistral_svc.continuar_conversa, "default", texto_usuario)` (appel sync via threadpool).
				3. `await whatsapp_svc.enviar_mensagem_texto(telefone, resposta)` (async) — envoi vers WhatsApp.

		- `audio` :
			- `_processar_audio(mensagem_dict)` (utilise `AudioMessage.model_validate`) -> renvoie `dados` = `{telefone, mensagem_id, timestamp, tipo:'audio', media_id, mime_type}`.
			- Si `config.integration_whatsapp` : appelle `_baixar_audio_para_integracao(...)` puis `_salvar_integracao(...)` pour conserver audio et métadonnées.
			- Planifie traitement en arrière-plan et retourne `_criar_resposta("received","Mensagem de áudio recebida e agendada", dados_extraidos)`.
			- Background (`_process_message_bg`) :
				1. `arquivo = await whatsapp_svc.baixar_audio(media_id)` -> Path local du fichier audio.
				2. `texto_transcrito = await asyncio.to_thread(gladia_svc.transcrever_audio, arquivo)` -> transcription (string).
				3. `resposta_texto = await asyncio.to_thread(mistral_svc.continuar_conversa, "default", texto_transcrito)` -> réponse LLM (string).
				4. `caminho_audio, duration = await asyncio.to_thread(murf_svc.gerar_audio, resposta_texto)` -> Path audio TTS + durée.
				5. `await whatsapp_svc.enviar_mensagem_audio(telefone, caminho_audio)` -> envoi audio via WhatsApp.

		- Autre type : `_processar_tipo_desconhecido` renvoie un dict minimal; si `integration_whatsapp` enregistre; retourne accepted.

**Modèles & validation (Pydantic)**
- `app/models/webhook.py` :
	- `WebhookPayload` — racine ; méthodes utilitaires : `extrair_mensagem()`, `extrair_text_message()`, `extrair_audio_message()`, `extrair_contato()`, `extrair_phone_number_id()`.
	- `WebhookMessage`, `TextMessage`, `AudioMessage` — validation et propriétés d'accès (`TextMessage.body`, `AudioMessage.audio_id`, `AudioMessage.mime_type`).
	- But : standardiser le payload et éviter accès direct par clefs non vérifiées.

**Storages (contrats)**
- `BaseStorage` (`app/storage/base_storage.py`) fournit API thread-safe :
	- `obter(chave) -> T | None` — lire un item.
	- `salvar(chave, item) -> None` — sauvegarder/mettre à jour.
	- `listar_todos() -> list[T]`, `deletar(chave) -> bool`, `limpar_todos()`.
- `UsuarioStorage`, `SessaoStorage`, `ConversaStorage` implémentent `_serializar`/`_deserializar` et méthodes spécifiques liées au domaine (`atualizar_cota`, `criar_sessao_nova`, `criar_nova_conversa`, etc.).

**Services externes (contrats et entrées/sorties)**
- `WhatsAppService(config: ConfiguracaoApp)` (`app/services/whatsapp_service.py`) — async client.
	- Méthodes importantes :
		- `obter_url_media(media_id: str) -> str` (async) : récupère URL temporaire via Graph API.
		- `baixar_audio(media_id: str) -> Path` (async) : télécharge et retourne `Path` du fichier `.ogg` local.
		- `fazer_upload_audio(caminho_audio: Path) -> str` (async) : uploade fichier et retourne `media_id`.
		- `enviar_mensagem_texto(telefone: str, texto: str) -> str` (async) : envoie texte, retourne `message_id`.
		- `enviar_mensagem_audio(telefone: str, caminho_audio: Path) -> str` (async) : upload + envoi audio, retourne `message_id`.
		- `salvar_resultado_integracao(...) -> Optional[Path]` : si `integration_whatsapp` active, écrit `extracted_data.json` et `metadata.json` et copie audio reçu.
	- Exceptions et codes HTTP sont gérés et remontés sous forme de `ValueError` ou logs.

- `GladiaService()` (`app/services/gladia_service.py`) — stub synchrone.
	- Contrat utilisé : `transcrever_audio(caminho_audio: Path) -> str` (retourne texte). Dans la version actuelle, c'est un stub simulant upload/polling.

- `MistralService()` (`app/services/mistral_service.py`) — stub synchrone.
	- Contrats : `iniciar_conversa(agent_id: str, texto_usuario: str) -> tuple[str,str]`, `continuar_conversa(conversation_id: str, texto_usuario: str) -> str`.
	- Utilisé via `asyncio.to_thread(...)` parce que l'implémentation est synchrone.

- `MurfService()` (`app/services/murf_service.py`) — stub synchrone.
	- Contrat : `gerar_audio(texto: str) -> tuple[Path,float]` (Path du fichier TTS + durée estimée).

**Flux de données (résumé concret)**
1. WhatsApp → Webhook POST : payload JSON.
2. `WebhookPayload.model_validate` -> `mensagem_dict = extrair_mensagem()`.
3. Branch: texte ou audio.
	 - Texte : extraire texte → planifier background → LLM -> `enviar_mensagem_texto`.
	 - Audio : download → STT (Gladia) → LLM → TTS (Murf) → upload+send audio.
4. Réponse HTTP immédiate au provider WhatsApp est un accusé de réception (JSON `received` + `dados_extraidos`) pour garder latence basse.

**Points d'attention & améliorations recommandées**
- Fermer proprement `WhatsAppService.httpx_client` dans `shutdown_event()` (app.state.whatsapp_service.close()).
- Remplacer stubs synchrone (`MistralService`, `GladiaService`, `MurfService`) par versions asynchrones ou exécuter explicitement dans un `ThreadPoolExecutor` dédié (optimisation de concurrence).
- Traçabilité : ajouter IDs de corrélation/logging dans background tasks pour diagnostiquer erreurs post-ack.
- Robustesse : réessais/exponential backoff sur envoi de message si code non-200; gestion de quota / circuit breaker.

**Références fichiers clés**
- Point d'entrée & lifecycle : `app/main.py`
- Routes webhook : `app/routes/webhook.py`
- Models payload : `app/models/webhook.py`
- WhatsApp client : `app/services/whatsapp_service.py`
- STT (stub) : `app/services/gladia_service.py`
- LLM (stub) : `app/services/mistral_service.py`
- TTS (stub) : `app/services/murf_service.py`
- Storages : `app/storage/base_storage.py`, `app/storage/usuario_storage.py`, `app/storage/sessao_storage.py`, `app/storage/conversa_storage.py`
- Config : `app/config.py`
- Logger singleton : `app/utils/logger.py`

---
Document rédigé automatiquement à partir de l'analyse de code source (Décembre 2025). Pour modifications, réponds quelle section tu veux étendre ou si tu veux que j'ajoute un diagramme d'appel.

