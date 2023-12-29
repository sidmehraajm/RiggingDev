import pymel.core as pm
import maya.cmds as cmds


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
                tempPos = pm.createNode("transform", n="Temp")
                pm.delete(pm.parentConstraint(i, tempPos))
                Jnt = pm.createNode("joint", n=(i + "_Jnt"))
                pm.delete(pm.parentConstraint(tempPos, Jnt))
                pm.delete(tempPos)
                jnts_tr.append(Jnt)

    def transfroms_to_curve(self, cmdsSel=None):
        p = []
        trs = cmdsSel
        for i in trs:
            mtx = i.worldMatrix.get()
            tr = mtx.translate.get()
            p.append(tr)
        crv = pm.curve(d=3, p=p)
