import discord
import os

from event_management import clean_event, update_event, update_role_for_user

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'discord_token')


# TODO(tunacom): Add some type hints.
class MyClient(discord.Client):

    async def on_scheduled_event_create(self, event):
        await update_event(event)

    async def on_scheduled_event_delete(self, event):
        await clean_event(event)

    async def on_scheduled_event_update(self, before, after):
        await clean_event(before)
        if after.status in [
                discord.EventStatus.scheduled, discord.EventStatus.active
        ]:
            await update_event(after)

    async def on_scheduled_event_user_add(self, event, user):
        await update_role_for_user(event, user)

    async def on_scheduled_event_user_remove(self, event, user):
        await update_role_for_user(event, user, remove=True)


def main():
    with open(TOKEN_PATH) as handle:
        token = handle.read().strip()

    intents = discord.Intents.default()
    intents.guild_scheduled_events = True
    intents.members = True

    client = MyClient(intents=intents)
    client.run(token)


if __name__ == '__main__':
    main()
