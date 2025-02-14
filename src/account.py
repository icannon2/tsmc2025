from discord import Message, TextStyle, ui, Interaction
from .bot import CommandHandlerImpl

accountRoles = {795258895622340619: [1339499087489273868, 1339498929901015100]}


class AccountUI(ui.Modal, title="Feedback"):
    name = ui.TextInput(
        label="Account Name",
        placeholder="Account Name",
    )

    message = ui.TextInput(
        label="Verification Message",
        style=TextStyle.long,
        placeholder="message",
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: Interaction):
        user_id = interaction.user.id
        roles = accountRoles.get(user_id)
        if roles is not None:
            for role in filter(lambda x: x.id in roles, interaction.guild.roles):
                await interaction.user.add_roles(role)
        await interaction.response.send_message(
            f"Thanks for your registration, {self.name.value}!", ephemeral=True
        )

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )


class AccountCommandHandler(CommandHandlerImpl):
    command_name = "account"
    description = "Account command"

    async def handle_command(self, interaction: Interaction) -> bool:
        if Interaction is None:
            return False
        await interaction.response.send_modal(AccountUI())
        return True
