"""Devices object"""
from typing import List, Dict, Optional

from .client import CoolkitDeviceClient
from .switch import CoolkitDeviceSwitch


class CoolkitDevice:
    SERVICE_TYPE = "_ewelink._tcp.local."

    def __init__(self, payload: dict):
        self._ip = None
        self._port = None
        self._payload = payload
        self._switches: List[CoolkitDeviceSwitch] = []
        self._populate_components()
        self._client = CoolkitDeviceClient(device=self)

    def get_info(self, param: str):
        if param not in self._payload:
            return None

        return self._payload[param]

    def _populate_components(self):
        if 'switch' in self.params:
            self._switches.append(CoolkitDeviceSwitch(self, 0))
        elif 'switches' in self.params:
            for i in range(0, len(self.params['switches'])):
                self._switches.append(CoolkitDeviceSwitch(self, i))

    @property
    def is_multi_switch_device(self) -> bool:
        return len(self.switches) > 1

    @property
    def switches(self):
        return self._switches

    @property
    def params(self) -> dict:
        return self.get_info('params')

    @params.setter
    def params(self, params: Dict) -> None:
        self._payload['params'] = params

    @property
    def api_key(self) -> str:
        return self.get_info('devicekey')

    @property
    def device_id(self) -> str:
        return self.get_info('deviceid')

    @property
    def name(self) -> str:
        return self.get_info('name')

    @property
    def device_type(self) -> str:
        return self.get_info('type')

    @property
    def device_model(self) -> str:
        return self.get_info('extra')['extra']['model']

    @property
    def product_model(self) -> str:
        return self.get_info('productModel')

    @property
    def brand(self) -> str:
        return self.get_info('brandName')

    @property
    def ip(self) -> Optional[str]:
        return self._ip

    @ip.setter
    def ip(self, ip: Optional[str]) -> None:
        self._ip = ip

    @property
    def port(self) -> Optional[int]:
        return self._port

    @port.setter
    def port(self, port: Optional[int]) -> None:
        self._port = port

    @property
    def control_url(self) -> Optional[str]:
        if self.ip is None or self.port is None:
            return None

        return 'http://' + self.ip + ':' + str(self.port)

    @property
    def is_online(self) -> bool:
        return self.get_info('online')

    @property
    def client(self) -> CoolkitDeviceClient:
        return self._client

    def __repr__(self) -> str:
        return '[' + self.device_id + '] ' + self.brand + ' (' + self.name + ') ' + self.product_model
