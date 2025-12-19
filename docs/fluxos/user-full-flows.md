# Fluxos Completos do Usuário
## Participantes do Sistema

- **Usuário (WhatsApp):** O cliente final que interage através do aplicativo.
- **Meta (WhatsApp Cloud API):** Interface oficial para recepção e envio de mensagens.
- **Servidor (Backend):** O núcleo da lógica de negócio e integração.
- **Gladia API (STT):** Serviço responsável por transformar áudio em texto.
- **Mistral AI (LLM):** Inteligência artificial que processa o texto e gera respostas.
- **Murf.ai (TTS):** Serviço que converte o texto da resposta em áudio sintetizado.

---

## Parte 1: Fluxo de Mensagem de Texto

1. **Envio:** O **Usuário** envia uma mensagem de texto via WhatsApp.
2. **Recebimento:** A **Meta** dispara um Webhook `POST /webhook` para o **Servidor**, contendo o número do remetente, o ID da mensagem e o corpo do texto.
3. **Extração:** O **Servidor** extrai o número de telefone e o conteúdo textual da requisição.
4. **Processamento:** O **Servidor** aplica a lógica de resposta (genérica ou específica).
5. **Resposta:** O **Servidor** faz um `POST` para a API da **Meta** com a resposta formatada.
6. **Entrega:** A **Meta** entrega a mensagem de texto final ao **Usuário**.

---

## Parte 2: Fluxo de Mensagem de Áudio

### 2.1 e 2.2: Recepção e Download do Áudio
- **Entrada:** O **Usuário** envia uma mensagem de áudio que chega ao **Servidor** via Webhook da **Meta** (contendo um `MEDIA_ID`).
- **Resgate da URL:** O **Servidor** solicita os detalhes da mídia à **Meta** via `GET /media/{MEDIA_ID}` e recebe uma URL temporária válida por 5 minutos.
- **Download:** O **Servidor** acessa a URL, baixa o arquivo binário (.ogg) e o armazena localmente para processamento.

### 2.3: Speech-to-Text (Gladia API)
- **Upload:** O **Servidor** envia o arquivo para a **Gladia** (`POST /v2/upload`) e recebe uma URL interna.
- **Transcrição:** O **Servidor** solicita o início da transcrição pré-gravada.
- **Polling:** O sistema entra em um loop de consulta (`GET`) até que o status mude de "queued" para "done", momento em que o texto completo (`full_transcript`) é retornado ao **Servidor**.

### 2.4: Processamento LLM (Mistral AI)
- **Interação:** O **Servidor** envia a transcrição para a **Mistral AI** através do endpoint de conversação, utilizando o ID de um agente configurado.
- **Inteligência:** A **Mistral** processa o contexto e retorna um JSON contendo o `conversation_id` e o conteúdo textual da resposta gerada.

### 2.5: Text-to-Speech (Murf.ai)
- **Sintetização:** O texto da resposta é enviado para a **Murf.ai** (`POST /v1/speech/generate`) especificando a voz, estilo e formato (OGG).
- **Recuperação:** A **Murf.ai** gera o áudio e fornece uma URL válida por 72 horas. O **Servidor** então baixa esse arquivo ou decodifica o Base64 recebido.

### 2.6: Envio da Resposta de Áudio
- **Upload para Meta:** O **Servidor** envia o arquivo de áudio sintetizado para os servidores da **Meta** para gerar um novo `MEDIA_ID`.
- **Notificação:** O **Servidor** envia o comando final de mensagem para a **Meta**, referenciando o `MEDIA_ID` e definindo o parâmetro `audio.voice=true` para que apareça como mensagem de voz.
- **Finalização:** A **Meta** entrega a resposta em áudio diretamente no WhatsApp do **Usuário**.

---

## Documentação Relacionada

- [Diagrama Mermaid do Fluxo Completo do usuário - para envio e recebimento de mensagens de texto e audio](diagram-user-full-flows.mmd)