import requests
import json
import os

def processar_video(url_video, nome_arquivo, token_crm):
    try:
        print(f"Baixando vídeo de: {url_video[:50]}...")
        # 1. Download silencioso
        with requests.get(url_video, stream=True) as r:
            r.raise_for_status()
            with open(nome_arquivo, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Download concluído.")

        # 2. Upload para o CRM
        url_crm = "http://app.nectarcrm.com.br/crm/api/1/publicacao/incluirComAnexos"
        payload_dados = {
            "contato": {"id": 2},
            "assunto": "Vídeo da Reunião - Fireflies",
            "descricao": "Publicação automática."
        }
        
        headers = {"Access-Token": token_crm}
        
        print("Enviando para o CRM...")
        with open(nome_arquivo, 'rb') as video_file:
            files = {
                'publicacao': (None, json.dumps(payload_dados), 'application/json'),
                'anexos': (nome_arquivo, video_file, 'video/mp4')
            }
            response = requests.post(url_crm, headers=headers, files=files)
            
            # 3. Se for bem-sucedido, exclui o arquivo e não exibe nada
            if response.status_code in [200, 201]:
                if os.path.exists(nome_arquivo):
                    os.remove(nome_arquivo)
            else:
                # Mantemos o print apenas para erro, para você saber se algo falhar
                print(f"Erro no CRM ({response.status_code}): {response.text}")

    except Exception as e:
        print(f"Ocorreu um erro crítico: {e}")

# --- CONFIGURAÇÃO ---
URL_FIREFLIES = "https://cdn.fireflies.ai/01KH4F88MPF5Y2FYHVT3JV9E8S/video.mp4?Expires=1771636508&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uZmlyZWZsaWVzLmFpLzAxS0g0Rjg4TVBGNVkyRllIVlQzSlY5RThTL3ZpZGVvLm1wNCIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc3MTYzNjUwOH19fV19&Signature=gqiPIm3YfGvfhJoj1uBNgDxkpXmb3Bo3HvHJZzVpzAPQAHmxlPhEj9Q23gVF1y~hXqghTlyqY4tydAYR9tP9GaEmA7DbD2TrP~MeKe5imcApKHCwGOGFhHTuqTBmA6O2CJe0Yf4uvuYX14jazQfw6-P0GPi1RrP9VwVXF-PL2UecAhuxSmuGwbWLk1d4KX64p6Q0oIoTA6VRbCdxfPcnfqGtoZRJI7dRnCauqbVNXdzgCUlcFIIdE2mEau9o3k0qhG~5LnQCJzpI6r-qgEP2HdpC6naJmGeIZL105evKqaNnihDdoK2j0fbHNuqm0tZKEOutEOzQOlWR0haGR6mXAg__&Key-Pair-Id=K25ZJR0UZVF4CM"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NjYxNzU0MDAsImV4cCI6MjUyOTYzMDAwMCwidXNlckxvZ2luIjoiZWR1YXJkb0ByZXZlbnVlbGFiLmNvbS5iciIsInVzZXJJZCI6IjE1NDM3OSIsInVzdWFyaW9NYXN0ZXJJZCI6IjM0OTUwIn0.X7nneT3JBOvciYE_qJioaL01UlRlIPf7T9sjsMT_HW8"
ARQUIVO_LOCAL = "video_fireflies.mp4"

processar_video(URL_FIREFLIES, ARQUIVO_LOCAL, TOKEN)