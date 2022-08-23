from discord import PermissionOverwrite, utils

DESCRIPTION_CHANNEL_PREFIX = 'channel: '
DESCRIPTION_ROLE_PREFIX = 'role: '

# All roles created by the bot will be prefixed with this to avoid the potential
# to delete existing groups.
ROLE_PREFIX = 'event-'
CATEGORY_NAME = 'event channels'


# TODO(tunacom): Add type hints.
def get_channel_and_role_names(event):
    channel_name = None
    role_name_suffix = None
    role_name = None
    for line in event.description.splitlines():
        if line.lower().startswith(DESCRIPTION_CHANNEL_PREFIX):
            channel_name = line[len(DESCRIPTION_CHANNEL_PREFIX):].strip()
        if line.lower().startswith(DESCRIPTION_ROLE_PREFIX):
            role_name_suffix = line[len(DESCRIPTION_ROLE_PREFIX):].strip()

    if role_name_suffix:
        role_name = ROLE_PREFIX + role_name_suffix

    return channel_name, role_name


async def clean_event(event):
    # Channels will be deleted manually, but we still clean up groups.
    _, role_name = get_channel_and_role_names(event)
    role = utils.get(event.guild.roles, name=role_name)
    if role:
        await role.delete()


async def update_event(event):
    channel_name, role_name = get_channel_and_role_names(event)

    role = None
    if role_name:
        role = await event.guild.create_role(name=role_name, mentionable=True)

    if not role:
        return

    async for user in event.users():
        member = event.guild.get_member(user.id)
        await member.add_roles(role)

    if not channel_name:
        return

    # Only create channels in the designated category. Bail out if it doesn't
    # exist to avoid issues.
    category = utils.get(event.guild.categories, name=CATEGORY_NAME)
    if not category:
        return

    channel = utils.get(event.guild.channels, name=channel_name)
    if channel:
        await channel.set_permissions(role, read_messages=True)
    else:
        overwrites = {
            event.guild.default_role: PermissionOverwrite(read_messages=False),
            role: PermissionOverwrite(read_messages=True),
        }
        await event.guild.create_text_channel(name=channel_name,
                                              overwrites=overwrites,
                                              category=category)


async def update_role_for_user(event, user, remove=False):
    _, role_name = get_channel_and_role_names(event)
    role = utils.get(event.guild.roles, name=role_name)
    if not role:
        return

    member = event.guild.get_member(user.id)
    if remove:
        await member.remove_roles(role)
    else:
        await member.add_roles(role)
