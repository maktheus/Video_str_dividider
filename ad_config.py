"""
Configurações de monetização para o aplicativo.
Os valores são carregados do arquivo .env para manter as credenciais seguras.
"""
import os
from dotenv import load_dotenv
import logging

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Tenta obter as configurações do arquivo .env, com fallbacks para valores de exemplo
try:
    # Google AdSense
    ADSENSE_CLIENT_ID = os.getenv("ADSENSE_CLIENT_ID", "ca-pub-1234567890123456")
    
    # Slots de anúncios
    ADSENSE_SLOTS = {
        "banner": os.getenv("ADSENSE_SLOT_BANNER", "1234567890"),
        "display": os.getenv("ADSENSE_SLOT_DISPLAY", "0987654321"),
        "leaderboard": os.getenv("ADSENSE_SLOT_LEADERBOARD", "1122334455"),
        "sidebar": os.getenv("ADSENSE_SLOT_SIDEBAR", "5566778899")
    }
    
    # Links de afiliados
    AFFILIATE_LINKS = {
        "microphone": os.getenv("AFFILIATE_LINK_MICROPHONE", "https://amzn.to/example1"),
        "software": os.getenv("AFFILIATE_LINK_SOFTWARE", "https://amzn.to/example2"),
        "camera": os.getenv("AFFILIATE_LINK_CAMERA", "https://amzn.to/example3"),
        "course": os.getenv("AFFILIATE_LINK_COURSE", "https://example.com/curso-video")
    }
    
    # Links de suporte
    SUPPORT_LINKS = {
        "coffee": os.getenv("SUPPORT_LINK_COFFEE", "https://www.buymeacoffee.com/seuusername"),
        "github": os.getenv("SUPPORT_LINK_GITHUB", "https://github.com/seuusername/video-transcription-tool")
    }
    
    # Imagens para anúncios de afiliados (opcional)
    AFFILIATE_IMAGES = {
        "microphone": "https://via.placeholder.com/300x200?text=Microfone",
        "software": "https://via.placeholder.com/300x200?text=Software",
        "camera": "https://via.placeholder.com/300x200?text=Camera",
        "course": "https://via.placeholder.com/300x200?text=Curso"
    }
    
    # Log de sucesso
    logging.info("Configurações de monetização carregadas com sucesso.")
    
except Exception as e:
    # Log de erro e uso de valores padrão
    logging.error(f"Erro ao carregar configurações de monetização: {e}")
    logging.warning("Usando valores de exemplo para configurações de monetização.")
    
    # Valores padrão em caso de erro
    ADSENSE_CLIENT_ID = "ca-pub-1234567890123456"
    
    ADSENSE_SLOTS = {
        "banner": "1234567890",
        "display": "0987654321",
        "leaderboard": "1122334455",
        "sidebar": "5566778899"
    }
    
    AFFILIATE_LINKS = {
        "microphone": "https://amzn.to/example1",
        "software": "https://amzn.to/example2",
        "camera": "https://amzn.to/example3",
        "course": "https://example.com/curso-video"
    }
    
    SUPPORT_LINKS = {
        "coffee": "https://www.buymeacoffee.com/seuusername",
        "github": "https://github.com/seuusername/video-transcription-tool"
    }
    
    AFFILIATE_IMAGES = {
        "microphone": "https://via.placeholder.com/300x200?text=Microfone",
        "software": "https://via.placeholder.com/300x200?text=Software",
        "camera": "https://via.placeholder.com/300x200?text=Camera",
        "course": "https://via.placeholder.com/300x200?text=Curso"
    }