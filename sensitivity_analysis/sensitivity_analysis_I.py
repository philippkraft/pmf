# -*- coding: utf-8 -*-
"""
Case Study I: Water balance - Multi layer Richards approach
The Case Study represents a summer wheat setup of PMF and with the
Catchment Modeling Framework (CMF) in the version cmf1d:

Weather     : Muenchenberg,

Soil texture: Various Sand,

Soil        : cmf1d,

Atmosphere  : cmf1d,      

Simulation  : 1.1.1980 - 31.12.1980 and 

Management  : Sowing - 1.3.JJJJ, Harvest - 8.1.JJJJ.


@author: Tobias

@version: 0.1 (29.06.2012)

@copyright: 
 This program is free software; you can redistribute it and/or modify it under  
 the terms of the GNU General Public License as published by the Free Software  
 Foundation; either version 3 of the License, or (at your option) any later 
 version. This program is distributed in the hope that it will be useful, 
 but WITHOUT ANY  WARRANTY; without even the implied warranty of MERCHANTABILITY 
 or  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
 more details. You should have received a copy of the GNU General 
 Public License along  with this program;
 if not, see <http://www.gnu.org/licenses/>.
"""


from pylab import *
#import pylab
import numpy
from datetime import *
import PMF
import cmf
from cmf_setup import cmf1d
from cmf_fp_interface import cmf_fp_interface
#from math import exp
    
#######################################
#######################################
### Runtime Loop
#from datetime import *

#def get_starttimeT(): 
#    return datetime(1992,1,1)
#    
#def get_endtimeT():
#    return datetime(1993,12,31)

def run(t,res,plant):
    if t.day==1 and t.month==3: #check sowing
        plant = PMF.createPlant_CMF() #create a plant instance without interfaces
        plant = PMF.connect(plant,cmf_fp,cmf_fp) #connect the plant with soil and atmosphere interface
    if t.day==1 and t.month==8: #check harvest
        plant =  None #delete plant instance
    if plant: #check, if plant exists
        plant(t,'day',1.) #run plant, daily time step, timeperiod: 1.             
    #calculate evaporation from bare soil
    baresoil(cmf_fp.Kr(),0.,cmf_fp.get_Rn(t, 0.12, True),cmf_fp.get_tmean(t),cmf_fp.get_es(t),cmf_fp.get_ea(t), cmf_fp.get_windspeed(t),0.,RHmin=30.,h=1.)    
    #get plant water uptake   
    flux = [uptake*-1. for uptake in plant.Wateruptake] if plant  else zeros(c.cell.layer_count())    
    #get evaporation from bare soil or plant model    
    flux[0] -= plant.et.evaporation if plant else baresoil.evaporation
    # set water flux of each soil layer from cmf   
    c.flux=flux
    # run cmf
    c.run(cmf.day)        
    #get status variables of cmf
    res.waterstorage.append(c.cell.layers.volume) #water content of each layer in [mm/day] (list with 40 soil layers)
    res.flux.append(c.flux) #water flux of each layer in [mm/day] (list with 40 soil layers)
    res.wetness.append(c.wetness) #wetness/water content of each layer in [%/day] (list with 40 soil layers)
    res.pF.append(c.pF)
    res.potential.append(c.potential)#!!
    res.porosity.append(c.porosity)#!!
    res.deep_percolation.append(c.groundwater.waterbalance(t)) #water flux to groundwater [mm/day]
    res.rain.append(c.cell.get_rainfall(t)) #rainfall in [mm/day]
    #get baresoil evaporation [mm/day]
    res.baresoil_evaporation.append(0.0) if plant else  res.baresoil_evaporation.append(baresoil.evaporation)       
    #get status variables of pmf
    #biomass status
    res.PotentialGrowth.append(plant.biomass.PotentialGrowth) if plant else res.PotentialGrowth.append(0) #[g/m2/day]
    res.ActualGrowth.append(plant.biomass.ActualGrowth) if plant else res.ActualGrowth.append(0) #[g/m2/day]
    res.biomass.append(plant.biomass.Total) if plant else res.biomass.append(0) #[g/m2]
    res.root_biomass.append(plant.root.Wtot) if plant else res.root_biomass.append(0) #[g/m2]
    res.shoot_biomass.append(plant.shoot.Wtot) if plant else res.shoot_biomass.append(0) #[g/m2]
    res.leaf.append(plant.shoot.leaf.Wtot) if plant else res.leaf.append(0) #[g/m2]
    res.stem.append(plant.shoot.stem.Wtot) if plant else res.stem.append(0) #[g/m2]
    res.storage.append(plant.shoot.storage_organs.Wtot) if plant else res.storage.append(0) #[g/m2]   
    res.lai.append(plant.shoot.leaf.LAI) if plant else res.lai.append(0) #[m2/m2]
    #development    
    res.developmentstage.append(plant.developmentstage.Stage[0]) if plant else res.developmentstage.append("")
    res.DAS.append(t-datetime(1980,3,1)) if plant else res.DAS.append(0)
    if plant:       
        if plant.developmentstage.Stage[0] != "D": 
            res.developmentindex.append(plant.developmentstage.StageIndex) if plant else res.developmentindex.append("")
        else:
            res.developmentindex.append("")
    else:
        res.developmentindex.append("")    
    #plant water balance [mm/day]
    res.ETo.append(plant.et.Reference) if plant else res.ETo.append(0)
    res.ETc.append(plant.et.Cropspecific) if plant else res.ETc.append(0)
    #transpiration is not equal to water uptake! transpiration is calculated without stress and wateruptake with stress!!!
    res.transpiration.append(plant.et.transpiration) if plant else res.transpiration.append(0) 
    res.evaporation.append(plant.et.evaporation) if plant else  res.evaporation.append(0)
    res.water_uptake.append(plant.Wateruptake) if plant else res.water_uptake.append(zeros(c.cell.layer_count())) #(list with 40 layers)    
    res.stress.append((plant.water_stress, plant.nutrition_stress) if plant else (0,0)) # dimensionsless stress index (0-->no stress; 1-->full stress)    
    #root growth
    res.potential_depth.append(plant.root.potential_depth) if plant else res.potential_depth.append(0) #[cm]
    res.rooting_depth.append(plant.root.depth) if plant else res.rooting_depth.append(0) #[cm]
    res.branching.append(plant.root.branching) if plant else res.branching.append(zeros(c.cell.layer_count())) # growth RATE in each layer per day [g/day](list with 40 layers)
    res.root_growth.append(plant.root.actual_distribution) if plant else  res.root_growth.append(zeros(c.cell.layer_count())) # total root biomass in each layer [g/layer]
    res.time.append(t)
    return plant

class Res(object):
    def __init__(self):
        self.flux=[]
        self.water_uptake = []
        self.branching = []
        self.transpiration = []
        self.evaporation = []
        self.biomass = []
        self.root_biomass = []
        self.shoot_biomass = []
        self.lai = []
        self.root_growth = []
        self.ETo = []
        self.ETc = []
        self.wetness = []
        self.pF=[]
        self.potential=[]#!!
        self.porosity=[]#!!
        self.rain = []
        self.temperature = []
        self.DAS = []
        self.stress = []
        self.leaf=[]
        self.stem=[]
        self.storage=[]
        self.potential_depth=[]
        self.rooting_depth=[]
        self.time = []
        self.developmentstage = []
        self.PotentialGrowth = []
        self.ActualGrowth = []
        self.developmentindex=[]
        self.deep_percolation=[]
        self.baresoil_evaporation=[]
        self.waterstorage=[]
    def __repr__(self):
        return "Shoot=%gg, Root=%gg, ETc = %gmm, Wateruptake=%gmm, Stress=%s" % (self.shoot_biomass[-1],self.root_biomass[-1],self.ETc[-1],sum(self.water_uptake[-1]),self.stress[-1])

#######################################
#######################################
### Setup script

if __name__=='__main__':
    
    #from Atmosphere import ClimateStation
#    import psyco
#    psyco.full()
    
    #Create cmf cell    

    
#########Plot1 Kersebaum#########
#########Bodenschichten##########
    #Interpolated Soillayers    
    #c=cmf1d(sand=[90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,88.33,86.67,85.00,83.33,81.67,80.00,82.00,84.00,86.00,88.00,90.00,92.00,92.33,92.67,93.00,93.33,93.67,94.00,94.13,94.27,94.40,94.53,94.67,94.80,94.93,95.07,95.20,95.33,95.47,95.60,95.73,95.87,96.00],silt=[2.00,2.17,2.33,2.50,2.67,2.83,3.00,3.33,3.67,4.00,4.33,4.67,5.00,5.50,6.00,6.50,7.00,7.50,8.00,7.33,6.67,6.00,5.33,4.67,4.00,3.83,3.67,3.50,3.33,3.17,3.00,2.93,2.87,2.80,2.73,2.67,2.60,2.53,2.47,2.40,2.33,2.27,2.20,2.13,2.07,2.00],clay=[8.00,7.83,7.67,7.50,7.33,7.17,7.00,6.67,6.33,6.00,5.67,5.33,5.00,6.17,7.33,8.50,9.67,10.83,12.00,10.67,9.33,8.00,6.67,5.33,4.00,3.83,3.67,3.50,3.33,3.17,3.00,2.93,2.87,2.80,2.73,2.67,2.60,2.53,2.47,2.40,2.33,2.27,2.20,2.13,2.07,2.00],c_org=[76.00,74.33,72.67,71.00,69.33,67.67,66.00,57.67,49.33,41.00,32.67,24.33,16.00,14.67,13.33,12.00,10.67,9.33,8.00,6.67,5.33,4.00,2.67,1.33,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00],bedrock_K=0.01,layercount=6,layerthickness=[.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05],tracertext='')
    #Orignal Soillayer      
    c=cmf1d(sand=[90.,90.,80.,92.,94.,96.],silt=[3.,5.,8.,4.,3.,2.],clay=[7.,5.,12.,4.,3.,2.],c_org=[.66,.16,.08,0.,0.,0.],bedrock_K=0.01,layercount=6,layerthickness=[.3,.3,.3,.3,.3,.75],tracertext='')
#################################
#################################

#########Plot2 Kersebaum#########
#########Bodenschichten##########
    #Interpolated Soillayers
    #c=cmf1d(sand=[82.00,82.50,83.00,83.50,84.00,84.50,85.00,85.42,85.83,86.25,86.67,87.08,87.50,87.92,88.33,88.75,89.17,89.58,90.00,88.75,87.50,86.25,85.00,83.75,82.50,81.25,80.00,80.00,80.00,80.00,80.00,80.00,80.00,80.00,80.00,85.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00,90.00],silt=[13.00,12.50,12.00,11.50,11.00,10.50,10.00,9.58,9.17,8.75,8.33,7.92,7.50,7.08,6.67,6.25,5.83,5.42,5.00,5.38,5.75,6.13,6.50,6.88,7.25,7.63,8.00,8.25,8.50,8.75,9.00,9.25,9.50,9.75,10.00,7.50,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00],clay=[5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.88,6.75,7.63,8.50,9.38,10.25,11.13,12.00,11.75,11.50,11.25,11.00,10.75,10.50,10.25,10.00,7.50,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00,5.00],c_org=[0.69,0.67,0.65,0.64,0.62,0.60,0.58,0.54,0.51,0.47,0.43,0.39,0.36,0.32,0.28,0.24,0.21,0.17,0.13,0.11,0.10,0.08,0.07,0.05,0.03,0.02,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00],bedrock_K=0.01,layercount=6,layerthickness=[.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05],tracertext='')
    #Orignal Soillayer    
    #c=cmf1d(sand=[85.,90.,80.,80.,90.,90],silt=[10.,5.,8.,10.,5.,5.],clay=[5.,5.,12.,10.,5.,5.],c_org=[.58,.13,0.,0.,0.,0.],bedrock_K=0.01,layercount=6,layerthickness=[.3,.6,.4,.4,.1,.45],tracertext='')
#################################
#################################

#########Plot3 Kersebaum#########
#########Bodenschichten##########
    #Interpolated Soillayers    
    #c=cmf1d(sand=[81.00,81.67,82.33,83.00,83.67,84.33,85.00,85.36,85.71,86.07,86.43,86.79,87.14,87.50,87.86,88.21,88.57,88.93,89.29,89.64,90.00,85.50,81.00,80.96,80.91,80.87,80.83,80.78,80.74,80.70,80.65,80.61,80.57,80.52,80.48,80.43,80.39,80.35,80.30,80.26,80.22,80.17,80.13,80.09,80.04,80.00],silt=[12.00,11.50,11.00,10.50,10.00,9.50,9.00,8.71,8.43,8.14,7.86,7.57,7.29,7.00,6.71,6.43,6.14,5.86,5.57,5.29,5.00,5.50,6.00,6.13,6.26,6.39,6.52,6.65,6.78,6.91,7.04,7.17,7.30,7.43,7.57,7.70,7.83,7.96,8.09,8.22,8.35,8.48,8.61,8.74,8.87,9.00],clay=[7.00,6.83,6.67,6.50,6.33,6.17,6.00,5.93,5.86,5.79,5.71,5.64,5.57,5.50,5.43,5.36,5.29,5.21,5.14,5.07,5.00,9.00,13.00,12.91,12.83,12.74,12.65,12.57,12.48,12.39,12.30,12.22,12.13,12.04,11.96,11.87,11.78,11.70,11.61,11.52,11.43,11.35,11.26,11.17,11.09,11.00],c_org=[0.76,0.74,0.71,0.69,0.67,0.64,0.62,0.59,0.55,0.52,0.48,0.45,0.41,0.38,0.34,0.31,0.27,0.24,0.20,0.17,0.13,0.07,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00],bedrock_K=0.01,layercount=4,layerthickness=[.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05],tracertext='')        
    #Orignal Soillayer      
    #c=cmf1d(sand=[85.,90.,81.,80.],silt=[9.,5.,6.,9],clay=[6.,5.,13.,11.],c_org=[.62,.13,0.,0.],bedrock_K=0.01,layercount=4,layerthickness=[.3,.7,.1,1.15],tracertext='')
#################################
#################################
    print "cmf is setup"
    #start = get_starttimeT()
    Datenstart = datetime(1992,1,1)    
    start = datetime(1992,1,1)    
    end = datetime(1993,4,21) 
   
    #end = get_endtimeT()
    #Station1_Giessen = meteo() #!!!
    #Station1_Giessen.load_weather('climate_giessen.csv') #!!!
    c.load_meteo(Datenstart,start, 'Muencheberg', rain_factor=1.)
    print "meteo loaded"
    cmf_fp = cmf_fp_interface(c.cell)
    cmf_fp.default_Nconc = .3
    #cmf_fp.default_Nconc = .1
    
    
    
    print "Interface to PMF"
    c.cell.saturated_depth=5.
    #Create evapotranspiration instance or bare soil conditions
    baresoil = PMF.ProcessLibrary.ET_FAO([0.,0.,0.,0.],[0.,0.,0.,0.],kcmin = 0.)
    
    #set management
    sowingdate = set(datetime(i,3,1) for i in range(1980,2100))
    harvestdate = set(datetime(i,8,1) for i in range(1980,2100))
    #Simulation period
    
    #Simulation
    
    #start = get_starttimeT()
    #print start
    #end = get_endtimeT()
    res = Res()
    plant = None
    print "Run ... "    
    start_time = datetime.now()
    c.t = start
    start_content = np.sum(c.cell.layers.volume)
    Vergangene_Tage = 0
    while c.t<end:
        plant=run(c.t,res,plant)
        Vergangene_Tage+=1
        
    
    water_content_0_30cm = res.porosity[Vergangene_Tage-1][0]*res.wetness[Vergangene_Tage-1][0]*100 #Porenvolumen0-30cm * Wassergehalt pro Porenvolumen0-30cm *100 (Prozentangabe fuer Endtag)
    water_content_30_60cm = res.porosity[Vergangene_Tage-1][1]*res.wetness[Vergangene_Tage-1][1]*100 #Porenvolumen30-60cm * Wassergehalt pro Porenvolumen30-60cm *100 (Prozentangabe fuer Endtag)
    water_content_60_90cm = res.porosity[Vergangene_Tage-1][2]*res.wetness[Vergangene_Tage-1][2]*100 #Porenvolumen60-90cm * Wassergehalt pro Porenvolumen60-90cm *100 (Prozentangabe fuer Endtag)
    
    print '\n############ Water_content_cmf ##############'
    print '\nWassergehalt berechnet fuer: ' + str(end.date())
    print 'Wassergehalt 0 bis 30 cm:' 
    print round(water_content_0_30cm,1) 
    print 'Wassergehalt 30 bis 60 cm:'
    print round(water_content_30_60cm,1)
    print 'Wassergehalt 60 bis 90 cm:'
    print round(water_content_60_90cm,1)    
    print '\n'
    
    print '######### Water_content_Kersebaum ###########'
    c.load_water_content('Water_content_Plot1.csv')
    
    

    
    
    
    P = np.sum(res.rain) # precipitation
    E = np.sum(res.evaporation)+np.sum(res.baresoil_evaporation) # evaporation from baresoil and covered soil
    T = np.sum(np.sum(res.water_uptake)) # actual transpiration
    DP = np.sum(res.deep_percolation) # deep percolation (groundwater losses)
    storage =np.sum(c.cell.layers.volume)- start_content 
    print '\n################################\n' + '################################\n' + 'Water balance'
    print  "%gmm (P) = %gmm (E) +  %gmm (T) + %gmm (DP) + %gmm (delta)" % (P,E,T,DP,storage)
    print  "Water content according to water balance: %gmm \nActual water content of soil: %gmm" % ((start_content + P-DP-T-E),np.sum(c.cell.layers.volume))

    
    
    ######
    # groundwater.waterbalance -> der Fluß ist nicht in flux mit drin!!!
######################################
######################################
## Show results

#    timeline=drange(start,end,timedelta(1))
#    pylab.subplot(311)
#    pylab.contourf(transpose([r[:20] for r in res.pF]),cmap=cm.jet,aspect='auto',interpolation='nearest',extent=[0,len(timeline),100,0],vmin=0.,vmax=6.0)#conturf statt imshow, macht das die Bodenlayer korrekt dargestellt werden. Generell mehr Bodenlayer erzeugen (per hand interpolation)
#    ylabel('Depth [cm]')
#    xlabel('Day of year')
#    pylab.subplot(312)
#    plot_date(timeline,[i[0] for i in res.stress],'b',label='Drought stress')
#    ylabel('Stress index [-]')
#    ylim(0,1)
#    legend(loc=0)
#    pylab.subplot(313)
#    plot_date(timeline,[-r for r in res.rooting_depth],'g',label='Actual')
#    plot_date(timeline,[-r for r in res.potential_depth],'k--',label='Potential')
#    ylabel('Rooting depth [mm]')
#    legend(loc=0)
#    show()




    timeline=drange(start,end,timedelta(1))
    subplot(311)
    imshow(transpose([r[:20] for r in res.pF]),cmap=cm.jet,aspect='auto',interpolation='nearest',extent=[0,len(timeline),100,0],vmin=0.,vmax=6.0)#conturf statt imshow, macht das die Bodenlayer korrekt dargestellt werden. Generell mehr Bodenlayer erzeugen (per hand interpolation)
    ylabel('Depth [cm]')
    xlabel('Day of year')
    subplot(312)
    plot_date(timeline,[i[0] for i in res.stress],'b',label='Drought stress')
    ylabel('Stress index [-]')
    ylim(0,1)
    legend(loc=0)
    subplot(313)
    plot_date(timeline,[-r for r in res.rooting_depth],'g',label='Actual')
    plot_date(timeline,[-r for r in res.potential_depth],'k--',label='Potential')
    ylabel('Rooting depth [mm]')
    legend(loc=0)
    show()

#===============================================================================
# import csv, codecs, cStringIO
# 
# with open('cmf1D.csv', 'wb') as f:    
#     writer = csv.writer(f,delimiter='\t', quotechar='"',quoting=csv.QUOTE_ALL)
#     writer.writerow(['Year','Month','Day','Rainfall','Temperature','Radiation','Wetness','Stage','StageIndex','Transpiration','Evaporation','Wateruptake','Root biomass','Shoot biomass','PotentialGrowth','ActualGrowht','LAI','RootingDepth','Stress'])
#     for i,day in enumerate(res.time):
#         writer.writerow([day.year,day.month,day.day,
#                          res.rain[i],res.temperature[i],res.radiation[i],sum(res.wetness[i]),
#                          res.developmentstage[i],res.developmentindex[i],res.transpiration[i],res.evaporation[i],sum(res.water_uptake[i]),res.root_biomass[i],res.shoot_biomass[i],res.PotentialGrowth[i],res.ActualGrowth[i],res.lai[i],res.rooting_depth[i],res.stress[i][0]])
#===============================================================================

