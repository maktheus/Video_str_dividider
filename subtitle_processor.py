import os
import subprocess
import srt
import datetime
import tempfile
import time
import json
import threading
import streamlit as st

class SubtitleProcessor:
    def __init__(self):
        """Initialize the SubtitleProcessor class."""
        # Status file to track transcription progress
        self.status_file = None
        
        # Status structure with default values
        self.default_status = {
            'stage': 'not_started',  # not_started, extracting_audio, transcribing, finishing, complete
            'progress': 0,           # 0-100
            'message': '',
            'complete': False,
            'error': None,
            'result_path': None
        }
    
    def transcribe_video(self, video_path, output_path):
        """Transcribe a video file using Whisper CLI and save as SRT.
        
        Args:
            video_path (str): Path to the video file.
            output_path (str): Path to save the SRT file.
            
        Returns:
            str: Path to the generated SRT file.
        """
        # Create a simple cache file name based on video file name
        video_filename = os.path.basename(video_path)
        
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join(os.path.dirname(output_path), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Define cache file path
        cache_path = os.path.join(cache_dir, f"{video_filename}.srt")
        
        # Check if we have a cached transcription
        if os.path.exists(cache_path):
            st.success("Encontrada transcrição em cache. Usando versão previamente gerada.")
            # Copy cache to output
            with open(cache_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return output_path
        
        # Create progress indicators
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # STEP 1: Extract audio
            progress_text.write("⏳ Etapa 1/3: Extraindo áudio do vídeo...")
            progress_bar.progress(10)
            
            # Extract audio from video to temporary file
            temp_audio_file = os.path.join(os.path.dirname(output_path), f"temp_audio.wav")
            
            # Use ffmpeg command to extract audio
            ffmpeg_cmd = [
                "ffmpeg", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-y", temp_audio_file
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            progress_bar.progress(30)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao extrair áudio: {result.stderr}")
            
            # STEP 2: Transcribe audio
            progress_text.write("⏳ Etapa 2/3: Transcrevendo o áudio (isso pode levar alguns minutos)...")
            progress_bar.progress(40)
            
            # Create directory for Whisper output
            whisper_output_dir = os.path.join(os.path.dirname(output_path), "whisper_output")
            os.makedirs(whisper_output_dir, exist_ok=True)
            
            # Use Whisper CLI to transcribe - using the tiny model for faster transcription
            # Added beam_size=1 and faster options to improve speed
            whisper_cmd = [
                "whisper", temp_audio_file, 
                "--model", "tiny", 
                "--output_format", "srt", 
                "--output_dir", whisper_output_dir,
                "--beam_size", "1",           # Smaller beam size = faster
                "--best_of", "1",             # Fewer samples = faster
                "--condition_on_previous_text", "False", # Less context processing = faster
                "--temperature", "0"          # Deterministic = faster
            ]
            
            st.info("Iniciando transcrição com Whisper (modo rápido). A transcrição agora será muito mais rápida.")
            
            # Run whisper - this will block until complete
            result = subprocess.run(whisper_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro do Whisper: {result.stderr}")
            
            progress_bar.progress(80)
            
            # STEP 3: Process results
            progress_text.write("⏳ Etapa 3/3: Finalizando e salvando as legendas...")
            
            # The output file will be named like the input audio file but with .srt extension
            output_filename = os.path.splitext(os.path.basename(temp_audio_file))[0] + ".srt"
            generated_srt = os.path.join(whisper_output_dir, output_filename)
            
            # Check if output file exists
            if not os.path.exists(generated_srt):
                raise Exception("Arquivo SRT não foi gerado pelo Whisper.")
            
            # Read the file to fix possible encoding issues
            with open(generated_srt, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Save to cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write to the requested output path
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            progress_bar.progress(90)
            
            # Clean up temp files
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
            
            # Complete progress
            progress_bar.progress(100)
            progress_text.write("✅ Transcrição concluída com sucesso!")
            
            return output_path
                
        except Exception as e:
            error_msg = str(e)
            st.error(f"Erro ao transcrever o vídeo: {error_msg}")
            
            # Create a dummy SRT if transcription fails
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("1\n00:00:00,000 --> 00:00:05,000\nErro na transcrição: " + error_msg)
            
            # Clear progress
            progress_bar.progress(0)
            progress_text.write("❌ Ocorreu um erro durante a transcrição.")
            
            return output_path
    
    def transcribe_video_async(self, video_path, output_path):
        """Transcribe a video file using Whisper in a non-blocking way.
        
        Args:
            video_path (str): Path to the video file.
            output_path (str): Path to save the SRT file.
            
        Returns:
            dict: Status information about the transcription process.
        """
        # Create status file path
        status_dir = os.path.dirname(output_path)
        status_filename = f"transcription_status_{os.path.basename(video_path)}.json"
        self.status_file = os.path.join(status_dir, status_filename)
        
        # Check for cached transcription
        video_filename = os.path.basename(video_path)
        cache_dir = os.path.join(os.path.dirname(output_path), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{video_filename}.srt")
        
        # If cached version exists, just return it
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {
                'stage': 'complete',
                'progress': 100,
                'message': "✅ Transcrição encontrada em cache!",
                'complete': True,
                'result_path': output_path
            }
        
        # Check if there's an existing status file - this means transcription is in progress
        # or was completed
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                
                # If transcription is already complete, just return success
                if status['complete']:
                    return status
                
                # Update status message with appropriate text
                if status['stage'] == 'extracting_audio':
                    status['message'] = "⏳ Etapa 1/3: Extraindo áudio do vídeo..."
                elif status['stage'] == 'transcribing':
                    status['message'] = "⏳ Etapa 2/3: Transcrevendo o áudio (isso pode levar alguns minutos)..."
                elif status['stage'] == 'finishing':
                    status['message'] = "⏳ Etapa 3/3: Finalizando e salvando as legendas..."
                
                # Return current status
                return status
                
            except Exception:
                # If there's an error reading the status file, start over
                pass
        
        # Initialize status
        status = self.default_status.copy()
        status['stage'] = 'starting'
        status['message'] = "Iniciando processo de transcrição..."
        self._save_status(status)
        
        # Start transcription in a background thread
        thread = threading.Thread(
            target=self._run_transcription_process, 
            args=(video_path, output_path)
        )
        thread.daemon = True  # Thread will exit when main program exits
        thread.start()
        
        # Return initial status
        return status
    
    def _save_status(self, status):
        """Save transcription status to file."""
        if self.status_file:
            with open(self.status_file, 'w') as f:
                json.dump(status, f)
    
    def _run_transcription_process(self, video_path, output_path):
        """Run the transcription process in a background thread."""
        status = self.default_status.copy()
        
        try:
            # STEP 1: Extract audio
            status['stage'] = 'extracting_audio'
            status['message'] = "⏳ Etapa 1/3: Extraindo áudio do vídeo..."
            status['progress'] = 10
            self._save_status(status)
            
            # Extract audio from video to temporary file
            temp_audio_file = os.path.join(os.path.dirname(output_path), f"temp_audio_{int(time.time())}.wav")
            
            # Use ffmpeg command to extract audio
            ffmpeg_cmd = [
                "ffmpeg", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-y", temp_audio_file
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao extrair áudio: {result.stderr}")
            
            status['progress'] = 30
            self._save_status(status)
            
            # STEP 2: Transcribe audio
            status['stage'] = 'transcribing'
            status['message'] = "⏳ Etapa 2/3: Transcrevendo o áudio (isso pode levar alguns minutos)..."
            status['progress'] = 40
            self._save_status(status)
            
            # Create directory for Whisper output
            whisper_output_dir = os.path.join(os.path.dirname(output_path), "whisper_output")
            os.makedirs(whisper_output_dir, exist_ok=True)
            
            # Use Whisper CLI to transcribe with tiny model and speed optimizations
            whisper_cmd = [
                "whisper", temp_audio_file, 
                "--model", "tiny", 
                "--output_format", "srt", 
                "--output_dir", whisper_output_dir,
                "--beam_size", "1",           # Smaller beam size = faster
                "--best_of", "1",             # Fewer samples = faster
                "--condition_on_previous_text", "False", # Less context processing = faster
                "--temperature", "0"          # Deterministic = faster
            ]
            
            # Update message to reflect faster processing
            status['message'] = "⏳ Etapa 2/3: Transcrevendo o áudio no modo rápido (otimizado para velocidade)..."
            self._save_status(status)
            
            # Run whisper
            result = subprocess.run(whisper_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro do Whisper: {result.stderr}")
            
            status['progress'] = 80
            self._save_status(status)
            
            # STEP 3: Process results
            status['stage'] = 'finishing'
            status['message'] = "⏳ Etapa 3/3: Finalizando e salvando as legendas..."
            self._save_status(status)
            
            # The output file will be named like the input audio file but with .srt extension
            output_filename = os.path.splitext(os.path.basename(temp_audio_file))[0] + ".srt"
            generated_srt = os.path.join(whisper_output_dir, output_filename)
            
            # Check if output file exists
            if not os.path.exists(generated_srt):
                raise Exception("Arquivo SRT não foi gerado pelo Whisper.")
            
            # Read the file to fix possible encoding issues
            with open(generated_srt, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Save to cache
            cache_dir = os.path.join(os.path.dirname(output_path), "cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, f"{os.path.basename(video_path)}.srt")
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write to the requested output path
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            status['progress'] = 90
            self._save_status(status)
            
            # Clean up temp files
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
            
            # Complete status
            status['progress'] = 100
            status['stage'] = 'complete'
            status['message'] = "✅ Transcrição concluída com sucesso!"
            status['complete'] = True
            status['result_path'] = output_path
            self._save_status(status)
            
        except Exception as e:
            error_msg = str(e)
            status['error'] = error_msg
            status['message'] = f"❌ Erro: {error_msg}"
            status['stage'] = 'error'
            self._save_status(status)
            
            # Create a dummy SRT file on error
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("1\n00:00:00,000 --> 00:00:05,000\nErro na transcrição: " + error_msg)
    
    def _parse_srt_file(self, srt_file_path):
        """Parse an SRT file to get subtitle segments.
        
        Args:
            srt_file_path (str): Path to the SRT file.
            
        Returns:
            list: List of srt.Subtitle objects.
        """
        try:
            with open(srt_file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return list(srt.parse(content))
        except Exception as e:
            st.error(f"Erro ao analisar arquivo SRT: {str(e)}")
            return []
    
    def extract_subtitle_segment(self, subtitle_path, output_path, start_time, end_time):
        """Extract a segment from a subtitle file.
        
        Args:
            subtitle_path (str): Path to the subtitle file.
            output_path (str): Path to save the output subtitle segment.
            start_time (float): Start time of the segment in seconds.
            end_time (float): End time of the segment in seconds.
            
        Returns:
            str: Path to the output subtitle segment.
        """
        try:
            # Read the SRT file
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                subtitle_content = f.read()
            
            # Parse the subtitles
            subtitles = list(srt.parse(subtitle_content))
            
            # Filter subtitles within the segment timeframe
            segment_subtitles = []
            
            for subtitle in subtitles:
                # Convert to seconds for comparison
                sub_start_seconds = subtitle.start.total_seconds()
                sub_end_seconds = subtitle.end.total_seconds()
                
                # Check if subtitle is within the segment
                if (sub_end_seconds > start_time and sub_start_seconds < end_time):
                    # Adjust timing relative to the segment start
                    new_start = max(0, sub_start_seconds - start_time)
                    new_end = min(end_time - start_time, sub_end_seconds - start_time)
                    
                    # Create new subtitle with adjusted timing
                    new_subtitle = srt.Subtitle(
                        index=len(segment_subtitles) + 1,
                        start=datetime.timedelta(seconds=new_start),
                        end=datetime.timedelta(seconds=new_end),
                        content=subtitle.content
                    )
                    
                    segment_subtitles.append(new_subtitle)
            
            # Format as string
            segment_content = srt.compose(segment_subtitles)
            
            # Save the segment
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(segment_content)
            
            return output_path
        except Exception as e:
            raise Exception(f"Error extracting subtitle segment: {str(e)}")
