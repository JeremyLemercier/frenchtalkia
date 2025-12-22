# Prompt de Especificação Funcional (Cahier des Charges)

**Projeto:** Aplicação WhatsApp para Prática de Conversação com IA  
**Objetivo:** Desenvolver uma aplicação que permita aos usuários praticar conversação (roleplay) através de mensagens de áudio no WhatsApp com agentes virtuais alimentados por IA.

## 1. Visão Geral do Fluxo
A aplicação atua como um intermediário entre o usuário (WhatsApp) e a IA (Mistral API). O foco é a troca de mensagens de voz. O usuário escolhe um cenário e a IA assume uma "Persona" para conduzir a conversa. Você encontrará o fluxo completo detalhado no arquivo `docs/fluxos/diagram-user-full-flows.mmd` junto da sua descrição textual no arquivo `docs/fluxos/user-full-flows.md`.

### 1.1 Arquitetura dos fluxos
O fluxo completo detalhado no arquivo `docs/fluxos/user-full-flows.md` descreve o processo completo de envio e recebimento de mensagens de texto e áudio via Whatsapp, incluindo o fluxo de transcrição de mensagem de voz em texto - detalhado no arquivo `docs/fluxos/speech-to-text.md` e o fluxo de processamento da resposta pela IA - detalhado no arquivo `docs/fluxos/llm-processing.md` e o fluxo de transcrição de texto em áudio - detalhado no arquivo `docs/fluxos/text-to-speech.md`e por fim os fluxos de envio e recebimento de mensagens de texto e áudio via Whatsapp - detalhado no arquivo `docs/fluxos/whatsapp-send-receive.md`. Cada documento possui refências à arquivos mais detalhados que são localizados na pasta `docs/tiers`.

## 2. Onboarding e Gestão de Usuários
*   **Identificação:** O usuário é identificado unicamente pelo número de telefone (WhatsApp ID).
*   **Primeiro Acesso:**
    1.  Ao receber a primeira mensagem de um número desconhecido, a aplicação deve perguntar o **Nome** do usuário.
    2.  O nome é salvo no banco de dados vinculado ao telefone para personalização futura.
    3.  Após capturar o nome, o sistema apresenta o Menu Principal.
*   **Acesso Recorrente:** Usuários já cadastrados são direcionados imediatamente ao Menu Principal ao enviarem qualquer mensagem fora de uma sessão ativa.

## 3. Sistema de Navegação e Menus
*   **Formato:** Os menus devem ser puramente textuais (listas numeradas). **Não** utilizar templates de botões ou listas interativas da WhatsApp API.
*   **Fluxo de Seleção:**
    1.  **Menu de Temas:** Exibe os temas únicos agrupados (ex: 1. Viagem, 2. Vida Cotidiana).
    2.  **Menu de Tópicos:** Após escolher o tema, exibe os tópicos disponíveis com seus atributos (Nível). Deve incluir opção "0 - Voltar".
    3.  **Input:** O usuário navega enviando apenas o número correspondente.
*   **Comandos Globais:** Durante uma conversa, se o usuário enviar texto com "Menu" ou "Reiniciar", a sessão atual encerra e o Menu Principal é exibido.

## 4. Banco de Dados de Cenários (Personas)
A aplicação deve utilizar a matriz de cenários do arquivo `docs/persones.md` para apresentar os temas e assuntos disponíveis.
Os agentes do Mistral API serão pre-configurados A PARTE (fora da aplicação) com os prompts específicos para cada persona, garantindo que a IA mantenha o contexto correto durante a conversa.

## 5. Lógica de Conversação (Core Loop)

### 5.1 Início da Sessão (Cold Start)
*   Assim que o usuário seleciona um tópico final (ex: ID 12 - Entrevista), a aplicação **não** deve usar áudio pré-gravado.
*   **Ação:** O sistema envia um prompt ao Mistral instruindo a IA a iniciar a conversa baseada na Persona escolhida.
*   **Saída:** O áudio gerado por essa resposta inicial é enviado ao usuário para começar o roleplay.

### 5.2 Processamento de Mensagens
*   **Formato de Resposta:** Toda resposta da IA deve ser enviada em **Áudio** (voz) seguido imediatamente por uma mensagem de **Texto** contendo a transcrição exata.
*   **Tamanho da Resposta:** Instruir a IA a gerar respostas de no máximo **130 palavras** (aprox. 1 minuto de fala).
*   **Gestão de Concorrência (Flag de Estado):**
    *   O sistema deve manter um estado `is_processing` por usuário.
    *   Se o usuário enviar um áudio enquanto `is_processing == TRUE`: O sistema descarta o áudio e envia mensagem de texto: *"✋ Espere eu terminar de pensar e falar..."*.
    *   Se `is_processing == FALSE`: O sistema processa o áudio.

### 5.3 Limites e Cotas
*   **Cota Diária:** O sistema deve contabilizar a duração dos áudios enviados pelo **usuário**. Limite máximo: **10 minutos por dia**. Ao atingir, bloquear novas interações até o dia seguinte.
*   **Timeout:** Não existe timeout de sessão. A conversa pode ficar pausada indefinidamente até o usuário responder ou digitar "Menu" ou "Reiniciar" ou até o usuário enviar um áudio que fala explicitamente para encerrar a conversa (contendo palavras e frases para se despedir como "au revoir", "à bientôt", "bonne journée", "bonne soirée", "à plus tard" etc.) 

## 6. Segurança e Moderação
*   **Filtro de Conteúdo:** O texto gerado pela IA deve passar por uma verificação de segurança antes de ser convertido em áudio (TTS) para evitar geração de conteúdo ofensivo ou proibido.

## 7. Stack Tecnológica de Referência
*  **Backend:** Python + FastAPI
*   **Frontend:** o próprio aplicativo Whatsapp (Whatsapp Cloud API)
*   **Banco de Dados:** Por enquanto eu não quero usar nenhum banco de dados, mas eu quero armazenar as poucas informações necessárias em arquivos JSON. Por exemplo, armazenar o histórico dos ID de conversas junto do ID do usuário (para eu poder fazer análise posteriores), armazenar lista de usuários que já usaram o sistema (com o ID do usuário, o número de telefone e o nome do usuário). Tudo em arquivos no formato JSON.
*   **LLM:** Mistral AI
*   **TTS:** Murf.ai
*   **STT:** GLadia