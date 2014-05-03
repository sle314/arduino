TEMPLATE_FOLDER = "web/templates"
STATIC_FOLDER = "web"

DEBUG = False

IP = "192.168.1.224"
IP_DNS = "arduino.local"
LOCAL = "localhost"

PORT = "5000"
REST_ROOT = "/arduino"
MODE = "/mode"

GATEWAY = "http://161.53.19.65:8080"
NAME = "cyh-00606e334586"
APPLICATIONS = "/m2m/applications"
ACCESS_RIGHTS = "/m2m/accessRights/Locadmin_AR"
CONTAINERS = "/containers"
DESCRIPTOR = "/DESCRIPTOR"
CONTENT_INSTANCES = "/contentInstances"
LATEST_CONTENT = "/latest/content"

AUTH = "http://nsc1.actility.com:8088/m2m/applications/TPK_emVjQGZlci5ociANCg=="
# AUTH = "aHR0cCUzQS8vbnNjMS5hY3RpbGl0eS5jb20lM0E4MDg4L20ybS9hcHBsaWNhdGlvbnMvVFBLX2Q4M2JkZTM3Y2U1MWZiZWIxNGZkYmNiOTIwZTU2ZThk"

POST_AUTH = "http://nsc1.actility.com:8088/m2m/applications/SYSTEM"
# Y29hcCUzQS8vY3loLTAwNjA2ZTMzNDYwMS5hY3RpbGl0eS5jb20lM0E1NjgzL20ybS9hcHBsaWNhdGlvbnMvR0lQ

DEVICE_ID = "Arduino"
# DEVICE_ID = "APP_00137a0000005d98.1"

MAX_NR_VALUES = 20

HARDWARE = [
    {
        'name': 'TinkerKit!',
        'path': 'tinkerkit',
        'modules': [
            {
                'name': 'Thermistor',
                'path': 'thermistor',
                'type': 'Temperature',
                'io': 'input',
                'ad': 'analog',
                'methods': [
                    {
                        'name': 'Read analog value',
                        'path': 'read',
                        'type': 'read',
                        'value_type': 'int',
                        'unit': ''
                    },
                    {
                        'name': 'Read Celsius',
                        'path': 'read_celsius',
                        'type': 'read',
                        'value_type': 'real',
                        'unit': 'C'
                    },
                    {
                        'name': 'Read Fahrenheit',
                        'path': 'read_fahrenheit',
                        'type': 'read',
                        'value_type': 'real',
                        'unit': 'F'
                    }
                ]
            },
            {
                'name': 'LED',
                'path': 'led',
                'type': 'LED',
                'io': 'output',
                'ad': 'analog',
                'methods': [
                    {
                        'name': 'Turn on',
                        'path': 'on',
                        'type': 'call',
                        'value_type': None,
                        'unit': None
                    },
                    {
                        'name': 'Turn off',
                        'path': 'off',
                        'type': 'call',
                        'value_type': None,
                        'unit': None
                    },
                    {
                        'name': 'Get state',
                        'path': 'state',
                        'type': 'read',
                        'value_type': 'bool',
                        'unit': ''
                    },
                    {
                        'name': 'Adjust brightness',
                        'path': 'brightness',
                        'type': 'write',
                        'value_type': 'int',
                        'unit': ''
                    }
                ]
            }
        ],
        'pins': [
            { 'pin': 'I0', 'arduino_pin': 'A0', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'I1', 'arduino_pin': 'A1', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'I2', 'arduino_pin': 'A2', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'I3', 'arduino_pin': 'A3', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'I4', 'arduino_pin': 'A4', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'I5', 'arduino_pin': 'A5', 'io': 'input', 'ad': 'analog' },

            { 'pin': 'O0', 'arduino_pin': 'D11', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'O1', 'arduino_pin': 'D10', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'O2', 'arduino_pin': 'D9', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'O3', 'arduino_pin': 'D6', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'O4', 'arduino_pin': 'D5', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'O5', 'arduino_pin': 'D3', 'io': 'output', 'ad': 'analog' },
        ]

    },

    {
        'name': 'Arduino Yun',
        'path': 'yun',
        'modules': [
            {
                'name': 'digital in',
                'path': 'digital',
                'type': None,
                'io': 'input',
                'ad': 'digital',
                'methods': [
                    {
                        'name': 'Read value',
                        'path': 'read',
                        'type': 'read',
                        'value_type': 'bool',
                        'unit': ''
                    }
                ]
            },
            {
                'name': 'digital out',
                'path': 'digital',
                'type': None,
                'io': 'output',
                'ad': 'digital',
                'methods': [
                    {
                        'name': 'Read value',
                        'path': 'read',
                        'type': 'read',
                        'value_type': 'bool',
                        'unit': ''
                    },
                    {
                        'name': 'Write value',
                        'path': 'write',
                        'type': 'write',
                        'value_type': 'bool',
                        'unit': ''
                    },
                    {
                        'name': 'Toggle value',
                        'path': 'toggle',
                        'type': 'call',
                        'value_type': None,
                        'unit': None
                    }
                ]
            },
            {
                'name': 'analog out',
                'path': 'analog',
                'type': None,
                'io': 'output',
                'ad': 'analog',
                'methods': [
                    {
                        'name': 'Read value',
                        'path': 'read',
                        'type': 'read',
                        'value_type': 'str',
                        'unit': ''
                    },
                    {
                        'name': 'Write value',
                        'path': 'write',
                        'type': 'write',
                        'value_type': 'str',
                        'unit': ''
                    }
                ]
            },
            {
                'name': 'analog in',
                'path': 'analog',
                'type': None,
                'io': 'input',
                'ad': 'analog',
                'methods': [
                    {
                        'name': 'Read value',
                        'path': 'read',
                        'type': 'read',
                        'value_type': 'str',
                        'unit': ''
                    }
                ]
            }
        ],
        'pins': [
            { 'pin': 'A0', 'arduino_pin': 'A0', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'A1', 'arduino_pin': 'A1', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'A2', 'arduino_pin': 'A2', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'A3', 'arduino_pin': 'A3', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'A4', 'arduino_pin': 'A4', 'io': 'input', 'ad': 'analog' },
            { 'pin': 'A5', 'arduino_pin': 'A5', 'io': 'input', 'ad': 'analog' },

            { 'pin': 'A0', 'arduino_pin': 'A0', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'A1', 'arduino_pin': 'A1', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'A2', 'arduino_pin': 'A2', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'A3', 'arduino_pin': 'A3', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'A4', 'arduino_pin': 'A4', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'A5', 'arduino_pin': 'A5', 'io': 'input', 'ad': 'digital' },

            { 'pin': 'D2', 'arduino_pin': 'D2', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D3', 'arduino_pin': 'D3', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D4', 'arduino_pin': 'D4', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D5', 'arduino_pin': 'D5', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D6', 'arduino_pin': 'D6', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D7', 'arduino_pin': 'D7', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D8', 'arduino_pin': 'D8', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D9', 'arduino_pin': 'D9', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D10', 'arduino_pin': 'D10', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D11', 'arduino_pin': 'D11', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D12', 'arduino_pin': 'D12', 'io': 'output', 'ad': 'digital' },
            { 'pin': 'D13', 'arduino_pin': 'D13', 'io': 'output', 'ad': 'digital' },

            { 'pin': 'D2', 'arduino_pin': 'D2', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D3', 'arduino_pin': 'D3', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D4', 'arduino_pin': 'D4', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D5', 'arduino_pin': 'D5', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D6', 'arduino_pin': 'D6', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D7', 'arduino_pin': 'D7', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D8', 'arduino_pin': 'D8', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D9', 'arduino_pin': 'D9', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D10', 'arduino_pin': 'D10', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D11', 'arduino_pin': 'D11', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D12', 'arduino_pin': 'D12', 'io': 'input', 'ad': 'digital' },
            { 'pin': 'D13', 'arduino_pin': 'D13', 'io': 'input', 'ad': 'digital' },

            { 'pin': 'D3', 'arduino_pin': 'D3', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'D5', 'arduino_pin': 'D5', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'D6', 'arduino_pin': 'D6', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'D9', 'arduino_pin': 'D9', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'D10', 'arduino_pin': 'D10', 'io': 'output', 'ad': 'analog' },
            { 'pin': 'D11', 'arduino_pin': 'D11', 'io': 'output', 'ad': 'analog' }
        ]

    }
]