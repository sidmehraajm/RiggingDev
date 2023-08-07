import pymel.core as pm
win_name = 'vn_skin_tools'
win_title = 'Skin Tools'
win_size = (330,300)
if(pm.window(win_name,q=1, exists=True)):
    pm.deleteUI(win_name, window=True)
    
'''
if cmds.windowPref(win_name,q=1 ,exists=True ):
   cmds.windowPref(win_name, r=0 )
'''
pm.window(win_name, title=win_title, widthHeight=win_size, sizeable=False)

Tab = tabLayout('Tabs',p=win_name,tc =0,stb=1,snt=1)

deformer_form = pm.formLayout('Converter',parent='Tabs')
skin_utils_frame = pm.frameLayout('Export',parent='Tabs', label='Weights Import/Export', collapsable=True)  
output_win_frame = pm.frameLayout('Utils',parent='Tabs', label='Weights Mirror', collapsable=True) 
          

radio_layout = pm.rowColumnLayout(nc =2,p = deformer_form,cal =[2,'center'], h = 50)
radio_coll = pm.radioCollection( parent=radio_layout )
crv_to_skn_btn = cmds.radioButton(l = 'Curve To Skin', p = radio_layout,sl =1)
wire_to_skn_btn= cmds.radioButton(l = 'Wire To Skin', p = radio_layout,al ='center')
softsel_to_skn = cmds.radioButton(l = 'Soft Selection To Skin', p = radio_layout)
lat_to_skn_btn = cmds.radioButton(l = 'Lattice To Skin', p = radio_layout)
wrap_to_skn = cmds.radioButton(l = 'Wrap To Skin', p = radio_layout)
blendshape_to_skn = cmds.radioButton(l = 'Blendshape To Skin', p = radio_layout)
cluster_to_skn = cmds.radioButton(l = 'Cluster To Skin', p = radio_layout)

mesh_textfield = pm.textField('mesh_field', w = 180 , h=42 ,pht = 'Add Mesh',p = deformer_form,bgc = [(.17),(.18),(.19)])
deformer_textfield = pm.textField('df_field', w = 180 , h=41 ,pht = 'Add Deformer',p = deformer_form,bgc = [(.17),(.18),(.19)])

add_mesh_btn = pm.iconTextButton('mesh_btn',style='iconAndTextHorizontal',image1='addClip.png',l = 'Select Mesh',p = deformer_form,w = 120,h=40, bgc = [(.15),(.15),(.15)],en = 1)
add_df_btn = pm.iconTextButton('df_btn',style='iconAndTextHorizontal',image1='addClip.png',l = 'Select Deformer',p = deformer_form,w = 120,h=40, bgc = [(.15),(.15),(.15)],en = 1)
convert_btn = pm.iconTextButton('cvt_btn',style='iconAndTextHorizontal',image1='polyBakeSetNew.png',l = 'Convert to Skin',p = deformer_form,w = 150,h=40, bgc = [(.15),(.15),(.15)],en = 1, al ='center')

pm.formLayout(deformer_form,e=1,
	attachForm = [
	
	
	(radio_layout,'top',15),
	(mesh_textfield,'top',85),
	(deformer_textfield,'top',135),
	(add_mesh_btn,'top',86),
	(add_df_btn,'top',136),
	(convert_btn,'top',185),


	(radio_layout,'left',10),	
	(mesh_textfield,'left',10),
	(deformer_textfield,'left',10),

	(convert_btn,'left',75),

	
	(add_mesh_btn,'right',10),
	(add_df_btn,'right',10),
	
	])
	
pm.showWindow(win_name)













