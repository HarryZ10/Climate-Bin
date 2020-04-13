#  ip = request.headers.get('X-Forwarded-For', request.remote_addr)
#             ipList = ip.split(",")
#             locationData = requests.get(f'https://ip-geolocation.whoisxmlapi.com/api/v1?apiKey=at_DYkKn1tQbYef7QqaIM8zz19SONxK2&ipAddress={ipList[0]}').content
#             locationData = json.loads(locationData)
# https://ip-geolocation.whoisxmlapi.com/api
