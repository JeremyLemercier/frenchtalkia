# WhatsApp Cloud API - Especificação de Mensagens de Áudio - Versão: 1.0.0
Este documento é complemento da documentação principal [WhatsApp Cloud API - Referência de Mensagens](whatsapp-api-message.md:1)


## Tipos de Mensagens Vocais
A distinção mais importante é a origem e o propósito do áudio:

- **Mensagem de Áudio**: É um arquivo de som pré-existente que você anexa e envia. Pense nela como um anexo, como uma foto ou um documento. Pode ser uma música, um podcast, um efeito sonoro, etc.

Se você enviar qualquer outro formato (como MP3, que é convertido para MPEG pela API), ele será entregue como uma mensagem de áudio padrão, parecendo mais um anexo de arquivo.

- **Mensagem de Voz**: É uma gravação de voz feita na hora, no momento da conversa, para ser enviada como uma nota de voz pessoal. É o famoso "áudio do zap" que gravamos segurando o microfone no aplicativo.

Se você quer que sua mensagem apareça no WhatsApp como um "áudio" gravado na hora (com a ondinha e a foto de perfil), você precisa codificar seu arquivo de áudio no formato `OGG` com **codec `Opus`** antes de fazer o upload para a API.


## Supported media types
| Audio Type | Extension | MIME Type | Max Size |
| --- | --- | --- |
| AAC | .aac | audio/aac | 16 MB |
| AMR | .amr | audio/amr | 16 MB |
| MP3 | .mp3 | audio/mpeg | 16 MB |
| MP4 Audio | .m4a | audio/mp4 | 16 MB |
| OGG Audio | .ogg | audio/ogg (OPUS codecs only; base audio/ogg not supported; mono input only) | 16 MB |

Os arquivos de áudio devem ter no máximo 16 MB.

> **Nota importante:** Os erros mais comuns associados a arquivos de áudio são tipos MIME incompatíveis (o tipo MIME não corresponde ao tipo de arquivo indicado pelo nome do arquivo) e codificação inválida para arquivos .ogg (somente codecs OPUS). Se você encontrar um erro ao enviar uma mensagem com um arquivo de mídia, verifique se o tipo MIME real do seu arquivo de áudio corresponde ao tipo declarado e se é um dos tipos listados acima. Para arquivos .ogg, certifique-se de estar usando o codec OPUS.



curl 'https://graph.facebook.com/<API_VERSION>/<WHATSAPP_BUSINESS_PHONE_NUMBER_ID>/messages' \ 
-H 'Content-Type: application/json' \ 
-H 'Authorization: Bearer <ACCESS_TOKEN>' \ 
-d '{ 
  "messaging_product": "whatsapp",
  "recipient_type": "individual", 
  "to": "<WHATSAPP_USER_PHONE_NUMBER>", 
  "type": "audio", 
  "audio": { 
    "id": "<MEDIA_ID>", <!-- Only if using uploaded media --> 
    "link": "<MEDIA_URL>", <!-- Only if using hosted media (not recommended) --> 
    
  } 
}' 


## Fazendo Upload de Mídia

### Usando o ID da Mídia
Para obter um ID de mídia, você precisa fazer o upload do seu áudio para os servidores da API de Nuvem. Isso é feito com uma requisição `POST` para o endpoint `/media`.

**Exemplo de Requisição:**

```bash
curl -X POST 'https://graph.facebook.com/v24.0/<WHATSAPP_BUSINESS_PHONE_NUMBER_ID>/media' \
-H 'Authorization: Bearer ACCESS_TOKEN' \
-F 'file=@"URL_LOCAL_DO_ARQUIVO"' \
-F 'type="audio/mpeg"' \
-F 'messaging_product="whatsapp"'
```

Uma requisição bem-sucedida retorna um objeto JSON com o ID da mídia:

```json
{
  "id": "<MEDIA_ID>"
}
```

Uma vez que você tenha o ID da mídia, use-o no campo `"id"` da sua requisição `POST` para o endpoint `/messages`.

**Exemplo de Requisição:**

```bash
curl -X POST 'https://graph.facebook.com/v24.0/<WHATSAPP_BUSINESS_PHONE_NUMBER_ID>/messages' \
-H 'Authorization: Bearer ACCESS_TOKEN' \
-H 'Content-Type: application/json' \
-d '{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "<WHATSAPP_USER_PHONE_NUMBER>",
  "type": "audio",
  "audio": {
    "id": "<MEDIA_ID>",
    "voice": <IS_VOICE?> <!-- Incluir e definir como true, somente se o áudio for uma mensagem de voz --> 
  }
}'
```

### Usando uma URL

Em vez de fazer o upload do seu áudio, você pode usar a URL pública do seu arquivo.

**Exemplo de Requisição:**

```bash
curl -X POST 'https://graph.facebook.com/v24.0/<WHATSAPP_BUSINESS_PHONE_NUMBER_ID>/messages' \
-H 'Authorization: Bearer ACCESS_TOKEN' \
-H 'Content-Type: application/json' \
-d '{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "<WHATSAPP_USER_PHONE_NUMBER>",
  "type": "audio",
  "audio": {
    "link": "<MEDIA_URL>",
    "voice": <IS_VOICE?> <!-- Incluir e definir como true, somente se o áudio for uma mensagem de voz --> 
  }
}'
```

> **Nota:** Apenas os seguintes tipos de arquivo são suportados ao usar uma URL: `audio/aac`, `audio/mp4`, `audio/amr`, `audio/mpeg`, `audio/ogg; codecs=opus`.

### **Parâmetros do corpo da requisição**

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `messaging_product` | String | `whatsapp` |
| `recipient_type` | String | `individual` |
| `to` | String | Número de telefone do destinatário. Formate este número com um `+` no início e o código do país para garantir a formatação correta. |
| `type` | String | `audio` |
| `audio` | Objeto | Objeto de áudio. |

#### **Audio object**

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `link` | String | O protocolo e a URL da mídia a ser enviada. Use apenas com URLs HTTP/HTTPS. Não use este campo se você usar o campo `id`. |
| `id` | String | O ID do objeto de mídia. Não use este campo se você usar o campo `link`. |
| `voice` | Booleano | Defina como `true` se o áudio for uma mensagem de voz, caso contrário, omita este campo. |

## Example response

```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "RECIPIENT_PHONE_NUMBER",
      "wa_id": "WHATSAPP_ID"
    }
  ],
  "messages": [
    {
      "id": "wamid.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    }
  ]
}
```

**Parâmetros do corpo da resposta**

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `messaging_product` | String | `whatsapp` |
| `contacts` | Array | Array (lista) de objetos de contato. |
| `contacts[].input` | String | O número de telefone do destinatário. |
| `contacts[].wa_id` | String | O ID do WhatsApp do destinatário. |
| `messages` | Array | Array (lista) de objetos de mensagem. |
| `messages[].id` | String | O ID da mensagem. |

**Códigos de erro**

| Código | Mensagem | Descrição |
| :--- | :--- | :--- |
| 400 | Formato de número de telefone inválido | O número de telefone não está em um formato válido. |
| 400 | Tipo de mídia inválido | O tipo de mídia não é suportado. |
| 400 | Tamanho da mídia muito grande | O arquivo de mídia é maior que 16 MB. |
| 401 | Token de acesso inválido | O token de acesso é inválido ou expirou. |
| 403 | Permissões insuficientes | O token de acesso não possui as permissões necessárias. |
| 404 | Mídia não encontrada | O ID do objeto de mídia não existe. |
| 429 | Limite de taxa excedido | Muitas requisições foram feitas. |
| 500 | Erro interno do servidor | Ocorreu um erro interno no servidor. |


## Restrições

*   Arquivos de áudio devem ter 16 MB ou menos.
*   Arquivos de áudio devem estar em um dos tipos de mídia suportados.
*   Arquivos de áudio devem ser acessíveis via HTTP ou HTTPS.
*   Arquivos de áudio não podem ser enviados para grupos.
*   Arquivos de áudio não podem ser enviados com uma legenda.

## **Melhores práticas**

*   Use o parâmetro `link` para enviar arquivos de áudio que estão hospedados em uma URL pública.
*   Use o parâmetro `id` para enviar arquivos de áudio que foram carregados para a API de Nuvem do WhatsApp.
*   Garanta que os arquivos de áudio estejam em um dos tipos de mídia suportados.
*   Garanta que os arquivos de áudio tenham 16 MB ou menos.
*   Garanta que os arquivos de áudio sejam acessíveis via HTTP ou HTTPS.
*   Use uma CDN (Rede de Distribuição de Conteúdo) para hospedar arquivos de áudio para melhor desempenho.
*   Implemente uma lógica de nova tentativa com recuo exponencial (exponential backoff) para requisições que falharam.
*   Monitore seu uso da API para evitar atingir os limites de taxa.

## **Recursos relacionados**

- [Messages](https://developers.facebook.com/docs/whatsapp/cloud-api/messages)
- [Media](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media)
- [Webhooks](https://developers.facebook.com/docs/whatsapp/webhooks)