from django.shortcuts import render
from docx import Document
from datetime import datetime
import mysql.connector
import subprocess
import os
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.http import FileResponse

def home(request):
    conn = mysql.connector.connect(host="localhost", user="root", password="teste123", database="contrato_teste")
    my_cursor = conn.cursor()

    # Buscar todos os usuários da tabela
    tabela_sql = "SELECT id, ut_nome FROM utentes_data"
    my_cursor.execute(tabela_sql)
    usuarios = my_cursor.fetchall()
    
    conn.close()
    
    # Passar a lista de usuários para o template
    return render(request, 'templates.html', {'usuarios': usuarios})

#contrato em nova guia

def exibir_contrato(request, nome_arquivo):
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT, nome_arquivo)
    if os.path.exists(caminho_arquivo):
        return FileResponse(open(caminho_arquivo, 'rb'), content_type='application/pdf')
    else:
        return HttpResponse('Arquivo não encontrado.', status=404)

#gerar contratos especificos

def gerar_contrato_especifico(request):
    if request.method == 'POST':
        
        user_id = request.POST.get('user_id')
        documento_base = request.POST.get('documento_base')

        if not user_id or not documento_base:
            return JsonResponse({"status": "error", "message": "Selecione um usuário e um tipo de contrato."})
        
        caminho_documento_base = os.path.join(settings.DOCUMENTOS_BASE_DIR, documento_base)
        if not os.path.exists(caminho_documento_base):
            return JsonResponse({"status": "error", "message": "O documento base selecionado não foi encontrado."})

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="teste123", database="contrato_teste")
            my_cursor = conn.cursor()

            tabela_sql = "SELECT ut_nome, ut_nascimento, ut_endereco FROM utentes_data WHERE id = %s"
            my_cursor.execute(tabela_sql, (user_id,))
            linha = my_cursor.fetchone()

            if not linha:
                conn.close()
                return JsonResponse({"status": "error", "message": "Usuário não encontrado."})

            ut_nome = linha[0]
            ut_nascimento = linha[1]
            ut_endereco = linha[2]

            documento = Document(caminho_documento_base)

            referencias = {
                "NOME": ut_nome,
                "DATA": str(ut_nascimento),
                "ENDERECO": ut_endereco,
            }

            for paragrafo in documento.paragraphs:
                for codigo, valor in referencias.items():
                    paragrafo.text = paragrafo.text.replace(codigo, valor)

            tipo_contrato = documento_base.split('.')[0].replace('contrato_', '')
            contrato_nome = f"Contrato-{ut_nome}-{tipo_contrato}"

            # Define a condição para escolher o formato
            condicao = False  # Pode ser alterado conforme a sua lógica de negócio
            if condicao:
                # Gera o contrato em PDF
                contrato_pdf_path = os.path.join(settings.MEDIA_ROOT, f"{contrato_nome}.pdf")
                contrato_docx_path = contrato_pdf_path.replace('.pdf', '.docx')

                # Salva o arquivo DOCX temporário
                documento.save(contrato_docx_path)

                # Converte o DOCX para PDF usando LibreOffice
                try:
                    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', contrato_docx_path, '--outdir', settings.MEDIA_ROOT])
                    os.remove(contrato_docx_path)  # Remove o arquivo .docx após a conversão
                except Exception as e:
                    return JsonResponse({"status": "error", "message": f"Erro ao converter para PDF: {str(e)}"})

                return JsonResponse({'status': 'success', 'pdf_url': f'/media/{contrato_nome}.pdf'})
            else:
                # Gera o contrato em DOCX
                contrato_docx_path = os.path.join(settings.MEDIA_ROOT, f"{contrato_nome}.docx")

                # Salva diretamente o DOCX
                documento.save(contrato_docx_path)

                return JsonResponse({'status': 'success', 'docx_url': f'/media/{contrato_nome}.docx'})
        
        except Exception as e:
            print(f"Erro: {str(e)}")
            return JsonResponse({"status": "error", "message": "Erro ao gerar o contrato."})

    return JsonResponse({"status": "error", "message": "Método não permitido."})



