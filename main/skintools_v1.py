import maya.OpenMaya as om, pymel.core as pm, maya.cmds as cmds
import time, math, sys
import maya.cmds as cmds
import pymel.core as pm
import importlib
import pymel.core as pm
import maya.cmds as cmds
import pymel.core as pm
import sys
import importlib as imp
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
        crv = cmds.curve(p=[cmds.xform(d, t=1, q=1, ws=1) for d in cmds.ls(sl=1)])
        cmds.setAttr(crv+".dispCV", 1)
        #cmds.setAttr("curveShape1.overrideEnabled", 1)
        #cmds.setAttr("curveShape1.overrideColor", 5)
        # TODO should we really add this(create curve) if yes how ?

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

    def VertDistance(self, meshNam, VertNumList, moverNam, moveType = ".rotatePivot"):
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

        pm.move(1, moverNam + moveType, y=True, r=True)

        for xyz in [0, 1, 2]:
            set_02Z = []

            for b in VertNumList:
                Attrs = pm.xform(meshNam + ".vtx[" + b + "]", q=True, ws=True, t=True)[
                    xyz
                ]

                set_02Z.append((Attrs))
            pm.select(d=True)

            New_PoseVert.append(set_02Z)

        pm.move(-1, moverNam + moveType, y=True, r=True)

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
        self.NewjntNam = None

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

        # Add new joints to skin cluster

        if cmds.objExists(self.mesh + "_001_Jnt") == False:
            self.NewjntNam = cmds.joint(n=self.mesh + "_001_Jnt", p=positon)
            cmds.skinCluster(self.mesh, edit=True, ai=self.NewjntNam, lw=1, wt=0)
        else:
            self.NewjntNam = getData().NewJnt(positon, self.mesh)
            cmds.skinCluster(self.mesh, edit=True, ai=self.NewjntNam, lw=1, wt=0)

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
        cmds.select(d =True)

        clust = getData(object=self.mesh).get_skinCluster()

        if clust==None:
            if pm.objExists(self.mesh + "_HoldJnt") == False:
                pm.joint(n = self.mesh + "_HoldJnt")
                
            pm.skinCluster(self.mesh + "_HoldJnt", self.mesh)


        mesh_joints = pm.skinCluster(self.mesh, inf = True, q = True)
        #pm.setAttr(mesh_joints[0]+'.liw', 1)

        self.meshCluster = getData(object=self.mesh).get_skinCluster()

        # get effected verticies
        self.vertNumber = getData().effectedVertNumber(self.meshCluster, self.mesh + "_HoldJnt")

        Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, self.deformer, moveType = "")


        if pm.objExists(self.mesh + "_001_Jnt") == False:
            self.NewjntNam = cmds.joint(n = self.mesh + "_001_Jnt", p = positon)
            cmds.skinCluster(self.mesh, edit=True, ai=self.NewjntNam, lw=1, wt=0)
        else:
            self.NewjntNam = getData().NewJnt(positon, self.mesh)
            cmds.skinCluster(self.mesh, edit=True, ai=self.NewjntNam, lw=1, wt=0)

        # skin apply
        for R in self.vertNumber:
            if Fineldistance[self.vertNumber.index(R)] != 0.0:
                pm.skinPercent(
                    self.meshCluster,
                    self.mesh + ".vtx[" + R + "]",
                    tv=(self.NewjntNam, Fineldistance[self.vertNumber.index(R)]),
                )




        # Fineldistance = getData().VertDistance(self.mesh, self.vertNumber, xx)

        # TODO Cluster and Blendshape Function need to be added
        # TODO curve script not working with unlock a joint(solve it)
        # TODO get_influnced_joints not working for Wire1
        # just to remind myself:- self.variable bnane h har jgha
        # TODO you can call function with self.functionName also, but it should be inside the same class
        # TODO is there any alternate ?, ask to sid for "NewJnt" function.


# window
win_name = "vn_skin_tools"
win_title = "Skin Tools"
win_size = (330, 300)
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

Tab = pm.tabLayout("Tabs", p=win_name, tc=0, stb=1, snt=1)

deformer_form = pm.formLayout("Converter", parent="Tabs")
skin_utils_form = pm.formLayout("Import/Export", parent="Tabs")
output_win_frame = pm.formLayout("MirrorWeights", parent="Tabs")


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
    "restdf_skn_rb", l="Wire/Wrap/Lattice/DeltaMush", p=radio_layout, cc="df_skn_cc()"
)
blendshape_to_skn = pm.radioButton(
    "bs_skn_rb", l="Blendshape To Skin", p=radio_layout)

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

override_checkbox = pm.checkBox(
    label="Override Skin Cluster", align="left", p=deformer_form
)
unlocedvtx_checkbox = pm.checkBox(
    label="Unlocked Influneces Only", align="center", p=deformer_form
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
    bgc=[(0.23), (0.23), (0.253)],
    c="convert_to_skin()",
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
        (override_checkbox, "top", 180),
        (unlocedvtx_checkbox, "top", 200),
        (convert_btn, "top", 228),
        (informatipn_txt_f, "left", 10),
        (radio_layout, "left", 10),
        (mesh_textfield, "left", 10),
        (deformer_textfield, "left", 10),
        (override_checkbox, "left", 11),
        (unlocedvtx_checkbox, "left", 11),
        (convert_btn, "left", 95),
        (informatipn_txt_f, "right", 10),
        (add_mesh_btn, "right", 10),
        (add_df_btn, "right", 10),
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
    image1="addClip.png",
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
    image1="addClip.png",
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
    image1="addClip.png",
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
    pm.textField(informatipn_txt_f, e=1, ed=0,
                 nbg=1, pht="Add a Cluster and Mesh")


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


# convert functions
class con_to_skn:
    def __init__(self):
        self.msh = None
        self.defr = None

    def add_mesh(self):
        try:
            self.msh = str(pm.ls(sl=1)[0])
            if pm.objectType(pm.ls(pm.listHistory(self.msh), typ="mesh")[0]) == "mesh":
                pm.textField("mesh_field", e=1, tx=self.msh)
                return self.msh

        except:
            pm.error("Please select a Mesh")

    def add_deformer(self):
        try:
            self.defr = str(pm.ls(sl=1)[0])
            option_functions = {
                "crv_skn_rb": "curve",
                "softsel_skn_rb": "soft",
                "restdf_skn_rb": "rest",
                "cls_skn_rb": "cluster",
            }
            option = pm.radioCollection(radio_coll, q=1, sl=1)

            if option in option_functions:
                if option_functions[option] == "curve":
                    if (
                        pm.objectType(
                            pm.ls(pm.listHistory(self.defr),
                                  typ="nurbsCurve")[0]
                        )
                        == "nurbsCurve"
                    ):
                        pm.textField("df_field", e=1, tx=self.defr)
                        print(self.defr)
                        return self.defr

                elif option_functions[option] == "cluster":
                    if (
                        pm.objectType(
                            pm.ls(pm.listHistory(defr), typ="clusterHandle")[0]
                        )
                        == "clusterHandle"
                    ):
                        pm.textField("df_field", e=1, tx=self.defr)
                        print(self.defr)
                        return self.defr

                elif option_functions[option] == "soft":
                    pm.textField("df_field", e=1, tx=self.defr)
                    return self.defr

                elif option_functions[option] == "rest":
                    pm.textField("df_field", e=1, tx=self.defr)
                    return self.defr

        except:
            pm.error("Please select the correct deformer")

    def convert_to_skin(self):
        print(self.defr, self.msh)
        dc =deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.deformer_skin_convert()

    def rest_deformer(self):
        print(self.defr, self.msh)
        dc =deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.rest_deformer_skin_convert()

    def SoftSelection(self):
        print(self.defr, self.msh)
        dc =deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.SoftSelectionToConvert()

    def convert_cluster(self):
        print(self.defr, self.msh)
        dc =deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.ClusterConvert()


con = con_to_skn()


def mesh_add():
    c = con.add_mesh()


def deformer_add():
    c = con.add_deformer()


def convert_to_skin():
    option_functions = {
        "crv_skn_rb": con.convert_to_skin,
        "softsel_skn_rb": con.SoftSelection,
        "restdf_skn_rb": con.rest_deformer,
        "cls_skn_rb": con.convert_cluster,
    }
    option = pm.radioCollection(radio_coll, q=1, sl=1)

    if option in option_functions:
        c = option_functions[option]()
    else:
        print("Option is wip")
