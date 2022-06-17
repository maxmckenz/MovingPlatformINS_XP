"""
This plugin visualizes a moving-platform inertial navigation system in X-Plane.

Created by Max Mckenzie for X-Plane 11.55, 17/07/2022

www.flybymax.com
"""

import xp

# Define the class
class PythonInterface:
    def __init__(self):
        self.Name = "MovingPlatform"
        self.Sig = "movingplatform.xppython3"
        self.Desc = "A plugin to visualize a moving platform inertial navigation system"

        # Textures
        self.MAX_TEXTURES = 4
        self.PANEL_FILENAME = "Panel.bmp"
        self.GAUGE_FILENAME = "Gauge.bmp"
        self.NEEDLE_FILENAME = "Needle.bmp"
        self.NEEDLE_MASK_FILENAME = "NeedleMask.bmp"
        self.PANEL_TEXTURE = 0
        self.GAUGE_TEXTURE = 1
        self.NEEDLE_TEXTURE = 2
        self.NEEDLE_TEXTURE_MASK = 3

        # Display bool
        self.INS_DisplayPanelWindow = 1

        # Setup texture file locations
        self.FileName = "Resources/plugins/PythonPlugins/ExampleGauge/"

        self.PluginDataFile = os.path.join(xp.getSystemPath(), self.FileName)

        self.INS_PanelWindow = None
        self.DR_EngineN1 = xp.findDataRef("sim/flightmodel/engine/ENGN_N1_")

        self.DR_RED = xp.findDataRef("sim/graphics/misc/cockpit_light_level_r")
        self.DR_GREEN = xp.findDataRef("sim/graphics/misc/cockpit_light_level_g")
        self.DR_BLUE = xp.findDataRef("sim/graphics/misc/cockpit_light_level_b")
        self.INS_HotKey = None
        self.Texture = []


    def XPluginStart(self): # Required
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # Create our window, setup datarefs and register our hotkey.
        self.INS_PanelWindow = xp.createWindowEx(50, 600, 300, 400,
                                                 decoration=xp.WindowDecorationSelfDecorated,
                                                 click=self.INS_PanelMouseClickCallback,
                                                 visible=1)

        # Register a callback (function, phase, after=1, refCon=None)
        xp.registerDrawCallback(self.INS_DrawCallback, xp.Phase_LastCockpit)  # Doesn't work with "Phase_Gauges"

        self.INS_HotKey = xp.registerHotKey(xp.VK_DIVIDE, xp.DownFlag, "divide", self.ExampleGaugeHotKeyCallback)

        self.Texture = xp.generateTextureNumbers(self.MAX_TEXTURES)

        # Load the textures and bind them etc.
        self.LoadTextures()

        return self.Name, self.Sig, self.Desc

    def XPluginStop(self): # Required
        # Clean up
        xp.unregisterDrawCallback(self.INS_DrawCallback, xp.Phase_LastCockpit)
        xp.unregisterHotKey(self.INS_HotKey)
        xp.destroyWindow(self.ExampleGaugePanelDisplayWindow)

    def XPluginEnable(self): # Required, should return 1 if succesful
        return 1 # Otherwise plugin stops

    def XPluginDisable(self): # Required
        pass

    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam): # Required
        pass

    '''
    Methods from this point onwards are technically not required by X-Plane, order does not matter
    '''

    # Used for dragging plugin panel window.
    def CoordInRect(self, x, y, l, t, r, b):
        return ((x >= l) and (x < r) and (y < t) and (y >= b))

    def INS_DrawCallback(self, inPhase, inIsBefore, inRefcon):

        # Do the actual drawing, but only if our window is active
        if (self.INS_DisplayPanelWindow):

            # Get our current N1 for each engine
            self.EngineN1 = []
            count = xp.getDatavf(self.DR_EngineN1, self.EngineN1, 0, 8)

            # Convert N1 to rotation to match gauge
            self.EngineN1[0] = float((270 * self.EngineN1[0] / 100.0) - 135)
            print(self.EngineN1[0])
            self.DrawGLScene(512, 250)

        return 1



    """
    ExampleGaugePanelMouseClickCallback

    Our mouse click callback updates the position that the windows is dragged to.
    """

    def INS_PanelMouseClickCallback(self, inWindowID, x, y, inMouse, inRefcon):
        global Dragging, dX, dY, Width, Height

        if not self.INS_DisplayPanelWindow:
            return 0

        # Get the windows current position
        (Left, Top, Right, Bottom) = xp.getWindowGeometry(inWindowID)

        if (inMouse == xp.MouseDown):
            # Test for the mouse in the top part of the window
            if (self.CoordInRect(x, y, Left, Top, Right, Top - 15)):
                dX = x - Left
                dY = y - Top
                Width = Right - Left
                Height = Bottom - Top
                Dragging = 1

        if (inMouse == xp.MouseDrag):
            # We are dragging so update the window position
            if (Dragging):
                Left = (x - dX)
                Right = Left + Width
                Top = (y - dY)
                Bottom = Top + Height
                xp.setWindowGeometry(inWindowID, Left, Top, Right, Bottom)

        if (inMouse == xp.MouseUp):
            Dragging = 0

        return 1

    # Toggle between display and non display
    def ExampleGaugeHotKeyCallback(self, refCon):
        xp.setWindowIsVisible(self.ExampleGaugePanelDisplayWindow,
                              not xp.getWindowIsVisible(self.ExampleGaugePanelDisplayWindow))
        self.INS_DisplayPanelWindow = not self.ExampleGaugeDisplayPanelWindow

    # Loads all our textures
    def LoadTextures(self):
        if not self.LoadGLTexture(self.PANEL_FILENAME, self.PANEL_TEXTURE):
            xp.debugString("Panel texture failed to load\n")
        if not self.LoadGLTexture(self.GAUGE_FILENAME, self.GAUGE_TEXTURE):
            xp.debugString("Gauge texture failed to load\n")
        if not self.LoadGLTexture(self.NEEDLE_FILENAME, self.NEEDLE_TEXTURE):
            xp.debugString("Needle texture failed to load\n")
        if not self.LoadGLTexture(self.NEEDLE_MASK_FILENAME, self.NEEDLE_TEXTURE_MASK):
            xp.debugString("Needle texture mask failed to load\n")

    # Loads one texture
    def LoadGLTexture(self, FileName, TextureId):
        # Need to get the actual texture path
        # and append the filename to it.
        TextureFileName = self.PluginDataFile + FileName
        # Get the bitmap from the file
        im = Image.open(TextureFileName)
        ix, iy, image = im.size[0], im.size[1], im.convert('RGBA').tobytes()
        xp.bindTexture2d(self.Texture[TextureId], 0)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

        return 1

    # Draws the textures that make up the gauge
    def DrawGLScene(self, x1, y1):
        Red = xp.getDataf(self.DR_RED)
        Green = xp.getDataf(self.DR_GREEN)
        Blue = xp.getDataf(self.DR_BLUE)

        # Setup sizes for panel and gauge
        PanelWidth = 256
        PanelHeight = 256
        GaugeWidth = 128
        GaugeHeight = 128
        GaugeWidthRatio = GaugeWidth / 256.0
        GaugeHeightRatio = GaugeHeight / 256.0

        # Need to find out where our window is
        (lLeft, lTop, lRight, lBottom) = xp.getWindowGeometry(self.ExampleGaugePanelDisplayWindow)
        PanelWindowLeft = int(lLeft)
        PanelWindowTop = int(lTop)
        PanelWindowRight = int(lRight)
        PanelWindowBottom = int(lBottom)

        # Setup our panel and gauge relative to our window
        PanelLeft = PanelWindowLeft
        PanelRight = PanelWindowRight
        PanelBottom = PanelWindowBottom
        PanelTop = PanelWindowTop
        GaugeLeft = PanelLeft + 64
        GaugeRight = GaugeLeft + GaugeWidth
        GaugeBottom = PanelBottom + 64
        GaugeTop = GaugeBottom + GaugeHeight

        # Setup our needle relative to the gauge
        NeedleLeft = GaugeLeft + 125.0 * GaugeWidthRatio
        NeedleRight = NeedleLeft + 8.0 * GaugeWidthRatio
        NeedleBottom = GaugeBottom + 120.0 * GaugeHeightRatio
        NeedleTop = NeedleBottom + 80.0 * GaugeWidthRatio
        NeedleTranslationX = NeedleLeft + ((NeedleRight - NeedleLeft) / 2)
        NeedleTranslationY = NeedleBottom + (5 * GaugeHeightRatio)

        # Tell Xplane what we are doing
        xp.setGraphicsState(
            numberTexUnits=1)  # ( NOTE: xppython3 bug requires parameter named 'numberTextUnits', fixed v3.1.3)

        # Handle day/night
        glColor3f(Red, Green, Blue)

        # Draw Panel
        glPushMatrix()
        xp.bindTexture2d(self.Texture[self.PANEL_TEXTURE], 0)
        glBegin(GL_QUADS)
        # X-Plane flips image, so glTexCoord2f() values are flipped from Sandy's example.
        glTexCoord2f(1, 1);
        glVertex2f(PanelRight, PanelBottom)  # Bottom Right Of The Texture and Quad
        glTexCoord2f(0, 1);
        glVertex2f(PanelLeft, PanelBottom)  # Bottom Left Of The Texture and Quad
        glTexCoord2f(0, 0);
        glVertex2f(PanelLeft, PanelTop)  # Top Left Of The Texture and Quad
        glTexCoord2f(1, 0);
        glVertex2f(PanelRight, PanelTop)  # Top Right Of The Texture and Quad
        glEnd()
        glPopMatrix()

        # Draw Gauge
        glPushMatrix()
        xp.bindTexture2d(self.Texture[self.GAUGE_TEXTURE], 0)
        glBegin(GL_QUADS)
        glTexCoord2f(1, 1);
        glVertex2f(GaugeRight, GaugeBottom)  # Bottom Right Of The Texture and Quad
        glTexCoord2f(0, 1);
        glVertex2f(GaugeLeft, GaugeBottom)  # Bottom Left Of The Texture and Quad
        glTexCoord2f(0, 0);
        glVertex2f(GaugeLeft, GaugeTop)  # Top Left Of The Texture and Quad
        glTexCoord2f(1, 0);
        glVertex2f(GaugeRight, GaugeTop)  # Top Right Of The Texture and Quad
        glEnd()
        glPopMatrix()

        glPushMatrix()
        # Turn on Alpha Blending and turn off Depth Testing
        xp.setGraphicsState(numberTexUnits=1,
                            alphaBlending=1)  # ( NOTE: xppython3 bug requires parameter named 'numberTextUnits', fixed v3.1.3)

        glTranslatef(NeedleTranslationX, NeedleTranslationY, 0.0)
        glRotatef(self.EngineN1[0], 0.0, 0.0, -1.0)
        glTranslatef(-NeedleTranslationX, -NeedleTranslationY, 0.0)

        glBlendFunc(GL_DST_COLOR, GL_ZERO)

        # Draw Needle Mask
        xp.bindTexture2d(self.Texture[self.NEEDLE_TEXTURE_MASK], 0)
        glBegin(GL_QUADS)
        glTexCoord2f(1, 1);
        glVertex2f(NeedleRight, NeedleBottom)  # Bottom Right Of The Texture and Quad
        glTexCoord2f(0, 1);
        glVertex2f(NeedleLeft, NeedleBottom)  # Bottom Left Of The Texture and Quad
        glTexCoord2f(0, 0);
        glVertex2f(NeedleLeft, NeedleTop)  # Top Left Of The Texture and Quad
        glTexCoord2f(1, 0);
        glVertex2f(NeedleRight, NeedleTop)  # Top Right Of The Texture and Quad
        glEnd()

        glBlendFunc(GL_ONE, GL_ONE)

        # Draw Needle
        xp.bindTexture2d(self.Texture[self.NEEDLE_TEXTURE], 0)
        glBegin(GL_QUADS)
        glTexCoord2f(1, 1);
        glVertex2f(NeedleRight, NeedleBottom)  # Bottom Right Of The Texture and Quad
        glTexCoord2f(0, 1);
        glVertex2f(NeedleLeft, NeedleBottom)  # Bottom Left Of The Texture and Quad
        glTexCoord2f(0, 0);
        glVertex2f(NeedleLeft, NeedleTop)  # Top Left Of The Texture and Quad
        glTexCoord2f(1, 0);
        glVertex2f(NeedleRight, NeedleTop)  # Top Right Of The Texture and Quad
        glEnd()

        # # Turn off Alpha Blending and turn on Depth Testing
        xp.setGraphicsState(numberTexUnits=1,
                            depthTesting=1)  # ( NOTE: xppython3 bug requires parameter named 'numberTextUnits', fixed v3.1.3)
        glPopMatrix()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glFlush()

        return 1
