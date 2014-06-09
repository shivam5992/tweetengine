import HTMLParser, itertools, re

removable = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']

def remove_special(text, excpt=None):
	if excpt == None:
		for x in removable:
			if x in text:
				text = text.replace(x," ")
	else:
		for spchar in removable:
			if spchar not in excpt:
				text = text.replace(spchar, " ")
	text = " ".join(text.split()).strip()
	return text

def repeated_chars(text, level=2):
	text = ''.join(''.join(s)[:level] for _, s in itertools.groupby(text))
	return text

def decode_it(text, decoding="utf-8"):
    text = text.decode(decoding).encode("ascii","ignore")
    return text
	
def escape(text):
    text = HTMLParser.HTMLParser().unescape(text)
    return text

def improve_repeated(text):
    text = ''.join(''.join(s)[:2] for _, s in itertools.groupby(text))
    return text  

def split_attached(text):
	if len(text.split()) == 1 and not text.isupper():
		lis = re.findall('[A-Z][^A-Z]*', text)
		if len(lis) == 0:
			line = text
		else:
			line = " ".join(re.findall('[A-Z][^A-Z]*', text))
	else:
		newd = []
		for word in text.split():
			if not word.isupper():
				lis = re.findall('[A-Z][^A-Z]*', word)
				if len(lis) == 0:
					newd.append(word)
				else:
					newd.append(" ".join(lis))
			else:
				newd.append(word)
		line = " ".join(newd)
	return line

def remove_url(text):
    mypatt = "http[s]?://[a-zA-Z0-9]*"
    strongpatt = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(strongpatt, text)
    f = 0
    for url in urls:
        i = text.index(url)
        text = text[:i] + text[i+len(url):]
    return text