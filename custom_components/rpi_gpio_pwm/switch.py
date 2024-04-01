"""Support for LED lights that can be controlled using PWM."""
from __future__ import annotations

import logging

from gpiozero import PWMLED
#from gpiozero.pins.pigpio import PiGPIOFactory

import voluptuous as vol

from homeassistant.components.switch import (
    PLATFORM_SCHEMA,
    SwitchEntity,
)
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME, STATE_ON, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_SWITCHS = "switchs"
CONF_PIN = "pin"
CONF_FREQUENCY = "frequency"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SWITCHS): vol.All(
            cv.ensure_list,
            [
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_PIN): cv.positive_int,
                    vol.Optional(CONF_FREQUENCY): cv.positive_int,
                    vol.Optional(CONF_UNIQUE_ID): cv.string,
                }
            ],
        )
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the PWM LED lights."""
    switchs = []
    for switch_conf in config[CONF_SWITCHS]:
        pin = switch_conf[CONF_PIN]
        opt_args = {}
        if CONF_FREQUENCY in switch_conf:
            opt_args["frequency"] = switch_conf[CONF_FREQUENCY]
        #opt_args["pin_factory"] = PiGPIOFactory(host=led_conf[CONF_HOST], port= led_conf[CONF_PORT])
        if CONF_UNIQUE_ID in switch_conf:
            led = PwmSimpleLed(PWMLED(pin, **opt_args), switch_conf[CONF_NAME], switch_conf[CONF_UNIQUE_ID])
        else:
            led = PwmSimpleLed(PWMLED(pin, **opt_args), switch_conf[CONF_NAME])
        switchs.append(led)

    add_entities(switchs)


class PwmSimpleLed(SwitchEntity, RestoreEntity):
    """Representation of a simple one-color PWM LED."""

    def __init__(self, led, name, unique_id):
        """Initialize one-color PWM LED."""
        self._led = led
        self._name = name
        self._unique_id = unique_id
        self._is_on = False

    async def async_added_to_hass(self):
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._is_on = last_state.state == STATE_ON
    
    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the group."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn on a led."""
        self._led.on()
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn off a LED."""
        if self.is_on:
            self._led.off()
        self._is_on = False
        self.schedule_update_ha_state()