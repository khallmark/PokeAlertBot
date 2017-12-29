import requests
import json
import time

payload = {"last_id": "0"}

cont = True

while cont:
    r = requests.get("http://pokenotifier.com/data", params=payload)

    data = json.loads(r.text)

    data.sort(key=id, reverse=True)
    #print(data[0])

    lastid = data[0]["id"].split("-")[1]
    print(lastid)

    time.sleep(2)
    payload = {"last_id": lastid}

