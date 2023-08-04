import pymel.core as pm
import maya.cmds as cmds

'''

ui
query definations - selection check error
find data 
create curve from transforms
one defination for all deformer
skin cluster utils 
export/import- skin/deformers 
copy skin 
vertex weight slider
mirror deformer weight
'''

class find_data:
    '''
    TODO write doc
    '''
    def __init__(self,mesh):
        self.mesh = mesh

class vn_skin_utils:
    '''
    TODO write doc
    '''
    def __init__(self):
        self.holdjoint = '_hold_jnt'
        self.prefix = '_skn_tmp_jnt'

    def create_joint(self,pos):
        jnt = pm.createNode('joint')
        




    


