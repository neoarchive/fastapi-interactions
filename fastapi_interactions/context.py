from dataclasses import dataclass
from .models import (
    Interaction, ApplicationCommandData,
    User,
    Snowflake
)
from typing import Optional, Any
import httpx
from .responses import MessageResponse


@dataclass
class Context:
    interaction: Interaction
    options: ApplicationCommandData
    http: httpx.AsyncClient

    @property
    def user(self) -> User:
        if self.interaction.user is not None:
            return self.interaction.user
        if (
            self.interaction.member is not None
            and self.interaction.member.user is not None
        ):
            return self.interaction.member.user
        raise ValueError("Interaction does not contain `user` or `member.user`")

    @property
    def guild_id(self) -> Optional[Snowflake]:
        return self.interaction.guild_id

    @property
    def channel_id(self) -> Optional[Snowflake]:
        return self.interaction.channel_id

    @property
    def _webhook_base(self) -> str:
        return f"https://discord.com/api/v10/webhooks/{self.interaction.application_id}/{self.interaction.token}"

    async def send(self, content: str, ephemeral: bool = False) -> None:
        message = MessageResponse(content, ephemeral=ephemeral)
        await self.http.post(
            url=self._webhook_base,
            json=message.to_payload()
        )

    def get_option_value(self, name: str, default: Any = None) -> Any:
        option = self.options.options_by_name.get(name)
        return option.value if option is not None else default
