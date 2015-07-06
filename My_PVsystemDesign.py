#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'Wang Hongwei'
"""
详细介绍：内蒙古工业大学，电力学院，电气工程及其自动化专业，可再生能源及其自动化课程，一次课程设计。

计算原理：详见 introduction.doc 文件。

简介：
    独立光伏发电系统计算程序：针对某个地区，设计独立光伏发电系统（如路灯），通过查询该地区的
太阳辐照量（查询国家气象局发布的数据，见参考资料：中国中国气象辐射资料年册），通过给定的数值，
计算出平均月日均辐照量。
    路灯设置亮灭原则是太阳升起时灯灭，太阳落下时开灯，通过公式计算出太阳升起和落下的时间。
黑夜时间即路灯工作时间。
    最后将相关参数生成一个 .csv 文件，文件命名规则是根据程序运行时间生成文件名，以确保不会有重复命名文件。
"""
import math
import time
import csv

fai = 43.6          #所在地区的纬度
beta = 60.1
H = [0, 7.57, 11.96, 15.81, 19.03, 20.58, 22.18, 22.44, 19.41, 17.33, 12.26, 9.31, 7.27]    #refer to weather data.Tongliao.
pOfLight = 30.0
vOfLight = 12
n1=n2=0.9
#ki = 0.66             # coefficient of (imax-imin) to define the value of I.
ki = 0.495
DOD = 0.7
ks = 1.5
Vd = 12.0
Vb = 1.0

def getDays( year, month ):
    day = 31
    while day:
        try:
            time.strptime( '%s-%s-%d'%( year, month, day ), '%Y-%m-%d' )
            return day
        except:
            day -= 1

daysOfMonth = [0]*13   # define the length of array moth is 13, cause it's begin with moth[0].

Month = xrange(1,13)   # xrange(1,13) will make a array with length of 12[1-12].

for i in Month:
    daysOfMonth[i] = getDays( 2014, i )

Isc = 1367
listOfCwj = [1]*366
Ws = [1]*366
Wst = [1]*366
Rb = [1]*366
Part1OfRb = [1]*366
Part2OfRb = [1]*366
Part3OfRb = [1]*366
Part4OfRb = [1]*366
Ho = [1]*366
timeOfNight = [1]*366
daysOfYear = xrange(1,366)

for i in daysOfYear:
    listOfCwj[i] = 23.45*math.sin(math.radians(360.0/365*(284+i))) #OK.
    Ws[i] = math.acos(-math.tan(math.radians(fai))*math.tan(math.radians(listOfCwj[i])))
    timeOfNight[i] = 24.0-2.0*Ws[i]/math.radians(15)
    Wst[i] = min(Ws[i],math.acos(-math.tan(math.radians(fai - beta))*math.tan(math.radians(listOfCwj[i]))))
    Part1OfRb[i] = math.cos(math.radians(fai - beta))*math.cos(math.radians(listOfCwj[i]))*math.sin(Wst[i])
    Part2OfRb[i] = Wst[i]*math.sin(math.radians(fai - beta))*math.sin(math.radians(listOfCwj[i]))
    Part3OfRb[i] = math.cos(math.radians(fai))*math.cos(math.radians(listOfCwj[i]))*math.sin(Ws[i])
    Part4OfRb[i] = Ws[i]*math.sin(math.radians(fai))*math.sin(math.radians(listOfCwj[i]))
    Rb[i] = (Part1OfRb[i] + Part2OfRb[i])/(Part3OfRb[i] + Part4OfRb[i])
    Ho[i] = 24.0/math.pi*Isc*(1+0.033*math.cos(math.radians(360.0/365*i)))*(Part3OfRb[i] + Part4OfRb[i])*3.6/1000

theNumOfMonth = [0]*13
averOfRb = [0]*13
averOfHo = [0]*13
averOfNight = [0]*13
QlOfMonth = [0]*13

for i in xrange(1,13):
    theNumOfMonth[i] = theNumOfMonth[i-1] + daysOfMonth[i]

for i in xrange(1,13):      # compute month's average of Rb and Ho.
    monthSumOfRb = 0
    monthSumOfHo = 0
    monthSumOfNight = 0
    for j in xrange(theNumOfMonth[i-1]+1,theNumOfMonth[i]+1):
        monthSumOfRb += Rb[j]
        monthSumOfHo += Ho[j]
        monthSumOfNight += timeOfNight[j]
    averOfRb[i] = monthSumOfRb/daysOfMonth[i]
    averOfHo[i] = monthSumOfHo/daysOfMonth[i]
    averOfNight[i] = monthSumOfNight/daysOfMonth[i]
    QlOfMonth[i] = pOfLight*averOfNight[i]/vOfLight

Hd = [0]*13
Hb = [0]*13
Kt = [0]*13
for i in xrange(1,13):
    Kt[i] = H[i]/averOfHo[i]
    Hd[i] = (1.390-4.027*(Kt[i])+5.531*(pow(Kt[i],2))-3.108*(pow(Kt[i],3)))*H[i]
    Hb[i] = H[i] - Hd[i]

Ht = [0]*13
Hbt = [0]*13
Hdt = [0]*13
Hrt = [0]*13
kwhOfHt = [0]*13
for i in xrange(1,13):
    Hbt[i] = Hb[i]*averOfRb[i]
    Hdt[i] = Hd[i]*(Hb[i]/averOfHo[i]+0.5*(1-Hb[i]/averOfHo[i])*(1+math.cos(beta)))
    Hrt[i] = 0.45*0.2*H[i]*(1-math.cos(math.radians(beta)))
    Ht[i] = Hbt[i]+Hdt[i]+Hrt[i]
    kwhOfHt[i] = Ht[i]/3.6

################################################################################################################
#########################################   Thank God!!!    ####################################################
################################################################################################################
averQlOfYear = 0
averHtOfYear = 0
for i in xrange(1,13):
    averQlOfYear += QlOfMonth[i]
    averHtOfYear += kwhOfHt[i]
averQlOfYear = averQlOfYear/12.0
averHtOfYear = averHtOfYear/12.0

tmpOfHtMin = [0]*12
for i in xrange(1,13):
    tmpOfHtMin[i-1] = kwhOfHt[i]
Htmin = min(tmpOfHtMin)

imi = averQlOfYear/(averHtOfYear*n1*n2)
ima = averQlOfYear/(Htmin*n1*n2)
valOfI = (ima-imi)*ki+imi

Qa = [0]*13
Qc = [0]*13
deltaQ = [0]*12
for i in xrange(1,13):
    Qa[i] = daysOfMonth[i]*valOfI*kwhOfHt[i]*n1*n2
    Qc[i] = daysOfMonth[i]*QlOfMonth[i]
    deltaQ[i-1] = Qa[i]-Qc[i]

sumOfQi = 0
for i in xrange(12):
    sumOfQi -= min(0,deltaQ[i])

holdDays = sumOfQi/averQlOfYear

B = sumOfQi/(DOD*n2)

Pscell = ks*valOfI*(Vd+Vb)

print holdDays
print valOfI
print Pscell
print B
################################################################################################################
#########################################   Thank God, Again!!!    #############################################
################################################################################################################

month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
filename = '%0.0f' % time.time() + '.csv'
with open(filename, 'wb') as csvfile:
    spamwriter = csv.writer(csvfile,dialect='excel')
    spamwriter.writerow(['','','','','光伏发电系统——太阳能路灯设计的相关计算'])
    spamwriter.writerow([])
    spamwriter.writerow(['','参数设定：'])
    spamwriter.writerow(['','fai——光伏系统地理纬度，这里取通辽市纬度：'+ str(fai) +'°；'])
    spamwriter.writerow(['','s——光伏组件安装倾角，取'+ str(beta) +'°，可根据计算结果做进一步调整；'])
    spamwriter.writerow(['','ki——为计算I时设定的系数，取值范围为0到1，可根据计算结果做进一步调整，这里取'+str(ki)+'；'])
    spamwriter.writerow(['','Plight——路灯功率，这里取'+str(pOfLight)+ 'W ；'])
    spamwriter.writerow(['','Vwork——路灯工作电压，这里取'+str(vOfLight)+'V ；'])
    spamwriter.writerow(['','n1——从方阵到蓄电池回路的输入效率，这里取'+str(n1)+'；'])
    spamwriter.writerow(['','n2——由蓄电池到负载的放电回路效率，这里取'+str(n2)+'；'])
    spamwriter.writerow(['','DOD——蓄电池的放电深度，通常取0.3到0.8，此题中取'+str(DOD)+'；'])
    spamwriter.writerow(['','k——阵安全系数，通常取1到1.5，此题中取'+str(ks)+'；'])
    spamwriter.writerow(['','Vd——蓄电池充电电压，此题中取为'+str(Vd)+'V ；'])
    spamwriter.writerow(['','Vb——防反充二极管及线路压降，此题中取为'+str(Vb)+'V 。'])
    spamwriter.writerow(['','（备注：详细计算方程和参数见文本文档。）'])
    spamwriter.writerow([])
    spamwriter.writerow([])
    spamwriter.writerow(['', 'Rb', 'Ho', 'H', 'Kt', 'Hd', 'Hb', 'Hdt', 'Hbt', 'Hrt', 'Ht', 'Ht(KW·h)'])
    for i in xrange(1,13):
        spamwriter.writerow(['%s' % month[i-1],"%.3f" % averOfRb[i], "%.3f" % averOfHo[i], "%.2f" % H[i], "%.3f" % Kt[i], "%.3f" % Hd[i], "%.3f" % Hb[i], "%.3f" % Hdt[i], "%.3f" % Hbt[i], "%.3f" % Hrt[i], "%.4f" % Ht[i], "%.4f" % kwhOfHt[i]])
    spamwriter.writerow([])
    spamwriter.writerow(['','Rb——倾斜面与水平面上直接辐射量的比值，无量纲；'])
    spamwriter.writerow(['','Ho——大气层外水平面上的太阳辐射量；'])
    spamwriter.writerow(['','H——水平面上的总辐射量，气象站观测数据；'])
    spamwriter.writerow(['','Kt——晴朗指数，无量纲；'])
    spamwriter.writerow(['','Hd——水平面上的散射辐射量，可通过拟合法求出；'])
    spamwriter.writerow(['','Hb——水平面上的直接辐射量；'])
    spamwriter.writerow(['','Hdt——倾斜面上的太阳散射辐射量；'])
    spamwriter.writerow(['','Hbt——倾斜面上的太阳直接辐射量；'])
    spamwriter.writerow(['','Hrt——倾斜面上的地面反射辐射量；'])
    spamwriter.writerow(['','Ht——光伏阵列太阳总辐射量，（兆焦耳*每天/平方米）；'])
    spamwriter.writerow(['','Ht(KW·h)——光伏阵列太阳总辐射量，（千瓦时*每天/平方米）；'])
    spamwriter.writerow(['','（备注：以上关于辐射量的参数若不做特殊说明，单位都是（兆焦耳*每天/平方米））；'])
    spamwriter.writerow([])
    spamwriter.writerow([])
    spamwriter.writerow(['', 'Twork', 'Ql', 'Ht(KW·h)', 'Qa', 'Qc', 'Qa-Qc'])
    for i in xrange(1,13):
        spamwriter.writerow(['%s' % month[i-1],"%.3f" % averOfNight[i],"%.3f" % QlOfMonth[i], "%.3f" % kwhOfHt[i], "%.3f" % Qa[i], "%.3f" % Qc[i], "%.3f" % deltaQ[i-1]])
    spamwriter.writerow([])
    spamwriter.writerow(['','Twork——月均日路灯黑夜工作时间，(h)；'])
    spamwriter.writerow(['','Ql——负载耗电量；'])
    spamwriter.writerow(['','Ht(KW·h）——月均日光伏阵列太阳总辐射量，（千瓦时*每天/平方米）；'])
    spamwriter.writerow(['','Qa——方阵各月发电量；'])
    spamwriter.writerow(['','Qc——各月负载耗电量；'])
    spamwriter.writerow(['','Qa-Qc——当月亏欠量；'])
    spamwriter.writerow(['','（备注：以上Ql、Qa、Qc、Qa-Qc的单位是（千瓦时））；'])
    spamwriter.writerow([])
    spamwriter.writerow([])
    spamwriter.writerow(['','Imin','Imax','I'])
    spamwriter.writerow(['',"%.3f" % imi,"%.3f" % ima,"%.3f" % valOfI])
    spamwriter.writerow([])
    spamwriter.writerow(['','Imin——方阵输出的最小电流；'])
    spamwriter.writerow(['','Imax——方阵输出的最大电流；'])
    spamwriter.writerow(['','I——（可能的）方阵输出电流；'])
    spamwriter.writerow([])
    spamwriter.writerow([])
    spamwriter.writerow(['','n1','B','P'])
    spamwriter.writerow(['',"%.3f" % holdDays,"%.3f" % B,"%.3f" % Pscell])
    spamwriter.writerow([])
    spamwriter.writerow(['','n1——发生亏欠月时，蓄电池能坚持的天数；'])
    spamwriter.writerow(['','B——蓄电池容量，（Ah）；'])
    spamwriter.writerow(['','P——太阳电池方阵容量，（W）。'])
