from datetime import datetime
import time
import os

#Pegando de banco.txt
#Essa função primeiro escreve a melhorVolta.txt
#Depois escreve os valores de posição, velocidade e timestamp no dataPoints.txt
#Depois escreve na communication.txt o valor de 1 para notificar que a mensagem foi escrita

#Essa função escreve a bestLap.txt
#Recebe o arqName da melhor volta e os dados da melhor volta
def writeBestLap(arqName, data):
    with open(arqName,"w") as f:
        for i in data:
            f.write(i)
    return True

def writeInFile(file, data, mode="a" ):
    try:
        with open(file, mode) as f:
            f.write(data)
            print(f"Written: Message {data} in {file} with mode '{mode} at {datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")[:-3]}'")
            return True
    except IOError as e:
        print(f"Error writing to file: {e}")
        return False

#Escreve os valores na dataFile e na communicationFile a cada 0.5 segundos
#pointsNumber é o numero de pontos que foi escrito na primeira volta
#dataBase contem os dados que devem ser escrito a partir de pointsNumber
def writting(dataFile, communicationFile, pointsNumber, dataBase):
    counter = pointsNumber

    while True:
        data = dataBase[counter]
        if writeInFile(dataFile, data):
            writeInFile(communicationFile, "1", "w")
        counter += 1
        time.sleep(0.5)


if __name__ == "__main__":
    #O correto é tratar os erros de escrita e leitura
    dataFile = "data/dataPoints.txt"
    dataFileBestLap = "data/bestLap.txt"
    databaseFile = "data/banco.txt"

    #Pega os dados do banco e armazena em data
    data = []
    with open(databaseFile, 'r') as f:
        i = 0
        for line in f:
            data.append(str(i) + " " + line)
            i += 1
    
    #Acha a primeira volta nos dados do banco
    i = 0
    firstLap = []
    while data[i].split(' ')[2] == '0':
        firstLap.append(data[i])
        i += 1

    #Escreve a melhor volta no arquivo bestLap.txt
    writeBestLap(dataFileBestLap, firstLap)
    writeBestLap(dataFile, firstLap)
    
    if not os.path.exists(dataFile):
        open(dataFile, 'w').close()
    writting(dataFile, "data/communication.txt", i, data)
