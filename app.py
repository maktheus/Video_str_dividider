import streamlit as st
import os
import tempfile
import time
from video_processor import VideoProcessor
from subtitle_processor import SubtitleProcessor
from utils import save_uploaded_file, create_download_link
from ads import display_ad, display_affiliate_ad, display_support_message, show_video_tools_ads

# Set page configuration
st.set_page_config(
    page_title="Transcrição e Divisão de Vídeos",
    page_icon="🎬",
    layout="wide",
)

# Importar configurações de anúncios
from ad_config import ADSENSE_CLIENT_ID, ADSENSE_SLOTS, AFFILIATE_LINKS, AFFILIATE_IMAGES

# Inject AdSense script into HTML head - carrega do arquivo .env via ad_config.py
adsense_script = f"""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT_ID}"
     crossorigin="anonymous"></script>
<!-- Google AdSense verificação de site -->
<meta name="google-adsense-account" content="{ADSENSE_CLIENT_ID}">
"""
st.markdown(adsense_script, unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'subtitle_path' not in st.session_state:
    st.session_state.subtitle_path = None
if 'segments' not in st.session_state:
    st.session_state.segments = []
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()

# Create a modern header with title and description
st.markdown("""
<div style="text-align:center; padding:10px 0 30px 0;">
    <h1 style="color:#1e3a8a; font-size:36px; font-weight:700; margin-bottom:12px;">
        🎬 Transcrição e Divisão de Vídeos
    </h1>
    <p style="color:#4a5568; font-size:18px; max-width:800px; margin:0 auto; line-height:1.5;">
        Transforme seus vídeos com transcrições profissionais, divida em partes perfeitas 
        e baixe com legendas sincronizadas automaticamente.
    </p>
</div>
""", unsafe_allow_html=True)

# Top banner ad in a more subtle way
col_ad = st.container()
with col_ad:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        display_ad(
            ad_type="banner", 
            slot_id=ADSENSE_SLOTS["banner"], 
            client_id=ADSENSE_CLIENT_ID,
            width=728, 
            height=90
        )

# Display support message in a more prominent position
display_support_message()

# Create custom tabs with icons and better labels
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px;
        padding: 0 20px;
        background-color: #f0f6ff;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4287f5 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Create tabs for different stages of the process with modern naming
tabs = st.tabs(["📤 Adicionar Vídeo & Transcrever", "✂️ Dividir em Segmentos", "⬇️ Baixar & Compartilhar"])

# Tab 1: Upload and Transcribe
with tabs[0]:
    st.markdown("""
    <div style="margin-bottom:20px;">
        <h3 style="color:#1e3a8a; font-size:20px; font-weight:600; margin-bottom:8px;">
            Adicione seu vídeo para começar
        </h3>
        <p style="color:#4a5568; font-size:15px; margin-top:0;">
            Faça upload de um arquivo local ou baixe diretamente de uma URL do YouTube
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create styled tabs for file upload methods
    upload_tabs = st.tabs(["📂 Upload de Arquivo", "🎬 Baixar do YouTube"])
    
    # Tab for file upload
    with upload_tabs[0]:
        st.markdown("""
        <p style="color:#4a5568; font-size:14px; margin-bottom:15px;">
            Selecione um arquivo de vídeo do seu computador para transcrever. 
            Suportamos MP4, AVI, MOV e outros formatos populares.
        </p>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Arraste seu arquivo aqui ou clique para selecionar", 
                                         type=["mp4", "avi", "mov", "mkv", "webm"])
        
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            if st.session_state.video_path is None:
                st.session_state.video_path = save_uploaded_file(uploaded_file, st.session_state.temp_dir)
                st.success("✅ Vídeo carregado com sucesso! Pronto para transcrever.")
    
    # Tab for YouTube link
    with upload_tabs[1]:
        st.markdown("""
        <p style="color:#4a5568; font-size:14px; margin-bottom:15px;">
            Cole o link de qualquer vídeo público do YouTube para baixar e transcrever automaticamente.
            Ideal para palestras, tutoriais e entrevistas.
        </p>
        """, unsafe_allow_html=True)
        
        youtube_url = st.text_input("Cole a URL do YouTube aqui", 
                                   placeholder="https://www.youtube.com/watch?v=...")
        
        if youtube_url:
            st.markdown("<hr style='margin: 20px 0 15px 0; border:none; height:1px; background-color:#e0e8f5;'>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="margin:10px 0 20px 0;">
                <h4 style="color:#1e3a8a; font-size:16px; font-weight:600; margin-bottom:8px;">
                    ⚙️ Configurações de Download e Processamento
                </h4>
                <p style="color:#4a5568; font-size:14px; margin-top:0;">
                    Configure as opções antes de iniciar o download do vídeo
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Configurações de download
            config_cols = st.columns([1, 1])
            
            with config_cols[0]:
                # Configurações de download
                st.markdown("<p style='font-weight:500; font-size:15px;'>Opções de Download</p>", unsafe_allow_html=True)
                
                # Opção para baixar com legendas
                download_with_subs = st.checkbox("Baixar legendas disponíveis no YouTube", 
                                              value=True,
                                              help="Se disponíveis, baixa as legendas oficiais ou automáticas do YouTube junto com o vídeo")
                
                # Opção só para legendas
                subs_only = st.checkbox("Apenas legendas (sem vídeo)", 
                                     value=False,
                                     help="Baixa somente as legendas, sem o vídeo")
                
                # Qualidade do vídeo para download
                video_quality_options = {
                    'low': "Baixa - Menor arquivo, download rápido",
                    'medium': "Média - 720p, bom equilíbrio",
                    'high': "Alta - Melhor resolução disponível"
                }
                
                download_quality = st.selectbox(
                    "Qualidade do vídeo",
                    options=list(video_quality_options.keys()),
                    format_func=lambda x: video_quality_options.get(x, x),
                    index=1,  # Medium por padrão
                    key="download_quality_select",
                    help="Selecione a qualidade do vídeo a ser baixado do YouTube"
                )
                
            with config_cols[1]:
                # Configurações de transcrição (apenas se não for somente legendas)
                if not subs_only:
                    st.markdown("<p style='font-weight:500; font-size:15px;'>Opções de Transcrição</p>", unsafe_allow_html=True)
                
                    # Modelo Whisper
                    model_display = {
                        "tiny": "Tiny - Mais rápido (menor precisão)",
                        "base": "Base - Equilíbrio velocidade/precisão",
                        "small": "Small - Maior precisão (mais lento)"
                    }
                    
                    # Recuperar configurações anteriores (se existirem)
                    default_model = st.session_state.get("whisper_model", "tiny")
                    
                    whisper_model = st.selectbox(
                        "Modelo de transcrição",
                        options=["tiny", "base", "small"],
                        format_func=lambda x: model_display.get(x, x),
                        index=["tiny", "base", "small"].index(default_model) if default_model in ["tiny", "base", "small"] else 0,
                        key="youtube_whisper_model",
                        help="Escolha o modelo do Whisper para a transcrição. Modelos maiores são mais precisos, mas mais lentos."
                    )
                    
                    # Qualidade da transcrição
                    quality_display = {
                        "fast": "Rápida - Otimizada para velocidade",
                        "balanced": "Balanceada - Bom equilíbrio",
                        "high": "Alta - Máxima precisão (mais lenta)"
                    }
                    
                    # Recuperar qualidade anterior (se existir)
                    default_quality = st.session_state.get("quality_preset", "fast")
                    
                    quality_preset = st.selectbox(
                        "Qualidade da transcrição",
                        options=["fast", "balanced", "high"],
                        format_func=lambda x: quality_display.get(x, x),
                        index=["fast", "balanced", "high"].index(default_quality) if default_quality in ["fast", "balanced", "high"] else 0,
                        key="youtube_quality_preset",
                        help="Configure o nível de qualidade da transcrição."
                    )
                    
                    # Atualizar session_state imediatamente ao alterar os valores
                    st.session_state.whisper_model = whisper_model
                    st.session_state.quality_preset = quality_preset
            
            # Botão destacado para iniciar o processamento
            st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
            
            # Ações disponíveis baseadas nas opções
            action_cols = st.columns([2, 2, 1])
            
            with action_cols[0]:
                if not subs_only:
                    # Botão para baixar vídeo (com ou sem legendas)
                    process_button_label = "📥 Baixar e Processar Vídeo"
                    process_help_text = "Baixa o vídeo do YouTube e prepara para transcrição" + (" (com legendas originais)" if download_with_subs else "")
                    
                    if st.button(process_button_label, 
                               help=process_help_text,
                               use_container_width=True,
                               type="primary"):  # Botão destacado
                        try:
                            with st.spinner("🔄 Baixando do YouTube..."):
                                video_processor = VideoProcessor()
                                
                                # Passar a qualidade selecionada para o download
                                result = video_processor.download_youtube_video(
                                    youtube_url, 
                                    st.session_state.temp_dir, 
                                    download_with_subs,
                                    quality=download_quality
                                )
                                
                                # Handle subtitle result
                                if download_with_subs and isinstance(result, dict):
                                    st.session_state.video_path = result['video_path']
                                    
                                    # Check if subtitles were found
                                    if result.get('subtitle_path'):
                                        st.session_state.subtitle_path = result['subtitle_path']
                                        st.session_state.processing_complete = True
                                        st.session_state.transcription_complete = True
                                        
                                        st.success("✅ Vídeo e legendas originais baixados com sucesso!")
                                        st.info("ℹ️ As legendas do YouTube foram carregadas. Você pode pular a etapa de transcrição e ir direto para a divisão ou download.")
                                    else:
                                        st.success("✅ Vídeo baixado com sucesso, mas sem legendas disponíveis.")
                                        st.info("Prossiga com a transcrição Whisper para gerar as legendas.")
                                else:
                                    st.session_state.video_path = result
                                    st.success("✅ Vídeo baixado com sucesso! Pronto para transcrever.")
                                    

                                    

                                
                        except Exception as e:
                            st.error(f"❌ Erro ao baixar vídeo: {str(e)}")
            
            with action_cols[1]:
                if subs_only:
                    # Botão apenas para legendas
                    if st.button("📄 Baixar Apenas Legendas", 
                               help="Tenta baixar apenas as legendas do vídeo do YouTube (se disponíveis)",
                               use_container_width=True):
                        try:
                            with st.spinner("🔄 Verificando e baixando legendas..."):
                                video_processor = VideoProcessor()
                                subtitle_path = video_processor.download_youtube_subtitles(youtube_url, st.session_state.temp_dir)
                                
                                if subtitle_path:
                                    st.session_state.subtitle_path = subtitle_path
                                    st.session_state.processing_complete = True
                                    st.session_state.transcription_complete = True
                                    
                                    # Exibir botão de download para as legendas
                                    with open(subtitle_path, 'r', encoding='utf-8', errors='replace') as f:
                                        subtitle_data = f.read()
                                        st.download_button(
                                            label="⬇️ Baixar Legendas SRT",
                                            data=subtitle_data,
                                            file_name="legendas_youtube.srt",
                                            mime="text/plain"
                                        )
                                    
                                    # Mostrar prévia
                                    if len(subtitle_data) > 500:
                                        subtitle_preview = subtitle_data[:500] + "..."
                                    else:
                                        subtitle_preview = subtitle_data
                                        
                                    # Tratar a substituição de quebras de linha antes do f-string    
                                    subtitle_preview_html = subtitle_preview.replace('\n', '<br>')
                                        
                                    st.markdown(f"""
                                    <div style="max-height:200px; overflow-y:auto; padding:15px; background-color:#f7f9fc; 
                                        border-radius:8px; margin:15px 0; border:1px solid #e0e8f5; font-size:14px; line-height:1.6;">
                                        {subtitle_preview_html}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                else:
                                    st.error("❌ Este vídeo não possui legendas disponíveis no YouTube.")
                                    st.info("Tente baixar o vídeo completo e usar o Whisper para transcrição automática.")
                        except Exception as e:
                            st.error(f"❌ Erro ao baixar legendas: {str(e)}")
    
    # Display video and transcription options if a video is loaded
    if st.session_state.video_path is not None:
        st.markdown("<hr style='margin: 30px 0 20px 0; border:none; height:1px; background-color:#e0e8f5;'>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-bottom:15px;">
            <h3 style="color:#1e3a8a; font-size:20px; font-weight:600; margin-bottom:8px;">
                🎥 Seu vídeo está pronto para processamento
            </h3>
            <p style="color:#4a5568; font-size:14px; margin-top:0;">
                Visualize seu vídeo e clique no botão abaixo para iniciar a transcrição com inteligência artificial
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns to display video and info side by side
        vid_col1, vid_col2 = st.columns([2, 1])
        
        with vid_col1:
            # Display the uploaded video with a styled container
            st.markdown("<div style='padding:5px; border-radius:10px; background-color:#f0f6ff;'>", unsafe_allow_html=True)
            st.video(st.session_state.video_path)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with vid_col2:
            # Display video information
            video_processor = VideoProcessor()
            duration = video_processor.get_video_duration(st.session_state.video_path)
            duration_min = int(duration // 60)
            duration_sec = int(duration % 60)
            
            # Calcula o tempo estimado de transcrição com otimizações (cerca de 0.75x a duração do vídeo)
            est_transcription_time = max(1, int(duration_min * 0.75))
            
            st.markdown(f"""
            <div style="background-color:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); height:100%;">
                <h4 style="color:#4287f5; font-size:16px; margin-bottom:15px; font-weight:600;">Informações do Vídeo</h4>
                <div style="margin-bottom:10px;">
                    <div style="font-size:14px; color:#718096; margin-bottom:2px;">Duração:</div>
                    <div style="font-weight:500; color:#2d3748;">{duration_min} minutos e {duration_sec} segundos</div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="font-size:14px; color:#718096; margin-bottom:2px;">Formato:</div>
                    <div style="font-weight:500; color:#2d3748;">{os.path.splitext(st.session_state.video_path)[1].upper().replace(".", "")}</div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="font-size:14px; color:#718096; margin-bottom:2px;">Tamanho estimado da transcrição:</div>
                    <div style="font-weight:500; color:#2d3748;">~{int(duration * 1.5)} palavras</div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="font-size:14px; color:#718096; margin-bottom:2px;">Tempo estimado para transcrição:</div>
                    <div style="font-weight:500; color:#2d3748;">~{est_transcription_time} minutos</div>
                </div>
                <div style="margin-top:15px; padding:10px; background-color:#ebfbee; border-radius:5px; border-left:3px solid #48bb78;">
                    <div style="font-size:12px; color:#2d3748;">
                        <strong>Nota:</strong> A transcrição utiliza o modelo <strong>tiny</strong> do Whisper com otimizações para máxima velocidade.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Transcribe button section
        if 'transcription_started' not in st.session_state:
            st.session_state.transcription_started = False
            
        if 'transcription_complete' not in st.session_state:
            st.session_state.transcription_complete = False
        
        # Instruções e avisos importantes antes da transcrição
        st.markdown(f"""
        <div style="margin:25px 0 15px 0; padding:15px; background-color:#fff7e3; border-radius:8px; border-left:4px solid #f6ad55;">
            <h4 style="color:#c05621; margin-top:0; font-size:16px; font-weight:600;">⚠️ Informações importantes</h4>
            <p style="color:#4a5568; margin-bottom:5px; font-size:14px;">
                • A transcrição leva em média <strong>{est_transcription_time} minutos</strong> para este vídeo
            </p>
            <p style="color:#4a5568; margin-bottom:5px; font-size:14px;">
                • Todo o processamento é feito localmente em seu computador
            </p>
            <p style="color:#4a5568; margin-bottom:0; font-size:14px;">
                • Não feche esta página durante o processamento
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Elegante botão de transcrição com colunas para melhor layout
        st.markdown("<div style='margin:25px 0;'>", unsafe_allow_html=True)
        
        # Informações de qualidade e modelo definidas (usar valores das configurações do YouTube quando disponíveis)
        # Recuperar modelo e qualidade da session_state (que foram salvos anteriormente)
        whisper_model = st.session_state.get("whisper_model", "tiny")
        quality_preset = st.session_state.get("quality_preset", "fast")
        
        # Dicionários de exibição para mostrar nomes amigáveis em vez de valores técnicos
        model_display = {
            "tiny": "Tiny - Mais rápido (menor precisão)",
            "base": "Base - Equilíbrio velocidade/precisão",
            "small": "Small - Maior precisão (mais lento)"
        }
        
        quality_display = {
            "fast": "Rápida - Otimizada para velocidade",
            "balanced": "Balanceada - Bom equilíbrio",
            "high": "Alta - Máxima precisão (mais lenta)"
        }
        
        # Mostrar informações do modelo e qualidade selecionados
        model_quality_info = st.container()
        with model_quality_info:
            st.markdown(f"""
            <div style="background-color:#f0f9ff; padding:15px; border-radius:8px; margin:10px 0; border-left:4px solid #3b82f6;">
                <p style="margin:0 0 8px 0; font-weight:600; color:#1e3a8a;">Configurações de Transcrição:</p>
                <div style="display:flex; flex-wrap:wrap; gap:15px;">
                    <div style="min-width:180px;">
                        <span style="font-size:13px; color:#4b5563; display:block;">Modelo:</span>
                        <span style="font-weight:500; color:#1e40af;">{model_display.get(whisper_model, whisper_model)}</span>
                    </div>
                    <div style="min-width:180px;">
                        <span style="font-size:13px; color:#4b5563; display:block;">Qualidade:</span>
                        <span style="font-weight:500; color:#1e40af;">{quality_display.get(quality_preset, quality_preset)}</span>
                    </div>
                </div>
                <p style="margin:10px 0 0 0; font-size:13px; color:#4b5563;">
                    Para alterar estas configurações, você pode ajustá-las na etapa de download do YouTube.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        # Estimativa de tempo atualizada com base no modelo e qualidade
        time_multipliers = {
            "tiny": {"fast": 0.75, "balanced": 1.0, "high": 1.25},
            "base": {"fast": 1.0, "balanced": 1.25, "high": 1.5},
            "small": {"fast": 1.5, "balanced": 1.75, "high": 2.0}
        }
        
        time_multiplier = time_multipliers[whisper_model][quality_preset]
        est_transcription_time = max(1, int(duration_min * time_multiplier))
        
        # Atualizar a mensagem de tempo estimado com base na seleção
        st.markdown(f"""
        <div style="margin:10px 0 15px 0; padding:10px; background-color:#e6fffa; border-radius:6px; border-left:3px solid #38b2ac;">
            <p style="margin:0; color:#2c7a7b; font-size:14px;">
                <strong>Tempo estimado:</strong> Cerca de {est_transcription_time} minutos com o modelo selecionado
            </p>
        </div>
        """, unsafe_allow_html=True)
            
        # Check if we should start transcription
        transcribe_col1, transcribe_col2, transcribe_col3 = st.columns([1, 2, 1])
        with transcribe_col2:
            # Destaque para o botão com estilo personalizado antes do botão real
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:10px;">
                <span style="background-color:#f9a825; color:white; padding:3px 8px; border-radius:4px; font-size:12px; font-weight:500;">
                    MODELO {whisper_model.upper()} - QUALIDADE {quality_preset.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔊 Iniciar Transcrição", 
                        help=f"Utiliza o modelo {whisper_model} do Whisper com configuração de qualidade {quality_preset}. Esta operação leva cerca de {time_multiplier}x a duração do vídeo.",
                        use_container_width=True,
                        type="primary") or st.session_state.transcription_started:
                # Set flag to indicate transcription has started
                st.session_state.transcription_started = True
            
            # Initialize processors
            subtitle_processor = SubtitleProcessor()
            video_processor = VideoProcessor()
            
            # Define output path
            output_srt_path = os.path.join(st.session_state.temp_dir, "subtitles.srt")
            
            # Check if transcription is already in progress
            if not st.session_state.transcription_complete:
                # Styled container for transcription progress
                transcription_container = st.container()
                with transcription_container:
                    st.markdown("""
                    <div style="background-color:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin:15px 0;">
                        <h4 style="color:#4287f5; font-size:16px; margin-bottom:15px; font-weight:600;">
                            🤖 IA processando seu áudio
                        </h4>
                    """, unsafe_allow_html=True)
                    
                    # Start or continue transcription with selected model and quality
                    transcription_status = subtitle_processor.transcribe_video_async(
                        st.session_state.video_path, 
                        output_srt_path,
                        model=whisper_model,
                        quality_preset=quality_preset
                    )
                    
                    # Check if transcription is finished
                    if transcription_status.get('complete', False):
                        st.session_state.subtitle_path = output_srt_path
                        st.session_state.processing_complete = True
                        st.session_state.transcription_complete = True
                        st.session_state.transcription_started = False
                        
                        # Show completion status
                        st.markdown("""
                        <div style="margin-top:10px;">
                            <span style="background-color:#4caf50; color:white; padding:4px 8px; border-radius:4px; font-size:13px; font-weight:500;">
                                CONCLUÍDO
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)  # Close the container
                        
                        st.success("✅ Transcrição concluída com sucesso! Agora você pode dividir o vídeo ou baixar a legenda.")
                    else:
                        # Show progress and status in a more attractive way
                        st.write(f"**Status atual:** {transcription_status.get('message', 'Processando...')}")
                        
                        # Show progress if available
                        progress_value = transcription_status.get('progress', 0)
                        st.progress(progress_value)
                        
                        # Show estimated time with faster processing
                        duration = video_processor.get_video_duration(st.session_state.video_path)
                        video_minutes = int(duration // 60)
                        
                        # Com as otimizações, o tempo estimado agora é de 0.5x a 1x a duração do vídeo
                        est_time = max(1, int(video_minutes * 0.75))
                        
                        st.info(f"⏱️ Transcrição em andamento (modo rápido). Tempo estimado: cerca de {est_time} minutos para um vídeo de {video_minutes} minutos.")
                        
                        # Discretely show a small ad while they wait
                        st.markdown("<div style='margin:20px 0;'>", unsafe_allow_html=True)
                        ad_col1, ad_col2, ad_col3 = st.columns([1, 2, 1])
                        with ad_col2:
                            display_ad(
                                ad_type="processing", 
                                slot_id=ADSENSE_SLOTS.get("display", ADSENSE_SLOTS["banner"]), 
                                client_id=ADSENSE_CLIENT_ID,
                                width=300, 
                                height=100
                            )
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)  # Close the container
                        
                        # Add a rerun to check progress
                        time.sleep(1)
                        st.rerun()
                
            # If transcription is complete, just update state
            elif st.session_state.transcription_complete:
                st.session_state.subtitle_path = output_srt_path
                st.session_state.processing_complete = True
            
            # Display the subtitles if transcription is complete
            if st.session_state.subtitle_path and os.path.exists(st.session_state.subtitle_path):
                st.markdown("""
                <div style="margin-top:25px; margin-bottom:10px;">
                    <h3 style="color:#1e3a8a; font-size:20px; font-weight:600; margin-bottom:8px;">
                        📝 Legendas Geradas
                    </h3>
                    <p style="color:#4a5568; font-size:14px; margin-top:0;">
                        Suas legendas foram geradas com sucesso. Você pode visualizá-las abaixo ou baixá-las.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a better download button
                with open(st.session_state.subtitle_path, 'r') as f:
                    subtitle_data = f.read()
                    
                download_col1, download_col2 = st.columns([1, 3])
                with download_col1:
                    st.download_button(
                        label="⬇️ Baixar Legendas (SRT)",
                        data=subtitle_data,
                        file_name="legendas.srt",
                        mime="text/plain",
                        help="Arquivo de legendas no formato SRT compatível com a maioria dos players de vídeo",
                        use_container_width=True
                    )
                
                # Parse SRT for cleaner preview
                import re
                # Remove timing info for preview
                preview_text = re.sub(r'\d+\s+\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s+', '', subtitle_data)
                # Remove numbers
                preview_text = re.sub(r'^\d+$', '', preview_text, flags=re.MULTILINE)
                # Clean up extra whitespace
                preview_text = re.sub(r'\n\s*\n', '\n\n', preview_text)
                
                # Show preview in a nice scrollable container
                st.markdown(f"""
                <div style="max-height:250px; overflow-y:auto; padding:20px; background-color:#f7f9fc; 
                     border-radius:8px; margin:15px 0 20px 0; border:1px solid #e0e8f5; font-size:14px; line-height:1.6;">
                    {preview_text[:1000]}
                    {"..." if len(preview_text) > 1000 else ""}
                </div>
                """, unsafe_allow_html=True)
                
                # Adicionar uma sugestão discreta para a próxima etapa
                st.markdown("""
                <div style="padding:15px; background-color:#e6f7ff; border-radius:8px; margin:20px 0; border-left:4px solid #4287f5;">
                    <h4 style="color:#1e3a8a; margin-top:0; font-size:16px; font-weight:600;">💡 Próximo passo recomendado</h4>
                    <p style="margin-bottom:0; color:#4a5568;">
                        Agora você pode dividir seu vídeo em partes usando a aba <strong>"✂️ Dividir em Segmentos"</strong> acima. 
                        As legendas serão automaticamente sincronizadas com cada parte!
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Now add a subtle ad below the transcription
                st.markdown("<div style='margin:15px 0; text-align:center;'>", unsafe_allow_html=True)
                display_ad(
                    ad_type="inline", 
                    slot_id=ADSENSE_SLOTS.get("leaderboard", ADSENSE_SLOTS["banner"]), 
                    client_id=ADSENSE_CLIENT_ID,
                    width=728, 
                    height=90
                )
                st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: Split Video
with tabs[1]:
    if st.session_state.processing_complete:
        st.markdown("""
        <div style="margin-bottom:20px;">
            <h3 style="color:#1e3a8a; font-size:22px; font-weight:600; margin-bottom:8px;">
                ✂️ Dividir Vídeo em Segmentos
            </h3>
            <p style="color:#4a5568; font-size:15px; margin-top:0;">
                Divida seu vídeo em partes iguais ou em pontos específicos para facilitar o compartilhamento
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add explanation about subtitles in a beautiful info box
        st.markdown("""
        <div style="padding:15px; background-color:#f0f6ff; border-radius:8px; margin:15px 0; border-left:4px solid #4287f5;">
            <h4 style="color:#1e3a8a; margin-top:0; font-size:16px; font-weight:600;">💡 Como funciona</h4>
            <p style="margin-bottom:0; color:#4a5568; line-height:1.5;">
                Ao dividir o vídeo, o sistema também divide automaticamente as legendas. 
                Cada segmento de vídeo recebe suas próprias legendas sincronizadas, com os tempos
                ajustados para corresponder ao novo segmento. Isso é perfeito para compartilhar 
                em redes sociais ou dividir conteúdo longo em partes.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show original video for reference
        st.write("#### Vídeo Original")
        st.video(st.session_state.video_path)
        
        st.write("#### Configurar Divisão")
        st.write("Especifique como você deseja dividir o vídeo:")
        
        # Opções de qualidade de vídeo
        quality_cols = st.columns([3, 2])
        with quality_cols[0]:
            video_quality = st.select_slider(
                "Qualidade do vídeo:",
                options=["low", "medium", "high"],
                value="medium",
                format_func=lambda x: {
                    "low": "Baixa (mais rápido)",
                    "medium": "Média (equilibrado)",
                    "high": "Alta (qualidade máxima)"
                }.get(x, x)
            )
            
        with quality_cols[1]:
            st.info({
                "low": "⚡ Processamento rápido, qualidade menor",
                "medium": "⚖️ Bom equilíbrio velocidade/qualidade",
                "high": "🔍 Máxima qualidade, mais lento"
            }.get(video_quality))
        
        # Option for splitting method
        split_method = st.radio(
            "Escolha o método de divisão:",
            ["Partes iguais", "Marcadores de tempo personalizados"]
        )
        
        video_processor = VideoProcessor()
        duration = video_processor.get_video_duration(st.session_state.video_path)
        
        # Show video duration
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        st.write(f"**Duração do vídeo:** {minutes} minutos e {seconds} segundos ({duration:.2f} segundos)")
        
        # Initialize segments in session state if not exists
        if 'segments' not in st.session_state:
            st.session_state.segments = []
        
        if split_method == "Partes iguais":
            # Add some tips
            st.info("💡 Este modo divide o vídeo em partes com igual duração.")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                num_parts = st.number_input("Número de partes", min_value=2, max_value=20, value=2)
            
            with col2:
                segment_duration = duration / num_parts
                segment_min = int(segment_duration // 60)
                segment_sec = int(segment_duration % 60)
                st.write(f"Cada parte: ~{segment_min}m {segment_sec}s")
            
            if st.button("Dividir Vídeo", key="split_equal"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Show initial status
                status_text.write("Iniciando divisão do vídeo...")
                progress_bar.progress(10)
                
                # Clear previous segments
                st.session_state.segments = []
                
                # Split the video and subtitles
                try:
                    # Update status
                    status_text.write("Processando segmentos de vídeo...")
                    progress_bar.progress(30)
                    
                    # Split the video with the selected quality
                    st.session_state.segments = video_processor.split_video_equal_parts(
                        st.session_state.video_path,
                        st.session_state.subtitle_path,
                        num_parts,
                        st.session_state.temp_dir,
                        quality=video_quality
                    )
                    
                    # Complete progress
                    progress_bar.progress(100)
                    status_text.write(f"✅ Vídeo dividido em {num_parts} partes com sucesso!")
                    
                except Exception as e:
                    st.error(f"Erro ao dividir vídeo: {str(e)}")
                    progress_bar.progress(0)
        
        else:  # Custom timestamps
            # Add some tips
            st.info("💡 Este modo permite dividir o vídeo em pontos específicos. Digite os tempos (em segundos) nos quais deseja fazer os cortes.")
            
            # Add example markers based on video duration
            if duration > 60:
                example_markers = [
                    int(duration * 0.25),  # 25% of the video
                    int(duration * 0.5),   # 50% of the video
                    int(duration * 0.75)   # 75% of the video
                ]
                example_str = '\n'.join([str(marker) for marker in example_markers])
            else:
                example_str = "5\n10\n15"
            
            # Allow user to specify timestamps
            timestamps_str = st.text_area(
                "Digite os marcadores de tempo (em segundos, um por linha):",
                value=example_str,
                help="Por exemplo, para um vídeo de 5 minutos (300 segundos), você pode digitar:\n60\n120\n180\n240"
            )
            
            # Add a visualization of the markers
            if timestamps_str:
                try:
                    timestamps = [float(ts.strip()) for ts in timestamps_str.split('\n') if ts.strip()]
                    timestamps = sorted([ts for ts in timestamps if 0 < ts < duration])
                    
                    if timestamps:
                        # Calculate segment positions for visualization
                        segment_points = [0] + timestamps + [duration]
                        segments_info = []
                        
                        for i in range(len(segment_points) - 1):
                            start = segment_points[i]
                            end = segment_points[i+1]
                            segment_duration = end - start
                            
                            # Format times
                            start_min = int(start // 60)
                            start_sec = int(start % 60)
                            end_min = int(end // 60)
                            end_sec = int(end % 60)
                            
                            segments_info.append(
                                f"Segmento {i+1}: {start_min}m{start_sec}s - {end_min}m{end_sec}s (duração: {segment_duration:.1f}s)"
                            )
                        
                        # Show segments info
                        st.write("**Segmentos que serão criados:**")
                        for info in segments_info:
                            st.write(info)
                except ValueError:
                    st.warning("Por favor, digite apenas valores numéricos para os marcadores de tempo.")
            
            if st.button("Dividir Vídeo", key="split_custom"):
                if timestamps_str:
                    try:
                        timestamps = [float(ts.strip()) for ts in timestamps_str.split('\n') if ts.strip()]
                        timestamps = sorted([ts for ts in timestamps if 0 < ts < duration])
                        
                        if timestamps:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Show initial status
                            status_text.write("Iniciando divisão do vídeo...")
                            progress_bar.progress(10)
                            
                            # Clear previous segments
                            st.session_state.segments = []
                            
                            try:
                                # Update status
                                status_text.write("Processando segmentos de vídeo nos pontos especificados...")
                                progress_bar.progress(30)
                                
                                # Split the video with the selected quality
                                st.session_state.segments = video_processor.split_video_custom_timestamps(
                                    st.session_state.video_path,
                                    st.session_state.subtitle_path,
                                    timestamps,
                                    st.session_state.temp_dir,
                                    quality=video_quality
                                )
                                
                                # Complete progress
                                progress_bar.progress(100)
                                status_text.write(f"✅ Vídeo dividido em {len(timestamps)+1} segmentos com sucesso!")
                                
                            except Exception as e:
                                st.error(f"Erro ao dividir vídeo: {str(e)}")
                                progress_bar.progress(0)
                        else:
                            st.error("Nenhum marcador de tempo válido fornecido.")
                    except ValueError:
                        st.error("Por favor, digite marcadores de tempo numéricos válidos.")
        
        # Display the segments
        if st.session_state.segments:
            st.markdown("""
            <div style="margin:30px 0 20px 0;">
                <h3 style="color:#1e3a8a; font-size:22px; font-weight:600; margin-bottom:8px;">
                    🎬 Segmentos de Vídeo Gerados
                </h3>
                <p style="color:#4a5568; font-size:15px; margin-top:0;">
                    Seus vídeos foram divididos com legendas sincronizadas para cada parte
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a subtitle banner
            st.markdown("""
            <div style="margin-bottom:20px; padding:12px 15px; background-color:#f7f9fc; border-radius:8px; display:flex; align-items:center; justify-content:space-between;">
                <div style="font-weight:500; color:#4a5568;">Visualize, reproduza e baixe os segmentos de vídeo abaixo</div>
                <div style="color:#4287f5; font-size:14px;">Cada segmento inclui legendas sincronizadas</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Small ad between segments header and content
            display_ad(
                ad_type="segment-header", 
                slot_id=ADSENSE_SLOTS.get("banner", ADSENSE_SLOTS["banner"]), 
                client_id=ADSENSE_CLIENT_ID,
                width=728, 
                height=90
            )
            
            # Create better visual segments display
            for i, segment in enumerate(st.session_state.segments):
                # Display segment information
                segment_start = segment['start_time']
                segment_end = segment['end_time']
                segment_duration = segment_end - segment_start
                
                # Format times for display
                start_min = int(segment_start // 60)
                start_sec = int(segment_start % 60)
                end_min = int(segment_end // 60)
                end_sec = int(segment_end % 60)
                
                # Create a card-like container for each segment
                st.markdown(f"""
                <div style="margin:25px 0; padding:15px; background-color:white; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    <div style="display:flex; align-items:center; margin-bottom:12px;">
                        <div style="background-color:#4287f5; color:white; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; margin-right:12px;">
                            {i+1}
                        </div>
                        <div>
                            <h4 style="margin:0 0 5px 0; color:#1e3a8a; font-size:18px; font-weight:600;">Segmento {i+1}</h4>
                            <div style="color:#718096; font-size:14px;">
                                De {start_min}m{start_sec}s até {end_min}m{end_sec}s
                                <span style="margin-left:10px; padding:3px 8px; background-color:#e6f7ff; border-radius:4px; font-size:12px; color:#4287f5;">
                                    Duração: {int(segment_duration//60)}m{int(segment_duration%60)}s
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Create columns for video and controls
                vid_col, info_col = st.columns([2, 1])
                
                with vid_col:
                    # Display video preview with nice styling
                    st.markdown("<div style='padding:5px; border-radius:8px; background-color:#f0f6ff;'>", unsafe_allow_html=True)
                    st.video(segment['video_path'])
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with info_col:
                    # Read subtitle content for information
                    with open(segment['subtitle_path'], 'r', encoding='utf-8', errors='replace') as f:
                        subtitle_content = f.read()
                    
                    # Count number of subtitle entries
                    subtitle_count = subtitle_content.count('\n\n') + 1
                    
                    # Create an information card
                    st.markdown(f"""
                    <div style="background-color:#f7f9fc; padding:15px; border-radius:8px; height:100%; border:1px solid #e0e8f5;">
                        <h4 style="color:#4287f5; font-size:16px; margin-bottom:15px; font-weight:600;">Informações do Segmento</h4>
                        <div style="margin-bottom:10px;">
                            <div style="font-size:13px; color:#718096; margin-bottom:2px;">Legendas sincronizadas:</div>
                            <div style="font-weight:500; color:#2d3748;">{subtitle_count} frases</div>
                        </div>
                        <div style="margin-bottom:10px;">
                            <div style="font-size:13px; color:#718096; margin-bottom:2px;">Formato:</div>
                            <div style="font-weight:500; color:#2d3748;">MP4 + SRT</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Subtitle and download options
                st.markdown("<div style='margin-top:15px;'>", unsafe_allow_html=True)
                
                # Create tabs for actions
                segment_tabs = st.tabs(["⬇️ Baixar", "📝 Ver Legendas"])
                
                with segment_tabs[0]:
                    # Download buttons with better styling
                    download_col1, download_col2 = st.columns(2)
                    
                    with download_col1:
                        st.download_button(
                            label="📹 Baixar Vídeo",
                            data=open(segment['video_path'], 'rb'),
                            file_name=f"segmento_{i+1}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                    
                    with download_col2:
                        st.download_button(
                            label="📄 Baixar Legendas",
                            data=open(segment['subtitle_path'], 'r', encoding='utf-8', errors='replace'),
                            file_name=f"segmento_{i+1}_legendas.srt",
                            mime="text/plain",
                            use_container_width=True
                        )
                
                with segment_tabs[1]:
                    # Parse SRT for cleaner preview
                    import re
                    # Remove timing info for preview
                    preview_text = re.sub(r'\d+\s+\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s+', '', subtitle_content)
                    # Remove numbers
                    preview_text = re.sub(r'^\d+$', '', preview_text, flags=re.MULTILINE)
                    # Clean up extra whitespace
                    preview_text = re.sub(r'\n\s*\n', '\n\n', preview_text)
                    
                    # Show subtitles in a nice container
                    st.markdown(f"""
                    <div style="max-height:200px; overflow-y:auto; padding:15px; background-color:#f7f9fc; 
                         border-radius:8px; border:1px solid #e0e8f5; font-size:14px; line-height:1.6;">
                        {preview_text}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add a separator between segments except for the last one
                if i < len(st.session_state.segments) - 1:
                    # Insert a small ad after every second segment
                    if (i + 1) % 2 == 0:
                        st.markdown("<div style='margin:30px 0; text-align:center;'>", unsafe_allow_html=True)
                        display_ad(
                            ad_type="between-segments", 
                            slot_id=ADSENSE_SLOTS.get("display", ADSENSE_SLOTS["banner"]), 
                            client_id=ADSENSE_CLIENT_ID,
                            width=300, 
                            height=250
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<hr style='margin:30px 0; border:none; height:1px; background-color:#e0e8f5;'>", unsafe_allow_html=True)
    else:
        st.info("👆 Por favor, envie e transcreva um vídeo primeiro na aba 'Enviar e Transcrever'.")

# Tab 3: Download
with tabs[2]:
    if st.session_state.processing_complete:
        st.markdown("""
        <div style="margin-bottom:25px;">
            <h3 style="color:#1e3a8a; font-size:22px; font-weight:600; margin-bottom:8px;">
                ⬇️ Opções de Download
            </h3>
            <p style="color:#4a5568; font-size:15px; margin-top:0;">
                Baixe seu vídeo e legendas em diversos formatos
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a more attractive UI layout
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_left:
            # Affiliate ad on the left with better styling
            st.markdown("""
            <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-bottom:20px;">
                <h4 style="color:#4287f5; font-size:16px; margin-bottom:10px; font-weight:600;">Produtos Recomendados</h4>
            </div>
            """, unsafe_allow_html=True)
            
            display_affiliate_ad(
                product_name="Microfone para Vídeos",
                product_url=AFFILIATE_LINKS["microphone"],
                image_url=AFFILIATE_IMAGES["microphone"],
                width=250,
                height=250,
                description="Melhore a qualidade do áudio dos seus vídeos com este microfone profissional"
            )
            
            # Add a second affiliate product
            st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
            display_affiliate_ad(
                product_name="Tripé para Câmera",
                product_url=AFFILIATE_LINKS.get("tripod", AFFILIATE_LINKS["microphone"]),
                image_url=AFFILIATE_IMAGES.get("tripod", AFFILIATE_IMAGES["microphone"]),
                width=250,
                height=250,
                description="Estabilize suas filmagens com este tripé versátil"
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_right:
            # Ad on the right with better styling
            st.markdown("""
            <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-bottom:20px;">
                <h4 style="color:#4287f5; font-size:16px; margin-bottom:10px; font-weight:600;">Ferramentas Recomendadas</h4>
            </div>
            """, unsafe_allow_html=True)
            
            display_ad(
                ad_type="display", 
                slot_id=ADSENSE_SLOTS.get("display", ADSENSE_SLOTS["banner"]), 
                client_id=ADSENSE_CLIENT_ID,
                width=250, 
                height=250
            )
            
            # Show video tools as affiliate ads
            st.markdown("<div style='margin-top:25px;'>", unsafe_allow_html=True)
            show_video_tools_ads()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_center:
            # Create a better visual for download options
            st.markdown("""
            <div style="background-color:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-bottom:25px;">
                <h4 style="color:#1e3a8a; font-size:18px; margin-bottom:15px; font-weight:600;">
                    <span style="margin-right:8px;">📁</span> Arquivos para Download
                </h4>
                <p style="color:#718096; font-size:14px; margin-bottom:20px;">
                    Todos os arquivos são processados localmente e ficam disponíveis apenas durante esta sessão
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create a card for video download
            st.markdown("""
            <div style="margin-bottom:20px; padding:20px; background-color:#f0f6ff; border-radius:10px; border-left:4px solid #4287f5;">
                <div style="display:flex; align-items:center; margin-bottom:15px;">
                    <div style="font-size:24px; margin-right:15px;">🎬</div>
                    <div>
                        <h5 style="margin:0 0 5px 0; color:#1e3a8a; font-size:16px; font-weight:600;">Vídeo Original</h5>
                        <div style="color:#718096; font-size:13px;">Arquivo MP4 sem alterações</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Safely get the video filename
            video_filename = "video_original.mp4"
            video_path = st.session_state.get("video_path", "")
            
            if video_path and os.path.exists(video_path):
                video_filename = os.path.basename(video_path)
                
                # Add download button for the original video
                with open(video_path, 'rb') as f:
                    st.download_button(
                        label="💾 Baixar Vídeo Original",
                        data=f,
                        file_name=video_filename,
                        mime="video/mp4",
                        use_container_width=True
                    )
            else:
                st.warning("Arquivo de vídeo não disponível.")
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close video card
            
            # Create a card for subtitles download
            st.markdown("""
            <div style="margin-bottom:20px; padding:20px; background-color:#f0f9ff; border-radius:10px; border-left:4px solid #38b2ac;">
                <div style="display:flex; align-items:center; margin-bottom:15px;">
                    <div style="font-size:24px; margin-right:15px;">📝</div>
                    <div>
                        <h5 style="margin:0 0 5px 0; color:#1e3a8a; font-size:16px; font-weight:600;">Legendas (SRT)</h5>
                        <div style="color:#718096; font-size:13px;">Arquivo de legendas formato padrão SRT</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Add download button for the subtitles
            subtitle_path = st.session_state.get("subtitle_path", "")
            
            if subtitle_path and os.path.exists(subtitle_path):
                try:
                    with open(subtitle_path, 'r', encoding='utf-8', errors='replace') as f:
                        subtitle_data = f.read()
                        st.download_button(
                            label="💾 Baixar Legendas SRT",
                            data=subtitle_data,
                            file_name="legendas_completas.srt",
                            mime="text/plain",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Erro ao carregar legendas: {str(e)}")
                    subtitle_data = ""
            else:
                st.warning("Arquivo de legendas não disponível.")
                subtitle_data = ""
            
            # Subtitle preview
            if len(subtitle_data) > 500:
                subtitle_preview = subtitle_data[:500] + "..."
            else:
                subtitle_preview = subtitle_data
            
            # Tratar a substituição de quebras de linha antes do f-string    
            subtitle_preview_html = subtitle_preview.replace('\n', '<br>')
            
            st.markdown(f"""
            <div style="margin-top:10px; background-color:white; padding:10px; border-radius:6px; max-height:100px; overflow-y:auto; font-size:12px; font-family:monospace; color:#4a5568;">
                {subtitle_preview_html}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close subtitles card
            
            # Create a card for embedded subtitles
            st.markdown("""
            <div style="margin-bottom:20px; padding:20px; background-color:#f0f6f9; border-radius:10px; border-left:4px solid #805ad5;">
                <div style="display:flex; align-items:center; margin-bottom:15px;">
                    <div style="font-size:24px; margin-right:15px;">🎞️</div>
                    <div>
                        <h5 style="margin:0 0 5px 0; color:#1e3a8a; font-size:16px; font-weight:600;">Vídeo com Legendas Embutidas</h5>
                        <div style="color:#718096; font-size:13px;">Arquivo MP4 com legendas permanentes</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Opções de qualidade de vídeo para legendas incorporadas
            st.write("#### Configurações de Saída")
            subtitle_quality = st.select_slider(
                "Qualidade do vídeo com legendas:",
                options=["low", "medium", "high"],
                value="medium",
                format_func=lambda x: {
                    "low": "Baixa (mais rápido)",
                    "medium": "Média (equilibrado)",
                    "high": "Alta (qualidade máxima)"
                }.get(x, x)
            )
            
            st.markdown(f"""
            <div style="margin:10px 0; padding:8px; border-radius:5px; background-color:{
                {"low": "#fff3e0", "medium": "#e8f5e9", "high": "#e3f2fd"}.get(subtitle_quality, "#f5f5f5")
            };">
                <p style="margin:0; font-size:13px;">
                    {
                        {
                            "low": "⚡ Processamento mais rápido, arquivo menor, qualidade reduzida",
                            "medium": "⚖️ Bom equilíbrio entre velocidade e qualidade",
                            "high": "🔍 Máxima qualidade, processamento mais lento, arquivo maior"
                        }.get(subtitle_quality)
                    }
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a button to create a video with embedded subtitles
            if st.button("🔄 Gerar Vídeo com Legendas Embutidas", use_container_width=True):
                # Create a styled container for the processing
                process_container = st.container()
                with process_container:
                    st.markdown("""
                    <div style="padding:15px; background-color:white; border-radius:8px; margin:10px 0; border:1px solid #e0e8f5;">
                        <h4 style="color:#4287f5; font-size:16px; margin-bottom:10px; font-weight:600;">
                            Processando Vídeo
                        </h4>
                    """, unsafe_allow_html=True)
                    
                    # Show progress
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    progress_text.write("🔄 Iniciando processamento...")
                    progress_bar.progress(10)
                    
                    # Define output path
                    output_video_path = os.path.join(st.session_state.temp_dir, "embedded_video.mp4")
                    
                    try:
                        # Update progress
                        progress_text.write("⚙️ Incorporando legendas no vídeo...")
                        progress_bar.progress(30)
                        
                        # Embed subtitles into the video with the selected quality
                        video_processor = VideoProcessor()
                        output_path = video_processor.embed_subtitles(
                            st.session_state.video_path,
                            st.session_state.subtitle_path,
                            output_video_path,
                            quality=subtitle_quality
                        )
                        
                        st.session_state.embedded_video_path = output_path
                        
                        # Update progress
                        progress_bar.progress(90)
                        
                        # Show success message
                        progress_text.write("✅ Legendas incorporadas com sucesso!")
                        progress_bar.progress(100)
                        
                        st.markdown("</div>", unsafe_allow_html=True)  # Close processing container
                        
                        # Preview the video with better styling
                        st.markdown("""
                        <div style="margin:20px 0 15px 0;">
                            <h5 style="color:#1e3a8a; font-size:16px; margin-bottom:10px; font-weight:600;">
                                Prévia do Vídeo com Legendas
                            </h5>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.video(output_path)
                        
                        # Add download button with better styling
                        st.markdown("""
                        <div style="margin:15px 0 10px 0;">
                            <h5 style="color:#1e3a8a; font-size:16px; margin-bottom:10px; font-weight:600;">
                                Download Disponível
                            </h5>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with open(output_path, 'rb') as f:
                            st.download_button(
                                label="💾 Baixar Vídeo com Legendas Embutidas",
                                data=f,
                                file_name="video_com_legendas.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    except Exception as e:
                        st.error(f"Erro ao incorporar legendas: {str(e)}")
                        progress_bar.progress(0)
                        st.markdown("</div>", unsafe_allow_html=True)  # Close processing container
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close embedded subtitles card
            
            # If there are segments, show them too
            if st.session_state.segments:
                st.markdown("""
                <div style="margin:30px 0 20px 0;">
                    <h4 style="color:#1e3a8a; font-size:18px; margin-bottom:10px; font-weight:600;">
                        <span style="margin-right:8px;">✂️</span> Segmentos de Vídeo
                    </h4>
                    <p style="color:#718096; font-size:14px; margin-bottom:15px;">
                        Baixe os segmentos de vídeo que você criou anteriormente
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a list of segments in cards
                for i, segment in enumerate(st.session_state.segments):
                    st.markdown(f"""
                    <div style="margin-bottom:15px; padding:15px; background-color:#f9f9fd; border-radius:10px; border-left:4px solid #7f9cf5;">
                        <div style="display:flex; align-items:center; margin-bottom:10px;">
                            <div style="background-color:#7f9cf5; color:white; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; margin-right:12px;">
                                {i+1}
                            </div>
                            <div>
                                <h5 style="margin:0; color:#1e3a8a; font-size:16px; font-weight:600;">Segmento {i+1}</h5>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create columns for different download options
                    download_col1, download_col2 = st.columns(2)
                    
                    with download_col1:
                        with open(segment['video_path'], 'rb') as f:
                            st.download_button(
                                label=f"📹 Vídeo Segmento {i+1}",
                                data=f,
                                file_name=f"segmento_{i+1}.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    with download_col2:
                        with open(segment['subtitle_path'], 'r') as f:
                            st.download_button(
                                label=f"📄 Legendas Segmento {i+1}",
                                data=f,
                                file_name=f"segmento_{i+1}.srt",
                                mime="text/plain",
                                use_container_width=True
                            )
                    
                    # Add a button for embedded subtitles but in a more elegant way
                    segment_id = f"segment_{i+1}"
                    segment_button_key = f"embed_button_{segment_id}"
                    
                    # Layout melhorado para qualidade de vídeo
                    quality_cols = st.columns([2, 3])
                    
                    with quality_cols[0]:
                        # Qualidade de vídeo para este segmento
                        segment_quality = st.select_slider(
                            f"Qualidade - Segmento {i+1}:",
                            options=["low", "medium", "high"],
                            value="medium",
                            key=f"segment_quality_{i}",
                            format_func=lambda x: {
                                "low": "Baixa",
                                "medium": "Média",
                                "high": "Alta"
                            }.get(x, x)
                        )
                    
                    with quality_cols[1]:
                        # Ícone e descrição mais compactos
                        st.info({
                            "low": "⚡ Rápido, menor tamanho",
                            "medium": "⚖️ Equilibrado",
                            "high": "🔍 Alta qualidade, maior arquivo"
                        }.get(segment_quality))
                    
                    if st.button(f"🔄 Gerar Segmento {i+1} com Legendas Embutidas", key=segment_button_key, use_container_width=True):
                        segment_process_container = st.container()
                        with segment_process_container:
                            st.markdown(f"""
                            <div style="padding:15px; background-color:white; border-radius:8px; margin:10px 0; border:1px solid #e0e8f5;">
                                <h4 style="color:#4287f5; font-size:16px; margin-bottom:10px; font-weight:600;">
                                    Processando Segmento {i+1}
                                </h4>
                            """, unsafe_allow_html=True)
                            
                            segment_progress_text = st.empty()
                            segment_progress_bar = st.progress(0)
                            
                            segment_progress_text.write("🔄 Iniciando processamento...")
                            segment_progress_bar.progress(10)
                            
                            try:
                                segment_progress_text.write(f"⚙️ Incorporando legendas no segmento {i+1}...")
                                segment_progress_bar.progress(30)
                                
                                # Define output path for this segment
                                embedded_segment_path = os.path.join(st.session_state.temp_dir, f"embedded_segment_{i+1}.mp4")
                                
                                # Embed subtitles into the segment with selected quality
                                video_processor = VideoProcessor()
                                output_segment_path = video_processor.embed_subtitles(
                                    segment['video_path'],
                                    segment['subtitle_path'],
                                    embedded_segment_path,
                                    quality=segment_quality
                                )
                                
                                # Store the path for later
                                segment['embedded_path'] = output_segment_path
                                
                                segment_progress_bar.progress(90)
                                segment_progress_text.write(f"✅ Legendas incorporadas no segmento {i+1} com sucesso!")
                                segment_progress_bar.progress(100)
                                
                                st.markdown("</div>", unsafe_allow_html=True)  # Close processing container
                                
                                # Preview
                                st.video(output_segment_path)
                                
                                # Download button
                                with open(output_segment_path, 'rb') as f:
                                    st.download_button(
                                        label=f"💾 Baixar Segmento {i+1} com Legendas",
                                        data=f,
                                        file_name=f"segmento_{i+1}_com_legendas.mp4",
                                        mime="video/mp4",
                                        use_container_width=True
                                    )
                                
                            except Exception as e:
                                st.error(f"Erro ao incorporar legendas no segmento {i+1}: {str(e)}")
                                segment_progress_bar.progress(0)
                                st.markdown("</div>", unsafe_allow_html=True)  # Close processing container
        
        # Display a nice banner ad
        st.markdown("<div style='margin:30px 0; text-align:center;'>", unsafe_allow_html=True)
        display_ad(
            ad_type="banner", 
            slot_id=ADSENSE_SLOTS.get("leaderboard", ADSENSE_SLOTS["banner"]), 
            client_id=ADSENSE_CLIENT_ID,
            width=728, 
            height=90
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display support message with better styling
        st.markdown("""
        <div style="margin:30px 0; padding:20px; background-color:#f7f9fc; border-radius:10px; text-align:center; border:1px solid #e0e8f5;">
            <h4 style="color:#1e3a8a; font-size:18px; margin-bottom:15px; font-weight:600;">
                ❤️ Gostou da ferramenta?
            </h4>
            <p style="color:#4a5568; font-size:15px; margin-bottom:20px; max-width:600px; margin-left:auto; margin-right:auto;">
                Esta aplicação é gratuita e mantida por mim. Se ela foi útil para você, considere fazer uma pequena doação para
                ajudar a mantê-la online e continuar melhorando!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Three column layout for support options
        support_col1, support_col2, support_col3 = st.columns(3)
        
        with support_col1:
            st.markdown("""
            <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); text-align:center; height:100%;">
                <div style="font-size:28px; margin-bottom:10px;">☕</div>
                <h5 style="color:#1e3a8a; font-size:16px; margin-bottom:10px; font-weight:600;">
                    Pague um café
                </h5>
                <p style="color:#718096; font-size:14px; margin-bottom:15px;">
                    Qualquer quantia é bem-vinda!
                </p>
                <a href="https://www.buymeacoffee.com/exemplo" target="_blank" style="display:inline-block; background-color:#FFDD00; color:#000000; font-weight:600; padding:8px 16px; border-radius:4px; text-decoration:none; font-size:14px;">
                    Doar
                </a>
            </div>
            """, unsafe_allow_html=True)
            
        with support_col2:
            st.markdown("""
            <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); text-align:center; height:100%;">
                <div style="font-size:28px; margin-bottom:10px;">⭐</div>
                <h5 style="color:#1e3a8a; font-size:16px; margin-bottom:10px; font-weight:600;">
                    Compartilhe
                </h5>
                <p style="color:#718096; font-size:14px; margin-bottom:15px;">
                    Indique para amigos!
                </p>
                <div style="display:flex; justify-content:center; gap:10px;">
                    <a href="https://twitter.com/intent/tweet?text=Ferramenta%20incr%C3%ADvel%20para%20transcrever%20v%C3%ADdeos!" target="_blank" style="display:inline-block; background-color:#1DA1F2; color:white; font-weight:600; padding:8px 16px; border-radius:4px; text-decoration:none; font-size:14px;">
                        Twitter
                    </a>
                    <a href="https://www.facebook.com/sharer/sharer.php?u=https://example.com" target="_blank" style="display:inline-block; background-color:#4267B2; color:white; font-weight:600; padding:8px 16px; border-radius:4px; text-decoration:none; font-size:14px;">
                        Facebook
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with support_col3:
            st.markdown("""
            <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); text-align:center; height:100%;">
                <div style="font-size:28px; margin-bottom:10px;">📧</div>
                <h5 style="color:#1e3a8a; font-size:16px; margin-bottom:10px; font-weight:600;">
                    Contato
                </h5>
                <p style="color:#718096; font-size:14px; margin-bottom:15px;">
                    Dúvidas ou sugestões?
                </p>
                <a href="mailto:contato@exemplo.com" style="display:inline-block; background-color:#805AD5; color:white; font-weight:600; padding:8px 16px; border-radius:4px; text-decoration:none; font-size:14px;">
                    Enviar Email
                </a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Por favor, envie e transcreva um vídeo primeiro.")

# Add video tools ads before footer
show_video_tools_ads()

# Bottom banner ad
st.markdown("<div style='margin:30px 0;'></div>", unsafe_allow_html=True)  # Add space before ad
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    display_ad(
        ad_type="leaderboard", 
        slot_id=ADSENSE_SLOTS["leaderboard"], 
        client_id=ADSENSE_CLIENT_ID,
        width=728, 
        height=90
    )

# Add footer
st.markdown("---")
st.markdown("Aplicativo de Transcrição e Divisão de Vídeos - Desenvolvido com Streamlit, Whisper e FFmpeg")

# Display a small privacy and ad notice
st.markdown("""
<div style="font-size:11px; color:#666; text-align:center; margin-top:20px;">
    Este site usa cookies e contém anúncios para ajudar a manter seu funcionamento gratuito.
    Ao usar este site, você concorda com nossa <a href="#">Política de Privacidade</a>.
</div>
""", unsafe_allow_html=True)
