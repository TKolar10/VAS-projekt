import datetime
import time
import re
import spade
from spade import quit_spade
from tkinter import *
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour, FSMBehaviour, State, OneShotBehaviour
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

class Agent(Agent):
    class Primi(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                ispis = msg.body
                print(ispis)
                splitanje = ispis.split("|")
                okvir = Tk()
                br=1
                lbl = Listbox(okvir)
                for x in splitanje:
                    lbl.insert(br,x)
                    br+=1
                lbl.pack()
                okvir.mainloop() 
               
            else:
                print("Nema poruke")

    async def setup(self):
        print("Ponasanje agneta drugog")
        ponasanje = self.Primi()
        self.add_behaviour(ponasanje)
        
     
            

if __name__ == '__main__':
    print("Agent primatenje")
    agent = Agent('primatelj@rec.foi.hr','tajna')
    pokretanje  = agent.start()
    pokretanje.result()
    input("Press ENTER to exit. \n")
    agent.stop()
    quit_spade()


