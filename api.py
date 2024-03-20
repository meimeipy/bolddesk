from flask import Flask, request, jsonify
from datetime import datetime
import requests
app = Flask(__name__)
def adicionar_contato_bold_desk(cliente_fornecedor_detalhes):
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    api_key = "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="

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
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
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
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    }   
    novos_dados = cliente_fornecedor.get('event', {}).get('body', {}).get('event', {})
    print("3", novos_dados)
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
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
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
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
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
def formatt_cnpj_cpf(value):
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

def buscacliente(dadoss):
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    }

    response_tickets = requests.get(url, headers=headers)
    print("1", response_tickets)

    if response_tickets.status_code == 200:
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 40,
            "Page": 1,
        }
        try:
            while True:
                response_contatos = requests.get(url_contatos, headers=headers, params=params)
                print("2", response_contatos.text)
                response_contatos.raise_for_status()
                if params["Page"] >=21:
                    break
                if response_contatos.status_code == 200:
                    dados_bold_desk = response_contatos.json().get("result", [])
                    print("3", dados_bold_desk)

                    for contact in dados_bold_desk:
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == format_cnpj_cpf(dadoss['cnpj_cpf']):
                            if 'userId' in contact:
                                user_id = contact['userId']
                                print("123333", user_id)
                                return "true"
                            else:
                                return f"Contact encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}, mas 'userId' não está presente."

                    # Fix the typo and adjust the indentation
                    params["Page"] += 1
                else:
                    # Move this break outside the loop to continue checking pages
                    break

            # This return statement will only be reached if the loop completes without finding the contact
            return f"Nenhum contato encontrado para contactExternalReferenceId {dadoss['cnpj_cpf']}"

        except requests.exceptions.RequestException as e:
         return jsonify({"error": f"Falha na solicitação: {str(e)}"}), 500

    return jsonify({"error": f"Falha ao obter tickets: {response_tickets.status_code}"}), 500

@app.route('/webhook/consultaclienteid', methods=['GET']) 
def dados_rece():
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
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    }

    response_tickets = requests.get(url, headers=headers)
    print("1", response_tickets)

    if response_tickets.status_code == 200:
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 40,
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
def consultar_detalhes_do_ticket(user_id):
    url_ticket = f"https://vittel.bolddesk.com/api/v1/tickets"
    headers = {
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
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
    dadoss = request.args  
    print("12", dadoss)
    
    if 'cnpj_cpf' in dadoss and dadoss['cnpj_cpf']:
        return acharocliente(dadoss)
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
    
################################################################################################    
    # ABRIR TICKET
def formatt_cnpj_cpf(value):
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

def acharoccliente(dadoss):
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    }

    response_tickets = requests.get(url, headers=headers)
    

    if response_tickets.status_code == 200:
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 40,
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

def Abrir_Ticket(user_id, dadoss):
        dadoss = dict(dadoss)
        extracted_data = {key: dadoss.get(key) for key in ["Assunto", "Categoria", "Descrição"]}
        print(extracted_data)
        category_ids = {
            "Telefonia IP": 11,
            "PABX IP": 12,
            "Ramais Hardphone": 13,
            "Ramais Softphone": 14,
            "Ramais Agentes": 15,
            "Call Center": 16,
            "Sip Trunk": 17,
            "Chat": 18,
            "Omnichannel": 19,
            "WhatsApp Web": 20,
            "WhatsApp API Cloud": 21,
            "Cloud Server": 22,
            "SMS": 23
        }
        
        user_selection = dadoss.get('Categoria')
        category_id = category_ids[user_selection]
        
        now = datetime.utcnow()
        dueDate = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
        
        ticket_data = {
            "brandId": 1,
            "subject": extracted_data['Assunto'],
            "categoryId": category_id,  
            "isVisibleInCustomerPortal": True,
            "requesterId": user_id,  
            "description": extracted_data['Descrição'],
            "priorityId": 1,
            "dueDate": dueDate,
            "ticketPortalValue": 0
        }
        
        url_ticket = "https://vittel.bolddesk.com/api/v1/tickets"
        headers = {
            "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU=",
        }
        
        response_ull = requests.post(url_ticket, headers=headers, json=ticket_data) 
        print("1", response_ull.status_code)
        if response_ull.status_code == 201:
            
           print(response_ull.text)
           
           return "true", 201, response_ull.json()
        else:
            return "false", 400

@app.route('/webhook/opent', methods=['POST']) 
def dados_booti():
    dadoss = request.args  
    print("12", dadoss)
    
    if 'cnpj_cpf' in dadoss and dadoss['cnpj_cpf']:
        return acharoccliente(dadoss)
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
#############################################################################################
def formatt_cnpj_cpf(value):
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

def acharocliente(dadoss):
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    }

    response_tickets = requests.get(url, headers=headers)
    print("1", response_tickets)

    if response_tickets.status_code == 200:
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 40,
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
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
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
    url = "https://vittel.bolddesk.com/api/v1.0/tickets"
    headers = {
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    }

    response_tickets = requests.get(url, headers=headers)
    print("1", response_tickets)

    if response_tickets.status_code == 200:
        url_contatos = "https://vittel.bolddesk.com/api/v1/contacts"
        params = {
            "PerPage": 40,
            "Page": 1,
        }
        try:
            while True:
                response_contatos = requests.get(url_contatos, headers=headers, params=params)
                print("2", response_contatos.text)
                response_contatos.raise_for_status()
                if params["Page"] >=21:
                    break
                if response_contatos.status_code == 200:
                    dados_bold_desk = response_contatos.json().get("result", [])
                    print("3", dados_bold_desk)

                    for contact in dados_bold_desk:
                        if 'contactExternalReferenceId' in contact and contact['contactExternalReferenceId'] == format_cnpj_cpf(dados['cnpj_cpf']):
                            if 'userId' in contact:
                                user_id = contact['userId']
                                print("123333", user_id)
                                return agenteachado(user_id)
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

def agenteachado(user_id): 
    url_agente = f"https://vittel.bolddesk.com/api/v1/tickets/"
    params = {
        "Q": [f"requester:[{user_id}]", "status:[1,2]"]
    }
    headers = {
        "x-api-key": "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    }

    response = requests.get(url_agente, headers=headers, params=params)
    print("22", response)

    if response.status_code == 200:
        # Assuming the response is a JSON object with a 'result' field containing a list
        results = response.json().get("result", [])

        if results:
            # Assuming the first item in the list contains the ticket information
            ticket_info = results[0]

            # Extracting the required fields
            agente = ticket_info.get("agent", {})
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

            # You can now use these variables in your code
            # For example, you can return them as a dictionary:
            return {
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
            }
        else:
                return "Não existe tickets."

        return "Nenhum resultado encontrado na resposta."

    return f"Falha ao consultar detalhes do ticket para UserID"

@app.route('/webhook/detalhesticket', methods=['GET']) 
def dados_recebidos2():
    dados = request.args  
    print("12", dados)
    
    if 'cnpj_cpf' in dados and dados['cnpj_cpf']:
        return encontrarcliente(dados)
    else:
        return jsonify({"message": "Os parâmetros são necessários"}), 400
    

        
if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
    
    
    
    