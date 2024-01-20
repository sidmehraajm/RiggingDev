import maya.cmds as cmds
import pymel.core as pm
import sys
import time
import maya.OpenMaya as om
import math


###############################################
#Module
###############################################



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






###############################################
#Transform
###############################################


class JointProc:
    import pymel.core as pm

    cmdsSel = None
    sel = None

    def __init__(self):
        self.sel = pm.ls(sl=1)

    def getSelection(self, Pivs=cmdsSel):
        components = Pivs
        selList = []
        objName = components[0][0 : components[0].index(".")]
        # go through every component in the list. If it is a single component ("pCube1.vtx[1]"), add it to the list. Else,
        # add each component in the index ("pCube1.vtx[1:5]") to the list
        for c in components:
            if ":" not in c:
                selList.append(c)
            else:
                startComponent = int(c[c.index("[") + 1 : c.index(":")])
                endComponent = int(c[c.index(":") + 1 : c.index("]")])
                componentType = c[c.index(".") + 1 : c.index("[")]
                while startComponent <= endComponent:
                    selList.append(
                        objName + "." + componentType + "[" + str(startComponent) + "]"
                    )
                    startComponent += 1

        return selList
        pivsList.append(selList)

    def CtrJnt(self, Piv=sel):
        # createJoint

        sl = Piv
        try:
            pm.select(sl)
            tempPos = pm.cluster(n="Temp")[1]
            Jnt = pm.createNode("joint", n=(sl[0] + "Jnt"))
            pm.delete(pm.parentConstraint(tempPos, Jnt))
            pm.delete(tempPos)
            return Jnt

        except:
            tempPos = pm.createNode("transform", n="Temp")
            pm.delete(pm.parentConstraint(sl, tempPos))
            Jnt = pm.createNode("joint", n=(sl[0] + "_Jnt"))
            pm.delete(pm.parentConstraint(tempPos, Jnt))
            pm.delete(tempPos)
            return Jnt

    def CtrJntEach(self, cmdsSel=None):
        # createJoint
        try:
            sl = getSelection()
            print(sl)

        except:
            sl = cmdsSel
            print(sl)

        jnts_tr = []
        for i in sl:
            pass
            if pm.objectType(i) == "mesh":
                try:
                    pm.select(i)
                    tempPos = pm.cluster(n="Temp")[1]
                    Jnt = pm.createNode("joint", n=(i + "Jnt"))
                    pm.delete(pm.parentConstraint(tempPos, Jnt))
                    pm.delete(tempPos)
                    print(Jnt)

                except:
                    tempPos = pm.createNode("transform", n="Temp")
                    pm.delete(pm.parentConstraint(i, tempPos))
                    Jnt = pm.createNode("joint", n=(i + "_Jnt"))
                    pm.delete(pm.parentConstraint(tempPos, Jnt))
                    pm.delete(tempPos)
                    print(Jnt)
            else:
                pm.select(i)
                tempPos = pm.cluster(n="Temp")[1]
                Jnt = pm.createNode("joint", n=(i + "Jnt"))
                pm.delete(pm.parentConstraint(tempPos, Jnt))
                pm.delete(tempPos)
                print(Jnt)

    def transfroms_to_curve(self, cmdsSel=None):
        p = []
        trs = cmdsSel
        for i in trs:
            mtx = i.worldMatrix.get()
            tr = mtx.translate.get()
            p.append(tr)
        crv = pm.curve(d=3, p=p)





#########################################
#UI
#########################################

# window
win_name = "vn_skin_tools"
win_title = "VN Skin Tools"
win_size = (330, 290)
if pm.window(win_name, q=1, exists=True):
    pm.deleteUI(win_name, window=True)

"""
if pm.windowPref(win_name,q=1 ,exists=True ):
   pm.windowPref(win_name, r=0 )
"""
pm.window(
    win_name,
    title=win_title,
    widthHeight=win_size,
    sizeable=False,
    bgc=[(0.2), (0.2), (0.2)],
)

Tab = pm.tabLayout("Tabs", p=win_name, tc=0, stb=1, snt=0)

deformer_form = pm.formLayout("Converter", parent="Tabs")
skin_utils_form = pm.formLayout("Import/Export", en=0, vis=0)
utils_form = pm.formLayout("Utilities", parent="Tabs")
about_form = pm.formLayout("About", parent="Tabs")

# output_win_frame = pm.formLayout("MirrorWeights", parent="Tabs")


radio_layout = pm.rowColumnLayout(nc=2, p=deformer_form, cal=[2, "left"], h=55)
radio_coll = pm.radioCollection(parent=radio_layout)
crv_to_skn_btn = pm.radioButton(
    "crv_skn_rb", l="Curve To Skin", p=radio_layout, sl=1, cc="crv_skn_cc()"
)
softsel_to_skn = pm.radioButton(
    "softsel_skn_rb", l="Soft Selection To Skin", p=radio_layout, cc="softSel_skn_cc()"
)
cluster_to_skn = pm.radioButton(
    "cls_skn_rb", l="Cluster To Skin", p=radio_layout, cc="cl_skn_cc()"
)
df_to_skn_btn = pm.radioButton(
    "restdf_skn_rb", l="Wire/Wrap/Lattice", p=radio_layout, cc="df_skn_cc()"
)  # /DeltaMush
blendshape_to_skn = pm.radioButton(
    "bs_skn_rb", l="Blendshape To Skin", cc="blend_to_skin_cc()", p=radio_layout
)

blocking_to_skin = pm.radioButton(
    "smooth_skn_rb",
    l="Blocking to Smooth Skin",
    cc="delta_to_skin_cc()",
    p=radio_layout,
)

informatipn_txt_f = pm.textField(
    "info_txtf",
    w=180,
    h=25,
    p=deformer_form,
    en=0,
    pht="Add a Skinned Curve and Mesh",
    nbg=1,
)

mesh_textfield = pm.textField(
    "mesh_field", w=180, h=35, pht="Add Mesh", p=deformer_form
)
deformer_textfield = pm.textField(
    "df_field", w=180, h=35, pht="Add Skinned Curve", p=deformer_form
)


add_mesh_btn = pm.button(
    "mesh_btn", l="Select Mesh", p=deformer_form, w=120, h=34, c="mesh_add()"
)
add_df_btn = pm.button(
    "df_btn", l="Select Deformer", p=deformer_form, w=120, h=34, c="deformer_add()"
)
convert_btn = pm.iconTextButton(
    "cvt_btn",
    style="iconAndTextHorizontal",
    image1="polyColorSetEditor.png",
    label="Convert to Skin",
    p=deformer_form,
    w=130,
    h=40,
    bgc=[(0.33), (0.33), (0.353)],
    c="convert_to_skin()",
)
time_elapsed_txf = pm.textField(
    "time_txtf",
    w=80,
    h=25,
    p=deformer_form,
    en=0,
    pht="Time Elapsed: ",
    nbg=1,
)

pm.formLayout(
    deformer_form,
    e=1,
    attachForm=[
        (radio_layout, "top", 10),
        (informatipn_txt_f, "top", 67),
        (mesh_textfield, "top", 97),
        (deformer_textfield, "top", 135),
        (add_mesh_btn, "top", 98),
        (add_df_btn, "top", 136),
        (time_elapsed_txf, "top", 235),
        (convert_btn, "top", 190),
        (informatipn_txt_f, "left", 10),
        (radio_layout, "left", 10),
        (mesh_textfield, "left", 10),
        (deformer_textfield, "left", 10),
        (time_elapsed_txf, "left", 90),
        (convert_btn, "left", 95),
        (informatipn_txt_f, "right", 10),
        (add_mesh_btn, "right", 10),
        (add_df_btn, "right", 10),
        (time_elapsed_txf, "right", 50),
    ],
)

skinCLusterName = pm.scrollField(
    "skn_cl_name",
    w=300,
    h=30,
    p=skin_utils_form,
    bgc=[(0.17), (0.18), (0.19)],
    editable=True,
    wordWrap=False,
)
selc_mesh_btn = pm.button(
    "select_mesh",
    l="1. Select Mesh",
    p=skin_utils_form,
    w=150,
    h=30,
    bgc=[(0.2), (0.2), (0.2)],
    en=1,
)
rename_skn_btn = pm.button(
    "rename_skn",
    l="2. Rename SkinC",
    p=skin_utils_form,
    w=150,
    h=30,
    bgc=[(0.2), (0.2), (0.2)],
    en=1,
)

path_textfield = pm.textField(
    "df_field",
    w=180,
    h=41,
    pht="Add Deformer",
    p=skin_utils_form,
    bgc=[(0.17), (0.18), (0.19)],
)
selectPath_button = pm.iconTextButton(
    "df_btn",
    style="iconAndTextHorizontal",
    l="Select path",
    p=skin_utils_form,
    w=120,
    h=40,
    bgc=[(0.2), (0.2), (0.2)],
    en=1,
)

import_skn_button = pm.iconTextButton(
    "imp_skn",
    style="iconAndTextHorizontal",
    l="Import Deformer",
    p=skin_utils_form,
    w=150,
    h=40,
    bgc=[(0.2), (0.2), (0.2)],
    en=1,
)
export_skn_button = pm.iconTextButton(
    "exp_skn ",
    style="iconAndTextHorizontal",
    l="Export Deformer",
    p=skin_utils_form,
    w=150,
    h=40,
    bgc=[(0.2), (0.2), (0.2)],
    en=1,
)

pm.formLayout(
    skin_utils_form,
    e=1,
    attachForm=[
        (skinCLusterName, "top", 10),
        (selc_mesh_btn, "top", 45),
        (rename_skn_btn, "top", 45),
        (import_skn_button, "top", 125),
        (export_skn_button, "top", 125),
        (path_textfield, "top", 80),
        (selectPath_button, "top", 80),
        (path_textfield, "left", 10),
        (skinCLusterName, "left", 10),
        (import_skn_button, "left", 11),
        (selc_mesh_btn, "left", 11),
        (rename_skn_btn, "right", 11),
        (selectPath_button, "right", 10),
        (export_skn_button, "right", 10),
    ],
)

jnt_btwn_btn = pm.button(
    "jnt_btwn_btn",
    l="Joint at Center",
    p=utils_form,
    w=290,
    h=50,
    bgc=[(0.2), (0.21), (0.2)],
    en=1,
    c="jnt_btwn()",
)
jnt_each_btn = pm.button(
    "jnt_each_btn",
    l="Joint at each selection (Supports Mesh)",
    p=utils_form,
    w=290,
    h=50,
    bgc=[(0.2), (0.21), (0.2)],
    en=1,
    c="jnt_each()",
)
tr_to_crv_btn = pm.button(
    "tr_to_crv_btn",
    l="Transfrom to Curve",
    p=utils_form,
    w=290,
    h=50,
    bgc=[(0.2), (0.21), (0.2)],
    en=1,
    c="tr_crv()",
)
pm.formLayout(
    utils_form,
    e=1,
    attachForm=[
        (jnt_btwn_btn, "top", 10),
        (jnt_each_btn, "top", 69),
        (tr_to_crv_btn, "top", 130),
        (jnt_btwn_btn, "left", 10),
        (jnt_each_btn, "left", 10),
        (tr_to_crv_btn, "left", 10),
        (jnt_btwn_btn, "right", 10),
        (jnt_each_btn, "right", 10),
        (tr_to_crv_btn, "right", 10),
    ],
)
about_txf = pm.button(
    "about_txf",
    w=290,
    h=50,
    l="Authors:\nVishal Nagpal\nSiddarth Mehra",
    p=about_form,
    en=1,
    bgc=[0.5, 0.7, 0.7],
    c="pm.launch(web='https://www.linkedin.com/in/vishal-nagpal-82975a149/')",
)
link_btnSid = pm.button(
    "lnkSid",
    w=290,
    h=25,
    l="LinkedIn(Siddarth)",
    p=about_form,
    en=1,
    bgc=[0.2, 0.4, 0.76],
    c="pm.launch(web='https://www.linkedin.com/in/siddarthmehraajm/')",
)

link_btnVish = pm.button(
    "lnkVish",
    w=290,
    h=25,
    l="LinkedIn(Vishal)",
    p=about_form,
    en=1,
    bgc=[0.2, 0.4, 0.76],
    c="pm.launch(web='https://www.linkedin.com/in/vishal-nagpal-82975a149/')",
)

how_to_btn = pm.button(
    "how_to_btn",
    w=290,
    h=50,
    l="How to Use This Tool (Youtube Demo)",
    p=about_form,
    en=1,
    bgc=[0.6, 0.12, 0.12],
    c="pm.launch(web='https://youtu.be/wTVYchvHAuU/')",
)


pm.formLayout(
    about_form,
    e=1,
    attachForm=[
        (about_txf, "top", 10),
        (link_btnVish, "top", 97),
        (link_btnSid, "top", 67),
        (how_to_btn, "top", 130),
        (about_txf, "left", 10),
        (link_btnVish, "left", 10),
        (link_btnSid, "left", 10),
        (how_to_btn, "left", 10),
        (about_txf, "right", 10),
        (link_btnVish, "right", 10),
        (link_btnSid, "right", 10),
        (how_to_btn, "right", 10),
    ],
)


pm.showWindow(win_name)


# radio button change
def crv_skn_cc():
    pm.button(add_mesh_btn, e=1, en=1)
    pm.button(add_df_btn, e=1, en=1)
    pm.textField(mesh_textfield, e=1, en=1, pht="Add Mesh")
    pm.textField(deformer_textfield, e=1, en=1, pht="Add Skinned Curve")
    pm.textField(
        informatipn_txt_f, e=1, ed=0, nbg=1, pht="Add a Skinned Curve and Mesh"
    )


def softSel_skn_cc():
    pm.button(add_mesh_btn, e=1, en=0)
    pm.button(add_df_btn, e=1, en=0)
    pm.textField(mesh_textfield, e=1, en=0, pht=" ")
    pm.textField(deformer_textfield, e=1, en=0, pht=" ")
    pm.textField(
        informatipn_txt_f,
        e=1,
        ed=0,
        nbg=1,
        pht="Select Verticies/Face with soft selection",
    )


def cl_skn_cc():
    pm.button(add_mesh_btn, e=1, en=1)
    pm.button(add_df_btn, e=1, en=1)
    pm.textField(mesh_textfield, e=1, en=1, pht="Add Mesh")
    pm.textField(deformer_textfield, e=1, en=1, pht="Add Cluster")
    pm.textField(informatipn_txt_f, e=1, ed=0, nbg=1, pht="Add a Cluster and Mesh")


def df_skn_cc():
    pm.button(add_mesh_btn, e=1, en=1)
    pm.button(add_df_btn, e=1, en=1)
    pm.textField(mesh_textfield, e=1, en=1, pht="Add Mesh")
    pm.textField(deformer_textfield, e=1, en=1, pht="Add Deformer")
    pm.textField(
        informatipn_txt_f,
        e=1,
        ed=0,
        nbg=1,
        pht="Add Wire/Wrap/Lattice/DeltaMush and a Mesh",
    )


def delta_to_skin_cc():
    pm.button(add_mesh_btn, e=1, en=1)
    pm.button(add_df_btn, e=1, en=0)
    pm.textField(mesh_textfield, e=1, en=1, pht=" ")
    pm.textField(deformer_textfield, e=1, en=0, pht=" ")
    pm.textField(
        informatipn_txt_f,
        e=1,
        ed=0,
        nbg=1,
        pht="Add delta mush, delete delta after conversion",
    )


def blend_to_skin_cc():
    pm.button(add_mesh_btn, e=1, en=1)
    pm.button(add_df_btn, e=1, en=0)
    pm.textField(mesh_textfield, e=1, en=1, pht=" ")
    pm.textField(deformer_textfield, e=1, en=0, pht=" ")
    pm.textField(
        informatipn_txt_f,
        e=1,
        ed=0,
        nbg=1,
        pht="Select mesh with BS, first bs will be converted",
    )


# convert functions


class con_to_skn:
    def __init__(self):
        self.msh = None
        self.defr = None

    def add_mesh(self):
        try:
            Mymsh = str(pm.ls(sl=1)[0])
            if pm.objectType(pm.ls(pm.listHistory(Mymsh), typ="mesh")[0]) == "mesh":
                pm.textField("mesh_field", e=1, tx=Mymsh)
                self.msh = Mymsh
                return self.msh

        except:
            pm.error("Please select a Mesh")

    def add_deformer(self):
        try:
            Mydefr = str(pm.ls(sl=1)[0])
            option_functions = {
                "crv_skn_rb": "curve",
                "softsel_skn_rb": "soft",
                "restdf_skn_rb": "rest",
                "cls_skn_rb": "cluster",
                "bs_skn_rb": "blend",
                "smooth_skn_rb": "delta",
            }
            option = pm.radioCollection(radio_coll, q=1, sl=1)

            if option in option_functions:
                if option_functions[option] == "curve":
                    if (
                        pm.objectType(
                            pm.ls(pm.listHistory(Mydefr), typ="nurbsCurve")[0]
                        )
                        == "nurbsCurve"
                    ):
                        pm.textField("df_field", e=1, tx=Mydefr)
                        print(Mydefr)
                        self.defr = Mydefr
                        return self.defr
                elif option_functions[option] == "cluster":
                    if (
                        pm.objectType(
                            pm.ls(pm.listHistory(Mydefr), typ="clusterHandle")[0]
                        )
                        == "clusterHandle"
                    ):
                        pm.textField("df_field", e=1, tx=Mydefr)
                        print(Mydefr)
                        self.defr = Mydefr
                        return self.defr

                elif option_functions[option] == "soft":
                    pm.textField("df_field", e=1, tx=Mydefr)
                    self.defr = Mydefr
                    return self.defr

                elif option_functions[option] == "rest":
                    pm.textField("df_field", e=1, tx=Mydefr)
                    self.defr = Mydefr
                    return self.defr
                elif option_functions[option] == "delta":
                    pm.textField("df_field", e=1, tx=Mydefr)
                    self.defr = Mydefr
                    return self.defr
                elif option_functions[option] == "blend":
                    pm.textField("df_field", e=1, tx=Mydefr)
                    self.defr = Mydefr
                    return self.defr

        except:
            pm.error("Please select the correct Deformer/Node")



    def main_convert_to_skin(self):
        print(self.defr, self.msh)
        dc = deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.deformer_skin_convert()

    def rest_deformer(self):
        print(self.defr, self.msh)
        dc = deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.rest_deformer_skin_convert()

    def SoftSelection(self):
        dc = deformerConvert()
        dc.SoftSelectionToConvert()

    def convert_cluster(self):
        print(self.defr, self.msh)
        dc = deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.ClusterConvert()

    def delta_skin(self):
        print(self.defr, self.msh)
        dc = deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.deltaMush_skin_convert()

    def blend_skin(self):
        print(self.defr, self.msh)
        dc = deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.blendShapeConvert()


# button functions


def jnt_btwn():
    t = JointProc()
    t.CtrJnt(cmds.ls(sl=1))


def jnt_each():
    t = JointProc()
    t.CtrJntEach(cmds.ls(sl=1, fl=1))


def tr_crv():
    t = JointProc()
    t.transfroms_to_curve(pm.ls(sl=1))


con = con_to_skn()


def mesh_add():
    c = con.add_mesh()


def deformer_add():
    c = con.add_deformer()


def convert_to_skin():
    pm.textField(time_elapsed_txf, e=1, ed=0, nbg=1, pht="Time Elapsed:")
    start = time.time()
    option_functions = {
        "crv_skn_rb": con.main_convert_to_skin,
        "softsel_skn_rb": con.SoftSelection,
        "restdf_skn_rb": con.rest_deformer,
        "cls_skn_rb": con.convert_cluster,
        "smooth_skn_rb": con.delta_skin,
        "bs_skn_rb": con.blend_skin,
    }
    option = pm.radioCollection(radio_coll, q=1, sl=1)

    if option in option_functions:
        c = option_functions[option]()
    else:
        print("Option is wip")
    end = time.time()
    pm.textField(
        time_elapsed_txf,
        e=1,
        ed=0,
        nbg=1,
        pht="Time Elapsed:%d seconds" % (end - start),
    )
    print("Total time elapsed_%d" % (end - start))
