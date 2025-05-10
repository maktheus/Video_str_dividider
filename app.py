import streamlit as st
import os
import tempfile
import time
from video_processor import VideoProcessor
from subtitle_processor import SubtitleProcessor
from utils import save_uploaded_file, create_download_link

# Set page configuration
st.set_page_config(
    page_title="Transcrição e Divisão de Vídeos",
    page_icon="🎬",
    layout="wide",
)

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

# Create title and description
st.title("Transcrição e Divisão de Vídeos")
st.write("Envie um vídeo para transcrevê-lo com Whisper, dividi-lo em partes e baixá-lo com legendas sincronizadas.")

# Create tabs for different stages of the process
tabs = st.tabs(["Enviar e Transcrever", "Dividir Vídeo", "Baixar"])

# Tab 1: Upload and Transcribe
with tabs[0]:
    # File upload
    uploaded_file = st.file_uploader("Envie seu arquivo de vídeo", type=["mp4", "avi", "mov", "mkv"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        if st.session_state.video_path is None:
            st.session_state.video_path = save_uploaded_file(uploaded_file, st.session_state.temp_dir)
            st.success(f"Vídeo enviado com sucesso!")
        
        # Display the uploaded video
        st.video(st.session_state.video_path)
        
        # Transcribe button
        if st.button("Transcrever com Whisper"):
            with st.spinner("Transcrevendo vídeo..."):
                # Initialize the subtitle processor
                subtitle_processor = SubtitleProcessor()
                
                # Transcribe the video
                st.session_state.subtitle_path = subtitle_processor.transcribe_video(
                    st.session_state.video_path, 
                    os.path.join(st.session_state.temp_dir, "subtitles.srt")
                )
                
                # Set the processing complete flag
                st.session_state.processing_complete = True
                
            st.success("Transcrição concluída!")
            
            # Display the subtitles
            if st.session_state.subtitle_path:
                with open(st.session_state.subtitle_path, 'r') as f:
                    st.download_button(
                        label="Baixar arquivo SRT",
                        data=f,
                        file_name="legendas.srt",
                        mime="text/plain"
                    )
                
                with open(st.session_state.subtitle_path, 'r') as f:
                    st.text_area("Legendas Geradas (formato SRT)", f.read(), height=300)

# Tab 2: Split Video
with tabs[1]:
    if st.session_state.processing_complete:
        st.write("Especifique como dividir o vídeo:")
        
        # Option for splitting method
        split_method = st.radio(
            "Escolha o método de divisão:",
            ["Partes iguais", "Marcadores de tempo personalizados"]
        )
        
        video_processor = VideoProcessor()
        duration = video_processor.get_video_duration(st.session_state.video_path)
        
        if split_method == "Partes iguais":
            num_parts = st.number_input("Número de partes", min_value=2, max_value=20, value=2)
            
            if st.button("Dividir Vídeo"):
                with st.spinner(f"Dividindo vídeo em {num_parts} partes iguais..."):
                    # Clear previous segments
                    st.session_state.segments = []
                    
                    # Split the video and subtitles
                    st.session_state.segments = video_processor.split_video_equal_parts(
                        st.session_state.video_path,
                        st.session_state.subtitle_path,
                        num_parts,
                        st.session_state.temp_dir
                    )
                
                st.success(f"Vídeo dividido em {num_parts} partes com sucesso!")
        
        else:  # Custom timestamps
            st.write(f"Duração do vídeo: {duration:.2f} segundos")
            
            # Allow user to specify timestamps
            timestamps_str = st.text_area(
                "Digite os marcadores de tempo (em segundos, um por linha):",
                help="Por exemplo:\n30\n120\n180"
            )
            
            if st.button("Dividir Vídeo"):
                if timestamps_str:
                    try:
                        timestamps = [float(ts.strip()) for ts in timestamps_str.split('\n') if ts.strip()]
                        timestamps = sorted([ts for ts in timestamps if 0 < ts < duration])
                        
                        if timestamps:
                            with st.spinner(f"Dividindo vídeo nos marcadores de tempo personalizados..."):
                                # Clear previous segments
                                st.session_state.segments = []
                                
                                # Split the video and subtitles
                                st.session_state.segments = video_processor.split_video_custom_timestamps(
                                    st.session_state.video_path,
                                    st.session_state.subtitle_path,
                                    timestamps,
                                    st.session_state.temp_dir
                                )
                            
                            st.success(f"Vídeo dividido em {len(timestamps)} pontos com sucesso!")
                        else:
                            st.error("Nenhum marcador de tempo válido fornecido.")
                    except ValueError:
                        st.error("Por favor, digite marcadores de tempo numéricos válidos.")
        
        # Display the segments
        if st.session_state.segments:
            st.write("### Segmentos de Vídeo")
            for i, segment in enumerate(st.session_state.segments):
                with st.expander(f"Segmento {i+1}"):
                    st.video(segment['video_path'])
                    with open(segment['subtitle_path'], 'r') as f:
                        st.text_area(f"Legendas do Segmento {i+1}", f.read(), height=150)
    else:
        st.info("Por favor, envie e transcreva um vídeo primeiro.")

# Tab 3: Download
with tabs[2]:
    if st.session_state.processing_complete:
        st.write("### Opções de Download")
        
        # Download full video with subtitles
        st.write("#### Vídeo Completo")
        
        create_download_link(
            st.session_state.video_path,
            "Baixar Vídeo Original",
            os.path.basename(st.session_state.video_path)
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

# Add footer
st.markdown("---")
st.markdown("Aplicativo de Transcrição e Divisão de Vídeos - Desenvolvido com Streamlit, Whisper e FFmpeg")
