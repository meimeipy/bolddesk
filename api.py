from flask import Flask, request, jsonify
from datetime import datetime
import requests
import schedule
import csv
import time
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


def job():
    with app.app_context():
        listar_cliente()
    
scheduler = BackgroundScheduler(timezone=timezone('America/Sao_Paulo'))
scheduler.add_job(func=job, trigger="interval", days=1, start_date='2022-01-01 00:00:00')
scheduler.start()

def importa_registros(clientes_filtrados):
    if not isinstance(clientes_filtrados, list):
        clientes_filtrados = [clientes_filtrados]
    url_tickets = "https://vittel.bolddesk.com/api/v1.0/tickets"
    url_contacts = 'https://vittel.bolddesk.com/api/v1/contacts'
    api_key = "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    
    headers = {"x-api-key": api_key}

    processados = set()
    for registro in clientes_filtrados:
        telefone1_ddd = registro['telefone1_ddd'] if registro['telefone1_ddd'] else ''
        telefone1_numero = registro['telefone1_numero'] if registro['telefone1_numero'] else ''
        if registro['cnpj_cpf'] in processados:
            print(f"Contato {registro['nome']} já processado, pulando...")
            continue
        processados.add(registro['cnpj_cpf'])
        dados_contato = {
            'contactName': registro['razao_social'],
            'emailId': registro['email'],
            'contactDisplayName': registro['nome_fantasia'],
            'contactPhoneNo': telefone1_ddd + telefone1_numero,
            'contactExternalReferenceId': registro['cnpj_cpf'],
        }

        # Adicione uma menagem de log para verificar os dados enviados

        response = requests.post(url_contacts, json=dados_contato, headers=headers)

        # Adicione mensagens de log para verificar a resposta da API


        if response.status_code == 200:
            print(f"Contato {registro.get('nome', 'Unknown')} adicionado com sucesso!")
        else:
            print(f"Falha ao adicionar contato {registro.get('nome', 'Unknown')}. Código de status: {response.status_code}")
        # Aguarde 1.5 segundos entre as chamadas para respeitar a taxa limite de 40 por minuto
        time.sleep(1.5)
@app.route('/webhook/importar', methods=['POST'])
def listar_cliente():
 
    url = "https://app.omie.com.br/api/v1/geral/clientes/"
    headers = {"Content-Type": "application/json"}
    data = {
        "call": "ListarClientes",
        "app_key": "4024681641981",
        "app_secret": "8fb7e54bce3344f6ac60fca754878f6d",
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 1,  # Fetch only one record to get the total count
                "apenas_importado_api": "N"
            }
        ]
    }

    # Make an initial request to get the total number of records
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    total_de_registros = response_data.get("total_de_registros", 0)
    # Update the 'registros_por_pagina' parameter to fetch all records
    data["param"][0]["registros_por_pagina"] = total_de_registros

    # Make a second request to fetch all records
    # Make a second request to fetch all records
    # Make a second request to fetch all records
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    clientes = response_data.get('clientes_cadastro', [])
    clientes_filtrados = []
    start_cnpj_cpf = '14.512.528/0001-54'  # Replace with your actual start CNPJ/CPF
    start_fetching = False

    if isinstance(clientes, list):
        for registro in clientes:
            cliente_filtrado = {
                'cnpj_cpf': registro.get('cnpj_cpf'),
                'email': registro.get('email'),
                'nome_fantasia': registro.get('nome_fantasia'),
                'razao_social': registro.get('razao_social'),
                'telefone1_ddd': registro.get('telefone1_ddd'),
                'telefone1_numero': registro.get('telefone1_numero'),
            }
            if cliente_filtrado['cnpj_cpf'] == start_cnpj_cpf:
                start_fetching = True
            if start_fetching:
                clientes_filtrados.append(cliente_filtrado)
                print("registros filtrados", cliente_filtrado)
    else:
        print(f"Erro: 'registros' não é uma lista. Valor atual: {clientes}")

    importa_registros(clientes_filtrados)    
    return jsonify(response_data)
# Agora, todos_registros contém todos os registros da API

def adicionar_contato_bold_desk(cliente_fornecedor_detalhes):
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    api_key = "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="

    headers = {
        "x-api-key": api_key, "Content-Type": "application/json"
    }

    
    response = requests.get(url, api_key, headers=headers)
    print("aqui", response)     

    
    nome = cliente_fornecedor_detalhes.get("steps.trigger", {}).get("context", {}).get('event', {}).get('body', {}).get('event', {}).get("razao_social")
    email = cliente_fornecedor_detalhes.get("steps.trigger", {}).get("context", {}).get('event', {}).get('body', {}).get('event', {}).get('email', {}).get("contabilidade")
    telefone = cliente_fornecedor_detalhes.get("steps.trigger", {}).get("context", {}).get('event', {}).get('body', {}).get('event', {}).get('tags', {}).get("telefone1_numero")
    nomedisplay = cliente_fornecedor_detalhes.get("steps.trigger", {}).get("context", {}).get('event', {}).get('body', {}).get('event', {}).get("nome_fantasia")
    cpfcnpj = cliente_fornecedor_detalhes.get("steps.trigger", {}).get("context", {}).get('event', {}).get('body', {}).get('event', {}).get("cnpj_cpf")
    url_bold_desk = "https://vittel.bolddesk.com/api/v1/contacts"
    dados_contato_bold_desk = {
        "contactName": nome,
        "emailId": email,
        "contactPhoneNo": telefone,
        "contactDisplayName": nomedisplay,
        "contactExternalReferenceId": cpfcnpj
    }
    print(dados_contato_bold_desk)
    
    try:
        response = requests.post(url_bold_desk, json=dados_contato_bold_desk, headers=headers)
        print(response)
        if response.status_code == 200:
            return jsonify({"message": "Contato adicionado ao BoldDesk com sucesso"}), 201
        else:
            return jsonify({"message": f" {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({"message": f"Erro ao fazer a solicitação à API do BoldDesk: {str(e)}"}), 500

@app.route('/webhook/adicionar', methods=['POST'])
def webhook_handler():
    dados_webhook = request.json.get("steps.trigger", {}).get("context", {}).get("event", {}).get("body", {}).get("event", {}).get("topic")

    
    if dados_webhook == "ClienteFornecedor.Incluido":
        
        cliente_fornecedor_detalhes = request.json
        
        print(cliente_fornecedor_detalhes)
        return adicionar_contato_bold_desk(cliente_fornecedor_detalhes)
    else:
        return jsonify({"message": "ClienteFornecedor.Incluido não encontrado no JSON"})
    
    
###########################################################################################################    
        
def list_items(cliente_fornecedor):
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }

    response_tickets = requests.get(url, headers=headers)
    print("1", response_tickets)
    
    if response_tickets.status_code == 200:
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 10,
            "Page": 1,
        }
        response_contatos = requests.get(url_contatos, params=params, headers=headers)

        print("2", response_contatos.text)

        if response_contatos.status_code == 200:
            dados_bold_desk = response_contatos.json().get("result", [])

            for contact in dados_bold_desk:
                if b'contactExternalReferenceId' in contact: 
                    if contact[b'contactExternalReferenceId'] == cliente_fornecedor.get('event', {}).get('body', {}).get('event', {}).get('cnpj_cpf'):
                        return atualizar_dados(dados_bold_desk, cliente_fornecedor)
                    print("000", contact)
                    break
                else:
                    return {"result": f"Campo 'contactExternalReferenceId' encontrado em {contact}"}
            else:
                return "Contato não encontrado para CNPJ/CPF"
        else:
            return f"Erro ao obter dados do BoldDesk: {response_contatos.status_code} - {response_contatos.text}"
    else:
        return f"Erro ao obter tickets do BoldDesk: {response_tickets.status_code} - {response_tickets.text}"

def atualizar_dados(dados_bold_desk, cliente_fornecedor):    
    url = "https://vittel.bolddesk.com/api/v1/contacts"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }   
    novos_dados = cliente_fornecedor.get('event', {}).get('body', {}).get('event', {})
    campos_alterados = {}
    
    if 'nome_fantasia' in novos_dados and 'contactDisplayName' in dados_bold_desk and novos_dados['nome_fantasia'] != dados_bold_desk['contactDisplayName']:
        campos_alterados['nome_fantasia'] = {
            'old_value': dados_bold_desk['contactDisplayName'],
            'new_value': novos_dados['nome_fantasia']
        }

    
    if 'razao_social' in novos_dados and 'contactName' in dados_bold_desk and novos_dados['razao_social'] != dados_bold_desk['contactName']:
        campos_alterados['razao_social'] = {
            'old_value': dados_bold_desk['contactName'],
            'new_value': novos_dados['razao_social']
        }
    if 'nome_fantasia' in novos_dados and 'contactDisplayName' in dados_bold_desk and novos_dados['nome_fantasia'] != dados_bold_desk['contactDisplayName']:
        campos_alterados['nome_fantasia'] = {
            'old_value': dados_bold_desk['contactDisplayName'],
            'new_value': novos_dados['nome_fantasia']
        }
    if 'email' in novos_dados and 'emailId' in dados_bold_desk and novos_dados['email'] != dados_bold_desk['emailId']:
        campos_alterados['email'] = {
            'old_value': dados_bold_desk['emailId'],
            'new_value': novos_dados['email']
        }
    if 'cnpj_cpf' in novos_dados and 'contactExternalReferenceId' in dados_bold_desk and novos_dados['cnpj_cpf'] != dados_bold_desk['contactExternalReferenceId']:
        campos_alterados['cnpj_cpf'] = {
            'old_value': dados_bold_desk['contactExternalReferenceId'],
            'new_value': novos_dados['cnpj_cpf']
        }
    if campos_alterados:
        update_response = requests.put(url, json=dados_bold_desk, headers=headers)
        print("4", update_response)

        return campos_alterados
    
@app.route('/webhook/att', methods=['PUT'])
def webhook_att():
    dados_webhook = request.json.get("event", {}).get("body", {}).get("topic")
    print("aqui", dados_webhook)

    if dados_webhook == "ClienteFornecedor.Alterado":
        cliente_fornecedor = request.json
        print("00", cliente_fornecedor)
        return list_items(cliente_fornecedor)
    else:
        return jsonify({"message": "ClienteFornecedor.Alterado não encontrado no JSON"})
    
  
################################################################################################################
def list_items(clientefornecedor):
    url_tickets = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }

    response_tickets = requests.get(url_tickets, headers=headers)
    print("1", response_tickets)

    if response_tickets.status_code == 200:
        url_contacts = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 40,
            "Page": 1,
        }

        try:
            while True:
                response_contacts = requests.get(url_contacts, params=params, headers=headers)
                print("2", response_contacts.text)
                response_contacts.raise_for_status()
                if params["Page"] >=12:
                    break
                if response_contacts.status_code == 200:
                    dados_bold_desk = response_contacts.json().get("result", [])
                    

                    for contact in dados_bold_desk:
                        print("contactExternalReferenceId", contact['contactExternalReferenceId'])
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == clientefornecedor.get('event', {}).get('body', {}).get('event', {}).get('cnpj_cpf'):
                            if 'userId' in contact:
                                userid = contact['userId']
                                print(userid)
                                # Não retorna aqui, apenas marca para exclusão
                                return excluir_para_spam(userid)
                            
                            else:
                                return f"Contact encontrado para contactExternalReferenceId {['cnpj_cpf']}, mas 'userId' não está presente."
                    
                    params["Page"] += 1
                else:
                    # Move this break outside the loop to continue checking pages
                    break

            # Adicionado retorno para indicar que todos os contatos foram verificados
            return f"Verificação concluída para contactExternalReferenceId {['cnpj_cpf']}"

        except requests.exceptions.RequestException as e:
            return f"Erro ao obter contatos do BoldDesk: {str(e)}"

    return f"Falha ao obter tickets: {response_tickets.status_code}"

def excluir_para_spam(userid):
    url_delete_contact = f"https://vittel.bolddesk.com/api/v1/contacts"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }
    data = {
        "contactId": [userid],
        "markTicketAsSpam": True
    }
    try:
        response = requests.delete(url_delete_contact, json=data, headers=headers)
        print(response)
        response.raise_for_status()

        if response.status_code == 200:
            return "Contato excluído com sucesso."
        else:
            return f"Erro ao excluir contato. Código de status: {response.status_code}, Mensagem: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Erro na solicitação de exclusão: {str(e)}"
    except Exception as e:
        return f"Erro inesperado ao excluir contato: {str(e)}"
    

@app.route('/webhook/deletar', methods=['DELETE'])
def webhook_delete():
    dados_webhook = request.json.get("event", {}).get("body", {}).get("topic")
    print("aqui", dados_webhook)

    if dados_webhook == "ClienteFornecedor.Excluido":
        clientefornecedor = request.json
        print("00", clientefornecedor)
        return list_items(clientefornecedor)
    else:
        return jsonify({"message": "ClienteFornecedor.Alterado não encontrado no JSON"})

#########################################################################################################
# consulta cnpj
import requests
import requests_cache

def formatt_cnpj_cpf(value):
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

def buscacliente(dadoss):
        requests_cache.install_cache('api_cache', expire_after=600)
        
        headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
        }
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 100,
            "Page": 1,
        }
        try:
            while True:
                response_contatos = requests.get(url_contatos, headers=headers, params=params)
                
                response_contatos.raise_for_status()
                if params["Page"] >=30:
                    break
                if response_contatos.status_code == 200:
                    dados_bold_desk = response_contatos.json().get("result", [])

                    for contact in dados_bold_desk:
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == formatt_cnpj_cpf(dadoss['cnpj_cpf']):
                            if 'userId' in contact:
                                user_id = contact['userId']
                                print("123333", user_id)
                                contact_name = contact['contactDisplayName']
                                print("123333", contact_name)
                                return jsonify({"user_id": user_id, "contact_name": contact_name})
                            else:
                                return f"Contact encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}, mas 'userId' não está presente."

                    # Fix the typo and adjust the indentation
                    params["Page"] += 1
                else:
                    # Move this break outside the loop to continue checking pages
                    break

            # This return statement will only be reached if the loop completes without finding the contact
            return "false"

        except requests.exceptions.RequestException as e:
         return jsonify({"error": f"Falha na solicitação: {str(e)}"}), 500

        return jsonify({"error": f"Falha ao obter tickets: {response_tickets.status_code}"}), 500

@app.route('/webhook/consultaclienteid', methods=['GET']) 
def dados_rece():
    token = request.headers.get('token')
    if token != "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=":
        return jsonify({"message": "Token inválido"}), 401
    dadoss = request.args  
    
    if 'cnpj_cpf' in dadoss and dadoss['cnpj_cpf']:
        return buscacliente(dadoss)
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
    
    
    
    
    

###############################################################################################


# consulta detalhes do ticket

def formatt_cnpj_cpf(value):
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

def acharocliente(dadoss):
        requests_cache.install_cache('api_cache', expire_after=600)

        headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
        }

        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 100,
            "Page": 1,
        }
        try:
            while True:
                response_contatos = requests.get(url_contatos, headers=headers, params=params)
                response_contatos.raise_for_status()
                if params["Page"] >= 21:
                    break
                if response_contatos.status_code == 200:
                    dados_bold_desk = response_contatos.json().get("result", [])

                    for contact in dados_bold_desk:
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == formatt_cnpj_cpf(dadoss['cnpj_cpf']):
                            if 'userId' in contact:
                                user_id = contact['userId']
                                print("123333", user_id)
                                return consultar_detalhes_do_ticket(user_id)
                            else:
                                return f"Contact encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}, mas 'userId' não está presente."

                    params["Page"] += 1
                else:
                    break

            return f"Nenhum contato encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}"

        except requests.exceptions.RequestException as e:
            return f"Falha na solicitação: {str(e)}"
def consultar_detalhes_do_ticket(user_id):
    url_ticket = f"https://vittel.bolddesk.com/api/v1/tickets"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }
   
    params = {
    "Q":  [f"requester:[{user_id}]", "status:[1,2]"]
    }


    response_ticket = requests.get(url_ticket, headers=headers, params=params)
    
    
    if response_ticket.status_code == 200:
        return response_ticket.json()
    else:
        return f"Falha ao consultar detalhes do ticket para UserID {user_id}"
    
    
@app.route('/webhook/consultat', methods=['GET']) 
def dados_boot():
    token = request.headers.get('token')
    if token != "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=":
        return jsonify({"message": "Token inválido"}), 401
    dadoss = request.args  
    print("12", dadoss)
    
    if 'cnpj_cpf' in dadoss and dadoss['cnpj_cpf']:
        return acharocliente(dadoss)
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
    
################################################################################################    
    # ABRIR TICKET
# def formatt_cnpj_cpf(value):
#     return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"
import re

def formatt_cnpj_cpf(value):
    # Remover todos os caracteres não numéricos
    value = re.sub(r'\D', '', value)
    
    # Verificar o comprimento para determinar se é CNPJ ou CPF
    if len(value) == 14:  # CNPJ
        return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"
    elif len(value) == 11:  # CPF
        return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"
    else:
        return "Formato inválido"
def acharoccliente(dadoss):
        requests_cache.install_cache('api_cache', expire_after=600)

        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        headers = {
            "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
        }
        params = {
            "PerPage": 100,
            "Page": 1,
        }
        try:
            while True:
                response_contatos = requests.get(url_contatos, headers=headers, params=params)
                
                response_contatos.raise_for_status()
                if response_contatos.status_code == 200:
                    dados_bold_desk = response_contatos.json().get("result", [])
                    

                    for contact in dados_bold_desk:
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == formatt_cnpj_cpf(dadoss['cnpj_cpf']):
                            if 'userId' in contact:
                                user_id = contact['userId']
                                print(user_id)
                                return Abrir_Ticket(user_id, dadoss)
                            else:
                                return f"Contact encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}, mas 'userId' não está presente."

                    params["Page"] += 1
                else:
                    break

            return f"Nenhum contato encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}"

        except requests.exceptions.RequestException as e:
            return f"Falha na solicitação: {str(e)}"

from datetime import datetime

def Abrir_Ticket(user_id, dadoss):
    dadoss = dict(dadoss)
    user_id = user_id
    extracted_data = {key: dadoss.get(key) for key in ["Assunto", "Categoria", "Descrição"]}
    print("123", extracted_data)
    logging.debug(f"Extracted data: {extracted_data}")
    category_ids = {
        "VOZ IP": 11,
        "PABX IP": 12,
        "Call Center": 16,
        "Sip Trunk": 17,
        "Whatsapp/Chat": 18,
        "Cloud Server": 22,
        "SMS": 23
    }
    
    user_selection = dadoss.get('Categoria')
    logging.debug(f"User selection: {user_selection}")
    category_id = category_ids[user_selection]
    cater = dadoss.get('Categoria')
    now = datetime.utcnow()
    dueDate = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Generate the protocol
    # Generate the protocol
    protocol = now.strftime("%Y%m%d%H%M%S")

    # Append the protocol to the subject
    subject_with_protocol = f"{cater} - {protocol}"
    assunto = extracted_data['Assunto']
    ticket_data = {
        "brandId": 1,
        "subject": subject_with_protocol,  # Use the subject with the protocol
        "categoryId": category_id,  
        "isVisibleInCustomerPortal": True,
        "requesterId": user_id,  
        "description": f"{extracted_data['Descrição']}, Protocolo: {protocol}, Requisitante:{dadoss.get('NAME')}{dadoss.get('phoneNumber')}",
        "agentId": None,
        "priorityId": 1,
        "dueDate": dueDate,
        "ticketPortalValue": 0,
    }
    
    url_ticket = "https://vittel.bolddesk.com/api/v1/tickets"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=",
    }
    
    response_ull = requests.post(url_ticket, headers=headers, json=ticket_data) 
    
    print("to aqui", response_ull.json())
    
    logging.debug(f"Response: {response_ull.text}")
    
    if response_ull.status_code == 201:
        print(f"user_id: {user_id}")
        
        logging.debug(f"user_id: {user_id}")
        
        ticketId = response_ull.json().get("id")
        
        response_data = {"protocol": protocol, "assunto": assunto, "user_id": user_id, "ticketId": ticketId, "status": "true", "code": 201}
        
        print("Response data:", response_data)
        logging.debug(f"Response data: {response_data}")
        
        return response_data, 201
    else:
        print("2", response_ull.text)
        print("user: ", user_id)
        return {"status": "false", "code": 400,}, 400

@app.route('/webhook/opent', methods=['POST']) 
def dados_booti():
    token = request.headers.get('token')
    if token != "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=":
        return jsonify({"message": "Token inválido"}), 401
    dadoss = request.args  
    print("12", dadoss)
    
    if 'cnpj_cpf' in dadoss and dadoss['cnpj_cpf']:
        return acharoccliente(dadoss)
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
#############################################################################################
# Atualizar ticket
@app.route('/webhook/get-sender-name/<conversationId>/<ticketId>', methods=['GET'])
def get_sender_name(conversationId, ticketId):
    token = request.headers.get('token')
    if token != "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=":
        return jsonify({"message": "Token inválido"}), 401
    url = f'https://chat.omnigo.com.br/api/v1/accounts/1/conversations/{conversationId}'
    headers = {
        "api_access_token": "8BNDLDVBN8nw4AmArzsHghZx"
    }
    response = requests.get(url, headers=headers)
    print("1get_sender_name", response.json())
    if response.status_code == 200:
        try:
            data = response.json()
            print("1get_sender_name", data)
            sender_name = data['meta']['assignee']['name']
            print("2get_sender_name", sender_name)
            result = editar_ticket(ticketId, sender_name)
            return jsonify({"message": result})
        except KeyError as e:
            return jsonify({"error": f"Chave não encontrada: {str(e)}"}), 400
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Erro ao decodificar JSON: {str(e)}"}), 400
    else:
        return jsonify({"error": f"Falha na solicitação: {response.status_code}"}), response.status_code
def editar_ticket(ticketId, sender_name):
    try:
    # URL para buscar detalhes dos agentes
        sender_name = sender_name
        requests_cache.install_cache('api_cache', expire_after=600)

        agents_url = "https://vittel.bolddesk.com/api/v1/agents"
        headers = {
            "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=",
            "Content-Type": "application/json"
        }
        
        # Fazendo a requisição para obter a lista de agentes
        response = requests.get(agents_url, headers=headers)
        if response.status_code != 200:
            return f"Falha ao buscar o agente: {response.status_code}"
        
        agents_response = response.json()
        if not isinstance(agents_response, dict) or 'result' not in agents_response:
            return "Formato de resposta inesperado da API."
        
        agents = agents_response['result']
        if not isinstance(agents, list):
            return "Formato de resposta inesperado da API."
        
        # Filtrar o agente pelo nome
        agent_info = next((agent for agent in agents if agent['name'] == sender_name), None)
        if not agent_info:
            return "Agente não encontrado."
        
        # Preparar os dados para atualizar o ticket
        url = f"https://vittel.bolddesk.com/api/v1/tickets/{ticketId}/update_fields"
        payload = {
            "fields": {
                "agentid": agent_info['userId'],

                },
                "notes": "Agente atualizado via API."
            }

    
        
        # Fazendo a requisição para atualizar o ticket
        response = requests.put(url, headers=headers, json=payload)
        print("4editar_ticket", response.json())
        
        if response.status_code == 200:
            return sender_name
        else:
            return "false"
    except requests.RequestException as e:
        return jsonify({"error": f"Erro na requisição: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500
# def editar_ticket(ticketId, sender_name):
#     # URL para buscar detalhes dos agentes
#     agents_url = "https://vittel.bolddesk.com/api/v1/agents"
#     headers = {
#         "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=",
#         "Content-Type": "application/json"
#     }
    
#     # Fazendo a requisição para obter a lista de agentes
#     response = requests.get(agents_url, headers=headers)
#     print("2editar_ticket", response.json())
#     if response.status_code != 200:
#         return f"Falha ao buscar o agente: {response.status_code}"
    
#     agents = response.json()
#     if not isinstance(agents, list):
#         return "Formato de resposta inesperado da API."
#     # Filtrar o agente pelo nome
#     agent_info = next((agent for agent in agents if agent['name'] == sender_name), None)
#     print("3editar_ticket", agent_info)
#     if not agent_info:
#         return "Agente não encontrado."
    
#     # Preparar os dados para atualizar o ticket
#     url = f"https://vittel.bolddesk.com/api/v1/tickets/{ticketId}"
#     payload = {
#         "fields": {
#             "agent": {
#                 "id": agent_info['userId'],
#                 "name": agent_info['name'],
#                 "emailId": agent_info['emailId']
#             }
#         }
#     }
    
#     # Fazendo a requisição para atualizar o ticket
#     response = requests.put(url, headers=headers, json=payload)
    
#     if response.status_code == 200:
#         return "Ticket atualizado com sucesso."
#     else:
#         return f"Falha ao atualizar o ticket: {response.status_code}"

#############################################################################################
def formatt_cnpj_cpf(value):
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

def acharocliente(dadoss):
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }

    response_tickets = requests.get(url, headers=headers)
    print("1", response_tickets)

    if response_tickets.status_code == 200:
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 100,
            "Page": 1,
        }
        try:
            while True:
                response_contatos = requests.get(url_contatos, headers=headers, params=params)
                print("2", response_contatos.text)
                response_contatos.raise_for_status()
                if params["Page"] >= 21:
                    break
                if response_contatos.status_code == 200:
                    dados_bold_desk = response_contatos.json().get("result", [])
                    print("3", dados_bold_desk)

                    for contact in dados_bold_desk:
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == formatt_cnpj_cpf(dadoss['cnpj_cpf']):
                            if 'userId' in contact:
                                user_id = contact['userId']
                                print("123333", user_id)
                                return consultar_detalhes_do_ticket(user_id)
                            else:
                                return f"Contact encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}, mas 'userId' não está presente."

                    params["Page"] += 1
                else:
                    break

            return f"Nenhum contato encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}"

        except requests.exceptions.RequestException as e:
            return f"Falha na solicitação: {str(e)}"
    
    return "Falha na busca do cliente"
def consultar_detalhes_do_ticket(user_id):
    url_ticket = f"https://vittel.bolddesk.com/api/v1/tickets"
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }
   
    params = {
    "Q":  [f"requester:[{user_id}]", "ticketId:[1]", "status:[1,2]"], 
    }


    response_ticket = requests.get(url_ticket, headers=headers, params=params)
    print(response_ticket)
    
    if response_ticket.status_code == 200:
        return response_ticket
    else:
        return f"Falha ao consultar detalhes do ticket para UserID {user_id}"

    
@app.route('/webhook/deletarticket', methods=['DEL']) 
def handle_delete_ticket_request():
    token = request.headers.get('token')
    if token != "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=":
        return jsonify({"message": "Token inválido"}), 401
    dadoss = request.args  
    print("12", dadoss)
    
    if 'cnpj_cpf' in dadoss and dadoss['cnpj_cpf']:
        return acharocliente(dadoss)
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
    
    
    
#  achar agente   
def format_cnpj_cpf(value):
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

def encontrarcliente(dados):
        requests_cache.install_cache('api_cache', expire_after=600)
        headers = {
            "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
        }
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 100,
            "Page": 1,
        }
        try:
            while True:
                response_contatos = requests.get(url_contatos, headers=headers, params=params)
                
                response_contatos.raise_for_status()
                if params["Page"] >=21:
                    break
                if response_contatos.status_code == 200:
                    dados_bold_desk = response_contatos.json().get("result", [])
                    

                    for contact in dados_bold_desk:
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == formatt_cnpj_cpf(dados['cnpj_cpf']):
                            if 'userId' in contact:
                                user_id = contact['userId']
                                print("123333", user_id)
                                return agenteachado(dados, user_id)
                            else:
                                 return f"Contact encontrado para contactExternalReferenceId {dados['cnpj_cpf']}, mas 'userId' não está presente."

                    # Fix the typo and adjust the indentation
                    params["Page"] += 1
                else:
                    # Move this break outside the loop to continue checking pages
                    break

            # This return statement will only be reached if the loop completes without finding the contact
            return f"Nenhum contato encontrado para contactExternalReferenceId {dados['cnpj_cpf']}"

        except requests.exceptions.RequestException as e:
            return f"Falha na solicitação: {str(e)}"

        return f"Falha ao obter tickets: {response_tickets.status_code}"

def agenteachado(dados, user_id): 
    url_agente = f"https://vittel.bolddesk.com/api/v1/tickets/"
    params = {
        "Q": [f"requester:[{user_id}]", "status:[1,2,3]"]
    }
    headers = {
        "x-api-key": "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0="
    }

    response = requests.get(url_agente, headers=headers, params=params)
    print("1", response.json())

    if response.status_code == 200:
        # Assuming the response is a JSON object with a 'result' field containing a list
        results = response.json().get("result", [])
        category_ids = {
                "VOZ IP": 11,
                "PABX IP": 12,
                "Call Center": 16,
                "Sip Trunk": 17,
                "Whatsapp/Chat": 18,
                "Cloud Server": 22,
                "SMS": 23
        }
        user_selection = dados.get('Categoriaa') or dados.get('Categoria')
        if results is None:
            return "Não existe tickets."
        category_id = category_ids[user_selection]
            
        all_tickets = []
        for ticket_info in results:
            # Extracting the required fields
            if ticket_info.get("category", {}).get("id") == category_id:
                agente = ticket_info.get("agent", {})
                print("2", agente)
                marca = ticket_info.get("brand")
                categoria = ticket_info.get("category", {})
                criadoEm = ticket_info.get("createdOn")
                ultimaRespostaEm = ticket_info.get("lastRepliedOn")
                ultimaMudancaStatusEm = ticket_info.get("lastStatusChangedOn")
                prioridade = ticket_info.get("priority", {})
                solicitante = ticket_info.get("requester", {})
                resolucaoPrevistaPara = ticket_info.get("resolutionDue")
                respostaPrevistaPara = ticket_info.get("responseDue")
                origem = ticket_info.get("source")
                status = ticket_info.get("status", {})
                tag = ticket_info.get("tag", [])
                titulo = ticket_info.get("title")

                # Add the ticket to the list
                all_tickets.append({
                    "agente": agente,
                    "marca": marca,
                    "categoria": categoria,
                    "criadoEm": criadoEm,
                    "ultimaRespostaEm": ultimaRespostaEm,
                    "ultimaMudancaStatusEm": ultimaMudancaStatusEm,
                    "prioridade": prioridade,
                    "solicitante": solicitante,
                    "resolucaoPrevistaPara": resolucaoPrevistaPara,
                    "respostaPrevistaPara": respostaPrevistaPara,
                    "origem": origem,
                    "status": status,
                    "tag": tag,
                    "titulo": titulo
                })
            if all_tickets:
                return jsonify(all_tickets)
            else:
                return "Não existe tickets."

        return f"Falha ao consultar detalhes do ticket para UserID"

@app.route('/webhook/detalhesticket', methods=['GET']) 
def dados_recebidos2():
    token = request.headers.get('token')
    if token != "1Ed7TGUUE0rzqjP5WCbsRZh56qtWP8eHHKXD9aK/+X0=":
        return jsonify({"message": "Token inválido"}), 401
    dados = request.args  
    print("12", dados)
    if 'cnpj_cpf' in dados and dados['cnpj_cpf'] and 'user_id' in dados and dados['user_id']:
        return agenteachado(dados, dados['user_id'])
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
    

        
if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
    
    
    
    