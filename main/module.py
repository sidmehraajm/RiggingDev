import maya.OpenMaya as om
import pymel.core as pm
import maya.cmds as cmds
import time
import math
import sys

"""

ui
query definations - selection check error
find data 
create curve from transforms
one defination for all deformer----*
skin cluster utils 
export/import- skin/deformers 
copy skin 
vertex weight slider
mirror deformer weight
"""


class utils:
    def __init__(self, object=None):
        self.obj = object

    def CreateCrv(self):
        crv = cmds.curve(p=[cmds.xform(d, t=1, q=1, ws=1)
                         for d in cmds.ls(sl=1)])
        cmds.setAttr(crv+".dispCV", 1)

    def softSelection(self):
        selection = om.MSelectionList()
        softSelection = om.MRichSelection()
        om.MGlobal.getRichSelection(softSelection)
        softSelection.getSelection(selection)

        dagPath = om.MDagPath()
        component = om.MObject()

        iter = om.MItSelectionList(selection, om.MFn.kMeshVertComponent)
        elements = []
        while not iter.isDone():
            iter.getDagPath(dagPath, component)
            dagPath.pop()
            fnComp = om.MFnSingleIndexedComponent(component)
            for i in range(fnComp.elementCount()):
                elements.append(
                    [fnComp.element(i), fnComp.weight(i).influence()])
            iter.next()
        return elements


class getData:
    """
    A class for extracting information and performing calculations related to deformations.
    """

    def __init__(self, object=None):
        self.obj = object

    def get_skinCluster(self):
        """
        Get the skinCluster associated with the object.

        Returns:
            skinCluster (str or None): The name of the skinCluster or None if not found.

        """
        pyObj = pm.PyNode(self.obj)
        try:
            self.skn = pm.ls(pm.listHistory(pyObj), typ="skinCluster")[0]
            return self.skn

        except:
            return None

    def get_influnced_joints(self, skin_node=None):
        """
        Get the list of influenced joints by a given skinCluster.

        Args:
            skin_node (str): The name of the skinCluster.

        Returns:
            influences (list or None): A list of influenced joint names or None if not found.

        """
        try:
            self.influences = pm.skinCluster(skin_node, inf=True, q=True)
            return self.influences

        except:
            # pm.error('No skinCluster found!')
            pass

    def solvVert(self, vertcnt):
        """
        Extract vertex numbers from vertex count strings.

        Args:
            vertcnt (list): List of vertex count strings.

        Returns:
            totalCounts (list): List of extracted vertex numbers as strings.

        """
        totalCounts = []

        for vert in vertcnt:
            split01 = vert.split("[")
            split02 = split01[-1].split("]")
            start = int(split02[0])

            totalCounts.append(str(start))

        return totalCounts

    def effectedVertNumber(self, meshClust, unlockJt):
        """
        Calculate the affected vertex numbers when a joint is unlocked in a skinCluster.

        Args:
            meshClust (str): The name of the skinCluster.
            unlockJt (str): The name of the joint to be unlocked.

        Returns:
            vertNumb (list): List of affected vertex numbers as strings.

        """
        vertNumb = []
        pm.select(cl=1)
        pm.skinCluster(meshClust, e=True, siv=unlockJt)
        effectdVrt0 = cmds.ls(sl=True, fl=1)
        vertNumb = getData().solvVert(effectdVrt0)
        cmds.select(d=1)

        return vertNumb

    def getUnlockedJnt(self, mesh_joinds):
        """
        Find and return joints that are unlocked among a list of joints.

        Args:
            mesh_joints (list): List of joint names to check.

        Returns:
            unlockJnd (list): List of unlocked joint names.

        Raises:
            pm.error: If no joint is unlocked or if more than one joint is unlocked.

        """
        unlockJnd = []
        for n in mesh_joinds:
            findlock = pm.getAttr(n + ".liw")
            if findlock == False:
                unlockJnd.append(n)

        if unlockJnd == []:
            pm.error("Please unlock one joint for distributing the weight")

        if len(unlockJnd) > 1:
            pm.error("Only one joint should be unlocked")

        return unlockJnd

        # ---------------------------------------------------Distance between two vertex

    def VertDistance(self, meshNam, VertNumList, moverNam, moveType=".rotatePivot", BS=False, WeightName=None):
        """
        Calculate the distances between two sets of vertices on a mesh.

        Args:
            mesh_name (str): The name of the mesh.
            vert_num_list (list): List of vertex numbers as strings.
            mover_name (str): The name of the mover object.

        Returns:
            Distance (list): List of distances between vertices.

        """
        old_PoseVert = []
        New_PoseVert = []
        Distance = []

        for xyz in [0, 1, 2]:
            set_01Z = []

            for d in VertNumList:
                Attr = pm.xform(meshNam + ".vtx[" + d + "]", q=True, ws=True, t=True)[
                    xyz
                ]

                set_01Z.append((Attr))
            pm.select(d=True)

            old_PoseVert.append(set_01Z)

        if BS == False:
            pm.move(1, moverNam + moveType, y=True, r=True)
        else:
            pm.setAttr(moverNam[0] + '.' + WeightName[0], 0)

        for xyz in [0, 1, 2]:
            set_02Z = []

            for b in VertNumList:
                Attrs = pm.xform(meshNam + ".vtx[" + b + "]", q=True, ws=True, t=True)[
                    xyz
                ]

                set_02Z.append((Attrs))
            pm.select(d=True)

            New_PoseVert.append(set_02Z)

        if BS == False:
            pm.move(-1, moverNam + moveType, y=True, r=True)
        else:
            pm.setAttr(moverNam[0] + '.' + WeightName[0], 1)

        for o in range(len(VertNumList)):
            x1, y1, z1 = (
                float(old_PoseVert[0][o]),
                float(old_PoseVert[1][o]),
                float(old_PoseVert[2][o]),
            )
            x2, y2, z2 = (
                float(New_PoseVert[0][o]),
                float(New_PoseVert[1][o]),
                float(New_PoseVert[2][o]),
            )

            Distance.append(
                math.sqrt(
                    ((x1 - x2) * (x1 - x2))
                    + ((y1 - y2) * (y1 - y2))
                    + ((z1 - z2) * (z1 - z2))
                )
            )

        return Distance

        # ---------------------------------------------------percentage_find

    def WeightByOnePercentage(self, distance, hold_skin):
        """
        Calculate weight values based on distances and skinCluster weights.

        Args:
            distance (list): List of distances between vertices.
            hold_skin (list): List of skinCluster weights.

        Returns:
            percentage (list): List of weight values.

        """
        percentage = []

        for nnn in range(len(hold_skin)):
            Onepercentage = (hold_skin[nnn] / 1.0) * distance[nnn]
            percentage.append(Onepercentage)

        return percentage

    # --------------------------------------------------- check deformer Type
    def deformerType(self, Name):
        """
        Identify and return the type of deformer applied to an object.

        Args:
            name (str): The name of the object.

        Returns:
            deformer_type (str): The type of deformer (e.g., 'wire', 'lattice', 'cluster', 'wrap', 'blendShape').

        """
        nodes = []

        for dfm in cmds.listHistory(Name):
            if cmds.nodeType(dfm) == "wire":
                pm.setAttr(dfm + ".rotation", 0.0)
                nodes.append("wire")
            if cmds.nodeType(dfm) == "lattice":
                nodes.append("lattice")
            if cmds.nodeType(dfm) == "cluster":
                nodes.append("cluster")
            if cmds.nodeType(dfm) == "wrap":
                nodes.append("wrap")
            if cmds.nodeType(dfm) == "blendShape":
                nodes.append("blendShape")
            if cmds.nodeType(dfm) == "deltaMesh":
                nodes.append("deltaMesh")

        return nodes[0]

    def NewJnt(self, positonN, MeshNam):
        cmds.select(d=True)
        objList = cmds.ls(MeshNam + "_*_Jnt")
        number = [int(i.split("_")[1]) for i in objList]

        nList = []
        for i in range(1, len(number)+2):
            if i not in number:
                nList.append(i)

        jntt = cmds.joint(n=MeshNam + "_" +
                          str(nList[0]).zfill(3) + "_Jnt", p=positonN)
        cmds.select(d=True)
        return jntt

    def BlendShape(self, Nam):

        list = cmds.listHistory(Nam, lv=1)
        nodes = [i for i in list if pm.nodeType(i) == 'blendShape']
        return nodes

    def check_connections(self, obj):
        attributes = ['tx', 'ty', 'tz',
                      'rx', 'ry', 'rz',
                      'sx', 'sy', 'sz']

        for i in attributes:
            keys = cmds.keyframe(obj + '.' + i, query=True)
            if keys:
                print('Please remove all keyframes on joints')

            '''constraints = cmds.listConnections(obj + '.' + i, type='constraint')
            if constraints:
                print('Please remove all constraints on joints')

            connections = cmds.listConnections(obj + '.' + i, plugs=True)
            if connections:
                print('Please remove all connections on joints')'''


class deformerConvert(getData):
    """
    Main class for converting deformers to skincluster.

    Args:
        deformer (str, optional): The name of the deformer to be converted.
        mesh (str, optional): The name of the mesh to be processed.

    Attributes:
        deformer (str): The name of the deformer being converted.
        mesh (str): The name of the mesh being processed.
        hold_joint (str or None): The name of the hold joint created or None.
        meshCluster (str or None): The name of the mesh's skinCluster or None.
        vertNumber (list): List of vertex numbers as strings.
        hold_skin_value (list): List of hold joint's skin weights.
        deformer_inf_jnts (list): List of influenced joint names from the deformer.
        mesh_inf_jnts (list): List of influenced joint names from the mesh.

    """

    def __init__(self, deformer=None, mesh=None):
        getData.__init__(self)
        self.deformer = deformer
        self.mesh = mesh
        self.meshCluster = None
        self.vertNumber = []
        self.hold_skin_value = []
        self.deformer_inf_jnts = getData().get_influnced_joints(self.deformer)
        self.Mesh_inf_jnts = getData().get_influnced_joints(self.mesh)
        self.NewjntNam = None
        self.hold_jntSuffix = '_hold_jnt'
        self.dupMesh = None

    def deformer_skin_convert(self):
        """
        Convert skin weights from the deformer to the mesh.

        Use For Curve to Skin

        """
        # get mesh skin cluster
        self.meshCluster = getData(object=self.mesh).get_skinCluster()

        # check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh + self.hold_jntSuffix) == False:
                pm.createNode("joint", n=self.mesh + self.hold_jntSuffix)

            self.meshCluster = pm.skinCluster(
                self.mesh + self.hold_jntSuffix, self.mesh)
            cmds.select(cl=1)

        # get influnced joints of the mesh
        mesh_joints = pm.skinCluster(self.mesh, inf=True, q=True)

        # get unlocked joint to transfer deformer weight
        unlockJnt = getData().getUnlockedJnt(mesh_joints)

        # lock all other weights except the first unlocked weight
        pm.setAttr(unlockJnt[0] + ".liw", 1)

        # get effected verticies
        self.vertNumber = getData().effectedVertNumber(self.meshCluster, unlockJnt)

        # save hold joint's weight
        for fdf in self.vertNumber:
            JntVal = pm.skinPercent(
                str(self.meshCluster),
                self.mesh + ".vtx[" + fdf + "]",
                transform=unlockJnt[0],
                query=True,
            )
            self.hold_skin_value.append(JntVal)

        # Add other joints to skin cluster
        for gfs in self.deformer_inf_jnts:
            pm.skinCluster(self.meshCluster, edit=True, ai=gfs, lw=1)

        # Create wire deformer
        wireDfm = pm.wire(
            self.mesh,
            w=self.deformer,
            gw=False,
            en=1.000000,
            ce=0.000000,
            li=0.000000,
            dds=[(0, 1000)],
        )[0]
        pm.setAttr(wireDfm.rotation, 0)

        for xx in self.deformer_inf_jnts:
            Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, xx)
            WeightbyPercent = getData().WeightByOnePercentage(
                Fineldistance, self.hold_skin_value
            )

            # apply skin weight
            cmds.setAttr(unlockJnt[0] + ".liw", 0)
            for R in self.vertNumber:
                if WeightbyPercent[self.vertNumber.index(R)] != 0.0:
                    pm.skinPercent(
                        self.meshCluster,
                        self.mesh + ".vtx[" + R + "]",
                        tv=(xx, WeightbyPercent[self.vertNumber.index(R)]),
                    )

        for fv in self.deformer_inf_jnts:
            pm.setAttr(fv + ".liw", 0)

        pm.skinCluster(self.meshCluster, e=True, ri=unlockJnt[0])

        # cleanup
        if self.meshCluster == []:
            pm.delete(unlockJnt[0])

        pm.disconnectAttr((cmds.listRelatives(self.deformer, shapes=True)[
                          0])+".worldSpace[0]", wireDfm+".deformedWire[0]")
        pm.delete(wireDfm)
        pm.delete(self.deformer + "BaseWire")

    def rest_deformer_skin_convert(self):
        """
        Restore the original skin weights on the mesh after deformer conversion.

        Use for Wire, Wrap, delta Mesh and Lattice

        """

        # to check type of deformer and set wire rotation 1
        getData().deformerType(self.mesh)

        meshSkinClust = [getData(object=self.mesh).get_skinCluster()]

        deformerSkinClust = getData(object=self.deformer).get_skinCluster()

        if not deformerSkinClust:  # error if no skin
            pm.error("<<<<<(No SKIN found on deformer)>>>>>")

        if deformerSkinClust in meshSkinClust:  # reomve if same skincluster in mesh
            meshSkinClust.remove(deformerSkinClust)

        # check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh + self.hold_jntSuffix) == False:
                pm.createNode("joint", n=self.mesh + self.hold_jntSuffix)

            self.meshCluster = pm.skinCluster(
                self.mesh + self.hold_jntSuffix, self.mesh)
            cmds.select(cl=1)

        # get effected verticies
        self.vertNumber = [str(i) for i in range(
            cmds.polyEvaluate(self.mesh, v=True))]

        # Add other joints to skin cluster
        pm.skinCluster(self.meshCluster,
                       ai=self.deformer_inf_jnts, edit=True, lw=1, wt=0)

        for xx in self.deformer_inf_jnts:
            Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, xx)

            # skin apply
            for R in self.vertNumber:
                if Fineldistance[self.vertNumber.index(R)] != 0.0:
                    pm.skinPercent(
                        self.meshCluster,
                        self.mesh + ".vtx[" + R + "]",
                        tv=(xx, Fineldistance[self.vertNumber.index(R)]),
                    )

        for fv in self.deformer_inf_jnts:
            pm.setAttr(fv + ".liw", 0)

    def SoftSelectionToConvert(self):
        sel = cmds.ls(sl=True)

        cmds.select(d=1)

        bbx = cmds.xform(sel, q=True, bb=True, ws=True)

        positon = (
            ((bbx[0] + bbx[3]) / 2.0),
            ((bbx[1] + bbx[4]) / 2.0),
            ((bbx[2] + bbx[5]) / 2.0),
        )

        self.mesh = sel[0].split(".")[0]

        self.meshCluster = getData(object=self.mesh).get_skinCluster()

        # check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh + self.hold_jntSuffix) == False:
                pm.createNode("joint", n=self.mesh + self.hold_jntSuffix)

            self.meshCluster = pm.skinCluster(
                self.mesh + self.hold_jntSuffix, self.mesh)
            cmds.select(cl=1)

        # get influnced joints of the mesh
        mesh_joints = pm.skinCluster(self.mesh, inf=True, q=True)

        # get unlocked joint to transfer deformer weight
        unlockJnt = getData().getUnlockedJnt(mesh_joints)

        self.vertNumber = getData().effectedVertNumber(self.meshCluster, unlockJnt)

        # Add new joints to skin cluster
        if cmds.objExists(self.mesh + "_001_Jnt") == False:
            self.NewjntNam = cmds.joint(n=self.mesh + "_001_Jnt", p=positon)
            cmds.skinCluster(self.mesh, edit=True,
                             ai=self.NewjntNam, lw=1, wt=0)
        else:
            self.NewjntNam = getData().NewJnt(positon, self.mesh)
            cmds.skinCluster(self.mesh, edit=True,
                             ai=self.NewjntNam, lw=1, wt=0)

        cmds.select(sel)
        for i in utils().softSelection():
            cmds.select(d=1)

            pm.skinPercent(
                self.meshCluster,
                self.mesh + ".vtx[" + str(i[0]) + "]",
                tv=(self.NewjntNam, i[1]),
            )

    def ClusterConvert(self):

        positon = cmds.getAttr(self.deformer+'.origin')[0]
        cmds.select(d=True)

        clust = getData(object=self.mesh).get_skinCluster()

        if clust == None:
            if pm.objExists(self.mesh + self.hold_jntSuffix) == False:
                pm.joint(n=self.mesh + self.hold_jntSuffix)

            pm.skinCluster(self.mesh + self.hold_jntSuffix, self.mesh)

        mesh_joints = pm.skinCluster(self.mesh, inf=True, q=True)
        # pm.setAttr(mesh_joints[0]+'.liw', 1)

        self.meshCluster = getData(object=self.mesh).get_skinCluster()

        # get effected verticies
        self.vertNumber = getData().effectedVertNumber(
            self.meshCluster, self.mesh + self.hold_jntSuffix)

        Fineldistance = getData().VertDistance(
            self.mesh, self.vertNumber, self.deformer, moveType="")

        if pm.objExists(self.mesh + "_001_Jnt") == False:
            self.NewjntNam = cmds.joint(n=self.mesh + "_001_Jnt", p=positon)
            cmds.skinCluster(self.mesh, edit=True,
                             ai=self.NewjntNam, lw=1, wt=0)
        else:
            self.NewjntNam = getData().NewJnt(positon, self.mesh)
            cmds.skinCluster(self.mesh, edit=True,
                             ai=self.NewjntNam, lw=1, wt=0)

        # skin apply
        for R in self.vertNumber:
            if Fineldistance[self.vertNumber.index(R)] != 0.0:
                pm.skinPercent(
                    self.meshCluster,
                    self.mesh + ".vtx[" + R + "]",
                    tv=(self.NewjntNam,
                        Fineldistance[self.vertNumber.index(R)]),
                )

    def blendShapeConvert(self):

        self.deformer = getData().BlendShape(self.mesh)

        WeightNam = pm.listAttr(self.deformer[0] + '.w', m=True)

        clust = getData(object=self.mesh).get_skinCluster()

        if clust == None:
            cmds.select(d=1)
            if pm.objExists(self.mesh + self.hold_jntSuffix) == False:
                pm.joint(n=self.mesh + self.hold_jntSuffix)

            pm.skinCluster(self.mesh + self.hold_jntSuffix, self.mesh)

        pm.setAttr(self.deformer[0] + '.' + WeightNam[0], 1)

        self.meshCluster = getData(object=self.mesh).get_skinCluster()

        self.vertNumber = getData().effectedVertNumber(
            self.meshCluster, self.mesh + self.hold_jntSuffix)

        Fineldistance = getData().VertDistance(self.mesh, self.vertNumber,
                                               self.deformer, moveType="", BS=True, WeightName=WeightNam)

        if pm.objExists(self.mesh + "_001_Jnt") == False:
            self.NewjntNam = cmds.joint(n=self.mesh + "_001_Jnt", p=(0, 0, 0))
            cmds.skinCluster(self.mesh, edit=True,
                             ai=self.NewjntNam, lw=1, wt=0)
        else:
            self.NewjntNam = getData().NewJnt((0, 0, 0), self.mesh)
            cmds.skinCluster(self.mesh, edit=True,
                             ai=self.NewjntNam, lw=1, wt=0)

        # skin apply
        for R in self.vertNumber:
            if Fineldistance[self.vertNumber.index(R)] != 0.0:
                pm.skinPercent(
                    self.meshCluster,
                    self.mesh + ".vtx[" + R + "]",
                    tv=(self.NewjntNam,
                        Fineldistance[self.vertNumber.index(R)]),
                )

    def deltaMush_skin_convert(self):
        """
        Restore the original skin weights on the mesh after deformer conversion.

        Use for Wire, Wrap, delta Mesh and Lattice

        """
        # print (self.Mesh_inf_jnts)
        # getData().check_connections(self.Mesh_inf_jnts)

        self.dupMesh = cmds.duplicate(self.mesh, n=self.mesh+"_Test")[0]

        meshSkinClust = [getData(object=self.mesh).get_skinCluster()]

        if not meshSkinClust:  # error if no skin
            pm.error("<<<<<(No SKIN found on mesh)>>>>>")

        # check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh + self.hold_jntSuffix) == False:
                pm.createNode("joint", n=self.mesh + self.hold_jntSuffix)

            pm.skinCluster(
                meshSkinClust[0], ai=self.mesh + self.hold_jntSuffix, edit=True, lw=0, wt=0)

        # get effected verticies
        self.vertNumber = [str(i) for i in range(
            cmds.polyEvaluate(self.mesh, v=True))]

        # Add all joints to skin cluster with dupMesh
        self.meshCluster = pm.skinCluster(self.Mesh_inf_jnts, self.dupMesh)
        cmds.select(cl=1)
        pm.skinCluster(self.meshCluster, ai=self.mesh +
                       self.hold_jntSuffix, edit=True, lw=0, wt=0)

        for xx in self.Mesh_inf_jnts:
            Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, xx)

            # skin apply
            for R in self.vertNumber:
                if Fineldistance[self.vertNumber.index(R)] != 0.0:
                    pm.skinPercent(
                        self.meshCluster,
                        self.dupMesh + ".vtx[" + R + "]",
                        tv=(xx, Fineldistance[self.vertNumber.index(R)]),
                    )

        for fv in self.Mesh_inf_jnts:
            pm.setAttr(fv + ".liw", 0)

        # copyWeight from dup mesh to main mesh
        cmds.connectAttr(self.meshCluster + ".weightList",
                         meshSkinClust[0].name() + ".weightList",)
        cmds.disconnectAttr(self.meshCluster + ".weightList",
                            meshSkinClust[0].name() + ".weightList",)
        cmds.delete(self.dupMesh, self.mesh + self.hold_jntSuffix)

        # TODO "error, 'only one joint' " softseletion convert, when other joint are unlocked, maybe it
        # should give error

        # deltaMush working with heirarchy, but there should not be any key (add error)
