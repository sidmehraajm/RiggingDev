import maya.OpenMaya as om, pymel.core as pm, maya.cmds as cmds
import time, math, sys

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

    # one defination for all
    def WhichDeformerButton(self, ddeformer):
        if ddeformer == "Wire":
            print("Converting wire deformer to skin")

        if ddeformer == "Lattice":
            print("Converting Lattice deformer to skin")

        if ddeformer == "Wrap":
            print("Converting Wrap deformer to skin")

        if ddeformer == "Cluster":
            print("Converting Cluster deformer to skin")

        if ddeformer == "SoftSelection":
            print("Converting SoftSelection deformer to skin")

        if ddeformer == "DeltaMesh":
            print("Converting DeltaMesh deformer to skin")

    def CreateCrv(self):
        cmds.curve(p=[cmds.xform(d, t=1, q=1, ws=1) for d in cmds.ls(sl=1)])

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
                elements.append([fnComp.element(i), fnComp.weight(i).influence()])
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
            #print (vert)
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

    def VertDistance(self, meshNam, VertNumList, moverNam):
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

        pm.move(1, moverNam + ".rotatePivot", y=True, r=True)

        for xyz in [0, 1, 2]:
            set_02Z = []

            for b in VertNumList:
                Attrs = pm.xform(meshNam + ".vtx[" + b + "]", q=True, ws=True, t=True)[
                    xyz
                ]

                set_02Z.append((Attrs))
            pm.select(d=True)

            New_PoseVert.append(set_02Z)

        pm.move(-1, moverNam + ".rotatePivot", y=True, r=True)

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

        return nodes[0]


    def NewJnt(self, positonN, MeshNam):
        cmds.select(d=True)
        objList = cmds.ls(MeshNam + "_*_Jnt")
        number = [int(i.split("_")[1]) for i in objList]
        
        nList = []
        for i in range(1, len(number)+2):
            if i not in number:
                nList.append(i)
                
        jntt = cmds.joint(n= MeshNam + "_" + str(nList[0]).zfill(3) + "_Jnt", p=positonN)
        cmds.select(d=True)
        return jntt


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
        inf_jnts (list): List of influenced joint names from the deformer.

    """

    def __init__(self, deformer=None, mesh=None):
        getData.__init__(self)
        self.deformer = deformer
        self.mesh = mesh
        self.hold_joint = None
        self.meshCluster = None
        self.vertNumber = []
        self.hold_skin_value = []
        self.inf_jnts = getData().get_influnced_joints(self.deformer)

    def deformer_skin_convert(self):
        """
        Convert skin weights from the deformer to the mesh.

        Use For Curve to Skin

        """
        # get mesh skin cluster
        self.meshCluster = getData(object=self.mesh).get_skinCluster()

        # check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh + "_HoldJnt") == False:
                self.hold_joint = pm.createNode("joint", n=self.mesh + "_HoldJnt")

            self.meshCluster = pm.skinCluster(self.hold_joint, self.mesh)
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
        for gfs in self.inf_jnts:
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

        for xx in self.inf_jnts:
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

        for fv in self.inf_jnts:
            pm.setAttr(fv + ".liw", 0)

        pm.skinCluster(self.meshCluster, e=True, ri=unlockJnt[0])

        # cleanup
        if self.meshCluster == []:
            pm.delete(unlockJnt[0])

        pm.disconnectAttr((cmds.listRelatives(self.deformer, shapes=True)[0])+".worldSpace[0]", wireDfm+".deformedWire[0]")
        pm.delete(wireDfm)
        pm.delete(self.deformer + "BaseWire")

    def rest_deformer_skin_convert(self):
        """
        Restore the original skin weights on the mesh after deformer conversion.

        Use for Wire, Wrap, delta Mesh and Lattice

        """

        deformerTyp = getData().deformerType(
            self.mesh
        )  # to check type of deformer and set wire rotation 1

        meshSkinClust = [getData(object=self.mesh).get_skinCluster()]

        deformerSkinClust = getData(object=self.deformer).get_skinCluster()

        if not deformerSkinClust:  # error if no skin
            pm.error("<<<<<(No SKIN found on deformer)>>>>>")

        if deformerSkinClust in meshSkinClust:  # reomve if same skincluster in mesh
            meshSkinClust.remove(deformerSkinClust)

        # check if there is a cluster else create a new one
        if self.meshCluster == None:
            if pm.objExists(self.mesh + "_HoldJnt") == False:
                self.hold_joint = pm.createNode("joint", n=self.mesh + "_HoldJnt")

            self.meshCluster = pm.skinCluster(self.hold_joint, self.mesh)
            cmds.select(cl=1)

        # get influnced joints of the mesh
        mesh_joints = pm.skinCluster(self.mesh, inf=True, q=True)

        # get effected verticies
        self.vertNumber = [str(i) for i in range(cmds.polyEvaluate(self.mesh, v=True))]

        # Add other joints to skin cluster

        pm.skinCluster(self.meshCluster, ai=self.inf_jnts, edit=True, lw=1, wt=0)

        for xx in self.inf_jnts:
            Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, xx)

            # skin apply
            for R in self.vertNumber:
                if Fineldistance[self.vertNumber.index(R)] != 0.0:
                    pm.skinPercent(
                        self.meshCluster,
                        self.mesh + ".vtx[" + R + "]",
                        tv=(xx, Fineldistance[self.vertNumber.index(R)]),
                    )

        for fv in self.inf_jnts:
            pm.setAttr(fv + ".liw", 0)

        # ---------------------------------------------------delete_Unwanted_Things

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
            if pm.objExists(self.mesh + "_HoldJnt") == False:
                self.hold_joint = pm.createNode("joint", n=self.mesh + "_HoldJnt")

            self.meshCluster = pm.skinCluster(self.hold_joint, self.mesh)
            cmds.select(cl=1)

        # get influnced joints of the mesh
        mesh_joints = pm.skinCluster(self.mesh, inf=True, q=True)

        # get unlocked joint to transfer deformer weight
        unlockJnt = getData().getUnlockedJnt(mesh_joints)

        self.vertNumber = getData().effectedVertNumber(self.meshCluster, unlockJnt)

        # Add other joints to skin cluster
        SoftJnt = []

        if cmds.objExists(self.mesh + "_001_Jnt") == True:
            jntNam = getData().NewJnt(positon, self.mesh)
            SoftJnt.append(jntNam)
            cmds.skinCluster(self.mesh, edit=True, ai=jntNam, lw=1, wt=0)
            cmds.select(d=True)

        if cmds.objExists(self.mesh + "_001_Jnt") == False:
            NwJnt = cmds.joint(n=self.mesh + "_001_Jnt", p=positon)
            SoftJnt.append(NwJnt)
            cmds.skinCluster(self.mesh, edit=True, ai=self.mesh + "_001_Jnt", lw=1, wt=0)

        cmds.select(sel)
        for i in utils().softSelection():
            cmds.select(d=1)

            pm.skinPercent(
                self.meshCluster,
                self.mesh + ".vtx[" + str(i[0]) + "]",
                tv=(SoftJnt[0], i[1]),
            )

            
    def ClusterConvert(self):

        sel = pm.ls(sl=True)
        positon = cmds.getAttr(sel[0]+'.origin')[0]





        # Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, xx)

        # TODO Cluster and Blendshape Function need to be added
        # TODO curve script not working with unlock a joint(solve it)
        # TODO get_influnced_joints not working for Wire1
        # just to remind myself:- self.variable bnane h har jgha
        # TODO you can call function with self.functionName also, but it should be inside the same class
        # TODO is there any alternate ?, ask to sid for "NewJnt" function.
