import os
import subprocess
import tempfile
import json
from subtitle_processor import SubtitleProcessor

class VideoProcessor:
    def __init__(self):
        """Initialize the VideoProcessor class."""
        self.subtitle_processor = SubtitleProcessor()
    
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
