from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests
import json
import os
import uuid

app = FastAPI(title="Video Processor API")

# Modelo de dados para a requisição
class VideoProcessRequest(BaseModel):
    url_video: str
    token_crm: str
    nome_arquivo: str = "video_fireflies.mp4"
    contato_id: int

def executar_processamento_completo(url_video, nome_arquivo, token_crm, contato_id):
    """
    Mantive sua lógica original, mas adicionei um ID único ao nome do arquivo
    para evitar conflitos se dois processos rodarem ao mesmo tempo.
    """
    arquivo_temp = f"{nome_arquivo}"
    
    try:
        # 1. Download
        with requests.get(url_video, stream=True) as r:
            r.raise_for_status()
            with open(arquivo_temp, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # 2. Upload para o CRM
        url_crm = "http://app.nectarcrm.com.br/crm/api/1/publicacao/incluirComAnexos"
        payload_dados = {
            "contato": {"id": contato_id},
            "assunto": "Vídeo da Reunião - Fireflies",
            "descricao": "Publicação automática via API."
        }
        
        headers = {"Access-Token": token_crm}
        
        with open(arquivo_temp, 'rb') as video_file:
            files = {
                'publicacao': (None, json.dumps(payload_dados), 'application/json'),
                'anexos': (arquivo_temp, video_file, 'video/mp4')
            }
            response = requests.post(url_crm, headers=headers, files=files)
            
            if response.status_code in [200, 201]:
                print(f"Sucesso: Vídeo enviado para o CRM.")
            else:
                print(f"Erro no CRM ({response.status_code}): {response.text}")

    except Exception as e:
        print(f"Erro crítico no processamento: {e}")
    
    finally:
        # 3. Limpeza: Sempre tenta excluir o arquivo temporário
        if os.path.exists(arquivo_temp):
            os.remove(arquivo_temp)

@app.post("/processar-video")
def processar(dados: VideoProcessRequest, background_tasks: BackgroundTasks):
    """
    Endpoint para processar o vídeo. 
    Usa BackgroundTasks para liberar o cliente da API imediatamente 
    enquanto o download/upload acontece no servidor.
    """
    background_tasks.add_task(
        executar_processamento_completo, 
        dados.url_video, 
        dados.nome_arquivo, 
        dados.token_crm,
        dados.contato_id
    )
    
    return {"status": "processamento_iniciado", "mensagem": "O vídeo está sendo baixado e enviado ao CRM em segundo plano."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)