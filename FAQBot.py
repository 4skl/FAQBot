import os

import discord
from random import choice
import json, atexit

TOKEN = 'TOKEN'

client = discord.Client()

faq_prefix = '!faq'

base_server_datas = {
    'faq': {},
}

message_faq_not_created = 'No FAQ for this server yet'
message_faq_empty = 'The FAQ of this server is actually empty'
message_faq_not_found = 'No FAQ with this name found, use `'+faq_prefix+' list` to see all FAQ\'s'
message_invalid_command = 'Invalid command, see `'+faq_prefix+'` for help'
message_help = '`'+faq_prefix+'` to see this help\n`'+faq_prefix+' add <name> <description>`\n`'+faq_prefix+' delete <name>`\n`'+faq_prefix+' list`\n`'+faq_prefix+' show <name>`'

data_filepath = './datas.json'

try:
    data_file = open(data_filepath, 'r')
    try:
        data = json.load(data_file)
    except json.JSONDecodeError:
        open(data_filepath+str(time.time())+'.ersave','w+', encoding="utf-8").write(data_file.read())
        data = {}
except FileNotFoundError:
    data_file = open(data_filepath, 'w+')
    data = {}

def on_dest_save():
    data_file = open(data_filepath, 'w+')
    json.dump(data, data_file)
    data_file.flush()
    data_file.close()

atexit.register(on_dest_save)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.content.startswith(faq_prefix):
        if len(message.content) > len(faq_prefix):
            if message.content[len(faq_prefix)] == ' ': #check the space after the !faq => to modify
                faq_command = message.content[len(faq_prefix)+1:]
                server_id = str(message.guild.id)
                if faq_command.startswith('list'):
                    if server_id in data:
                        server_faq = data[server_id]['faq']
                        if len(server_faq) == 0:
                            await message.channel.send(message_faq_empty)
                        else:
                            faq_list_text = 'Server\'s FAQs :\n'
                            for faq_name in server_faq:
                                faq_list_text += '\t' + faq_name + ' : ' + server_faq[faq_name] + '\n'
                            await message.channel.send(faq_list_text)
                    else:
                        await message.channel.send(message_faq_not_created)

                elif faq_command.startswith('add'):
                    if not server_id in data:
                        data[server_id] = base_server_datas.copy()
                    server_faq = data[server_id]['faq']
                    name_end = faq_command.find(' ', len('add ')) #TODO ff correct this
                    if name_end == -1:
                        await message.channel.send(message_invalid_command)
                    else:
                        name_to_add = faq_command[len('add '):name_end] #TODO ff correct this
                        server_faq[name_to_add] = faq_command[name_end:]

                elif faq_command.startswith('delete'):
                    if server_id in data:
                        server_faq = data[server_id]['faq']
                        name_to_delete = faq_command[len('delete '):] #TODO ff correct this
                        if name_to_delete in server_faq:
                            del server_faq[name_to_delete]
                            await message.channel.send('Successfully deleted')
                        else:
                            await message.channel.send(message_faq_not_found)
                    else:
                        await message.channel.send(message_faq_not_created)

                elif faq_command.startswith('show'):
                    if server_id in data:
                        server_faq = data[server_id]['faq']
                        name_to_show = faq_command[len('show '):] #TODO ff correct this
                        if name_to_show in server_faq:
                            await message.channel.send(name_to_show + ' : ' + server_faq[name_to_show])
                        else:
                            await message.channel.send(message_faq_not_found)
                    else:
                        await message.channel.send(message_faq_not_created)
        else:
            await message.channel.send(message_help)

client.run(TOKEN)