import time
import pymel.core as pm
import maya.cmds as cmds

class deformerConvert:
    '''
    TODO write doc
    '''

    def __init__(self, deformer = None, mesh = None):
        self.deformer = deformer
        self.mesh = mesh
        self.hold_joint = None

        

    def deformer_skin_convert(self):
        
        
        selection0 = cmds.ls(sl=True)
        selecti_00 = selection0[0]
        selecti_01 = selection0[1]
        cmds.select(d = True)
        
        #------------------------------------------------------Find_SkinCluster
        
        def SkinClustor(self, NamSkinClust):
            nodes = []
        
            node = cmds.listHistory(NamSkinClust)
            for damn in node:
                
                if cmds.nodeType(damn) == 'skinCluster':
                    nodes.append(damn)
            return nodes
        
        cluster_00 = SkinClustor(selecti_00)
        cluster_01no = SkinClustor(selecti_01)
        
        #------------------------------------------------------Find_crv_Jnt
        
        Aljnts = cmds.skinCluster( selecti_00, inf = True, q = True)
        
        #------------------------------------------------------if_no_skin_on mesh
        
        if cluster_01no == []:
            if pm.objExists("New_Nagpal_Jnt") == False:
                pm.joint(n = "New_Nagpal_Jnt")
                
            cmds.skinCluster('New_Nagpal_Jnt', selecti_01)
            
        cmds.select(d = True)
        cluster_01 = SkinClustor(selecti_01)
        #------------------------------------------------------Find_Hold_Jnt
        
        Meeshjnts = cmds.skinCluster(selecti_01, inf = True, q = True)
        
        #------------------------------------------------------find unlocked join and lock it
        
        unlockJnt = []
        
        for n in Meeshjnts:
            findlock = cmds.getAttr(n+'.liw')
            if findlock == False:
                unlockJnt.append(n)
        
        if unlockJnt == []:
            cmds.error( "Please unlock one joint" )
        
        if len(unlockJnt) > 1:
            cmds.error( "Please only one joint should be unlocked" )
            
        cmds.setAttr(unlockJnt[0]+'.liw', 1)
        
        #------------------------------------------------------solvVert

        def solvVert(self,vertcnt):
            
            totalCounts = []
            
            for vert in vertcnt:
                
                split01 = vert.split("[")
                split02 = split01[-1].split("]")
        
                start = int(split02[0])
                
                totalCounts.append(str(start))
                    
            return (totalCounts)
        

        #------------------------------------------------------getEffectedVrt
        
        cmds.select(d = True)
        
        gotselected = []
        if len(cluster_01no) == 1:
            cmds.skinCluster(cluster_01no, e=True, selectInfluenceVerts = unlockJnt)
            effectdVrt0 = cmds.ls(sl=True, fl =1 )
            gotselected = solvVert(effectdVrt0)
            
        if len(cluster_01no) != 1:
            polyCo = cmds.polyEvaluate(selecti_01, v=True )
            for i in range(polyCo):
                gotselected.append(str(i))
        
        
        cmds.select(d = True)
        
        
        #------------------------------------------------------save_Hold_Jnt_Weight
        cmds.select(selecti_01)
        #polyCount2 = cmds.polyEvaluate( v=True )
        cmds.select(d =True)
        
        Value = []
        
        for fdf in gotselected:
            
            JntVal = cmds.skinPercent(SkinClustor(selecti_01)[0], selecti_01+'.vtx['+fdf+']' , transform = unlockJnt[0], query=True )
            Value.append(JntVal)
        
        
        #------------------------------------------------------addInflunce_other_Jnts
        
        for gfs in Aljnts:
        
            cmds.select(selecti_01)
        
            cmds.skinCluster(edit=True,ai=gfs,lw = 1)
        
        
        #------------------------------------------------------wire
        
        wireDfm = pm.wire( selecti_01, w= selecti_00,n = selecti_00+'_coolforge', gw = False, en= 1.000000, ce= 0.000000, li= 0.000000, dds=[(0, 1000)] )[0]
        pm.setAttr(selecti_00+"_coolforge.rotation", 0)
        
        #------------------------------------------------------
        
        for xx in Aljnts:
        
            whichVer = []
        
            verName = cmds.select(xx, r =True)
        
            cmds.move( 1, xx+'.rotatePivot', y=True, r = True)
        
            whichVer.append(xx)
        
            cmds.select(selecti_01)
        
            cmds.duplicate(n = 'Get_Test_Mesh')
        
            cmds.move( -1, xx+'.rotatePivot', y=True, r = True)
        
            cmds.select(selecti_01)
        
            #polyCount = cmds.polyEvaluate( v=True )
        
        
            set_01ZMain = []
            set_02ZMain = []
            finlDist= []
                
            for x in range(3):
                    
                set_01Z = []
                
                set_02Z = []
                
            #------------------------------------------------------
                for d in gotselected:
                    
                    Attr = pm.xform(selecti_01+'.vtx['+d+']', q =True, ws = True, t=True)[x]
                    
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
            
            for nnn in range(len(Value)):
                
                FinelW = (Value[nnn]/1.0)*finlDist[nnn]
                FinelWeight.append(FinelW)
            
            #---------------------------------------------------addSkin
            cmds.setAttr(unlockJnt[0]+'.liw', 0)
            for R in gotselected:
                
        
                if FinelWeight[gotselected.index(R)] != 0.0:
        
        
        
                    cmds.skinPercent( SkinClustor(selecti_01)[0],selecti_01+'.vtx['+R+']', tv=(whichVer[0], FinelWeight[gotselected.index(R)]))
        
        
            cmds.delete('Get_Test_Mesh')
        
        for fv in Aljnts:
            cmds.setAttr(fv+'.liw', 0)
        
        cmds.skinCluster(SkinClustor(selecti_01)[0], e = True, ri= unlockJnt[0])
        #---------------------------------------------------delete_Unwanted_Things
        if cluster_01no == []:
            pm.delete(unlockJnt[0])
        pm.delete(wireDfm)
        pm.delete(selecti_00+'BaseWire')
        
        
            
            
        #---------------------------------------------------Total_Time         
            
        sys.stdout.write('You have done a great job. ' " %s seconds " % (time.time() - start_time))
            
        #---------------------------------------------------end...
        
        

        

    '''-----------------------------------------------------------------------------------'''
