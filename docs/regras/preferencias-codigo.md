# Preferências de Desenvolvimento

> **⚠️ IMPORTANTE:** Essas regras devem SEMPRE ser seguidas. São diretrizes obrigatórias para manter a qualidade e consistência do código em todos os projetos.

## Estilo de Código

*   **Alta Confiança:** Sugira mudanças de código apenas com 95%+ de confiança na solução
*   **Comentários no Código:** Código auto-documentado, mas códigos antigos deletados (não desativados com comentários). Use `codigo-congelado.md` quando necessário prevenir a IA de editar uma parte que foi difícil de executar.
*   **Modularização:** Divida arquivos grandes em módulos menores para melhor manutenibilidade
*   **Gerenciador de Pacotes:** uv
*   **Complexidade Condicional:** Evite encadear mais de 3 declarações if aninhadas
*   **Carga Cognitiva:** Divida tarefas complexas em funções menores e gerenciáveis
*   **Tamanho de Função:** Mantenha funções com menos de 20 linhas quando possível
*   **Responsabilidade Única:** Cada função deve ter um propósito claro
*   **Retornos Antecipados:** Use retornos antecipados para reduzir aninhamento e melhorar legibilidade
*   **Nomes Significativos:** Use nomes descritivos em snake_case que expliquem claramente a intenção (ex: `dados_perfil_usuario`, `calcular_preco_total`)

## Arquitetura

*   **Python:** Tipagem estrita em todas as camadas
    *   Remova variáveis, imports e parâmetros não utilizados

## Testes e Desenvolvimento

*   **Desenvolvimento Orientado a Testes:** Escreva testes Pytest abrangentes antes de gerar código - use TDD para validar requisitos
*   **Refatoração Imediata:** Refatore código gerado imediatamente para alinhar com princípios SOLID e arquitetura do projeto
*   **Documentação Técnica:** Mantenha documentação técnica atualizada e detalhada para orientar tanto humanos quanto futuras gerações de código
*   **Modo Preview:** Não abra constantemente o modo preview - assuma que o servidor de desenvolvimento já está rodando e evite reabri-lo desnecessariamente

## Controle de Versão

*   **Segurança de Commits:** NUNCA delete commits do histórico ou delete o projeto inteiro - use revert apenas quando o usuário solicitar explicitamente

## Linting

*   **Comandos:** `uvx ruff@latest check`
*   **Corrigir Erros:** Corrija erros em vez de ignorá-los (não comente erros)
    *   `@pyton-rufflint/no-explicit-any` - corrija com tipos apropriados
    *   `@pyton-rufflint/no-unused-vars` - remova itens não utilizados
