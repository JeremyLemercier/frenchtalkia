# WhatsApp Cloud API - Especificação complementar para Mídia - Versão: 1.0.0

O endpoint de mídia da API de Nuvem do WhatsApp Business permite que você faça upload, download e exclua mídias.

## Como Funciona
Para enviar uma mensagem de mídia, você deve primeiro fazer o upload da mídia para os servidores da API de Nuvem. Isso gera um ID de mídia que você pode usar para enviar a mídia para seus clientes.

Para usar o endpoint de mídia, você precisará de:

*   O ID de um número de telefone do WhatsApp Business.
*   Um token de acesso do sistema ou do usuário.
*   A permissão `whatsapp_business_messaging`.

## Endpoints
O endpoint de mídia é um edge do nó de ID do número de telefone.

```
https://graph.facebook.com/VERSION/PHONE_NUMBER_ID/media
```

## Upload de Mídia
Para fazer o upload de mídia, envie uma requisição `POST` para `/PHONE_NUMBER_ID/media` e anexe a mídia à sua requisição.

**Exemplo de Requisição**

```bash
curl 'https://graph.facebook.com/<API_VERSION>/<PHONE_NUMBER_ID>/media' \
-H 'Authorization: Bearer <ACCESS_TOKEN>' \
-F 'messaging_product=whatsapp' \
-F 'file=@<FILE_PATH_AND_NAME>;type=<MIME_TYPE>'
```

**Parâmetros da Requisição**

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `file` | Form-data | **Obrigatório.** Caminho para o arquivo armazenado no seu sistema local. |
| `type` | Form-data | **Obrigatório.** Tipo de mídia. Use o tipo MIME do arquivo. Veja os tipos de mídia suportados. |
| `messaging_product` | Form-data | **Obrigatório.** Produto de mensagens sendo usado. Sempre `whatsapp`. |

**Resposta**

Uma requisição bem-sucedida retorna um objeto JSON com o ID da mídia.

```json
{
  "id": "MEDIA_ID"
}
```

Use este ID para enviar a mensagem de mídia. IDs de mídia expiram após 30 dias. Se você tentar acessar a mídia após a expiração, receberá uma mensagem de erro. Recomendamos que você salve o ID da mídia no seu banco de dados e o use para futuras requisições.

## Recuperar URL da Mídia
Para recuperar a URL da sua mídia, envie uma requisição `GET` para `/MEDIA_ID`.

**Exemplo de Requisição**

```bash
curl 'https://graph.facebook.com/<API_VERSION>/<MEDIA_ID>?phone_number_id=<BUSINESS_PHONE_NUMBER_ID>' \
-H 'Authorization: Bearer EAAJB'
```

**Parâmetros da Requisição**

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `phone_number_id` | Query String | **Opcional.** O ID do número de telefone do WhatsApp Business. Use este parâmetro para validar se a mídia pertence ao número de telefone do WhatsApp Business especificado. Se a mídia não pertencer ao número de telefone, a requisição falhará com um código de erro. |


**Resposta**

Uma requisição bem-sucedida retorna um objeto JSON com uma URL de mídia.

```json
{
  "messaging_product": "whatsapp",
  "url": "<MEDIA_URL>",
  "mime_type": "<MEDIA_MIME_TYPE>",
  "sha256": "<SHA_256_HASH>",
  "file_size": "<MEDIA_FILE_SIZE>",
  "id": "<MEDIA_ID>"
}
```

**Propriedades da Resposta**

| Propriedade | Tipo | Descrição |
| :--- | :--- | :--- |
| `url` | String | URL para a mídia. Esta URL é temporária e expira após 5 minutos. |
| `mime_type` | String | O tipo MIME da mídia. |
| `sha256` | String | O hash SHA256 da mídia. |
| `file_size` | Integer | O tamanho do arquivo em bytes. |
| `id` | String | O ID da mídia. |
| `messaging_product` | String | Produto de mensagens sendo usado. Sempre `whatsapp`. |


## Download de Mídia
Para baixar a mídia, use a URL retornada na resposta da recuperação de URL de mídia. Envie uma requisição `GET` para esta URL com um token de acesso.

**Exemplo de Requisição**

```bash
curl '<MEDIA_URL>' \
-H 'Authorization: Bearer EAAJB...' \
-o '<DESIRED_FILE_NAME>'
```

A resposta será o arquivo de mídia bruto. Você pode então salvar o arquivo.


## Excluir Mídia

Para excluir mídia, envie uma requisição `DELETE` para `/MEDIA_ID`.

**Exemplo de Requisição**

```bash
curl -X DELETE 'https://graph.facebook.com/<API_VERSION>/<MEDIA_ID>?phone_number_id=<BUSINESS_PHONE_NUMBER_ID>' \
-H 'Authorization: Bearer EAAJB...'
```

**Parâmetros da Requisição**

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `phone_number_id` | Query String | **Opcional.** O ID do número de telefone do WhatsApp Business. Use este parâmetro para validar se a mídia pertence ao número de telefone do WhatsApp Business especificado. Se a mídia não pertencer ao número de telefone, a requisição falhará com um código de erro. |

**Resposta**

Uma requisição bem-sucedida retorna um objeto JSON.

```json
{
  "success": true
}
```


## Tipos de Mídia Suportados

| Tipo | Tipo MIME | Tamanho Máximo |
| :--- | :--- | :--- |
| Áudio | `audio/aac`, `audio/mp4`, `audio/amr`, `audio/mpeg`, `audio/ogg; codecs=opus` | 16MB |
| Documento | Qualquer tipo MIME de documento válido | 100MB |
| Imagem | `image/jpeg`, `image/png` | 5MB |
| Sticker | `image/webp` | 100KB |
| Vídeo | `video/mp4`, `video/3gpp` | 16MB |

**Notas sobre Vídeo:**

*   Apenas os codecs de vídeo H.264 e de áudio AAC são suportados.
*   Apenas vídeos com um único stream de áudio ou sem stream de áudio são suportados.

## **Recursos relacionados**
- [WhatsApp Cloud API - Referência de Mensagens](whatsapp-api-message.md:1)
- [WhatsApp Cloud API - Especificação de Mensagens de Áudio](whatsapp-api-audio-spec.md:1)