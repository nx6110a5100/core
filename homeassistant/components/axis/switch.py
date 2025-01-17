"""Support for Axis switches."""
from typing import Any

from axis.models.event import Event, EventOperation, EventTopic

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .axis_base import AxisEventBase
from .const import DOMAIN as AXIS_DOMAIN
from .device import AxisNetworkDevice


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Axis switch."""
    device: AxisNetworkDevice = hass.data[AXIS_DOMAIN][config_entry.entry_id]

    @callback
    def async_create_entity(event: Event) -> None:
        """Create Axis switch entity."""
        async_add_entities([AxisSwitch(event, device)])

    device.api.event.subscribe(
        async_create_entity,
        topic_filter=EventTopic.RELAY,
        operation_filter=EventOperation.INITIALIZED,
    )


class AxisSwitch(AxisEventBase, SwitchEntity):
    """Representation of a Axis switch."""

    def __init__(self, event: Event, device: AxisNetworkDevice) -> None:
        """Initialize the Axis switch."""
        super().__init__(event, device)

        if event.id and device.api.vapix.ports[event.id].name:
            self._attr_name = device.api.vapix.ports[event.id].name

    @property
    def is_on(self) -> bool:
        """Return true if event is active."""
        return self.event.is_tripped

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on switch."""
        await self.device.api.vapix.ports[self.event.id].close()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off switch."""
        await self.device.api.vapix.ports[self.event.id].open()
