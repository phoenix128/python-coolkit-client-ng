# Sonoff client with LAN mode support

Client for Sonoff devices using eWeLink access


API keys retrieval inspired on: https://github.com/peterbuga/HASS-sonoff-ewelink
LAN mode communication inspired on: https://github.com/barbieri/pysonofflan/tree/V3-Firmware-fixes

**REQUIRES SONOFF FIRMWARE 3.3.x or above**

## Usage example

```
#!/usr/bin/env python
import asyncio

from coolkit_client import CoolkitSession, CoolkitDevicesRepository
from coolkit_client.device_control import CoolkitDeviceControl
from coolkit_client.discover import CoolkitDevicesDiscovery


async def listener(switch: CoolkitDeviceSwitch, state: bool) -> None:
    print("State changed to " + str(state))


async def start():
    # Cloud connection is initially required to retrieve the device api-key
    # The system will operate in LAN mode once started
    await CoolkitSession.login(
        username='my@email.com',
        password='IDoNotTellYou!',
        region='eu'
    )

    # Retrieve cloud devices list and API keys
    await CoolkitDevicesDiscovery.discover()
    await asyncio.sleep(2)

    # Get a specific device (identified by its ID)
    my_device = CoolkitDevicesRepository.get_device('1000012345')

    # Register an event change callback (more than one can be registered)
    my_device.add_state_callback('test-listener', listener)

    # Blink the first switch of our device
    await my_device.switches[0].set_state(True)
    await asyncio.sleep(1)
    await my_device.switches[0].set_state(False)

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())

```
