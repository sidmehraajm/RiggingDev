import maya.cmds as cmds
import pymel.core as pm
import importlib
import pymel.core as pm
import maya.cmds as cmds, pymel.core as pm, sys, importlib as imp
sys.path.append('/Users/siddarthmehraajm/Documents/GitHub/AutoRiggingFramework/RiggingDev/main')
import module as m
imp.reload(m)

import pymel.core as pm
win_name = 'vn_skin_tools'
win_title = 'Skin Tools'
win_size = (330,300)
if(pm.window(win_name,q=1, exists=True)):
    pm.deleteUI(win_name, window=True)
    
'''
if pm.windowPref(win_name,q=1 ,exists=True ):
   pm.windowPref(win_name, r=0 )
'''
pm.window(win_name, title=win_title, widthHeight=win_size, sizeable=False)

Tab = pm.tabLayout('Tabs',p=win_name,tc =0,stb=1,snt=1)

deformer_form = pm.formLayout('Converter',parent='Tabs')
skin_utils_form = pm.formLayout('Import/Export',parent='Tabs')
output_win_frame = pm.formLayout('MirrorWeights',parent='Tabs')
          

radio_layout = pm.rowColumnLayout(nc =2,p = deformer_form,cal =[2,'center'], h = 50)
radio_coll = pm.radioCollection( parent=radio_layout )
crv_to_skn_btn = pm.radioButton(l = 'Curve To Skin', p = radio_layout,sl =1)
wire_to_skn_btn= pm.radioButton(l = 'Wire To Skin', p = radio_layout,al ='center')
softsel_to_skn = pm.radioButton(l = 'Soft Selection To Skin', p = radio_layout)
lat_to_skn_btn = pm.radioButton(l = 'Lattice To Skin', p = radio_layout)
wrap_to_skn = pm.radioButton(l = 'Wrap To Skin', p = radio_layout)
blendshape_to_skn = pm.radioButton(l = 'Blendshape To Skin', p = radio_layout)
cluster_to_skn = pm.radioButton(l = 'Cluster To Skin', p = radio_layout)

mesh_textfield = pm.textField('mesh_field', w = 180 , h=42 ,pht = 'Add Mesh',p = deformer_form,bgc = [(.17),(.18),(.19)])
deformer_textfield = pm.textField('df_field', w = 180 , h=41 ,pht = 'Add Deformer',p = deformer_form,bgc = [(.17),(.18),(.19)])

override_checkbox = pm.checkBox( label='Override Skin Cluster', align='left', p = deformer_form )
unlocedvtx_checkbox = pm.checkBox( label='Unlocked Influneces Only', align='center', p = deformer_form )


add_mesh_btn = pm.iconTextButton('mesh_btn',style='iconAndTextHorizontal',image1='addClip.png',l = '   Select Mesh',p = deformer_form,w = 120,h=40, bgc = [(.2),(.2),(.2)],en = 1)
add_df_btn = pm.iconTextButton('df_btn',style='iconAndTextHorizontal',image1='addClip.png',l = 'Select Deformer',p = deformer_form,w = 120,h=40, bgc = [(.2),(.2),(.2)],en = 1)
convert_btn = pm.iconTextButton('cvt_btn',style='iconAndTextHorizontal', image1='polyColorSetEditor.png', label='Convert to Skin',p = deformer_form,w=130,h=40, bgc = [(.4),(.43),(.45)])

pm.formLayout(deformer_form,e=1,
	attachForm = [

	(radio_layout,'top',15),
	(mesh_textfield,'top',85),
	(deformer_textfield,'top',130),
	(add_mesh_btn,'top',86),
	(add_df_btn,'top',131),
	(override_checkbox,'top',180),
	(unlocedvtx_checkbox,'top',200),	
	(convert_btn,'top',228),

	(radio_layout,'left',10),	
	(mesh_textfield,'left',10),
	(deformer_textfield,'left',10),
	(override_checkbox,'left',11),
	(unlocedvtx_checkbox,'left',11),
	(convert_btn,'left',95),

	(add_mesh_btn,'right',10),
	(add_df_btn,'right',10),
	
	])

skinCLusterName = pm.scrollField('skn_cl_name', w = 300 , h=30 ,p = skin_utils_form,bgc = [(.17),(.18),(.19)],editable=True, wordWrap=False,)
selc_mesh_btn = pm.button('select_mesh',l = '1. Select Mesh',p = skin_utils_form,w = 150,h=30, bgc = [(.2),(.2),(.2)],en = 1)
rename_skn_btn = pm.button('rename_skn',l = '2. Rename SkinC',p = skin_utils_form,w = 150,h=30, bgc = [(.2),(.2),(.2)],en = 1)

path_textfield = pm.textField('df_field', w = 180 , h=41 ,pht = 'Add Deformer',p = skin_utils_form,bgc = [(.17),(.18),(.19)])

selectPath_button = pm.iconTextButton('df_btn',style='iconAndTextHorizontal',image1='addClip.png',l = 'Select path',p = skin_utils_form,w = 120,h=40, bgc = [(.2),(.2),(.2)],en = 1)

import_skn_button = pm.iconTextButton('imp_skn',style='iconAndTextHorizontal',image1='addClip.png',l = 'Import Deformer',p = skin_utils_form,w = 150,h=40, bgc = [(.2),(.2),(.2)],en = 1)
export_skn_button = pm.iconTextButton('exp_skn ',style='iconAndTextHorizontal',image1='addClip.png',l = 'Export Deformer',p = skin_utils_form,w = 150,h=40, bgc = [(.2),(.2),(.2)],en = 1)

pm.formLayout(skin_utils_form,e=1,
	attachForm = [
	(skinCLusterName,'top',10),
	(selc_mesh_btn,'top',45),
	(rename_skn_btn,'top',45),
	(import_skn_button,'top',125),
	(export_skn_button,'top',125),
	(path_textfield,'top',80),
	(selectPath_button,'top',80),	

	(path_textfield,'left',10),
	(skinCLusterName,'left',10),
	(import_skn_button,'left',11),	
	(selc_mesh_btn,'left',11),
	
	(rename_skn_btn,'right',11),
	(selectPath_button,'right',10),
	(export_skn_button,'right',10),
	
	
	])


pm.showWindow(win_name)

class con_to_skn:
    def __init__(self):
        self.msh = None
        self.defr = None
        
    def add_mesh(self):
        try:
            self.msh = str(pm.ls(sl=1)[0])
            pm.textField('mesh_field', e=1,tx=self.msh)
            return self.msh
            
        except:
            pm.error('Please select a Mesh')
            
        
            
    def add_deformer(self):
        try:
            self.defr = str(pm.ls(sl=1)[0])
            pm.textField('df_field', e=1,tx=self.defr)
            print(self.defr)
            return self.defr
            
        except:
            pm.error('Please select a Mesh')
            
        
        
        #do we need a condition to see like if the right deformer is selected

    
    def convert_to_skin(self):
        print(self.defr,self.msh)
        dam  = m.deformerConvert(deformer =self.defr, mesh = self.msh)
        
a = con_to_skn()
c = a.add_mesh()
a.add_deformer()
a.convert_to_skin()

















