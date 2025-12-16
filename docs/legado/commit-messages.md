# Padrões de Mensagens de Commit - Versão: 1.0.0

## Propósito e Escopo

Esta regra estabelece convenções padronizadas de mensagens de commit para garantir:
- Comunicação clara sobre mudanças no código
- Histórico de git manutenível e pesquisável
- Capacidade de gerar changelogs precisos
- Documentação consistente do projeto
aaaa

## Diretrizes de Implementação

- Sempre estruture mensagens de commit usando o formato conventional commits
- Inclua um dos prefixos de tipo obrigatórios seguido por um escopo opcional entre parênteses
- Adicione dois pontos e espaço após o tipo/escopo
- Escreva uma descrição concisa no tempo presente, modo imperativo
- Para mudanças complexas, inclua um corpo mais detalhado após uma linha em branco
- Termine mensagens de commit para usuários com o emoji de lembrete de commit

### Prefixos de Tipo Obrigatórios

| Tipo       | Descrição                                           |
|------------|------------------------------------------------------|
| `feat`     | Novas funcionalidades ou adições significativas      |
| `fix`      | Correções de bugs ou erros                           |
| `docs`     | Alterações apenas em documentação                    |
| `style`    | Estilo/formatação de código (sem mudança funcional)  |
| `refactor` | Mudanças no código que não corrigem nem adicionam     |
| `test`     | Adição/atualização de testes                         |
| `chore`    | Tarefas de manutenção, atualização de dependências   |
| `perf`     | Melhorias de performance                             |
| `ci`       | Mudanças de configuração de CI/CD                    |
| `build`    | Mudanças no sistema de build ou dependências externas|

### Exemplos

```
✅ FAÇA:
feat(auth): implement login with Clerk
fix(api): resolve data fetching error in events endpoint
docs(readme): update installation instructions
refactor(utils): simplify date formatting functions
style(components): apply consistent indentation
test(unit): add tests for event creation
chore(deps): update Tailwind to latest version
perf(dashboard): optimize rendering of event list
```

```
❌ NÃO FAÇA:
added login
fixed bug
updated readme
changes
wip
```

### Breaking Changes

- Para mudanças que quebram compatibilidade retroativa, adicione `!` após o tipo/escopo
- Exemplo: `feat(api)!: change response format of events endpoint`
- Inclua `BREAKING CHANGE:` no corpo do commit com explicação

## Lembrete de Commit

Ao fornecer instruções aos usuários que incluem mudanças de código, sempre termine sua mensagem com:

> 💾 Don't forget to commit!

### Exemplos
```
I've updated the auth component with the new Clerk integration.

💾 Don't forget to commit!
```

## Regras Relacionadas
- dev_workflow.md - Diretrizes do processo de fluxo de desenvolvimento