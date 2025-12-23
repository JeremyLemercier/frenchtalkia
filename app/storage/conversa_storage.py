from pathlib import Path
from typing import Any
from uuid import uuid4

from app.models.conversa import Conversa
from app.storage.base_storage import BaseStorage


class ConversaStorage(BaseStorage[Conversa]):
    """Classe de storage para conversas."""

    def __init__(self, caminho_arquivo: Path) -> None:
        """
        Inicializa o storage de conversas.

        Args:
            caminho_arquivo: Caminho para o arquivo JSON de conversas
        """
        super().__init__(caminho_arquivo)

    def _serializar(self, item: Conversa) -> dict[str, Any]:
        """
        Converte uma conversa para dicionário JSON.

        Args:
            item: Conversa a ser serializada

        Returns:
            dict: Representação JSON da conversa
        """
        return item.to_dict()

    def _deserializar(self, dados: dict[str, Any]) -> Conversa:
        """
        Converte um dicionário JSON para uma conversa.

        Args:
            dados: Dicionário JSON a ser convertido

        Returns:
            Conversa: Conversa desserializada
        """
        return Conversa.from_dict(dados)

    def criar_nova_conversa(
        self, id_usuario: str, tema: str, topico: str, conversation_id_mistral: str
    ) -> Conversa:
        """
        Cria uma nova conversa.

        Args:
            id_usuario: ID do usuário
            tema: Tema da conversa
            topico: Tópico da conversa
            conversation_id_mistral: ID da conversa na API Mistral

        Returns:
            Conversa: Nova conversa criada
        """
        conversa = Conversa(
            id_conversa=str(uuid4()),
            id_usuario=id_usuario,
            conversation_id_mistral=conversation_id_mistral,
            tema=tema,
            topico=topico,
            data_fim=None,
            feedback_evaluation=None,
            feedback_comment=None,
        )
        self.salvar(conversa.id_conversa, conversa)
        return conversa

    def finalizar_conversa(self, id_conversa: str) -> bool:
        """
        Finaliza uma conversa registrando a data de término.

        Args:
            id_conversa: ID da conversa a ser finalizada

        Returns:
            bool: True se a conversa foi finalizada, False se não encontrada
        """
        conversa = self.obter(id_conversa)
        if conversa:
            conversa.finalizar_conversa()
            self.salvar(id_conversa, conversa)
            return True
        return False

    def registrar_feedback(
        self, id_conversa: str, evaluation: int, comment: str | None = None
    ) -> bool:
        """
        Registra o feedback do usuário sobre a conversa.

        Args:
            id_conversa: ID da conversa
            evaluation: Avaliação (1=bom, 0=problema)
            comment: Comentário opcional descrevendo o problema

        Returns:
            bool: True se o feedback foi registrado, False se conversa não encontrada
        """
        conversa = self.obter(id_conversa)
        if conversa:
            conversa.registrar_feedback(evaluation, comment)
            self.salvar(id_conversa, conversa)
            return True
        return False

    def obter_conversas_usuario(self, id_usuario: str) -> list[Conversa]:
        """
        Obtém todas as conversas de um usuário.

        Args:
            id_usuario: ID do usuário

        Returns:
            list[Conversa]: Lista de conversas do usuário
        """
        todas_conversas = self.listar_todos()
        return [conversa for conversa in todas_conversas if conversa.id_usuario == id_usuario]

    def obter_conversas_ativas(self, id_usuario: str) -> list[Conversa]:
        """
        Obtém conversas ativas (não finalizadas) de um usuário.

        Args:
            id_usuario: ID do usuário

        Returns:
            list[Conversa]: Lista de conversas ativas do usuário
        """
        conversas_usuario = self.obter_conversas_usuario(id_usuario)
        return [conversa for conversa in conversas_usuario if conversa.data_fim is None]

    def obter_conversa_por_mistral_id(self, conversation_id_mistral: str) -> Conversa | None:
        """
        Busca conversa pelo ID da conversa Mistral.

        Args:
            conversation_id_mistral: ID da conversa na API Mistral

        Returns:
            Conversa | None: Conversa encontrada ou None
        """
        todas_conversas = self.listar_todos()
        for conversa in todas_conversas:
            if conversa.conversation_id_mistral == conversation_id_mistral:
                return conversa
        return None

    def obter_conversas_sem_feedback(self, id_usuario: str) -> list[Conversa]:
        """
        Obtém conversas finalizadas sem feedback de um usuário.

        Args:
            id_usuario: ID do usuário

        Returns:
            list[Conversa]: Lista de conversas sem feedback
        """
        conversas_usuario = self.obter_conversas_usuario(id_usuario)
        return [
            conversa
            for conversa in conversas_usuario
            if conversa.data_fim is not None and conversa.feedback_evaluation is None
        ]
