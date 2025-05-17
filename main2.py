import yt_dlp

def listar_formatos(url):
    opciones = {
        'quiet': True,
        'cookiefile': 'bilibili.tv_cookies.txt',
        'noplaylist': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0',
        'force_generic_extractor': False,
        'allow_unplayable_formats': True,

    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)
        formatos = info.get("formats", [])
        print(f"\nFormatos disponibles para: {info.get('title')}\n")

        for f in formatos:
            f_id = f.get("format_id")
            ext = f.get("ext")
            res = f.get("height")
            acodec = f.get("acodec")
            vcodec = f.get("vcodec")

            if acodec != 'none' and vcodec != 'none':
                tipo = "video+audio"
            elif acodec != 'none':
                tipo = "audio only"
            elif vcodec != 'none':
                tipo = "video only"
            else:
                tipo = "unknown"

            print(f"{f_id:10} | {ext:4} | {str(res) + 'p' if res else '   '} | {tipo}")

    return info.get('title')

def descargar_segmento(url, video_id, audio_id, title):
    format_string = f"{video_id}+{audio_id}"
    print(f"\n⏬ Intentando descargar con formato: {format_string}\n")

    opciones = {
        'format': format_string,
        'cookiefile': 'cookies.txt',
        'merge_output_format': 'mp4',
        'outtmpl': f"{title}_test.mp4"
    }

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        print("✅ Descarga completada correctamente.")
    except Exception as e:
        print("❌ Error durante la descarga:")
        print(e)

if __name__ == "__main__":
    url = input("🔗 URL del video: ").strip()
    title = listar_formatos(url)

    video_id = input("\n🎞️ Ingrese el video_id que desea probar: ").strip()
    audio_id = input("🔊 Ingrese el audio_id que desea probar: ").strip()

    descargar_segmento(url, video_id, audio_id, title)
