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

from libavg import avg
from testcase import *
import gc

class OffscreenTestCase(AVGTestCase):
    def __init__(self, testFuncName):
        AVGTestCase.__init__(self, testFuncName)
    
    def testCanvasBasics(self):
        def createCanvas(isFirst, canvasName, x):
            canvas = self.__createOffscreenCanvas(canvasName, False)
            canvas.getElementByID("test1").x = x
            node = avg.ImageNode(parent=Player.getRootNode(), id="imagenode")
            node.href="canvas:"+canvasName
            if isFirst:
                self.assert_(canvas.getNumDependentCanvases() == 0)
                self.canvas1 = canvas
            else:
                self.assert_(canvas.getNumDependentCanvases() == 1)
                self.canvas2 = canvas

        def unlink():
            self.node = Player.getElementByID("imagenode")
            self.node.unlink()
            self.assert_(self.canvas1.getNumDependentCanvases() == 0)
            gc.collect()

        def relink():
            Player.getRootNode().appendChild(self.node)
            self.node = None
            self.assert_(self.canvas1.getNumDependentCanvases() == 1)
            
        def changeHRef(href):
            Player.getElementByID("imagenode").href = href

        def setBitmap():
            bitmap = avg.Bitmap("rgb24-65x65.png")
            Player.getElementByID("imagenode").setBitmap(bitmap)

        def deleteCanvases():
            changeHRef("")
            firstNode.href = ""
            Player.deleteCanvas("testcanvas1")
#            self.assertException(lambda: changeHRef("canvas:testcanvas1"))
            changeHRef("canvas:testcanvas2")
#            self.assertException(lambda: Player.deleteCanvas("testcanvas2"))
            changeHRef("")
            Player.deleteCanvas("testcanvas2")
#            self.assertException(lambda: Player.deleteCanvas("foo"))

        self.loadEmptyScene()
        createCanvas(True, "testcanvas1", 0)
        firstNode = Player.getElementByID("imagenode")
        self.start(None, 
                (lambda: self.compareImage("testOffscreen1", False),
                 unlink,
                 lambda: self.compareImage("testOffscreen2", False), 
                 relink,
                 lambda: self.compareImage("testOffscreen1", False),
                 unlink,
                 lambda: createCanvas(False, "testcanvas2", 80),
                 lambda: self.compareImage("testOffscreen3", False),
                 lambda: changeHRef("canvas:testcanvas1"),
                 lambda: self.assert_(self.canvas1.getNumDependentCanvases() == 1),
                 lambda: self.assert_(self.canvas2.getNumDependentCanvases() == 0),
                 lambda: self.compareImage("testOffscreen1", False),
                 lambda: changeHRef("rgb24-65x65.png"),
                 lambda: self.assert_(self.canvas1.getNumDependentCanvases() == 0),
                 lambda: self.compareImage("testOffscreen4", False),
                 lambda: changeHRef("canvas:testcanvas1"),
                 lambda: self.assert_(self.canvas1.getNumDependentCanvases() == 1),
                 lambda: self.compareImage("testOffscreen1", False),
                 setBitmap,
                 lambda: self.compareImage("testOffscreen4", False),
                 deleteCanvases,
                 lambda: self.compareImage("testOffscreen5", False),
                ))

    def testCanvasLoadAfterPlay(self):
        def __createOffscreenCanvas():
            offscreenCanvas = self.__createOffscreenCanvas("offscreencanvas", False)
            self.node = avg.ImageNode(parent=Player.getRootNode(), 
                    href="canvas:offscreencanvas")
    
        self.loadEmptyScene()
        self.start(None,
                (
                 __createOffscreenCanvas,
                 lambda: self.compareImage("testOffscreen1", False),
                ))

    def testCanvasResize(self):
        def setSize():
            self.node.size = (80, 60)

        mainCanvas, offscreenCanvas = self.__setupCanvas(False)
        self.start(None,
                (setSize,
                 lambda: self.compareImage("testCanvasResize", False)
                ))

    def testCanvasErrors(self):
        self.loadEmptyScene()
        # Missing size
        self.assertException(
                lambda: Player.loadCanvasString("""<canvas id="foo"/>"""))
        # Duplicate canvas id
        Player.loadCanvasString("""<canvas id="foo" size="(160, 120)"/>""")
        self.assertException(
                lambda: Player.loadCanvasString("""<canvas id="foo" size="(160, 120)"/>"""))

    def testCanvasAPI(self):
        def checkMainScreenshot():
            bmp1 = Player.screenshot()
            bmp2 = mainCanvas.screenshot()
            self.assert_(self.areSimilarBmps(bmp1, bmp2, 0.01, 0.01))

        def checkCanvasScreenshot():
            bmp = offscreenCanvas.screenshot()
            self.compareBitmapToFile(bmp, "testOffscreenScreenshot", False)

        mainCanvas = self.loadEmptyScene()
        self.assert_(mainCanvas == Player.getMainCanvas())
        self.assert_(mainCanvas.getRootNode() == Player.getRootNode())
        offscreenCanvas = self.__createOffscreenCanvas("offscreencanvas", False)
        self.assert_(offscreenCanvas == Player.getCanvas("offscreencanvas"))
        self.assert_(offscreenCanvas.getElementByID("test1").href == "rgb24-65x65.png")
        self.assert_(offscreenCanvas.getElementByID("missingnode") == None)
        self.assertException(Player.screenshot())
        self.start(None, 
                (checkMainScreenshot,
                 checkCanvasScreenshot))

    def testCanvasEvents(self):
        def onOffscreenImageDown(event):
            self.__offscreenImageDownCalled = True

        def onMainDown(event):
            self.__mainDownCalled = True

        def reset():
            self.__offscreenImageDownCalled = False
            self.__mainDownCalled = False

        def setPos():
            self.node.pos = (80, 60)
            self.node.size = (80, 60)

        mainCanvas, offscreenCanvas = self.__setupCanvas(True)
        offscreenImage = offscreenCanvas.getElementByID("test1")
        offscreenImage.setEventHandler(avg.CURSORDOWN, avg.MOUSE, onOffscreenImageDown)
        Player.getRootNode().setEventHandler(avg.CURSORDOWN, avg.MOUSE, onMainDown)
        helper = Player.getTestHelper()
        self.__offscreenImageDownCalled = False
        self.__mainDownCalled = False
        self.start(None,
                (lambda: helper.fakeMouseEvent(avg.CURSORDOWN, True, False, False, 
                        10, 10, 1),
                 lambda: self.assert_(self.__offscreenImageDownCalled),
                 reset,
                 lambda: helper.fakeMouseEvent(avg.CURSORDOWN, True, False, False, 
                        80, 10, 1),
                 lambda: self.assert_(not(self.__offscreenImageDownCalled)),
                 reset,
                 setPos,
                 lambda: helper.fakeMouseEvent(avg.CURSORDOWN, True, False, False, 
                        70, 65, 1),
                 lambda: self.assert_(not(self.__offscreenImageDownCalled)),
                 lambda: helper.fakeMouseEvent(avg.CURSORDOWN, True, False, False, 
                        120, 65, 1),
                 lambda: self.assert_(not(self.__offscreenImageDownCalled)),
                 reset,
                 lambda: helper.fakeMouseEvent(avg.CURSORDOWN, True, False, False, 
                        110, 65, 1),
                 lambda: self.assert_(self.__offscreenImageDownCalled and 
                        not(self.__mainDownCalled)),
                 reset,
                 lambda: helper.fakeMouseEvent(avg.CURSORDOWN, True, False, False, 
                        1, 1, 1),
                 lambda: self.assert_(not(self.__offscreenImageDownCalled) and 
                        self.__mainDownCalled),
                ))

    def testCanvasEventCapture(self):
        def onOffscreenImageDown(event):
            self.__offscreenImageDownCalled = True

        mainCanvas, offscreenCanvas = self.__setupCanvas(True)
        offscreenImage = offscreenCanvas.getElementByID("test1")
        offscreenImage.setEventHandler(avg.CURSORDOWN, avg.MOUSE, onOffscreenImageDown);
        helper = Player.getTestHelper()
        self.__offscreenImageDownCalled = False
        offscreenImage.setEventCapture()
        self.start(None,
                (lambda: helper.fakeMouseEvent(avg.CURSORDOWN, True, False, False, 
                        80, 10, 1),
                 lambda: self.assert_(self.__offscreenImageDownCalled),
                ))
                
    def testCanvasRender(self):
        def renderCanvas():
            canvas = self.__createOffscreenCanvas("testcanvas", False)
            canvas.render()
            bmp = canvas.screenshot()
            self.compareBitmapToFile(bmp, "testOffscreenScreenshot", False)
            Player.deleteCanvas("testcanvas")
            canvas = None

        mainCanvas = self.loadEmptyScene()
        self.assertException(renderCanvas);
        Player.deleteCanvas("testcanvas")
        self.start(None,
                (renderCanvas,
                ))
        
    def testCanvasCrop(self):
        mainCanvas = self.loadEmptyScene()
        canvas = Player.loadCanvasString("""
            <canvas id="testcanvas" width="160" height="120">
                <div pos="(40, 30)" size="(80, 60)">
                    <image id="test1" pos="(-32, -32)" href="rgb24-65x65.png"/>
                </div>
            </canvas>
        """)
        node = avg.ImageNode(parent=Player.getRootNode(), 
                href="canvas:testcanvas")
        self.start(None,
                (lambda: self.compareImage("testCanvasCrop", False),
                ))

    def testCanvasAlpha(self):
        mainCanvas = self.loadEmptyScene()
        canvas = Player.loadCanvasString("""
            <canvas id="testcanvas" width="80" height="120">
                <image id="test1" href="rgb24alpha-64x64.png"/>
            </canvas>
        """)
        avg.RectNode(parent=Player.getRootNode(), fillcolor="FFFFFF",
                pos=(0.5, 0.5), size=(160, 48), fillopacity=1)
        node = avg.ImageNode(parent=Player.getRootNode(), 
                href="canvas:testcanvas")
        avg.ImageNode(parent=Player.getRootNode(), x=64, href="rgb24alpha-64x64.png")
        self.start(None,
                (lambda: self.compareImage("testCanvasAlpha", False),
                ))

    def testCanvasBlendModes(self):
        def createBaseCanvas():
            return Player.loadCanvasString("""
                <canvas id="testcanvas" width="160" height="120">
                    <image href="freidrehen.jpg"/>
                    <image id="blend" x="0" y="0" opacity="0.6" href="rgb24-65x65.png"/>
                    <image x="0" y="48" opacity="0.6" href="rgb24-65x65.png" 
                            blendmode="add"/>
                    <image x="48" y="0" opacity="0.6" href="rgb24-65x65.png" 
                            blendmode="min"/>
                    <image x="48" y="48" opacity="0.6" href="rgb24-65x65.png" 
                            blendmode="max"/>
                </canvas>
            """)
       
        mainCanvas = self.loadEmptyScene()
        canvas = createBaseCanvas()
        node = avg.ImageNode(parent=Player.getRootNode(), href="canvas:testcanvas")
        self.start(None,
                (lambda: self.compareImage("testCanvasBlendModes", False),
                ))

    def testCanvasMultisampling(self):
        def testIllegalSamples():
            canvas = Player.loadCanvasString(
                    """<canvas id="brokencanvas" width="160" height="120" 
                            multisamplesamples="42"/>""")
        mainCanvas = self.loadEmptyScene()
        if not(avg.OffscreenCanvas.isMultisampleSupported()):
            print "Offscreen multisampling not supported - skipping test."
            return
        canvas = Player.loadCanvasString("""
            <canvas id="testcanvas" width="160" height="120" multisamplesamples="2">
                <image id="test1" href="rgb24-65x65.png" angle="0.1"/>
            </canvas>
        """)
        self.assert_(canvas.multisamplesamples == 2)
        node = avg.ImageNode(parent=Player.getRootNode(), 
                href="canvas:testcanvas")
        self.start(None,
                (lambda: self.compareImage("testCanvasMultisample", False),
                 lambda: self.assertException(testIllegalSamples),
                ))
       
    def testCanvasMipmap(self):
        mainCanvas = self.loadEmptyScene()

        canvas = Player.loadCanvasString("""
            <canvas id="testcanvas" width="80" height="120" mipmap="True">
                <image id="test1" href="rgb24alpha-64x64.png"/>
            </canvas>
        """)
        node = avg.ImageNode(parent=Player.getRootNode(), size=(40, 30), 
                href="canvas:testcanvas")
        self.start(None,
                (lambda: self.compareImage("testCanvasMipmap", False),
                ))

    def testCanvasDependencies(self):
        def makeCircularRef():
            self.offscreen1.getElementByID("test1").href = "canvas:offscreencanvas2"
            
        def createTwoCanvases():
            self.offscreen1 = self.__createOffscreenCanvas("offscreencanvas1", False)
            self.offscreen2 = self.__createOffscreenCanvas("offscreencanvas2", False)
            self.node = avg.ImageNode(parent=Player.getRootNode(), 
                    href="canvas:offscreencanvas1")
            node = self.offscreen1.getElementByID("test1")
            node.href = "canvas:offscreencanvas2"
            node.size = (80, 60)
            
        def exchangeCanvases():
            self.offscreen1.getElementByID("test1").href = "rgb24-65x65.png"
            self.offscreen2.getElementByID("test1").href = "canvas:offscreencanvas1"
            self.node.href = "canvas:offscreencanvas2"
            
        mainCanvas = self.loadEmptyScene()
        createTwoCanvases()
        self.offscreen1.getElementByID("test1").href = ""
        self.offscreen1 = None
        self.offscreen2 = None
        self.node.href = ""
        self.node = None
        Player.deleteCanvas("offscreencanvas1")
        Player.deleteCanvas("offscreencanvas2")
        self.start(None,
                   (createTwoCanvases,
                    lambda: self.compareImage("testCanvasDependencies1", False),
                    exchangeCanvases,
                    lambda: self.compareImage("testCanvasDependencies2", False),
                    lambda: self.assertException(makeCircularRef),
                  ))

    def __setupCanvas(self, handleEvents):
        mainCanvas = self.loadEmptyScene()
        offscreenCanvas = self.__createOffscreenCanvas("offscreencanvas", handleEvents)
        self.node = avg.ImageNode(parent=Player.getRootNode(), 
                href="canvas:offscreencanvas")
        return (mainCanvas, offscreenCanvas)

    def __createOffscreenCanvas(self, canvasName, handleEvents):
        return Player.loadCanvasString("""
            <canvas id="%s" width="160" height="120" handleevents="%s">
                <image id="test1" href="rgb24-65x65.png"/>
            </canvas>
        """%(canvasName, str(handleEvents)))


def offscreenTestSuite(tests):
    availableTests = (
            "testCanvasBasics",
            "testCanvasLoadAfterPlay",
            "testCanvasResize",
            "testCanvasErrors",
            "testCanvasAPI",
            "testCanvasEvents",
            "testCanvasEventCapture",
            "testCanvasRender",
            "testCanvasCrop",
            "testCanvasAlpha",
            "testCanvasBlendModes",
            "testCanvasMultisampling",
            "testCanvasMipmap",
            "testCanvasDependencies",
            )
    return createAVGTestSuite(availableTests, OffscreenTestCase, tests)


Player = avg.Player.get()