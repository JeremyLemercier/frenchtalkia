# Fluxo Completo: Receber e Responder Mensagens via WhatsApp Cloud API

## Visão Geral
Este documento descreve o fluxo completo para receber uma mensagem de um usuário (áudio ou texto) através do WhatsApp e enviar uma resposta no mesmo formato (áudio ou texto) para esse usuário pelo canal WhatsApp, utilizando a WhatsApp Cloud API.

---

## 1. Arquitetura do Fluxo

O fluxo funciona em dois sentidos:
- **ENTRADA**: Receber mensagens de usuários via Webhooks
- **SAÍDA**: Enviar respostas através de requisições POST diretas à API

```
┌─────────────────────────┐
│   Usuário WhatsApp      │
└────────────┬────────────┘
             │
             │ 1. Envia mensagem (áudio/texto)
             ▼
┌─────────────────────────────────────────┐
│  WhatsApp Cloud API                     │
│  (Recebe mensagem)                      │
└────────────┬────────────────────────────┘
             │
             │ 2. Dispara Webhook
             ▼
┌─────────────────────────────────────────┐
│  Sua Aplicação                          │
│  (Processa mensagem)                    │
└────────────┬────────────────────────────┘
             │
             │ 3. Prepara resposta
             ▼
┌─────────────────────────────────────────┐
│  WhatsApp Cloud API                     │
│  (Envia resposta)                       │
└────────────┬────────────────────────────┘
             │
             │ 4. Entrega mensagem
             ▼
┌─────────────────────────────────────────┐
│   Usuário WhatsApp                      │
│   (Recebe resposta)                     │
└─────────────────────────────────────────┘
```

---

## 2. PARTE 1: RECEBER MENSAGENS (WEBHOOK)

### 2.1 Configuração Inicial do Webhook

Para receber mensagens, você deve configurar um webhook na sua plataforma WhatsApp Business. O WhatsApp enviará eventos em tempo real para seu servidor através de requisições HTTP.

**Endpoint esperado em sua aplicação:**
```
POST https://seu-dominio.com/webhooks/whatsapp
```

### 2.2 Estrutura da Mensagem Recebida

Quando um usuário envia uma mensagem, o WhatsApp dispara um webhook com a seguinte estrutura JSON:

#### Exemplo: Mensagem de Texto
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "5585987654321",
              "phone_number_id": "BUSINESS_PHONE_NUMBER_ID"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Nome do Usuário"
                },
                "wa_id": "558599999999"
              }
            ],
            "messages": [
              {
                "from": "558599999999",
                "id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA",
                "timestamp": "1725000000",
                "type": "text",
                "text": {
                  "body": "Conteúdo da mensagem de texto"
                }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

#### Exemplo: Mensagem de Áudio
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "5585987654321",
              "phone_number_id": "BUSINESS_PHONE_NUMBER_ID"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Nome do Usuário"
                },
                "wa_id": "558599999999"
              }
            ],
            "messages": [
              {
                "from": "558599999999",
                "id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA",
                "timestamp": "1725000000",
                "type": "audio",
                "audio": {
                  "mime_type": "audio/ogg; codecs=opus",
                  "sha256": "HASH_SHA256_DO_ARQUIVO",
                  "id": "MEDIA_ID_DO_AUDIO"
                }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

### 2.3 Extração de Informações Críticas do Webhook

Da mensagem recebida, extraia:

| Campo | Origem | Descrição | Exemplo |
|-------|--------|-----------|---------|
| **Número do usuário** | `messages[].from` | Número de telefone do remetente | `558599999999` |
| **Message ID** | `messages[].id` | ID único da mensagem para contexto | `wamid.HBgL...` |
| **Tipo de mensagem** | `messages[].type` | Pode ser `text` ou `audio` | `audio` |
| **Conteúdo (texto)** | `messages[].text.body` | Corpo da mensagem de texto | `"Olá"` |
| **ID da Mídia (áudio)** | `messages[].audio.id` | ID da mídia para download | `MEDIA_ID` |
| **Phone Number ID** | `metadata.phone_number_id` | ID do seu número de negócio | `BUSINESS_PHONE_NUMBER_ID` |
| **Token de Acesso** | Configuração da app | Token Bearer para autenticação | `EAAJB...` |

### 2.4 Validação do Webhook

O WhatsApp valida seu webhook com uma requisição GET contendo um token:

```
GET https://seu-dominio.com/webhooks/whatsapp?hub.mode=subscribe&hub.challenge=CHALLENGE_TOKEN&hub.verify_token=YOUR_VERIFY_TOKEN
```

Sua aplicação deve responder com:
```
200 OK
CHALLENGE_TOKEN
```

---

## 3. PARTE 2: PROCESSAR A MENSAGEM RECEBIDA

### 3.1 Fluxo de Processamento

Após receber o webhook, sua aplicação deve:

1. **Validar a mensagem** - Verificar assinatura e integridade
2. **Extrair informações** - Obter número do usuário, tipo de mensagem e conteúdo
3. **Processar o conteúdo**:
   - Se for **texto**: Processar diretamente
   - Se for **áudio**: Fazer download do arquivo
4. **Gerar resposta** - Criar resposta baseada no processamento
5. **Enviar resposta** - Usar a API para enviar de volta

### 3.2 Processamento de Mensagem de Texto

```
1. Recebe webhook com texto
2. Extrai: from, text.body, id da mensagem
3. Processa o texto (ex: envia para LLM, busca em BD)
4. Obtém resultado
5. Segue para PARTE 4 para enviar resposta
```

### 3.3 Processamento de Mensagem de Áudio

#### Passo 1: Fazer Download do Áudio

**Requisição 1: Obter URL da Mídia**

```http
GET https://graph.facebook.com/v24.0/<MEDIA_ID>?phone_number_id=<BUSINESS_PHONE_NUMBER_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

**Parâmetros:**
- `<MEDIA_ID>`: ID recebido no webhook (`messages[].audio.id`)
- `<BUSINESS_PHONE_NUMBER_ID>`: ID do seu número de negócio
- `<ACCESS_TOKEN>`: Seu token de acesso Bearer

**Resposta (200 OK):**
```json
{
  "messaging_product": "whatsapp",
  "url": "https://media-service.whatsapp.com/d/H7...",
  "mime_type": "audio/ogg; codecs=opus",
  "sha256": "HASH_SHA256",
  "file_size": 12345,
  "id": "MEDIA_ID"
}
```

**Nota Importante:** A URL é **temporária** e expira em **5 minutos**. Você deve fazer o download dentro deste prazo.

#### Passo 2: Fazer Download do Arquivo de Áudio

```http
GET https://media-service.whatsapp.com/d/H7...
Authorization: Bearer <ACCESS_TOKEN>
```

**Resposta:**
- Arquivo binário de áudio (arquivo bruto)

**Salve o arquivo localmente** com a extensão apropriada:
- `.ogg` para `audio/ogg; codecs=opus` (mensagens de voz)
- `.mp3` para `audio/mpeg`
- `.aac` para `audio/aac`
- etc.

#### Passo 3: Processar o Áudio

Após fazer download, você pode:
- **Transcrever** para texto (usar Gladia API, Whisper, etc.)
- **Analisar** emoção, tom, etc.
- **Processar** conforme sua lógica de negócio

---

## 4. PARTE 3: RECUPERAR CONTEXTO DA CONVERSA (OPCIONAL)

Se você precisa responder no contexto da mensagem anterior, pode usar o `message_id` recebido.

### 4.1 Responder em Contexto

Quando enviar a resposta (PARTE 4), inclua um campo `context` com o ID da mensagem original:

```json
{
  "messaging_product": "whatsapp",
  "context": {
    "message_id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA"
  },
  "to": "558599999999",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "Resposta contextuada"
  }
}
```

Isso fará a resposta aparecer como uma resposta direta à mensagem original no WhatsApp.

---

## 5. PARTE 4: ENVIAR RESPOSTAS

### 5.1 Enviar Resposta de Texto

**Requisição HTTP:**

```http
POST https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/messages
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "<WHATSAPP_USER_PHONE_NUMBER>",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "Sua resposta aqui (máx. 4096 caracteres)"
  }
}
```

**Parâmetros:**
- `<PHONE_NUMBER_ID>`: ID do seu número de negócio WhatsApp
- `<ACCESS_TOKEN>`: Seu token de acesso Bearer
- `<WHATSAPP_USER_PHONE_NUMBER>`: Número do usuário (ex: `558599999999`)

**Resposta (200 OK):**
```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "558599999999",
      "wa_id": "558599999999"
    }
  ],
  "messages": [
    {
      "id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA"
    }
  ]
}
```

### 5.2 Enviar Resposta de Áudio

Para enviar áudio, você precisa primeiro **fazer upload** do arquivo e depois **enviar a mensagem de áudio**.

#### Passo 1: Fazer Upload do Arquivo de Áudio

**Requisição HTTP:**

```http
POST https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/media
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: multipart/form-data

file=@"caminho/para/arquivo.ogg"
type="audio/ogg; codecs=opus"
messaging_product="whatsapp"
```

**Ou com curl:**

```bash
curl -X POST 'https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/media' \
-H 'Authorization: Bearer <ACCESS_TOKEN>' \
-F 'file=@"caminho/para/audio.ogg"' \
-F 'type="audio/ogg; codecs=opus"' \
-F 'messaging_product="whatsapp"'
```

**Parâmetros:**
- `<PHONE_NUMBER_ID>`: ID do seu número de negócio
- `<ACCESS_TOKEN>`: Token Bearer
- `file`: Caminho local do arquivo de áudio
- `type`: Tipo MIME do arquivo (ver tabela abaixo)
- `messaging_product`: Sempre `whatsapp`

**Tipos de Áudio Suportados:**

| Tipo de Áudio | MIME Type | Extensão | Tamanho Máx |
|---|---|---|---|
| OGG (Mensagem de voz) | `audio/ogg; codecs=opus` | `.ogg` | 16 MB |
| AAC | `audio/aac` | `.aac` | 16 MB |
| AMR | `audio/amr` | `.amr` | 16 MB |
| MP3 | `audio/mpeg` | `.mp3` | 16 MB |
| MP4 Audio | `audio/mp4` | `.m4a` | 16 MB |

**Nota Importante:** Para que o áudio apareça como uma **"nota de voz"** (com onda sonora) no WhatsApp, use:
- Formato: **OGG**
- Codec: **Opus**
- MIME Type: **`audio/ogg; codecs=opus`**
- Canais de áudio: **Mono apenas**

**Resposta (200 OK):**
```json
{
  "id": "<MEDIA_ID>"
}
```

Salve este `<MEDIA_ID>` - você usará para enviar a mensagem.

#### Passo 2: Enviar Mensagem de Áudio

**Requisição HTTP:**

```http
POST https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/messages
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "<WHATSAPP_USER_PHONE_NUMBER>",
  "type": "audio",
  "audio": {
    "id": "<MEDIA_ID>",
    "voice": true
  }
}
```

**Parâmetros:**
- `<PHONE_NUMBER_ID>`: ID do seu número de negócio
- `<ACCESS_TOKEN>`: Token Bearer
- `<WHATSAPP_USER_PHONE_NUMBER>`: Número do usuário
- `<MEDIA_ID>`: ID retornado no upload
- `voice`: `true` para aparecer como mensagem de voz; `false` ou omitido para aparecer como áudio

**Resposta (200 OK):**
```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "558599999999",
      "wa_id": "558599999999"
    }
  ],
  "messages": [
    {
      "id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA"
    }
  ]
}
```

#### Alternativa: Usar URL Pública

Se você hospedar o áudio em uma URL pública, pode enviar diretamente sem upload:

```http
POST https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/messages
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "<WHATSAPP_USER_PHONE_NUMBER>",
  "type": "audio",
  "audio": {
    "link": "https://seu-cdn.com/audio.ogg",
    "voice": true
  }
}
```

---

## 6. Fluxo Completo Resumido

### 6.1 Receber → Processar → Responder (Texto)

```
1. WEBHOOK RECEBIDO
   POST https://seu-dominio.com/webhooks/whatsapp
   ↓
   from: 558599999999
   type: text
   text.body: "Olá"

2. PROCESSAR TEXTO
   Processar mensagem em sua aplicação
   ↓
   resposta: "Olá! Como posso ajudar?"

3. ENVIAR RESPOSTA
   POST https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/messages
   type: text
   to: 558599999999
   text.body: "Olá! Como posso ajudar?"
```

### 6.2 Receber → Processar → Responder (Áudio)

```
1. WEBHOOK RECEBIDO
   POST https://seu-dominio.com/webhooks/whatsapp
   ↓
   from: 558599999999
   type: audio
   audio.id: MEDIA_ID

2. FAZER DOWNLOAD DO ÁUDIO
   GET https://graph.facebook.com/v24.0/MEDIA_ID
   → Obtém URL temporária (válida 5 min)
   ↓
   GET https://media-service.whatsapp.com/d/H7...
   → Salva arquivo .ogg localmente

3. PROCESSAR ÁUDIO
   Transcrever/Processar com Gladia
   ↓
   resposta_audio: arquivo.ogg (novo)

4. FAZER UPLOAD DO ÁUDIO DE RESPOSTA
   POST https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/media
   file: arquivo_resposta.ogg
   type: audio/ogg; codecs=opus
   ↓
   MEDIA_ID_RESPOSTA

5. ENVIAR MENSAGEM DE ÁUDIO
   POST https://graph.facebook.com/v24.0/<PHONE_NUMBER_ID>/messages
   type: audio
   audio.id: MEDIA_ID_RESPOSTA
   audio.voice: true
```

---

## 7. Headers e Autenticação

### 7.1 Headers Obrigatórios para Envio

```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

### 7.2 Headers para Upload de Mídia

```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: multipart/form-data
```

### 7.3 Validação de Webhook

Para garantir que o webhook vem do WhatsApp, valide a assinatura:

```
X-Hub-Signature: sha256=<HASH>
```

O hash é calculado como: `SHA256(payload + app_secret)`

---

## 8. Tratamento de Erros

### 8.1 Erros Comuns

| Código | Erro | Causa | Solução |
|--------|------|-------|---------|
| 400 | Invalid phone number format | Número sem código de país | Use formato: `558599999999` (55 = Brasil) |
| 401 | Invalid access token | Token expirado ou inválido | Renove o token Bearer |
| 403 | Insufficient permissions | Token sem permissões | Adicione permissão `whatsapp_business_messaging` |
| 404 | Media not found | MEDIA_ID inválido ou expirado | Refaça o upload |
| 429 | Rate limit exceeded | Muitas requisições | Implemente fila com backoff exponencial |
| 500 | Internal server error | Erro do servidor | Tente novamente com retry logic |

### 8.2 Retry Logic Recomendada

```
1. Primeira tentativa imediata
2. Se falhar com erro 429 ou 5xx:
   - Aguarde 1 segundo
   - Tente novamente
   - Se falhar, aguarde 2 segundos
   - Tente novamente
   - Se falhar, aguarde 4 segundos
   - Tente novamente
   (Parar após 3 tentativas com backoff exponencial)
```

---

## 9. Limites e Quotas

- **Taxa de envio**: 80 mensagens por segundo por número
- **Tamanho de mensagem de texto**: 4096 caracteres
- **Tamanho de arquivo de áudio**: 16 MB
- **Validade do MEDIA_ID**: 30 dias
- **Validade da URL temporária**: 5 minutos
- **Janela de resposta**: 24 horas para responder mensagens de clientes
- **Requisições em paralelo**: Use fila para não exceder 80 msg/s

---

## 10. Exemplo Prático Completo (Pseudocódigo)

```python
# 0. WEBHOOK VERIFICATION
@app.get("/webhooks/whatsapp")
def verify_webhook(request):
    if request.args.get('hub.mode') == 'subscribe':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            print("WEBHOOK VERIFIED")
            return request.args.get('hub.challenge')
    return "Verification failed", 403

# 1. RECEBER WEBHOOK
@app.post("/webhooks/whatsapp")
def receive_message(request):
    data = request.json
    
    for entry in data['entry']:
        for change in entry['changes']:
            if change['field'] == 'messages':
                msg = change['value']['messages'][0]
                from_number = msg['from']
                message_id = msg['id']
                msg_type = msg['type']
                
                # 2. PROCESSAR TEXTO
                if msg_type == 'text':
                    text_body = msg['text']['body']
                    response = process_text(text_body)
                    send_text_message(from_number, response)
                
                # 2. PROCESSAR ÁUDIO
                elif msg_type == 'audio':
                    media_id = msg['audio']['id']
                    
                    # Fazer download
                    audio_url = get_media_url(media_id)
                    audio_file = download_audio(audio_url)
                    
                    # Processar
                    transcript = transcribe_audio(audio_file)
                    response_text = process_text(transcript)
                    
                    # Sintetizar resposta em áudio
                    response_audio = text_to_speech(response_text)
                    
                    # Fazer upload
                    response_media_id = upload_audio(response_audio)
                    
                    # Enviar
                    send_audio_message(from_number, response_media_id)

# 3. ENVIAR MENSAGEM DE TEXTO
def send_text_message(to_number, body):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": body
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 4. ENVIAR MENSAGEM DE ÁUDIO
def send_audio_message(to_number, media_id):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "audio",
        "audio": {
            "id": media_id,
            "voice": True
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 5. FAZER UPLOAD DE ÁUDIO
def upload_audio(audio_file_path):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    with open(audio_file_path, 'rb') as f:
        files = {
            'file': (f, open(audio_file_path, 'rb'), 'audio/ogg; codecs=opus'),
            'type': (None, 'audio/ogg; codecs=opus'),
            'messaging_product': (None, 'whatsapp')
        }
        response = requests.post(url, headers=headers, files=files)
    return response.json()['id']

# 6. OBTER URL DA MÍDIA
def get_media_url(media_id):
    url = f"https://graph.facebook.com/v24.0/{media_id}?phone_number_id={PHONE_NUMBER_ID}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    return response.json()['url']

# 7. FAZER DOWNLOAD DO ÁUDIO
def download_audio(media_url):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.get(media_url, headers=headers)
    with open('temp_audio.ogg', 'wb') as f:
        f.write(response.content)
    return 'temp_audio.ogg'
```

---

## 11. Resumo dos Endpoints Utilizados

| Operação | Método | Endpoint | Descrição |
|----------|--------|----------|-----------|
| Receber mensagem | POST | `https://seu-dominio.com/webhooks/whatsapp` | Seu servidor recebe webhooks |
| Enviar texto | POST | `https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages` | Envia mensagem de texto |
| Enviar áudio | POST | `https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages` | Envia mensagem de áudio |
| Upload de mídia | POST | `https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/media` | Faz upload de arquivo de áudio |
| Obter URL da mídia | GET | `https://graph.facebook.com/v24.0/{MEDIA_ID}` | Obtém URL temporária da mídia |
| Fazer download | GET | `https://media-service.whatsapp.com/d/{HASH}` | Faz download do arquivo |
| Validar webhook | GET | `https://seu-dominio.com/webhooks/whatsapp?hub.mode=subscribe&hub.challenge=...` | Validação do WhatsApp |

---

## 12. Diagrama de Sequência

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Usuário   │         │ Sua Aplicação│         │ WhatsApp API│
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                       │                       │
       │ 1. Envia mensagem     │                       │
       │──────────────────────────────────────────────>│
       │                       │                       │
       │                       │ 2. Webhook            │
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ 3. Processa           │
       │                       │    (se áudio,         │
       │                       │     faz download)     │
       │                       │                       │
       │                       │ 4. Gera resposta      │
       │                       │    (se áudio,         │
       │                       │     faz upload)       │
       │                       │                       │
       │                       │ 5. Envia resposta     │
       │                       │──────────────────────>│
       │                       │                       │
       │ 6. Recebe resposta    │                       │
       │<──────────────────────────────────────────────│
       │                       │                       │
```

---

## 13. Considerações de Produção

1. **Segurança**:
   - Nunca exponha seu ACCESS_TOKEN no código-fonte
   - Use variáveis de ambiente
   - Valide assinatura do webhook

2. **Performance**:
   - Implemente fila de mensagens (Redis, RabbitMQ)
   - Respeite limite de 80 msg/segundo
   - Use async/await para não bloquear threads

3. **Resiliência**:
   - Implemente retry logic com backoff exponencial
   - Armazene IDs de mensagens enviadas
   - Trate webhooks duplicados idempotentemente

4. **Monitoramento**:
   - Log todos os eventos (recebimento, envio, erros)
   - Monitore taxa de entrega
   - Alerte sobre falhas de envio

5. **Armazenamento de Mídia**:
   - MEDIA_IDs expiram em 30 dias
   - URLs temporárias expiram em 5 minutos
   - Considere armazenar cópia local dos áudios

---

## Documentação Relacionada

- [WhatsApp Cloud API - Referência de Mensagens](whatsapp-api-message.md)
- [WhatsApp Cloud API - Especificação de Mensagens de Áudio](whatsapp-api-audio-spec.md)
- [WhatsApp Cloud API - Referência de Mídia](whatsapp-api-media-reference.md)
