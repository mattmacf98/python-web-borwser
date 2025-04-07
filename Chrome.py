from DrawLine import DrawLine
from DrawOutline import DrawOutline
from DrawRect import DrawRect
from DrawText import DrawText
from Rect import Rect
from URL import URL
from Utils import WIDTH, get_font


class Chrome:
    def __init__(self, browser):
        self.browser = browser
        self.font = get_font(20, "normal", "roman")
        self.font_height = self.font.metrics("linespace")
        self.focus = None
        self.address_bar = ""

        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2*self.padding
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + self.font_height + 2*self.padding
        self.bottom = self.urlbar_bottom

        back_width = self.font.measure("<") + 2*self.padding
        self.back_rect = Rect(self.padding, self.urlbar_top + self.padding, self.padding + back_width, self.urlbar_bottom - self.padding)

        self.address_rect = Rect(self.back_rect.top + self.padding, self.urlbar_top + self.padding, WIDTH - self.padding, self.urlbar_bottom - self.padding)

        add_tab_width = self.font.measure("+") + 2*self.padding
        self.new_tab_rect = Rect(self.padding, self.padding, self.padding + add_tab_width, self.padding + self.font_height)

    def blur(self):
        self.focus = None

    def keypress(self, char):
        if self.focus == "address_bar":
            self.address_bar += char
            return True
        return False

    def enter(self):
        if self.focus == "address_bar":
            self.browser.active_tab.load(URL(self.address_bar))
            self.focus = None

    def click(self, x, y):
        self.focus = None
        if self.new_tab_rect.contains_point(x, y):
            self.browser.new_tab(URL("https://browser.engineering/"))
        elif self.back_rect.contains_point(x, y):
            self.browser.active_tab.go_back()
        elif self.address_rect.contains_point(x, y):
            self.focus = "address_bar"
            self.address_bar = ""
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).contains_point(x, y):
                    self.browser.active_tab = tab
                    break
    
    def tab_rect(self, index):
        tabs_start = self.new_tab_rect.right + self.padding
        tab_width = self.font.measure("Tab X") + 2*self.padding
        return Rect(tabs_start + index*tab_width, self.tabbar_top, tabs_start + (index+1)*tab_width, self.tabbar_bottom)
    
    def paint(self):
        cmds = []

        cmds.append(DrawRect(Rect(0, 0, WIDTH, self.bottom), "white"))
        cmds.append(DrawLine(0, self.tabbar_top, WIDTH, self.tabbar_top, "black", 1))

        # add tab
        cmds.append(DrawOutline(self.new_tab_rect, "black", 1))
        cmds.append(DrawText(self.new_tab_rect.left + self.padding, self.new_tab_rect.top, "+", self.font, "black"))

        # tabs
        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(DrawLine(bounds.left, 0, bounds.left, bounds.bottom, "black", 1))
            cmds.append(DrawLine(bounds.right, 0, bounds.right, bounds.bottom, "black", 1))
            cmds.append(DrawText(bounds.left + self.padding, bounds.top + self.padding, "Tab {}".format(i), self.font, "black"))
            if tab == self.browser.active_tab:
                cmds.append(DrawLine(0, bounds.bottom, bounds.left, bounds.bottom, "black", 1))
                cmds.append(DrawLine(bounds.right, bounds.bottom, WIDTH, bounds.bottom, "black", 1))

        # back
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(DrawText(self.back_rect.left + self.padding, self.back_rect.top, "<", self.font, "black"))

        # address bar
        cmds.append(DrawOutline(self.address_rect, "black", 1))
        if self.focus == "address_bar":
            cmds.append(DrawText(self.address_rect.left + self.padding, self.address_rect.top, self.address_bar, self.font, "black"))
            w = self.font.measure(self.address_bar)
            cmds.append(DrawLine(self.address_rect.left + self.padding + w, self.address_rect.top, self.address_rect.left + self.padding + w, self.address_rect.bottom, "red", 1))
        else:
            url = str(self.browser.active_tab.url)
            cmds.append(DrawText(self.address_rect.left + self.padding, self.address_rect.top, url, self.font, "black"))

        return cmds