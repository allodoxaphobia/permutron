#!/usr/bin/env python

# DO NOT EDIT HERE, update config if changes are desired
binders=[""]
suffixbinders=[""]
suffixes=[] #NO empty sting here!
#commonly used substitutes for characters
#We don't do capitalization per letter atm, if you want that, add "p":"P","q":"Q" etc..;. to this list here and remove named items with capital letter)
permutations = {
	"a":"@4",
	"A":"@4",
	"e":"3",
	"E":"3",
	"i":"1",
	"I":"1",
	"o":"0",
	"O":"0",
	"s":"$"
}

human_level=3

wordcombinations=[] #used to store bound words
permutedwords=[] #temp fix to remove duplicates

SETTINGS={}

def loadconfig():
	global SETTINGS,binders,suffixbinders,suffixes,human_level
	try:
		f=open("permutron.conf","r")
		for line in f.read().split("\n"):
			if len(line) > 0:
				if line[0] != "#":
					data = line.split("=",1)
					data[0] = data[0].strip(' \t\n\r')
					data[1] = data[1].strip(' \t\n\r')
					SETTINGS[data[0]]=data[1]
		f.close()
		human_level=int(SETTINGS["human_pass"])
		
		for binder in list(SETTINGS["binders"+str(human_level)].strip()):
			binders.append(binder.strip())
		for suffixbinder in list(SETTINGS["suffix_binders"+str(human_level)].strip()):
			suffixbinders.append(suffixbinder.strip())
		for suffix in SETTINGS["suffixes"].split(","):
			if len(suffix.strip())>0:
				suffixes.append(suffix.strip())
		human_level=int(SETTINGS["human_pass"])
	except Exception,e:
		print "Error opening config file",e
		exit(1)


def loadwords(filen):
	#builds array of words from file
	#expects fiel with one word per line. Filters out empty lines and changes everything t lowercase
	try:
		f=open(filen,"r") 
		data=f.read().split("\n")
		f.close()
		words=[]
		for word in data:
			tmp=word.strip()
			if len(tmp)>0:
				if tmp[0]<>"#": #remove comments
					tmp=tmp.lower()
					if tmp not in words:#duplicate removal
						words.append(tmp)
		return words
	except Exception, e:
		print "Faile dto load wordlist: ", e.message
		exit(1)

def generatesuffixes(word):
	#global suffixes,binders
	#returns word with all possible binder+suffix combinations
	#also returns word itself
	sf=[word]
	for suffix in suffixes:
			if suffix not in word:
				for binder in suffixbinders:
					if binder not in suffix or binder=='':#don't add a binder if the same char is already in the suffix
						sf.append(word+binder+suffix)
	return sf

def exceeds(value,limit):
	#retuns by how much a given value exceeds a limit
	if value>limit:
		return value-limit
	else:
		return 0 

def likelyhoodtest(word,level=3): #this routine checks likelyhood a password is human generated, level 0 = all passwords pass, level 5 = most restrictive
	#returns true or false, true=pass, false=fail, password will not be used/printed

	#FIRST we will validate password against policies if they are specified in config
	lcasecount=0
	ucasecount=0
	digitcount=0
	specialcount=0
	for char in word:
		if char in "abcdefghijklmnopqrstuvwxyz":
			lcasecount+=1
		elif char in "ABCDEFGHIJKLMNOPQRSITUVW":
			ucasecount+=1
		elif char in "0123456789":
			digitcount+=1
		else:
			specialcount+=1
	if SETTINGS["use_policy"]<>0:
		if len(word)> int(SETTINGS["max_len"]): return False
		if len(word)< int(SETTINGS["min_len"]): return False
		if int(SETTINGS["must_have_digit"])==1 and digitcount==0: return False
		if int(SETTINGS["must_have_upper"])==1 and ucasecount==0: return False
		if int(SETTINGS["must_have_lower"])==1 and lcasecount==0: return False
		if int(SETTINGS["must_have_special"])==1 and specialcount==0: return False
	#Human Validation tests
	#TODO: some tests carry more weight then others, we should add a weight to these calculations
	if level==0: return True #all is good
	nonhuman=0
	#the longer it is then 12 chars, the less likely it is human
	if len(word)>12:
		nonhuman +=((len(word)-12)*(level*0.5))
	#shorter then 8? the shorted, the less likely
	if len(word)<8:
		nonhuman += ((8-len(word))*(level*0.4))
	#counting total amount of special chars, anythin more then 1/3 of all characters is unlikely
	if len(word)/3<specialcount:
		nonhuman+=(specialcount-(len(word)/3))*(level*1) # (diff between length and countofspecials)*level
	#occrences of special chars:
	nonhuman += exceeds(word.count("@"),3)*(level*0.5)
	nonhuman += exceeds(word.count("$"),3)*(level*0.5)
	nonhuman += exceeds(word.count("#"),3)*(level*0.5)
	nonhuman += exceeds(word.count("!"),3)*(level*0.5)
	nonhuman += exceeds(word.count("*"),3)*(level*0.5)
	nonhuman += exceeds(word.count("-"),2)*(level*0.7)
	nonhuman += exceeds(word.count("_"),2)*(level*1)
	nonhuman += exceeds(word.count("<"),1)*(level*1.5)
	nonhuman += exceeds(word.count(">"),1)*(level*1.5)
	nonhuman += exceeds(word.count("{"),0)*(level*0.8)
	nonhuman += exceeds(word.count("}"),0)*(level*0.8)
	nonhuman += exceeds(word.count(","),1)*(level*0.7)
	nonhuman += exceeds(word.count("."),1)*(level*0.5)
	nonhuman += exceeds(word.count(":"),2)*(level*1.5)
	nonhuman += exceeds(word.count(";"),1)*(level*1.2)
	#print "#",word, nonhuman
	#there is usually a balance between upper and lowercase
	#either uppercasing is limited to first letters or intersperced
	if ucasecount>3 and abs(ucasecount-lcasecount)>3:
		nonhuman += abs(ucasecount-lcasecount)*(level*0.3	)
	if nonhuman>5:	
		return False
	else: return True



def generateboundwords(firstword,wordset):
	global binders,wordcombinations,suffixbinders
	wordcombinations=wordcombinations + generatesuffixes(firstword)
	for word in wordset:
		if word in firstword or firstword in word:
			pass # this is done to avoid abreviations being added to string that already has full word in it
		else:
			tmpbinders=list(binders)#copy not reference
			for binder in binders:
				wordcombinations.append(firstword + binder + word)
				wordcombinations.append(firstword + binder + word.title())
				wordcombinations.append(firstword + binder + word.upper())
				wordcombinations = wordcombinations + generatesuffixes(firstword + binder + word)
				wordcombinations = wordcombinations + generatesuffixes(firstword + binder + word.title())
				wordcombinations = wordcombinations + generatesuffixes(firstword + binder + word.upper())
				#note: we currently only bind a maximum of two words and we don't append a word to itself


def genpasswordperms(password,offset=0):
	#for each entry in array wordcombinations we will generate character substitutions
	#recursive
	global permutations,permutedwords,human_level
	#print password #unpermutated is also valid entry
	i=offset
	if likelyhoodtest(password,human_level) and password not in permutedwords:
		permutedwords.append(password) #append word itself
		print password
	while i <len(password):
		if password[i] in permutations: #is it a character in need of substitution ,or already a product of substitution
			for replacement in permutations[password[i]]:
				if password.count(replacement)<=2:
					#chances that a substitute char is used more then 2 times is slim
					tmppass=password[:i]+replacement+password[i+1:]
					genpasswordperms(tmppass,i)
		i=i+1

def main(args):
	global permutedwords
	loadconfig()
	#Load words to work with
	words = loadwords("words.txt")#todo: make command line arg
	#step 1, create all possible combinations from words, using all possible binders
	for word in words:
		tmplist= list(words) #copy it rather then ref. it
		tmplist.remove(word) #we don't do word+sameword 
		generateboundwords(word,tmplist)
		generateboundwords(word.title(),tmplist)#capitalize first letter
		generateboundwords(word.upper(),tmplist)
	print "### Number of wordcombinations loaded", str(len(wordcombinations))
	print "### Generating permutations:"
	for word in wordcombinations:
		genpasswordperms(word)
main(None)


