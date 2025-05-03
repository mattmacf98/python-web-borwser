from Browser import Browser
from URL import URL
import sys 
import sdl2
import ctypes

def mainloop(browser: Browser):
    event = sdl2.SDL_Event()
    while True:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                browser.handle_quit()
                sdl2.SDL_Quit()
                sys.exit()
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(event.button)
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    browser.scroll_down()
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    browser.scroll_up()
            elif event.key.keysym.sym == sdl2.SDL_TEXTINPUT:
                browser.handle_key(event.text.text.decode("utf-8"))
        browser.active_tab.task_runner.run()
        browser.raster_and_draw()
        browser.scheduele_animation_frame()

if __name__ == "__main__":
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS)
    browser = Browser()
    browser.new_tab(URL(sys.argv[1]))
    mainloop(browser)

