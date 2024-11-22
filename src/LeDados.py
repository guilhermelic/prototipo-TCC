from datetime import datetime
import time
import os
import shutil

from library.biblioteca import displayNoData, geraRetas, leRegioes, paramsReta, pontosParaRetaInfinita, display, paramsReta, whatRegion
from library.biblioteca import timeDiff, timeCompare

#Esse maxLaneWidth precisa ter relação com o tamanho da pista
maxLaneWidth = 0.00008

#Configurações e variáveis do pygame
import pygame
pygame.init()
clock = pygame.time.Clock()
actualPosition = 0      #registra a posicao atual
bestLap = -1
actualLap = -1
screen = pygame.display.set_mode([500, 500])
font = pygame.font.Font('freesansbold.ttf', 16)

minValueValidLap = 27
qtdeErros = 0
qtdeErrosControl = 0

def readDiffTimes(arqName):
    startData = readFirstLine(arqName)
    print("Primeiro dado: " + str(startData))
    endData = readDataFile(arqName, minValueValidLap)
    if endData == []:
        print("Error: minValueValidLap " )
        return -1
    print("Último dado: " + str(endData))
    if len(endData) > 1:
        return timeDiff(endData[1],startData[1])
    else:
        print("endData vazio causou erro: " + str(endData))
        return -1

#Toda vez que trocar de volta precisa verificar se a nova foi melhor
#A volta atual precisa estar num arquivo actualLap.txt
#Se a volta atual estiver incompleta, não altera 
def newLap():
    global bestLap
    global actualLap

    print("\nDados da volta atual:")
    timeActual = readDiffTimes("data/actualLap.txt")
    print("Tempo da volta atual: " + str(timeActual))
    print("\nDados da melhor volta:")
    timeBest = readDiffTimes("data/bestLap.txt")
    print("Tempo da melhor volta: " + str(timeBest))

    if timeActual == -1 or timeBest == -1:
        return
    
    if timeCompare(str(timeActual), str(timeBest)):
        #Reescrever a melhor volta
        print("\n--> A melhor volta será atualizada")
        shutil.copyfile("data/actualLap.txt", "data/bestLap.txt")
        bestLap = actualLap
        #Reescrever as retas
        with open("data/actualLap.txt", "r") as f:
            (i, timeStamp, lap, posX, posY, vel, fuel) = lePosicoes(f)
        with open("data/regioes.txt", "w") as f:
            geraRetas(maxLaneWidth,posX,posY,f)
    else:
        #Não reescrever a melhor volta
        pass
    return


#Faz todo o processo de leitura. Le a melhor volta
#Sempre que trocar de volta, verifica se a nova foi melhor
def readCommunicationFile(communicationFile):
    with open("data/actualLap.txt", "w") as arq:
        pass

    with open("data/bestLap.txt", "r") as arq:
        readBestLap("data/bestLap.txt")

    counter, timestamp, lap, posX, posY, vel, fuel = readDataFile("data/dataPoints.txt")
    dataAnterior = (counter, timestamp, lap, posX, posY, vel, fuel)
    global qtdeErros
    global qtdeErrosControl
    global actualLap
    actualLap = lap
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        try:
            with open(communicationFile, 'r+') as f:
                content = f.read().strip()
                if content == "1":
                    f.seek(0)
                    f.write("0")
                    dataAnterior = (counter, timestamp, lap, posX, posY, vel, fuel)
                    counter, timestamp, lap, posX, posY, vel, fuel = readDataFile("data/dataPoints.txt")
                    if actualLap != lap:
                        newLap()
                        actualLap = lap
                        with open("data/actualLap.txt", "w") as arq:
                            pass
                    with open("data/actualLap.txt", 'a') as f:
                        f.write(f'{counter} {timestamp} {lap} {posX} {posY} {vel} {fuel}\n')

                    # print(f'Last line readed: {}')
                else:
                    # print(f"Do not read: {content}")
                    pass
        except IOError as e:
            print(f"Error reading from file1: {e.filename}")
        screen.fill((255,255,255))
        a=0
        b=0
        lado=0
        pos5 = []
        #0-counter; 1-timestamp; 2-lap; 3-posX; 4-posY; 5-vel; 6-fuel
        #Le as posições da melhor volta
        with open("data/bestLap.txt", "r") as f:
            bestData = lePosicoes(f)
        
        #Le as regioes da melhor volta
        with open("data/regioes.txt", "r") as f:
            regioes = leRegioes(f)

        actualPosition, rectangle = whatRegion((posX,posY),regioes)
        if actualPosition == -1 and qtdeErrosControl != counter:
            qtdeErrosControl = counter
            qtdeErros+=1
            print("qtdeErros = ",qtdeErros, ", counter = ", counter)

        #Tela de x={500->1000}
        a,b = paramsReta((posX,posY),(dataAnterior[3],dataAnterior[4]))
        if posX>dataAnterior[3]:
            lado = 1
        if posX<dataAnterior[3]:
            lado = -1

        if actualPosition != -1:    #Região encontrada
            #Descobre os 5 proximos pontos
            for j in range(actualPosition,actualPosition+5):
                pos5.insert(0,(bestData[3][j%len(bestData[3])],bestData[4][j%len(bestData[4])]))
            velocidades=[]
            for j in range(actualPosition,actualPosition+6):
                velocidades.append(bestData[5][j%len(bestData[5])])
            display(screen,0,a,b,pos5,maxLaneWidth, lado, vel, velocidades, actualLap, bestLap, font)
        else:
            displayNoData(screen, 0, vel, font)
        clock.tick(3)
        pygame.display.flip()
                
        time.sleep(0.1)

def readFirstLine(dataFile):
    with open(dataFile, 'rb') as f:
        try:
            firstLine = f.readline().decode()
            firstLine = firstLine.split()
            for i in range(len(firstLine)):
                if i!=1:
                    firstLine[i] = float(firstLine[i])
            return firstLine
        except IOError as e:
            print(f"Error reading to file: {e}")

def readDataFile(dataFile, minSize = -1):
    with open(dataFile, 'rb') as f:
        #conta o numero de linhas do arquivo
        if minSize != -1:
            line_count = 0
            for _ in f:
                line_count += 1
            if line_count < minSize:
                print("Line count é: " + str(line_count))
                return []
            f.seek(0)

        try:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
        last_line = last_line.split()
        for i in range(len(last_line)):
            # 0 0.0 0 809.8262 -713.5493 21.785471 0.99962175
            # int float int float float float float
            if i==0 or i==2:
                last_line[i] = int(last_line[i])
            elif i == 1:
                last_line[i] = last_line[i]
            else:
                last_line[i] = float(last_line[i])
        return last_line

#2 Ler o arquivo com posicoes e velocidades
from library.biblioteca import lePosicoes
# (posX,posY,velocidade) = lePosicoes(arq)
# arq.close()

#Le a melhor volta e retorna o tempo pra completar a volta, alem 
# do vetor interno e externo de retas
def readBestLap(fileBestLap):
    global bestLap
    try:
        with open(fileBestLap, 'r') as f:
            (i, timeStamp, lap, posX, posY, vel, fuel) = lePosicoes(f)
            if bestLap == -1:
                bestLap = int(lap[0])
            arq = open("data/regioes.txt","w")
            geraRetas(maxLaneWidth,posX,posY,arq)
            arq.close()
            # print("vetorInterno: ",vetorInterno,"\nvetorExterno",vetorExterno, "\nDurationLap: ", durationLap)
            return
    except IOError as e:
        print(f"Error reading to file: {e}")
        
    
if __name__ == "__main__":
    communicationFile = "data/communication.txt"
    # Garantir que o arquivo existe

    if not os.path.exists(communicationFile):
        open(communicationFile, 'w').close()
    readCommunicationFile(communicationFile)
