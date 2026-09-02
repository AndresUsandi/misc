import tiktoken

class Chunk:
    def __init__(self):
        self.Id = -1
        self.Index = -1
        self.Text = ""
        self.Type = "AMBIGUOUS"
        self.Tokenizer = tiktoken.get_encoding("gpt2")

    def getTokens(self):
        tokenIds = self.Tokenizer.encode(self.Text)
        tokens = []
        for i in range(len(tokenIds)):
            tokens.append(self.Tokenizer.decode([tokenIds[i]]))
        return tokens

class Chapter:
    def __init__(self):
        self.Id = -1
        self.Number = -1
        self.Title = ""
        self.Chunks: list[Chunk] = []

    def getFullText(self):
        fullText = []
        for i in range(len(self.Chunks)):
            fullText.append(self.Chunks[i].Text)
        return "\n\n".join(fullText)

    def getAllTokens(self):
        tokens = []
        for i in range(len(self.Chunks)):
            tokens.extend(self.Chunks[i].getTokens())
        return tokens

class Book:
    def __init__(self):
        self.Id = -1
        self.Title = ""
        self.Chapters: list[Chapter] = []

    def getFullText(self):
        fullText = []
        for i in range(len(self.Chapters)):
            fullText.append(self.Chapters[i].getFullText())
        return "\n\n".join(fullText)

    def getAllTokens(self):
        tokens = []
        for i in range(len(self.Chapters)):
            tokens.extend(self.Chapters[i].getAllTokens())
        return tokens