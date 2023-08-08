import time
import pymel.core as pm
import maya.cmds as cmds
import math

class getData:
    '''
    TODO write doc
    '''

    def __init__(self, object = None):
        self.obj = object
    
    def get_skinCluster(self):
        pyObj = pm.PyNode(self.obj)
        try:
            self.skn = pm.ls(pm.listHistory(pyObj),typ = 'skinCluster')[0]
            return self.skn

        except:
            return None
            
    def get_influnced_joints(self,skin_node = None):

        try:
            self.influences = pm.skinCluster(skin_node, inf = True, q = True)
            return self.influences

        except:
            #pm.error('No skinCluster found!')
            pass
        
    def solvVert(self,vertcnt):
        
        totalCounts = []
        
        for vert in vertcnt:
            
            split01 = vert.split("[")
            split02 = split01[-1].split("]")
    
            start = int(split02[0])
            
            totalCounts.append(str(start))
                
        return (totalCounts)
        


class deformerConvert(getData):
    '''
    TODO write doc
    '''

    def __init__(self, deformer = None, mesh = None):
        getData.__init__(self)
        self.deformer = deformer
        self.mesh = mesh
        self.hold_joint = None
        self.meshCluster = None
        self.inf_jnts = getData().get_influnced_joints(self.deformer)


    def deformer_skin_convert(self):
        '''
        TODO write doc
        '''
        #get mesh skin cluster
        self.meshCluster = getData(object = self.mesh).get_skinCluster()
        

        #check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh+"_New_Jnt") == False:
                hold_jnt = pm.createNode('joint',n = self.mesh+"_New_Jnt")
                
            self.meshCluster = pm.skinCluster(hold_jnt, self.mesh)


        #get influnced joints of the mesh
        mesh_joints = pm.skinCluster(self.mesh, inf = True, q = True)


        #get unlocked joint to transfer deformer weight
        unlockJnt = []
        for n in mesh_joints:
            findlock = pm.getAttr(n+'.liw')
            print (findlock)
            if findlock == False:
                unlockJnt.append(n)
        
        if unlockJnt == []:
            pm.error( "Please unlock one joint" )
        
        if len(unlockJnt) > 1:
            pm.error( "Only one joint should be unlocked" )
            
        #lock all other weights except the first unlocked weight
        pm.setAttr(unlockJnt[0]+'.liw', 1)


        #get effected verticies
        gotselected = []
        if self.meshCluster:
            pm.skinCluster(self.meshCluster, e=True, siv = unlockJnt)
            effectdVrt0 = cmds.ls(sl=True, fl =1 )
            gotselected = getData().solvVert(effectdVrt0)

        else:
            polyCo = cmds.polyEvaluate(self.mesh, v=True )
            for i in range(polyCo):
                gotselected.append(str(i))
        

        #save hold joint's weight
        hold_skin_value = []

        for fdf in gotselected:
            JntVal = pm.skinPercent(str(self.meshCluster), self.mesh+'.vtx['+fdf+']' , transform = unlockJnt[0], query=True )
            hold_skin_value.append(JntVal)
        
        #Add other joints to skin cluster
        for gfs in self.inf_jnts:
            pm.skinCluster(self.meshCluster, edit=True,ai=gfs,lw = 1)

        #Create wire deformer 
        wireDfm = pm.wire( self.mesh, w= self.deformer, gw = False, en= 1.000000, ce= 0.000000, li= 0.000000, dds=[(0, 1000)] )[0]
        pm.setAttr(wireDfm.rotation, 0)
        
        #------------------------------------------------------
        
        for xx in self.inf_jnts:
        
            whichVer = []
            '''
            TODO ye whichVer bahar shift kr skte h kya list har bar band rhi h aur har bar append ho rha h esme toh ky mtlb h, whichVer = karke likh dega to vo ve chlega na 
            ye duplicate wala change krde, pymel ka .getPointPosition se hojyega
            example - 

            vtx = pm.PyNode('pSphere1.vtx[334]')
            pos = vtx.getPosition()

            '''
            pm.select(xx, r =True)
            pm.move( 1, xx+'.rotatePivot', y=True, r = True)
            whichVer.append(xx)
            pm.select(self.mesh)
            pm.duplicate(n = 'Get_Test_Mesh')
            pm.move( -1, xx+'.rotatePivot', y=True, r = True)
            pm.select(self.mesh)
            #polyCount = cmds.polyEvaluate( v=True )

            set_01ZMain = []
            set_02ZMain = []
            finlDist= []
                
            for x in range(3):
                    
                set_01Z = []
                
                set_02Z = []
                
            #------------------------------------------------------
                for d in gotselected:
                    
                    Attr = pm.xform(self.mesh+'.vtx['+d+']', q =True, ws = True, t=True)[x]
                    
                    set_01Z.append((Attr))
                    
            #------------------------------------------------------
                for b in gotselected:
                    
                    Attrs = pm.xform('Get_Test_Mesh'+'.vtx['+b+']', q =True, ws = True, t=True)[x]
                    
                    set_02Z.append((Attrs))
                
                pm.select(d =True)
                
                set_01ZMain.append(set_01Z)
                set_02ZMain.append(set_02Z)
            
            #---------------------------------------------------getDiff 
            for o in range(len(gotselected)):
                    
                x1      = float(set_01ZMain[0][o])
                
                y1      = float(set_01ZMain[1][o])
            
                z1      = float(set_01ZMain[2][o])
                
                x2      = float(set_02ZMain[0][o])
            
                y2      = float(set_02ZMain[1][o])
                
                z2      = float(set_02ZMain[2][o])
                    
                findis = math.sqrt(((x1-x2)*(x1-x2))+((y1-y2)*(y1-y2))+((z1-z2)*(z1-z2)))
                    
                finlDist.append(findis)
        
            #---------------------------------------------------percentage_find
            FinelWeight = []
            
            for nnn in range(len(hold_skin_value)):
                
                FinelW = (hold_skin_value[nnn]/1.0)*finlDist[nnn]
                FinelWeight.append(FinelW)
            
            #---------------------------------------------------addSkin
            cmds.setAttr(unlockJnt[0]+'.liw', 0)
            for R in gotselected:
                
        
                if FinelWeight[gotselected.index(R)] != 0.0:
        
        
        
                    pm.skinPercent(self.meshCluster,self.mesh+'.vtx['+R+']', tv=(whichVer[0], FinelWeight[gotselected.index(R)]))
        
        
            cmds.delete('Get_Test_Mesh')
        
        for fv in self.inf_jnts:
            pm.setAttr(fv+'.liw', 0)
        
        pm.skinCluster(self.meshCluster, e = True, ri= unlockJnt[0])
        #---------------------------------------------------delete_Unwanted_Things
        if self.meshCluster == []:
            pm.delete(unlockJnt[0])
        pm.delete(wireDfm)
        pm.delete(self.deformer+'BaseWire')
        
        
        #TODO maya 2024 m curve delete hora h bnane k bad vo b dkna h kya dikat h thori safai krdi bs line 132 se tu change krde tarika calculation ka uske bad har deformer m kse kam krega uske conditions dalte h
            


