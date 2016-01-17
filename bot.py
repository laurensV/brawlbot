import discord
import logging
import requests
import getpass
import urllib2,cookielib
from BeautifulSoup import BeautifulSoup

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

client = discord.Client()
email = "laurensverspeek@outlook.com"
password = ""

if not email:
    email = raw_input('Email: ')
else:
	print email
if not password:
    password = getpass.getpass('Password:')
    
print('\nTrying to log in...')
client.login(email, password)

if not client.is_logged_in:
    print('Logging in to Discord failed')
    exit(1)

@client.event
def on_message(message):
    args = message.content.split(' ')
    command = args.pop(0)
    if (command == '!rank'):
        modes = []
        regions = []
        options = []
        user_name_list = ""
        for arg in args:
            #check empty argument
            if not arg:
                continue
            if (arg.lower() in ['1v1', '2v2']):
                modes.append(arg.lower())
            elif (arg.lower() in ['eu', 'us', 'sea', 'na']):
            	if(arg.lower()=='na'):
            		regions.append('us')
            	else:
                	regions.append(arg.lower())
            elif (arg.lower() in ['--exact', '--first', '--all']):
                options.append(arg.lower())
            else: 
                user_name_list += arg + " " 
        
        # default values when not specified
        if not user_name_list:
            user_name_list = message.author.name

        user_name_list = user_name_list.split("&&")
        
        if not modes:
            modes = ['1v1']
        if not regions:
            regions = ['eu', 'us', 'sea']
        if not options:
            options = ['--first']

        
        for user_name in user_name_list:
            reply = ""
            #removing trailing spaces
            user_name = user_name.strip()
            user_found = False;
            for mode in modes:
                for region in regions:
                    url = 'http://www.brawlhalla.com/rankings/'+region+'/'+mode+'/?p=' + user_name
                    response = requests.get(url)
                    if(response.status_code == 200):
                        parsed_html = BeautifulSoup(response.content)
                        users_temp =  parsed_html.body.findAll('td', attrs={'class':'pnameleft'})
                        if not users_temp:
                            continue
                        
                        users = []

                        if ('--exact' not in options or '--all' in options):
                            # add first result to the list                        
                            users.append(users_temp.pop(0))
                        if ('--first' not in options or '--all' in options):
                            # add exact results to the list                        
                            for user in users_temp:
                                if(user.text.lower() == user_name.lower()):
                                    users.append(user)
                        elif ('--exact' in options):
                            #both first and exact are in options, check first result
                            user = users_temp.pop(0)
                            if(user.text.lower() == user_name.lower()):
                                users.append(user)
                            
                        if not users:
                            continue
    
                        if (user_found == False):
                            user_found = True                
                        
                        for user in users:
                            if (mode == '1v1'):
                                reply += '**'+ region.upper() + ' ' + mode + '**' + "\tuser: **" + user.text + "**"
                            elif (mode == '2v2'):
                                user_names = user.parent.findAll('td', attrs={'class':'pnameleft'})                            
                                reply += '**'+ region.upper() + ' ' + mode + '**' + "\tusers: **" + user_names[0].text + "** & **"+ user_names[1].text + "**" 
                            user_info = user.parent.findAll('td', attrs={'class':'pcenter'})
                            reply += "\trank: **" + user_info[0].text + "**"
                            reply += "\twin-loss: **" + user_info[1].text + "**"
                            reply += "\telo: **" + user_info[2].text + "**\n"
                    else:
                        reply = "Couldn't reach brawhalla rankings.."
                        break
                
            if not user_found:
                reply = "Couldn't find user " + user_name
            client.send_message(message.channel, reply.encode('utf-8'))

    if (command == '!links'):
        options = []
        for arg in args:
            #check empty argument
            if not arg:
                continue
            options.append(arg.lower())
            
        urls = {}
        urls['steam'] = "http://steamcommunity.com/app/291550"
        urls['wiki'] = "http://wiki.brawlhalla.com/"
        urls['rankings'] = "http://www.brawlhalla.com/rankings"
        urls['reddit'] = "http://brawlhalla.reddit.com"
        urls['home'] = "http://www.brawlhalla.com/"
        urls['twitter'] = "https://twitter.com/brawlhalla"
        urls['twitch'] = "http://www.twitch.tv/brawlhalla"
        urls['youtube'] = "https://www.youtube.com/user/brawlhalla"
        urls['facebook'] = "https://www.facebook.com/Brawlhalla/"
        urls['web'] = "http://steamcommunity.com/groups/WEUB"
        
        reply = "Useful links:"
        for name,url in urls.iteritems():
            if(name in options or not options):
                reply += "\n**"+name+":** \t" + url
        
        client.send_message(message.channel, reply.encode('utf-8'))
        
    if (command == '!weapons'):
        chararg = ""
        for arg in args:
            #check empty argument
            if not arg:
                continue
            chararg += arg.lower().replace("+", " ").replace("_", " ") + " "
        chararg = chararg.strip()
        url = 'http://wiki.brawlhalla.com/w/Weapons'
        response = requests.get(url)
        if(response.status_code == 200):
            parsed_html = BeautifulSoup(response.content)
            chars = parsed_html.body.find('a', attrs={'title':'Ada'}).parent.parent.parent.findAll('li')
            reply = "Weapons used by Legends:"            
            for char in chars:
                parts = char.text.split(":")
                if(parts[0].lower() == chararg or not chararg):
                    weapons = parts[1].split(" and ")
                    reply += "\n"+parts[0]+":\t**"+weapons[0]+"** + **" + weapons[1] + "**"

        else:
            reply = "Can't reach brawlhalla wiki"
        
        client.send_message(message.channel, reply.encode('utf-8'))
    
    if (command == '!stats'):
        char = ""
        for arg in args:
            #check empty argument
            if not arg:
                continue
            temp = arg.lower().replace("+", "_") + "_"
            char += temp[0].upper() + temp[1:]
        
        if not char:
            reply = "Please pick a character (example: !stats scarlet)"
        else:
            char = char[:-1]
            url = 'http://wiki.brawlhalla.com/w/' + char
            response = requests.get(url)
            if(response.status_code == 200):
                parsed_html = BeautifulSoup(response.content)
                reply = "Stats for **"+char+"**:\n" 
                parts = parsed_html.body.find('div', attrs={'class':'thumbcaption'}).text.split(": ")
                reply += "\tStrength: **" + parts[1][0] + "**\n" 
                reply += "\tDexterity: **" + parts[2][0] + "**\n" 
                reply += "\tArmor: **" + parts[3][0] + "**\n" 
                reply += "\tSpeed: **" + parts[4][0] + "**\n" 
    
            else:
                reply = "Can't find character"
        
        client.send_message(message.channel, reply.encode('utf-8'))
        
    if (command == '!queue'):
        modes = []
        regions = []
        for arg in args:
            #check empty argument
            if not arg:
                continue
            if (arg.lower() in ['1v1', '2v2']):
                modes.append(arg.lower())
            elif (arg.lower() in ['eu', 'us', 'sea', 'na']):
                regions.append(arg.lower())
    
        if not modes:
            modes = ['1v1']
        if not regions:
            regions = ['eu']
        reply = ""
        for mode in modes:
            for region in regions:
                if region == 'us':
                    region = 'na'
                arg2v2 = ""
                if(mode == '2v2'):
                    arg2v2 = '2v2'
                url = 'http://brawlmance.com/top/'+arg2v2+region+'.php'
                hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                       'Accept-Encoding': 'none',
                       'Accept-Language': 'en-US,en;q=0.8',
                       'Connection': 'keep-alive'}
                
                req = urllib2.Request(url, headers=hdr)
                
                try:
                    page = urllib2.urlopen(req)
                    content = page.read()
                    parsed_html = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
                    reply += "\nQueue for **"+mode+" "+region+"**:"
                    partsWrapper = parsed_html.findAll("tr")
                    for partWrapper in partsWrapper:
                        parts = partWrapper.findAll("td")
                        try:
                            reply += "\n\tUser: **"+parts[1].text+"**\t rank: **"+parts[0].text+"**\t"+parts[2].text.replace("minutes", "minutes, ")[:-2]
                        except IndexError:
                            reply += "\n\t"+parts[0].text
                except Exception:
                    reply = "  can't reach Brawlmance.."
                    break
                
        client.send_message(message.channel, reply[1:].encode('utf-8'))
        
    if (command == '!help'):
        options = []
        for arg in args:
            #check empty argument
            if not arg:
                continue
            options.append(arg.lower())
            
        functions = {}
        functions['rank'] = "Get rankings for brawlhalla\n\t\t\tArguments (order not important):\n\t\t\t\tyour **username** (defaults to discord username)(use && for multiple usernames)\n\t\t\t\t**1v1**, **2v2**(defaults to **1v1**)\n\t\t\t\t**eu, us, sea** (defaults to all)\n\t\t\t\t**--exact** (for only exact username matches)\n\t\t\t\t**--first** (for the first result) (defaults to --first)\n\t\t\t\t**--all** (for both exact and the first result)"
        functions['queue'] = "See who of the top 100 players is playing ranked (brawlmance.com)\n\t\t\tArguments (order not important):\n\t\t\t\t**1v1**, **2v2**(defaults to **1v1**)\n\t\t\t\t**eu, us, sea** (defaults to eu)"
        functions['help'] = "See this help text \n\t\t\tArguments:\n\t\t\t\t**command** (defaults to all commands)"
        functions['stats'] = "Get stats for a character\n\t\t\tArguments:\n\t\t\t\t**Character name** (required)"
        functions['weapons'] = "Get weapons for a character\n\t\t\tArguments:\n\t\t\t\t**Character name** (defaults to all characters)"
        functions['links'] = "See useful links for brawlhalla \n\t\t\tArguments:\n\t\t\t\t**site** (defaults to all useful sites)"
        
        reply = "**HELP** for brawlbot v1.0\n\n"
        for key,value in functions.iteritems():
            if (key in options or not options):
                reply += "**!" + key + "**:\t" + value + "\n\n"
        reply += "Made by @Laurens. Donations to https://www.paypal.me/laurensv"
        client.send_message(message.channel, reply.encode('utf-8'))

@client.event
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run()