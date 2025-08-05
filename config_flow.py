import voluptuous as vol
from homeassistant import config_entries
from . import DOMAIN


class ParkingsGentFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            interval = user_input.get("update_interval", 5)
            if interval < 1:
                errors["base"] = "invalid_interval"
            else:
                return self.async_create_entry(title="Parkings Gent", data={
                    "update_interval": interval
                })

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("update_interval", default=5): vol.Coerce(int)
            }),
            errors=errors
        )
