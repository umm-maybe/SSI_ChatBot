from Reddit_ChatBot_Python import ChatBot, RedditAuthentication, CustomType
from simpletransformers.language_generation import LanguageGenerationModel

PATH_TO_MODEL = "best_model" #Put the path to your model here!
#Make false if you dont want to use ur gpu.
USE_CUDA = False
#CUDA cuts generation time in half. Make sure you follow github page if you want to set this to True.

# create authentication with username and pass
reddit_authentication = RedditAuthentication.PasswordAuth(reddit_username="", reddit_password="")

# instantiate the chatbot
chatbot = ChatBot(print_chat=True, store_session=True, log_websocket_frames=False,  # some parameters u might wanna know
                  authentication=reddit_authentication)

# you can add a rate limit like so:
chatbot.enable_rate_limiter(max_calls=23,  # how many messages will be sent by the bot
                            period=1.5  # in what period (minutes)
                            )

memory = {} # to avoid crosstalk between conversations, store memories in dictionary keyed by channel_url

# now you can add hooks which will be executed when a frame is received like so:
@chatbot.event.on_message
def gen_response(resp):  # resp is a SimpleNamespace that carries all the data of the received frame
    if resp.user.name == chatbot.get_own_name():  # return if the message is from the bot
        return True
    optPrompt = resp.message
    chatbot.send_typing_indicator(resp.channel_url)
    global memory
    if not(resp.channel_url in memory):
        print('I do not remember ' + resp.user.name + ', starting new conversation.')
        memory[resp.channel_url] = ''
    formattedPrompt = '<|sor|>' + optPrompt + '<|eor|><|sor|>'
    if (len(memory[resp.channel_url]) == 0):
        formattedPrompt = '<|soss|><|sot|>' + optPrompt + '<|eot|><|sor|>'
    memory[resp.channel_url] += formattedPrompt
    print('\nPROMPT:' + formattedPrompt + '\n')
    print('\nMEMORY:' + memory[resp.channel_url] + '\n')
    model = LanguageGenerationModel("gpt2", PATH_TO_MODEL, use_cuda=USE_CUDA)
    text_generation_parameters = {
		'max_length': 50,
		'num_return_sequences': 1,
		'prompt': memory[resp.channel_url],
		'temperature': 0.8, #0.8
		'top_k': 40,
}
    output_list = model.generate(prompt=memory[resp.channel_url], args=text_generation_parameters)
    response = output_list[0]
    response = response.replace(memory[resp.channel_url], '')
    i = 0
    cleanStr = ''
    print(response)
    for element in response:
        if element == '<':
            i = 1
        if i == 0 and element != '!':
            cleanStr += element
        if element == '>':
            i = 0
    if not cleanStr:
        cleanStr = 'Idk how to respond to that lol.'
    memory[resp.channel_url] += cleanStr + "<|eor|>"
    memory[resp.channel_url] = memory[resp.channel_url][-500:] # hacky - using EXPERIMENTAL_MEMORY default setting
    chatbot.stop_typing_indicator(resp.channel_url)
    chatbot.send_message(cleanStr,resp.channel_url)
    return True  # return true if you want to be done with checking the other hooks, otherwise return None or False
        # keep in mind that first added hooks get executed first

# there are also other types of hooks like this one for invitations
@chatbot.event.on_invitation
def on_invit(resp):
    global memory
    if resp.channel_type == CustomType.group:
        invit_type = "group chat"
    elif resp.channel_type == CustomType.direct:
        invit_type = "DM"
    else:
        invit_type = None
    print(f"got invited to {invit_type} by {resp.data.inviter.nickname}")
    chatbot.accept_chat_invite(resp.channel_url)
    memory[resp.channel_url] = ''
    chatbot.send_message("Hey!", resp.channel_url)
    return True


# or on ready hook
@chatbot.event.on_ready
def report_channels(_):
    channels = chatbot.get_channels()
    print("Now chatting with "+ str(len(channels)) + " Redditors")

# wanna check invitations on start? i got you
@chatbot.event.on_ready
def check_invites(_):
    global memory
    invites = chatbot.get_chat_invites()
    for invite in invites:
        print(f"invited to chat by {invite.inviter} with the message {invite.last_message.message}")
        chatbot.accept_chat_invite(invite.channel_url)
        chatbot.send_message("Hey!", invite.channel_url)
        memory[invite.channel_url] = '' # initialise memory for conversation
    return True

# and finally, run forever...
chatbot.run_4ever(auto_reconnect=True)
# set auto_reconnect to True so as to re-connect in case remote server shuts down the connection after some period of time
