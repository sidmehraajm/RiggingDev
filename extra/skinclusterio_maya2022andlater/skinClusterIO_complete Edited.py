
###########################

#Title: skinClusterIO.py
#Author: Noah Schnapp
#LinkedIn: https://www.linkedin.com/in/wnschnapp/

###########################
####### IMPORTS ###########
###########################

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as OpenMayaAPI
import maya.api.OpenMayaAnim as OpenMayaAnimAPI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMaya as OpenMaya
import os
import imp

import numpy as np
import json

import time

####################################################################

dirpath = r'C:\Users\user\Downloads'

####################################################################

#...SCRIPT EDITOR USE


# import sys 
# import imp 
# dirpath = r'C:\Users\wnsch\Dropbox\projects\2021-09-10_skinClusterIO\contents\04-example-files'
# sys.path.insert(0, dirpath) 
# import skinClusterIO_complete 
# imp.reload(skinClusterIO_complete)
# skinClusterIO_complete.create_sphereSkin()


#...results
# 200k tris, 100 jnts
# json 			= 		68.02 seconds, 177MB filesize
# compression 	= 		2.14 seconds, 3.5MB filesize

#...json
# GetData Elapsed: 4.30999994278
# SaveData Elapsed: 4.42299985886
# Total Elapsed: 8.81399989128

# ReadData Elapsed: 1.15600013733
# SetData Elapsed: 76.2200000286
# Total Elapsed: 77.6979999542

#...compression
# GetData Elapsed: 2.2389998436
# Save Elapsed: 0.0019998550415
# Total Elapsed: 2.24399995804

#...three phases
# get data
# compress data
# write data

# read data
# uncompress data
# set data

####################################################################
#...CODE START

def create_sphereSkin():

	#...vars
	mesh = 'mesh'
	smoothDivisions = 4
	jntCount = 100

	#...file new
	cmds.file(new=True, f=True)
	#...create sphere
	cmds.polySphere(n=mesh, r=5)
	#...smooth
	cmds.polySmooth(mesh, divisions=smoothDivisions)
	cmds.delete(mesh, ch=True)
	#...create joints
	cmds.select(cl=True)
	jnt_Array = [cmds.joint() for j in range(jntCount)]
	#...bind
	skinCluster = cmds.skinCluster(jnt_Array, mesh, n='skinCluster_mesh', tsb = True)[0]

	return True

def devSave():

	#...init class
	cSkinClusterIO_json = SkinClusterIO_json()
	cSkinClusterIO = SkinClusterIO()

	#...vars
	mesh = 'mesh'

	#...timeStart
	timeStart = time.time()

	#...run
	# cSkinClusterIO_json.save(mesh, dirpath=dirpath)
	cSkinClusterIO.save(mesh, dirpath=dirpath)

	#...timeEnd
	timeEnd = time.time()
	timeElapsed = timeEnd-timeStart

	#...print time
	print('Total Elapsed: %s'%timeElapsed)

	return True

def devLoad():

	#...init class
	cSkinClusterIO_json = SkinClusterIO_json()
	cSkinClusterIO = SkinClusterIO()

	#...vars
	mesh = 'mesh'

	#...timeStart
	timeStart = time.time()

	#...run
	# cSkinClusterIO_json.load(mesh, dirpath=dirpath)
	cSkinClusterIO.load(mesh, dirpath=dirpath)

	#...timeEnd
	timeEnd = time.time()
	timeElapsed = timeEnd-timeStart

	#...print time
	print('Total Elapsed: %s'%timeElapsed)

	return True

def devSaveLoad():

	#...create demo
	# create_sphereSkin()
	devSave()
	devLoad()

	return True

class SkinClusterIO(object):

	def __init__(self):

		#...class init
		self.cDataIO 			    = DataIO()

		#...vars
		self.name                   = ''
		self.type                  	= 'skinCluster'
		self.legend_Array = None
		self.weightsNonZero_Array   = []
		self.weights_Array          = []
		self.infMap_Array 			= []
		self.vertSplit_Array        = []
		self.inf_Array              = []
		self.skinningMethod         = 1
		self.normalizeWeights       = 1
		self.geometry               = None
		self.blendWeights           = []
		self.vtxCount               = 0
		self.envelope        		= 1
		self.skinningMethod         = 1
		self.useComponents         	= 0
		self.normalizeWeights       = 1
		self.deformUserNormals      = 1

		pass

	def get_mesh_components_from_tag_expression(self, skinPy, tag='*'):
		geo_types = ["mesh", "nurbsSurface", "nurbsCurve"]
		for t in geo_types:
			obj = skinPy.listConnections(et=True, t=t)
			if obj:
				geo = obj[0].getShape().name()
		# Get attr out of shape
		attr_out = cmds.deformableShape(geo, localShapeOutAttr=True)[0]
		# Get the output geometry data as MObject
		sel = OpenMaya.MSelectionList()
		sel.add(geo)
		dep = OpenMaya.MObject()
		sel.getDependNode(0, dep)
		fn_dep = OpenMaya.MFnDependencyNode(dep)
		plug = fn_dep.findPlug(attr_out, True)
		obj = plug.asMObject()
		# Use the MFnGeometryData class to query the components for a tag expression
		fn_geodata = OpenMaya.MFnGeometryData(obj)
		# Components MObject
		components = fn_geodata.resolveComponentTagExpression(tag)
		dagPath = OpenMaya.MDagPath.getAPathTo(dep)
		return dagPath, components
		
	def get_data(self, skinCluster):

		#...get PyNode skinCluster
		skinPy = pm.PyNode(skinCluster)

		#...Pre Maya 2022 or new compoent tag expression
		try:
			fnSet = OpenMaya.MFnSet(skinPy.__apimfn__().deformerSet())
			members = OpenMaya.MSelectionList()
			fnSet.getMembers(members, False)
			dagPath = OpenMaya.MDagPath()
			components = OpenMaya.MObject()
			members.getDagPath(0, dagPath, components)
		except:
			dagPath, components = self.get_mesh_components_from_tag_expression(skinPy)


		#...get mesh
		geometry = cmds.skinCluster(skinCluster, query = True, geometry = True)[0]

		#...get vtxID_Array
		vtxID_Array = list(range(0,len(cmds.ls('%s.vtx[*]'%geometry,fl=1))))

		#...get skin
		selList = OpenMayaAPI.MSelectionList()
		selList.add(mel.eval('findRelatedSkinCluster %s' % geometry))
		skinPath = selList.getDependNode(0)

		#...get mesh
		selList = OpenMayaAPI.MSelectionList()
		selList.add(geometry)
		meshPath = selList.getDagPath(0)

		#...get vtxs
		fnSkinCluster = OpenMayaAnimAPI.MFnSkinCluster(skinPath);
		fnVtxComp = OpenMayaAPI.MFnSingleIndexedComponent()
		vtxComponents = fnVtxComp.create( OpenMayaAPI.MFn.kMeshVertComponent )
		fnVtxComp.addElements(vtxID_Array);

		#...get weights/infs
		dWeights, infCount = fnSkinCluster.getWeights(meshPath, vtxComponents)
		weights_Array = np.array(list(dWeights), dtype='float64')
		inf_Array = [dp.partialPathName() for dp in fnSkinCluster.influenceObjects()]
		
		#...convert to weightsNonZero_Array
		weightsNonZero_Array, infMap_Array, vertSplit_Array = self.compress_weightData(weights_Array, infCount)

		#...gatherBlendWeights
		blendWeights_mArray = OpenMaya.MDoubleArray()
		skinPy.__apimfn__().getBlendWeights(dagPath, components, blendWeights_mArray)
		
		#...set data to self vars
		self.name 					= skinCluster
		self.weightsNonZero_Array   = np.array(weightsNonZero_Array)
		self.infMap_Array       	= np.array(infMap_Array)
		self.vertSplit_Array       	= np.array(vertSplit_Array)
		self.inf_Array              = np.array(inf_Array)
		self.geometry               = geometry
		self.blendWeights           = np.array(blendWeights_mArray)
		self.vtxCount               = len(vertSplit_Array)-1

		#...get attrs
		self.envelope         		= cmds.getAttr(skinCluster + ".envelope")
		self.skinningMethod         = cmds.getAttr(skinCluster + ".skinningMethod")
		self.useComponents       	= cmds.getAttr(skinCluster + ".useComponents")
		self.normalizeWeights       = cmds.getAttr(skinCluster + ".normalizeWeights")
		self.deformUserNormals      = cmds.getAttr(skinCluster + ".deformUserNormals")
	
		return True

	def set_data(self, skinCluster):

		#...get PyNode skinCluster
		skinPy = pm.PyNode(skinCluster)

		#...Pre Maya 2022 or new compoent tag expression
		try:
			fnSet = OpenMaya.MFnSet(skinPy.__apimfn__().deformerSet())
			members = OpenMaya.MSelectionList()
			fnSet.getMembers(members, False)
			dagPath = OpenMaya.MDagPath()
			components = OpenMaya.MObject()
			members.getDagPath(0, dagPath, components)
		except:
			dagPath, components = self.get_mesh_components_from_tag_expression(skinPy)

		###################################################

		#...set infs
		influencePaths = OpenMaya.MDagPathArray()
		infCount = skinPy.__apimfn__().influenceObjects(influencePaths)
		influences_Array = [influencePaths[i].partialPathName() for i in range(influencePaths.length())]

		#...change the order in set(i,i)
		influenceIndices = OpenMaya.MIntArray(infCount)
		[influenceIndices.set(i,i) for i in range(infCount)]

		###################################################

		#...construct mArrays from normal/numpy arrays
		infCount = len(influences_Array)
		weightCounter = 0
		weights_Array = []
		weights_mArray = OpenMaya.MDoubleArray()
		length = len(self.vertSplit_Array)
		for vtxId, splitStart in enumerate(self.vertSplit_Array):
			if vtxId < length-1:
				vertChunk_Array = [0]*infCount
				splitEnd = self.vertSplit_Array[vtxId+1]

				#...unpack data and replace zeros with nonzero weight vals
				for i in range(splitStart, splitEnd):
					infMap = self.infMap_Array[i]
					val = self.weightsNonZero_Array[i]
					vertChunk_Array[infMap] = val

				#...append to raw data array
				for vert in vertChunk_Array:
					weights_mArray.append(vert)

		blendWeights_mArray = OpenMaya.MDoubleArray()
		for i in self.blendWeights:
			blendWeights_mArray.append(i)
		
		###################################################
		#...set data
		# skinPy.setWeights(dagPath, components, influenceIndices, weights_mArray, False)

		skinPy.__apimfn__().setWeights(dagPath, components, influenceIndices, weights_mArray, False)
		#skinPy.setBlendWeights(dagPath, components, blendWeights_mArray)
		skinPy.__apimfn__().setBlendWeights(dagPath, components, blendWeights_mArray)
		###################################################
		#...set attrs of skinCluster
		cmds.setAttr('%s.envelope'%skinCluster, self.envelope)
		cmds.setAttr('%s.skinningMethod'%skinCluster, self.skinningMethod)
		cmds.setAttr('%s.useComponents'%skinCluster, self.useComponents)
		cmds.setAttr('%s.normalizeWeights'%skinCluster, self.normalizeWeights)
		cmds.setAttr('%s.deformUserNormals'%skinCluster, self.deformUserNormals)

		#...name
		cmds.rename(skinCluster, self.name)

		return True

	def save(self, node=None, dirpath=None):
		
		#...get selection
		if node == None:
			node = cmds.ls(sl=1)
			if node == None:
				print('ERROR: Select Something!')
				return False
			else:
				node = node[0]

		#...get skinCluster
		skinCluster = mel.eval('findRelatedSkinCluster ' + node)
		if not cmds.objExists(skinCluster):
			print('ERROR: Node has no skinCluster!')
			return False

		#...get dirpath
		if dirpath == None:
			startDir = cmds.workspace(q=True, rootDirectory=True)
			dirpath = cmds.fileDialog2(caption='Save Skinweights', dialogStyle=2, fileMode=3, startingDirectory=startDir, fileFilter='*.npy', okCaption = "Select")

		#...get filepath
		skinCluster = 'skinCluster_%s'%node
		filepath = '%s/%s.npy'%(dirpath, skinCluster)

		#...timeStart
		timeStart = time.time()

		#...get data
		self.get_data(skinCluster)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('GetData Elapsed: %s'%timeElapsed)

		#...construct data_dict instead of data array
		data_dict = {
		    'legend': self.legend_Array,
		    'weightsNonZero_Array': self.weightsNonZero_Array.tolist(),
		    'vertSplit_Array': self.vertSplit_Array.tolist(),
		    'infMap_Array': self.infMap_Array.tolist(),
		    'inf_Array': self.inf_Array.tolist(),
		    'geometry': self.geometry,
		    'blendWeights': self.blendWeights.tolist(),
		    'vtxCount': self.vtxCount,
		    'name': self.name,
		    'envelope': self.envelope,
		    'skinningMethod': self.skinningMethod,
		    'useComponents': self.useComponents,
		    'normalizeWeights': self.normalizeWeights,
		    'deformUserNormals': self.deformUserNormals,
		    'type': self.type
		}

		#...timeStart
		timeStart = time.time()

		#...write data 
		#print('Data before saving:', data_dict)
		np.save(filepath, data_dict)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('SaveData Elapsed: %s'%timeElapsed)

		return True	

	def load(self, node=None, dirpath=None):

		#...get selection
		if node == None:
			node = cmds.ls(sl=1)
			if node == None:
				print('ERROR: Select Something!')
				return False
			else:
				node = node[0]

		#...get dirpath
		if dirpath == None:
			startDir = cmds.workspace(q=True, rootDirectory=True)
			dirpath = cmds.fileDialog2(caption='Load Skinweights', dialogStyle=2, fileMode=1, startingDirectory=startDir, fileFilter='*.npy', okCaption = "Select")

		#...get filepath
		skinCluster = 'skinCluster_%s'%node
		filepath = '%s/%s.npy'%(dirpath, skinCluster)

		#...check if skinCluster exists
		if not os.path.exists(filepath):
			print('ERROR: SkinCluster for node "%s" not found on disk!'%node)
			return False

		#...unbind current skinCluster
		skinCluster = mel.eval('findRelatedSkinCluster ' + node)
		if cmds.objExists(skinCluster):
			mel.eval('skinCluster -e  -ub ' + skinCluster)

		#...timeStart
		timeStart = time.time()

		#...read data
		data = np.load(filepath, allow_pickle=True)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('ReadData Elapsed: %s'%timeElapsed)

		#...get item data from the dictionary
		self.legend_Array = data['legend']
		self.weightsNonZero_Array = np.array(data['weightsNonZero_Array'])
		self.infMap_Array = np.array(data['infMap_Array'])
		self.vertSplit_Array = np.array(data['vertSplit_Array'])
		self.inf_Array = np.array(data['inf_Array'])
		self.blendWeights = np.array(data['blendWeights'])
		self.vtxCount = data['vtxCount']
		self.geometry = data['geometry']
		self.name = data['name']
		self.envelope = data['envelope']
		self.skinningMethod = data['skinningMethod']
		self.useComponents = data['useComponents']
		self.normalizeWeights = data['normalizeWeights']
		self.deformUserNormals = data['deformUserNormals']

		#...bind skin
		for inf in self.inf_Array:
			if not cmds.objExists(inf):
				cmds.select(cl=True)
				cmds.joint(n=inf)
		skinCluster = 'skinCluster_%s'%node
		skinCluster = cmds.skinCluster(self.inf_Array, node, n=skinCluster, tsb = True)[0]

		#...timeStart
		timeStart = time.time()

		#...set data
		self.set_data(skinCluster)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('SetData Elapsed: %s'%timeElapsed)

		return True	

	###################################
	def compress_weightData(self, weights_Array, infCount):

		#...convert to weightsNonZero_Array
		weightsNonZero_Array = []
		infCounter = 0
		infMap_Chunk = []
		infMap_ChunkCount = 0
		vertSplit_Array = [infMap_ChunkCount]
		infMap_Array = []

		for w in weights_Array:
			if w != 0.0:
				weightsNonZero_Array.append(w)
				infMap_Chunk.append(infCounter)

			#...update inf counter
			infCounter += 1
			if infCounter ==  infCount:
				infCounter = 0
				
				#...update vertSplit_Array
				infMap_Array.extend(infMap_Chunk)
				infMap_ChunkCount = len(infMap_Chunk)+infMap_ChunkCount
				vertSplit_Array.append(infMap_ChunkCount)
				infMap_Chunk = []

		return weightsNonZero_Array, infMap_Array, vertSplit_Array

class SkinClusterIO_json(object):

	def __init__(self):

		pass

	def save(self, node=None, dirpath=None):
		
		#...get selection
		if node == None:
			node = cmds.ls(sl=1)
			if node == None:
				print('ERROR: Select Something!')
				return False
			else:
				node = node[0]

		#...get skinCluster
		skinCluster = mel.eval('findRelatedSkinCluster ' + node)
		if not cmds.objExists(skinCluster):
			print('ERROR: Node has no skinCluster!')
			return False

		#...get dirpath
		if dirpath == None:
			startDir = cmds.workspace(q=True, rootDirectory=True)
			dirpath = cmds.fileDialog2(caption='Save Skinweights', dialogStyle=2, fileMode=3, startingDirectory=startDir, fileFilter='*.json', okCaption = "Select")

		#...get filepath
		skinCluster = 'skinCluster_%s'%node
		filepath = '%s/%s.json'%(dirpath, skinCluster)

		#...timeStart
		timeStart = time.time()

		#...get data
		data = {}
		shape = cmds.listRelatives(node, c=True)[0]
		vtx_Array = ["{0}.vtx[{1}]".format(shape, x) for x in cmds.getAttr(shape + ".vrts", multiIndices=True)]
		for vtx in vtx_Array:
			inf_Array = cmds.skinPercent(skinCluster, vtx, transform=None, q=1)		
			weights = cmds.skinPercent(skinCluster, vtx, q=1, v=1)
			data[vtx] = list(zip(inf_Array, weights))

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('GetData Elapsed: %s'%timeElapsed)

		#...timeStart
		timeStart = time.time()

		#...write data
		with open(filepath, 'w') as fh:
			json.dump(data, fh, indent=4, sort_keys=True)

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('SaveData Elapsed: %s'%timeElapsed)

		return True

	def load(self, node=None, dirpath=None):
		
		#...get selection
		if node == None:
			node = cmds.ls(sl=1)
			if node == None:
				print('ERROR: Select Something!')
				return False
			else:
				node = node[0]

		#...get dirpath
		if dirpath == None:
			startDir = cmds.workspace(q=True, rootDirectory=True)
			dirpath = cmds.fileDialog2(caption='Load Skinweights', dialogStyle=2, fileMode=3, startingDirectory=startDir, fileFilter='*.json', okCaption = "Select")
		
		#...get filepath
		skinCluster = 'skinCluster_%s'%node
		filepath = '%s/%s.json'%(dirpath, skinCluster)

		#...check if skinCluster exists
		if not os.path.exists(filepath):
			print('ERROR: SkinCluster for node "%s" not found on disk!'%node)
			return False

		#...unbind current skinCluster
		skinCluster = mel.eval('findRelatedSkinCluster ' + node)
		if cmds.objExists(skinCluster):
			mel.eval('skinCluster -e  -ub ' + skinCluster)

		#...timeStart
		timeStart = time.time()

		#...load
		fh = open(filepath, 'r')
		data = json.load(fh)
		fh.close()

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('ReadData Elapsed: %s'%timeElapsed)

		#...bind skin
		for vtx, weights in data.items():
			inf_Array = [inf[0] for inf in weights]
			break
		#...create the joint if it doesnt exist
		for inf in inf_Array:
			if not cmds.objExists(inf):
				cmds.select(cl=True)
				cmds.joint(n=inf)
		skinCluster = 'skinCluster_%s'%node
		skinCluster = cmds.skinCluster(inf_Array, node, n=skinCluster, tsb = True)[0]

		#...timeStart
		timeStart = time.time()

		#...set data
		[cmds.skinPercent(skinCluster, vtx, tv=data[vtx], zri=1) for vtx in data.keys()]

		#...timeEnd
		timeEnd = time.time()
		timeElapsed = timeEnd-timeStart

		#...print time
		print('SetData Elapsed: %s'%timeElapsed)
		
		return True

class DataIO(object):

	def __init__(self):

		pass

	@staticmethod
	def get_legendArrayFromData(data):

		return data[0]

	@staticmethod
	def get_dataItem(data, item, legend_Array=None):
		if item not in data[0]:
			print('ERROR: "%s" Not Found in data!'%item)
			return False
		#...no legend_Array
		if legend_Array is None:
			legend_Array = [key for key in data[0]]	
		#...with legend_Array
		return data[legend_Array.index(item)]

	@staticmethod
	def set_dataItems(data, itemData_Array):

		return data




