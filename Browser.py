import math
from Chrome import Chrome
from Tab import Tab
from Utils import HEIGHT, WIDTH, parse_color
import sdl2
import skia

HSTEP, VSTEP = 13, 18

class Browser:
    def __init__(self):
        self.chrome = Chrome(self)
        self.sdl_windwow = sdl2.SDL_CreateWindow(b"Browser", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, WIDTH, HEIGHT, sdl2.SDL_WINDOW_SHOWN)
        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(
                WIDTH, HEIGHT,
                ct=skia.kRGBA_8888_ColorType,
                at=skia.kUnpremul_AlphaType
            )
        )
        self.chrome_surface = skia.Surface(WIDTH, math.ceil(self.chrome.bottom))
        self.tab_surface = None
        self.tabs = []
        self.active_tab = None

        if sdl2.SDL_BYTEORDER == sdl2.SDL_BIG_ENDIAN:
            self.RED_MASK = 0xff000000
            self.GREEN_MASK = 0x00ff0000
            self.BLUE_MASK = 0x0000ff00
            self.ALPHA_MASK = 0x000000ff
        else:
            self.RED_MASK = 0x000000ff
            self.GREEN_MASK = 0x0000ff00
            self.BLUE_MASK = 0x00ff0000
            self.ALPHA_MASK = 0xff000000
        

    def handle_key(self, e):
        if len(e.char) == 0: return
        if not (0x20 <= ord(e.char) <= 0x7E): return

        if self.chrome.keypress(e.char):
            self.raster_chrome()
            self.draw()
        elif self.focus == "content":
            self.active_tab.keypress(e.char)
            self.raster_tab()
            self.draw()

    def handle_enter(self):
        self.chrome.enter()
        self.draw()

    def scroll_down(self):
        self.active_tab.scrolldown()
        self.draw()

    def scroll_up(self):
        self.active_tab.scrollUp()
        self.draw()

    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.focus = None
            self.chrome.click(e.x, e.y)
            self.raster_chrome()
        else:
            url = self.active_tab.url
            self.focus = "content"
            self.chrome.blur()
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
            if self.active_tab.url != url:
                self.raster_chrome()
            self.raster_tab()
        self.draw()

    def raster_tab(self):
        tab_height = math.ceil(self.active_tab.document.height + 2 * VSTEP)
        if not self.tab_surface or tab_height != self.tab_surface.height():
            self.tab_surface = skia.Surface(WIDTH, tab_height)
        
        canvas = self.tab_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        self.active_tab.raster(canvas)

    def raster_chrome(self):
        canvas = self.chrome_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)

        for cmd in self.chrome.paint():
            cmd.execute(canvas)

    def draw(self):
        canvas = self.root_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)

        tab_rect = skia.Rect.MakeLTRB(0, self.chrome.bottom, WIDTH, HEIGHT)
        tab_offset = self.chrome.bottom - self.active_tab.scroll
        canvas.save()
        canvas.clipRect(tab_rect)
        canvas.translate(0, tab_offset)
        self.tab_surface.draw(canvas, 0, 0)
        canvas.restore()

        chrome_rect = skia.Rect.MakeLTRB(0, 0, WIDTH, self.chrome.bottom)
        canvas.save()
        canvas.clipRect(chrome_rect)
        self.chrome_surface.draw(canvas, 0, 0)
        canvas.restore()

        skia_image = self.root_surface.makeImageSnapshot()
        skia_bytes = skia_image.tobytes()
        depth = 32 # bits per pixel
        pitch = 4 * WIDTH # bytes per line
        sdl_surface = sdl2.SDL_CreateRGBSurfaceFrom(
            skia_bytes, WIDTH, HEIGHT, depth, pitch,
            self.RED_MASK, self.GREEN_MASK, self.BLUE_MASK, self.ALPHA_MASK
        )

        rect = sdl2.SDL_Rect(0, 0, WIDTH, HEIGHT)
        window_surface = sdl2.SDL_GetWindowSurface(self.sdl_windwow)
        sdl2.SDL_BlitSurface(sdl_surface, rect, window_surface, rect)
        sdl2.SDL_UpdateWindowSurface(self.sdl_windwow)

        

   
    def new_tab(self, url):
        new_tab = Tab(HEIGHT - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.raster_tab()
        self.raster_chrome()
        self.draw()
        
    def handle_quit(self):
        sdl2.SDL_DestroyWindow(self.sdl_windwow)