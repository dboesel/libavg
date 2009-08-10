#!/usr/bin/python
# -*- coding: utf-8 -*-
# libavg - Media Playback Engine.
# Copyright (C) 2003-2008 Ulrich von Zadow
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Current versions can be found at www.libavg.de
#

import unittest

import sys, platform

# Import the correct version of libavg. Since it should be possible to
# run the tests without installing libavg, we add the location of the 
# uninstalled libavg to the path.
# TODO: This is a mess. 
sys.path += ['../wrapper/.libs', '../python']
if platform.system() == 'Darwin':
    sys.path += ['../..']     # Location of libavg in a mac installation. 

if platform.system() == 'Windows':
    from libavg import avg    # Under windows, there is no uninstalled version.
else:
    import avg

from testcase import *

class AnimTestCase(AVGTestCase):
    def __init__(self, testFuncName):
        AVGTestCase.__init__(self, testFuncName, 24)
    def initScene(self):
        Player.loadString("""
            <avg width="160" height="120">
                <image id="test" x="64" y="30" href="rgb24-65x65.png"/>
            </avg>
        """)
        self.__node = Player.getElementByID("test")
        Player.setFakeFPS(10)

    def testAnimType(self, curAnim, imgBaseName):
        def onStop():
            self.__onStopCalled = True
        def startAnim():
            self.__onStopCalled = False
            self.__anim.start()
        def startKeepAttr():
            self.__node.x = 32 
            self.__anim.start(True)
        def abortAnim():
            self.__anim.abort()
        self.__anim = curAnim
        self.__anim.setStopCallback(onStop)
        self.__onStopCalled = False
        self.assertException(lambda: self.__anim.start())
        self.start(None,
                (startAnim,
                 lambda: self.compareImage(imgBaseName+"1", False),
                 lambda: self.compareImage(imgBaseName+"2", False),
                 lambda: self.compareImage(imgBaseName+"3", False),
                 lambda: self.assert_(self.__onStopCalled),
                 lambda: self.assert_(not(self.__anim.isRunning())),
                 lambda: self.assert_(avg.getNumRunningAnims() == 0),
                 lambda: self.compareImage(imgBaseName+"4", False),
                 lambda: self.assert_(self.__node.x == 100),
                 startAnim,
                 lambda: self.compareImage(imgBaseName+"1", False),
                 lambda: self.assert_(avg.getNumRunningAnims() == 1),
                 abortAnim,
                 lambda: self.assert_(avg.getNumRunningAnims() == 0),
                 lambda: self.compareImage(imgBaseName+"5", False),
                 lambda: self.assert_(not(self.__anim.isRunning())),
                 None,
                 lambda: self.assert_(self.__onStopCalled),
                 startAnim,
                 startKeepAttr,
                 lambda: self.compareImage(imgBaseName+"6", False),
                 lambda: self.assert_(avg.getNumRunningAnims() == 1)
                ))
        self.__anim = None

    def testLinearAnim(self):
        self.initScene()
        curAnim = avg.LinearAnim(self.__node, "x", 300, 0, 100)
        self.testAnimType(curAnim, "testLinearAnimC")

    def testFadeIn(self):
        def onStop():
            self.__onStopCalled = True
        self.initScene()
        self.__node.opacity=0.5
        self.__onStopCalled = False
        self.start(None,
                (lambda: avg.fadeIn(self.__node, 200, 1, onStop),
                 lambda: self.compareImage("testFadeIn1", False),
                 lambda: self.compareImage("testFadeIn2", False),
                 lambda: self.compareImage("testFadeIn3", False),
                 lambda: self.assert_(self.__onStopCalled),
                 lambda: self.assert_(avg.getNumRunningAnims() == 0)
                ))
        self.__anim = None

    def testFadeOut(self):
        def onStop():
            self.__onStopCalled = True
        self.initScene()
        self.__node.opacity=0.5
        self.__onStopCalled = False
        self.start(None,
                (lambda: avg.fadeOut(self.__node, 200, onStop),
                 lambda: self.compareImage("testFadeOut1", False),
                 lambda: self.compareImage("testFadeOut2", False),
                 lambda: self.compareImage("testFadeOut3", False),
                 lambda: self.assert_(self.__onStopCalled),
                 lambda: self.assert_(avg.getNumRunningAnims() == 0)
                ))
        self.__anim = None

    def testNonExistentAttributeAnim(self):
        self.initScene()
        self.assertException(lambda: avg.LinearAnim(self.__node, "foo", 0, 0, 0, False))
        self.assertException(lambda: avg.LinearAnim(None, "x", 0, 0, 0, False))

    def testLinearAnimZeroDuration(self):
        def onStop():
            self.__onStopCalled = True
        def startAnim():
            self.__onStopCalled = False
            self.__anim.start()
        self.initScene()
        self.__anim = avg.LinearAnim(self.__node, "x", 0, 0, 100, False, None, onStop)
        self.__onStopCalled = False
        self.start(None,
                (startAnim,
                 lambda: self.compareImage("testLinearAnimZeroDurationC1", False),
                 lambda: self.assert_(avg.getNumRunningAnims() == 0),
                 lambda: self.assert_(self.__onStopCalled),
                 lambda: self.assert_(not(self.__anim.isRunning()))
                ))
        self.__anim = None

    def testPointAnim(self):
        def startAnim():
            self.__anim.start()
        def startKeepAttr():
            self.__node.pos = (50, 20)
            self.__anim.start(True)
        self.initScene()
        self.__anim = avg.LinearAnim(self.__node, "pos", 200, avg.Point2D(0,0), 
                avg.Point2D(100,40), False)
        self.start(None,
                (startAnim,
                 lambda: self.compareImage("testPointAnim1", False),
                 lambda: self.compareImage("testPointAnim2", False),
                 None,
                 lambda: self.assert_(not(self.__anim.isRunning())),
                 startKeepAttr,
                 lambda: self.compareImage("testPointAnim3", False),
                ))

    def testIntAnim(self):
        def startAnim():
            self.__anim.start()
        self.initScene()
        self.__doubleAnim = avg.LinearAnim(self.__node, "x", 300, 0, 100, True)
        self.__pointAnim = avg.LinearAnim(self.__node, "pos", 200, avg.Point2D(0,0), 
                avg.Point2D(100,40), True)
        self.start(None,
                (self.__doubleAnim.start,
                 None,
                 None,
                 lambda: self.compareImage("testIntAnim1", False),
                 self.__doubleAnim.abort,
                 self.__pointAnim.start,
                 None,
                 None,
                 lambda: self.compareImage("testIntAnim2", False),
                ))

    def testEaseInOutAnim(self):
        self.initScene()
        curAnim = avg.EaseInOutAnim(self.__node, "x", 300, 0, 100, 100, 100, False)
        self.testAnimType(curAnim, "testEaseInOutAnimC")

    def testSplineAnim(self):
        self.initScene()
        curAnim = anim.SplineAnim(self.__node, "x", 300, 0, 0, 100, 0, False)
        self.testAnimType(curAnim, "testSplineAnim")

    def testContinuousAnim(self):
        def onStart():
            Player.setTimeout(10,startAnim)
            Player.setTimeout(100,lambda:self.compareImage("testContAnim1", False))
            Player.setTimeout(200,startAnim2)
            Player.setTimeout(400,lambda:self.compareImage("testContAnim2", False))
            Player.setTimeout(450,startAnim3)
            Player.setTimeout(700,lambda:self.compareImage("testContAnim3", False))
            Player.setTimeout(800,stopAnim)
            Player.setTimeout(900,lambda:self.compareImage("testContAnim4", False))
            Player.setTimeout(1000,Player.stop)
        def startAnim():
            node=Player.getElementByID("mainimg")
            self.anim=anim.ContinuousAnim(node,"angle",0,1,0)
            self.anim.start()
        def startAnim2():
            node=Player.getElementByID("nestedimg1")
            self.anim2=anim.ContinuousAnim(node,"width",0,50,0)
            self.anim2.start()
        def startAnim3():
            node=Player.getElementByID("nestedimg2")
            self.anim3=anim.ContinuousAnim(node,"x",0,50,0)
            self.anim3.start()
        def stopAnim():
            self.anim.abort()
            self.anim2.abort()
            self.anim3.abort()
            self.anim = None
            self.anim2 = None
            self.anim3 = None

        Player.setFakeFPS(25)
        anim.init(avg)
        Player.loadFile("avg.avg")
        Player.setTimeout(1, onStart)
        Player.play()

    def testWaitAnim(self):
        def animStopped():
            self.__endCalled = True

        def startAnim():
            self.anim = avg.WaitAnim(200, animStopped, None)
            self.anim.start()

        self.initScene()
        self.__endCalled = False
        self.start(None,
                (startAnim, 
                 lambda: self.assert_(self.anim.isRunning()),
                 None,
                 None,
                 lambda: self.assert_(not(self.anim.isRunning())),
                 lambda: self.assert_(self.__endCalled)
                ))

    def testStateAnim(self):
        def state1StopCallback():
            self.__state1StopCallbackCalled = True
        def state2StartCallback():
            if self.__state1StopCallbackCalled:
                self.__stop1Start2CallbackOrder = True
            self.__state2StartCallbackCalled = True
        def makeAnim():
            self.anim = avg.StateAnim(
                    [avg.AnimState("STATE1", avg.LinearAnim(self.__node, "x", 200, 
                            0, 100, False, None, state1StopCallback), "STATE2"),
                     avg.AnimState("STATE2", avg.LinearAnim(self.__node, "x", 200, 
                            100, 50, False, state2StartCallback), "STATE3"),
                     avg.AnimState("STATE3", avg.WaitAnim())
                    ])
#            self.anim.setDebug(True)

        self.initScene()
        self.__state1StopCallbackCalled = False
        self.__state2StartCallbackCalled = False
        self.__stop1Start2CallbackOrder = False
        self.start(None,
                (makeAnim,
                 lambda: self.compareImage("testStateAnimC1", False),
                 lambda: self.anim.setState("STATE1"),
                 None,
                 lambda: self.compareImage("testStateAnimC2", False),
                 lambda: self.assert_(self.anim.getState() == "STATE2"),
                 lambda: self.compareImage("testStateAnimC3", False),
                 lambda: self.assert_(self.__state1StopCallbackCalled),
                 lambda: self.assert_(self.__state2StartCallbackCalled),
                 lambda: self.assert_(self.__stop1Start2CallbackOrder),
                 lambda: self.assert_(self.anim.getState() == "STATE3"),
                 lambda: self.compareImage("testStateAnimC4", False),
                 lambda: self.anim.setState("STATE1"),
                 lambda: self.assert_(avg.getNumRunningAnims() == 1),
                 lambda: self.compareImage("testStateAnimC5", False)
                ))

    def testParallelAnim(self):
        def animStopped():
            self.__endCalled = True

        def startAnim():
            self.anim = avg.ParallelAnim(
                    [ avg.LinearAnim(self.nodes[0], "x", 200, 0, 60),
                      avg.LinearAnim(self.nodes[1], "x", 400, 0, 120),
                      avg.EaseInOutAnim(self.nodes[2], "x", 400, 0, 120, 100, 100)
                    ], None, animStopped)
            self.__endCalled = False
            self.anim.start()

        def startTimedAnim():
            self.anim = avg.ParallelAnim(
                    [ avg.LinearAnim(self.nodes[0], "x", 200, 0, 60),
                      avg.LinearAnim(self.nodes[1], "x", 400, 0, 120),
                    ], None, animStopped, 200)
            self.__endCalled = False
            self.anim.start()
            
        def abortAnim():
            self.anim.abort()

        Player.loadString('<avg width="160" height="120"/>')
        self.nodes = []
        for i in range(3):
            node = Player.createNode("image", 
                    {"id":str(i), "x":64, "y": i*20, "href":"rgb24-64x64.png"})
            Player.getRootNode().appendChild(node)
            self.nodes.append(node)
        Player.setFakeFPS(10)
        self.__endCalled = False
        #TODO: test abort, max lifetime
        self.start(None,
                (startAnim,
                 lambda: self.assert_(avg.getNumRunningAnims() == 3),
                 lambda: self.compareImage("testParallelAnimC1", False),
                 lambda: self.assert_(self.anim.isRunning()),
                 None,
                 None,
                 lambda: self.assert_(not(self.anim.isRunning())),
                 lambda: self.compareImage("testParallelAnimC2", False),
                 lambda: self.assert_(self.__endCalled),
                 lambda: self.assert_(avg.getNumRunningAnims() == 0),
                 startAnim,
                 abortAnim,
                 lambda: self.compareImage("testParallelAnimC3", False),
                 lambda: self.assert_(self.__endCalled),
                 lambda: self.assert_(avg.getNumRunningAnims() == 0),
                 startTimedAnim,
                 None,
                 None,
                 lambda: self.assert_(self.__endCalled),
                 lambda: self.assert_(avg.getNumRunningAnims() == 0),

                ))
        self.nodes = []


def animTestSuite(tests):
    availableTests = (
        "testLinearAnim",
        "testFadeIn",
        "testFadeOut",
        "testNonExistentAttributeAnim",
        "testLinearAnimZeroDuration",
        "testPointAnim",
        "testEaseInOutAnim",
        "testIntAnim",
#        "testSplineAnim",
#        "testContinuousAnim",
        "testWaitAnim",
        "testParallelAnim",
        "testStateAnim",
        )
    return AVGTestSuite(availableTests, AnimTestCase, tests)

Player = avg.Player.get()

if __name__ == '__main__':
    runStandaloneTest(animTestSuite)

