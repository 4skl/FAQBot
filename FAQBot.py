import discord
from random import choice
import json, atexit, threading, time

TOKEN = open('token','r').read()

faq_prefix = '!faq'

base_server_datas = {
    'faq': {},
}

message_faq_not_created = 'No FAQ for this server yet'
message_faq_empty = 'The FAQ of this server is actually empty'
message_faq_not_found = 'No FAQ with this name found, use `'+faq_prefix+' list` to see all FAQ\'s'
message_invalid_command = 'Invalid command, see `'+faq_prefix+'` for help'
message_help = '`'+faq_prefix+'` to see this help\n`'+faq_prefix+' add <name> <description>`  to add an faq entry\n`'+faq_prefix+' delete <name>` to delete an faq entry\n`'+faq_prefix+' list` to list all faq of the server\n`'+faq_prefix+' <name>` to show an faq'

data_filepath = './datas.json'

data_file = open(data_filepath, 'r')
try:
    data = json.load(data_file)
except json.JSONDecodeError:
    ersave = open(data_filepath+str(time.time())+'.ersave','w+', encoding="utf-8") # to save erroned datas
    data_file.seek(0)
    ersave.write(data_file.read())
    ersave.close()
    data = {}
data_file.close()

## saving
def save():
    data_file = open(data_filepath, 'w+')
    json.dump(data, data_file)
    data_file.close()

# add data saving at regular intervals
def save_at_interval(interval):
    global save_interval_running
    while save_interval_running:
        save()
        time.sleep(interval)

save_interval_running = True
save_thread = threading.Thread(target=save_at_interval, args=(5,))
save_thread.start()

atexit.register(save)
##

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=message_help.replace('`',''))) # add what activity the bot make

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
                                faq_list_text += '\t' + faq_name + ' : `' + server_faq[faq_name] + '`\n'
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
                        await message.add_reaction('✅') # adding ✅ when added

                elif faq_command.startswith('delete'):
                    if server_id in data:
                        server_faq = data[server_id]['faq']
                        name_to_delete = faq_command[len('delete '):] #TODO ff correct this
                        if name_to_delete in server_faq:
                            del server_faq[name_to_delete]
                            await message.add_reaction('✅') # adding ✅ when deleted
                        else:
                            await message.channel.send(message_faq_not_found)
                    else:
                        await message.channel.send(message_faq_not_created)

                # adding clear command for admins
                elif faq_command == ('clear all'):
                    if message.author.guild_permissions.administrator:
                        data[server_id]['faq'] = {} # empty server faq
                        await message.channel.send('Successfully cleared ✅')
                    else:
                        message.add_reaction('❌') # adding ❌ when the user doesn't have the rights
                else:
                    ''' can be problematic if an faq starts with show, delete, add or list or if is clear all :/
                    if faq_command.startswith('show'):
                        faq_command = faq_command[len('show '):]
                    '''
                    if server_id in data:
                        server_faq = data[server_id]['faq']
                        name_to_show = faq_command
                        if name_to_show in server_faq:
                            await message.channel.send(name_to_show + ' : ' + server_faq[name_to_show])
                        else:
                            await message.channel.send(message_faq_not_found)
                    else:
                        await message.channel.send(message_faq_not_created)
        else:
            await message.channel.send(message_help)

client.run(TOKEN)
print("stoping")
save_interval_running = False
