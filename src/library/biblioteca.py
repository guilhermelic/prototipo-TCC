import random
import math
from time import sleep
import pygame
from datetime import datetime
from matplotlib.path import Path

#Recebe o valor de alfa atual e o valor da variavel aleatoria atual, entre 90 e 180
#Além disso, recebe: i, timestamp, lap
#Escreve no padrão (i, timestamp, lap, posx, posy, vel, fuel)
def geraDado( alfa, varRamdom, i, lap ):
    varRamdom = varRamdom + random.randint(-1,1)
    if varRamdom<90:
        varRamdom = 90
    if varRamdom>180:
        varRamdom = 180

    return "{0} {1} {2} {3} {4} {5} {6}\n" .format(i, actualTime(), lap, round(250 + math.cos(alfa)*varRamdom), round(250+ math.sin(alfa)*varRamdom),
                                                round(random.randint(0,100)), round(random.randint(0,100)))
    return "{0} {1} {2}\n" .format(round(250 + math.cos(alfa)*varRamdom), round(250+ math.sin(alfa)*varRamdom),
                                                round(random.randint(0,100)))

def actualTime():
    dt = datetime.now()
    return f'{str(dt.hour).zfill(2)}:{str(dt.minute).zfill(2)}:{str(dt.second).zfill(2)}.{str(dt.microsecond).zfill(6)}'
#Gera os pontos e coloca no mapa, além disso gera a velocidade na terceira posicao
#Escreve tanto na bestLap como na data
def geraDados(qtdPontos, arqBest, arqData):
    varRamdom = random.randint(90,180)
    for i in range(qtdPontos):
        alfa = i*2*math.pi/qtdPontos
        data = geraDado(alfa, varRamdom, i, 1)
        arqBest.write(data)
        arqData.write(data)
        sleep(0.001)

def timeDiff(time1, time2):
    fmt_with_ms = "%H:%M:%S.%f"
    fmt_without_ms = "%H:%M:%S"
    
    try:
        t1 = datetime.strptime(time1, fmt_with_ms)
    except ValueError:
        t1 = datetime.strptime(time1, fmt_without_ms)
    
    try:
        t2 = datetime.strptime(time2, fmt_with_ms)
    except ValueError:
        t2 = datetime.strptime(time2, fmt_without_ms)
    
    # Retornando a diferença de tempo
    return t1 - t2

#Return true if time1 < time2
#Ou seja, time1 deve ser o tempo da volta atual e se for menor que time2 deve atualizar a melhor volta
def timeCompare(time1, time2):
    fmt_with_ms = "%H:%M:%S.%f"
    fmt_without_ms = "%H:%M:%S"
    
    try:
        t1 = datetime.strptime(time1, fmt_with_ms)
    except ValueError:
        t1 = datetime.strptime(time1, fmt_without_ms)
    
    try:
        t2 = datetime.strptime(time2, fmt_with_ms)
    except ValueError:
        t2 = datetime.strptime(time2, fmt_without_ms)
    return t1 < t2

#Read the positions and return the (i, timestamp, lap, posx, posy, vel, fuel)
def lePosicoes(arq):
    k = arq.read()
    k = k.split()       #the positions are here

    counter = []
    timestamp = []
    lap = []
    posX=[]
    posY=[]
    vel=[]
    fuel=[]    

    for i in range(0,len(k),7):
        k[i] = float(k[i])
        counter.append(k[i])

    for i in range(1,len(k),7):
        timestamp.append(k[i])

    for i in range(2,len(k),7):
        k[i] = float(k[i])
        lap.append(k[i])
    
    for i in range(3,len(k),7):
        k[i] = float(k[i])
        posX.append(k[i]
                    )
    for i in range(4,len(k),7):
        k[i] = float(k[i])
        posY.append(k[i])

    for i in range(5,len(k),7):
        k[i] = float(k[i])
        vel.append(k[i])

    for i in range(6,len(k),7):
        k[i] = float(k[i])
        fuel.append(k[i])

    return counter, timestamp, lap, posX, posY, vel, fuel

#Gera as retas (regioes)
def geraRetas(tamRetas, x, y, arq):
    #Vetores a serem armazenados os pontos para região
    vetor_interno = []
    vetor_externo = []

    #Coeficiente da reta
    m = 0

    pos_atual = (x[0], y[0])
    delta_y = (y[0]-y[-1])
    delta_x = (x[0]-x[-1])
    if delta_x!=0:
        angle = math.atan(delta_y/delta_x)
    else:
        angle = math.pi/2
    vetor_interno.append((pos_atual[0]-tamRetas*math.sin(angle),pos_atual[1]+tamRetas*math.cos(angle))) 
    vetor_externo.append((pos_atual[0]+tamRetas*math.sin(angle),pos_atual[1]-tamRetas*math.cos(angle)))

    for i in range(1, len(x)):
        pos_atual = (x[i], y[i])
        delta_y = (y[i]-y[i-1])
        delta_x = (x[i]-x[i-1])
        if delta_x!=0:
            angle = math.atan(delta_y/delta_x)
        else:
            angle = math.pi/2

        vetor_interno.append((pos_atual[0]-tamRetas*math.sin(angle),pos_atual[1]+tamRetas*math.cos(angle))) 
        vetor_externo.append((pos_atual[0]+tamRetas*math.sin(angle),pos_atual[1]-tamRetas*math.cos(angle))) 

    for i in range(len(vetor_interno)):
        arq.write("{0} {1} {2} {3}\n" .format(vetor_interno[i][0],vetor_interno[i][1],vetor_externo[i][0],vetor_externo[i][1]))

    return vetor_interno, vetor_externo

def leRegioes(arq):
    # arq = open("regioes.txt","r")
    regions = []

    k = arq.read()
    k = k.split()       #the regions are here
    for i in range(len(k)):
        k[i] = float(k[i])
    for i in range(0,len(k),4):
        regions.append((k[i],k[i+1],k[i+2],k[i+3]))
    return regions

#recebe as posições 1 e 2 e retorna os pontos que devem ser desenhados para obter uma reta infinita
def pontosParaRetaInfinita(pos1, pos2, maxX, maxY):
    if pos1[0]==pos2[0]:
        return (pos1[0],0),(pos1[0],maxY)
    if pos1[1]==pos2[1]:
        return (0,pos1[1]),(maxX,pos1[1])
    angulo = (pos2[1]-pos1[1])/float(pos2[0]-pos1[0])
    (x,y)=pos1
    while (x<maxX) and (y<maxY) and (x>0) and (y>0):
        x = x + 1
        y = y + angulo
    posMin1 = (x,y)
    if posMin1[1]>maxY: posMin1 = (x,maxY)
    if posMin1[1]<0: posMin1 = (x,0)

    (x,y)=(float(pos2[0]),float(pos2[1]))
    while (x<maxX) and (y<maxY) and (x>0) and (y>0):
        x = x - 1
        y = y - angulo
    posMin2 = (x,y)
    if posMin2[1]>maxY: posMin2 = (x,maxY)
    if posMin2[1]<0: posMin2 = (x,0)
    return (int(posMin1[0]),int(posMin1[1])), (int(posMin2[0]),int(posMin2[1]))


BACKGROUND = (33, 145, 140)
GREEN = (94, 201, 98)
YELLOW = (253, 231, 37)

TAM = 500
yLineCenter = 225
hTriangle = 108
lTriangle = 91
radius = 20
deltaX = []
deltaX.append(150)
for i in range(1,5):
    deltaX.append(deltaX[0]+i*20)

def displayBasic(screen,dx):
    x0 = (0+dx,yLineCenter+hTriangle)
    x1 = (lTriangle+dx,yLineCenter)
    x2 = (TAM-lTriangle+dx,yLineCenter)
    x3 = (TAM+dx,yLineCenter+hTriangle)

    pygame.draw.polygon(screen, BACKGROUND, ((0+dx,TAM),(0+dx,0),(TAM+dx,0),(TAM+dx,TAM)))
    pygame.draw.line(screen, (0,0,0), (0+dx,yLineCenter), (TAM+dx, yLineCenter))  #Line to orientate
    pygame.draw.polygon(screen, GREEN, ((0+dx,yLineCenter),x0,x1))
    pygame.draw.polygon(screen, GREEN, ((TAM+dx,yLineCenter),x3,x2))
    pygame.draw.polygon(screen, (59, 82, 139), ((0+dx,TAM), x0,x1,x2,x3, (TAM+dx,TAM)))

#Essa função desenha o display visto pelo motorista
#recebe dx, que seria o deslocamento da tela
#recebe as infos da reta (y=ax+b)
#recebe um vetor pos com os próximos 5 pontos
#recebe o tamanho da reta
#recebe se o motorista está indo para direita ou esquerda no mapa superior
#lado=1 (direita); lado=-1(esquerda); lado=0 (nenhum)
#velAtual = velocidade atual do motorista
#velocidades = vetor com as próximas 6 velocidades da melhor volta
#actualLap = volta atual
def display(screen,dx, a, b, pos, tamReta, lado, velAtual, velocidades, actualLap, bestLap, font):
    displayBasic(screen,dx)
    y = 250     #y começa em 250 e vai subindo de 45 em 45
    for i in range(5):
        dist = distancia(pos[i][0],pos[i][1],a,b)
        if dist == 0: 
            pygame.draw.circle(screen, (YELLOW if velAtual>velocidades[i+1] else GREEN), (TAM/2+dx,y), radius)
        else:
            distPixels = int(dist*deltaX[i]/tamReta)
            if distPixels > deltaX[i]: distPixels = deltaX[i]
            if estaAcima(pos[i][0],pos[i][1],a,b):
                if lado == 1:
                    pygame.draw.circle(screen,(YELLOW if velAtual>velocidades[i+1] else GREEN), (TAM/2+distPixels+dx,y), radius)
                else:
                    pygame.draw.circle(screen, (YELLOW if velAtual>velocidades[i+1] else GREEN), (TAM/2-distPixels+dx,y), radius)
            else:
                if lado == 1:
                    pygame.draw.circle(screen, (YELLOW if velAtual>velocidades[i+1] else GREEN), (TAM/2-distPixels+dx,y), radius)
                else:
                    pygame.draw.circle(screen, (YELLOW if velAtual>velocidades[i+1] else GREEN), (TAM/2+distPixels+dx,y), radius)
        y += 45
    text  = font.render('Veloc. atual = {0} m/s'.format(velAtual), True, (0,0,0))
    screen.blit(text, (dx+10, 10))
    text  = font.render('Veloc. (melhor volta) = {0} m/s'.format(velocidades[0]), True, (0,0,0))
    screen.blit(text, (dx+240, 10))
    #Tudo relacionado com volta escreve +1, por conta da "volta 0"
    text  = font.render('Volta atual = {0}'.format(actualLap+1), True, (0,0,0))
    screen.blit(text, (dx+10, 30))
    text  = font.render('Melhor volta = {0}'.format(bestLap+1), True, (0,0,0))
    screen.blit(text, (dx+240, 30))

def displayNoData(screen, dx, velAtual, font):
    displayBasic(screen,dx)
    text  = font.render('Velocidade atual = {0} m/s'.format(velAtual), True, (0,0,0))
    screen.blit(text, (dx+10, 10))

#Retorna se o ponto (x,y) está acima da reta (a,b)
def estaAcima(x,y,a,b):
    return (a*x+b) > y

#Retorna a distancia entre o ponto (x,y) e a reta (a,b)
def distancia(x,y,a,b):
    # return abs((a*x+b)-y)
    if a == 10000000:
        return abs(b-x)
    return abs(a * x - y + b) / math.sqrt(a**2 + 1)

#Retorna os valores de a e b para uma reta recebendo 2 pontos
def paramsReta(p1,p2):
    if p1[0] == p2[0]:
        a = 10000000
        b = p1[0]
        return a,b
    else:
        a = (p2[1]-p1[1])/(p2[0]-p1[0])
        b = p1[1]-a*p1[0]
        return a,b

def linesToPoints (linha1, linha2):
    points = []
    x1 = linha1[0]
    y1 = linha1[1]
    points.append((x1,y1))
    x2 = linha1[2]
    y2 = linha1[3]
    points.append((x2,y2))
    x3 = linha2[0]
    y3 = linha2[1]
    points.append((x3,y3))
    x4 = linha2[2]
    y4 = linha2[3]
    points.append((x4,y4))
    return points

def triangleArea(p1,p2,p3):
    det = p1[0]*p2[1] + p1[1]*p3[0] + p2[0]*p3[1] - p3[0]*p2[1] - p3[1]*p1[0] - p2[0]*p1[1] 
    return abs(det)/2.0

def compareArea(Points):
    area1 = triangleArea(Points[0],Points[1],Points[2]) + triangleArea(Points[0],Points[3],Points[2])
    area2 = triangleArea(Points[1],Points[2],Points[3]) + triangleArea(Points[1],Points[0],Points[3])
    return area1 == area2

def orderPoints(Points, k=0):
    #print("area1: {0}, area2: {1}, k={2}, {3}".format(area1,area2,k,Points))

    if compareArea(Points):
        #print("Retornei")
        return Points
    
    elif compareArea((Points[1],Points[0],Points[2],Points[3])):
        return (Points[1],Points[0],Points[2],Points[3])
    
    elif compareArea((Points[0],Points[1],Points[3],Points[2])):
        return ((Points[0],Points[1],Points[3],Points[2]))

    elif compareArea((Points[0],Points[2],Points[3],Points[1])):
        return ((Points[0],Points[2],Points[3],Points[1]))
    
    elif compareArea((Points[0],Points[2],Points[1],Points[3])):
        return ((Points[0],Points[2],Points[1],Points[3]))
    
    else:
        return ((Points[1],Points[0],Points[2],Points[3]))

def isPointInRegion(ponto, linha1, linha2):     #01,12,23,30
    # A região é definida por quatro pontos no formato (x, y)
    points = linesToPoints(linha1, linha2)
    points = orderPoints(points)
    area = triangleArea(points[0],points[1],points[2]) + triangleArea(points[0],points[3],points[2])
    areaTest = 0
    for i in range(3):
        areaTest += triangleArea(ponto, points[i], points[i+1])
    areaTest += triangleArea(ponto, points[3], points[0])
    if areaTest == area:
        return True
    else:
        return False

from library.orderingPoints import order_points

#Recebe ponto a verificar se esta na região
#Retorna o indice da região e os 4 pontos da região
def whatRegion(point, regions):
    #Função agora
    for i in range(len(regions)):
        points = linesToPoints(regions[i-1],regions[i])
        points = order_points(points)
        polygon = Path(points)
        if polygon.contains_point(point):
            return i, points
    # print(f"ponto ({point[0]}, {point[1]}) fora da região")
    return -1, []

def main():
    pass

if __name__ == "__main__":
    main()