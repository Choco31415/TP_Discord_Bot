# Handle imports
from Lounges.lounges import lounges
from config import server_settings
from command_registration import aliases
from discord.utils import get

# Define variables

# Deifne methods
async def process_command_params(message, command_info):
    '''
    Check the parameters of a command.
    :param message: Message that is command.
    :param command_info: Command invoked.
    :return: If parameters are safe or not.
    '''
    channel = message.channel

    args = message.content.split(" ")[1:]
    new_args = []

    params = command_info.get_params()

    pos = 0

    safe = True
    for param in params:
        # Process message argument
        param_name = param["name"]
        param_attributes = param["attributes"] if "attributes" in param else []

        if len(args) > 0:
            arg = args.pop(0)

            if param_name == "username":
                # Check that user exists on server
                new_args.append(get_user(arg, message.guild))
                exists = not new_args[-1] is None
            elif param_name == "lounge":
                # Check that lounge exists on server
                if "extended"  in  param_attributes:
                    lounge_name = "_".join([arg] + args)
                else:
                    lounge_name = arg
                matches = get(lounges, guild=message.guild, name=lounge_name)
                new_args.append(lounge_name)
                exists = not matches is None
            elif param_name == "role":
                # Check that role is in set
                new_args.append(arg)
                roles = server_settings[message.guild.id]["roles"]
                exists = arg in roles
            else:
                # Default pass the old arg
                new_args.append(arg)
                exists = not arg is None
        else:
            arg = None
            new_args.append(None)

            exists = False

        #logger.debug("Processing arg {}, param {}, which exists {}.".format(arg, param, exists))

        # Check that requirements are met
        check = param["check"]
        optional = "optional" in param_attributes

        if optional and not exists:
            new_args.pop(-1)
            break

        if check == "exists" and not exists:
            safe = False
            if not arg is None:
                await channel.send(
                    "{} {} not recognized.".format(param_name.capitalize(), arg))
            else:
                await channel.send(
                    "Missing parameter {}.".format(param_name.capitalize()))
        elif check == "not exists" and exists:
            safe = False
            await channel.send(
                "{} {} already exists.".format(param_name.capitalize(), arg))

        if not safe:
            break

        # Iterate
        pos += 1

    if safe and len(args) > 0:
        new_args.extend(args)

    return safe, new_args

def get_user(arg, guild):
    '''
    Finds a user give a string identifier
    :param arg: The string identifier
    :return: A user, or None if not found
    '''

    for user in guild.members:
        if ">" in arg:
            # User was @
            found = (str(user.id) + ">") in arg

            if "#" in arg:
                found = found and user.discriminator in arg
        else:
            found = user.name.lower() == arg.lower()

        if found:
            return user
    else:
        return None

def resolve_command(command):
    '''
    Handles aliasing.
    :param command: A possible command alias.
    :return: A non-alias command.
    '''
    if command in aliases:
        return aliases[command]
    else:
        return command