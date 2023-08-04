#TODO conditions for deformers radio button change
import pymel.core as pm
win_name = 'vn_skin_tools'
win_title = 'Skin Tools'
win_size = (350,500)
if(pm.window(win_name, exists=True)):
    pm.deleteUI(win_name, window=True)
pm.window(win_name, title=win_title, widthHeight=win_size, sizeable=False)

main_form = pm.formLayout(numberOfDivisions=100)
deformer_frame = pm.frameLayout(parent=main_form, label='Deformer To Skin', collapsable=True)
skin_utils_frame = pm.frameLayout(parent=main_form, label='Weights Import/Export', collapsable=True)  
output_win_frame = pm.frameLayout(parent=main_form, label='Weights Mirror', collapsable=True) 
          
pm.formLayout(main_form, edit=True,
                attachForm=([deformer_frame, 'top', 0], [deformer_frame, 'left', 0], [deformer_frame, 'right', 0], [skin_utils_frame, 'left', 0], 
                [skin_utils_frame, 'right', 0], [output_win_frame, 'left', 0], [output_win_frame, 'right', 0]),
                attachControl=([skin_utils_frame, 'top', 10, deformer_frame], [output_win_frame, 'top', 10, skin_utils_frame]))
radio_layout = pm.rowColumnLayout(nc =3,p = deformer_frame)
radio_coll = pm.radioCollection( parent=radio_layout )
crv_to_skn_btn = cmds.radioButton(l = 'Curve To Skin', p = radio_layout,sl =1)
wire_to_skn_btn= cmds.radioButton(l = 'Wire To Skin', p = radio_layout)
softsel_to_skn = cmds.radioButton(l = 'Soft Selection To Skin', p = radio_layout)
lat_to_skn_btn = cmds.radioButton(l = 'Lattice To Skin', p = radio_layout)
wrap_to_skn = cmds.radioButton(l = 'Wrap To Skin', p = radio_layout)
blendshape_to_skn = cmds.radioButton(l = 'Blendshape To Skin', p = radio_layout)
cluster_to_skn = cmds.radioButton(l = 'Cluster To Skin', p = radio_layout)

    
pm.showWindow(win_name)
