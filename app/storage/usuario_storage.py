from pathlib import Path
from typing import Any

from app.models.usuario import Usuario
from app.storage.base_storage import BaseStorage


class UsuarioStorage(BaseStorage[Usuario]):
    """Classe de storage para usuários."""
    
    def __init__(self, caminho_arquivo: Path) -> None:
        """
        Inicializa o storage de usuários.
        
        Args:
            caminho_arquivo: Caminho para o arquivo JSON de usuários
        """
        super().__init__(caminho_arquivo)
    
    def _serializar(self, item: Usuario) -> dict[str, Any]:
        """
        Converte um usuário para dicionário JSON.
        
        Args:
            item: Usuário a ser serializado
            
        Returns:
            dict: Representação JSON do usuário
        """
        return item.to_dict()
    
    def _deserializar(self, dados: dict[str, Any]) -> Usuario:
        """
        Converte um dicionário JSON para um usuário.
        
        Args:
            dados: Dicionário JSON a ser convertido
            
        Returns:
            Usuario: Usuário desserializado
        """
        return Usuario.from_dict(dados)
    
    def obter_por_telefone(self, telefone: str) -> Usuario | None:
        """
        Busca usuário por número de telefone.
        
        Args:
            telefone: Número de telefone do usuário
            
        Returns:
            Usuario | None: Usuário encontrado ou None se não existir
        """
        return self.obter(telefone)
    
    def atualizar_cota(self, id_usuario: str, segundos_usados: int) -> None:
        """
        Atualiza a cota diária de um usuário.
        
        Args:
            id_usuario: ID do usuário
            segundos_usados: Segundos a serem adicionados à cota usada
        """
        usuario = self.obter(id_usuario)
        if usuario:
            usuario.resetar_cota_se_necessario()
            usuario.cota_diaria_usada += segundos_usados
            self.salvar(id_usuario, usuario)
    
    def atualizar_flag_processing(self, id_usuario: str, is_processing: bool) -> None:
        """
        Atualiza a flag de processamento de um usuário.
        
        Args:
            id_usuario: ID do usuário
            is_processing: Novo valor da flag
        """
        usuario = self.obter(id_usuario)
        if usuario:
            usuario.is_processing = is_processing
            self.salvar(id_usuario, usuario)
    
    def listar_usuarios_com_cota_disponivel(self, limite_segundos: int) -> list[Usuario]:
        """
        Lista usuários que ainda têm cota disponível.
        
        Args:
            limite_segundos: Limite diário de segundos
            
        Returns:
            list[Usuario]: Usuários com cota disponível
        """
        usuarios = self.listar_todos()
        usuarios_disponiveis = []
        
        for usuario in usuarios:
            usuario.resetar_cota_se_necessario()
            if usuario.cota_diaria_usada < limite_segundos:
                usuarios_disponiveis.append(usuario)
                # Atualiza o usuário se a cota foi resetada
                self.salvar(usuario.id_usuario, usuario)
        
        return usuarios_disponiveis