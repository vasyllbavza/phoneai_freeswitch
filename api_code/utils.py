from word2number import w2n

def isNumber(str):    
    try:
        return w2n.word_to_num(str)
    except:
        return False

def findKeys(audio_text):
    from urllib.parse import unquote
    audio_text = unquote(audio_text)
    audio_text = audio_text.strip()
    ret = [isNumber(s) for s in audio_text.split() if isNumber(s)]
    return ret