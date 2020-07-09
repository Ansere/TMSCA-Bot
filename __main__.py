import os
import question
import embed
import io
import renderer
import base64

from discord import File
from discord import Embed
from discord.ext import commands
from inspect import currentframe, getframeinfo
from dotenv import load_dotenv

load_dotenv()
frameinfo = getframeinfo(currentframe())
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDID = os.getenv('DISCORD_GUILD')
eventNums = {"ns": 80, "cal": 80, "math": 50, "sci": 50}
bot = commands.Bot(command_prefix = 't.')
bot.remove_command("help")


@bot.event
async def on_ready():
    question.ChannelHandler.loadChannels()
    question.QuestionClient.loadQuestions("sci.txt")
    question.QuestionClient.loadQuestions("cal.txt")
    await question.QuestionClient.loadQuestionPics()
    question.Info.loadQuestionsInfo()
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(pass_context = True)
async def help(ctx, *args):
    array = Training(bot).get_commands()
    for com in Training(bot).get_commands():
        array.extend(commands.Bot.get_command(bot, str(com)).aliases)
    if len(args) > 0 and any(args[0] == str(com) for com in array):
        arg = str(bot.get_command(args[0]))
        if question.QuestionClient.eventDict(arg) >= 0:
            await ctx.channel.send(embed=embed.embedCommands(arg))
        elif (arg == "check"):
            await ctx.channel.send(embed = embed.checkCommandEmbed())
        else:
            print("Command of arg " + arg + " not handled in help embeds")
    else:
        embedVar = Embed(title="Commands", description="""All commands start with `t.`
        Use `t.help [command]` to view more info about that command!
        """, color=0x00ff00)
        embedVar.add_field(name="Events", value=", ".join(str(command) for command in Training(bot).get_commands()), inline=True)
        embedVar.add_field(name="Leaderboard", value="lb", inline=True)
        embedVar.set_thumbnail(url="https://cdn.discordapp.com/emojis/729376734549639189.png?v=1")
        await ctx.channel.send(embed=embedVar)

@bot.command(pass_context = True, aliases = ['l'])
async def latex(ctx, *args):
    file = renderer.latexRender(" ".join(args))
    if isinstance(file, str):
        await ctx.channel.send(file)
    else:
        await ctx.channel.send(file=File(file, 'image.png'))

class Training(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @bot.command(pass_context = True, aliases = ["numbersense"])
    async def ns(ctx, *args):
        await BotUtils.sendQuestion(ctx, "ns", args)

    @bot.command(pass_context = True, aliases = ["calculator", "calc"])
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def cal(ctx, *args):
        try:
            await BotUtils.sendQuestion(ctx, "cal", args)
        except(commands.errors.CommandOnCooldown):
            await ctx.channel.send(commands.CommandOnCooldown)

    @bot.command(pass_context = True, aliases = ["generalmath","gm"])
    async def math(ctx, *args):
        await BotUtils.sendQuestion(ctx, "math", args)

    @bot.command(pass_context=True, aliases=["generalscience", "gs", "science"])
    async def sci(ctx, *args):
        await BotUtils.sendQuestion(ctx, "sci", args)

    @bot.command(pass_context=True, aliases=["c"])
    async def check(ctx, *arg):
        await ctx.channel.send(question.QuestionClient.checkQuestion(ctx, arg))

    @cal.error
    async def sendCDError(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'This command is ratelimited, please try again in {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

class Debug(commands.Cog):
    def __init(self, bot):
        self.bot = bot
        self.last_member = None

    @bot.command(pass_context=True)
    async def clearchannels(ctx):
        question.ChannelHandler.channelcheck = {}
        question.ChannelHandler.channelquestion = {}
        question.ChannelHandler.saveChannels()
        print(str(ctx.message.author) + " has wiped channel data")
        await ctx.channel.send("Channel data was wiped!")

class Info(commands.Cog):

    @bot.command(pass_contex = True, aliases = ["i", "stats"])
    async def info(ctx):
        embedVar = Embed(title = "Info", description = "Stats about the bot!")
        embedVar.add_field(name = "Questions", value = str(len(question.QuestionClient.questions)) + " questions from **" +
                str(question.Info.uniquetests) + "** tests from **" + str(question.Info.uniqueyears) + "** years" + """
                **""" + str(question.Info.eqd["ns"]) + "** " + question.QuestionClient.fullName("ns") + " questions" + """
                **""" + str(question.Info.eqd["cal"]) + "** " + question.QuestionClient.fullName("cal") + " questions" + """
                **""" + str(question.Info.eqd["math"]) + "** " + question.QuestionClient.fullName("math") + " questions" + """
                **""" + str(question.Info.eqd["sci"]) + "** " + question.QuestionClient.fullName("sci") + " questions", inline = False)
        await ctx.channel.send(embed = embedVar)

class BotUtils():

    @staticmethod
    def getCommandName(alias):
        return str(bot.get_command(alias))

    @staticmethod
    def getCommandAliases(name):
        return commands.Bot.get_command(bot, name).aliases

    @staticmethod
    async def sendQuestion(ctx, event, args):
        objquestion = question.QuestionClient.getQuestion(ctx, event, args)
        if isinstance(objquestion, str):
            await ctx.channel.send(objquestion)
            return False
        await ctx.channel.send("Question #" + str(objquestion.questionNum) + " from Test #" + str(objquestion.test) + " from " + str(objquestion.year) + ":")
        if bool(objquestion.picstring):
            image = io.BytesIO(base64.b64decode(objquestion.picstring))
            await ctx.channel.send(file = File(image, "image.png"))
        elif objquestion.picstring is False:
            await ctx.channel.send()
        result = ""
        try:
            objquestion.rawquestion.replace("", "")
            image = io.BytesIO(base64.b64decode(objquestion.question))
            await ctx.channel.send(file=File(image, "image.png"))
        except:
            if isinstance(objquestion.question, str):
                if objquestion.question != "":
                    await ctx.channel.send(objquestion.question)
            elif isinstance(objquestion.question, bool):
                await ctx.channel.send("There is supposed to be an image here! Please contact support!")
        if len(objquestion.answerChoices) == 5:
            result += "\n\tA. " + objquestion.answerChoices[0] + "\n\tB. " + objquestion.answerChoices[1] + "\n\tC. " + objquestion.answerChoices[2] + "\n\tD. " + objquestion.answerChoices[3]+ "\n\tE. " + objquestion.answerChoices[4]
        if bool(result):
            await ctx.channel.send(result)

    @staticmethod
    def formatCalAnswers(answer):
        try:
            if "x10" in answer:
                float(answer[:answer.index("x")])
                if ("^" in answer):
                    float(answer[answer.index("^") + 1:])
            else:
                float(answer)
        except:
            return False
        answer = answer.replace(" ", "")
        if answer.startswith("-"):
            answer = answer[1:]
        if "x10" in answer:
            if answer.endswith("x10"):
                answer += "^1"
            if not ("x10^" in answer):
                return False
            x = answer.index("x")
            scalar = answer[:x]
            if not (answer.replace(".", "")[:3].isdigit()):
                return False
            if not (int(answer[0]) > 0) or not ("." in scalar):
                return False
            if not (len(scalar.replace(".", "")) == 3):
                return False
            if not (answer[1] == "."):
                return False
        elif answer.replace(".", "").isdigit():
            if len(answer) == 3 and "0" in answer:
                return False
            if not ("." in answer):
                answer += "."
            if answer.startswith("0"):
                return False
            arr2 = []
            letterno = 0
            swap = False
            if not (len(answer.replace(".", "")) == 3):
                if not (len(answer.replace(".", "")) > 3):
                    return False
                if not (answer.startswith(".") or answer.endswith(".")):
                    return False
                if answer.startswith("."):
                    swap = True
                    answer = answer[::-1]
                for letter in answer:
                    if letter.isdigit() and int(answer[letterno:][:-1]) == 0 and letter == 0:
                        y = 1
                    elif letter == "." or bool(int(answer[letterno:][:-1])):
                        arr2.append(letter)
                    letterno += 1
                if swap == True:
                    arr2.reverse()
                    answer = answer[::-1]
                scalar = "".join(arr2).replace(".", "")
                if not (len(scalar) == 3):
                    return False

        if answer.endswith("x10"):
            return answer + "^1"
        elif "x10" in answer:
            return answer
        elif answer[1] == ".":
            return answer + "x10^0"
        elif answer[2] == ".":
            return answer[0] + "." + answer.replace(".", "")[1:3] + "x10^1"
        elif answer.startswith("."):
            answer = answer[::-1]
            result = answer[0] + "." + answer[1:3] + "x10^" + str(1 - len(answer) + 2)
            return result
        elif answer.endswith("."):
            return answer[0] + "." + answer[1:3] + "x10^" + str(len(answer) - 2)

bot.run(TOKEN)
