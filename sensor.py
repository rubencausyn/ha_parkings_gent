from __future__ import annotations
import logging
import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "parkings_gent"
_LOGGER = logging.getLogger(__name__)
URL = "https://data.stad.gent/api/explore/v2.1/catalog/datasets/bezetting-parkeergarages-real-time/records?order_by=availablecapacity&limit=30&timezone=Europe%2FBrussels"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    # We will fetch data on every update, so just create one entity per parking result dynamically.
    # However, we need to know the parkings first. Let's fetch once now and create an entity per parking.
    data = await fetch_data()
    entities = []
    for parking in data:
        if "name" in parking:
            entities.append(GentParkingSensor(parking))
    async_add_entities(entities, True)


async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch data")
                return []
            data = await resp.json()
            return data.get("results", [])


class GentParkingSensor(SensorEntity):
    _attr_native_unit_of_measurement = "spaces"
    should_poll = True

    def __init__(self, initial_data):
        self.data = initial_data
        self._attr_unique_id = self.data.get("name")
        self._attr_name = self.data.get("name", "Onbekende Parking")

    async def async_update(self):
        # Fetch fresh data on every update
        data = await fetch_data()
        # Find our parking data by name
        for parking in data:
            if parking.get("name") == self._attr_unique_id:
                self.data = parking
                break

    @property
    def native_value(self):
        return self.data.get("availablecapacity")

    @property
    def extra_state_attributes(self):
        return {
            "total_capacity": self.data.get("totalcapacity"),
            "last_update": self.data.get("lastupdate"),
            "occupation": self.data.get("occupation"),
            "type": self.data.get("type"),
            "description": self.data.get("description"),
            "id": self.data.get("id"),
            "openingtimesdescription": self.data.get("openingtimesdescription"),
            "isopennow": self.data.get("isopennow"),
            "temporaryclosed": self.data.get("temporaryclosed"),
            "operatorinformation": self.data.get("operatorinformation"),
            "freeparking": self.data.get("freeparking"),
            "urllinkaddress": self.data.get("urllinkaddress"),
            "occupancytrend": self.data.get("occupancytrend"),
            "locationanddimension": self.data.get("locationanddimension"),
            "location_lon": self.data.get("location", {}).get("lon"),
            "location_lat": self.data.get("location", {}).get("lat"),
            "text": self.data.get("text"),
            "categorie": self.data.get("categorie"),
            "dashboard": self.data.get("dashboard")
        }
