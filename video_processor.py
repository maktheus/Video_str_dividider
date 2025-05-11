import os
import subprocess
import tempfile
import json
import time
import streamlit as st
import yt_dlp
from subtitle_processor import SubtitleProcessor

class VideoProcessor:
    def __init__(self):
        """Initialize the VideoProcessor class."""
        self.subtitle_processor = SubtitleProcessor()
        
    def download_youtube_video(self, youtube_url, output_dir, download_subtitles=False):
        """Download a video from YouTube using yt-dlp, with option for subtitles.
        
        Args:
            youtube_url (str): URL of the YouTube video.
            output_dir (str): Directory to save the downloaded video.
            download_subtitles (bool): Whether to download subtitles.
            
        Returns:
            dict: Dictionary with paths to the downloaded files or str path if no subtitles.
        """
        try:
            # Create a progress message
            st.write("Conectando ao YouTube...")
            
            # Generate an output filename with timestamp to avoid conflicts
            timestamp = int(time.time())
            output_filename = f"youtube_video_{timestamp}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[ext=mp4]',  # Best quality in mp4 format
                'outtmpl': output_path,     # Output path
                'quiet': True,              # Less verbose output
                'no_warnings': True,        # No warnings
                'progress': False,          # No progress to avoid clutter in logs
            }
            
            # Setup subtitle options if requested
            subtitle_path = None
            if download_subtitles:
                # Add subtitle options
                ydl_opts.update({
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['pt', 'en'],  # Prefer Portuguese, then English
                    'subtitlesformat': 'srt',
                })
            
            # Create progress status
            status = st.empty()
            status.write("Obtendo informações do vídeo...")
            
            # First get video info to show title
            info = None
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(youtube_url, download=False)
                    video_title = info.get('title', 'Vídeo do YouTube') if info else 'Vídeo do YouTube'
                except Exception:
                    video_title = 'Vídeo do YouTube'
            
            # Check if video has subtitles
            has_subtitles = False
            if info and isinstance(info, dict):
                if 'subtitles' in info and info['subtitles']:
                    has_subtitles = True
                elif 'automatic_captions' in info and info['automatic_captions']:
                    has_subtitles = True
                
            # Display title
            if download_subtitles and has_subtitles:
                status.write(f"Vídeo encontrado: {video_title} (com legendas)")
                status.write(f"Baixando o vídeo e legendas... (pode levar alguns minutos)")
            else:
                status.write(f"Vídeo encontrado: {video_title}")
                status.write(f"Baixando o vídeo... (pode levar alguns minutos)")
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Check if file exists
            if not os.path.exists(output_path):
                raise Exception("Falha ao baixar o vídeo - arquivo não foi criado")
            
            # If subtitles were requested, look for the downloaded subtitle file
            if download_subtitles and has_subtitles:
                subtitle_filename = f"{os.path.splitext(output_filename)[0]}.pt.srt"
                subtitle_path = os.path.join(output_dir, subtitle_filename)
                
                # Check if Portuguese subtitle exists
                if not os.path.exists(subtitle_path):
                    # Try English subtitle
                    subtitle_filename = f"{os.path.splitext(output_filename)[0]}.en.srt"
                    subtitle_path = os.path.join(output_dir, subtitle_filename)
                
                # Check if any subtitle was found
                if os.path.exists(subtitle_path):
                    status.write(f"✅ Download do vídeo e legendas concluído!")
                    return {
                        'video_path': output_path,
                        'subtitle_path': subtitle_path
                    }
                else:
                    status.write(f"✅ Download do vídeo concluído! (Legendas não encontradas)")
            else:
                status.write(f"✅ Download do vídeo concluído!")
            
            # If we reached here, either subtitles weren't requested or weren't found
            if download_subtitles:
                return {
                    'video_path': output_path,
                    'subtitle_path': None
                }
            else:
                return output_path
            
        except Exception as e:
            st.error(f"Erro ao baixar vídeo do YouTube: {str(e)}")
            raise Exception(f"Erro ao baixar vídeo do YouTube: {str(e)}")
            
    def download_youtube_subtitles(self, youtube_url, output_dir):
        """Download only subtitles from YouTube using yt-dlp.
        
        Args:
            youtube_url (str): URL of the YouTube video.
            output_dir (str): Directory to save the subtitles.
            
        Returns:
            str: Path to the downloaded subtitle file, or None if not available.
        """
        try:
            # Create a progress message
            status = st.empty()
            status.write("Verificando legendas disponíveis...")
            
            # Generate an output filename with timestamp to avoid conflicts
            timestamp = int(time.time())
            output_filename = f"youtube_subtitles_{timestamp}"
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Configure yt-dlp options for subtitles only
            ydl_opts = {
                'skip_download': True,       # Skip video download
                'writesubtitles': True,      # Download subtitles
                'writeautomaticsub': True,   # Get auto-generated if needed
                'subtitleslangs': ['pt', 'en'],  # Prefer Portuguese, then English
                'subtitlesformat': 'srt',    # SRT format
                'outtmpl': os.path.join(output_dir, output_filename),  # Output template
                'quiet': True,               # Less verbose output
                'no_warnings': True          # No warnings
            }
            
            # First check if video has subtitles
            info = None
            video_title = 'Vídeo do YouTube'
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    if info and isinstance(info, dict):
                        video_title = info.get('title', 'Vídeo do YouTube')
            except Exception:
                status.write("Erro ao obter informações do vídeo, mas tentando baixar as legendas mesmo assim.")
                
            # Check if video has available subtitles
            has_subtitles = False
            if info and isinstance(info, dict):
                if 'subtitles' in info and info['subtitles']:
                    has_subtitles = True
                    status.write(f"Legendas oficiais encontradas para: {video_title}")
                elif 'automatic_captions' in info and info['automatic_captions']:
                    has_subtitles = True
                    status.write(f"Legendas automáticas encontradas para: {video_title}")
                else:
                    status.write(f"❌ O vídeo '{video_title}' não possui legendas disponíveis.")
                    return None
            else:
                # Sem informações suficientes, vamos tentar baixar mesmo assim
                status.write("Tentando baixar legendas mesmo sem informações detalhadas...")
                
            # Download the subtitles
            status.write("Baixando legendas...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Look for the downloaded subtitle file - yt-dlp will add language code extension
            pt_subtitle_path = os.path.join(output_dir, f"{output_filename}.pt.srt")
            en_subtitle_path = os.path.join(output_dir, f"{output_filename}.en.srt")
            
            # Check if Portuguese subtitles exist
            if os.path.exists(pt_subtitle_path):
                status.write(f"✅ Legendas em português baixadas com sucesso!")
                return pt_subtitle_path
            # If not, check for English
            elif os.path.exists(en_subtitle_path):
                status.write(f"✅ Legendas em inglês baixadas com sucesso!")
                return en_subtitle_path
            else:
                status.write("❌ Não foi possível baixar as legendas.")
                return None
                
        except Exception as e:
            st.error(f"Erro ao baixar legendas do YouTube: {str(e)}")
            return None
    
    def get_video_duration(self, video_path):
        """Get the duration of a video file in seconds.
        
        Args:
            video_path (str): Path to the video file.
            
        Returns:
            float: Duration of the video in seconds.
        """
        try:
            # Use ffprobe to get duration
            ffprobe_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "json", video_path
            ]
            
            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao obter duração do vídeo: {result.stderr}")
            
            # Parse JSON output
            output = json.loads(result.stdout)
            duration = float(output['format']['duration'])
            return duration
        except Exception as e:
            raise Exception(f"Erro ao obter duração do vídeo: {str(e)}")
    
    def split_video_equal_parts(self, video_path, subtitle_path, num_parts, output_dir):
        """Split a video into equal parts and generate corresponding subtitles.
        
        Args:
            video_path (str): Path to the video file.
            subtitle_path (str): Path to the subtitle file.
            num_parts (int): Number of parts to split the video into.
            output_dir (str): Directory to save the output files.
            
        Returns:
            list: List of dictionaries containing paths to video and subtitle segments.
        """
        # Get video duration
        duration = self.get_video_duration(video_path)
        
        # Calculate segment duration
        segment_duration = duration / num_parts
        
        # Create timestamps for splitting
        timestamps = [i * segment_duration for i in range(1, num_parts)]
        
        # Split the video using custom timestamps
        return self.split_video_custom_timestamps(video_path, subtitle_path, timestamps, output_dir)
    
    def split_video_custom_timestamps(self, video_path, subtitle_path, timestamps, output_dir):
        """Split a video at custom timestamps and generate corresponding subtitles.
        
        Args:
            video_path (str): Path to the video file.
            subtitle_path (str): Path to the subtitle file.
            timestamps (list): List of timestamps (in seconds) to split the video at.
            output_dir (str): Directory to save the output files.
            
        Returns:
            list: List of dictionaries containing paths to video and subtitle segments.
        """
        # Get video duration
        duration = self.get_video_duration(video_path)
        
        # Ensure valid timestamps
        timestamps = sorted([ts for ts in timestamps if 0 < ts < duration])
        
        # Add start and end points
        start_times = [0] + timestamps
        end_times = timestamps + [duration]
        
        segments = []
        
        # Create temp directory for segments
        segments_dir = os.path.join(output_dir, "segments")
        os.makedirs(segments_dir, exist_ok=True)
        
        # Process each segment
        for i, (start, end) in enumerate(zip(start_times, end_times)):
            # Define output paths
            segment_video_path = os.path.join(segments_dir, f"segment_{i+1}.mp4")
            segment_subtitle_path = os.path.join(segments_dir, f"segment_{i+1}.srt")
            
            # Extract video segment
            self._extract_video_segment(video_path, segment_video_path, start, end - start)
            
            # Extract subtitle segment
            self.subtitle_processor.extract_subtitle_segment(subtitle_path, segment_subtitle_path, start, end)
            
            # Add segment to the list
            segments.append({
                'video_path': segment_video_path,
                'subtitle_path': segment_subtitle_path,
                'start_time': start,
                'end_time': end
            })
        
        return segments
    
    def _extract_video_segment(self, input_path, output_path, start_time, duration):
        """Extract a segment from a video file.
        
        Args:
            input_path (str): Path to the input video file.
            output_path (str): Path to save the output video segment.
            start_time (float): Start time of the segment in seconds.
            duration (float): Duration of the segment in seconds.
        """
        try:
            # Use ffmpeg command to extract segment
            ffmpeg_cmd = [
                "ffmpeg", "-i", input_path, "-ss", str(start_time), 
                "-t", str(duration), "-c", "copy", "-y", output_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao extrair segmento de vídeo: {result.stderr}")
                
        except Exception as e:
            raise Exception(f"Erro ao extrair segmento de vídeo: {str(e)}")
    
    def embed_subtitles(self, video_path, subtitle_path, output_path):
        """Embed subtitles into a video file.
        
        Args:
            video_path (str): Path to the video file.
            subtitle_path (str): Path to the subtitle file.
            output_path (str): Path to save the output video with embedded subtitles.
            
        Returns:
            str: Path to the output video with embedded subtitles.
        """
        try:
            # Use ffmpeg to embed subtitles
            subtitle_path_esc = subtitle_path.replace("'", "'\\''")  # Escape single quotes
            
            ffmpeg_cmd = [
                "ffmpeg", "-i", video_path, 
                "-vf", f"subtitles='{subtitle_path_esc}'", 
                "-c:a", "copy", "-c:v", "libx264", "-preset", "medium",
                "-y", output_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao incorporar legendas: {result.stderr}")
                
            return output_path
        except Exception as e:
            raise Exception(f"Erro ao incorporar legendas: {str(e)}")
