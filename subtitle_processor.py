import os
import subprocess
import srt
import datetime
import tempfile
import streamlit as st

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
        try:
            # Extract audio from video to temporary file
            temp_audio_file = os.path.join(os.path.dirname(output_path), "temp_audio.wav")
            
            # Show progress message
            st.write("Extraindo áudio do vídeo...")
            
            # Use ffmpeg command to extract audio
            ffmpeg_cmd = [
                "ffmpeg", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-y", temp_audio_file
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao extrair áudio: {result.stderr}")
            
            # Show transcription progress
            st.write("Transcrevendo o áudio com Whisper (pode levar alguns segundos)...")
            
            # Use Whisper CLI to transcribe
            result = subprocess.run(
                ["whisper", temp_audio_file, "--model", "tiny", "--output_format", "srt", "--output_dir", os.path.dirname(output_path)],
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Erro do Whisper: {result.stderr}")
            
            # The output file will be named like the input audio file but with .srt extension
            generated_srt = os.path.join(os.path.dirname(output_path), os.path.splitext(os.path.basename(temp_audio_file))[0] + ".srt")
            
            # If file exists, rename it to the requested output path
            if os.path.exists(generated_srt):
                # Read the file to fix possible encoding issues
                with open(generated_srt, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Write to the requested output path
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                # Clean up temp files
                os.remove(temp_audio_file)
                os.remove(generated_srt)
                
                return output_path
            else:
                raise Exception(f"Arquivo SRT não foi gerado pelo Whisper.")
                
        except Exception as e:
            st.error(f"Erro ao transcrever o vídeo: {str(e)}")
            # Create a dummy SRT if transcription fails
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("1\n00:00:00,000 --> 00:00:05,000\nErro na transcrição. Por favor, tente novamente.")
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
