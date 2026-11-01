"""The interaction context passed to command handlers.

A :class:`Context` bundles the parsed interaction, the command's option values,
and an async HTTP client for followup webhook requests.
"""

from dataclasses import dataclass
from .models import Interaction, ApplicationCommandData, User, Snowflake
from typing import Optional, Any
import httpx
from .responses import MessageResponse


@dataclass
class Context:
    """State and helpers for a single interaction.

    Attributes:
        interaction: The parsed interaction payload from Discord.
        options: The application command data, including supplied option values.
        http: Async HTTP client used for followup webhook requests.
    """

    interaction: Interaction
    options: ApplicationCommandData
    http: httpx.AsyncClient

    @property
    def user(self) -> User:
        """The user who invoked the interaction.

        Guild interactions expose the user through ``member.user``; direct
        message interactions expose it directly on the interaction.

        Raises:
            ValueError: If the payload contains neither ``user`` nor ``member.user``.
        """
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
        """The guild ID where the interaction occurred, or ``None`` in DMs."""
        return self.interaction.guild_id

    @property
    def channel_id(self) -> Optional[Snowflake]:
        """The channel ID where the interaction occurred, if present."""
        return self.interaction.channel_id

    @property
    def _webhook_base(self) -> str:
        return f"https://discord.com/api/v10/webhooks/{self.interaction.application_id}/{self.interaction.token}"

    async def send(self, content: str, ephemeral: bool = False) -> None:
        """Send a followup message through the interaction webhook.

        Args:
            content: The message text to send.
            ephemeral: Whether the message should only be visible to the
                invoking user. Defaults to ``False``.
        """
        message = MessageResponse(content, ephemeral=ephemeral)
        await self.http.post(url=self._webhook_base, json=message.to_payload())

    def get_option_value(self, name: str, default: Any = None) -> Any:
        """Return the value of a command option by name.

        Args:
            name: The option name to look up.
            default: Value returned when the option was not supplied.

        Returns:
            The option value, or ``default`` when it is missing.
        """
        option = self.options.options_by_name.get(name)
        return option.value if option is not None else default
