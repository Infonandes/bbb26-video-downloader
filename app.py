#!/usr/bin/env python3
"""
Serviço de Download de Vídeos BBB26 via Webhook
GitHub: https://github.com/Infonandes/bbb26-video-downloader
"""

from flask import Flask, request, jsonify, send_file
import subprocess
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Pasta temporária para downloads
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    """Health check"""
    return jsonify({
        "status": "online",
        "servico": "Download de Vídeos BBB26",
        "versao": "1.0.0",
        "endpoints": {
            "/download": "POST - Baixar vídeo HLS",
            "/status": "GET - Status do serviço"
        }
    })

@app.route('/download', methods=['POST'])
def download_video():
    """
    Endpoint principal para download
    
    Body esperado:
    {
        "hls_url": "https://...",
        "nome_arquivo": "video.mp4",
        "video_id": "12345678"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'hls_url' not in data:
            return jsonify({
                "erro": "URL do vídeo não fornecida",
                "exemplo": {
                    "hls_url": "https://vod-cm-ah-24-31.video.globo.com/...",
                    "nome_arquivo": "BBB26_video.mp4",
                    "video_id": "14263747"
                }
            }), 400
        
        hls_url = data['hls_url']
        nome_arquivo = data.get('nome_arquivo', f'video_{uuid.uuid4()}.mp4')
        video_id = data.get('video_id', 'unknown')
        
        # Caminho do arquivo de saída
        output_path = os.path.join(DOWNLOAD_DIR, nome_arquivo)
        
        print(f"📥 Iniciando download: {nome_arquivo}")
        print(f"🔗 URL: {hls_url[:80]}...")
        
        # Comando yt-dlp
        comando = [
            'yt-dlp',
            hls_url,
            '-o', output_path,
            '--no-warnings',
            '--quiet',
            '--no-playlist',
            '--progress'
        ]
        
        # Executar download
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if resultado.returncode != 0:
            print(f"❌ Erro no download: {resultado.stderr}")
            return jsonify({
                "erro": "Falha ao baixar vídeo",
                "detalhes": resultado.stderr,
                "codigo": resultado.returncode
            }), 500
        
        if not os.path.exists(output_path):
            return jsonify({
                "erro": "Arquivo não foi criado após download"
            }), 500
        
        tamanho_bytes = os.path.getsize(output_path)
        tamanho_mb = tamanho_bytes / (1024 * 1024)
        
        print(f"✅ Download concluído! Tamanho: {tamanho_mb:.2f} MB")
        
        return send_file(
            output_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=nome_arquivo
        )
        
    except subprocess.TimeoutExpired:
        return jsonify({
            "erro": "Timeout: Download demorou mais de 10 minutos"
        }), 504
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return jsonify({
            "erro": "Erro interno",
            "detalhes": str(e)
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """Verificar status do serviço"""
    try:
        arquivos = []
        if os.path.exists(DOWNLOAD_DIR):
            for arquivo in os.listdir(DOWNLOAD_DIR):
                caminho = os.path.join(DOWNLOAD_DIR, arquivo)
                if os.path.isfile(caminho):
                    tamanho = os.path.getsize(caminho)
                    arquivos.append({
                        "nome": arquivo,
                        "tamanho_mb": round(tamanho / (1024 * 1024), 2)
                    })
        
        return jsonify({
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "arquivos_disponiveis": len(arquivos),
            "arquivos": arquivos[:10]
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
