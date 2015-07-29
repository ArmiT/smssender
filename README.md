# SMSSender

The Simple http server, that can communicate with the GSM modem over serial connection and send sms messages
 
Tested on the modem: Huawei i3131
## Usage
After start the server you can send GET requests in the next format:
```
http://<host>[:port]/?c=<command>&access-token=<valid_auth_key>[&params=<params_in_the_json>]
```

Example -  If you want to create sms, Send the request to the server with next parameters:

 * c=send_sms
 * access-token=<valid auth key>
 * params in the next format:

```json
{
    "phone": "89203048606", 
    "text": "Ваша заявка №12346 Принята в обработку. См. http://d3.ru/1dhk54ff"
}
```
Where:
* phone have format: (\+?7|8)(){11} 
* text can contains up to 160 of ascii symbols, or up to 70 cyrillic or other utf-8 symbols    

Parameters should be encoded to the url format.

After processing, server sends response in the next format:
* if all OK
HTTP 200OK
```json
{
    "response": "success"
}
```
* if happens internal error
HTTP 500
```json
{
    "error": "<error description>"
}
```
* if authenticate fails
HTTP 401
```json
{
    "error": "Authenticate error"
}
```

Possible errors:
* the text should not be an empty string
* The text should not be longer than 160 characters to ascii
* The text should not be longer than 70 characters for not ascii
* phone number is required
* phone number has invalid format
* payload is required
* internal modem error. The message not sended
* command is required
* Authenticate error

Full request:
```
192.168.0.175:8080/?c=send_sms&access-token=500a7317788e421227edf73552a4dd10&params={"phone": "%2B79203048606", "text": "Your task №12346 is done"}
```

## Installing

You must install next packages:
* [Serial](https://pypi.python.org/pypi/pyserial)
* [python-messaging](https://github.com/pmarti/python-messaging)

Actualize the .config file. Choose IP address, port for server and parameters for serial connection.
Fill the auth keys.
Ex.
```
[HTTP]
host=192.168.0.175
port=8080

[LOG]
file=app.log

[SERIAL]
port=COM12
baudrate=9600

[AUTH]
key_param=access-token
keys=[{"key": "500a7f0d325e421227edfd2952a4dd10"}, {"key": "54b41191a856acc1be94812d7549d77f"}]
```

Prepare modem
* Set modem to the USB port
* Install the drivers
* Check whether there a new serial ports in the list of devices.  For example: you should found port with name "HUAWEI Mobile Connect - 3G PC UI Interface"
* For Microsoft Windows OS only: Stop the service, which the occupy serial port. For example "MegaFon Internet Service"
8 Add the exception for service and port to the firewall
* Run the server
```
python main.py
```