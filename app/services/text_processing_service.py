class TextProcessingService:
    """Serviço para processamento de mensagens de texto com reconhecimento de padrões."""

    def __init__(self) -> None:
        """Inicializa o serviço de processamento de texto."""
        self.patterns = {
            "ajuda": "Olá! Eu sou o FrenchTalkIA. Posso ajudar você a praticar francês. Envie um áudio ou texto para começar.",
            "menu": "Menu Principal:\n1. Praticar Conversação\n2. Aprender Vocabulário\n3. Dicas de Gramática\nDigite o número ou nome da opção.",
            "falar com humano": "Entendi que você quer falar com um humano. Vou encaminhar sua solicitação para nossa equipe de suporte.",
            "sair": "Au revoir! Espero ver você em breve para mais prática de francês.",
            "info": "FrenchTalkIA v0.1.0\nUm robô inteligente para ajudar no seu aprendizado de francês.",
        }

    def processar_texto(self, texto: str) -> str:
        """
        Processa o texto recebido identificando padrões e retornando uma resposta.

        Args:
            texto: Texto recebido do usuário

        Returns:
            str: Resposta gerada
        """
        texto_lower = texto.lower().strip()
        
        # Verificar padrões exatos ou parciais simples
        resposta = "Desculpe, não entendi. Tente 'ajuda' ou 'menu'."
        
        for pattern, response in self.patterns.items():
            if pattern in texto_lower:
                resposta = response
                break
        
        return resposta
