# CS121: Treemaps
# Sample use of Chi_Canvas

from drawing import ChiCanvas

def draw(canvas):
    
    # draw a blue rectangle w/ text "Blue rectangle"
    x0 = 0.1
    y0 = 0.05
    w = 0.2
    h = 0.35
    canvas.draw_rectangle(x0, y0, x0+w, y0+h, fill='blue')
    canvas.draw_text(x0+w/2, y0+h/2, w*.95,  "Blue rectangle", fg="black")

    # draw a red rectangle w/ text "This rectangle is red"
    x0 = 0.5
    y0 = 0.5
    w = 0.3
    h = 0.4
    canvas.draw_rectangle(x0, y0, x0+w, y0+h, fill='red')
    canvas.draw_text_vertical(x0+w/2.0, y0+h/2, h*.85,  "This text is vertical", 
                     fg="black")


def go():
    # create a canvas
    c = ChiCanvas(10, 10)

    # draw sample rectangles
    draw(c)

    # show them.
    c.show()

    c.savefig("sample.png")


if __name__=="__main__":
    go()
