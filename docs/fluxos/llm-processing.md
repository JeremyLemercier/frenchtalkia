# Fluxo de Processamento LLM - Integração com API Mistral

## Visão Geral
Este documento descreve os fluxos de comunicação com a API da Mistral para iniciar conversas com agentes e continuar conversas existentes, incluindo endpoints, métodos HTTPS e detalhes das requisições e respostas.


---

## 1. Fluxo para Iniciar uma Conversa com um Agente

### Visão Geral do Fluxo
Este fluxo descreve o processo completo desde o envio da primeira mensagem do usuário até o recebimento da resposta do LLM, assumindo que o agente já foi criado e seu ID está disponível.

### Etapa 1: Preparação da Requisição
**Objetivo**: Construir a chamada para iniciar uma nova conversa com um agente.

**Método HTTP**: `POST`

**Endpoint**: `https://api.mistral.ai/v1/conversations/start`

**Headers Necessários**:
- `Authorization: Bearer {MISTRAL_API_KEY}`
- `Content-Type: application/json`

**Corpo da Requisição (JSON)**:
```python
{
    "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",  # ID do agente criado previamente
    "inputs": "Who is Albert Einstein?",                 # Mensagem do usuário (string ou lista)
    # "inputs": [{"role": "user", "content": "Who is Albert Einstein?"}]  # Alternativa: lista de mensagens
    # "store": true  # Opcional: armazenar conversa na nuvem (padrão: true)
}
```

**Detalhes da Requisição**:
- **agent_id**: Identificador único do agente que foi criado anteriormente (obrigatório)
- **inputs**: Pode ser uma string simples ou uma lista de objetos com `role` e `content` (obrigatório)
- **store**: Define se o histórico será armazenado na nuvem da Mistral (padrão: `true`, opcional)

### Etapa 2: Envio da Requisição
O cliente (sua aplicação) envia a requisição POST para o endpoint da Mistral com as credenciais de autenticação.

**Código Python de Exemplo**:
```python
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

response = client.beta.conversations.start(
    agent_id="ag_0684fe0e0b98773e8000323fc71a3986",
    inputs="Who is Albert Einstein?"
)
```

### Etapa 3: Processamento no Servidor da Mistral
**O que acontece no servidor**:
1. A API valida a autenticação e o ID do agente
2. Recupera a configuração do agente (modelo, instruções, ferramentas, parâmetros de conclusão)
3. Cria uma nova conversa e gera um `conversation_id` único
4. Envia a mensagem do usuário para o modelo LLM configurado no agente
5. O modelo processa a mensagem considerando:
   - As instruções do agente (system prompt)
   - Os parâmetros de conclusão do agente (temperatura, top_p, etc.)
   - Qualquer ferramenta disponível ao agente
6. O modelo gera uma resposta de conclusão

### Etapa 4: Recebimento da Resposta
**Método HTTP**: `POST` (resposta do servidor)

**Estrutura da Resposta (JSON)**:
```json
{
  "conversation_id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
  "outputs": [
    {
      "content": "Albert Einstein was a German-born theoretical physicist who is widely regarded as one of the most influential scientists of the 20th century...",
      "object": "entry",
      "type": "message.output",
      "created_at": "2025-06-16T09:19:09.031905Z",
      "completed_at": "2025-06-16T09:19:15.125347Z",
      "id": "msg_0684fe18d08278058000efa70b28fa5a",
      "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
      "model": "mistral-medium-2505",
      "role": "assistant"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 500,
    "total_tokens": 650,
    "connector_tokens": null,
    "connectors": null
  },
  "object": "conversation.response"
}
```

### Etapa 5: Armazenamento de Dados Importantes
**Dados críticos retornados que devem ser armazenados**:

1. **conversation_id**: Identificador único da conversa (`conv_0684fe18cbc57ba6800065acdd2b6c85`)
   - Essencial para continuar a conversa em futuras mensagens
   - Mapeia para o histórico completo armazenado na nuvem da Mistral

2. **outputs**: Array contendo as respostas do assistente
   - **content**: O texto da resposta gerada pelo modelo
   - **id**: Identificador único da mensagem
   - **created_at**: Timestamp quando a entrada foi criada
   - **completed_at**: Timestamp quando o processamento foi concluído

3. **usage**: Informações sobre consumo de tokens
   - **prompt_tokens**: Tokens utilizados na entrada
   - **completion_tokens**: Tokens gerados na saída
   - **total_tokens**: Total de tokens consumidos

### Resumo do Fluxo Completo - Primeira Mensagem

```
CLIENTE                          SERVIDOR MISTRAL                  MODELO LLM
   |                                  |                              |
   |---- POST /conversations/start --->|                              |
   |   (agent_id + inputs)             |                              |
   |                                   |-- Valida agent_id ---------->|
   |                                   |-- Recupera config do agente  |
   |                                   |-- Cria conversation_id       |
   |                                   |-- Envia mensagem ----------->|
   |                                   |                              |
   |                                   |<-- Processa mensagem --------|
   |                                   |<-- Retorna resposta ---------|
   |                                   |                              |
   |<-- conversation.response ---------|                              |
   |   (conversation_id, outputs)      |                              |
   |                                   |                              |
```

---

## 2. Fluxo para Continuar uma Conversa com um Agente

### Visão Geral do Fluxo
Este fluxo descreve o processo de enviar uma segunda mensagem a uma conversa existente, mantendo todo o histórico da conversa anterior, até receber a resposta do LLM para a segunda mensagem.

### Etapa 1: Preparação da Requisição para Continuar
**Objetivo**: Adicionar uma nova mensagem a uma conversa existente.

**Método HTTP**: `POST`

**Endpoint**: `https://api.mistral.ai/v1/conversations/append`

**Headers Necessários** (idênticos ao fluxo anterior):
- `Authorization: Bearer {MISTRAL_API_KEY}`
- `Content-Type: application/json`

**Corpo da Requisição (JSON)**:
```python
{
    "conversation_id": "conv_0684fe18cbc57ba6800065acdd2b6c85",  # ID da conversa anterior
    "inputs": "Translate to French.",                             # Segundo envio do texto
    # "completion_args": {  # Opcional: sobrescrever parâmetros do agente
    #     "temperature": 0.3,
    #     "top_p": 0.95
    # }
}
```

**Detalhes da Requisição**:
- **conversation_id**: Identificador único da conversa criada na etapa anterior (obrigatório)
- **inputs**: A nova mensagem do usuário (string ou lista, obrigatório)
- **completion_args**: Parâmetros opcionais que sobrescrevem os parâmetros padrão do agente (opcional)

### Etapa 2: Envio da Requisição para Continuar
O cliente envia a requisição POST para o endpoint de append com o ID da conversa e a nova mensagem.

**Código Python de Exemplo**:
```python
response = client.beta.conversations.append(
    conversation_id="conv_0684fe18cbc57ba6800065acdd2b6c85",  # ID da conversa anterior
    inputs="Translate to French.",
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95
    }
)
```

### Etapa 3: Recuperação do Histórico no Servidor
**O que acontece no servidor da Mistral**:
1. A API valida a autenticação e o `conversation_id`
2. Recupera todo o histórico da conversa anterior, incluindo:
   - A primeira mensagem do usuário: "Who is Albert Einstein?"
   - A resposta anterior do assistente
3. Recupera a configuração do agente associado à conversa
4. Constrói o contexto completo da conversa para passar ao modelo

### Etapa 4: Processamento da Segunda Mensagem
**No processador do LLM**:
1. O modelo recebe o histórico completo como contexto:
   ```
   user: "Who is Albert Einstein?"
   assistant: "Albert Einstein was a German-born theoretical physicist..."
   user: "Translate to French."
   ```
2. Processa a nova mensagem considerando:
   - Todos os parâmetros do agente (instruções, temperatura, etc.)
   - O contexto completo da conversa anterior
   - Qualquer instrução adicional para manter coerência
3. Gera uma resposta de conclusão baseada no novo pedido do usuário (tradução)

### Etapa 5: Recebimento da Resposta da Segunda Mensagem
**Estrutura da Resposta (JSON)**:
```json
{
  "conversation_id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
  "outputs": [
    {
      "content": "Albert Einstein était un physicien théoricien né en Allemagne, largement considéré comme l'un des scientifiques les plus influents du 20ᵉ siècle...",
      "object": "entry",
      "type": "message.output",
      "created_at": "2025-06-16T09:19:56.901953Z",
      "completed_at": "2025-06-16T09:20:03.257737Z",
      "id": "msg_0684fe1bce6e72bc8000f89d886633fe",
      "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
      "model": "mistral-medium-2505",
      "role": "assistant"
    }
  ],
  "usage": {
    "prompt_tokens": 384,
    "completion_tokens": 471,
    "total_tokens": 855,
    "connector_tokens": null,
    "connectors": null
  },
  "object": "conversation.response"
}
```

### Etapa 6: Dados Importantes da Segunda Resposta
**Informações críticas retornadas**:

1. **conversation_id**: Mantém-se o mesmo (`conv_0684fe18cbc57ba6800065acdd2b6c85`)
   - Confirma que as mensagens foram adicionadas à mesma conversa
   - O servidor mantém internamente o histórico crescente

2. **outputs[0].content**: A resposta traduzida para francês
   - Resultado da segunda solicitação do usuário

3. **outputs[0].id**: ID único desta nova mensagem de saída
   - Diferente do ID da primeira resposta
   - Exemplo: `msg_0684fe1bce6e72bc8000f89d886633fe`

4. **usage**: Contagem de tokens para esta segunda requisição
   - **prompt_tokens**: 384 (inclui todo o histórico + nova mensagem)
   - **completion_tokens**: 471 (resposta da tradução)
   - Totalizando 855 tokens para esta requisição

### Etapa 7: Histórico Persistente na Mistral
**O histórico agora contém**:
```json
{
  "entries": [
    {
      "role": "user",
      "content": "Who is Albert Einstein?",
      "id": "msg_0684fe18cbbf7c358000e14357aedf41",
      "created_at": "2025-06-16T09:19:08.734315Z"
    },
    {
      "role": "assistant",
      "content": "Albert Einstein was a German-born theoretical physicist...",
      "id": "msg_0684fe18d08278058000efa70b28fa5a",
      "created_at": "2025-06-16T09:19:09.031905Z"
    },
    {
      "role": "user",
      "content": "Translate to French.",
      "id": "msg_0684fe1bc9057cbe8000753468b64f7d",
      "created_at": "2025-06-16T09:19:56.563908Z"
    },
    {
      "role": "assistant",
      "content": "Albert Einstein était un physicien théoricien...",
      "id": "msg_0684fe1bce6e72bc8000f89d886633fe",
      "created_at": "2025-06-16T09:19:56.901953Z"
    }
  ]
}
```

### Resumo do Fluxo Completo - Segunda Mensagem

```
CLIENTE                          SERVIDOR MISTRAL                  MODELO LLM
   |                                  |                              |
   |-- POST /conversations/append ---->|                              |
   |   (conversation_id + inputs)      |                              |
   |                                   |-- Valida conversation_id ---|
   |                                   |-- Recupera histórico full   |
   |                                   |-- Constrói contexto ------->|
   |                                   |                              |
   |                                   |<-- Processa com contexto ----|
   |                                   |<-- Gera resposta ------------|
   |                                   |                              |
   |<-- conversation.response ---------|                              |
   |   (conversation_id, outputs)      |                              |
   |   (com histórico expandido)       |                              |
   |                                   |                              |
```

---

## Diferenças-Chave Entre os Dois Fluxos

| Aspecto | Primeira Mensagem (start) | Segunda Mensagem (append) |
|---------|---------------------------|------------------------|
| **Endpoint** | `/conversations/start` | `/conversations/append` |
| **Parâmetro Principal** | `agent_id` | `conversation_id` |
| **Contexto Enviado** | Vazio (primeira vez) | Histórico completo |
| **Tokens de Entrada** | Apenas a primeira mensagem | Histórico + nova mensagem |
| **Resposta** | Novo `conversation_id` retornado | Mesmo `conversation_id` |
| **Armazenamento** | Cria novo histórico | Expande histórico existente |

---

## Fluxo de Dados Completo - Duas Mensagens

```
┌─────────────────────────────────────────────────────────────────┐
│ INÍCIO: Agente já criado com ID = ag_0684fe0e0b98773e8000323...│
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ PRIMEIRA MENSAGEM (POST /conversations/start)                   │
│ ├─ Envio: { agent_id, inputs: "Who is Albert Einstein?" }      │
│ ├─ Servidor: Cria conversa, processa no LLM                    │
│ └─ Retorno: { conversation_id, outputs[0].content }             │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓ (Armazenar conversation_id)
         │
┌─────────────────────────────────────────────────────────────────┐
│ SEGUNDA MENSAGEM (POST /conversations/append)                   │
│ ├─ Envio: { conversation_id, inputs: "Translate to French." }  │
│ ├─ Servidor: Recupera histórico full, processa com contexto    │
│ └─ Retorno: { conversation_id, outputs[0].content }             │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ RESULTADO FINAL                                                  │
│ ├─ Histórico mantém 4 entradas (2 user + 2 assistant)          │
│ ├─ Conversação coerente com contexto preservado                │
│ └─ Conversation ID permanece o mesmo durante toda interação    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Considerações Importantes

### Autenticação
- Toda requisição deve incluir o header `Authorization: Bearer {MISTRAL_API_KEY}`
- A chave de API deve ser válida e ter permissão para acessar agents e conversations

### Armazenamento de Estado
- O `conversation_id` é crítico - deve ser armazenado para continuar conversas
- Se `store=true` (padrão), a Mistral mantém o histórico internamente
- Se `store=false`, o cliente é responsável por manter o histórico

### Tokens e Custos
- A primeira mensagem consome tokens apenas da primeira mensagem
- Mensagens subsequentes consomem tokens do histórico completo + nova mensagem
- Monitorar o uso total de tokens para gerenciar custos

### Limite de Contexto
- Cada solicitação (requisição ao LLM) inclui todos os tokens da conversa anterior
- O número total de tokens é reportado no campo `usage`
- Conversas muito longas podem atingir limites de contexto do modelo

### Taxa de Requisições
- Respeitar os limites de rate limiting da API da Mistral
- Implementar retry logic com backoff exponencial para falhas

### Tratamento de Erros
- Validar o `conversation_id` antes de tentar append
- Implementar timeouts apropriados para requisições
- **401 Unauthorized**: Chave de API inválida ou ausente
- **400 Bad Request**: Parâmetros inválidos ou agent_id/conversation_id incorretos
- **500 Internal Server Error**: Erro no processamento do servidor

---

## Documentos Relacionados
- [Mistral - Agentes e Conversas](../tiers/mistral-agents-and-conversations.md)
- [Mistral - Respostas API Agentes e Conversas](../tiers/mistral-conv-outputs-examples.md)
- [Documentação Oficial da Mistral - Agentes](https://docs.mistral.ai/agents/agents)
- [Documentação Oficial da Mistral - Conversas](https://docs.mistral.ai/agents/conversations)