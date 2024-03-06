
import requests
import csv
import time

def importacsv():
    url_tickets = "https://vittel.bolddesk.com/api/v1.0/tickets"
    url_contacts = 'https://vittel.bolddesk.com/api/v1/contacts'
    api_key = "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    
    headers = {"x-api-key": api_key}

    caminho_arquivo_csv = 'CLIENTES.csv'

    # Conjunto para armazenar IDs externos já adicionados
    ids_externos_adicionados = set()

    with open(caminho_arquivo_csv, 'r', encoding='utf-8') as CLIENTES_csv:
        leitor_csv = csv.reader(CLIENTES_csv, delimiter=';')

        for linha in leitor_csv:
            # Adicione mensagens de log para verificar os dados
            # print(f"Dados lidos: {linha[3]}")

            # Se precisar substituir ',' por '.' para campos numéricos, faça isso diretamente
            dados_contato = {
                'contactName': linha[3],
                'emailId': linha[7],  
                'contactDisplayName': linha[4],
                'contactPhoneNo': linha[5],
                'contactExternalReferenceId': linha[2],
            }

            # Verifica se o ID externo já foi adicionado
            if dados_contato['contactExternalReferenceId'] in ids_externos_adicionados:
                print(f"Contato {linha[3]} já adicionado. Ignorando.")
                continue

            # Adiciona o ID externo ao conjunto
            ids_externos_adicionados.add(dados_contato['contactExternalReferenceId'])

            # Adicione uma mensagem de log para verificar os dados enviados
            print(f"Dados enviados para a API: {dados_contato}")

            response = requests.post(url_contacts, json=dados_contato, headers=headers)

            # Adicione mensagens de log para verificar a resposta da API
            print(f"Resposta da API: {response.status_code}")
            print(response.text)

            if response.status_code == 200:
                print(f"Contato {linha[3]} adicionado com sucesso!")
            else:
                print(f"Falha ao adicionar contato {linha[3]}. Código de status: {response.status_code}")

            # Aguarde 1.5 segundos entre as chamadas para respeitar a taxa limite de 40 por minuto
            time.sleep(1.5)

# Chamada da função
importacsv()





