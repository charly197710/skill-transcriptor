# 🎤 Meeting Transcriber

Aplicación de escritorio para transcribir, analizar y resumir grabaciones de audio y video.

## 🚀 Características

- **Transcripción local** (sin internet) usando Whisper
- **Transcripción API** (con OpenRouter) para resultados más precisos
- **Análisis automático**: puntos clave, decisiones, tareas pendientes
- **Exportación**: Markdown, PDF, Mapa Mental HTML interactivo
- **Multilingüe**: detección automática de idioma
- **Historial**: guarda transcripciones y análisis en base de datos local

## 📦 Instalación

Requiere Python 3.10+ y [uv](https://github.com/astral-sh/uv):

```bash
# 1. Clonar repositorio
git clone https://github.com/charly197710/skill-transcriptor.git
cd skill-transcriptor

# 2. Instalar dependencias
uv pip install flet sounddevice soundfile faster-whisper fpdf2
```

## ▶️ Uso

### App de escritorio
```bash
# Ejecutar con uv
uv run python main.py

# O usar el script batch
run.bat
```

### Línea de comandos
```bash
# Transcribir audio
uv run scripts/transcribe.py local --input audio.wav --output texto.txt

# Analizar transcripción
uv run scripts/analyze.py full --input texto.txt --output analisis.json

# Generar resumen
uv run scripts/summary.py md --input analisis.json --output resumen.md
```

## 📋 Flujo de trabajo

1. **Cargar archivo** → Selecciona audio/video desde tu computadora
2. **Transcribir** → Procesa el archivo (20-60 segundos)
3. **Analizar** → Extrae puntos clave, decisiones, tareas
4. **Exportar** → Descarga Markdown, PDF o Mapa Mental

## 🔧 Configuración

Archivo `config.json` (opcional):
```json
{
  "output_dir": "./output",
  "default_lang": "es",
  "default_mode": "local",
  "openrouter_api_key": "tu-api-key",
  "whisper_model": "base"
}
```

## 🎯 Notas importantes

- **Modo local** es gratuito pero más lento
- **API Whisper-1** requiere saldo en OpenRouter ($0.50 mínimo)
- Los archivos se guardan en `output/` por defecto

---

**Desarrollado como skill para Hermes Agent**  
*Reúne toda la funcionalidad de transcripción y análisis en una interfaz amigable*