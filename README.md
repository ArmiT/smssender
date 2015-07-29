# SMSSender

The Simple http server, that can communicate with the GSM modem over serial connection and send sms messages
 
Tested on the modem: Huawei i3131
## Usage

## Installing

You must install next packages:
- [Serial](https://pypi.python.org/pypi/pyserial)
- [python-messaging](https://github.com/pmarti/python-messaging)

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
- Set modem to the USB port
- Install the drivers
- Check whether there a new serial ports in the list of devices.  For example: you should found port with name "HUAWEI Mobile Connect - 3G PC UI Interface"
- For Microsoft Windows OS only: Stop the service, which the occupy serial port. For example "MegaFon Internet Service"
- Add the exception for service and port to the firewall
- Run the server
```
python main.py
```
