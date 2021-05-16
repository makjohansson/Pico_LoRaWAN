from machine import UART, Pin
from lib.error import RAK811TimeoutError

class BoardRAK811UART():

    # Last line read from UART, used to stop reading and return response
    GET_CONFIG_RESPONSE = 'DownLinkCounter'
    OK_RESPONSE = 'OK '
    ACK_RESPONSE = 'at+recv'
    RESTART_RESPONSE = 'Initialization OK'

    # Timeout for response from UART
    # RAK811 response time is normally less than 1.5 seconds (ms)
    RESPONSE_TIMEOUT = 8000
    # A command ends with <CR><LF> i.e \r\n
    CRLF = '\r\n'

    PORT = 0
    BAUDRATE = 115200

    def __init__(self, port=PORT, baudrate=BAUDRATE, response_timeout=RESPONSE_TIMEOUT):
	    self.uart = UART(port, baudrate, timeout=response_timeout)
            self.led = Pin(25, Pin.OUT)

    
    def send_command(self, command):
        """
        Send AT command to the module. at+ and the <CR><LF> (i.e \r\n) are appended to the command
        in this function.
        """
        self.uart.write('at+{}{}'.format(command, self.CRLF))
    
    def get_response(self, stop_response, list_response=False):
        """
        Receive response from the RAK811 module, if response not received in time
        the RAK811TimeoutError will be raised.
        When expected response consist of more than one line, list_response must be set to True
        If an error accurse, that error code will be returned
        """	
        response = ''
        error = False
        try:
            if not list_response:
                while not response.startswith(stop_response):
                    data = self.uart.readline()
                    if data is not None:
                        response = data.decode('ascii')
                        response = response.rstrip(self.CRLF)
                        if response.startswith('ERROR'):
                            error = True
                            break
                    else:
                        raise RAK811TimeoutError('Response timeout', response)
            else:
                response_list = []
                while not response.startswith(stop_response):
                    data = self.uart.readline()
                    if data is not None:
                        response = data.decode('ascii')
                        response = response.rstrip(self.CRLF)
                        if response.startswith('ERROR'):
                            error = True
                            break
                        response_list.append(response)
                    else:
                        raise RAK811TimeoutError('Response timeout', response)
                if not error:
                    response = response_list
        except RAK811TimeoutError:
            pass
        return response

    def get_downlink_response(self):
        response = self.get_response(self.ACK_RESPONSE)
        return response

    def get_lora_config(self):
        config_dict = {}
        self.send_command('get_config=lora:status')
        response = self.get_response(self.GET_CONFIG_RESPONSE, True)

        for setting in response:
            k_v = setting.split(':')
            config_dict[k_v[0]] = k_v[1].strip()
        
        return config_dict
    
    def _reset_lora(self):
        '''
        Reset RAK811 LoraWAN config
        '''
        self.send_command('set_config=lora:default_parameters')
        print(self.get_response(self.OK_RESPONSE))
    
    def _reset_device(self):
        '''
        Reset RAK811 device config
        Return True if no Error
        '''
        self.send_command('set_config=device:restart')
        response_list = self.get_response(self.RESTART_RESPONSE, True)
        if isinstance(response_list, list):
            print('Board reset')
            for response in response_list: [print(response)]
            return True
        else:
            print(response_list)
            return False


    def hard_reset(self):
        '''
        Reset RAK811 to default settings
        '''
        if(self._reset_device()):
            self._reset_lora()
    
    def sleep(self, status):
        '''
        status  0 wake up,
                1 sleep
        '''
        self.send_command('set_config=device:sleep:{}'.format(status))
        print(self.get_response(self.OK_RESPONSE))

    def led(self, status):
        '''
        Pico's on-board led, 1=on, 0=off
        '''
        self.led(status)
    



        