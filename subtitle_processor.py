import os
import whisper
import srt
import datetime
import tempfile
import streamlit as st

class SubtitleProcessor:
    def __init__(self):
        """Initialize the SubtitleProcessor class."""
        # The model will be loaded when needed
        self.model = None
    
    def transcribe_video(self, video_path, output_path):
        """Transcribe a video file using Whisper and save as SRT.
        
        Args:
            video_path (str): Path to the video file.
            output_path (str): Path to save the SRT file.
            
        Returns:
            str: Path to the generated SRT file.
        """
        # Show progress message
        st.write("Carregando o modelo Whisper (pode levar alguns segundos na primeira vez)...")
        
        # Load the model if not already loaded
        if self.model is None:
            # Use the tiny model for fastest processing
            # Can be changed to other model sizes like "base", "small", "medium", "large"
            self.model = whisper.load_model("tiny")
        
        try:
            # Transcribe the audio
            st.write("Transcrevendo o vídeo com Whisper...")
            result = self.model.transcribe(video_path)
            
            # Convert the result to SRT format
            srt_content = self._whisper_result_to_srt(result)
            
            # Save the SRT file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return output_path
        except Exception as e:
            raise Exception(f"Erro ao transcrever o vídeo: {str(e)}")
    
    def _whisper_result_to_srt(self, result):
        """Convert Whisper transcription result to SRT format.
        
        Args:
            result (dict): Whisper transcription result.
            
        Returns:
            str: SRT formatted subtitles.
        """
        srt_subtitles = []
        
        for i, segment in enumerate(result['segments']):
            # Create SRT subtitle object
            subtitle = srt.Subtitle(
                index=i+1,
                start=datetime.timedelta(seconds=segment['start']),
                end=datetime.timedelta(seconds=segment['end']),
                content=segment['text'].strip()
            )
            
            srt_subtitles.append(subtitle)
        
        # Format as string
        return srt.compose(srt_subtitles)
    
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
