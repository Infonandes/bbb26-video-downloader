# 🎬 BBB26 Video Downloader

Serviço para download de vídeos do BBB26 via API.

## 🚀 Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## 📡 Endpoints

- `GET /` - Health check
- `POST /download` - Baixar vídeo
- `GET /status` - Status do serviço

## 💻 Uso
```bash
curl -X POST https://seu-servico.railway.app/download \
  -H "Content-Type: application/json" \
  -d '{
    "hls_url": "https://...",
    "nome_arquivo": "video.mp4",
    "video_id": "12345678"
  }'
```

## 🛠️ Tecnologias

- Python 3.11
- Flask
- yt-dlp
- Gunicorn
