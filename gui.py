import PySimpleGUI as sg
from proxy import ServerProcess
from urllib.parse import urlparse
import webbrowser

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Some text on Row 1',  font='Courier 15')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Run'), sg.Button('Exit')] ]

sp = None
# Create the Window
window = sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    print('event', event)
    if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
        print('terminate server and exit')
        if sp:
            sp.stop()
        break
    if event == 'Run':
        print('You entered ', values[0])
        urlp = urlparse(values[0])
        port = 20443
        sp = ServerProcess(('0.0.0.0', port))
        sp.start()

        wan_ip = '192.168.2.2'
        wan_url = urlp._replace(netloc=f'{wan_ip}:{port}').geturl()
        webbrowser.open(wan_url)

window.close()
