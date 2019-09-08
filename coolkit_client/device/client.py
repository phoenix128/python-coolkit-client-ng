"""Service session object"""

import asyncio
import json
import time
from base64 import b64decode, b64encode
from typing import TYPE_CHECKING, Optional

import aiohttp
import requests
from Crypto.Random import get_random_bytes

#pycryptodome
from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from zeroconf import Zeroconf, ServiceBrowser

from ..log import Log

if TYPE_CHECKING:
    from .device import CoolkitDevice


class CoolkitDeviceClient:
    COMMAND_SWITCHES_PATH = '/zeroconf/switches'
    COMMAND_SWITCH_PATH = '/zeroconf/switch'

    _service_browser: ServiceBrowser = None
    _encrypted: bool = False

    def __init__(self, device: 'CoolkitDevice'):
        self.http_session = requests.Session()
        self._device = device

    async def send(self, url: str, params: dict) -> Optional[dict]:
        if self._device.control_url is None:
            Log.error('Device ' + self._device.device_id + ' does not have a local IP')
            return None

        payload = {
            'sequence': str(int(time.time())),
            'deviceid': self._device.device_id,
            'selfApikey': '123',
            'data': json.dumps(params),
            'encrypt': self._encrypted
        }

        if self._encrypted:
            payload = self._encrypt_message(payload)

        request = json.dumps(payload)

        async with aiohttp.ClientSession() as session:
            response = await session.post(self._device.control_url + url, data=request)

        json_res = await response.json()
        if json_res.get('error') != 0:
            Log.error('Error while sending command to device')

        return json_res

    async def send_switch_command(self, params: dict) -> dict:
        if self._device.is_multi_switch_device:
            return await self.send(self.COMMAND_SWITCHES_PATH, params)

        return await self.send(self.COMMAND_SWITCH_PATH, params)

    def _encrypt_message(self, data: dict) -> dict:
        iv = get_random_bytes(16)
        data['iv'] = b64encode(iv).decode("utf-8")

        api_key = bytes(self._device.api_key, 'utf-8')
        plaintext = bytes(data['data'], 'utf-8')

        hash = MD5.new()
        hash.update(api_key)
        key = hash.digest()

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        padded = pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded)
        encoded = b64encode(ciphertext)

        data['data'] = encoded.decode("utf-8")

        return data

    def _decrypt_message(self, message: bytes, iv: bytes) -> bytes:
        try:
            api_key = bytes(self._device.api_key, 'utf-8')
            encoded = message

            hash = MD5.new()
            hash.update(api_key)
            key = hash.digest()

            cipher = AES.new(key, AES.MODE_CBC, iv=b64decode(iv))
            ciphertext = b64decode(encoded)
            padded = cipher.decrypt(ciphertext)
            plaintext = unpad(padded, AES.block_size)

            return plaintext
        except Exception as ex:
            Log.error('Error decrypting for device ' + self._device.device_id + ': ' + format(ex))

    def handle_encrypted_message(self, message: bytes, iv: bytes) -> None:
        """Handle update message in encrypted form"""
        decrypted_message = self._decrypt_message(message, iv)
        self.handle_message(decrypted_message)

    def handle_message(self, message: bytes) -> None:
        """Handle update message"""
        data = json.loads(message.decode('utf-8'))
        self._device.params = data

        print(str(self._device))
        print(data)

        if data.get('switch'):
            self._handle_message_switch(data)
        elif data.get('switches'):
            self._handle_message_switches(data)

    def _handle_message_switch(self, data: dict) -> None:
        """Update device with a single outlet"""
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._device.switches[0].update_state(data['switch'] == 'on'))
        loop.close()

    def _handle_message_switches(self, data: dict) -> None:
        """Update device with multiple outlets"""

        loop = asyncio.new_event_loop()
        for switch in data['switches']:
            index = int(switch['outlet'])
            loop.run_until_complete(self._device.switches[index].update_state(switch['switch'] == 'on'))
        loop.close()
        
    def set_service_browser(self, zeroconf: Zeroconf, name: str) -> None:
        self._service_browser = ServiceBrowser(zeroconf, name, listener=self)

    def update_service(self, zeroconf: Zeroconf, type: str, name: str) -> None:
        info = zeroconf.get_service_info(type, name)

        if info.properties.get(b'encrypt'):
            iv = info.properties.get(b'iv')
            data1 = info.properties.get(b'data1')

            if len(data1) == 249:
                data2 = info.properties.get(b'data2')
                data1 += data2

                if len(data2) == 249:
                    data3 = info.properties.get(b'data3')
                    data1 += data3

                    if len(data3) == 249:
                        data4 = info.properties.get(b'data4')
                        data1 += data4

            self.handle_encrypted_message(data1, iv)
            self._encrypted = True

        else:
            data = info.properties.get(b'data1')
            self.handle_message(data)
            self._encrypted = False

