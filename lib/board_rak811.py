from machine import UART
from lib.error import RAK811TimeoutError
import time

class BoardRAK811UART():
    
    OK_RESPONSE = 'OK '
    ACK_RESPONSE = 'at+recv'

    # Timeout for response from UART
    # RAK811 response time is normally less than 1.5 seconds 
    RESPONSE_TIMEOUT = 5000 # (ms)
    # A command ends with <CR><LF> i.e \r\n
    CRLF = '\r\n'

    PORT = 1
    BAUDRATE = 115200

    def __init__(self, port=PORT, baudrate=BAUDRATE, response_timeout=RESPONSE_TIMEOUT):
        self.uart = UART(port, baudrate, timeout=response_timeout)

    
    def send_command(self, command):
        """
        Send AT command to the module. at+ and the <CR><LF> (i.e \r\n) are appended to the command
        in this function. Wait 0.2 seconds to ensure the sent command been transferred before asking for the response.
        """
        self.uart.write('at+{}{}'.format(command, self.CRLF))
        time.sleep(0.5)
    
    def get_response(self, list_response=False):
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
                while self.uart.any() > 0:
                    data = self.uart.readline()
                    if data is not None:
                        response = data.decode('ascii')
                        response = response.rstrip(self.CRLF)
                        print(response)
                        if response.startswith('ERROR'):
                            error = True
                            break
                    else:
                        raise RAK811TimeoutError('Response timeout', response)
            else:
                response_list = []
                while self.uart.any() > 0:
                    data = self.uart.readline()
                    if data is not None:
                        response = data.decode('ascii')
                        response = response.rstrip(self.CRLF)
                        print(response)
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
    
    def get_custom_response(self, stop):
        response = ''
        try:
            while not response.startswith(stop):
                data = self.uart.readline()
                if data is not None:
                    response = data.decode('ascii')
                    response = response.rstrip(self.CRLF)
                    if response.startswith('ERROR'):
                            break
        except RAK811TimeoutError:
            response = 'Timeout error'
        return response
    
    def join_response(self):
        return self.get_custom_response(self.OK_RESPONSE)

    def get_downlink_response(self):
        response = self.get_custom_response(self.OK_RESPONSE)
        if response == self.OK_RESPONSE:
            response = self.get_response()
        return response
        

    def get_lora_config(self):
        config_dict = {}
        response = ''
        # After deepsleep RAK811 always returns the ( ERROR 5 : 'There is an error when sending data through the UART port' ) once.
        while type(response) is str: 
            self.send_command('get_config=lora:status')
            response = self.get_response(True)

        for setting in response:
            k_v = setting.split(':')
            config_dict[k_v[0]] = k_v[1].strip()
            if k_v[0] == 'Joined Network': # Ugly solution to a UART problem, must investigate further
                break
        return config_dict
    
    def _reset_lora(self):
        '''
        Reset RAK811 LoraWAN config
        '''
        self.send_command('set_config=lora:default_parameters')
        print(self.get_response())
    
    def _reset_device(self):
        '''
        Reset RAK811 device config
        Return True if no Error
        '''
        self.send_command('set_config=device:restart')
        response_list = self.get_response(True)
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
        print(self.get_response())