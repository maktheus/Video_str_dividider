# Transcrição e Divisão de Vídeos

Este projeto oferece ferramentas para transcrever vídeos usando Whisper, dividir vídeos em partes e baixar vídeos do YouTube com suas legendas.

## Interface Web

Para iniciar a interface web, execute:

```bash
streamlit run app.py
```

A interface web suporta:
- Upload de arquivos de vídeo ou download de vídeos do YouTube
- Transcrição de vídeos usando Whisper
- Divisão de vídeos em partes iguais ou em pontos específicos
- Download de vídeos divididos com legendas sincronizadas
- Incorporação de legendas diretamente nos vídeos

## Interface de Linha de Comando (CLI)

### Instalação como Pacote Python

Você pode instalar este projeto como um pacote Python para tornar os comandos da CLI disponíveis globalmente no seu sistema:

```bash
# Instalação a partir do diretório do projeto
pip install -e .

# Ou instalar a partir do GitHub
pip install git+https://github.com/seuusername/video-transcription-tool.git
```

Após a instalação, você pode usar o comando `videotranscricao` de qualquer lugar no seu sistema:

```bash
# Ver ajuda disponível
videotranscricao --help
```

### Uso Direto (sem instalação)

Alternativamente, você pode usar a CLI diretamente:

```bash
# Tornar o script executável (se necessário)
chmod +x cli.py

# Executar diretamente
python cli.py COMANDO [OPÇÕES]
```

### Exemplos de Uso da CLI

#### Transcrever um vídeo
```bash
videotranscricao transcribe --input video.mp4 --output legendas.srt
```

#### Baixar e transcrever vídeo do YouTube
```bash
videotranscricao youtube --url "https://www.youtube.com/watch?v=ID_DO_VIDEO" --output video_baixado.mp4 --transcribe
```

#### Dividir um vídeo em partes iguais
```bash
videotranscricao split --input video.mp4 --subtitle legendas.srt --parts 3 --output pasta_saida
```

#### Dividir um vídeo em pontos específicos (segundos)
```bash
videotranscricao split --input video.mp4 --subtitle legendas.srt --timestamps 30,60,90 --output pasta_saida
```

#### Incorporar legendas no vídeo
```bash
videotranscricao embed --input video.mp4 --subtitle legendas.srt --output video_com_legendas.mp4
```

### Ajuda Completa

Para ver todas as opções disponíveis:

```bash
videotranscricao --help
```

Para ajuda específica de um comando:

```bash
videotranscricao transcribe --help
videotranscricao youtube --help
videotranscricao split --help
videotranscricao embed --help
```

## Requisitos

O projeto requer Python 3.8+ e as seguintes bibliotecas:
- streamlit
- whisper
- ffmpeg-python
- yt-dlp
- srt

## Monetização

Este projeto inclui opções de monetização que podem ser configuradas via arquivo `.env`:

1. **Google AdSense:** Para receber dinheiro de anúncios exibidos no aplicativo
2. **Links de Afiliados:** Para receber comissões de produtos recomendados
3. **Doações:** Links personalizados para receber doações

### Configuração do arquivo .env

Para configurar a monetização, crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# Google AdSense
ADSENSE_CLIENT_ID=ca-pub-SEUCODIGO
ADSENSE_SLOT_BANNER=SEUSLOT1
ADSENSE_SLOT_DISPLAY=SEUSLOT2
ADSENSE_SLOT_LEADERBOARD=SEUSLOT3

# Links de afiliados
AFFILIATE_LINK_MICROPHONE=https://amzn.to/seucódigo1
AFFILIATE_LINK_SOFTWARE=https://amzn.to/seucódigo2

# Links de suporte
SUPPORT_LINK_COFFEE=https://www.buymeacoffee.com/seuusername
SUPPORT_LINK_GITHUB=https://github.com/seuusername/video-transcription-tool
```

**Importante:** O arquivo `.env` é automaticamente ignorado pelo `.gitignore` para manter suas credenciais seguras.

## Notas

- A transcrição com Whisper pode levar vários minutos dependendo do tamanho do vídeo e da capacidade do computador.
- Para vídeos longos, considere dividi-los em partes menores antes da transcrição.
- As legendas são automaticamente sincronizadas com os segmentos de vídeo quando um vídeo é dividido.