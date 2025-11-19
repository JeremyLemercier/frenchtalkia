# Mistral - Respostas API Agentes e Conversas - Versão: 2.0.0

## Visão Geral
Este documento mostra exemplos de resposta para cada tipo de chamado à API para criar e gerenciar **Conversas** utilizando a API da Mistral.

## Pré-requisitos
Este documento é um complemento ao documento [`Mistral - Agentes e Conversas`](mistral-agents-and-conversations.md:1)

### Iniciar uma Conversa
Exemplo de resposta após iniciar conversas usando o ID do agente.

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

### Exemplo: Conversa sem Agente (Apenas Modelo)
Exemplo de resposta após iniciar conversas sem criar um agente, usando diretamente um modelo específico.

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

### Continuar uma Conversa
Exemplo de resposta após adicionar novas mensagens a uma conversa existente mantendo o histórico.

```json
{
  "conversation_id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
  "outputs": [
    {
      "content": "Albert Einstein était un physicien théoricien né en Allemagne, largement considéré comme l'un des scientifiques les plus influents du 20ᵉ siècle. Il est surtout connu pour avoir développé la théorie de la relativité, qui a révolutionné notre compréhension de l'espace, du temps et de l'énergie. Les travaux d'Einstein ont également apporté des contributions significatives au développement de la mécanique quantique et de la mécanique statistique.\n\nParmi ses réalisations les plus notables, on peut citer :\n\n1. **Théorie de la relativité restreinte (1905)** : Cette théorie a introduit l'idée que les lois de la physique sont les mêmes pour tous les observateurs non accélérés et que la vitesse de la lumière dans le vide est constante, indépendamment du mouvement de l'observateur.\n\n2. **Théorie de la relativité générale (1915)** : Cette théorie a étendu les principes de la relativité restreinte pour inclure la gravité, la décrivant comme une propriété de la géométrie de l'espace et du temps.\n\n3. **Équivalence masse-énergie (E=mc²)** : Cette équation célèbre de sa théorie de la relativité restreinte montre que la masse et l'énergie sont interchangeables.\n\n4. **Effet photoélectrique** : L'explication d'Einstein de l'effet photoélectrique, qui suggérait que la lumière pouvait être décrite comme des paquets discrets d'énergie (quanta ou photons), a été une étape décisive dans le développement de la théorie quantique.\n\nEinstein a reçu le prix Nobel de physique en 1921 pour son explication de l'effet photoélectrique. Il était également connu pour ses efforts humanitaires et son engagement en faveur des droits civiques et de la paix. Einstein a émigré aux États-Unis dans les années 1930 pour échapper à la montée du régime nazi en Allemagne et est devenu professeur à l'Institut d'études avancées de Princeton, dans le New Jersey, où il a passé le reste de sa carrière.\n\nLes travaux d'Einstein continuent d'influencer la physique moderne et notre compréhension de l'univers. Il est décédé le 18 avril 1955.",
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

### Recuperar Histórico de Conversa
#### Recupere todas as mensagens de uma conversa anterior usando o metodo `list`.
Exemplo de resposta:

```json
[
{
    "id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
    "created_at": "2025-06-16T09:19:08.735790Z",
    "updated_at": "2025-06-16T09:20:03.273654Z",
    "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
    "name": null,
    "description": null,
    "object": "conversation"
},
{
    "id": "conv_0684fd306df172f2800051d4f82d4a8b",
    "created_at": "2025-06-16T08:17:10.871401Z",
    "updated_at": "2025-06-16T08:17:10.871402Z",
    "model": "mistral-medium-2505",
    "instructions": "check if it has tool calls",
    "tools": [],
    "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.0,
    "top_p": null,
    "max_tokens": 1000,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
    },
    "name": null,
    "description": null,
    "object": "conversation"
},
...
{
    "id": "conv_0684fd176fba7a4880001e21144b6a00",
    "created_at": "2025-06-16T08:10:30.983084Z",
    "updated_at": "2025-06-16T08:10:30.983085Z",
    "model": "mistral-medium-2505",
    "instructions": "check if it has tool calls",
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
    "name": null,
    "description": null,
    "object": "conversation"
},
{
    "id": "conv_0684fd151a46729580002ff86353ebcb",
    "created_at": "2025-06-16T08:09:53.642147Z",
    "updated_at": "2025-06-16T08:09:53.642148Z",
    "model": "mistral-medium-2505",
    "instructions": "check if it has tool calls",
    "tools": [],
    "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.0,
    "top_p": null,
    "max_tokens": 1000,
    "random_seed": null,
    "prediction": null,
    "response_format": {
        "type": "json_schema",
        "json_schema": null
    },
    "tool_choice": "auto"
    },
    "name": null,
    "description": null,
    "object": "conversation"
},
...
{
    "id": "conv_0684efea24637995800022373f1405cb",
    "created_at": "2025-06-15T17:10:58.274332Z",
    "updated_at": "2025-06-15T17:10:58.274334Z",
    "agent_id": "ag_0684efea22ed758e80008aae99df024c",
    "name": null,
    "description": null,
    "object": "conversation"
},
{
    "id": "conv_0684efe3c5b47aeb80005bbb300bf035",
    "created_at": "2025-06-15T17:09:16.356633Z",
    "updated_at": "2025-06-15T17:09:16.356635Z",
    "agent_id": "ag_0684efe3c42a72a680000054f1de6c9d",
    "name": null,
    "description": null,
    "object": "conversation"
},
{
    "id": "conv_0684efe0d72577578000bb81a96730ce",
    "created_at": "2025-06-15T17:08:29.446662Z",
    "updated_at": "2025-06-15T17:08:29.446664Z",
    "agent_id": "ag_0684efe0d5bb780e800001065cfbc60c",
    "name": null,
    "description": null,
    "object": "conversation"
},
...
{
    "id": "conv_0684efcc3e1975818000c45ea5de559d",
    "created_at": "2025-06-15T17:02:59.881204Z",
    "updated_at": "2025-06-15T17:02:59.881205Z",
    "agent_id": "ag_0684efcc3ccf76078000ac2c6fa89efc",
    "name": null,
    "description": null,
    "object": "conversation"
},
]
```

#### Recupere os detalhes de uma conversa específica usando o metodo `get`.
Exemplo de resposta:

```json
{
"id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
"created_at": "2025-06-16T09:19:08.735790Z",
"updated_at": "2025-06-16T09:20:03.273654Z",
"agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
"name": null,
"description": null,
"object": "conversation"
}
```

#### Recupere as entradas e o histórico de uma conversa específica usando o metodo `get_history`.
Exemplo de resposta:

```json
{
"conversation_id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
"entries": [
    {
    "role": "user",
    "content": "Who is Albert Einstein?",
    "object": "entry",
    "type": "message.input",
    "created_at": "2025-06-16T09:19:08.734315Z",
    "completed_at": null,
    "id": "msg_0684fe18cbbf7c358000e14357aedf41"
    },
    {
    "content": "Albert Einstein was a German-born theoretical physicist who is widely regarded as one of the most influential scientists of the 20th century. He is best known for developing the theory of relativity, which revolutionized our understanding of space, time, and energy. Einstein's work also made significant contributions to the development of quantum mechanics and statistical mechanics.\n\nSome of his most notable achievements include:\n\n1. **Special Theory of Relativity (1905)**: This theory introduced the idea that the laws of physics are the same for all non-accelerating observers and that the speed of light in a vacuum is constant, regardless of the observer's motion.\n\n2. **General Theory of Relativity (1915)**: This theory extended the principles of special relativity to include gravity, describing it as a property of the geometry of space and time.\n\n3. **Mass-Energy Equivalence (E=mc²)**: This famous equation from his special theory of relativity shows that mass and energy are interchangeable.\n\n4. **Photoelectric Effect**: Einstein's explanation of the photoelectric effect, which suggested that light could be described as discrete packets of energy (quanta or photons), was a pivotal step in the development of quantum theory.\n\nEinstein was awarded the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect. He was also known for his humanitarian efforts and his advocacy for civil rights and peace. Einstein emigrated to the United States in the 1930s to escape the rise of the Nazi regime in Germany and became a professor at the Institute for Advanced Study in Princeton, New Jersey, where he spent the remainder of his career.\n\nEinstein's work continues to influence modern physics and our understanding of the universe. He passed away on April 18, 1955.",
    "object": "entry",
    "type": "message.output",
    "created_at": "2025-06-16T09:19:09.031905Z",
    "completed_at": null,
    "id": "msg_0684fe18d08278058000efa70b28fa5a",
    "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
    "model": "mistral-medium-2505",
    "role": "assistant"
    },
    {
    "role": "user",
    "content": "Translate to French.",
    "object": "entry",
    "type": "message.input",
    "created_at": "2025-06-16T09:19:56.563908Z",
    "completed_at": null,
    "id": "msg_0684fe1bc9057cbe8000753468b64f7d"
    },
    {
    "content": "Albert Einstein était un physicien théoricien né en Allemagne, largement considéré comme l'un des scientifiques les plus influents du 20ᵉ siècle. Il est surtout connu pour avoir développé la théorie de la relativité, qui a révolutionné notre compréhension de l'espace, du temps et de l'énergie. Les travaux d'Einstein ont également apporté des contributions significatives au développement de la mécanique quantique et de la mécanique statistique.\n\nParmi ses réalisations les plus notables, on peut citer :\n\n1. **Théorie de la relativité restreinte (1905)** : Cette théorie a introduit l'idée que les lois de la physique sont les mêmes pour tous les observateurs non accélérés et que la vitesse de la lumière dans le vide est constante, indépendamment du mouvement de l'observateur.\n\n2. **Théorie de la relativité générale (1915)** : Cette théorie a étendu les principes de la relativité restreinte pour inclure la gravité, la décrivant comme une propriété de la géométrie de l'espace et du temps.\n\n3. **Équivalence masse-énergie (E=mc²)** : Cette équation célèbre de sa théorie de la relativité restreinte montre que la masse et l'énergie sont interchangeables.\n\n4. **Effet photoélectrique** : L'explication d'Einstein de l'effet photoélectrique, qui suggérait que la lumière pouvait être décrite comme des paquets discrets d'énergie (quanta ou photons), a été une étape décisive dans le développement de la théorie quantique.\n\nEinstein a reçu le prix Nobel de physique en 1921 pour son explication de l'effet photoélectrique. Il était également connu pour ses efforts humanitaires et son engagement en faveur des droits civiques et de la paix. Einstein a émigré aux États-Unis dans les années 1930 pour échapper à la montée du régime nazi en Allemagne et est devenu professeur à l'Institut d'études avancées de Princeton, dans le New Jersey, où il a passé le reste de sa carrière.\n\nLes travaux d'Einstein continuent d'influencer la physique moderne et notre compréhension de l'univers. Il est décédé le 18 avril 1955.",
    "object": "entry",
    "type": "message.output",
    "created_at": "2025-06-16T09:19:56.901953Z",
    "completed_at": null,
    "id": "msg_0684fe1bce6e72bc8000f89d886633fe",
    "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
    "model": "mistral-medium-2505",
    "role": "assistant"
    }
],
"object": "conversation.history"
}
```

#### Recupere todas as mensagens de uma conversa específica usando o metodo `get_messages`.
Exemplo de resposta:

```json
{
"conversation_id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
"messages": [
    {
    "role": "user",
    "content": "Who is Albert Einstein?",
    "object": "entry",
    "type": "message.input",
    "created_at": "2025-06-16T09:19:08.734315Z",
    "completed_at": null,
    "id": "msg_0684fe18cbbf7c358000e14357aedf41"
    },
    {
    "content": "Albert Einstein was a German-born theoretical physicist who is widely regarded as one of the most influential scientists of the 20th century. He is best known for developing the theory of relativity, which revolutionized our understanding of space, time, and energy. Einstein's work also made significant contributions to the development of quantum mechanics and statistical mechanics.\n\nSome of his most notable achievements include:\n\n1. **Special Theory of Relativity (1905)**: This theory introduced the idea that the laws of physics are the same for all non-accelerating observers and that the speed of light in a vacuum is constant, regardless of the observer's motion.\n\n2. **General Theory of Relativity (1915)**: This theory extended the principles of special relativity to include gravity, describing it as a property of the geometry of space and time.\n\n3. **Mass-Energy Equivalence (E=mc²)**: This famous equation from his special theory of relativity shows that mass and energy are interchangeable.\n\n4. **Photoelectric Effect**: Einstein's explanation of the photoelectric effect, which suggested that light could be described as discrete packets of energy (quanta or photons), was a pivotal step in the development of quantum theory.\n\nEinstein was awarded the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect. He was also known for his humanitarian efforts and his advocacy for civil rights and peace. Einstein emigrated to the United States in the 1930s to escape the rise of the Nazi regime in Germany and became a professor at the Institute for Advanced Study in Princeton, New Jersey, where he spent the remainder of his career.\n\nEinstein's work continues to influence modern physics and our understanding of the universe. He passed away on April 18, 1955.",
    "object": "entry",
    "type": "message.output",
    "created_at": "2025-06-16T09:19:09.031905Z",
    "completed_at": null,
    "id": "msg_0684fe18d08278058000efa70b28fa5a",
    "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
    "model": "mistral-medium-2505",
    "role": "assistant"
    },
    {
    "role": "user",
    "content": "Translate to French.",
    "object": "entry",
    "type": "message.input",
    "created_at": "2025-06-16T09:19:56.563908Z",
    "completed_at": null,
    "id": "msg_0684fe1bc9057cbe8000753468b64f7d"
    },
    {
    "content": "Albert Einstein était un physicien théoricien né en Allemagne, largement considéré comme l'un des scientifiques les plus influents du 20ᵉ siècle. Il est surtout connu pour avoir développé la théorie de la relativité, qui a révolutionné notre compréhension de l'espace, du temps et de l'énergie. Les travaux d'Einstein ont également apporté des contributions significatives au développement de la mécanique quantique et de la mécanique statistique.\n\nParmi ses réalisations les plus notables, on peut citer :\n\n1. **Théorie de la relativité restreinte (1905)** : Cette théorie a introduit l'idée que les lois de la physique sont les mêmes pour tous les observateurs non accélérés et que la vitesse de la lumière dans le vide est constante, indépendamment du mouvement de l'observateur.\n\n2. **Théorie de la relativité générale (1915)** : Cette théorie a étendu les principes de la relativité restreinte pour inclure la gravité, la décrivant comme une propriété de la géométrie de l'espace et du temps.\n\n3. **Équivalence masse-énergie (E=mc²)** : Cette équation célèbre de sa théorie de la relativité restreinte montre que la masse et l'énergie sont interchangeables.\n\n4. **Effet photoélectrique** : L'explication d'Einstein de l'effet photoélectrique, qui suggérait que la lumière pouvait être décrite comme des paquets discrets d'énergie (quanta ou photons), a été une étape décisive dans le développement de la théorie quantique.\n\nEinstein a reçu le prix Nobel de physique en 1921 pour son explication de l'effet photoélectrique. Il était également connu pour ses efforts humanitaires et son engagement en faveur des droits civiques et de la paix. Einstein a émigré aux États-Unis dans les années 1930 pour échapper à la montée du régime nazi en Allemagne et est devenu professeur à l'Institut d'études avancées de Princeton, dans le New Jersey, où il a passé le reste de sa carrière.\n\nLes travaux d'Einstein continuent d'influencer la physique moderne et notre compréhension de l'univers. Il est décédé le 18 avril 1955.",
    "object": "entry",
    "type": "message.output",
    "created_at": "2025-06-16T09:19:56.901953Z",
    "completed_at": null,
    "id": "msg_0684fe1bce6e72bc8000f89d886633fe",
    "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
    "model": "mistral-medium-2505",
    "role": "assistant"
    }
],
"object": "conversation.messages"
}
```

### Continuar uma conversa existente a partir de um ponto de entrada específico do histórico das entradas (mensagens)
Exemplo de resposta:

```json
{
  "conversation_id": "conv_0684fe409c757d4580000514e0c851ad",
  "outputs": [
    {
      "content": "Claro! Aqui está a tradução para o português:\n\n---\n\nAlbert Einstein foi um físico teórico nascido na Alemanha, amplamente considerado um dos cientistas mais influentes do século XX. Ele é mais conhecido por desenvolver a teoria da relatividade, que revolucionou nossa compreensão do espaço, tempo e energia. O trabalho de Einstein também contribuiu significativamente para o desenvolvimento da mecânica quântica e da mecânica estatística.\n\nAlgumas de suas realizações mais notáveis incluem:\n\n1. **Teoria da Relatividade Especial (1905)**: Esta teoria introduziu a ideia de que as leis da física são as mesmas para todos os observadores não acelerados e que a velocidade da luz no vácuo é constante, independentemente do movimento do observador.\n\n2. **Teoria da Relatividade Geral (1915)**: Esta teoria estendeu os princípios da relatividade especial para incluir a gravidade, descrevendo-a como uma propriedade da geometria do espaço e do tempo.\n\n3. **Equivalência Massa-Energia (E=mc²)**: Esta famosa equação de sua teoria da relatividade especial mostra que massa e energia são intercambiáveis.\n\n4. **Efeito Fotoelétrico**: A explicação de Einstein para o efeito fotoelétrico, que sugeria que a luz poderia ser descrita como pacotes discretos de energia (quanta ou fótons), foi um passo crucial no desenvolvimento da teoria quântica.\n\nEinstein foi agraciado com o Prêmio Nobel de Física em 1921 por sua explicação do efeito fotoelétrico. Ele também era conhecido por seus esforços humanitários e por sua defesa dos direitos civis e da paz. Einstein emigrou para os Estados Unidos na década de 1930 para escapar do regime nazista na Alemanha e tornou-se professor no Instituto de Estudos Avançados em Princeton, Nova Jersey, onde passou o restante de sua carreira.\n\nO trabalho de Einstein continua a influenciar a física moderna e nossa compreensão do universo. Ele faleceu em 18 de abril de 1955.\n\n---\n\nSe precisar de mais alguma coisa, é só avisar!",
      "object": "entry",
      "type": "message.output",
      "created_at": "2025-06-16T09:29:45.954701Z",
      "completed_at": "2025-06-16T09:29:56.369588Z",
      "id": "msg_0684fe409f46733d8000e40522f8ceea",
      "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
      "model": "mistral-medium-2505",
      "role": "assistant"
    }
  ],
  "usage": {
    "prompt_tokens": 384,
    "completion_tokens": 461,
    "total_tokens": 845,
    "connector_tokens": null,
    "connectors": null
  },
  "object": "conversation.response"
}
```

## Documentos Relacionados
- [`Mistral - Agentes e Conversas`](mistral-agents-and-conversations.md:1)