# Fluxo de Integração da API Gladia

## Fluxo Completo de Integração da Gladia

### **Etapa 1: Upload do Arquivo de Áudio**
*Documento: gladia-api-upload.md*

Você começa fazendo o **upload do seu arquivo de áudio** para os servidores da Gladia.

- **Método HTTP**: `POST`
- **Endpoint**: `https://api.gladia.io/v2/upload`
- **Autenticação**: Header `x-gladia-key: <sua-chave-api>`
- **Formato do corpo**: `multipart/form-data` contendo o arquivo de áudio/vídeo no campo `audio`

**Resposta esperada (200 OK)**:
```json
{
  "audio_url": "https://api.gladia.io/file/6c09400e-23d2-4bd2-be55-96a5ececfa3b",
  "audio_metadata": { ... }
}
```

Você recebe uma **`audio_url`** que será usada na próxima etapa. Esta URL interna da Gladia referencia o arquivo que você enviou.

---

### **Etapa 2: Iniciar a Transcrição**
*Documento: gladia-api-transciption.md*

Com a `audio_url` obtida no passo anterior, você **inicia uma tarefa de transcrição**.

- **Método HTTP**: `POST`
- **Endpoint**: `https://api.gladia.io/v2/pre-recorded`
- **Autenticação**: Header `x-gladia-key: <sua-chave-api>`
- **Formato do corpo**: `application/json`

O corpo deve conter:
- `audio_url`: A URL do arquivo obtida no upload (ex: `https://api.gladia.io/file/6c09400e-23d2-4bd2-be55-96a5ececfa3b`)
- `language_config`: Objeto com configurações de idioma:
  - `languages`: Array de códigos de idioma (ex: `["fr"]` para francês)
  - `code_switching`: Boolean indicando se deve permitir múltiplos idiomas

**Resposta esperada (201 Created)**:
```json
{
  "id": "45463597-20b7-4af7-b3b3-f5fb778203ab",
  "result_url": "https://api.gladia.io/v2/transcription/45463597-20b7-4af7-b3b3-f5fb778203ab"
}
```

Você recebe um **`id`** da tarefa de transcrição. Este ID será usado para consultar o resultado.

---

### **Etapa 3: Recuperar o Resultado da Transcrição**
*Documento: gladia-api-getresult.md*

Após iniciar a transcrição, você **consulta o status e obtém o resultado**.

- **Método HTTP**: `GET`
- **Endpoint**: `https://api.gladia.io/v2/pre-recorded/{transcription_id}` (substitua `{transcription_id}` pelo ID recebido na etapa 2)
- **Autenticação**: Header `x-gladia-key: <sua-chave-api>`

**Resposta esperada (200 OK)**:
```json
{
  "id": "01J3QPA1YJ5Y9T...J7",
  "status": "done",
  "result": {
    "transcription": {
      "full_transcript": "Este é o texto completo da transcrição...",
      "languages": ["fr"],
      "utterances": [ ... ]
    }
  }
}
```

O campo **`status`** pode ser:
- `queued`: A transcrição ainda está sendo processada (aguarde e faça nova requisição)
- `done`: A transcrição foi concluída

Quando `status` for `done`, o campo **`result.transcription.full_transcript`** contém o **texto completo da transcrição** do seu áudio.

---

## Resumo do Fluxo

```
1. POST /v2/upload 
   ↓ (obtém audio_url)
2. POST /v2/pre-recorded 
   ↓ (obtém transcription_id)
3. GET /v2/pre-recorded/{transcription_id} 
   ↓ (obtém full_transcript quando status = "done")
```
