# API Gladia: Iniciar uma Transcrição Pré-gravada - Versão: 2.0.0

## Visão Geral
Este documento descreve como iniciar uma tarefa de transcrição pré-gravada usando a API da Gladia. Esta funcionalidade permite enviar um arquivo de áudio (através de uma URL) e configurar diversos parâmetros para obter uma transcrição precisa e rica em detalhes. O resultado da transcrição deve ser obtido através do endpoint `GET /v2/pre-recorded/:id`.

## Pré-requisitos
-   **Chave de API**: É necessário ter uma chave de API da Gladia (`x-gladia-key`) para autenticar as requisições.
-   **URL do Áudio**: Uma URL acessível para um arquivo de áudio. Pode ser uma URL externa ou uma URL de um arquivo previamente enviado para a Gladia (`https://api.gladia.io/file/...`).

## Início Rápido

Para iniciar uma transcrição, envie uma requisição `POST` para o endpoint `/v2/pre-recorded` com a URL do áudio e os parâmetros desejados.

```bash
curl --request POST \
  --url https://api.gladia.io/v2/pre-recorded \
  --header 'Content-Type: application/json' \
  --header 'x-gladia-key: <api-key>' \
  --data '{
  "language_config": {
    "languages": [],
    "code_switching": false
  },
  "audio_url": "http://files.gladia.io/example/audio-transcription/split_infinity.wav"
}'
```

## Detalhes do Endpoint

-   **Método**: `POST`
-   **URL**: `https://api.gladia.io/v2/pre-recorded`

### Autenticação
A autenticação é feita através do cabeçalho (`Header`) da requisição, utilizando sua chave de API.

-   **Cabeçalho**: `x-gladia-key`
-   **Valor**: `Sua Chave de API da Gladia`

### Corpo da Requisição (Body)

O corpo da requisição deve ser em formato `application/json` e pode conter os seguintes campos:

-   **`audio_url`** (string, obrigatório): URL para um arquivo Gladia ou um arquivo externo de áudio ou vídeo.
-   **`language_config`** (object, obrigatório): Configurações de idioma.
    -   `languages` (array de strings): Lista de códigos de idioma a serem detectados. Ex: `["en", "pt"]`. If one language is set, it will be used for the transcription. Otherwise, language will be auto-detected by the model.
    -   `code_switching` (boolean): Se `true`, permite detecção de códigos de múltiplos idiomas. If true, language will be auto-detected on each utterance. Otherwise, language will be auto-detected on first utterance and then used for the rest of the transcription. If one language is set, this option will be ignored.

### Resposta de Sucesso (201 Created)

Se a tarefa de transcrição for iniciada com sucesso, a API retornará um objeto JSON com o ID da tarefa e a URL para consultar o resultado.

```json
{
  "id": "45463597-20b7-4af7-b3b3-f5fb778203ab",
  "result_url": "https://api.gladia.io/v2/transcription/45463597-20b7-4af7-b3b3-f5fb778203ab"
}
```

#### Campos da Resposta:

-   `id` (string): O ID único da tarefa de transcrição.
-   `result_url` (string): A URL completa para obter o resultado da transcrição usando o endpoint `GET`.

## Solução de Problemas

-   **Problema**: Recebendo erro `400 Bad Request`.
    -   **Solução**: Verifique se a `audio_url` foi fornecida e se é uma URL válida. Além disso, confira se todos os outros parâmetros no corpo da requisição estão formatados corretamente conforme a especificação da API.

-   **Problema**: Recebendo erro `401 Unauthorized`.
    -   **Solução**: Verifique se a sua `x-gladia-key` está correta e incluída no cabeçalho.

-   **Problema**: Recebendo erro `422 Unprocessable Entity`.
    -   **Solução**: Os parâmetros fornecidos estão incorretos. Verifique a documentação para garantir que os valores e tipos dos parâmetros estão corretos (ex: `language` deve ser um código de idioma válido).
