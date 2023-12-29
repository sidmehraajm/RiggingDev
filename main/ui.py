import maya.cmds as cmds
import pymel.core as pm
import importlib
import pymel.core as pm
import maya.cmds as cmds
import pymel.core as pm
import sys
import importlib as imp

sys.path.append(
    "/Users/siddarthmehraajm/Documents/GitHub/AutoRiggingFramework/RiggingDev/main"
)
import transform as tr
import module as m

# window
win_name = "vn_skin_tools"
win_title = "VN Skin Tools"
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
    c="jnt_each()",
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
    l="UI Author: Siddarth Mehra \n Code Author: Vishal Nagpal " ,
    p=about_form,
    en=1,
    bgc=[0.5, 0.7, 0.7],
    c="pm.launch(web='https://www.linkedin.com/in/vishal-nagpal-82975a149/')",
)
link_btnVish = pm.button(
    "lnkVish",
    w=290,
    h=25,
    l="LinkedIn(Siddarth)",
    p=about_form,
    en=1,
    bgc=[0.2, 0.4, 0.76],
    c="pm.launch(web='https://www.linkedin.com/in/siddarthmehraajm/')",
)

link_btnSid = pm.button(
    "lnkSid",
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
    c="pm.launch(web='https://www.linkedin.com/in/vishal-nagpal-82975a149/')",
)


pm.formLayout(
    about_form,
    e=1,
    attachForm=[
        (about_txf, "top", 10),
        (link_btnSid, "top", 90),
        (link_btnVish, "top", 70),
        (how_to_btn, "top", 130),
        (about_txf, "left", 10),
        (link_btnSid, "left", 10),
        (link_btnVish, "left", 10),
        (how_to_btn, "left", 10),
        (about_txf, "right", 10),
        (link_btnSid, "right", 10),
        (link_btnVish, "right", 10),
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

    def convert_to_skin(self):
        print(self.defr, self.msh)
        dc = m.deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.deformer_skin_convert()

    def rest_deformer(self):
        print(self.defr, self.msh)
        dc = m.deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.rest_deformer_skin_convert()

    def SoftSelection(self):
        print(self.defr, self.msh)
        dc = m.deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.SoftSelectionToConvert()

    def convert_cluster(self):
        print(self.defr, self.msh)
        dc = m.deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.ClusterConvert()

    def delta_skin(self):
        print(self.defr, self.msh)
        dc = m.deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.deltaMush_skin_convert()

    def blend_skin(self):
        print(self.defr, self.msh)
        dc = m.deformerConvert(deformer=self.defr, mesh=self.msh)
        dc.blendShapeConvert()


# button functions


def jnt_btwn():
    t = tr.JointProc()
    t.CtrJnt(cmds.ls(sl=1))


def jnt_each():
    t = tr.JointProc()
    t.CtrJntEach(cmds.ls(sl=1, fl=1))


def jnt_each():
    t = tr.JointProc()
    t.transfroms_to_curve(pm.ls(sl=1))


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
        "smooth_skn_rb": con.delta_skin,
        "bs_skn_rb": con.blend_skin,
    }
    option = pm.radioCollection(radio_coll, q=1, sl=1)

    if option in option_functions:
        c = option_functions[option]()
    else:
        print("Option is wip")
