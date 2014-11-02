# -*- coding: utf-8 -*-
from codecs import open
from unidecode import unidecode
from bs4 import BeautifulSoup
from urllib2 import urlopen
import json,csv
import re,htmlentitydefs

# Fonction de decodage des caractères ASCII qui caché l'adresse mail facile pour un bot 
# Un glue de chez Seb! j aime bien son génie de python


def htmlentitydecode(s):
    # First convert alpha entities (such as &eacute;)
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[entity])
        return u" "  # Unknown entity: We replace with a space.
    t = re.sub(u'&(%s);' % u'|'.join(htmlentitydefs.name2codepoint), entity2char, s)
   
    # Then convert numerical entities (such as &#233;)
    t = re.sub(u'&#(\d+);', lambda x: unichr(int(x.group(1))), t)
    
    # Then convert hexa entities (such as &#x00E9;)
    return re.sub(u'&#x(\w+);', lambda x: unichr(int(x.group(1),16)), t)


def vas_chercher():

	#Liste des quelques urls des pages qui contiennent la liste des deputes
	#Encore une optimisation comme celel d alioune sur le nombre de page avec une incrementation possible 
	urls = {
		"http://www.assemblee-nationale.sn/index.php?option=com_content&view=article&id=214&Itemid=218",
		"http://www.assemblee-nationale.sn/index.php?option=com_content&view=article&id=214&Itemid=218&limitstart=1",
		"http://www.assemblee-nationale.sn/index.php?option=com_content&view=article&id=214&Itemid=218&limitstart=2",
		"http://www.assemblee-nationale.sn/index.php?option=com_content&view=article&id=214&Itemid=218&limitstart=3",
		"http://www.assemblee-nationale.sn/index.php?option=com_content&view=article&id=214&Itemid=218&limitstart=4"
	}

	deputes = []

	for url in urls:
		page = urlopen(url)
		laSoupe = BeautifulSoup(page.read())

		# capture de la table qui se situe juste après la div.pagenavcounter
		tableDepute = laSoupe.find('div', { 'class':'pagenavcounter'}).findNextSibling().tbody.find_all('tr')
		
		# Retrait du haut de la pile, les dechets qui devaient figurer dans le Thead du tableau
		tableDepute.pop(0)

		
		for tr in tableDepute:
			tds = tr.find_all('td')

			depute = []

			for td in tds:

				# tranformation des données en unicode pour pouvoir reconstruire les adresses emails des deputes
				# le code pourrait faire une refactoristation pour seulement etre seulement a l indice ou le texte
				# situé
				sanitizedString = htmlentitydecode(td.get_text())
				
				# le bouillon de regex pour capturer cette semblante sécurité
				mail = re.search(r"var addy([0-9]*) \= '([a-z0-9\.\_\-]*)'",sanitizedString,re.M|re.I); 

				if mail:
					depute.append(mail.group(2)+'@assemblee-nationale.sn')
				else:
					depute.append(td.get_text().encode('utf-8'))
				#print depute
			deputes.append(depute)
			deputes = sorted(deputes, key= lambda dep: int(dep[0]))
	# Saving to json
	json_file = open('data/data.json','w')
	json.dump(deputes,json_file)
	json_file.close();

	#saving to csv
	entete = ['id','Prénom','Nom','Email']
	deputes.insert(0,entete)

	csv_file = open('data/data.csv','w')
	writer = csv.writer(csv_file,delimiter=b',')
	for line in deputes:
		writer.writerow(line)



vas_chercher()