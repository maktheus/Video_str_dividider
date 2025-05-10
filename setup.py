from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="transcricao-video",
    version="1.0.0",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Ferramenta para transcrição e divisão de vídeos com legendas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seuusername/video-transcription-tool",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit",
        "whisper",
        "ffmpeg-python",
        "yt-dlp",
        "srt",
        "python-dotenv",
        "trafilatura",
    ],
    entry_points={
        "console_scripts": [
            "videotranscricao=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
)