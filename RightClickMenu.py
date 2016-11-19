__author__ = 'tyoung'
from PygameWindowInfo import PygameWindowInfo
import pygame
from pygame.locals import *
import sys
from popup_menu import PopupMenu
font = pygame.font.Font(None, 10)
import re
from Background import Background
from Entity import Entity

import Tkinter, tkFileDialog, tkSimpleDialog
    #example
def rightClickMenu(x,y,target,model,camera,cached):
    menu_data=()
    if target:
        menu_data = (
            str(target.imgName),
            'Image',
            'Description',
            'Max Health',
            'Toggle Blocking',
            'Toggle Raw Scaling',
            'Toggle Wiggle',
            'Interaction',
            'Cycle Time',
            'Bind Joystick',
            'Send to Back',
        )
    else:
        menu_data = (
            ""+str(x)+','+str(y),
            (
                'New BlockLine',
                'Vertical BlockLine',
                'Horizontal BlockLine',
            ),
            'New NPC',
            'New Object',
            'New Background',
            (
                'New Sound',
                'Local Sound',
                'Global Sound',
            ),
            'Stopsound',
            'Redark',
            'Clear Blood',
            'Go To Area',
        )

    menu=PopupMenu(menu_data)
    callString = ""
    selection=menu.selection
    if len(selection)>0:
        callString=selection[0][1].text
        #callString=selection[0][0].name+ ':' + selection[0][1].text

    handleSelection(x,y,callString,target,model,camera,cached)
def getCharacterImage():
    pathparts= tkFileDialog.askopenfilename(filetypes=(("png", "*.png"),)).split('/')
    relativePathParts=pathparts[pathparts.index('maps'):]
    relativePathParts[-1]= re.sub('[P0-9]\.png','.png',relativePathParts[-1])
    wholePath='/'.join(relativePathParts)
    return wholePath

def getSound():
    pathparts= tkFileDialog.askopenfilename(filetypes=(("ogg", "*.ogg"),)).split('/')
    relativePathParts=pathparts[pathparts.index('maps'):]
    wholePath='/'.join(relativePathParts)
    return wholePath

def handleSelection(x,y,callString,target,model,camera,cached):
    try:
        ############   Targeted#############
        if callString == 'Toggle Blocking':
            target.blocking= not target.blocking
        if callString == 'Toggle Raw Scaling':
            target.rawScaling= not target.rawScaling
        if callString == 'Toggle Wiggle':
            target.wiggles= not target.wiggles
        if callString == 'Image':
            target.imgName=getCharacterImage()
        if callString == 'Description':
            newDesc = tkSimpleDialog.askstring(callString, "Enter Description", initialvalue=target.description)
            if newDesc:
                target.description = newDesc
        if callString == 'Max Health':
            target.maxHealth= tkSimpleDialog.askinteger(callString, "Enter max health (sets current to max)", initialvalue=target.maxHealth)
            target.hp=target.maxHealth
        if callString == 'Cycle Time':
            target.switchTime= tkSimpleDialog.askinteger(callString, "Enter number of frames between animation images", initialvalue=target.switchTime)
        if callString == 'Interaction':
            target.interactionString= tkSimpleDialog.askstring(callString, "Enter python interaction commands", initialvalue=target.interactionString)

        if callString == 'Send to Back':
            targetList=None
            if target in model.world.currentArea.backgrounds:
                targetList = model.world.currentArea.backgrounds
            elif target in model.world.currentArea.entities:
                targetList = model.world.currentArea.entities
            elif target in model.world.players:
                targetList = model.world.players
            if targetList:
                targetList.insert(-1, targetList.pop(targetList.index(target)))

        ########### Untargeted ##########

        if callString == 'New Background':
            model.world.currentArea.backgrounds.append(Background( getCharacterImage(), (x,y,1,1), False ))
        #if callString == 'New Area':
        #    model.world.setArea(tkSimpleDialog.askstring(callString, "Enter area name"),camera,model,cached, 0, 0)
        if callString == 'New Object':
            newEntity=Entity(getCharacterImage(), (int(x), int(y), 1, 1), 1,True, 100)
            newEntity.rawScaling=True
            newEntity.wiggles=False
            model.world.currentArea.entities.append(newEntity)
        if callString == 'New NPC':
            newEntity=Entity(getCharacterImage(), (int(x), int(y), 1, 1), tkSimpleDialog.askinteger(callString, "Ent new unit's max health"),True, 100)
            newEntity.rawScaling=False
            newEntity.wiggles=True
            model.world.currentArea.entities.append(newEntity)
        if callString == 'Vertical BlockLine':
            model.world.currentArea.addVerticalBlockLine((x,y,1,1))
        if callString == 'Horizontal BlockLine':
            model.world.currentArea.addHorizontalBlockLine((x,y,1,1))
        if callString == 'Global Sound':
            model.world.currentArea.soundManager.addBG(0,0,tkSimpleDialog.askfloat("Enter Volume", "Enter Volume (0.0 - 1.0)", initialvalue=1.0),False, getSound(),cached)
        if callString == 'Local Sound':
            model.world.currentArea.soundManager.addBG(x,y,tkSimpleDialog.askfloat("Enter Volume", "Enter Volume (0.0 - 1.0)", initialvalue=1.0),True, getSound(),cached)
        if callString == 'Go To Area':
            model.world.setArea(tkSimpleDialog.askstring(callString, "Enter area name"),camera,cached, 0, 0)
        if callString == 'Redark':
            for background in model.world.currentArea.backgrounds:
                background.FoW.redark()
            for player in model.world.players:
                model.world.reveal(player.rect[0],player.rect[1],camera,cached)
        if callString == 'Clear Blood':
            model.world.currentArea.blood=[]
        if callString == 'Stopsound':
            model.world.currentArea.soundManager.clearRunningAndStored(cached)
        if callString == 'Bind Joystick':
            camera.lookingForJoystickTarget=target
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            for joystick in joysticks:
                if not joystick.get_init():
                    joystick.init()
                #numButtons = joystick.get_numbuttons()
                #for i in range(numButtons):
                #     if joystick.get_button(i):
                #         return
    except Exception,e:
        print str(e)

    pass
