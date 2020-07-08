import random
import renderer as rr

class Question:
    def __init__(self, id, answer, question, answerchoices, picurl):
        id = Question.isIDValid(id)
        self.event = int(id[0])
        self.questionNum = int(id[1])
        self.test = int(id[2])
        self.year = int(id[3])
        self.metadata = int(id[4])
        self.answer = answer
        if question.startswith("-t"):
            latexpic = rr.latexRender(question.replace("-t ", ""))
            if isinstance(latexpic, str):
                print("Invalid LaTeX string of question with id " + self.getID())
                self.question = False
            else:
                self.question = latexpic
                self.rawquestion = question
        else:
            self.question = question
        x = answerchoices.split("|")
        if len(x) != 5 and bool(answerchoices):
            print(answerchoices)
            print("Invalid answer choices of question with id " + self.getID())
        else:
            self.answerChoices = x #optional, List
            self.picstring = picurl


    @staticmethod
    def isIDValid(id: str): #Returns a list, empty if id invalid, split if id valid
        id = id.split("|")
        if len(id) != 5 or not(any([number.isnumeric() for number in id])):
            return []
        if int(id[0]) < 2:
            eventquestions = 80
        else:
            eventquestions = 50
        if not(any([0 <= int(id[0]) <= 3, 0 < int(id[1]) <= eventquestions, 0 < int(id[2]) <= 14])):
            return []
        return id

    def toString(self):
        result = "Question #" + str(self.questionNum) + " from Test #" + str(self.test) + " from " + str(self.year) + ":"
        if self.question == "-p":
            result += "\nPicture-only question"
        else:
            result += "\n" + self.question
        if bool(self.answerChoices):
            result += "\nAnswer choices " + ", ".join(choice for choice in self.answerChoices)
        if bool(self.picstring):
            result += "\nPicstring: " + self.picstring
        return result

    def getID(self):
        return str(self.event) + "|" + str(self.questionNum) + "|" + str(self.test) + "|" + str(self.year) + "|" + str(self.metadata)

    def getPicPath(self):
        return str(self.getID())

class QuestionClient:
    questions = [] #list of all questions
    def __init__(self):
        self

    @staticmethod
    async def loadQuestionPics():
        for question in QuestionClient.questions:
            if bool(question.picstring):
                imgbyte = await rr.renderfromURL(question.picstring, 105)
                question.picstring = imgbyte
                if not(imgbyte):
                    return "Invalid URL from question with id " + question.getID()

    @staticmethod
    def loadQuestions(eventfile):
        try:
            plq = len(QuestionClient.questions) #abbr. pre-loaded questions
            lineno = 0
            with open("media\\questions\\" + eventfile) as f:
                for line in f:
                    lineno += 1
                    if line.startswith("#"):
                        lineno -= 1
                        continue
                    line = line.rstrip("\r\n")
                    if line == "":
                        break
                    QuestionClient.loadQuestion(str(QuestionClient.eventDict(eventfile[0:3])) + "|" + line, lineno)
                lqff = len([a for a in QuestionClient.questions if bool(a.question)]) - plq #abbr. loaded questions from file
                print(str(round((lineno - lqff)/(lineno) * 100, 2)) + "% loss of questions from file ("
                      + str(lqff) + " loaded out of " + str(lineno) + " in file " + eventfile + ")")
                print()
        except (FileNotFoundError):
            raise Exception("Event file " + eventfile + " not found!")

    @staticmethod
    def loadQuestion(line, lineno: int):
        line = line.replace("\,", "\esccomma")
        line = line.replace(", ", "\comma")
        line = line.replace("\esccomma", ",")
        line = line.split("\comma")
        if len(line) < 3:
            print("Invalid question format in line " + str(lineno))
            return False
        if not(bool(Question.isIDValid(line[0]))):
            print("Invalid id in line " + str(lineno))
            return False
        if len(line) <= 3:
            line.append("")
        if len(line) <= 4:
            line.append("")
        QuestionClient.questions.append(Question(line[0], line[1], line[2], line[3], line[4]))

    @staticmethod
    def getQuestion(ctx, event, args): #args is List
        possibleQuestions = [a for a in QuestionClient.questions if a.getID() != ChannelHandler.channelquestion.get(ctx.channel.id)]
        if ctx.channel.id in ChannelHandler.channelcheck:
            ChannelHandler.channelcheck.pop(ctx.channel.id)
        if ctx.channel.id in ChannelHandler.channelquestion:
            ChannelHandler.channelquestion.pop(ctx.channel.id)
        event = QuestionClient.eventDict(event)
        possibleQuestions = [a for a in possibleQuestions if a.event == event]
        if event == 1: #event-specific subcategories
            if any(x for x in args if x == "nc" or  x == "geo"):
                arg = next(x for x in args if x == "nc" or x == "geo")
                if arg == "nc":
                    possibleQuestions = [a for a in possibleQuestions if a.metadata == 0]
                else:
                    possibleQuestions = [a for a in possibleQuestions if a.metadata == 1]
        dlowbound = 1
        dhighbound = 50
        difficulty = [a for a in args if a == "easy" or a == "medium" or a == "hard"]
        if bool(difficulty):
            if difficulty[0] == "easy":
                dhighbound = 17
            elif difficulty[0] == "medium":
                dlowbound = 18
                dhighbound = 35
            else:
                dlowbound = 36
        if any(x for x in args if len(x) == 4 and x.isnumeric() == True):
            possibleQuestions = [a for a in possibleQuestions if a.year == int(next(x for x in args if len(x) == 4 and x.isnumeric() == True))]
        if any(x for x in args if x.startswith("t") == True and x[1:].isnumeric() == True):
            possibleQuestions = [a for a in possibleQuestions if a.test == int(next(x for x in args if x.startswith("t") and x[1:].isnumeric() == True)[1:])]
        if any(x for x in args if x.startswith("q") == True and x[1:].isnumeric() == True):
            possibleQuestions = [a for a in possibleQuestions if a.test == int(next(x for x in args if x.startswith("q") and x[1:].isnumeric() == True)[1:])]
        possibleQuestions = [a for a in possibleQuestions if dlowbound <= a.questionNum <= dhighbound]
        try:
            question = random.choice(possibleQuestions)
        except:
            return "No such question exists!"
        ChannelHandler.channelcheck.update({ctx.channel.id: str(question.answer)})
        ChannelHandler.channelquestion.update({ctx.channel.id: str(question.getID())})
        ChannelHandler.saveChannels()
        return question

    @staticmethod
    def checkQuestion(ctx, arg): #returns correctness of answer as string, arg is user-given answer
        if len(arg) > 0:
            try:
                answer = ChannelHandler.channelcheck.get(ctx.channel.id)
                answer = answer.partition("\n")[0]
                if (ChannelHandler.channelquestion.get(ctx.channel.id)[-1] == "0" and ChannelHandler.channelquestion.get(ctx.channel.id)[1] == "1"):
                    QuestionClient.formatCalAnswers(answer)
                    try:
                        if not(arg[0][3].isdigit() and -1 <= int(arg[0][3]) - int(answer[3])):
                            raise Exception
                        result = "That is correct! (**Answer**: " + answer + ")"
                    except:
                        result = "That is incorrect, the correct answer is " + answer
                elif answer.lower().replace(" ", "") == arg[0] or (ChannelHandler.channelquestion.get(ctx.channel.id)[-1] == "0"):
                    result =  "That is correct!"
                else:
                    result = "That is incorrect, the correct answer is " + answer
                try:
                    ChannelHandler.channelcheck.pop(ctx.channel.id)
                    ChannelHandler.channelquestion.pop(ctx.channel.id)
                    ChannelHandler.saveChannels()
                    return result
                except:
                    raise Exception("No channel to pop after checking!")

            except:
                return "Nothing to check!"
        else:
            return "Needs an argument!"

    @staticmethod
    def eventDict(name):
        events = ["ns", "cal", "math", "sci"]
        if isinstance(name, int):
            return events[name]
        if isinstance(name, str):
            try:
                result = events.index(name)
                return result
            except:
                return False
    @staticmethod
    def fullName(name:str):
        eventabbr = ["ns", "cal", "math", "sci"]
        eventnames = ["Number Sense", "Calculator", "General Math", "General Science"]
        if name in eventabbr:
            return eventnames[eventabbr.index(name)]
        elif name in eventnames:
            return eventabbr[eventnames.index(name)]
        else:
            return False

class ChannelHandler:
    channelcheck = {}
    channelquestion = {}

    @staticmethod
    def loadChannels():
        print("Channel Data > Loading from channels.txt...")
        file = open("channels.txt", "r")
        lines = file.readlines()
        if len(lines) != 2:
            raise Exception("Exception: Invalid channels.txt when loading channel data")
            return False
        line = lines[0].rstrip("\r\n")
        if line != "{}":
            line = line.replace("{", "").replace("}", "").replace("'", "")
            line = line.split(",")
            for no, item in enumerate(line):
                item = item.split(": ")
                ChannelHandler.channelcheck.update({int(item[0]): item[1]})
            print("Channel Check > " + str(no + 1) + " channels loaded!")
        else:
            print("Channel Check > No channels loaded for checking!")
        line = lines[1].rstrip("\r\n")
        if line != "{}":
            line = line.replace("{", "").replace("}", "").replace("'", "")
            line = line.split(",")
            for no, item in enumerate(line):
                item = item.split(": ")
                ChannelHandler.channelquestion.update({int(item[0]): item[1].replace("'", "")})
            print("Channel No Dupe Questions > " + str(no + 1) + " channels loaded!")
        else:
            print("Channel No Dupe Questions > No channels loaded for checking!")
        print("Channel Data > Done!")

    @staticmethod
    def saveChannels():
        channelcstr = "{}"
        channelqstr = "{}"
        if bool(ChannelHandler.channelcheck):
            channelcstr = str(ChannelHandler.channelcheck)
        if bool(ChannelHandler.channelquestion):
            channelqstr = str(ChannelHandler.channelquestion)
        file = open("channels.txt", "w")
        file.write(channelcstr + "\n")
        file.write(channelqstr)
        file.close()

class Info:
    eqd = {} #abbr. Event Questions Dict where number of questions for each event is stored
    uniquetests = 0
    uniqueyears = 0

    @staticmethod
    def loadQuestionsInfo():
        for i in range(4):
            Info.eqd.update({QuestionClient.eventDict(i): sum(x.event == i for x in QuestionClient.questions)})
        setx = set(str(e.event) + "|" + str(e.test) + "|" + str(e.year) for e in QuestionClient.questions)
        Info.uniquetests = len(setx)
        setx = set(e.year for e in QuestionClient.questions)
        Info.uniqueyears = len(setx)



