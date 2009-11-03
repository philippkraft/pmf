"""
This setup build a cmf1d cell with defualt values. For a
given management with harvest and sowingdates a crop is 
created from the FlowerPower crop model. The plant growth
processes are taken from the FlowerPower process library.
The crop parameters are created from liture data which refer
to summer wheat. Meterological timeseries refer to a weather 
station from Giessen.
"""
from pylab import *
from datetime import *
import FlowerPower
import cmf
from cmf_setup import *
import struct

def getCropSpecificParameter(path):
    """
    Reads crop specific parameters from a
    parameterisation file
    
    @type path: String
    @param path: Path from the parametrisation file.
    @rtype: list
    @return: List with crop specific parameters.
    """
    param = [line for line in file(path+'.txt',"r") if line[0]!='#']
    return [eval(each) for each in param]
def timeseries_from_file(f):

    """ Loads a timeseries saved with to_file from a file

    Description of the file layout:

    byte:

    0   Number of (int64)

    8   Begin of timeseries (in ms since 31.12.1899) (int64)

    16  Step size of timeseries (in ms) (int64)

    24  Interpolation power (int64)

    32  First value of timeseries (float64)

    """
    # Open the file
    if isinstance(f,str):
        f=file(f,'rb')
    elif not hasattr(f,'read'):
        raise TypeError("The file f must either implement a 'read' method,like a file, or must be a valid file name")
    # Get the meta data header
    header_length=struct.calcsize('qqqq')
    header=struct.unpack('qqqq',f.read(header_length))
    # Create a timeseries
    res=cmf.timeseries(header[1]*cmf.ms,header[2]*cmf.ms,header[3])
    # Put the data into the timeseries
    res.extend(struct.unpack('%id' % header[0],f.read(-1)))
    return res 
def load_meteo(project,stationname='Giessen'):
    # Load rain timeseries (doubled rain of giessen for more interstingresults)
    rain=timeseries_from_file(stationname + '.rain')*1.
    # Create a meteo station
    meteo=project.meteo_stations.add_station(stationname)
    # Meteorological timeseries
    meteo.Tmax=timeseries_from_file(stationname+'.Tmax')
    meteo.Tmin=timeseries_from_file(stationname+'.Tmin')
    meteo.rHmean=timeseries_from_file(stationname+'.rHmean')
    meteo.Windspeed=timeseries_from_file(stationname+'.Windspeed')
    meteo.Sunshine=timeseries_from_file(stationname+'.Sunshine')
    # Use the rainfall for each cell in the project
    cmf.set_precipitation(project.cells,rain)
    # Use the meteorological station for each cell of the project
    cmf.set_meteo_station(project.cells,meteo)
def createCrop_LUEconcept(soil,atmosphere,CropParams):
    """
    Returns a plant instance with the given parameter.
    
    Creates a plant with the given soil and amtosphere interface.
    The crop specific parameters must be taken from the input file.
    All other needed interfaces are set with the default classes.
    
    Discription of the input file:
    CropParams[0] : Basal crop coefficiants for each season
    CropParams[1] : Ligth use efficiency
    CropParams[2] : Extinction coefficiant
    CropParams[3] : Development
    CropParams[4] : K_m
    CropParams[5] : NO3_min
    CropParams[6] : Partitioning shoot
    CropParams[7] : Partitioning root
    CropParams[8] : Partitioning leaf
    CropParams[9] : Partitioning stem
    CropParams[10] : Partitioning storage
    CropParams[11] : tbase
    CropParams[12] : rootability_thresholds
    CropParams[13] : pressure_threshold
    CropParams[14] : plant_N
    CropParams[15] : leaf_specific_weight
    CropParams[16] : root_growth
    CropParams[17] : max_height
    CropParams[18] : Logistic growht rate
    CropParams[19] : Capacity limit
    
    @type soil: soil
    @param soil: Soil instance
    @type atmosphere: atmosphere
    @param atmosphere: Atmosphere instance
    @type CropParams: list
    @param CropParams: List with specific crop coeffciants.
    
    @rtype: FlowerPower.PlantComponents.Plant
    @return: Plant with specific parameters and soil and atmospere interface.
    """
    #SummerWheat
    #Development
    stage = CropParams[3]#[['Emergence',160.],['Leaf development',208.],['Tillering',421.],['Stem elongation',659.],['Anthesis',901.],['Seed fill',1174.],['Dough stage',1556.],['Maturity',1665.]]
    #Basal crop coefficiants for each season
    kcb = CropParams[0]#[0.15,1.1,0.15]
    #Lenght of seasons
    seasons = [stage[0][1], stage[3][1]-stage[0][1], stage[6][1]-stage[3][1], stage[-1][1]-stage[3][1]]
    #Ligth use efficiency
    LUE = CropParams[1]#3.0       
    #Extinction coefficiant
    k = CropParams[2]#0.4
    #K_m
    K_m = CropParams[4]#0.
    #NO3_min
    NO3_min = CropParams[5]#0.
    #Partitioning shoot
    shoot = CropParams[6]#[.0,.9,.9,.9,.95,1.,1.,1.]
    #Partitioning root
    root = CropParams[7]#[.0,.1,.1,.1,.05,.0,.0,.0]
    #Partitioning leaf
    leaf = [CropParams[8][i]*perc for i,perc in enumerate(shoot)]#[[.0,.5,.5,.3,0.,.0,.0,.0][i]*perc for i,perc in enumerate(shoot)]
    #Partitioning stem
    stem = [CropParams[9][i]*perc for i,perc in enumerate(shoot)]#[[.0,.5,.5,.7,.3,.0,.0,.0][i]*perc for i,perc in enumerate(shoot)]
    #Partitioning storage
    storage = [CropParams[10][i]*perc for i,perc in enumerate(shoot)]#[[.0,.0,.0,.0,.7,1.,1.,1.][i]*perc for i,perc in enumerate(shoot)]
    #tbase
    tbase = CropParams[11]#0.
    #rootability_thresholds
    rootability = CropParams[12]#[1.5,0.5,16000.,.0,0.0,0.0]
    #pressure_threshold
    pressure_thresholds = CropParams[13]#[0.,1.,500.,16000.]
    #plant_N
    plantN = CropParams[14]#[[160.,0.43],[1174.,0.16]]
    #leaf_specific_weight
    leaf_specific_weight = CropParams[15]#50.
    #root_growth
    root_growth = CropParams[16]#1.2
    #vetical_elongation
    max_height = CropParams[17]#1.0
    
    #Crop process models from ProcesLibrary
    et = FlowerPower.ET_FAO(kcb,seasons)
    
    biomass = FlowerPower.Biomass_LUE(LUE,k)
    development = FlowerPower.Development(stage)
    layer = FlowerPower.SoilLayer()
    layer.get_rootingzone(c.get_profile())
    nitrogen = FlowerPower.Nitrogen(layercount=len(layer))
    water = FlowerPower.Water_Feddes(layercount=len(layer))
    #Creates plant
    return FlowerPower.Plant(soil,atmosphere,et,water,biomass,development,layer,nitrogen,
                 shoot,root,leaf,stem,storage,root_growth=3.)
def run(start,end,step):
    #Set cmf time
    c.t = start
    
    Dr_new = 0
    
    
    #Modelrun for the given time period
    for t in drange(start,end,step):
        time = num2date(t)
            
        #sowing
        if t in sowingdate: plant = createCrop_LUEconcept(c,c,SummerWheat)
        #harvest
        if t in harvestdate: FlowerPower.Plant.Count-=1
    
        #Let grow
        if FlowerPower.Plant.Count > 0: plant(time,'day',1.)
        
        #Calculates evaporation for bare soil conditions
        #baresoil(c.Kr_cmf(),0.,c.get_Rn(time, 0.12, True),c.get_tmean(time),c.get_es(time),c.get_ea(time),
        #c.get_windspeed(time), 0.12,0.12,100.,RHmin=30.,h=1.)
        
        #Water flux from soil to plant
        
   
        
        #Calculation of water balance with cmf
        swc(plant.et.Cropspecific if FlowerPower.Plant.Count >0 else 0, plant.et.Evaporation if FlowerPower.Plant.Count >0 else 0, c.cell.rain(time), plant.root.depth if FlowerPower.Plant.Count >0 else 0)

        if FlowerPower.Plant.Count > 0:
            print time.year,time.month,time.day#,('Thermaltime: %4.3f, Biomass_LUE: %4.2f, LAI: %4.2f') % (plant.developmentstage.Thermaltime,plant.biomass.Total, plant.shoot.leaf.LAI)
            #print time.year,time.month,time.day, ('Waterdemand: %4.3f, Wateruptake: %4.3f') % (plant.et.Transpiration,sum(plant.water.Uptake))
            #print time.year,time.month,time.day, 'Wateruptake: ',['%4.2f' % w for w in plant.water.Uptake][:10]
            #print time.year,time.month,time.day, 'Rootbiomass: ',['%4.2f' % w for w in plant.root.actual_distribution][:10]
            #print time.year,time.month,time.day, 'Flux: ', ['%4.2f' % f for f in c.flux][:10]
            #print time.year,time.month,time.day, 'pF         : ', ['%4.2f' % pF for pF in c.pF][:10]
            #print time.year,time.month,time.day, 'Matrix potential: ', ['%4.2f' % m for m in c.matrix_potential][:10]
            #print time.year,time.month,time.day,'Pressurehead:', ['%4.2f' % plant.soil.get_pressurehead(l.center) for l in plant.root.zone][:10]
            #print time.year,time.month,time.day,'Penetration: ', ['%4.2f' % l.penetration for l in plant.root.zone][:10]
            #print time.year,time.month,time.day,'Alpha      : ', ['%4.2f' % a for a in plant.water.Alpha][:10]
            #print time.year,time.month,time.day,'FGI        : ', ['%4.2f' % f for f in plant.root.fgi][:10], '%4.2f' % sum(plant.root.fgi)
            #print time.year,time.month,time.day,'Branchning : ', ['%4.2f' % b for b in plant.root.branching][:10],'%4.2f' % sum(plant.root.branching), '%4.2f' % plant.root.Wtot,plant.root.growth
            
            print ('Rain %4.2f, ETc %4.2f, DP %4.2f, Dr %4.2f') % (c.cell.rain(time),plant.et.Cropspecific,max(c.cell.rain(time)-plant.et.Cropspecific,0),swc.Dr)
            
        else:
            print time.year,time.month,time.day



        
        flux = [uptake*-1. for uptake in plant.water.Uptake] if FlowerPower.Plant.Count >0 else [0]*21
        c.flux=flux
        c.run(cmf.day)
        
        
        res[0].append(c.Kr())
        res[1].append(swc.Kr)
        res[2].append(swc.Dr)
        res[3].append(c.cell.rain(time))
        res[4].append(sum(res[3])+plant.et.Evaporation if FlowerPower.Plant.Count >0 else 0)
        res[5].append(sum(res[3]))
        res[6].append(sum(res[4]))
        
if __name__=='__main__':
    #Create cmf cell
    c = cmf1d(sand=20,silt=0,clay=10,c_org=2.0,bedrock_K=0.01,layercount=20,layerthickness=0.1)
    c.cell.saturated_depth=5
    
    #Simple water balance model
    swc = FlowerPower.SWC()
    
    #Load meteological data
    load_meteo(c.project,stationname='Giessen')
    
    #Crop parameter
    SummerWheat = getCropSpecificParameter('SummerWheat')
    
    #set management
    sowingdate = [date2num(d) for d in [datetime(1980,3,1),datetime(1981,3,1),datetime(1982,3,1),
                 datetime(1983,3,1),datetime(1984,3,1)]]
    harvestdate = [date2num(d) for d in [datetime(1980,8,1),datetime(1981,8,30),datetime(1982,8,30),
                  datetime(1983,8,30),datetime(1984,8,30)]]
    
    #Simulation period
    start = datetime(1980,1,1)
    end = datetime(1980,12,31)
    
    #timestep = daily
    step = timedelta(1)
   
    #List for results
    res = [[],[],[],[],[],[],[]]
    print res
    #run simulation
    timer = datetime.now()
    run(start,end,step)
    print datetime.now() - timer
    
    
    timeline = drange(start,end,step)
    subplot(211)
    plot_date(timeline,res[0],fmt='r-',label='cmf_Kr')
    plot_date(timeline,res[1],fmt='b-',label='swc_Kr')
    plot_date(timeline,res[2],fmt='g-',label='swc_Dr')
    ylim(0,20)
    legend(loc=0)
    subplot(212)
    plot_date(timeline,res[5],fmt='b-',label='Rain')
    plot_date(timeline,res[6],fmt='g-',label='ETc')
    legend(loc=0)
    
    show()
    