# --------------------------------------------------------------
# VN_Magic_Deform_Tool_2.0.py - python Script
# --------------------------------------------------------------
#
# DESCRIPTION:
#	A nicer why to convert any deformer into skincluster
#	
# USAGE:
#	Copy "VN_Magic_Deform_Tool_2.0.py" in your maya python script editor and run ;
#
# AUTHORS:
#	Name      : Vishal Nagpal
#   Gmail     : vishalnagpal878@gamil.com
#   linkedin  : linkedin.com/in/vishal-nagpal-82975a149
#	Copyright ©2022 Vishal Nagpal
#
# VERSIONS:
#	2.0 - Feb 21, 2022 - Initial Release.
#
# Tip for knowledge:
#   The vertex distance can be equal to the weight.


import pymel.core as pm
import time
import math
import sys

if pm.window("VN_Magic_Deform_Tool", exists=True):
	pm.deleteUI("VN_Magic_Deform_Tool", window=True)

if pm.windowPref( "VN_Magic_Deform_Tool", exists=True ):
    pm.windowPref( "VN_Magic_Deform_Tool", remove=True )
    

window     = pm.window("VN Magic Deform Tool",s =0, iconName='Short Name',widthHeight=(300, 433), bgc = [(.1),(.1),(.01)])

form       = pm.formLayout(numberOfDivisions=100)
Text       = pm.text(l ='Just One Click!', h =20, w = 80 )

Wire       = pm.iconTextButton('WireBase',ann =' Wire to skin convert ' ,style='iconAndTextHorizontal', image1='wire.png',c = 'wireButton()' , label='Wire to Skin',w=200,h=35, bgc = [(.21),(.42),(.3)])
Lattice    = pm.iconTextButton('LatticeBase',ann =' Lattice to skin convert ',style='iconAndTextHorizontal', image1='lattice.png',c = 'latticeButton()',l = 'Lattice to Skin',w=200,h=35, bgc = [(.21),(.42),(.3)])
shape      = pm.iconTextButton('shapeBase',ann =' shape to skin convert ',style='iconAndTextHorizontal', image1='blendShape.png',c = 'blendShapeButton()' ,l = 'BlendShape to Skin',w=200,h=35, bgc = [(.21),(.42),(.3)])
Wrap       = pm.iconTextButton('wrapBase',ann =' Wrap to skin convert ',style='iconAndTextHorizontal', image1='wrap.png',c = 'wrapButton()',l = 'Wrap to Skin',w=200,h=35, bgc = [(.21),(.42),(.3)])
Cluster    = pm.iconTextButton('ClusterBase',ann =' Cluster to skin convert ',style='iconAndTextHorizontal', image1='cluster.png', c = 'clusterButton()',l = 'Cluster to Skin',w=200,h=35, bgc = [(.21),(.42),(.3)])
SoftS      = pm.iconTextButton('SoftSBase',ann =' Soft Selection to skin convert ',style='iconAndTextHorizontal', image1='sculptPinch.png', c = 'SoftButton()',l = 'Soft Selection to Skin',w=200,h=35, bgc = [(.21),(.42),(.3)])
Curve      = pm.iconTextButton('CurveBase',ann =' Curve to skin convert ',style='iconAndTextHorizontal', image1='curveEP.png', c = 'CurveButton()', l = 'Curve to Skin',w=200,h=45, bgc = [(.8),(.8),(.5)])

Linkdin    = pm.iconTextButton('LinkdinBase',ann =' https://www.linkedin.com/in/vishal-nagpal-82975a149/ ',c ='pm.webBrowser( url="https://www.linkedin.com/in/vishal-nagpal-82975a149/",vis =0)',style='iconAndTextHorizontal',l = 'Linkedin',w=550,h=15, bgc = [(.1),(.1),(.01)])
Gmail      = pm.iconTextButton('GmailBase',ann =' vishalnagpal878@gmail.com ',style='iconAndTextHorizontal',l = 'vishalnagpal878@gmail.com',w=550,h=15, bgc = [(.1),(.1),(.01)])


setingWire = pm.symbolButton(i = 'menuIconHelp.png', h= 30,w = 30,ann =' select wire first and then Mesh.\n\n ( Wire should have all skinned joints. \n joints should not have any connection. )')
setingLatt = pm.symbolButton(i = 'menuIconHelp.png', h= 30,w = 30,ann =' select lattice first and then Mesh.\n\n ( lattice should have all skinned joints. \n joints should not have any connection. )')
setingShap = pm.symbolButton(i = 'menuIconHelp.png', h= 30,w = 30,ann =' select blendshape.\n\n ( Mesh should have only one blenshape on it at a time. )')
setingWrap = pm.symbolButton(i = 'menuIconHelp.png', h= 30,w = 30,ann =' Select SourceMesh then WrapMesh. \n\n ( SourceMesh should have all skinned joints. \n joints should not have any connection. )')
setingClst = pm.symbolButton(i = 'menuIconHelp.png', h= 30,w = 30,ann =' Select cluster first then Mesh.')
setingSoft = pm.symbolButton(i = 'menuIconHelp.png', h= 30,w = 30,ann =' Create Soft Selection.\n\n ( select one cluster at a time.)')
setingCurv = pm.symbolButton(i = 'menuIconHelp.png', h= 30,w = 30,ann =' Select curve first and then Mesh.\n\n ( Curve should have all skinned joints. \n joints should not have any connection. )')


pm.formLayout( form, edit=True,  

attachForm=   [(Text, 'top', 5),
               (Wire, 'top', 40),
               (Lattice, 'top', 90),
               (shape, 'top', 140),
               (Wrap, 'top', 190),
               (Cluster, 'top', 240),
               (SoftS, 'top', 290),
               (Curve, 'top', 342),
               (setingWire, 'top', 40),
               (setingLatt, 'top', 90),
               (setingShap, 'top', 140),
               (setingWrap, 'top', 190),
               (setingClst, 'top', 240),
               (setingSoft, 'top', 295),
               (setingCurv, 'top', 348),
               (Linkdin, 'top', 393),
               (Gmail, 'top', 408),
            ],
attachControl=[(Text, 'bottom', 30, Wire), 
             ],
               
attachPosition=[(Text, 'right', 10, 65),
                (Wire, 'right', 0, 75), 
                (Lattice, 'right', 0, 75), 
                (shape, 'right', 0, 75), 
                (Wrap, 'right', 0, 75), 
                (Cluster, 'right', 0, 75), 
                (SoftS, 'right', 0, 75),
                (Curve, 'right', 0, 75),
                (setingWire, 'left', 20, 75),
                (setingLatt, 'left', 20, 75),
                (setingShap, 'left', 20, 75),
                (setingWrap, 'left', 20, 75),
                (setingClst, 'left', 20, 75),
                (setingSoft, 'left', 20, 75),
                (setingCurv, 'left', 20, 75),
                (Linkdin, 'left', 0, 40),
                (Gmail, 'left', 0, 22)],
                
 )

pm.showWindow( window )

'''--------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------'''

'''-----------------------------------------------------------------------------------'''

#=========================================New_Jnt_And_Rename
def NewJnt(positonN):
    objList = cmds.ls("NewVish_*_Jnt")
    
    alln = []
    
    for n in objList:
        objNewNum = int(n.split('_')[1])
        alln.append(objNewNum)
    alln.sort()
    
    alln2 = []
    for p in range(1,alln[0]):
        alln2.append(p)
    
    for d in range(len(alln)-1):
        for n in range(alln[d]+1,alln[d+1]):
            alln2.append(n)
    
    cmds.select(d = True)
    
    if alln2 != []:
        if alln2[0] < 10:
            zro = "0"
            cmds.joint(n = "NewVish_"+zro[0]+str(alln2[0])+"_Jnt", p = positonN)
        else:
            cmds.joint(n = "NewVish_"+str(alln2[0])+"_Jnt", p = positonN)
            
    if alln2 == []:
        if alln[-1]+1 < 10:
            zro = "0"
            cmds.joint(n = "NewVish_"+zro[0]+str(alln[-1]+1)+"_Jnt", p = positonN)
        else:
            cmds.joint(n = "NewVish_"+str(alln[-1]+1)+"_Jnt", p = positonN)
                        

#=========================================Checking if defaut strings already Exists --  Funtion

def findString():
    
    mysStrings = ['CoolForge','Get_Test_Mesh']
    
    for gbgbg in mysStrings:
        if cmds.objExists(gbgbg):
          print (pm.error( "<<<<<(Please Rename " + gbgbg + " or delete it )>>>>>" ))
          

'''-----------------------------------------------------------------------------------'''
def SimpleCurveConvert():
    
    start_time = time.time()
    
    #=========================================Checking if defaut strings already Exists
    
              
    findString()
    
    
    #=========================================start
    
    
    selection0 = cmds.ls(sl=True)
    selecti_00 = selection0[0]
    selecti_01 = selection0[1]
    cmds.select(d = True)
    
    #------------------------------------------------------Find_SkinCluster
    
    def SkinClustor(NamSkinClust):
        nodes = []
    
        node = cmds.listHistory(NamSkinClust)
        for damn in node:
            
            if cmds.nodeType(damn) == 'skinCluster':
                nodes.append(damn)
        return nodes
     
    cluster_00 = SkinClustor(selecti_00)
    cluster_01no = SkinClustor(selecti_01)
    
    #------------------------------------------------------Find_crv_Jnt
    
    Aljnts = cmds.skinCluster(selecti_00, inf = True, q = True)
    
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

    def solvVert(vertcnt):
        
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
    
    pm.wire( selecti_01, w= selecti_00,n = 'CoolForge', gw = False, en= 1.000000, ce= 0.000000, li= 0.000000, dds=[(0, 1000)] )
    pm.setAttr("CoolForge.rotation", 0)
    
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
    pm.delete('CoolForge')
    pm.delete(selecti_00+'BaseWire')
    
    
        
        
    #---------------------------------------------------Total_Time         
        
    sys.stdout.write('You have done a great job. ' " %s seconds " % (time.time() - start_time))
        
    #---------------------------------------------------end...
    
    

    

'''-----------------------------------------------------------------------------------'''




def ClusterConvert():
        
    start_time = time.time()
    
    #=========================================Checking if defaut strings already Exists
              
    findString()
    
    #=========================================start
    
    selection0 = pm.ls(sl=True)
    positon = cmds.getAttr(selection0[0]+'.origin')[0]
    
    pm.select(d =True)
    
    
    #------------------------------------------------------Find_SkinCluster
    
    
    def SkinClustor(NamSkinClust):
        nodes = []
    
        node = pm.listHistory(NamSkinClust)
        for damn in node:
            
            if pm.nodeType(damn) == 'skinCluster':
                nodes.append(damn)
        return nodes
    
    
    
    #------------------------------------------------------check if both have same skinclister
    
        
    if len(SkinClustor(selection0[-1]))==0:
        if pm.objExists("New_Vishu_Jnt") == False:
            pm.joint(n = "New_Vishu_Jnt")
            
        pm.skinCluster('New_Vishu_Jnt', selection0[-1])
    
    
    #------------------------------------------------------Find_Hold_Jnt
    
    
    Meeshjnts = pm.skinCluster(selection0[-1], inf = True, q = True)
    
    pm.setAttr(Meeshjnts[0]+'.liw', 1)
    
    
    #------------------------------------------------------
    pm.select(selection0[0], r =True)
    for nnn in range(len(selection0)-1):
        
        pm.select(selection0[nnn],add = True)
        
    
    pm.move( 1, y=True, r = True)
    
    pm.duplicate(selection0[-1], n = 'Get_Test_Mesh')
    
    pm.move( -1,y=True, r = True)
    
    pm.select(selection0[-1])
    
    polyCount = pm.polyEvaluate( v=True )
    
    
    #-----------------------------------------------------set1
    
    set_01ZMain = []
    set_02ZMain = []
    finlDist= []
        
    for x in range(3):
            
        set_01Z = []
        
        set_02Z = []
        
    #------------------------------------------------------
        for d in range(polyCount):
            
            Attr = '%.3f'%pm.xform(selection0[-1]+'.vtx['+str(d)+']', q =True, ws = True, t=True)[x]
            
            set_01Z.append((Attr))
            
    #------------------------------------------------------
        for b in range(polyCount):
            
            Attrs = '%.3f'%pm.xform('Get_Test_Mesh'+'.vtx['+str(b)+']', q =True, ws = True, t=True)[x]
            
            set_02Z.append((Attrs))
        
        pm.select(d =True)
        
        set_01ZMain.append(set_01Z)
        set_02ZMain.append(set_02Z)
      
    #---------------------------------------------------getDiff 
    for o in range(polyCount):
               
        x1      = float(set_01ZMain[0][o])
        
        y1      = float(set_01ZMain[1][o])
    
        z1      = float(set_01ZMain[2][o])
        
        x2      = float(set_02ZMain[0][o])
    
        y2      = float(set_02ZMain[1][o])
        
        z2      = float(set_02ZMain[2][o])
            
        findis = math.sqrt(((x1-x2)*(x1-x2))+((y1-y2)*(y1-y2))+((z1-z2)*(z1-z2)))
            
        finlDist.append(findis)
    
    
    #---------------------------------------------------addNewJnt and influnence
    
    if pm.objExists("NewVish_01_Jnt") == False:
        pm.joint(n = "NewVish_01_Jnt", p = positon)
    else:
        NewJnt(positon)
    
    NwJnt = pm.ls(sl=True)
    pm.select(selection0[-1])
    
    pm.skinCluster(edit=True,ai= NwJnt[0],lw = 1)
    
    #---------------------------------------------------addSkin
    
    for R in range(polyCount):
    
        pm.setAttr(Meeshjnts[0]+'.liw', 0)
    
            
    
        if finlDist[R] != 0.0:
    
    
    
            pm.skinPercent( SkinClustor(selection0[-1])[0],selection0[-1]+'.vtx['+str(R)+']', tv=(NwJnt[0], finlDist[R]))
    
    
    pm.delete('Get_Test_Mesh')
        
        
    #---------------------------------------------------Total_Time  
    
    
    sys.stdout.write('You have done a great job. ' " %s seconds " % (time.time() - start_time))
    
    
    
    
    #---------------------------------------------------end.. 







'''-----------------------------------------------------------------------------------'''


def SoftConvert():

    start_time = time.time()
    
    #=========================================Checking if defaut strings already Exists
              
    findString()
    
    #=========================================start
    
    selection0 = cmds.ls(sl=True)
    selecti_00 = selection0[0]
    cmds.cluster(n = 'VishClust')
    
    shapename = cmds.listHistory(selecti_00)[0]
    positon = cmds.getAttr("VishClustHandleShape.origin")[0]
    cmds.delete('VishClust')
    
    cmds.select(shapename)
    cmds.pickWalk(d = 'up')
    
    transName = cmds.ls(sl=True)
    
    cmds.select(d =True)
    
    
    #------------------------------------------------------Find_SkinCluster
    
    
    def SkinClustor(NamSkinClust):
        nodes = []
    
        node = cmds.listHistory(NamSkinClust)
        for damn in node:
            
            if cmds.nodeType(damn) == 'skinCluster':
                nodes.append(damn)
        return nodes
    
    cluster_01no = SkinClustor(transName)
    #------------------------------------------------------if_no_skin_on_mesh_thenadd_one_joint
    
    if cluster_01no == []:
        
        if cmds.objExists("New_VishHold_Jnt") == False:
            cmds.joint(n = "New_VishHold_Jnt")
            
        cmds.skinCluster('New_VishHold_Jnt', transName)
        
    
    cmds.select(d = True)
    cluster_01 = SkinClustor(transName)
    
    
    newJnt01 = []
    
    if cmds.objExists("NewVish_01_Jnt") == True:
        cmds.select(d = True)
        NewJnt(positon)
        NwJnt = cmds.ls(sl=True)
        newJnt01.append(NwJnt[0])
        cmds.select(transName)
        cmds.skinCluster(edit=True,ai=NwJnt[0],lw = 1, wt = 0)
        cmds.select(d = True)
        
    if cmds.objExists("NewVish_01_Jnt") == False:
        cmds.select(d = True)
        cmds.joint(n = "NewVish_01_Jnt", p = positon )
        NwJnt = cmds.ls(sl=True)
        newJnt01.append(NwJnt[0])
        cmds.select(transName)
        cmds.skinCluster(edit=True,ai="NewVish_01_Jnt",lw = 1, wt = 0)
    #------------------------------------------------------Find_Hold_Jnt
    
    
    Meeshjnts = cmds.skinCluster(transName, inf = True, q = True)
    
    cmds.setAttr(Meeshjnts[0]+'.liw', 1)
    
    
    #------------------------------------------------------
    
    cmds.select(selecti_00, r =True)
    for nnn in range(len(selection0)):
        cmds.select(selection0[nnn],add = True)
    
    cmds.move( 1, y=True, r = True)
    
    cmds.duplicate(transName[0], n = 'Get_Test_Mesh')
    
    cmds.move( -1,y=True, r = True)
    
    cmds.select(transName[0])
    
    polyCount = cmds.polyEvaluate( v=True )
    
    
    #-----------------------------------------------------set1
    
    set_01ZMain = []
    set_02ZMain = []
    finlDist= []
        
    for x in range(3):
            
        set_01Z = []
        
        set_02Z = []
        
    #------------------------------------------------------
        for d in range(polyCount):
            
            Attr = '%.3f'%pm.xform(transName[0]+'.vtx['+str(d)+']', q =True, ws = True, t=True)[x]
            
            set_01Z.append((Attr))
            
    #------------------------------------------------------
        for b in range(polyCount):
            
            Attrs = '%.3f'%pm.xform('Get_Test_Mesh'+'.vtx['+str(b)+']', q =True, ws = True, t=True)[x]
            
            set_02Z.append((Attrs))
        
        pm.select(d =True)
        
        set_01ZMain.append(set_01Z)
        set_02ZMain.append(set_02Z)
      
    #---------------------------------------------------getDiff 
    for o in range(polyCount):
               
        x1      = float(set_01ZMain[0][o])
        
        y1      = float(set_01ZMain[1][o])
    
        z1      = float(set_01ZMain[2][o])
        
        x2      = float(set_02ZMain[0][o])
    
        y2      = float(set_02ZMain[1][o])
        
        z2      = float(set_02ZMain[2][o])
            
        findis = math.sqrt(((x1-x2)*(x1-x2))+((y1-y2)*(y1-y2))+((z1-z2)*(z1-z2)))
            
        finlDist.append(findis)
    
    
    #---------------------------------------------------addSkin
    
    for R in range(polyCount):
    
        cmds.setAttr(Meeshjnts[0]+'.liw', 0)
    
            
    
        if finlDist[R] != 0.0:
    
    
    
            cmds.skinPercent( SkinClustor(transName[0])[0],transName[0]+'.vtx['+str(R)+']', tv=(newJnt01[0], finlDist[R]))
    
    
    cmds.delete('Get_Test_Mesh')
        
        
    #---------------------------------------------------Total_Time  
    
    
    sys.stdout.write('You have done a great job. ' " %s seconds " % (time.time() - start_time))
    
    
    
    
    #---------------------------------------------------end..


'''-----------------------------------------------------------------------------------'''

        
def WrapCurveWireLatticeConvet():

    start_time = time.time()
    
    #=========================================Checking if defaut strings already Exists
              
    findString()
    
    #=========================================start
    
    selection0 = cmds.ls(sl=True)
    
    cmds.select(d = True)
    
    #=========================================if_Wire_rotation_Zero
    def checkWire(NamwireDfm):
        nodes = []
    
        node = cmds.listHistory(NamwireDfm)
        for damn in node:
            
            if cmds.nodeType(damn) == 'wire':
                nodes.append(damn)
        return nodes
        
    rotVal = []
    if checkWire(selection0[1]) != []:
        rotVal2 = pm.getAttr(checkWire(selection0[1])[0]+".rotation")
        rotVal.append(rotVal2)
        if rotVal != 0.0:
            pm.setAttr(checkWire(selection0[1])[0]+".rotation", 0.0)
            
    #------------------------------------------------------Find_SkinCluster
    
    
    def SkinClustor(NamSkinClust):
        nodes = []
    
        node = cmds.listHistory(NamSkinClust)
        for damn in node:
            
            if cmds.nodeType(damn) == 'skinCluster':
                nodes.append(damn)
        return nodes
    
    #------------------------------------------------------check if both have same skinclister
    meshClust = SkinClustor(selection0[1])
    wireClust = SkinClustor(selection0[0])
    
    if len(SkinClustor(selection0[0]))==0:
        print (pm.error( "<<<<<(no skin on wire)>>>>>" ))
    
    if len(SkinClustor(selection0[0]))==1:
        if wireClust[0] in meshClust:
            meshClust.remove(wireClust[0])
    
    if SkinClustor(selection0[0]) != 0:
        for n in SkinClustor(selection0[0]):
            if n in meshClust:
                meshClust.remove(n)
            
    if meshClust==[]:
        if cmds.objExists("New_Vishu_Jnt") == False:
            cmds.joint(n = "New_Vishu_Jnt")
            
        cmds.skinCluster('New_Vishu_Jnt', selection0[1])
    
    #------------------------------------------------------Find_Hold_Jnt
    
    
    Meeshjnts = cmds.skinCluster(selection0[1], inf = True, q = True)
    
    cmds.setAttr(Meeshjnts[0]+'.liw', 1)
    
    
    #------------------------------------------------------Find_deformer_Jnt
    
    
    Aljnts = cmds.skinCluster(selection0[0], inf = True, q = True)
    
    
    #------------------------------------------------------addInflunce_other_Jnts
    
    
    
    for gfs in Aljnts:
        
        if gfs not in Meeshjnts:
    
            cmds.select(selection0[1])
        
            cmds.skinCluster(edit=True,ai=gfs,lw = 1)
    
    
    
    #------------------------------------------------------
    
    
    for xx in Aljnts:
    
        whichVer = []
    
        verName = cmds.select(xx, r =True)
    
        cmds.move( 1, xx+'.rotatePivot', y=True, r = True)
    
        whichVer.append(xx)
    
        cmds.select(selection0[1])
    
        cmds.duplicate(n = 'Get_Test_Mesh')
    
        cmds.move( -1, xx+'.rotatePivot', y=True, r = True)
    
        cmds.select(selection0[1])
    
        polyCount = cmds.polyEvaluate( v=True )
    
    
        set_01ZMain = []
        set_02ZMain = []
        finlDist= []
            
        for x in range(3):
                
            set_01Z = []
            
            set_02Z = []
            
        #------------------------------------------------------
            for d in range(polyCount):
                
                Attr = '%.3f'%pm.xform(selection0[1]+'.vtx['+str(d)+']', q =True, ws = True, t=True)[x]
                
                set_01Z.append((Attr))
                
        #------------------------------------------------------
            for b in range(polyCount):
                
                Attrs = '%.3f'%pm.xform('Get_Test_Mesh'+'.vtx['+str(b)+']', q =True, ws = True, t=True)[x]
                
                set_02Z.append((Attrs))
            
            pm.select(d =True)
            
            set_01ZMain.append(set_01Z)
            set_02ZMain.append(set_02Z)
          
        #---------------------------------------------------getDiff 
        for o in range(polyCount):
                   
            x1      = float(set_01ZMain[0][o])
            
            y1      = float(set_01ZMain[1][o])
        
            z1      = float(set_01ZMain[2][o])
            
            x2      = float(set_02ZMain[0][o])
        
            y2      = float(set_02ZMain[1][o])
            
            z2      = float(set_02ZMain[2][o])
                
            findis = math.sqrt(((x1-x2)*(x1-x2))+((y1-y2)*(y1-y2))+((z1-z2)*(z1-z2)))
                
            finlDist.append(findis)
    
    
        #---------------------------------------------------addSkin
    
        for R in range(int(polyCount)):
    
            cmds.setAttr(Meeshjnts[0]+'.liw', 0)
    
            
    
            if finlDist[R] != 0.0:
    
    
    
                cmds.skinPercent( SkinClustor(selection0[1])[0],selection0[1]+'.vtx['+str(R)+']', tv=(whichVer[0], finlDist[R]))
    
    
        cmds.delete('Get_Test_Mesh')
    
    
    if checkWire(selection0[1]) != []:
        pm.setAttr(checkWire(selection0[1])[0]+".rotation", rotVal[0])
    #---------------------------------------------------Total_Time         
    
    
    sys.stdout.write('You have done a great job. ' " %s seconds " % (time.time() - start_time))
    
    #---------------------------------------------------end..




    
'''---------------------------------------------------------------------------------'''
def BlendShapeConvert():
    
    start_time = time.time()
    
    #=========================================Checking if defaut strings already Exists
              
    findString()
    
    #=========================================start
    
    transName = pm.ls(sl=True)
    
    pm.listHistory(transName[0])
    
    pm.select(d =True)
    
    #------------------------------------------------------Find_SkinCluster
    
    def BlendShape(NamBlensSHape):
        nodes = []
    
        node = pm.listHistory(NamBlensSHape)
        for damn in node:
            
            if pm.nodeType(damn) == 'blendShape':
                nodes.append(damn)
        return nodes
    
    WeightName = pm.listAttr(BlendShape(transName[0])[0]+'.w', m =True)
    
    #------------------------------------------------------Find_SkinCluster
    
    
    def SkinClustor(NamSkinClust):
        nodes = []
    
        node = pm.listHistory(NamSkinClust)
        for damn in node:
            
            if pm.nodeType(damn) == 'skinCluster':
                nodes.append(damn)
        return nodes
    
    #------------------------------------------------------check if both have same skinclister
    
    if len(SkinClustor(transName[0]))==0:
        if pm.objExists("New_Vishu_Jnt") == False:
            pm.joint(n = "New_Vishu_Jnt")
            
        pm.skinCluster('New_Vishu_Jnt', transName[0])
        
    #------------------------------------------------------Find_Hold_Jnt
    
    MeshJnt = pm.skinCluster(transName[0], inf = True, q = True)
    
    pm.setAttr(MeshJnt[0]+'.liw', 1)
    
    #------------------------------------------------------
    
    pm.setAttr(BlendShape(transName[0])[0]+'.'+WeightName[0], 1)
    
    pm.duplicate(transName[0], n = 'Get_Test_Mesh')
    
    pm.setAttr(BlendShape(transName[0])[0]+'.'+WeightName[0], 0)
    
    pm.select(transName[0])
    
    polyCount = pm.polyEvaluate( v=True )
    
    pm.select(d =True)
    
    #---------------------------------------------------addNewJnt and influnence
    
    if pm.objExists("NewVish_01_Jnt") == False:
        pm.joint(n = "NewVish_01_Jnt")
    else:
        NewJnt((0.0,0.0,0.0))
    
    NwJnt = pm.ls(sl=True)
    pm.select(transName[0])
    
    pm.skinCluster(edit=True,ai= NwJnt[0],lw = 1)
    
    #-----------------------------------------------------set1
    
    set_01ZMain = []
    set_02ZMain = []
    finlDist= []
    
    
    finlDistGetBig = []
    
    
    for x in range(3):
            
        set_01Z = []
        
        set_02Z = []
        
    #------------------------------------------------------
        for d in range(polyCount):
            
            Attr = '%.3f'%pm.xform(transName[0]+'.vtx['+str(d)+']', q =True, ws = True, t=True)[x]
            
            set_01Z.append((Attr))
            
    #------------------------------------------------------
        for b in range(polyCount):
            
            Attrs = '%.3f'%pm.xform('Get_Test_Mesh'+'.vtx['+str(b)+']', q =True, ws = True, t=True)[x]
            
            set_02Z.append((Attrs))
        
        pm.select(d =True)
        
        set_01ZMain.append(set_01Z)
        set_02ZMain.append(set_02Z)
      
    #---------------------------------------------------getDiff 
    for o in range(polyCount):
               
        x1      = float(set_01ZMain[0][o])
        
        y1      = float(set_01ZMain[1][o])
    
        z1      = float(set_01ZMain[2][o])
        
        x2      = float(set_02ZMain[0][o])
    
        y2      = float(set_02ZMain[1][o])
        
        z2      = float(set_02ZMain[2][o])
            
        findis = math.sqrt(((x1-x2)*(x1-x2))+((y1-y2)*(y1-y2))+((z1-z2)*(z1-z2)))
            
        finlDist.append(findis)
        finlDistGetBig.append(findis)
                
    #---------------------------------------------------addSkin
    finlDistGetBig.sort()
    finlDistGetBigNum = finlDistGetBig[-1]
    
    for R in range(polyCount):
            
        pm.setAttr(MeshJnt[0]+'.liw', 0)
    
                
        if finlDist[R] != 0.0 :
            
            pm.skinPercent( SkinClustor(transName[0])[0],transName[0]+'.vtx['+str(R)+']', tv=(NwJnt[0], finlDist[R]/finlDistGetBigNum))
                
    pm.delete('Get_Test_Mesh')
        
    #---------------------------------------------------Total_Time  
    
    
    sys.stdout.write('You have done a great job. ' " %s seconds " % (time.time() - start_time))
    
    
    
    #---------------------------------------------------end..   

    
    
    
    
    
'''------------------------------------------------------------'''







#=========================================Lattice
def latticeButton():
    selectedo = cmds.ls(sl=True)
    listo = cmds.listHistory(selectedo[1]) 
    allObjecto = []
    for s in listo:
        if  cmds.nodeType(s) == 'lattice':
            allObjecto.append(s)
            
    if len(allObjecto) !=0:
        WrapCurveWireLatticeConvet()
        print('Lattice',allObjecto)
    else:
        cmds.error( "No_Lattice" )
#=========================================

#=========================================wire----
def wireButton():
    selectedo = cmds.ls(sl=True)
    listo = cmds.listHistory(selectedo[1]) 
    allObjecto = []
    for s in listo:
        if  cmds.nodeType(s) == 'wire':
            allObjecto.append(s)
            
    if len(allObjecto) !=0:
        WrapCurveWireLatticeConvet()
        print('Wire',allObjecto)
    else:
        cmds.error( "No_Wire" )
#=========================================

#=========================================wrap----
def wrapButton():
    selectedo = cmds.ls(sl=True)
    listo = cmds.listHistory(selectedo[1]) 
    allObjecto = []
    for s in listo:
        if  cmds.nodeType(s) == 'wrap':
            allObjecto.append(s)
            
    if len(allObjecto) !=0:
        WrapCurveWireLatticeConvet()
        print('Wrap',allObjecto)
    else:
        cmds.error( "No_Wrap" )
#=========================================

#=========================================blendShape----
def blendShapeButton():
    selectedo = cmds.ls(sl=True)
    listo = cmds.listHistory(selectedo[0]) 
    allObjecto = []
    for s in listo:
        if  cmds.nodeType(s) == 'blendShape':
            allObjecto.append(s)
            
    if len(allObjecto) !=0:
        BlendShapeConvert()
        print('BlendShape',allObjecto)
    else:
        cmds.error( "No_BlendShape" )
#=========================================

#=========================================clusterHandle----
def clusterButton():
    selectedo = cmds.ls(sl=True)
    listo = cmds.listHistory(selectedo[-1]) 
    allObjecto = []
    for s in listo:
        if  cmds.nodeType(s) == 'cluster':
            allObjecto.append(s)
            
    if len(allObjecto) !=0:
        ClusterConvert()
        print('Cluster',allObjecto)
    else:
        cmds.error( "No_Cluster" )
#=========================================

#=========================================SoftSelection
def SoftButton():
    checkSoft = cmds.softSelect(q = True, sse=True)
    
    selectedo = cmds.ls(sl=True)
    
    if cmds.nodeType(selectedo[0]) == 'mesh' and checkSoft == 1:
        SoftConvert()
        print('SoftSelection',selectedo)
    else:
        cmds.error( "No_SoftSelection" )
    
#=========================================

#=========================================Curve
def CurveButton():
    pm.pickWalk(d = 'down')
    selectedo = cmds.ls(sl=True)
    pm.pickWalk(d = 'up')
    if cmds.nodeType(selectedo[0]) == 'nurbsCurve' and cmds.nodeType(selectedo[1]) == 'mesh' :
        SimpleCurveConvert()
        print('Curve')
    else:
        cmds.error( "No_Curve" )
#=========================================

'''------------------------------------------------------------end'''
