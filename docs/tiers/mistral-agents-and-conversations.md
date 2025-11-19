# Mistral - Agentes e Conversas - Versão: 2.0.0

## Visão Geral
Este documento descreve como criar e gerenciar **Agentes** e **Conversas** utilizando a API da Mistral. O público-alvo são desenvolvedores que desejam implementar assistentes inteligentes com comportamento personalizado e histórico de interações persistente. Agentes e Conversas são recursos independentes que podem ser usados em conjunto ou separadamente.

## Pré-requisitos
- Conhecimento básico de APIs REST
- Uma chave de API válida da Mistral

## Início Rápido

### Criar um Agente Simples
Um agente é um conjunto de valores pré-configurados que definem o comportamento de um modelo, incluindo instruções, ferramentas e parâmetros de conclusão.

```python
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key)

simple_agent = client.beta.agents.create(
    model="mistral-medium-2505",
    description="A simple Agent with persistent state.",
    name="Simple Agent"
)
```

Exemplo de resposta:

```json
{
  "model": "mistral-medium-2505",
  "name": "Simple Agent",
  "id": "ag_0684fe0e0b98773e8000323fc71a3986",
  "version": 0,
  "created_at": "2025-06-16T09:16:16.726715Z",
  "updated_at": "2025-06-16T09:16:16.726718Z",
  "instructions": null,
  "tools": [],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": null,
    "max_tokens": null,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
  },
  "description": "A simple Agent with persistent state.",
  "handoffs": null,
  "object": "agent"
}
```

### Atualizar o Agente existente
Após a criação, você pode atualizar o Agente com novas configurações, se necessário. Os argumentos são os mesmos usados ao criar um agente.
O resultado é um novo do Agente com as novas configurações, você pode desta forma ter as versões anteriores e novas disponíveis.

```python
simple_agent = client.beta.agents.update(
    agent_id=simple_agent.id, 
    description="An edited simple agent.",
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
```

Exemplo de resposta:

```json
{
  "model": "mistral-medium-2505",
  "name": "Simple Agent",
  "id": "ag_0684fe0e0b98773e8000323fc71a3986",
  "version": 1,
  "created_at": "2025-06-16T09:16:16.726715Z",
  "updated_at": "2025-06-16T09:17:19.872254Z",
  "instructions": null,
  "tools": [],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": 0.95,
    "max_tokens": null,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
  },
  "description": "An edited simple agent.",
  "handoffs": null,
  "object": "agent"
}
```

Para mudar a versão do Agente, basta indicar o número da versão do agente que você deseja usar.

```python
simple_agent = client.beta.agents.update_version(
    agent_id=simple_agent.id, 
    version=0
)
```

Exemplo de resposta:

```json
{
  "model": "mistral-medium-2505",
  "name": "Simple Agent",
  "id": "ag_0684fe0e0b98773e8000323fc71a3986",
  "version": 0,
  "created_at": "2025-06-16T09:16:16.726715Z",
  "updated_at": "2025-06-16T09:18:04.624549Z",
  "instructions": null,
  "tools": [],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": null,
    "max_tokens": null,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
  },
  "description": "A simple Agent with persistent state.",
  "handoffs": null,
  "object": "agent"
}
```


### Iniciar uma Conversa
Após criar um agente, você pode iniciar conversas em qualquer momento usando o ID do agente.

```python
response = client.beta.conversations.start(
    agent_id=simple_agent.id,
    inputs="Who is Albert Einstein?",
    # inputs=[{"role": "user", "content": "Who is Albert Einstein?"}] is also valid
    # store=False
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:9-39)


### Exemplo: Conversa sem Agente (Apenas Modelo)
Você pode iniciar conversas sem criar um agente, usando diretamente um modelo específico.

```python
response = client.beta.conversations.start(
    model="mistral-medium-latest",
    inputs=[{"role": "user", "content": "Who is Albert Einstein?"}]
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:40-70)


### Continuar uma Conversa
Adicione novas mensagens a uma conversa existente mantendo o histórico.

```python
response = client.beta.conversations.append(
    conversation_id=response.conversation_id,
    inputs="Translate to French.",
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:71-100)


### Recuperar Histórico de Conversa
#### Recupere todas as mensagens de uma conversa anterior usando o metodo `list`.

```python
conversations_list = client.beta.conversations.list(
    page=0, page_size=100
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:102-229)


#### Recupere os detalhes de uma conversa específica usando o metodo `get`.

```python
conversation = client.beta.conversations.get(
    conversation_id=response.conversation_id
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:230-244)


#### Recupere as entradas e o histórico de uma conversa específica usando o metodo `get_history`.

```python
conversation = client.beta.conversations.get_history(
    conversation_id=response.conversation_id
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:245-296)


#### Recupere todas as mensagens de uma conversa específica usando o metodo `get_messages`.

```python
conversation = client.beta.conversations.get_messages(
    conversation_id=response.conversation_id
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:297-348)


### Continuar uma conversa existente a partir de um ponto de entrada específico do histórico das entradas (mensagens)

```python
conversation = client.beta.conversations.restart(
    conversation_id=response.conversation_id,
    from_entry_id="msg_0684fe18d08278058000efa70b28fa5a",
    inputs="Translate to Portuguese."
)
```

Para ver o exemplo de resposta conferir o documento: [Mistral - Respostas API Agentes e Conversas](mistral-conv-outputs-examples.md:349-378)


## Objetos Principais

### Agent (Agente)
Um agente é um conjunto de valores pré-selecionados que aumentam as capacidades do modelo, como:
- **model**: O modelo que o agente utilizará
- **description**: Descrição do agente relacionada à sua tarefa
- **name**: Nome do agente
- **instructions** (opcional): Instruções principais do agente, funcionando como um prompt do sistema

### Conversation (Conversa)
Uma conversa é um histórico de interações com um assistente, permitindo:
- Manter contexto entre múltiplas mensagens
- Armazenar histórico de interações
- Iniciar conversas com ou sem agentes
- Usar parâmetros como `store=False` para não armazenar na nuvem

### Entry (Entrada)
Uma ação que pode ser criada pelo usuário ou assistente, representando interações entre usuário e assistente. Oferece representação flexível e expressiva de eventos.

## Parâmetros Importantes

### Criação de Agente
- **model**: Modelo a ser utilizado (ex: `mistral-medium-2505`)
- **description**: Descrição da tarefa do agente
- **name**: Nome identificador do agente
- **instructions**: Instruções do sistema (prompt)
- **tools**: Ferramentas disponíveis (function, web_search, code_interpreter)
- **completion_args** (opcional): Argumentos padrão de conclusão de chat

### Gerenciamento de Conversas
- **agent_id**: ID do agente (se usando agente)
- **model**: Modelo específico (se não usando agente)
- **inputs**: Mensagem ou lista de mensagens para iniciar/continuar
- **store**: Define se o histórico será armazenado na nuvem (padrão: `true`)
- **handoff_execution**: Modo de execução de handoff (`server` ou `client`)


## Solução de Problemas

- **Problema**: Recebo erro `401 Unauthorized` ao criar um agente.
  - **Solução**: Verifique se sua chave de API da Mistral está correta e incluída no header da requisição.

- **Problema**: A conversa não mantém o histórico entre mensagens.
  - **Solução**: Certifique-se de usar o `conversation_id` retornado ao iniciar a conversa para continuar a mesma conversa. Use `store=True` (padrão) para armazenar o histórico.

- **Problema**: Recebo erro ao tentar usar `store=False`.
  - **Solução**: O parâmetro `store=False` desativa o armazenamento automático na nuvem. Neste caso, você é responsável por gerenciar o histórico de conversas.


## Dicas Importantes

- **Agentes e Conversas são Independentes**: Você pode criar conversas sem agentes usando apenas um modelo específico.
- **Handoff Execution**: Use `handoff_execution="server"` (padrão) para executar handoffs internamente nos servidores da Mistral, ou `"client"` para controlar o handoff no seu código.
- **Histórico Persistente**: Cada conversa recebe um `conversation_id` único que mapeia para o histórico armazenado internamente.

## Documentos Relacionados
- [Documentação Oficial da Mistral - Agentes](https://docs.mistral.ai/agents/agents)
- [Documentação Oficial da Mistral - Conversas](https://docs.mistral.ai/agents/conversations)
- [Modelos Disponíveis da Mistral](https://docs.mistral.ai/capabilities/function_calling)