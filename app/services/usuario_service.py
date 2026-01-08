from app.models.sessao import EstadoSessao, Sessao
from app.models.usuario import Usuario
from app.storage.sessao_storage import SessaoStorage
from app.storage.usuario_storage import UsuarioStorage


class UsuarioService:
    """Serviço para gerenciamento de usuários e suas sessões."""

    def __init__(self, usuario_storage: UsuarioStorage, sessao_storage: SessaoStorage) -> None:
        """
        Inicializa o serviço de usuários.

        Args:
            usuario_storage: Storage de usuários
            sessao_storage: Storage de sessões
        """
        self.usuario_storage = usuario_storage
        self.sessao_storage = sessao_storage

    def obter_ou_criar_usuario(self, telefone: str) -> tuple[Usuario, bool]:
        """
        Obtém usuário existente ou cria um novo.

        Args:
            telefone: Número de telefone do usuário

        Returns:
            tuple[Usuario, bool]: Usuário e flag indicando se é novo
        """
        usuario = self.usuario_storage.obter_por_telefone(telefone)

        if usuario is None:
            # Criar novo usuário
            usuario = Usuario(
                id_usuario=telefone, nome=None, cota_diaria_usada=0, is_processing=False
            )
            self.usuario_storage.salvar(telefone, usuario)

            # Criar sessão inicial
            self.sessao_storage.criar_sessao_nova(telefone, EstadoSessao.AGUARDANDO_NOME)

            return usuario, True

        # Resetar cota se necessário
        usuario.resetar_cota_se_necessario()
        self.usuario_storage.salvar(telefone, usuario)

        return usuario, False

    def registrar_nome_usuario(self, telefone: str, nome: str) -> Usuario:
        """
        Registra o nome do usuário e atualiza seu estado.

        Args:
            telefone: Número de telefone do usuário
            nome: Nome do usuário

        Returns:
            Usuario: Usuário atualizado
        """
        usuario = self.usuario_storage.obter_por_telefone(telefone)
        if usuario is None:
            raise ValueError(f"Usuário com telefone {telefone} não encontrado")

        usuario.nome = nome.strip()
        self.usuario_storage.salvar(telefone, usuario)

        # Atualizar estado da sessão para menu principal
        self.sessao_storage.atualizar_estado(telefone, EstadoSessao.MENU_PRINCIPAL)

        return usuario

    def verificar_cota_disponivel(
        self, id_usuario: str, limite_diario: int = 300
    ) -> tuple[bool, int]:
        """
        Verifica se o usuário tem cota disponível.

        Args:
            id_usuario: ID do usuário
            limite_diario: Limite diário de segundos (padrão: 300 = 5 minutos)

        Returns:
            tuple[bool, int]: Tem cota disponível e segundos restantes
        """
        usuario = self.usuario_storage.obter_por_telefone(id_usuario)
        if usuario is None:
            return False, limite_diario

        # Resetar cota se necessário
        if usuario.resetar_cota_se_necessario():
            self.usuario_storage.salvar(id_usuario, usuario)

        segundos_usados = usuario.cota_diaria_usada
        segundos_restantes = max(0, limite_diario - segundos_usados)
        tem_cota = segundos_restantes > 0

        return tem_cota, segundos_restantes

    def consumir_cota(self, id_usuario: str, segundos: int) -> bool:
        """
        Consome segundos da cota diária do usuário.

        Args:
            id_usuario: ID do usuário
            segundos: Segundos a serem consumidos

        Returns:
            bool: True se a cota foi consumida com sucesso
        """
        try:
            self.usuario_storage.atualizar_cota(id_usuario, segundos)
            return True
        except Exception:
            return False

    def obter_sessao_usuario(self, id_usuario: str) -> Sessao:
        """
        Obtém a sessão atual do usuário ou cria uma nova.

        Args:
            id_usuario: ID do usuário

        Returns:
            Sessao: Sessão do usuário
        """
        sessao = self.sessao_storage.obter_sessao_ativa(id_usuario)

        if sessao is None:
            # Criar nova sessão se não existir
            usuario, _ = self.obter_ou_criar_usuario(id_usuario)
            if usuario.nome:
                # Se usuário já tem nome, vai para menu principal
                sessao = self.sessao_storage.criar_sessao_nova(
                    id_usuario, EstadoSessao.MENU_PRINCIPAL
                )
            else:
                # Se não tem nome, aguarda nome
                sessao = self.sessao_storage.criar_sessao_nova(
                    id_usuario, EstadoSessao.AGUARDANDO_NOME
                )

        return sessao

    def atualizar_estado_sessao(self, id_usuario: str, novo_estado: EstadoSessao) -> None:
        """
        Atualiza o estado da sessão do usuário.

        Args:
            id_usuario: ID do usuário
            novo_estado: Novo estado da sessão
        """
        self.sessao_storage.atualizar_estado(id_usuario, novo_estado)

    def obter_usuario(self, telefone: str) -> Usuario | None:
        """
        Obtém usuário pelo telefone.

        Args:
            telefone: Número de telefone do usuário

        Returns:
            Usuario | None: Usuário encontrado ou None
        """
        return self.usuario_storage.obter_por_telefone(telefone)

    def iniciar_processamento(self, id_usuario: str) -> str:
        """
        Inicia o processamento para um usuário: marca que o usuário está em processamento.

        Args:
            id_usuario: ID do usuário (telefone)

        Returns:
            str: id_usuario
        """

        # Garantir que o usuário/sessão existem
        _ = self.obter_ou_criar_usuario(id_usuario)

        # Marcar flag de processamento no usuário (para compatibilidade)
        self.usuario_storage.atualizar_flag_processing(id_usuario, True)

        # Colocar estado EM_CONVERSA
        try:
            self.sessao_storage.atualizar_estado(id_usuario, EstadoSessao.EM_CONVERSA)
        except Exception:
            # se não houver sessão criada, criaremos uma
            self.sessao_storage.criar_sessao_nova(id_usuario, EstadoSessao.EM_CONVERSA)

        return id_usuario

    def processamento_em_andamento(self, id_usuario: str) -> bool:
        """
        Indica se há um processamento em andamento para o usuário.

        Usa a presença de flag `is_processing` do usuário.
        """
        usuario = self.usuario_storage.obter_por_telefone(id_usuario)
        if usuario:
            return bool(usuario.is_processing)
        return False

    def finalizar_processamento(self, id_usuario: str) -> None:
        """
        Finaliza o processamento para o usuário, se corresponder à sessão ativa. Reseta o estado da sessão.

        Args:
            id_usuario: ID do usuário (telefone)
        """
        sessao = self.sessao_storage.obter_sessao_ativa(id_usuario)
        if sessao is None:
            return
            
        try:
            usuario = self.usuario_storage.obter_por_telefone(id_usuario)
        except Exception:
            usuario = None

        self.usuario_storage.atualizar_flag_processing(id_usuario, False)

        if usuario and usuario.nome:
            sessao.atualizar_estado(EstadoSessao.MENU_PRINCIPAL)
        else:
            sessao.atualizar_estado(EstadoSessao.AGUARDANDO_NOME)

        # Persistir alterações
        self.sessao_storage.salvar(id_usuario, sessao)

        # Limpar flag de processamento do usuário
        self.usuario_storage.atualizar_flag_processing(id_usuario, False)

    def is_usuario_bloqueado(self, id_usuario: str) -> bool:
        """
        Verifica se usuário está bloqueado para processamento.

        Args:
            id_usuario: ID do usuário

        Returns:
            bool: True se usuário está bloqueado
        """
        usuario = self.usuario_storage.obter_por_telefone(id_usuario)
        return usuario.is_processing if usuario else False