from discord import Embed
import __main__
import question

def embedCommands(event):
    aliases = __main__.BotUtils.getCommandAliases(event)
    event = question.QuestionClient.eventDict(event)
    if event == 0: #ns
        embedVar = Embed(title = "Number Sense", description = "Returns a question from a TMSCA Number Sense Test")
        embedVar.add_field(name = "Usage", value = "`t.ns [(question) number | difficulty] [test number] [year]`", inline = False)
        embedVar.add_field(name = "Arguments", value = """*Filters*:
        `(question) number` - Written as q(question number); not recommended with difficulty argument
        `difficulty` - Either easy (Q#1 - 27), medium (Q#28 - 55), or hard (Q#56 - 80); not recommended with question argument
        `(test) number` - Written as t(test number)
        `year` - Written as literal year
        
        All arguments are optional and those left empty will be randomized""", inline = False)
        embedVar.add_field(name = "Aliases", value = ", ".join(aliases), inline = False)
        embedVar.add_field(name = "Example", value = """`t.ns hard 2002`
        Returns a random number sense question between 56 and 80 from a random test from 2002""", inline = False)
    elif event == 1: #cal
        embedVar = Embed(title="Calculator", description="Returns a question from a TMSCA Calculator Test")
        embedVar.add_field(name="Usage", value="`t.ns [(question) number | difficulty] [test number] [year] [nc|geo]`",
                           inline=False)
        embedVar.add_field(name="Arguments", value="""*Filters*:
                `(question) number` - Written as q(question number); not recommended with difficulty or question-type argument
                `difficulty` - Either easy (Q#1 - 27), medium (Q#28 - 55), or hard (Q#56 - 80); not recommended with question argument
                `(test) number` - Written as t(test number)
                `year` - Written as literal year
                `nc|geo` - Either Number Crunch, or Geometry, written as nc and geo respectively; not recommended with question argument

                All arguments are optional and those left empty will be randomized""", inline=False)
        embedVar.add_field(name="Aliases", value=", ".join(aliases), inline=False)
        embedVar.add_field(name="Example", value="""`t.cal gm easy t4`
                Returns a random geometry question between 1 and 27 from Test #4 from a random year""", inline=False)
    elif event == 2: #math
        embedVar = Embed(title="General Math", description="Returns a question from a TMSCA General Math Test")
        embedVar.add_field(name="Usage", value="`t.math [(question) number | difficulty] [test number] [year]`",
                           inline=False)
        embedVar.add_field(name="Arguments", value="""*Filters*:
                `(question) number` - Written as q(question number); not recommended with difficulty or question-type argument
                `difficulty` - Either easy (Q#1 - 17), medium (Q#28 - 35), or hard (Q#56 - 50); not recommended with question argument
                `(test) number` - Written as t(test number)
                `year` - Written as literal year

                All arguments are optional and those left empty will be randomized""", inline=False)
        embedVar.add_field(name="Aliases", value=", ".join(aliases), inline=False)
        embedVar.add_field(name="Example", value="""`t.math easy t7 2015`
                Returns a random general math question between 1 and 27 from Test #7 from 2015""", inline=False)
    elif event == 3: #sci
        embedVar = Embed(title="General Science", description="Returns a question from a TMSCA General Science Test")
        embedVar.add_field(name="Usage", value="`t.sci [(question) number | difficulty] [test number] [year]`",
                           inline=False)
        embedVar.add_field(name="Arguments", value="""*Filters*:
                       `(question) number` - Written as q(question number); not recommended with difficulty or question-type argument
                       `difficulty` - Either easy (Q#1 - 17), medium (Q#28 - 35), or hard (Q#56 - 50); not recommended with question argument
                       `(test) number` - Written as t(test number)
                       `year` - Written as literal year

                       All arguments are optional and those left empty will be randomized""", inline=False)
        embedVar.add_field(name="Aliases", value=", ".join(aliases), inline=False)
        embedVar.add_field(name="Example", value="""`t.sci q34 2011`
                       Returns the 34th science question of a random test from 2011""", inline=False)
    else:
         return False
    return embedVar

def checkCommandEmbed():
    aliases = __main__.BotUtils.getCommandAliases("check")
    embedVar = Embed(title="Check", description="Verifies given answer with actual answer of most recent TMSCA question in channel")
    embedVar.add_field(name="Usage", value="`t.check <answer>`",
                       inline=False)
    embedVar.add_field(name="Arguments", value="`answer` - (Required) Answer of most recent TMSCA question in channel, can either be number (ns, cal) or letter (math, sci)", inline=False)
    embedVar.add_field(name="Aliases", value=", ".join(aliases), inline=False)
    embedVar.add_field(name="Example", value="""`t.c d`
                           Checks if the answer of the most recent question is D""", inline=False)
    return embedVar