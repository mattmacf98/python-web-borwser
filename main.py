from Browser import Browser
from URL import URL
import tkinter
import sys 

if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()