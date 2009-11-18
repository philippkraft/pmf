# -*- coding: utf-8 -*-
import pylab as pylab
class Development:
    """
    Calculates the developmentstage of plant with the thermaltime concept.
    
    Development is an implementation of the plant interface
    development with the required functions.

    Implementation
    ==============
    A development instance must be hand over to plant for the 
    implementation of plant. Development for itsel must be
    implemented with the crop specific developmentstages and the
    related total thermaltime for each dtage.
    
    Call signature
    ==============
    Call development calculates thermaltime.
    """
    def __init__(self,stage):
        """
        Returns a development instance.
        
        Development is defined throug the stage parameter. 
        this parameter holds a list with the name of each
        stage and the related total thermaltime. The total
        values are the thresholds for changing the stage.
        The total thermaltime values of the stages are 
        constant values. Variation of the amount of time,
        which is required to reach the next stage, is only
        possibl through the variation of the daily calculated
        degree days.
        
        @type stage: list
        @param stage: List with names and total thermaltime requirement for each stage in [degreedays].
                      Example: [['Emergence',160.],['Leaf development',208.],...]
        @rtype: development
        @return: Development instance        
        """
        #List with all names and thermaltime thresholds of each stage
        self.stages=[]
        #State vairbles updated in every timestep
        self.tt=0.
        for s in stage:
            self.__setitem__(s)
    @property
    def StageIndex(self):
        """
        Returns the index of the actual development stage in the stage attribute of the development class
        
        @rtype: interger
        @return: Index of the actual development stage
        """
        return self.stages.index(self.Stage)
    @property
    def IsGrowingseason(self):
        """
        Returns True during growingseason.
        
        @rtype: boolean
        @return: True during growingseason.
        """
        return True if self.tt>=self.stages[0][1] and self.tt< self.stages[-1][1] else False
    @property
    def IsGerminated(self):
        """
        Return True, if germination is complete.
        
        @rtype: boolean
        @return: True, if germmination is complete.
        """
        return True if self.tt > self.stages[0][1] else False
    @property
    def Thermaltime(self):
        """
        Return actual thermaltime
        
        @rtype: double
        @return: Thermaltime in [degreedays].
        """
        return self.tt
    @property
    def Stage(self):
        """
        Returns the name of the actual development stage
        
        If development is finished, the function returns 'Development finished'
        
        @rtype: String
        @return: Actual developmentstage.
        """
        return filter(lambda i:i[1]>=self.tt, self.stages)[0] if self.tt<=self.stages[-1][1] else 'Development finished'
    def __setitem__(self,stage):
        self.stages.append(stage)
    def __getitem__(self,index):
        return self.stages[index]
    def __iter__(self):
        for s in self.stages:
            yield s
    def __call__(self,step,tmin,tmax,tbase):
        """
        Calcultes thermaltime.
        
        @type step: double
        @param step: Time step of the actual model period in [days or hours].
        @type tmin: double
        @param tmin: Daily minimum temperature in [Celsius].
        @type tmax: double
        @param tmax: Daily maximum temperature in [Celsius].
        @type tbase: double 
        @param tbase: Crop specific base temperature over which development can occur in [Celsius].
        """
        self.tt = self.tt + self.develop(tmin, tmax, tbase) * step
    def develop(self,tmin,tmax,tbase):
        """
        Returns thermaltime rate for given temperature and crop specific base temperature.
        
        If tmax or min smaller than tbase, the rate is defined to be zero.
        Else the rate is computed as (tmax+tmin/2 - tbase).
        
        @type tmin: double
        @param tmin: Daily minimum temperature in [Celsius].
        @type tmax: double
        @param tmax: Daily maximum temperature in [Celsius].
        @type tbase: double 
        @param tbase: Crop specific base temperature over which development can occur in [Celsius].
        @rtype: double
        @return: Thermaltime rate in [degreedays].
         
        @see: [Bonhomme, 2000, McMaster & Wilhelm, 1997] 
        """
        if tmax < tbase or tmin < tbase:
            return 0
        else:
            return ((tmax+tmin)/2.0-tbase)
class SoilLayer:
    """
    SoilLayer is the framework for the rootingzone and holds the geometrica attributes.
    
    Soillayer holds values for the geometrical descritpion
    of the rootingzone. It is devided into layers which can
    be penetrated from the plant root. 
    
    
    Soillayer holds values which describe the constantant
    
    Development is an implementation of the plant interface
    development with the required functions.

    Implementation
    ==============
    Soillayer is implemented without values. With the
    function get_rootingzone() a rootingzone can be created.
    
    Call signature
    ==============
    Call Soillayer calculates the actual rootingzone, depending
    on the pentration depth of the plant root.For that
    the root penetration for each layer is calculated.
    """
    def __init__(self,lower=0.,upper=0.,center=0.,thickness=0.,penetration=0.,soilprofile=[]):
        """
        Returns a soillayer instance with zero values for all attributes.
        
        To create a rootingzone get_rootingzone() must be called.
        
        @type lower: double
        @param lower: Lower limit of the soil layer relative to ground surface level in [cm].
        @type upper: double
        @param upper: Upper limit of the soil layer relative to ground surface level in [cm].
        @type center: double
        @param center: Center of the soil layer relative to ground surface level in [cm].
        @type thickness: double
        @param thickness: Thickness of the layer in [cm].
        @type penetration: double 
        @param penetration: Root penetrated fraction of the layer in [cm].
        @rtype: soillayer
        @return: soillayer instance
        """
        #Constant variables
        #Geometrical detail of the layer
        self.lower=lower
        self.upper=upper
        self.center=center
        self.thickness=thickness
        
        
        #List with all layers in the soilprofile, which is created with get_rootingzone()
        self.rootingzone=[]
        
        self.get_rootingzone(soilprofile)
        
        #State variables updated in every timestep
        self.penetration=penetration
    def __getitem__(self,index):
        return self.rootingzone[index]
    def __iter__(self):
        for horizon in self.rootingzone:
            yield horizon
    def __len__(self):
        return len(self.rootingzone)
    def get_rootingzone(self,soilprofile):
        """ Returns a rootingzone with the geomertical details of each layer.
        
        @type soilprofile: list
        @param soilprofile: List with the lower limits of the layers in the soilprofile in [cm].
        @rtype: soilprofile
        @return: Soilprofile which defines the actual rootingzone.
        """
        #Create soillayer for each layer in soilprofile
        for i,layer in enumerate(soilprofile):
            #Each layer is a soillayer instance
            self.rootingzone.append(SoilLayer())
            #set lower limit
            self.rootingzone[i].lower=layer
            #first layer upper limit = 0.
            if i == 0: 
                self.rootingzone[i].upper = 0.
            #all other layers upper limit = lower limit of the above layer
            else: 
                self.rootingzone[i].upper = (soilprofile[i-1])
            #Center and thickness of each layer
            self.rootingzone[i].center = (self.rootingzone[i].lower + self.rootingzone[i].upper) / 2.
            self.rootingzone[i].thickness = self.rootingzone[i].lower - self.rootingzone[i].upper
    def __call__(self,Zr):
        """
        Calculates the pentration depth for each soillayer in the rootingzone.
        
        @type Zr: double
        @param: Rootingdepth in [cm].
        @return: -
        """
        #For each layer in rootingzone
        for layer in self.rootingzone:
            #If lower limit <= rootingdepth, the soillayer is full penetrated
            if layer.lower <= Zr:
                layer.penetration = layer.thickness
            #If upperlimit above rootingdepth, layer is not penetrated
            elif layer.upper>Zr:
                layer_penetration = 0.
            #If only a part from the layer is penetrated, the value is rootingdepth minus upperlimit
            else: 
                layer.penetration = Zr - layer.upper
class ET_FAO:
    """
    Calculates crop specific Evapotranspiration and correponds with the plant inferface evaporation.
    
    ET_FAO calculates the crop specific Evapotranspiration.
    This concept based on the Penmnan-Monteith equation. 
    Reference Evapotranspiration (ETo) is ajdusted with crop 
    specific values. The resulting crop specific Evapotranspiration (ETc)
    is divided into a transpiration and a evaporation component.
    All equations and concepts implenented in this class are taken from
    "Crop evapotranspiration - Guidelines for computing crop water requirements - FAO Irrigation and drainage paper 56"
    except for the calculation of the fieldcover. In this case the calculation
    based on the leaf area index and not on the FAO-concept.
    All coefficiants used in this approach can be recieved from
    these guidelines.
       
    
    Implementation
    ==============
    ET_FAO must be implemented with the crop specif parameter.
    These parameter are related to the development of the plant.
    For the discritpion of influences of the development the development
    of the plant is divided into four seasons. This arrangement
    can be taken form the plant development class. For the calculation
    of the transpiration crop specific transpiration coefficiants for 
    each season are required, which can be received from th FAO-guidelines.
    
    Call signature
    ==============
    ET_FAO msut be called with crop specific values discribing vegetation
    strucute and development and the actual wheather conditions. For the calculation
    of the evaporation the calculation of a daily oil water balance is needed. For
    that the FAO water balance model can be used. These model is 
    implemented in the class SWC - SoilWaterContainer. It is possible
    to use other water balance models, if they match the interface requirements.    
    
     @see: [Allen et al, 1998]
    """
    def __init__(self,kcb_values,seasons, kcmin = 0.15):
        """
        Returns a ET_FAO instance.
        
        @type seasons: list
        @param seasons: List with the length of the four development seasons in [degreedays].
        @type kcb_values: list
        @param kcb_values: List with basal crop coefficiants for each season in seasons parameter in [-].
        @type Kcmin: double
        @param Kcmin: Minimum Kc for dry bare soil with no ground cover [0.15 - 0.20] in [-].
        
        @rtype: ET_FAO
        @return: ET_FAO instance
        
        @todo: Calculation of seasons!!!
        """
        #Constant variables
        self.kcb_values=kcb_values
        self.seasons=seasons
        self.kcmin = kcmin
        #State vairables
        self.eto=0.
        self.kcb=0.
        self.ke=0.
        self.fw=1.
        self.fc=0.
    @property
    def transpiration(self):
        """
        Returns transpiration
        
        @rtype: double
        @return: transpiration in [mm].
        """
        return self.eto * self.kcb
    @property
    def evaporation(self):
        """
        Returns evaporation
        
        @rtype: double
        @return: evaporation in [mm].
        """
        return self.eto * self.ke
    @property
    def Reference(self):
        """
        Returns reference Evapotranspiration.
        
        @rtype: double
        @return: Reference Evapotranspiration in [mm].
        """
        return self.eto
    @property
    def Cropspecific(self):
        """
        Returns Cropspecific Evapotranspiration.
        
        @rtype: double
        @return: Cropspecific Evapotranspiration in [mm].
        """
        return self.eto * (self.kcb+self.ke)
    @property
    def Adjusted(self):
        """
        Returns Adjusted cropspecific Evapotranspiration to water stress.
        
        @rtype: double
        @return: Adjusted cropspecific Evapotranspiration to water stress in [mm].
        """
        return self.eto * (self.kcb*self.ks+self.ke)
    def __call__(self,Kr,thermaltime,Rn,T,e_s,e_a,windspeed,LAI,alt=0.,RHmin=30.,h=1.):
        """
        Calculates reference Evapotranspiration and the crop specific adjustment factors Kcb and Ke.
        
        The user cann call the transpiration coefficiants wit hthe corresonding properties of the class.
        
        @type Kr: double 
        @param Kr: evaporation reduction coefficient dependent on the soil water depletion from the topsoil layer in [-].
        @type thermaltime: double
        @param thermaltime: Thermaltime in [degreedays].
        @type Rn: double
        @param Rn: Net radiation at the crop surface in [MJ m-2].
        @type T: double
        @param T: Mean daily air temperature at 2 m height in  [Celsius].
        @type e_s: double
        @param e_s: Saturation vapour pressure in [kPa].
        @type e_a: double
        @type e_a: Actual vapour pressure [kPa].
        @type windspeed: double
        @param windspedd: Wind speed at 2 m height [m s-1].
        @type vegH: double
        @param vegH: Vegetation height in [m].
        @type LAI: double
        @param LAI: Leaf are index in [m2 m-2].
        @type stomatal_resistance: double
        @param stomatal_resistance: Stomatal ristance in [s m-1].
        @type RHmin: double
        @param RHmin: Mean value for daily minimum relative humidity during the mid- or late season growth stage in [percent].
        @type h: double
        @param h: mean maximum plant height during the period of calculation (initial, development, mid-season, or late-season) in [m].
        
        @todo: Calculation of altitude.
        """
        #Calculates reference Evapotranspiration
        self.eto = self.calc_ETo(Rn,T,e_s,e_a,windspeed)
        
        #Calculates basal crop coefficaint for thhe transpiration calculation
        self.kcb = self.calc_Kcb(thermaltime, self.kcb_values[0], self.kcb_values[1],
                                 self.kcb_values[2], self.seasons[0], self.seasons[1], 
                                 self.seasons[2], self.seasons[3])
        
        #Calculates upper limit on the evaporation and transpiration from any cropped surface
        kcmax = self.calc_Kcmax(self.kcb, h, windspeed, RHmin)
        
        #Calcultes fieldcover afte FAO and exposed and wetted soil fraction
        self.fc = self.fc_from_LAI(LAI,fullcover = 3.)#self.calc_fc_dynamic(self.kcb, kcmax, vegH,self.kcmin)
        few = self.calc_few(self.fc, self.fw)
        
        #Calculates evaporation coefficiant
        self.ke = self.calc_Ke(Kr, kcmax, self.kcb, few)
        return self.eto * self.kcb
    def calc_ETo(self,Rn,T,e_s,e_a,windspeed=2.,LAI=24*0.12,stomatal_resistanc=100,alt=0,printSteps=0,vegH=0.12,daily=True):
        """
        Calculates the reference Evapotranspiration.
        
        The reference surface is a hypothetical grass reference crop with an 
        assumed crop height of 0.12 m, a fixed surface resistance of 70 s m-1 
        and an albedo of 0.23. The reference surface closely resembles an 
        extensive surface of green, well-watered grass of uniform height, 
        actively growing and completely shading the ground. The fixed surface 
        resistance of 70 s m-1 implies a moderately dry soil surface resulting 
        from about a weekly irrigation frequency. 
        
        @type Rn: double
        @param Rn: Net radiation at the crop surface in [MJ m-2].
        @type T: double
        @param T: Mean daily air temperature at 2 m height in  [Celsius].
        @type e_s: double
        @param e_s: Saturation vapour pressure in [kPa].
        @type e_a: double
        @type e_a: Actual vapour pressure [kPa].
        @type windspeed: double
        @param windspedd: Wind speed at 2 m height [m s-1].
        @type vegH: double
        @param vegH: Vegetation height in [m].
        @type LAI: double
        @param LAI: Leaf are index in [m2 m-2].
        @type stomatal_resistance: double
        @param stomatal_resistance: Stomatal ristance in [s m-1].
        @type alt: double
        @param alt: Geographical altitude in [decimal degrees].
        @rtype: double
        @return: Reference evapotranspiration in [mm].
        
        @todo: defintion of altitude
        """
        delta=4098*(0.6108*pylab.exp(17.27*T/(T+237.3)))/(T+237.3)**2
        if daily:   G=0
        else : G=(0.5-pylab.greater(Rn,0)*0.4)*Rn
        P=101.3*((293-0.0065*alt)/293)**5.253
        c_p=0.001013
        epsilon=0.622
        lat_heat=2.45
        gamma=c_p*P/(lat_heat*epsilon)
        R=0.287
        rho_a=P/(1.01*(T+273)*R)
        d=0.6666667*vegH
        z_om=0.123*vegH
        z_oh=0.1*z_om
        k=0.41
        r_a_u= pylab.log((2-d)/z_om)*pylab.log((2-d)/z_oh)/k**2
        r_a=r_a_u/windspeed
        r_s=100./(0.5*LAI) # LAIactive = LAI * 0.5
        nominator=(delta+gamma*(1+r_s/r_a))
        ATcoeff=epsilon*3.486*86400/r_a_u/1.01
        #AeroTerm=(rho_a*c_p*(e_s-e_a)/r_a)/nominator
        AeroTerm=gamma/nominator*ATcoeff/(T+273)*windspeed*(e_s-e_a)
        RadTerm=(delta*(Rn-G))/(nominator*lat_heat)
        if printSteps:
           print "ET= %0.2f,AT= %0.2f,RT=   %0.2f" % (AeroTerm+RadTerm,AeroTerm,RadTerm)
           print "Rn= %0.2f,G=  %0.2f,Dlt=  %0.2f" % (Rn,G,delta)
           gamma_star=gamma*(1+r_s/r_a)
           print "gamma*=%0.2f,dl/(dl+gm*)=%0.2f,gm/(dl+gm*)=%0.2f" % (gamma_star,delta/(delta+gamma_star),gamma/(delta+gamma_star))
           print "r_a=%0.2f,r_s=%0.2f,gamma=%0.2f" % (r_a,r_s,gamma)
           print "rho_a=%0.2f,c_p=%0.2f" % (rho_a,c_p)
           print "P=  %0.2f,e_a=%0.2f,e_s=  %0.2f" % (P,e_a,e_s)
        return AeroTerm+RadTerm
    def calc_ETc(self,ETo,Kcb,Ke):
        """ 
        Calculates crop specific Evapotranspiration.
        
        @type ETo: double
        @param ETo: Reference Evapotranspiration in [mm].
        @type Kcb: double
        @param Kcb: Basal crop coefficient (Kcb) in [-].
        @type Ke: double
        @type Ke: evaporation coefficiant in [-].
        @rtype: double
        @return: Crop specific evapotranspiration in [mm].
        """
        return ETo * (Kcb+Ke)
    def adjust_Kcb(self,Kcb_tab,windspeed,RHmin,h):
        """ 
        Adjust basal crio coefficiant (Kcb) to environmental conditions.
        
        @type Kcb_tab: double
        @param Kcb_tab: Constant basal crop coefficient (Kcb) related to the development season in [-].
        @type windspeed: double
        @param windspedd: Wind speed at 2 m height [m s-1].
        @type RHmin: double
        @param RHmin: Mean value for daily minimum relative humidity during the mid- or late season growth stage in [percent].
        @type h: double
        @param h: mean maximum plant height during the period of calculation (initial, development, mid-season, or late-season) in [m].
        @rtype: double
        @return: Kcb adjusted with windspeed, plant height and relative humidity in [-].
        """
        return Kcb_tab + (0.04*(windspeed-2.)-0.004*(RHmin-45))*(h/3.)**0.3
    def calc_Kcb(self,time,Kcb_ini,Kcb_mid,Kcb_end,Lini,Ldev,Lmid,Llate):
        """ 
        Constructed basal crop coefficient (Kcb) curve. 
            
        @type time: double 
        @param time: Day is the actual day or thermaltime in [days] or [degreedays]. 
        @type Kcb_ini: double 
        @param Kcb_ini: Kcb for initial season  
        @type Kcb_mid: double 
        @param Kcb_mid: Kcb for mid season 
        @type Kcb_end: double 
        @param Kcb_end: Kcb for late season   
        @type Lini: double 
        @param Lini: Length of initial season  
        @type Ldev: double 
        @param Ldev: ength of crop development season  
        @type Lmid: double 
        @param Lmid: Length of mid season
        @type Llate: double 
        @param Llate: Length of late season     
        @rtype: double
        @return: Kbc depending on the actual time in [-].
        """
        if time <=Lini: return Kcb_ini
        elif time <=Lini+Ldev: return Kcb_ini+(time-Lini)/Ldev*(Kcb_mid-Kcb_ini)
        elif time <=Lini+Ldev+Lmid: return Kcb_mid
        elif time <= Lini+Ldev+Lmid+Llate: return Kcb_mid+(time-(Lini+Ldev+Lmid))/Llate*(Kcb_end-Kcb_mid)
        else: return Kcb_end
    def calc_Ke(self,Kr,Kcmax,Kcb,few):
        """
        Calculates evaporation coefficiant.
        
        @type Kr: double
        @param Kr: evaporation reduction coefficient dependent on the cumulative depth of water depleted (evaporated) from the topsoil.
        @type Kcmax: double
        @param Kcmax: Maximum value of Kc following rain or irrigation in [-].
        @type Kcb: double
        @param Kcb: Basal crop coefficient in [mm].
        @type few: double
        @param few: Fraction of the soil that is both exposed and wetted, i.e., the fraction of soil surface from which most evaporation occurs.
        @rtype: double
        @return: evaporation coefficiant in [mm].
        """
        return min(Kr*(Kcmax - Kcb), few*Kcmax,)
    def calc_Kcmax(self,Kcb,h,windspeed,RHmin):
        """ 
        Calcualtes maximum value of Kc following rain or irrigation.
        
        @type Kcb: double
        @param Kcb: Basal crop coefficient in [mm].
        @type windspeed: double
        @param windspedd: Wind speed at 2 m height [m s-1].
        @type RHmin: double
        @param RHmin: Mean value for daily minimum relative humidity during the mid- or late season growth stage in [percent].
        @type h: double
        @param h: mean maximum plant height during the period of calculation (initial, development, mid-season, or late-season) in [m].
        @rtype: double
        @return: Maximum value of Kc following rain or irrigation in [-].
        """
        return max((1.2 + (0.04*(windspeed-2.)-0.004*(RHmin-45))*(h/3.)**0.3),Kcb+0.05)
    def calc_TEW(self,qFC,qWP,Ze):
        """
        Calculates total evaporable water.
        
        TEW total evaporable water = maximum depth of water 
        that can be evaporated from the soil when the topsoil
        has been initially completely wetted.
        
        
        @type qFC: double
        @param qFC: Soil water content at field capacity in [m3 m-3].
        @type qWP: double
        @param qWP: Soil water content at wilting point in [m3 m-3].
        @type Ze: double
        @param Ze: Depth [0.10-0.15m] of the surface soil layer that is subject to drying by way of evaporation in [m].
        @rtype: double
        @return: Total evaporable water in [mm].
        """
        return 1000(qFC-0.5*qWP)*Ze
    def calc_Kr(self,De,TEW,REW):
        """
        Calcualtes vaporation reduction coefficient
        
        Kr is the dimensionless evaporation reduction coefficient dependent on the soil 
        water depletion (cumulative depth of evaporation) from the topsoil layer.
        
        @type De: double
        @param De:  Cumulative depth of evaporation (depletion) from the soil surface layer at the end of the previos day in [mm].
        @type TEW: double
        @param TEW: Total evaporable water in [mm] 
        @type param: double
        @param param: cumulative depth of evaporation (depletion) at the end of stage 1 (REW = readily evaporable water)in [mm].
        @rtype: double
        @return: Dimensionless evaporation reduction coefficient in [-].
        """
        if De > REW:
            return (TEW-De)/(TEW-REW)
        else:
            return 1.
    def calc_few(self,fc,fw=1.):#fw=1. - precipitation
        """
        Calculates fraction of the soil that is both exposed and wetted.
        
        fc and fw: [0.01 - 1], for precipitation fw = 1.0
        
        @type fc: double
        @param gc: Effective fraction of soil surface covered by vegetation in [-].
        @type fw: double
        @param fw: Average fraction of soil surface wetted by irrigation or precipitation in [-].
        @rtype: double
        @return: Fraction of the soil that is both exposed and wetted in [-].
        """
        return min(1-fc,fw)
    def calc_fc_dynamic(self,Kcb,Kcmax,h,Kcmin):#
        """ 
        Dynamic calculates effective fraction of soil surface covered by vegetation.
        
        This equation should be used with caution and validated from field observations.
        
        Kcmin=0.15 - annual crops under nearly bare soil condition
        
        @type Kcb: double
        @param Kcb: Basal crop coefficient in [mm].
        @type Kcmax: double
        @param Kcmax: Maximum value of Kc following rain or irrigation in [-].
        @type h: double
        @param h: mean maximum plant height during the period of calculation (initial, development, mid-season, or late-season) in [m].
        @type Kcmin: double
        @param Kcmin: Minimum Kc for dry bare soil with no ground cover [0.15 - 0.20] in [-].
        @rtype: double
        @return: Effective fraction of soil surface covered by vegetation in [-].
        """
        return ((Kcb-Kcmin)/(Kcmax-Kcmin))**(1+0.5*h) 
    def calc_fc_static(self,thermaltime,seasons):
        """
        Calculates effective fraction of soil surface covered by vegetation.
        
        
        The value for fc is limited to < 0.99. The user should assume appropriate values
        for the various growth stages. 
        Typical values for fc :
        Season    fc
        1        0.0-0.1
        2        0.1-0.8
        3        0.8-1.
        4        0.2-0.8
        
        @type thermaltime: double
        @param thermaltime: Thermaltime in [degreedays].
        @type seasons: list
        @param seasons: List with the length of the four development seasons in [degreedays].
        @rtype: double
        @return: Effective fraction of soil surface covered by vegetation in [-].
        """
        if thermaltime <= seasons[0]: return 0.1 
        elif thermaltime <= seasons[0]+seasons[1]: return 0.8#
        elif thermaltime <= seasons[0]+seasons[1]+seasons[2]:return 1.
        else: return 0.8
    def fc_from_LAI(self,LAI,fullcover = 3.):
        """
        Returns fieldcover calculated from LAI.
        
        LAI 3.0 can be assumed as maximum fieldcover.
        For LAI > 3.0 fc equals one, for values under 3.0
        fc is computed as fraction from full cover.
        
        @type LAI: double
        @param LAI: Leaf area index in [m2 m-2].
        @type fullcover: double
        @param fullcover: LAI which leads to full fieldcover in [m2 m-2].
        
        @rtype: double
        @return: Effective fraction of soil surface covered by vegetation in [-].
        """ 
        return min(LAI / fullcover,1.)
class Water_FAO:
    """
    Simple water uptake model which computes water uptake under stressed condtionins.
    
    The model calculates plant water uptake under water stress
    conditon. Plant water demand equals the potential transpiration.
    If the soil cannot satisfy these demand, stress occurs and 
    the potential transpiration is reduced to the actual water uptake.
    The reduction facro through water stress is computed in realtion
    to "Crop evapotranspiration - Guidelines for computing crop 
    water requirements - FAO Irrigation and drainage paper 56".
    All equations and concepts implenented in this class are taken 
    from these approach.
    
    Implementation
    ==============
    WAter_FAO must be implemented wit ha crop specific stress
    coefficiant, which can be taken from the guidelines.
    
    Call signature
    ==============
    Water_FAO calculates the wateruptake under stressed pr no stressed
    conditions for a given soilprofile or rootingzone.
    
    @see: [Allen et al, 1998]
    """
    def __init__(self,waterbalance=None,plant=None,average_available_soilwater=0.5):
        """
        Returns a Water_FAO instance.
        
        @type average_available_soilwater: double
        @param average_available_soilwater:  fraction of TAW that a crop can extract from the root zone without suffering water stress in [-].
        @rtype: water_fao
        @return: WAter_FAO instance
        """
        self.waterbalance=waterbalance
        self.plant=plant
        
        #Constant variables
        self.p = average_available_soilwater
        #State variables
        self.ks=[]
        self.uptake = 0.
    def __call__(self,rootzone):
        """
        Calculates actual water uptake and contributes the uptake over the layer in the soil profile.
        
        @type rootzone: list
        @param rootzone: List with centre depth of each layer in  [cm].
        @rtype: list
        @return: Stress values for each layer in rootzone in [-].
        """
        RAW = soilvalues[0] * self.p
        return [self.calc_Ks(self.waterbalance.TAW, self.waterbalance.Dr, RAW, self.p) for z in rootzone]
    def calc_Ks(self,TAW,Dr,RAW,p):
        """ 
        Calculates transpiration reduction factor
        
        Water content in me root zone can also be expressed by root zone depletion,
        Dr, i.e., water shortage relative to field capacity. At field capacity, the root 
        zone depletion is zero (Dr = 0). When soil water is extracted by evapotranspiration, 
        the depletion increases and stress will be induced when Dr becomes equal to RAW. After 
        the root zone depletion exceeds RAW (the water content drops below the threshold q t), 
        the root zone depletion is high enough to limit evapotranspiration to less than potential 
        values and the crop evapotranspiration begins to decrease in proportion to the amount of 
        water remaining in the root zone.
        
        @type TAW: double
        @param TAW: Total available soil water in the root zone in [mm].
        @type Dr: double
        @param Dr: Root zone depletion in [mm].
        @type RAW: double
        @param RAW: Readily available soil water in the root zone in [mm].
        @type p: double
        @param p: Fraction of TAW that a crop can extract from the root zone without suffering water stress in [-].
        @rtype: double
        @return: transpiration reduction factor dependent on available soil water in [-].
        
        When the root zone depletion is smaller than RAW, Ks = 1
        """
        return (TAW-Dr)/((1-p)*TAW) if Dr > RAW else 1.
    def adjust_p(self,p_table,ETc):
        """ 
        Adjust extractable soil water without stress.
        
        p is Fraction of TAW that a crop can extract from the root zone without 
        suffering water stress. The values for p apply for ETc 5 mm/day can be 
        adjusted with the daily ETc. 
    
        @type p_table: double
        @param p_table: Fraction of TAW that a crop can extract from the root zone without suffering water stress in [-].
        @type ETc: double
        @param ETc: Crop specific evapotranspiration in [mm].
        @rtype: double
        @return: Adjusted extractable soil water in [-].
        """
        return p_table + 0.04*(5-ETc)
class Water_Feddes:
    """
    Water uptake model based on soil matrixpotential and a crop specific uptake function.
    
    The water uptake is limited througt a sink therm variable alpha.
    This value vary with the water pressure head in the soil layer. 
    Alpha is a dimensonless factor between zero and one. The factor 
    limits water uptake due to the wilting point and oxygen dificiency.
    Alpha is determinded with four threshold values for the pressure head
    (h1-oxygen deficiency,h-4 wiliting point, h2 and h3 -optimal conditons). 
    Values for the parameters vary with the crop.  
    
    Water stress in a soil layer can bee compensated from other soil layer.
    This compensation is a empirical distribution from stressed soil layer
    in less stressed soil layers. Compensation is limited to the actual 
    uptake multiplied with the maxcomp parameter. Maxcomp is a user value.
    
    
    Implementation
    ==============
    Water_Feddes must be implementeed with the maxcom parameter,
    which is defined from the user.
    
    Call signature
    ==============
    Water_feddes calculates the water uptake under stress conditions
    and calculates the compensation therm.    
    
    @see: [Feddes et al, 1978, Feddes & Raats 2004]
    """
    def __init__(self,waterbalance=None,plant=None,maxcomp=2.,layercount=41):
        """
        Returns a Water_Feddes instance.
        
        @type maxcomp: double
        @param maxcomp: Maximal compensation capacity factor in [-].
        @type layercount: double
        @param layercount: Count of the layer in the soil profile.
        
        @rtype: water_feddes
        @return: Water_Feddes instance
        """
        self.waterbalance=waterbalance
        self.plant=plant
        self.layercount=layercount
        #Constant variables
        self.max_compensation_capacity=maxcomp
        #State variables
        self.Sh=[0. for l in range(self.layercount)]
        self.alpha=[0. for l in range(self.layercount)]
        self.compensation=[0. for l in range(self.layercount)]
        self.Shcomp=[0. for l in range(self.layercount)]
    def __call__(self,rootzone):
        """
        Calulates water uptake under stressed conditions and compensation.
        
       
        @type rootzone: list
        @param rootzone: List with centre depth of each layer in  [cm].
        @rtype: list
        @return: Stress values for each layer in rootzone in [-].
        """
        return [self.sink_term(self.waterbalance.get_pressurehead(z), self.plant.pressure_threshold)for z in rootzone]
    def compensate(self,Sh,Sp,pressurehead,alpha,maxopth,maxcomp):
        """
        Calculates compensation factors for each layer in the rootingzone.
        
        Compensation capacity = (Actual uptake- Potential uptake) * maxcom
        
        @type s_p: list
        @param s_p: List with the potential water uptake for each soillayer in rootingzone in [mm].
        @type s_h: list
        @param s_h: List with the actual water uptake for each soillayer in rootingzone in [mm].
        @type pressurehead: list
        @param pressurehead: List with the soil pressurehead for each soillayer in rootingzone in [cm].
        @type alpha: list
        @param alpha: Prescribed crop specific function of soil water pressure head with values between or equal zero and one in [-].
        @type maxcomp: double
        @param maxcomp: Maximal compensation capacity factor in [-].
        @type maxopth: double
        @param maxopth: Plant pressure head until water uptake can occur without stress in [cm water column].
        @rtype: list
        @return: List with the compensated uptake in [mm].
        """
        #Remaining alpha of the less stress soil layer
        remaining_alpha= [max(1-(m/maxopth),0.) for i,m in enumerate(pressurehead)] 
        #Remaining uptake capacity of the soillayer
        remaining_uptake=sum(Sp)-sum(Sh)
        #Returns list with the compensation values in mm
        return [min(r/sum(remaining_alpha)*remaining_uptake,maxcomp*Sh[i])for i,r in enumerate(remaining_alpha)]     
    def sink_term(self,h_soil,h_plant): 
        """
        Computes sink term alpha.
        
        The water uptake is limited througt a sink therm variable alpha. 
        This value vary with the water pressure head in the soil layer. 
        Alpha is a dimensonless factor between zero and one. The factor 
        limits water uptake due to the wilting point and oxygen dificiency. 
        After alpha is determinded with four threshold values for the pressure head 
        (h1-oxygen deficiency,h-4 wiliting point, h2 and h3 -optimal conditons). 
        Values for the parameters vary with the crop.  H3 also varies with the 
        transpiration.
        
        @type h_soil: list
        @param h_soil: List with soil pressurehead for each layer in [cm water column].
        @type h_plant: list
        @param h_plant: List with soil pressurehead. These conditions limiting wate uptake in. [cm water column].
        @rtype: list
        @return: Prescribed crop specific function of soil water pressure head with values between or equal zero and one in [-].
        
        @see: [Feddes and Raats, 2004]
        """
        try:
            if h_soil<h_plant[0] or h_soil>h_plant[-1]: return 0
            if h_soil>=h_plant[1] and h_soil<=h_plant[2]: return 1
            elif h_soil<h_plant[1]: return (h_soil-h_plant[0])/(h_plant[1]-h_plant[0])
            else: return (h_plant[-1]-h_soil)/(h_plant[-1]-h_plant[-2])
        except ValueError, err:
            print err
class Biomass_LOG:
    """
    Calculates plant growth based on a logistical growth function.
    
    Growth is simulated with a logistic growth function The amount of biomass 
    in per time step depends on a crop specific growth coefficiant
    multiplied with the total biomass. A capacity limit limits 
    the growth. The growthrate for a timestep is given by the following equation.
    
    Implementation
    ==============
    Biomass_LOG must be implemented with specific values
    for limiting maximal biomass and a growthfactor.
    
    Call signature
    ==============
    Biomass_LOG must be called with the actual time step and stress
    coefficiant.
    
    @see: [J.H.M. Thornley & Johnson 1990]
    """
    def __init__(self,capacitylimit,growthfactor):
        """
        Returns a Biomass_LOG instance.
        
        @type capacitylimit: double
        @param capacitylimit: Maximal plant biomass in [g]. 
        @type growthfactor: double
        @param growthfactor: Growth facor of the plant in [g biomass day-1].
        @rtype: biomass_log
        @return: Biomass_LOG instance
        """
        #Constant variables
        self.capacitylimit=capacitylimit
        self.growthfactor=growthfactor
        #State variables
        self.total=1.
        self.stress=0.
    @property
    def PotentialGrowth(self):
        """
        Return potential growth without stress.
        
        @rtype: double
        @return: Potential growth in [g biomass day-1].
        """ 
        return self.logarithmic_growth(self.total, self.growthfactor, self.capacitylimit)
    @property
    def ActualGrowth(self):
        """
        Return actual growth influenced by water and nitorgen stress.
        
        @rtype: double
        @return: Actual growth in [g biomass day-1].
        """ 
        return self.PotentialGrowth * self.stress
    @property
    def Total(self):
        """
        Return total biomass.
        
        @rtype: double
        @return: Total biomass in [g].
        """ 
        return self.total
    def __call__(self,stress,step):
        """
        Calculats total plant biomass under stressed conditions.
        
        @type stress: double
        @param stress: Parameter for water and nitrogen stress between 0 - 1. in [-].
        @type step: double
        @param step: Time of the actual intervall.
        @return: -
        """
        self.stress=stress
        self.total = self.total + self.logarithmic_growth(self.total, self.growthfactor, self.capacitylimit) * stress * step
    def logarithmic_growth(self,total_biomass,growthfactor,capacitylimit):
        """
        Return growthrate from a logarithmic growht function.
        
        Calculates the growthrare of a logarithmic growth function.
        
        @type total_biomass: double
        @param total_biomass: Total bioamss of the plant in [g].
        @type capacitylimit: double
        @param capacitylimit: Maximal plant biomass in [g]. 
        @type growthfactor: double
        @param growthfactor: Growth facor of the plant in [g biomass day-1].
        @rtype: double
        @return: Growhtrate in [g biomass day-1].
        """
        return total_biomass * growthfactor * (1- total_biomass / capacitylimit)
    def atmosphere_values(self,atmosphere,time_act):
        """
        Biomass_LOG need no atmosphere values.
        """
        pass
class Biomass_LUE:
    """
    Calculates biomass growth with the radiation use efficiency concept.
    
    Calculates the daily biomass gorwht form a crop specific
    radiatiion use efficiency and the daily incoming absorbed
    photosynthetic active radiation (aPAR). aPAR depnds on the
    plant leaf area index and a dimensionless distinction
    coefficiant.
    
    Implementation
    ==============
    Biomass_LUE must be implemented with the crop specific paramters
    for the LUE-concept.
    
    Call signature
    ==============
    Plant must be calles with crop and environmental factors.
    
    """
    def __init__(self,RUE,k):
        """
        Returns a Biomass_LUE instance.
        
        @type RUE: double
        @param RUE: Radiation use efficiency [g m-1 day-1]
        @type k: double
        @param k: Canopy extinction coefficient in [-].
        @rtype: biomass_lue
        @return: Biomass_LUE instance
        """
        #Constant variables
        self.rue=RUE
        self.k=k
        #State variables
        self.total=0.
        self.growthrate=0.
    @property
    def PotentialGrowth(self):
        """
        Return potential growth without stress.
        
        @rtype: double
        @return: Potential growth in [g biomass day-1].
        """ 
        return self.growthrate
    @property
    def ActualGrowth(self):
        """
        Return actual growth influenced by water and nitorgen stress.
        
        @rtype: double
        @return: Actual growth in [g biomass day-1].
        """ 
        return self.growthrate * (1-self.stress)
    @property
    def Total(self):
        """
        Return actual growth influenced by water and nitorgen stress.
        
        @rtype: double
        @return: Actual growth in [g biomass day-1].
        """ 
        return self.total
    def __call__(self,step,stress,Rs,LAI):
        """
        Calcultes the stressed and unstressed growth of the plant.
        
        @type step: double
        @param step: Time step in [ddays
        @type Rs: double
        @param Rs: total solar radiation [MJ m-2 day-1].
        @type stress: double
        @param stress: Parameter for water and nitrogen stress between 0 - 1. in [-].
        @type LAI: double
        @param LAI: Leaf area index of the plant in [m2 m-2].
        @param Rs: total solar radiation [MJ m-2 day-1].
        @type stress: double
        """
        self.stress = stress
        self.growthrate = self.PAR_a(Rs, self.intercept(LAI, self.k))* self.rue
        self.total = self.total + self.growthrate * (1-self.stress) * step
    def PAR_a(self,Rs,interception):
        """ 
        Returns photosynthetically active absorbed radiation
        
        Canopy photosynthesis is closely related to the photosynthetically active 
        (400 to 700 mm) absorbed radiation (PARa) by green tissue in the canopy. 
        The values 0.5 is the fraction of total solar energy, which is photosynthetically 
        active interception - fraction of total solar radiation flux, which is 
        intercepted by the crop. The value 0.9 is the fraction of radiation 
        absorbed by the crop  allowing for a 6 percent albedo and for inactive radiation absorption.
        
        @type Rs: double
        @param Rs: total solar radiation [MJ m-2 day-1].
        @type interception: double
        @param interception: Fraction of total solar radiation flux, which is intercepted by the crop in [-].
        
        
        @rtype: double
        @return: Photosynthetically active absorbed radiation in [MJ m-2 day-1].
        """
        return Rs*0.5*0.9*(1-interception)
    def intercept(self,LAI,k):
        """
        Returns crop interception.
        
        anopy extinction coefficient in wheat crops ranges
        from 0.3 to 0.7 and is highly dependent on leaf angle
        (low K for erect leaves). From equation 3, it can be calculated that
        95 percent PAR interception requires a LAI as high as 7.5 for erect 
        leaves but a LAI of only about 4.0 for more horizontal leaves
        
        @type LAI: double
        @param LAI: Leaf area index of the plant in [m2 m-2].
        @type k: double
        @param k: Canopy extinction coefficient in [-].
        """
        return pylab.exp(-k*LAI)
    def atmosphere_values(self,atmosphere,time_act):
        """
        Returns a method to interfere with the atmosphere interface over the plant instance.
        
        @type atmosphere: atmosphere
        @param atmosphere: Atmosphere object from the plant interface soil.
        @type time_act: datetime
        @param time_act: Actual time in [DD,MM,JJJ].
        @rtype: method
        @return: Function for getting required atmosphere values.
        """
        return atmosphere.get_Rs(time_act)
class Nitrogen:
    """
    Calculates nitrogen uptake from the soil.
    
    The concepts for nitrogen uptake is taken from.The root 
    nitrogen uptake is divided into active and passive uptake. 
    Aktive uptake will occure, if passive uptake cannot satisfy 
    the demand. The passive uptake in each soil layer pa depends 
    on the soil water extraction sh and a maximum allowed solution 
    concetration cmax which can be taken up by plant roots. Low 
    values or zero inhibit passive nitrogen uptake. This can be 
    important for other nutrients which can be taken up only active.
    
    The potential active uptake from each soil layer is calculated with 
    the Michaelis-Menten function. This function descirbes the relationship 
    between influx and its concentration at the root surface. For that, the 
    crop specific Mechaelis Menten Constant Km, the minimum concentration cmin 
    at which can net influx occurr and the soil nitrogen concentration nutrientc  
    is needed
    
    Implementation
    ==============
    Nitrogen msut be impleneted withthe paramter
    for the michaelis menten equation.
    
    Call signature
    ==============
    Must be calles with water uptake, the plant nitrogen demand  
    and the nitrogen concentration in the soil.
    
    @see: [Simunek & Hopmans 2009]
    """
    def __init__(self,Km=0.1,NO3_min=0.,max_passive_uptake=1e300,layercount=41):
        """
        Returns a Biomass_LOG instance.
        
        @type Km: double
        @param Km: Half saturation concentration in umol/l  27. * 14e-6
        @type NO3_min: double
        @param NO3_min: Residual N concentration
        @type layercount: double
        @param layercount: Count of the layer in the soil profile.
        @type max_passive_uptake: double
        @param max_passive_uptake: ...
        
        
        @rtype: nitrogen
        @return: Nitrogen instance
        
        @todo: Define units for all parameters. 
        """
        self.layercount=layercount
        #Constant variables
        self.Km=Km
        self.NO3min=NO3_min
        self.max_passive_uptake=max_passive_uptake
        #State variables
        self.Pa=[0. for l in range(self.layercount)]
        self.Aa=[0. for l in range(self.layercount)]
    @property
    def Active(self):
        """
        Returns active nitrogen uptake.
        
        @rtype: double
        @return: Active nitrogen uptake.
        """
        return self.Aa
    @property
    def Passive(self):
        """
        Returns passive nitrogen uptake.
        
        @rtype: double
        @return: Passive nitrogen uptake.
        """
        return self.Pa
    @property
    def Total(self):
        """
        Returns total nitrogen uptake.
        
        @rtype: double
        @return: Total nitrogen uptake.
        """
        return [pa + self.Aa[i] for i,pa in enumerate(self.Pa)]
    def __call__(self,NO3_conc,Sh,Rp,root_fraction):
        """
        Calculates active and passive nitrogen uptake
        
        @type NO3_conc: list
        @param NO3_conc: NO3 concnetrations in rootzone.
        @type Sh: list
        @param Sh: Plant water uptake from the rootzone in [mm].
        @type Rp: list
        @param Rp: Potential nutrient demand of the plant in [g].
        @type root_fraction: list
        @param root_fraction: Root biomass fraction form whole biomass for each layer in the soil profile in [-].
        @todo: Check Passive uptake
        @return: -
        """
        
        #Passive uptake
        self.Pa = [max(0,w*min(NO3_conc[i],self.max_passive_uptake)) for i,w in enumerate(Sh)]
        #Residual demand
        Ap = max(Rp-sum(self.Pa),0.)
        #Michelis-menten values for each layer
        michaelis_menten = [(NO3-self.NO3min)/(self.Km+NO3-self.NO3min) if NO3>self.NO3min else 0.0 for NO3 in NO3_conc]
        #Active uptake
        self.Aa = [Ap * michaelis_menten[i] * fraction for i,fraction in enumerate(root_fraction)]
        if min(self.Pa)<0 or min(self.Aa)<0:
            a=2
