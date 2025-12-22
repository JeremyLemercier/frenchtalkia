import json
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseStorage(ABC, Generic[T]):
    """Classe abstrata base para operações de armazenamento JSON thread-safe."""
    
    def __init__(self, caminho_arquivo: Path) -> None:
        """
        Inicializa o storage com caminho do arquivo JSON.
        
        Args:
            caminho_arquivo: Caminho para o arquivo JSON de armazenamento
        """
        self.caminho_arquivo = caminho_arquivo
        self._lock = threading.Lock()
        
        # Garantir que o diretório existe
        self.caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        # Criar arquivo vazio se não existir
        if not self.caminho_arquivo.exists():
            self._escrever_arquivo({})
    
    def _ler_arquivo(self) -> dict[str, Any]:
        """
        Lê o arquivo JSON com tratamento de erro.
        
        Returns:
            dict: Dados lidos do arquivo ou dicionário vazio se houver erro
        """
        try:
            with self._lock:
                with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _escrever_arquivo(self, dados: dict[str, Any]) -> None:
        """
        Escreve dados no arquivo JSON com indentação e encoding UTF-8.
        
        Args:
            dados: Dados a serem escritos no arquivo
        """
        with self._lock:
            with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
    
    @abstractmethod
    def _serializar(self, item: T) -> dict[str, Any]:
        """
        Converte um item para dicionário JSON.
        
        Args:
            item: Item a ser serializado
            
        Returns:
            dict: Representação JSON do item
        """
        pass
    
    @abstractmethod
    def _deserializar(self, dados: dict[str, Any]) -> T:
        """
        Converte um dicionário JSON para um item.
        
        Args:
            dados: Dicionário JSON a ser convertido
            
        Returns:
            T: Item desserializado
        """
        pass
    
    def obter(self, chave: str) -> T | None:
        """
        Busca item por chave.
        
        Args:
            chave: Chave do item a ser buscado
            
        Returns:
            T | None: Item encontrado ou None se não existir
        """
        dados = self._ler_arquivo()
        if chave in dados:
            return self._deserializar(dados[chave])
        return None
    
    def salvar(self, chave: str, item: T) -> None:
        """
        Salva ou atualiza um item.
        
        Args:
            chave: Chave do item
            item: Item a ser salvo
        """
        dados = self._ler_arquivo()
        dados[chave] = self._serializar(item)
        self._escrever_arquivo(dados)
    
    def listar_todos(self) -> list[T]:
        """
        Retorna todos os itens armazenados.
        
        Returns:
            list[T]: Lista de todos os itens
        """
        dados = self._ler_arquivo()
        return [self._deserializar(item) for item in dados.values()]
    
    def deletar(self, chave: str) -> bool:
        """
        Remove um item pelo chave.
        
        Args:
            chave: Chave do item a ser removido
            
        Returns:
            bool: True se o item foi removido, False se não existia
        """
        dados = self._ler_arquivo()
        if chave in dados:
            del dados[chave]
            self._escrever_arquivo(dados)
            return True
        return False
    
    def existe(self, chave: str) -> bool:
        """
        Verifica se um item existe.
        
        Args:
            chave: Chave do item a ser verificado
            
        Returns:
            bool: True se o item existe, False caso contrário
        """
        dados = self._ler_arquivo()
        return chave in dados
    
    def limpar_todos(self) -> None:
        """Remove todos os itens do armazenamento."""
        self._escrever_arquivo({})