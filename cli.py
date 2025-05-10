#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI (Command Line Interface) para processamento de vídeos
--------------------------------------------------------
Esta ferramenta permite transcrever, dividir e processar vídeos com legendas
a partir da linha de comando, oferecendo as mesmas funcionalidades da interface web.

Exemplos de uso:
    # Transcrever um vídeo (gera arquivo SRT)
    python cli.py transcribe --input video.mp4 --output legendas.srt

    # Baixar e transcrever vídeo do YouTube
    python cli.py youtube --url "https://www.youtube.com/watch?v=ID_DO_VIDEO" --output video_baixado.mp4

    # Dividir um vídeo em partes iguais
    python cli.py split --input video.mp4 --subtitle legendas.srt --parts 3 --output pasta_saida

    # Dividir um vídeo em pontos específicos (segundos)
    python cli.py split --input video.mp4 --subtitle legendas.srt --timestamps 30,60,90 --output pasta_saida

    # Incorporar legendas no vídeo
    python cli.py embed --input video.mp4 --subtitle legendas.srt --output video_com_legendas.mp4
"""

import os
import sys
import time
import argparse
import tempfile
import shutil
from pathlib import Path

# Importar classes do projeto
from video_processor import VideoProcessor
from subtitle_processor import SubtitleProcessor


def setup_parser():
    """Configure o parser de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Ferramenta de linha de comando para transcrição e divisão de vídeos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Criar subparsers para diferentes comandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: transcribe
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcrever um vídeo para legendas SRT')
    transcribe_parser.add_argument('--input', '-i', required=True, help='Caminho para o arquivo de vídeo')
    transcribe_parser.add_argument('--output', '-o', help='Caminho para salvar o arquivo SRT (opcional)')
    transcribe_parser.add_argument('--model', '-m', default='tiny', choices=['tiny', 'base', 'small'], 
                                 help='Modelo Whisper a ser usado (tiny, base, small)')
    
    # Comando: youtube
    youtube_parser = subparsers.add_parser('youtube', help='Baixar vídeo do YouTube')
    youtube_parser.add_argument('--url', '-u', required=True, help='URL do vídeo do YouTube')
    youtube_parser.add_argument('--output', '-o', help='Caminho para salvar o vídeo (opcional)')
    youtube_parser.add_argument('--transcribe', '-t', action='store_true', 
                               help='Gerar transcrição depois de baixar')
    
    # Comando: split
    split_parser = subparsers.add_parser('split', help='Dividir vídeo em partes')
    split_parser.add_argument('--input', '-i', required=True, help='Caminho para o arquivo de vídeo')
    split_parser.add_argument('--subtitle', '-s', required=True, help='Caminho para o arquivo de legendas SRT')
    split_parser.add_argument('--output', '-o', required=True, help='Pasta para salvar os segmentos')
    split_parser.add_argument('--parts', '-p', type=int, help='Número de partes iguais (2-20)')
    split_parser.add_argument('--timestamps', '-ts', help='Timestamps para divisão (em segundos, separados por vírgula)')
    
    # Comando: embed
    embed_parser = subparsers.add_parser('embed', help='Incorporar legendas em um vídeo')
    embed_parser.add_argument('--input', '-i', required=True, help='Caminho para o arquivo de vídeo')
    embed_parser.add_argument('--subtitle', '-s', required=True, help='Caminho para o arquivo de legendas SRT')
    embed_parser.add_argument('--output', '-o', required=True, help='Caminho para salvar o vídeo com legendas')
    
    return parser


def print_progress(message, progress=None):
    """Exibe uma mensagem de progresso no console."""
    if progress is not None:
        # Cria uma barra de progresso simples
        bar_length = 30
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r{message} [{bar}] {progress}%")
    else:
        sys.stdout.write(f"\r{message}")
    
    sys.stdout.flush()


def transcribe_video(args):
    """Transcrever um vídeo para legendas SRT."""
    input_path = os.path.abspath(args.input)
    
    # Verificar se o arquivo de entrada existe
    if not os.path.exists(input_path):
        print(f"Erro: Arquivo de entrada '{input_path}' não encontrado.")
        return False
    
    # Configurar o caminho de saída
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        # Se não especificado, usa o mesmo nome do vídeo com extensão .srt
        output_path = os.path.splitext(input_path)[0] + ".srt"
    
    # Garantir que o diretório de saída existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Inicializar o processador de legendas
        subtitle_processor = SubtitleProcessor()
        
        print(f"Iniciando transcrição do vídeo: {os.path.basename(input_path)}")
        print(f"Usando modelo Whisper: {args.model}")
        print(f"Este processo pode levar vários minutos dependendo do tamanho do vídeo...")
        
        # Iniciar temporizador
        start_time = time.time()
        
        # Chamar o método de transcrição (versão sem thread)
        result = subtitle_processor.transcribe_video(input_path, output_path)
        
        # Mostrar tempo decorrido
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        print(f"\nTranscrição concluída em {minutes}m {seconds}s!")
        print(f"Arquivo de legendas salvo em: {output_path}")
        
        return True
    
    except Exception as e:
        print(f"\nErro ao transcrever vídeo: {str(e)}")
        return False


def download_youtube(args):
    """Baixar vídeo do YouTube."""
    video_processor = VideoProcessor()
    
    # Configurar o caminho de saída
    if args.output:
        output_path = os.path.abspath(args.output)
        output_dir = os.path.dirname(output_path)
    else:
        # Se não especificado, usa a pasta atual
        output_dir = os.path.abspath('.')
        output_path = os.path.join(output_dir, f"youtube_video_{int(time.time())}.mp4")
    
    # Garantir que o diretório de saída existe
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print(f"Baixando vídeo do YouTube: {args.url}")
        
        # Baixar o vídeo
        downloaded_path = video_processor.download_youtube_video(args.url, output_dir)
        
        # Se um caminho de saída específico foi fornecido, copie o arquivo
        if args.output and downloaded_path != output_path:
            shutil.copy2(downloaded_path, output_path)
            downloaded_path = output_path
        
        print(f"\nVídeo baixado com sucesso: {downloaded_path}")
        
        # Transcrever o vídeo se solicitado
        if args.transcribe:
            print("\nIniciando transcrição do vídeo baixado...")
            
            # Configurar argumentos para transcrição
            transcribe_args = argparse.Namespace()
            transcribe_args.input = downloaded_path
            transcribe_args.output = os.path.splitext(downloaded_path)[0] + ".srt"
            transcribe_args.model = "tiny"
            
            # Chamar a função de transcrição
            transcribe_video(transcribe_args)
        
        return True
    
    except Exception as e:
        print(f"\nErro ao baixar vídeo do YouTube: {str(e)}")
        return False


def split_video(args):
    """Dividir vídeo em partes."""
    input_path = os.path.abspath(args.input)
    subtitle_path = os.path.abspath(args.subtitle)
    output_dir = os.path.abspath(args.output)
    
    # Verificar se os arquivos de entrada existem
    if not os.path.exists(input_path):
        print(f"Erro: Arquivo de vídeo '{input_path}' não encontrado.")
        return False
    
    if not os.path.exists(subtitle_path):
        print(f"Erro: Arquivo de legendas '{subtitle_path}' não encontrado.")
        return False
    
    # Garantir que o diretório de saída existe
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        video_processor = VideoProcessor()
        
        # Obter a duração do vídeo
        duration = video_processor.get_video_duration(input_path)
        min_duration = int(duration // 60)
        sec_duration = int(duration % 60)
        
        print(f"Vídeo: {os.path.basename(input_path)} (Duração: {min_duration}m {sec_duration}s)")
        
        # Determinar o modo de divisão
        if args.parts:
            # Modo: partes iguais
            num_parts = args.parts
            if num_parts < 2 or num_parts > 20:
                print("Erro: O número de partes deve estar entre 2 e 20.")
                return False
            
            print(f"Dividindo vídeo em {num_parts} partes iguais...")
            
            # Calcular duração de cada parte
            part_duration = duration / num_parts
            part_min = int(part_duration // 60)
            part_sec = int(part_duration % 60)
            print(f"Cada parte terá aproximadamente {part_min}m {part_sec}s")
            
            # Dividir o vídeo
            segments = video_processor.split_video_equal_parts(
                input_path, subtitle_path, num_parts, output_dir
            )
            
        elif args.timestamps:
            # Modo: timestamps personalizados
            timestamps_str = args.timestamps
            try:
                timestamps = [float(ts.strip()) for ts in timestamps_str.split(',')]
                timestamps = sorted([ts for ts in timestamps if 0 < ts < duration])
            except ValueError:
                print("Erro: Os timestamps devem ser valores numéricos separados por vírgula.")
                return False
            
            if not timestamps:
                print("Erro: Nenhum timestamp válido fornecido.")
                return False
            
            print(f"Dividindo vídeo em {len(timestamps) + 1} segmentos nos pontos: {', '.join([str(ts) for ts in timestamps])} segundos...")
            
            # Dividir o vídeo
            segments = video_processor.split_video_custom_timestamps(
                input_path, subtitle_path, timestamps, output_dir
            )
            
        else:
            print("Erro: Você deve especificar --parts OU --timestamps")
            return False
        
        # Relatório de segmentos gerados
        print(f"\nDivisão concluída! {len(segments)} segmentos gerados:")
        for i, segment in enumerate(segments):
            start_min = int(segment['start_time'] // 60)
            start_sec = int(segment['start_time'] % 60)
            end_min = int(segment['end_time'] // 60)
            end_sec = int(segment['end_time'] % 60)
            
            segment_duration = segment['end_time'] - segment['start_time']
            duration_min = int(segment_duration // 60)
            duration_sec = int(segment_duration % 60)
            
            video_file = os.path.basename(segment['video_path'])
            subtitle_file = os.path.basename(segment['subtitle_path'])
            
            print(f"  Segmento {i+1}: {start_min}m{start_sec}s - {end_min}m{end_sec}s (Duração: {duration_min}m{duration_sec}s)")
            print(f"    - Vídeo: {video_file}")
            print(f"    - Legendas: {subtitle_file}")
        
        print(f"\nArquivos salvos em: {output_dir}")
        return True
    
    except Exception as e:
        print(f"\nErro ao dividir vídeo: {str(e)}")
        return False


def embed_subtitles(args):
    """Incorporar legendas em um vídeo."""
    input_path = os.path.abspath(args.input)
    subtitle_path = os.path.abspath(args.subtitle)
    output_path = os.path.abspath(args.output)
    
    # Verificar se os arquivos de entrada existem
    if not os.path.exists(input_path):
        print(f"Erro: Arquivo de vídeo '{input_path}' não encontrado.")
        return False
    
    if not os.path.exists(subtitle_path):
        print(f"Erro: Arquivo de legendas '{subtitle_path}' não encontrado.")
        return False
    
    # Garantir que o diretório de saída existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        video_processor = VideoProcessor()
        
        print(f"Incorporando legendas no vídeo...")
        print(f"  Vídeo: {os.path.basename(input_path)}")
        print(f"  Legendas: {os.path.basename(subtitle_path)}")
        print(f"Este processo pode levar alguns minutos...")
        
        # Iniciar temporizador
        start_time = time.time()
        
        # Incorporar as legendas
        result_path = video_processor.embed_subtitles(input_path, subtitle_path, output_path)
        
        # Mostrar tempo decorrido
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        print(f"\nLegendas incorporadas com sucesso em {minutes}m {seconds}s!")
        print(f"Vídeo com legendas salvo em: {result_path}")
        
        return True
    
    except Exception as e:
        print(f"\nErro ao incorporar legendas: {str(e)}")
        return False


def main():
    """Função principal da CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Verificar se um comando foi fornecido
    if not args.command:
        parser.print_help()
        return 1
    
    # Executar o comando especificado
    success = False
    if args.command == 'transcribe':
        success = transcribe_video(args)
    elif args.command == 'youtube':
        success = download_youtube(args)
    elif args.command == 'split':
        success = split_video(args)
    elif args.command == 'embed':
        success = embed_subtitles(args)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())