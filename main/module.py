import time
import pymel.core as pm
import maya.cmds as cmds
import math
import sys
'''

ui
query definations - selection check error
find data 
create curve from transforms
one defination for all deformer
skin cluster utils 
export/import- skin/deformers 
copy skin 
vertex weight slider
mirror deformer weight
'''



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
    


        #---------------------------------------------------Distance between two vertex
    def VertDistance(self, meshNam, VertNumList, moverNam ):
        
        old_PoseVert = []
        New_PoseVert = []
        Distance= []

        for xyz in [0,1,2]:
            set_01Z = []
            
            for d in VertNumList:
                
                Attr = pm.xform(meshNam+'.vtx['+d+']', q =True, ws = True, t=True)[xyz]
                
                set_01Z.append((Attr))
            pm.select(d =True)
        
            old_PoseVert.append(set_01Z)
        

        pm.move( 1, moverNam+'.rotatePivot', y=True, r = True)

        for xyz in [0,1,2]:
            set_02Z = []

            for b in VertNumList:
                
                Attrs = pm.xform(meshNam+'.vtx['+b+']', q =True, ws = True, t=True)[xyz]
                
                set_02Z.append((Attrs))
            pm.select(d =True)
            
            New_PoseVert.append(set_02Z)

        pm.move( -1, moverNam+'.rotatePivot', y=True, r = True)
        

        for o in range(len(VertNumList)):
                
            x1,y1,z1      = float(old_PoseVert[0][o]), float(old_PoseVert[1][o]), float(old_PoseVert[2][o])
            x2,y2,z2      = float(New_PoseVert[0][o]), float(New_PoseVert[1][o]), float(New_PoseVert[2][o])
                
            Distance.append(math.sqrt(((x1-x2)*(x1-x2))+((y1-y2)*(y1-y2))+((z1-z2)*(z1-z2))))
        
        return Distance
        


        #---------------------------------------------------percentage_find
    def WeightByOnePercentage(self, distance, hold_skin ):
        
        percentage = []

        for nnn in range(len(hold_skin)):
            Onepercentage = (hold_skin[nnn]/1.0)*  distance[nnn]
            percentage.append(Onepercentage)

        return percentage


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
        self.vertNumber = []
        self.hold_skin_value = []
        self.inf_jnts = getData().get_influnced_joints(self.deformer)


    def deformer_skin_convert(self):
        '''
        TODO write doc
        '''
        #get mesh skin cluster
        self.meshCluster = getData(object = self.mesh).get_skinCluster()
        

        #check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh+"_Hold_Jnt") == False:
                self.hold_joint = pm.createNode('joint',n = self.mesh+"_Hold_Jnt")
                
            self.meshCluster = pm.skinCluster(self.hold_joint, self.mesh)
            cmds.select(cl= 1)


        #get influnced joints of the mesh
        mesh_joints = pm.skinCluster(self.mesh, inf = True, q = True)


        #get unlocked joint to transfer deformer weight
        unlockJnt = []
        for n in mesh_joints:
            findlock = pm.getAttr(n+'.liw')
            if findlock == False:
                unlockJnt.append(n)
        
        if unlockJnt == []:
            pm.error( "Please unlock one joint" )
        
        if len(unlockJnt) > 1:
            pm.error( "Only one joint should be unlocked" )
            
        #lock all other weights except the first unlocked weight
        pm.setAttr(unlockJnt[0]+'.liw', 1)


        #get effected verticies
        if self.meshCluster:
            pm.skinCluster(self.meshCluster, e=True, siv = unlockJnt)
            effectdVrt0 = cmds.ls(sl=True, fl =1 )
            self.vertNumber = getData().solvVert(effectdVrt0)

        else:
            polyCo = cmds.polyEvaluate(self.mesh, v=True )
            for i in range(polyCo):
                self.vertNumber.append(str(i))
        

        #save hold joint's weight

        for fdf in self.vertNumber:
            JntVal = pm.skinPercent(str(self.meshCluster), self.mesh+'.vtx['+fdf+']' , transform = unlockJnt[0], query=True )
            self.hold_skin_value.append(JntVal)
        
        #Add other joints to skin cluster
        for gfs in self.inf_jnts:
            pm.skinCluster(self.meshCluster, edit=True,ai=gfs,lw = 1)

        #Create wire deformer 
        wireDfm = pm.wire( self.mesh, w= self.deformer, gw = False, en= 1.000000, ce= 0.000000, li= 0.000000, dds=[(0, 1000)] )[0]
        pm.setAttr(wireDfm.rotation, 0)
        
        #------------------------------------------------------
        
        for xx in self.inf_jnts:
        
            '''
            TODO 
            
            '''
        
            Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, xx)
            
            WeightbyPercent = getData().WeightByOnePercentage(Fineldistance, self.hold_skin_value)


            #---------------------------------------------------skin apply

            cmds.setAttr(unlockJnt[0]+'.liw', 0)
            for R in self.vertNumber:
                
                if WeightbyPercent[self.vertNumber.index(R)] != 0.0:
        
                    pm.skinPercent(self.meshCluster,self.mesh+'.vtx['+R+']', tv=(xx, WeightbyPercent[self.vertNumber.index(R)]))

        

        for fv in self.inf_jnts:
            pm.setAttr(fv+'.liw', 0)
        
        pm.skinCluster(self.meshCluster, e = True, ri= unlockJnt[0])
        #---------------------------------------------------delete_Unwanted_Things
        if self.meshCluster == []:
            pm.delete(unlockJnt[0])
        pm.delete(wireDfm)
        pm.delete(self.deformer+'BaseWire')
        
        
        #TODO 
        # just to remind myself:- self.variable bnane h har jgha
            

