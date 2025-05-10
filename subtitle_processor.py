import os
import subprocess
import srt
import datetime
import tempfile
import time
import hashlib
import streamlit as st
import threading

class SubtitleProcessor:
    def __init__(self):
        """Initialize the SubtitleProcessor class."""
        pass
    
    def transcribe_video(self, video_path, output_path):
        """Transcribe a video file using Whisper CLI and save as SRT.
        
        Args:
            video_path (str): Path to the video file.
            output_path (str): Path to save the SRT file.
            
        Returns:
            str: Path to the generated SRT file.
        """
        # Create a unique identifier for this video to use in cache
        video_hash = hashlib.md5(open(video_path, 'rb').read(1024*1024)).hexdigest()[:10]  # Use first MB for hash
        
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join(os.path.dirname(output_path), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Define cache file path
        cache_path = os.path.join(cache_dir, f"{video_hash}_transcription.srt")
        
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
            # STEP 1: Extract audio (25% of progress)
            progress_text.write("⏳ Etapa 1/3: Extraindo áudio do vídeo...")
            progress_bar.progress(5)
            
            # Extract audio from video to temporary file
            temp_audio_file = os.path.join(os.path.dirname(output_path), f"{video_hash}_audio.wav")
            
            # Use ffmpeg command to extract audio
            ffmpeg_cmd = [
                "ffmpeg", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-y", temp_audio_file
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            progress_bar.progress(25)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao extrair áudio: {result.stderr}")
            
            # STEP 2: Start transcription
            progress_text.write("⏳ Etapa 2/3: Transcrevendo o áudio (isso pode levar alguns minutos)...")
            
            # This flag will be set when the transcription is complete
            transcription_complete = {"status": False, "error": None}
            
            # Store the output file path
            transcription_result = {"path": None}
            
            # Define the transcription function that will run in a separate thread
            def run_transcription():
                try:
                    # Create temp directory for Whisper output
                    whisper_output_dir = os.path.join(os.path.dirname(output_path), "whisper_output")
                    os.makedirs(whisper_output_dir, exist_ok=True)
                    
                    # Use Whisper CLI to transcribe
                    result = subprocess.run(
                        ["whisper", temp_audio_file, "--model", "tiny", "--output_format", "srt", "--output_dir", whisper_output_dir],
                        capture_output=True, 
                        text=True
                    )
                    
                    if result.returncode != 0:
                        transcription_complete["error"] = f"Erro do Whisper: {result.stderr}"
                        transcription_complete["status"] = True
                        return
                    
                    # The output file will be named like the input audio file but with .srt extension
                    output_filename = os.path.splitext(os.path.basename(temp_audio_file))[0] + ".srt"
                    generated_srt = os.path.join(whisper_output_dir, output_filename)
                    
                    if not os.path.exists(generated_srt):
                        transcription_complete["error"] = "Arquivo SRT não foi gerado pelo Whisper."
                        transcription_complete["status"] = True
                        return
                    
                    # Save path to result
                    transcription_result["path"] = generated_srt
                    
                    # Mark as complete
                    transcription_complete["status"] = True
                    
                except Exception as e:
                    transcription_complete["error"] = str(e)
                    transcription_complete["status"] = True
            
            # Start transcription in a separate thread so we can update the progress
            transcription_thread = threading.Thread(target=run_transcription)
            transcription_thread.start()
            
            # Update progress while transcription is running
            start_time = time.time()
            while not transcription_complete["status"]:
                # Calculate progress based on time passed (estimate 2 minutes for completion)
                elapsed = time.time() - start_time
                estimated_total = 120  # 2 minutes estimated
                progress = min(25 + (elapsed / estimated_total) * 50, 75)  # From 25% to 75%
                
                # Update progress
                progress_bar.progress(int(progress))
                
                # Add a small delay
                time.sleep(0.5)
            
            # Check if transcription succeeded
            if transcription_complete["error"]:
                raise Exception(transcription_complete["error"])
            
            # STEP 3: Process and save transcription
            progress_text.write("⏳ Etapa 3/3: Finalizando e salvando as legendas...")
            progress_bar.progress(80)
            
            generated_srt = transcription_result["path"]
            
            # If file exists, process and save it
            if os.path.exists(generated_srt):
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
                
                # Don't delete the generated SRT as it's our cache
                
                progress_bar.progress(100)
                progress_text.write("✅ Transcrição concluída com sucesso!")
                
                return output_path
            else:
                raise Exception(f"Arquivo SRT não foi gerado pelo Whisper.")
                
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
