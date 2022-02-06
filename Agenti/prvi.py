import datetime
import time
import re
import spade
from spade import quit_spade
from tkinter import *
from spade.agent import Agent
from spade.behaviour import TimeoutBehaviour, CyclicBehaviour, FSMBehaviour, State, OneShotBehaviour
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

class proizvod:
        def __init__(self,trgovina,cijena):
            self.trgovina = trgovina
            self.cijena = cijena

def ispisTrgovineICijene(self,cijena,nazivShopa,brojac):
            cijenaLista = []
            proizvodLista = []
            nazivShopaLista = []
            cijeliProizvod = []
            br=0
            for i in cijena:
                red = i.text
                for char in ' ,.kn':
                    red = red.replace(char,'')
                cijenaLista.insert(br,int(red)/100)
                br +=1
            br=0
            for y in nazivShopa:
              nazivShopaLista.insert(br,y.get_attribute("alt"))

            for x in range(brojac):  
                if int(cijenaLista[x]) <= int(self.agent.cijena) and int(cijenaLista[x]) >= (int(self.agent.cijena)-1000):
                    cijeliProizvod.append(proizvod(nazivShopaLista[x],cijenaLista[x]))
                   
            return cijeliProizvod

class AgentAutomat(Agent):
    

    class PonasanjeKA(FSMBehaviour):
        async def on_start(self):
            print("Pokrenuto ponasanje")

    class StanjeKreiranjaForme(State):
        async def run(self):
            print("Ovo je stanje 1.")
            okvir = Tk()
            def ispis():
                a = proizvod.get()
                b = cijena.get() 
                #c = vrijeme.get()

                if a != "" and b != "":
                    
                    okvir.destroy()
                    self.agent.proizvod = a
                    self.agent.cijena = b
                    #self.agent.vrijeme=c
                    self.set_next_state("StanjePretrazivanja")
                else: 
                    Label(okvir,text="Potrebno je unesti sva polja!",width=30,font=("bold",15)).place(x=60,y=300)
            
                   
            okvir.geometry("500x400")

            proizvod= StringVar()
            vrijeme = StringVar()
            cijena = StringVar()
            okvir.title("Forma unosa")
            labelNaslov = Label(okvir,text="Forma unosa",width=20,font=("bold",30)).place(x=0,y=60)


            labelProizvod = Label(okvir,text="Naziv proizvoda",width=20,font=("bold",10)).place(x=80,y=150)
            unosProizvoda = Entry(okvir,textvariable=proizvod).place(x=250,y=150)

            labelCijena= Label(okvir,text="Željena cijena",width=20,font=("bold",10)).place(x=93,y=200)
            unosCijena = Entry(okvir,textvariable=cijena).place(x=250,y=200)

            #labelVrijemePonavljanja = Label(okvir,text="Vrijeme ponavljanja",width=20,font=("bold",10)).place(x=93,y=250)
            #unosVrijemePonavljanja = Entry(okvir,textvariable=vrijeme).place(x=250,y=250)

            gumb = Button(okvir, text='Submit',command = lambda:[ispis()], width=20, bg="black", fg="white").place(x=160,y=250)

            okvir.mainloop()

    class StanjePretrazivanja(State):
        async def run(self):
            print("Usao sam")
            browser = webdriver.Firefox(executable_path="./drivers/geckodriver")
            wait = WebDriverWait(browser,5)
            browser.get('https://www.nabava.net')
            wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/header/div/form/input[1]'))).send_keys(self.agent.proizvod)
            wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/header/div/form/input[1]'))).send_keys(Keys.ENTER)
            print("Drtuga str")
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="kPostavke.pregledSortTrazilica"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="kPostavke.pregledSortTrazilica"]/option[5]'))).click()

            time.sleep(1)
            
            skup = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/main/div[2]/div[1]/div[2]'))) 
            proizvodNaziv = skup.find_elements_by_class_name('offer__name') 
            cijena = skup.find_elements_by_class_name('offer__price')
            nazivShopa = skup.find_elements_by_class_name('offer__store-logo')
            
            brojac = len(cijena)
            while brojac < 1:
                time.sleep(2)
                browser.refresh()

            spisak = ispisTrgovineICijene(self,cijena,nazivShopa,brojac)
            stringSpisak = ""
            for x in spisak:
                stringSpisak += f"{x.trgovina}: {x.cijena}|"
            while len(spisak) < 1:
                time.sleep(2)
                browser.refresh()
           
            print("Spisak")
            self.agent.stringSpisak = stringSpisak
            browser.quit()
            self.set_next_state("StanjeSlanjaPoruke")

    class StanjeSlanjaPoruke(State):
        async def run(self):
            print("StanjeSlanjaPoruke")
            msg = spade.message.Message(
                to="primatelj@rec.foi.hr",
                body=f"{self.agent.stringSpisak}")
            await self.send(msg)
            print("Poruka je poslana")
            await self.agent.stop()
         

    async def setup(self):
       
        fsm = self.PonasanjeKA()

        fsm.add_state(name="StanjeKreiranjaForme", state=self.StanjeKreiranjaForme(), initial=True)
        fsm.add_state(name="StanjePretrazivanja", state=self.StanjePretrazivanja())
        fsm.add_state(name="StanjeSlanjaPoruke", state=self.StanjeSlanjaPoruke())


        fsm.add_transition(source="StanjeKreiranjaForme", dest="StanjePretrazivanja")
        fsm.add_transition(source="StanjePretrazivanja", dest="StanjeSlanjaPoruke")
        fsm.add_transition(source="StanjeKreiranjaForme", dest="StanjeKreiranjaForme")
        fsm.add_transition(source="StanjePretrazivanja", dest="StanjePretrazivanja")
        fsm.add_transition(source="StanjeSlanjaPoruke", dest="StanjeSlanjaPoruke")

        self.add_behaviour(fsm)



if __name__ == '__main__':
    print("glavni")
    parser = ArgumentParser()
    parser.add_argument(
        "-jid", type=str, help="JID agenta", default="posiljatelj@rec.foi.hr")
    parser.add_argument(
        "-pwd", type=str, help="Lozinka agenta", default="tajna")
    args = parser.parse_args()

    agentautomat = AgentAutomat(args.jid, args.pwd)
   
    pokretanje = agentautomat.start()
    pokretanje.result()  

    while agentautomat.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    agentautomat.stop()
    quit_spade()
