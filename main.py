import discord
import logging
import os

from event_management import clean_event, update_event, update_role_for_user

# TODO(tunacom): This can eventually be deleted.
logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG)

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'discord_token')


# TODO(tunacom): Add some type hints.
class MyClient(discord.Client):

    async def on_scheduled_event_create(self, event):
        logging.debug('Event creation event: %s', event.id)
        await update_event(event)

    async def on_scheduled_event_delete(self, event):
        logging.debug('Event deletion event: %s', event.id)
        await clean_event(event)

    async def on_scheduled_event_update(self, before, after):
        logging.debug('Event update event: %s', after.id)
        await clean_event(before)
        if after.status in [
                discord.EventStatus.scheduled, discord.EventStatus.active
        ]:
            await update_event(after)

    async def on_scheduled_event_user_add(self, event, user):
        logging.debug('User add event: %s, %s', event.id, user.name)
        await update_role_for_user(event, user)

    async def on_scheduled_event_user_remove(self, event, user):
        logging.debug('User remove event: %s, %s', event.id, user.name)
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
