import tiktoken 

encoding = tiktoken.get_encoding("cl100k_base")
banned_words = [
    "symphony", "silent", "tapestry", "whispered", "smile", "bustling", 
    "navigating", "realm", "embark", "virtuoso", "vibrant", "nestled",
    "serene", "luminous", "labyrinthine", "luminous", "labyrinth",
    "soul", "enhance", "whispering", "testament", "underscore",
    "dance", "landscape", "crucible", "soulful", "soulfully",
    "delve", "embodies", "embody", "embrace", "encompass", "encompass",
    "mere", "merely", "merest", "beacon", "crucial", "discover", "daunting",
    "blend", "unique", "world", "ensure", "foster", "fostering", "fosters", "clutching",
    "oppressive", "clarion call", "defiant", "defiance", "defiantly", "cacophony", "wry",
    "audacity", "rebellion", "rebel", "serenity", "redemption", "rallying cry", "shared vision",
    "solace", "canvas", "claroin", "odyssey", "journey", "silhouette", "constant companion,"
    "lingered", "thrum", "hush", "quiet rebellion", "unsung", "the rhythm of daily life",
    "stood apart", "face of adversity", "of a city where", "rebellion",
    "in the heart of", "unyielding", "her fortress", "his fortress", "from another era",
    "bore witness", "brimming with", "to etch", "destinies", "unappologetic",
    "silent declaration", "instances of a 'city' performing actions", "unwavering",
    "quiet act of"
    ]
banned_tokens = []

for word in banned_words:
    banned_tokens.extend(encoding.encode(word))

print(banned_tokens)

def get_bias():
    bias = {}
    for token in banned_tokens:
        bias[token] = -1
    return bias