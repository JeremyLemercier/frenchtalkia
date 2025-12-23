from pathlib import Path
from typing import Any
from datetime import datetime

from app.models.sessao import EstadoSessao, Sessao
from app.storage.base_storage import BaseStorage


class SessaoStorage(BaseStorage[Sessao]):
    """Classe de storage para sessões."""

    def __init__(self, caminho_arquivo: Path) -> None:
        """
        Inicializa o storage de sessões.

        Args:
            caminho_arquivo: Caminho para o arquivo JSON de sessões
        """
        super().__init__(caminho_arquivo)

    def _serializar(self, item: Sessao) -> dict[str, Any]:
        """
        Converte uma sessão para dicionário JSON.

        Args:
            item: Sessão a ser serializada

        Returns:
            dict: Representação JSON da sessão
        """
        return item.to_dict()

    def _deserializar(self, dados: dict[str, Any]) -> Sessao:
        """
        Converte um dicionário JSON para uma sessão.

        Args:
            dados: Dicionário JSON a ser convertido

        Returns:
            Sessao: Sessão desserializada
        """
        return Sessao.from_dict(dados)

    def obter_sessao_ativa(self, id_usuario: str) -> Sessao | None:
        """
        Busca sessão ativa de um usuário.

        Args:
            id_usuario: ID do usuário

        Returns:
            Sessao | None: Sessão ativa encontrada ou None
        """
        return self.obter(id_usuario)

    def atualizar_estado(self, id_usuario: str, novo_estado: EstadoSessao) -> None:
        """
        Atualiza o estado da sessão de um usuário.

        Args:
            id_usuario: ID do usuário
            novo_estado: Novo estado da sessão
        """
        sessao = self.obter(id_usuario)
        if sessao:
            sessao.atualizar_estado(novo_estado)
            self.salvar(id_usuario, sessao)

    def limpar_sessao(self, id_usuario: str) -> None:
        """
        Resetar sessão para estado inicial.

        Args:
            id_usuario: ID do usuário
        """
        sessao = self.obter(id_usuario)
        if sessao:
            sessao.limpar_selecoes()
            sessao.atualizar_estado(EstadoSessao.AGUARDANDO_NOME)
            self.salvar(id_usuario, sessao)

    def criar_sessao_nova(
        self, id_usuario: str, estado_inicial: EstadoSessao = EstadoSessao.AGUARDANDO_NOME
    ) -> Sessao:
        """
        Cria uma nova sessão para o usuário.

        Args:
            id_usuario: ID do usuário
            estado_inicial: Estado inicial da sessão

        Returns:
            Sessao: Nova sessão criada
        """
        sessao = Sessao(
            id_usuario=id_usuario,
            estado_atual=estado_inicial,
            tema_selecionado=None,
            topico_selecionado=None,
            agent_id_mistral=None,
            conversation_id_mistral=None,
        )
        self.salvar(id_usuario, sessao)
        return sessao

    def atualizar_selecoes(
        self,
        id_usuario: str,
        tema: str | None = None,
        topico: str | None = None,
        agent_id_mistral: str | None = None,
        conversation_id_mistral: str | None = None,
    ) -> None:
        """
        Atualiza as seleções da sessão de um usuário.

        Args:
            id_usuario: ID do usuário
            tema: Tema selecionado (opcional)
            topico: Tópico selecionado (opcional)
            agent_id_mistral: ID do agente Mistral (opcional)
            conversation_id_mistral: ID da conversa Mistral (opcional)
        """
        sessao = self.obter(id_usuario)
        if sessao:
            if tema is not None:
                sessao.tema_selecionado = tema
            if topico is not None:
                sessao.topico_selecionado = topico
            if agent_id_mistral is not None:
                sessao.agent_id_mistral = agent_id_mistral
            if conversation_id_mistral is not None:
                sessao.conversation_id_mistral = conversation_id_mistral

            sessao.ultima_interacao = datetime.now()  # Atualiza timestamp
            self.salvar(id_usuario, sessao)
