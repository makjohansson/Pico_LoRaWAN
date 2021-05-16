from lib.error import RAK811TimeoutError
from lib.board_rak811 import BoardRAK811UART


class LoRaWAN():

    config_commands = [
        'set_config=lora:dev_eui:',     # DevEUI 
        'set_config=lora:app_eui:',     # AppEUI
        'set_config=lora:app_key:',     # AppKey
        'set_config=lora:join_mode:',   # mode  
        'set_config=lora:class:',       # loraWAN_class 
        'set_config=lora:region:',      # region 
        'set_config=lora:dr:'           # data_rate 
    ]
    def __init__(self, DevEUI, AppEUI, AppKey, mode=0,loRaWAN_class=0, region='EU868', data_rate=5, port=1):
        """
		mode 	0 = OTAA (default), 1 = ABP

		class 	0 = A (default), 1 = B, 2 = C
		
		region	EU868 (defult)

		data_rate	value 0-5, 5 (default)

		port	port on network server, 1 (default), can also be set when sending
		"""
        self._config_list =[DevEUI, AppEUI, AppKey, mode, loRaWAN_class, region, data_rate]
        self.dev_eui = DevEUI
        self.app_eui = AppEUI
        self.app_key = AppKey
        self.mode = mode
        self.loRaWAN_class = loRaWAN_class	
        self.region = region
        self.data_rate = data_rate
        self.port = port
        
        self._board = BoardRAK811UART()
        self._config = self._board.get_lora_config() 
        self.has_joined = False if self._config['Joined Network'] == 'false' else True

        # Setup configurations
        if not self.has_joined:
            for i in range(len(self.config_commands)):
                self._board.send_command('{}{}'.format(self.config_commands[i], self._config_list[i]))
                response = self._board.get_response(self._board.OK_RESPONSE)
                print(response, self._config_list[i]) 
        
            

    def join(self):
        '''
        Join a network. Return True if join succeed, otherwise False
        '''
        try:
            self._board.send_command('join')
            response = self._board.get_response(self._board.OK_RESPONSE)
            self.has_joined = True
            print(response)
        except RAK811TimeoutError:
            print('Not yet joined')
            return False
        
                    
    def reset(self):
        self._board.hard_reset()
    
    def send(self, data, port=1):
        '''
        Data to send and port to use
        '''
        port = self.port if self.port == port else port 
        command = 'send=lora:{}:{}'.format(port, data)
        self._board.send_command(command)
        response = self._board.get_downlink_response()
        if response == self._board.OK_RESPONSE:
            print('No downlink')
        else:
            downlink_split = response[len(self._board.ACK_RESPONSE):].split(',')
            downlink_dict = {
	            'Port': downlink_split[0],
	            'RSSI': downlink_split[1],
	            'SNR': downlink_split[2],
	            'msg': downlink_split[3].split(':')[1]
            }

            msg = int(downlink_dict['msg'], 16)
            print('Received', msg)  

    def sleep(self):
        '''
        RAK811 to sleep mode
        '''
        self._board.sleep(1)
    
    def wake_up(self):
        '''
        Wake up RAK811
        '''
        self._board.sleep(0)
    
    def led(self, status):
        '''
        Pico's on-board led, 1=on, 0=off
        '''
        self._board.led(status)

        
       