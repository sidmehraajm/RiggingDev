import json, sys
import pymel.core as pm
import maya.cmds as cmds

def getShape(node, intermediate = False):
    if pm.nodeType(node)=='transform':
        tr = pm.PyNode(node)
        trShape = tr.getShapes()
        resultShapes = []
        for shape in trShape:
            isIntermediate = pm.getAttr('%s.intermediateObject'%shape)
            if intermediate and isIntermediate and pm.listConnections(shape, source = False):
                return str(shape)
            elif not intermediate and not isIntermediate:
                return str(shape)
        if trShape:
            return trShape[0]
        elif pm.nodeType(node) in ['mesh','nurbsCurve','nurbsSurface']:
            return str(node)
        return None
            
            
                
def getSkinCluster(shape):
    shape = getShape(shape)
    skin= pm.ls(pm.listHistory(shape),typ='skinCluster')
    if skin:
        return str(skin[0])
    raise RuntimeError('No SkinCluster found')
    
    
    
def writeJson(dataToWrite,fileName):
        if '.json' not in fileName:
            fileName+='.json'
            
        print("> write to json file is seeing: {0}".format(fileName))
        
        with open(fileName,'w') as jsonFile:
            json.dump(dataToWrite,jsonFile,indent = 2)
            
        print ("Data was successfully written to {0}".format(fileName))
        
        return fileName

        
        
            


def readJsonFile(fileName):
    try:
        with open(fileName,'r') as jsonFile:
            return json.load(jsonFile)
    except:
        raise RuntimeError("Could not read {0}".format(fileName))


class gatherData(object):

    def getShapeNode(self,shape):
        return(getShape(shape))
        
    def getSkinClusterNode(self,shape):
        return(getSkinCluster(shape))
        
    def getTransformNode(self,shape):
        if pm.nodeType(shape) == 'transform':
            return(shape)
        else:
            return(pm.listTransforms(shape)[0])
    def getVtxRange(self,shape):
        
        vtxData = pm.polyEvaluate(getShape(shape),v=1)
        #main Result1
        vtxResult = []
        for i in range(0,vtxData):
            vtxResult.append('%s.vtx[%s]'%(shape,i))
        return (vtxResult)
        
        
    def getJntInfluences(self,shape):
        skinCl = pm.PyNode(getSkinCluster(shape))
        jnts = skinCl.getInfluence()
        jntValues = []
        for i in jnts:
            jntValues.append(str(i))
            
        return(jntValues)

def ExtractData(v=0,tn=0,sn=0,sCn=0,jInf =0,objName = ''):
    '''
    vertex : v=1
    transformNode :tn=1
    shapeNode: sn=1
    skinClusteNOde:sCn=1
    jointInfluences: jInf=1
    objName = 'object name'
    '''
    returnValues = []

    data = gatherData()
    if v==1:
        returnValues.append(data.getVtxRange(objName))
    if tn==1:
        returnValues.append(data.getTransformNode(objName))
    if sn==1:
        returnValues.append(data.getShapeNode(objName))
    if sCn==1:
        returnValues.append(data.getSkinClusterNode(objName))
    if jInf==1:
        returnValues.append(data.getJntInfluences(objName))
    return returnValues

def getVtxWeights(vtxList=[],skinClusterNode ='',thresholdValue=0.001):
    '''
    vertexList: vtxList=[]
    skinCLusterName: skinClusterNode =''
    thresholdValue: thresholdValue=0.001
    '''
    
    if len(vtxList) != 0 and skinClusterNode != "":
        vtxDict = {}
        for vtx in vtxList:
            infValue = cmds.skinPercent(skinClusterNode,vtx,q=1,v=1,ib =thresholdValue)
            #print (infValue)
            infNames = cmds.skinPercent(skinClusterNode,vtx,transform = None,q=1,ib =thresholdValue)
            #print (infNames)
            vtxDict[vtx]= zip(infNames,infValue)
        return vtxDict
    else:
        raise RuntimeError("No Vertices or SkinCluster passed")
        
        
def export_deformer2(objectName='',filePath=''):
    if objectName =='' and filePath == '':
        raise RuntimeError("No object name specifide & no file path given")
    
    geoData = ExtractData(v=1,tn=1,sCn=1,jInf=1,objName = objectName)
    vtxData = geoData[0]
    geoName = geoData[1]
    skinClusterNode=geoData[2]
    thV = 0.001
    jntNames = geoData[-1]
    
    skinClusterDetails = [geoName,skinClusterNode,jntNames]
    vtxDict = getVtxWeights(vtxData,skinClusterNode)

    if skinClusterDetails:
        sknfilePath = filePath.split('.json')[0]+'_sknInfo.json'
        
        writeJson(dataToWrite = skinClusterDetails,fileName = sknfilePath)
            
    if vtxDict:
        writeJson(dataToWrite = vtxDict,fileName = filePath)
        


def import_deformer2(filePath):
    importFile = filePath
    sknfilePath = filePath.split('.json')[0]+'_sknInfo.json'
    sys.stdout.write('importing from %s'%str(importFile))
    
    skinData = readJsonFile(sknfilePath)
    
    MeshName = skinData[0]
    skinCLusterName = skinData[1]
    influenceJoints = skinData[-1]
    
    if not pm.objExists(MeshName):
        raise RuntimeError(str(MeshName)+' >> Mesh Not Found')
    for i in influenceJoints:
        if not pm.objExists(i):
            raise RuntimeError(str(i)+' >> joint Not Found')
            
    data = gatherData()
    try:
        oldSkin = data.getSkinClusterNode(MeshName)
        pm.delete(oldSkin)
        print('Removing existing skin Cluster on the object named')
    except:
        pass
                
    
    pm.skinCluster(influenceJoints,MeshName,n = skinCLusterName)
    pm.select(cl=1)
    
    #loading vtxweights
    
    filevtxData = readJsonFile(importFile)
    if len(filevtxData)>0:
        
        for key in filevtxData.keys():
            try:
                pm.skinPercent(skinCLusterName,key,tv=filevtxData[key],zri=1)
            except:
                raise RuntimeError('Issue while loading weights can be - Vertex not found or mesh changed')
                
    else:
        pm.error('JSON file is empty')
                
            
    
      
    
    
       
       

    
'''    
export_deformer2(objectName,filePath)    
    
import_deformer2(filePath)

objectName = 'qq'   
    
filePath = "E:/tst.json"
    
exportWeightsJSON('s','asd')
a = getVtxWeights(vtxList,skinClusterNode)
        
data = gatherData()
vtxList =data.getVtxRange('pCone1')     
skinClusterNode = data.getSkinClusterNode('pCone1')    
        
v =['a','bv','c']    
g = ['1','2','3']
a = zip(v,g)
a = list(a)    

'''    
    
   