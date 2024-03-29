from otp.ai.AIBaseGlobal import *
from otp.avatar import DistributedAvatarAI
import SuitPlannerBase, SuitBase, SuitDNA
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import ToontownBattleGlobals

class DistributedSuitBaseAI(DistributedAvatarAI.DistributedAvatarAI, SuitBase.SuitBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuitBaseAI')

    def __init__(self, air, suitPlanner):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        SuitBase.SuitBase.__init__(self)
        self.sp = suitPlanner
        self.maxHP = 10
        self.currHP = 10
        self.zoneId = 0
        self.dna = None
        self.virtual = 0
        self.skeleRevives = 0
        self.maxSkeleRevives = 0
        self.executive = 0
        self.manager = 0
        self.reviveFlag = 0
        self.buildingHeight = None
        return

    def generate(self):
        DistributedAvatarAI.DistributedAvatarAI.generate(self)

    def delete(self):
        self.sp = None
        del self.dna
        DistributedAvatarAI.DistributedAvatarAI.delete(self)
        return

    def requestRemoval(self):
        if self.sp != None:
            self.sp.removeSuit(self)
        else:
            self.requestDelete()
        return

    def setLevel(self, lvl=None):
        attributes = SuitBattleGlobals.SuitAttributes[self.dna.name]
        if attributes['level'] < 8: # IF NORMAL COG
            if lvl:
                self.level = lvl - attributes['level'] - 1
            else:
                self.level = SuitBattleGlobals.pickFromFreqList(attributes['freq'])
            if lvl > attributes['level'] + len(attributes['hp']):
                self.level = len(attributes['hp']) - 1
            self.notify.debug('Assigning level ' + str(lvl))
            if hasattr(self, 'doId'):
                self.d_setLevelDist(self.level)
            hp = attributes['hp'][self.level]
            self.maxHP = hp
            self.currHP = hp
        else:
            if self.dna.name == 'ssb':
                self.level = lvl
            else:
                self.level = attributes['level'] # don't subtract 1, assume the level is as-is from battleglobals
            self.notify.debug('Assigning level to non-normal cog ' + str(self.level))
            if hasattr(self, 'doId'):
                self.d_setLevelDist(self.level)      
            if self.dna.name == 'ssb':
                if self.level > 49:
                    hp = hp = attributes['hp'][49]
                else:
                    hp = attributes['hp'][self.level]
            else:
                hp = attributes['hp'][0]
            self.maxHP = hp
            self.currHP = hp     

    def getLevelDist(self):
        return self.getLevel()

    def d_setLevelDist(self, level):
        self.sendUpdate('setLevelDist', [level])

    def setupSuitDNA(self, level, type, track):
        dna = SuitDNA.SuitDNA()
        dna.newSuitRandom(type, track)
        self.dna = dna
        self.track = track
        self.setLevel(level)
        return None

    def getDNAString(self):
        if self.dna:
            return self.dna.makeNetString()
        else:
            self.notify.debug('No dna has been created for suit %d!' % self.getDoId())
            return ''

    def b_setBrushOff(self, index):
        self.setBrushOff(index)
        self.d_setBrushOff(index)
        return None

    def d_setBrushOff(self, index):
        self.sendUpdate('setBrushOff', [index])

    def setBrushOff(self, index):
        pass

    def d_denyBattle(self, toonId):
        self.sendUpdateToAvatarId(toonId, 'denyBattle', [])

    def b_setExecutive(self, executive):
        if executive == None:
            executive = 0
        self.setExecutive(executive)
        self.d_setExecutive(self.getExecutive())

    def d_setExecutive(self, executive):
        self.sendUpdate('setExecutive', [executive])

    def getExecutive(self):
        return self.executive

    def setExecutive(self, executive):
        if executive == None:
            executive = 0
        self.executive = executive
        if self.executive:
            self.maxHP = int(self.maxHP * ToontownBattleGlobals.EXECUTIVE_HP_MULT)
            self.currHP = self.maxHP

    def b_setManager(self, manager):
        if manager == None:
            manager = 0
        self.setManager(manager)
        self.d_setManager(self.getManager())

    def d_setManager(self, manager):
        self.sendUpdate('setManager', [manager])
    
    def getManager(self):
        return self.manager

    def setManager(self, manager):
        if manager == None:
            manager = 0
        self.manager = manager

    def b_setSkeleRevives(self, num):
        if num == None:
            num = 0
        self.setSkeleRevives(num)
        self.d_setSkeleRevives(self.getSkeleRevives())
        return

    def d_setSkeleRevives(self, num):
        self.sendUpdate('setSkeleRevives', [num])

    def getSkeleRevives(self):
        return self.skeleRevives

    def setSkeleRevives(self, num):
        if num == None:
            num = 0
        self.skeleRevives = num
        if num > self.maxSkeleRevives:
            self.maxSkeleRevives = num
        return

    def getMaxSkeleRevives(self):
        return self.maxSkeleRevives

    def useSkeleRevive(self):
        self.skeleRevives -= 1
        halfMaxHP = int(self.getMaxHealth() / 2)
        self.b_setMaxHp(halfMaxHP)
        self.b_setHP(halfMaxHP)
        self.maxHP = halfMaxHP
        self.currHP = halfMaxHP
        self.reviveFlag = 1

    def reviveCheckAndClear(self):
        returnValue = 0
        if self.reviveFlag == 1:
            returnValue = 1
            self.reviveFlag = 0
        return returnValue

    def getHP(self):
        return self.currHP

    def setHP(self, hp):
        self.currHP = hp

    def getMaxHP(self):
        return self.maxHP

    def setMaxHp(self, maxHp):
        self.maxHP = maxHp

    def b_setHP(self, hp):
        self.setHP(hp)
        self.d_setHP(hp)

    def d_setHP(self, hp):
        self.sendUpdate('setHP', [hp])

    def releaseControl(self):
        return None

    def getDeathEvent(self):
        return 'cogDead-%s' % self.doId

    def resume(self):
        self.notify.debug('resume, hp=%s' % self.currHP)
        if self.currHP <= 0:
            messenger.send(self.getDeathEvent())
            self.requestRemoval()
        return None

    def prepareToJoinBattle(self):
        pass

    def b_setSkelecog(self, flag):
        self.setSkelecog(flag)
        self.d_setSkelecog(flag)

    def setSkelecog(self, flag):
        SuitBase.SuitBase.setSkelecog(self, flag)

    def d_setSkelecog(self, flag):
        self.sendUpdate('setSkelecog', [flag])

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return 0

    def setVirtual(self, virtual):
        pass

    def getVirtual(self):
        return 0

    def isVirtual(self):
        return self.getVirtual()
