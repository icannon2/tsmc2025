from ..handler import CommandHandlerImpl


class AccountCommandHandler(CommandHandlerImpl):
    command_name = "register"
    description = "register an account"

    allowed_channels: list[str]

    def __init__(self, config: Config):
        self.state = state

        self.allowed_channels = config.allowed_channels
        super().__init__()

    async def handle_command(self, message: Message) -> bool:
        if (
            message.content.startswith("/register")
            and message.channel.id in self.allowed_channels
        ):
            thread = await message.channel.create_thread(
                name="chat", type=ChannelType.private_thread
            )
            if thread:
                await thread.send(
                    f"Hi {message.author.mention}! How can I help you today?"
                )
            else:
                raise Exception("Failed to create a thread")

            model = ChatroomModel(thread_id=thread.id, user_id=message.author.id)
            self.state.session.add(model)
            self.state.session.commit()

            return True
        return False
