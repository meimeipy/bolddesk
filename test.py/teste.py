@app.route("/hubsoft/customer/consulta/cpf", methods=["GET"])
def consulta_cpf():
    token= request.args.get("token")
    if token !=  "c87d9549342e13372f7e0947fb19b766":
        return geraResponse(401, "Token de acesso não fornecido")


    client_id = request.args.get("client")
    document = request.args.get("document")


    if not client_id or (not document):
        return geraResponse(400, "Os parâmetros 'telefone', 'telefone_my', 'document','client' e 'tipo' são obrigatórios")
    authentication = ""
    if client_id == "pontonet":
        authentication =  {
        "client_id": "40",
        "client_secret": "UI5N4UTmZoo9LokVb3MkZZqsTzPkirNmjBOV5ZAQ",
        "username": "vittel@vittel.com" ,
        "password": "kr6uex%$c7ANT4jpz",
        "grant_type": "password",
        "url": "https://api.pontonet.hubsoft.com.br"
         }

    elif  client_id == "deltaconnect":
         authentication =  {
        "client_id": "5",
        "client_secret": "N0GdbCK1c5DVpqNtNOsI4HwgnInPlIjeTh8dM2pk",
        "username": "vittel@api.com" ,
        "password": "c#CuG@£1I0F`L0jCR3[?",
        "grant_type": "password",
        "url": "https://api.deltaconnect.hubsoft.com.br"
         }

    elif client_id == "telecon":
        authentication ={
        "client_id": "5",
        "client_secret": "ZeUqJvHwTpoIGh83HVifDuels4xm69gd3qsFL95z",
        "username": "vittel@api.com.br",
        "password": "2*8q5g7oVtB*&phUkY7b",
        'grant_type': "password",
        "url": "https://api.logininternet.hubsoft.com.br"
        }
    else:
        return geraResponse(response.status_code, f"Erro ao consultar dados do cliente: {response.text}")

    access_token= hubsoft_login(authentication)
    url = authentication ["url"]+"/api/v1/integracao/cliente"

    busca = "cpf_cnpj"

    termo_busca = document
    params = {"busca": busca , "termo_busca": termo_busca}

    headers = {"Authorization": "Bearer " + access_token }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
            clientes = response.json()

    if len(clientes.get("clientes")) > 0:
            return "true"
    else:
            return "false"