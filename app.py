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
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("📥 Baixar e Processar", 
                            help="Baixa o vídeo do YouTube e prepara para transcrição",
                            use_container_width=True):
                    try:
                        with st.spinner("🔄 Baixando vídeo do YouTube..."):
                            # Download the YouTube video
                            video_processor = VideoProcessor()
                            st.session_state.video_path = video_processor.download_youtube_video(youtube_url, st.session_state.temp_dir)
                            
                        st.success("✅ Vídeo baixado com sucesso! Pronto para transcrever.")
                    except Exception as e:
                        st.error(f"❌ Erro ao baixar vídeo: {str(e)}")
    
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
            </div>
            """, unsafe_allow_html=True)
        
        # Transcribe button section
        if 'transcription_started' not in st.session_state:
            st.session_state.transcription_started = False
            
        if 'transcription_complete' not in st.session_state:
            st.session_state.transcription_complete = False
        
        # Elegante botão de transcrição
        st.markdown("<div style='margin:25px 0;'>", unsafe_allow_html=True)
        
        # Check if we should start transcription
        transcribe_col1, transcribe_col2, transcribe_col3 = st.columns([1, 2, 1])
        with transcribe_col2:
            if st.button("🔊 Iniciar Transcrição com IA", 
                        help="Utiliza o modelo Whisper para transcrever o áudio em texto",
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
                    
                    # Start or continue transcription
                    transcription_status = subtitle_processor.transcribe_video_async(
                        st.session_state.video_path, 
                        output_srt_path
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
                        
                        # Show estimated time
                        duration = video_processor.get_video_duration(st.session_state.video_path)
                        est_time = max(1, int(duration * 0.3))  # Rough estimate: 1/3 of video length
                        
                        st.info(f"⏱️ Transcrição em andamento. Tempo estimado: cerca de {est_time} minutos para um vídeo de {int(duration // 60)} minutos.")
                        
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
                    
                    # Split the video
                    st.session_state.segments = video_processor.split_video_equal_parts(
                        st.session_state.video_path,
                        st.session_state.subtitle_path,
                        num_parts,
                        st.session_state.temp_dir
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
                                
                                # Split the video
                                st.session_state.segments = video_processor.split_video_custom_timestamps(
                                    st.session_state.video_path,
                                    st.session_state.subtitle_path,
                                    timestamps,
                                    st.session_state.temp_dir
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
            st.write("### Segmentos de Vídeo Gerados")
            
            # Create columns for each segment
            cols = st.columns(min(3, len(st.session_state.segments)))
            
            for i, segment in enumerate(st.session_state.segments):
                col_index = i % 3
                
                with cols[col_index]:
                    st.write(f"**Segmento {i+1}**")
                    
                    # Display segment information
                    segment_start = segment['start_time']
                    segment_end = segment['end_time']
                    segment_duration = segment_end - segment_start
                    
                    # Format times for display
                    start_min = int(segment_start // 60)
                    start_sec = int(segment_start % 60)
                    end_min = int(segment_end // 60)
                    end_sec = int(segment_end % 60)
                    
                    st.write(f"Tempo: {start_min}m{start_sec}s até {end_min}m{end_sec}s")
                    st.write(f"Duração: {segment_duration:.1f}s")
                    
                    # Display video preview
                    st.video(segment['video_path'])
                    
                    # Create expander for subtitles
                    with st.expander("Ver Legendas Sincronizadas"):
                        # Read subtitle content
                        with open(segment['subtitle_path'], 'r', encoding='utf-8', errors='replace') as f:
                            subtitle_content = f.read()
                        
                        # Count number of subtitle entries
                        subtitle_count = subtitle_content.count('\n\n') + 1
                        
                        # Add informative header
                        st.write(f"**{subtitle_count} legendas sincronizadas com este segmento**")
                        st.write("As legendas abaixo foram ajustadas para sincronizar com este segmento de vídeo.")
                        
                        # Show subtitle content
                        st.text_area(f"Legendas do Segmento {i+1}", subtitle_content, height=150)
                        
                        # Add download button for this segment's subtitles
                        with open(segment['subtitle_path'], 'r') as f:
                            st.download_button(
                                label=f"Baixar legendas do Segmento {i+1}",
                                data=f,
                                file_name=f"segmento_{i+1}.srt",
                                mime="text/plain"
                            )
    else:
        st.info("👆 Por favor, envie e transcreva um vídeo primeiro na aba 'Enviar e Transcrever'.")

# Tab 3: Download
with tabs[2]:
    if st.session_state.processing_complete:
        st.write("### Opções de Download")
        
        # Sidebar ad
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_left:
            # Affiliate ad on the left
            display_affiliate_ad(
                product_name="Microfone para Vídeos",
                product_url=AFFILIATE_LINKS["microphone"],
                image_url=AFFILIATE_IMAGES["microphone"],
                width=250,
                height=250
            )
        
        with col_right:
            # Ad on the right
            display_ad(
                ad_type="display", 
                slot_id=ADSENSE_SLOTS["display"], 
                client_id=ADSENSE_CLIENT_ID,
                width=250, 
                height=250
            )
        
        with col_center:
            # Download full video with subtitles
            st.write("#### Vídeo Completo")
        
        # Safely get the video filename
        video_filename = "video_original.mp4"
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            video_filename = os.path.basename(st.session_state.video_path)
            
        create_download_link(
            st.session_state.video_path,
            "Baixar Vídeo Original",
            video_filename
        )
        
        if st.session_state.subtitle_path:
            with open(st.session_state.subtitle_path, 'r') as f:
                st.download_button(
                    label="Baixar Legendas Completas (SRT)",
                    data=f,
                    file_name="legendas_completas.srt",
                    mime="text/plain"
                )
        
        # Add option to download video with embedded subtitles
        if st.button("Criar Vídeo com Legendas Incorporadas"):
            with st.spinner("Incorporando legendas no vídeo..."):
                video_processor = VideoProcessor()
                embedded_video_path = video_processor.embed_subtitles(
                    st.session_state.video_path,
                    st.session_state.subtitle_path,
                    os.path.join(st.session_state.temp_dir, "embedded_video.mp4")
                )
                
                st.session_state.embedded_video_path = embedded_video_path
                
            st.success("Legendas incorporadas com sucesso!")
            
            create_download_link(
                st.session_state.embedded_video_path,
                "Baixar Vídeo com Legendas Incorporadas",
                "video_com_legendas.mp4"
            )
        
        # Download segments
        if st.session_state.segments:
            st.write("#### Segmentos de Vídeo")
            
            for i, segment in enumerate(st.session_state.segments):
                st.write(f"**Segmento {i+1}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    create_download_link(
                        segment['video_path'],
                        f"Baixar Vídeo do Segmento {i+1}",
                        f"segmento_{i+1}.mp4"
                    )
                
                with col2:
                    with open(segment['subtitle_path'], 'r') as f:
                        st.download_button(
                            label=f"Baixar Legendas do Segmento {i+1}",
                            data=f,
                            file_name=f"segmento_{i+1}.srt",
                            mime="text/plain"
                        )
                
                # Add option to download segment with embedded subtitles
                if st.button(f"Criar Segmento {i+1} com Legendas Incorporadas"):
                    with st.spinner(f"Incorporando legendas no segmento {i+1}..."):
                        video_processor = VideoProcessor()
                        embedded_segment_path = video_processor.embed_subtitles(
                            segment['video_path'],
                            segment['subtitle_path'],
                            os.path.join(st.session_state.temp_dir, f"embedded_segment_{i+1}.mp4")
                        )
                        
                        segment['embedded_path'] = embedded_segment_path
                        
                    st.success(f"Legendas incorporadas no segmento {i+1} com sucesso!")
                    
                    create_download_link(
                        segment['embedded_path'],
                        f"Baixar Segmento {i+1} com Legendas Incorporadas",
                        f"segmento_{i+1}_com_legendas.mp4"
                    )
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
