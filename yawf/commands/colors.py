colors = {
    "header": "\033[95m",
    "okblue": "\033[94m",
    "okgreen": "\033[92m",
    "warning": "\033[93m",
    "fail": "\033[91m",
    "endc": "\033[0m",
    "bold": "\033[1m",
    "underline": "\033[4m"
    }

def color_msg(color, *msgs, join_char=" "):
    msgs = join_char.join(msgs)
    color_code = colors[color]
    end = colors["endc"]
    return "{0}{1}{2}".format(color_code, msgs, end)
