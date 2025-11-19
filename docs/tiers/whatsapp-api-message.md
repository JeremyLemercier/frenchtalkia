# WhatsApp Cloud API - Referência de Mensagens - Versão: 1.0.0

## Visão Geral

Esta documentação cobre a API de Mensagens do WhatsApp Cloud, que permite enviar e gerenciar mensagens através da plataforma WhatsApp Business. A API suporta múltiplos tipos de mensagens incluindo texto, mídia, templates e mensagens interativas.

**Público-alvo**: Desenvolvedores integrando WhatsApp Business em aplicações.

## Pré-requisitos

- Conta WhatsApp Business ativa
- Token de acesso válido (Bearer Token)
- ID do número de telefone do WhatsApp Business
- ID do destinatário (número de telefone com código de país)
- Conhecimento básico de APIs REST
- Biblioteca HTTP (axios, fetch, etc.)

## Endpoint Base

```
POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages
```

**Parâmetros de Path:**
- `PHONE_NUMBER_ID`: ID do seu número de telefone WhatsApp Business

**Headers Obrigatórios:**
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

## Tipos de Mensagens Suportadas

### 1. Mensagem de Texto

Envia uma mensagem de texto simples.

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "5585987654321",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "Olá! Esta é uma mensagem de teste."
  }
}
```

**Parâmetros:**
- `messaging_product` (string, obrigatório): Sempre `"whatsapp"`
- `recipient_type` (string, opcional): Sempre `"individual"`
- `to` (string, obrigatório): Número do destinatário com código de país (sem símbolos)
- `type` (string, opcional): `"text"`
- `text.body` (string, obrigatório): Conteúdo da mensagem (máx. 4096 caracteres)
- `text.preview_url` (boolean, opcional): Mostrar preview de URLs (padrão: false)

### 2. Mensagem com Mídia

Envia imagens, vídeos, áudio ou documentos.

```json
{
  "messaging_product": "whatsapp",
  "to": "5585987654321",
  "type": "image",
  "image": {
    "link": "https://example.com/image.jpg"
  }
}
```

**Tipos de Mídia Suportados:**
- `image`: JPEG, PNG (máx. 16 MB)
- `video`: MP4, 3GPP (máx. 16 MB)
- `audio`: AAC, MP4, AMR, OGG (máx. 16 MB)
- `document`: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT (máx. 100 MB)

**Parâmetros de Mídia:**
- `id` (string): Obrigatório quando o paramêtro "type" é "audio", "image", "sticker", or "video" e você não está usando um "link" ou "text".
- `link` (string): URL pública da mídia
- `caption` (string, opcional): Legenda para imagens e vídeos (não aplicável para audio ou sticker)

### 3. Mensagem com Template

Envia mensagens pré-aprovadas com variáveis.

```json
{
  "messaging_product": "whatsapp",
  "to": "5585987654321",
  "type": "template",
  "template": {
    "name": "hello_world",
    "language": {
      "code": "pt_BR"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "João"
          }
        ]
      }
    ]
  }
}
```

**Parâmetros:**
- `template.name` (string, obrigatório): Nome do template aprovado
- `template.language.code` (string, obrigatório): Código do idioma (ex: `pt_BR`, `en_US`)
- `template.components` (array, opcional): Componentes com parâmetros dinâmicos da mensagem

### 4. Mensagem Interativa

Envia botões, listas ou respostas rápidas.

#### Botões

```json
{
  "messaging_product": "whatsapp",
  "to": "5585987654321",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "Qual é sua preferência?"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "btn_1",
            "title": "Opção 1"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "btn_2",
            "title": "Opção 2"
          }
        }
      ]
    }
  }
}
```

#### Lista

```json
{
  "messaging_product": "whatsapp",
  "to": "5585987654321",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {
      "text": "Selecione uma opção"
    },
    "action": {
      "button": "Menu",
      "sections": [
        {
          "title": "Seção 1",
          "rows": [
            {
              "id": "row_1",
              "title": "Item 1",
              "description": "Descrição do item 1"
            },
            {
              "id": "row_2",
              "title": "Item 2",
              "description": "Descrição do item 2"
            }
          ]
        }
      ]
    }
  }
}
```

**Parâmetros Interativos:**
- `interactive.type` (string): `"button"`, `"list"` ou `"product"`
- `interactive.body.text` (string): Texto principal
- `interactive.footer.text` (string, opcional): Rodapé
- `interactive.action.buttons` (array): Máximo 3 botões
- `interactive.action.sections` (array): Máximo 10 seções com até 10 itens cada

### 5. Mensagem de Localização

```json
{
  "messaging_product": "whatsapp",
  "to": "5585987654321",
  "type": "location",
  "location": {
    "latitude": "-3.7319",
    "longitude": "-38.5267",
    "name": "Fortaleza, CE",
    "address": "Avenida Beira Mar, Fortaleza"
  }
}
```

## Resposta da API

### Sucesso (200 OK)

```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "5585987654321",
      "wa_id": "5585987654321"
    }
  ],
  "messages": [
    {
      "id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA"
    }
  ]
}
```

#### Estrutura da Resposta
Se a API aceitar sua solicitação de envio de mensagem e não encontrar erros, ela retornará a seguinte resposta JSON: Observe que esta resposta indica apenas que a API aceitou sua solicitação; ela não indica que sua mensagem foi entregue. O status de entrega da mensagem é comunicado por meio dos webhooks de mensagens.

```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "<WHATSAPP_USER_PHONE_NUMBER>",
      "wa_id": "<WHATSAPP_USER_ID>"
    }
  ],
  "messages": [
    {
      "id": "<WHATSAPP_MESSAGE_ID>",
      "group_id": "<GROUP_ID>", <!-- Only included if messaging a group -->
      "message_status": "<PACING_STATUS>" <!-- Only included if sending a template -->
    }
  ]
}
```

**Parâmetros:**
- `message.id`: ID da mensagem do WhatsApp. Esse ID aparece nos webhooks de mensagens associadas, como webhooks de mensagens enviadas, lidas e entregues.
- `message.group_id`: Identificador do grupo (apenas incluído se a mensagem for enviada para um grupo)
- `message.message_status`: Status de pacing (apenas incluído se enviando um template)
- `contacts.input`: Número de telefone do usuário do WhatsApp. Pode não corresponder ao valor de wa_id.
- `contacts.wa_id`: ID do usuário do WhatsApp. Pode não corresponder ao valor de input.


### Erro

```json
{
  "error": {
    "message": "Invalid phone number format",
    "type": "OAuthException",
    "code": 400,
    "error_subcode": 2200
  }
}
```

## Códigos de Erro Comuns

| Código | Mensagem | Solução |
|--------|----------|---------|
| 400 | Invalid phone number format | Verifique o formato do número (com código de país, sem símbolos) |
| 401 | Invalid access token | Renove o token de acesso |
| 403 | Insufficient permissions | Verifique as permissões do token |
| 429 | Rate limit exceeded | Aguarde antes de enviar novas mensagens |
| 500 | Internal server error | Tente novamente mais tarde |

## Limites e Quotas

- **Taxa de envio**: 80 mensagens por segundo por número
- **Tamanho de mensagem**: 4096 caracteres (texto)
- **Tamanho de mídia**: 16 MB (imagens/vídeos), 100 MB (documentos)
- **Janela de resposta**: 24 horas para responder a mensagens de clientes
- **Mensagens de template**: Sem limite de janela de tempo

## Responder à uma mensagem

Precisa da Message ID da mensagem recebida.

```json
{
  "messaging_product": "whatsapp",
  "context": {
     "message_id": "MESSAGE_ID"
  },
  "to": "PHONE_NUMBER",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "your-text-message-content"
  }
```

## Solução de Problemas

- **Problema**: Mensagem não é entregue → **Solução**: Verifique se o número está registrado no WhatsApp e se o token é válido
- **Problema**: Erro 429 (Rate limit) → **Solução**: Implemente fila de mensagens com delay entre envios
- **Problema**: Template não encontrado → **Solução**: Verifique o nome exato do template aprovado
- **Problema**: Mídia não carrega → **Solução**: Certifique-se de que a URL é pública e acessível
- **Problema**: Caracteres especiais aparecem errados → **Solução**: Verifique a codificação UTF-8 da requisição

## Webhooks e Callbacks
Para receber confirmações de entrega e mensagens recebidas, configure webhooks.

## Melhores Práticas

1. **Armazene IDs de Mensagens**: Mantenha registro dos `wamid` para rastreamento
2. **Implemente Retry Logic**: Use backoff exponencial para falhas temporárias
3. **Valide Números**: Sempre valide o formato do número antes de enviar
4. **Use Templates**: Para mensagens recorrentes, use templates aprovados
5. **Monitore Taxa de Envio**: Respeite os limites de 80 msg/s
6. **Trate Webhooks Idempotentemente**: Processe eventos duplicados com segurança
7. **Criptografe Tokens**: Nunca exponha tokens em código ou logs

## Documentos Relacionados

- [Documentação Oficial WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Referência de Webhooks](https://developers.facebook.com/docs/whatsapp/webhooks)
- [Guia de Templates](https://developers.facebook.com/docs/whatsapp/message-templates)
- [Limites e Quotas](https://developers.facebook.com/docs/whatsapp/messaging-limits)
- [WhatsApp Cloud API - Exemplos de implementação simples](whatsapp-api-exemplos.md:1)
- [WhatsApp Cloud API - Especificação de Mensagens de Áudio](whatsapp-api-audio-spec.md:1)