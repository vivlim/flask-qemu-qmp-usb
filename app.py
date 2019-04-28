from flask import Flask
import qmp
import subprocess


def get_usb_devices():
    result = subprocess.run(['lsusb'], stdout=subprocess.PIPE)
    devices = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if len(line) > 0:
            sp = line.split(' ')
            device_ids = sp[5]
            device_name = ' '.join(sp[6:])
            devices.append((device_ids, device_name))
    return devices


def get_client():
    client = qmp.QEMUMonitorProtocol(('192.168.1.100', 4444))
    client.connect()
    return client


def add_usb_device(device):
    client = get_client()

    vendorid, productid, deviceid = device
    args = {
        "driver": "usb-host",
        "vendorid": vendorid,
        "productid": productid,
        "id": deviceid
    }
    return client.cmd("device_add", args=args)


def rm_usb_device(device):
    client = get_client()

    _, _, deviceid = device
    args = {
        "id": deviceid
    }
    return client.cmd("device_del", args=args)


# client.command("help")
# client.cmd("device_add", args=build_device_command("0x045e", "0x07a5", "MantaDesktop"))
# keyboard = ("0x045e", "0x07a5", "MantaDesktop")
# print(add_usb_device(client, keyboard))
# print(rm_usb_device(client, keyboard))


app = Flask(__name__)


@app.route('/')
def home():
    devices = get_usb_devices()
    page = []
    page.append('<table><tr><th>device</th><th></th><th></th></tr>')
    for device in devices:
        page.append('<tr><td>{0}</td><td><a href="/add/{1}/{2}">Add</a></td><td><a href="/del/{1}/{2}">Remove</a></td></tr>'.format(device[1], device[0], device[1].replace(' ', '').replace(',', '')))
    page.append('</table>')
    return '\n'.join(page)


@app.route('/add/<device_id>/<name>')
def add_device_route(device_id, name):
    device = ("0x" + device_id.split(':')[0], "0x" + device_id.split(':')[1], name)
    return str(add_usb_device(device)) + home()


@app.route('/del/<device_id>/<name>')
def del_device_route(device_id, name):
    device = ("0x" + device_id.split(':')[0], "0x" + device_id.split(':')[1], name)
    return str(rm_usb_device(device)) + '<hr/>' + home()