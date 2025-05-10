import os
import streamlit as st
import base64

def save_uploaded_file(uploaded_file, directory):
    """Save an uploaded file to a directory.
    
    Args:
        uploaded_file: The uploaded file object from Streamlit.
        directory (str): Directory to save the file.
        
    Returns:
        str: Path to the saved file.
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate file path
    file_path = os.path.join(directory, uploaded_file.name)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def create_download_link(file_path, text, download_filename=None):
    """Create a download link for a file.
    
    Args:
        file_path (str): Path to the file to download.
        text (str): Text to display for the download link.
        download_filename (str, optional): Filename to use when downloading.
            Defaults to the original filename.
    """
    if download_filename is None:
        download_filename = os.path.basename(file_path)
    
    # Read file data
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # Determine mime type
    _, file_extension = os.path.splitext(file_path)
    mime_type = get_mime_type(file_extension)
    
    # Create download button
    st.download_button(
        label=text,
        data=data,
        file_name=download_filename,
        mime=mime_type
    )

def get_mime_type(file_extension):
    """Get the MIME type for a file extension.
    
    Args:
        file_extension (str): File extension including the dot.
        
    Returns:
        str: MIME type for the file extension.
    """
    # MIME type mapping
    mime_types = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.srt': 'text/plain',
        '.txt': 'text/plain',
    }
    
    return mime_types.get(file_extension.lower(), 'application/octet-stream')
