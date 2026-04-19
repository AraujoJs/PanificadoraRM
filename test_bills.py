import urllib.request
import json

base_url = "http://127.0.0.1:5000"

req = urllib.request.Request(f"{base_url}/auth/entrar", data=json.dumps({"email": "joao@panificadora.com", "password": "admin1234"}).encode(), headers={"Content-Type": "application/json", "Accept": "application/json"})
with urllib.request.urlopen(req) as res:
    data = json.loads(res.read())
    token = data['token']

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

req = urllib.request.Request(f"{base_url}/api/v1/contas-pagar/", headers=headers)
with urllib.request.urlopen(req) as res:
    bills = json.loads(res.read())

if not bills:
    print("No bills found")
else:
    for b in bills:
        if b['status'] != 'pago':
            print(f"Paying bill {b['description']} ({b['bill_id']})")
            req = urllib.request.Request(f"{base_url}/api/v1/contas-pagar/{b['bill_id']}/pagar", data=json.dumps({}).encode(), headers=headers)
            try:
                with urllib.request.urlopen(req) as pay_res:
                    print(pay_res.getcode(), pay_res.read().decode())
            except Exception as e:
                print("ERROR:", e)
                try:
                    print(e.read().decode())
                except:
                    pass
            break
