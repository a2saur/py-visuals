import tkinter as tk
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageTk
import visCanvas as visC

### CODE START -- overall parameters
WIDTH = 800
HEIGHT = 400
FPS = 30
### CODE END

root = tk.Tk()

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#000")
canvas.pack()

cv = visC.VisCanvas(canvas, WIDTH, HEIGHT)

### CODE START -- initial setup
cv.add_sprite(visC.Dot("#FFF", "#FFF", 10, 50, 50, 0.5), "dot")
cv.add_sprite(visC.Rect("#000", "#FFF", 500, 100, 100, 150), "rect")
keyCodeText = visC.Text("Hello", 500, 100, 150, color="#FFF", autoSize=False)
cv.add_sprite(keyCodeText, "text")
keyCodeText2 = visC.Text("A", 500, 100, 300, color="#FFF", autoSize=True)
cv.add_sprite(keyCodeText2, "text")

slider1 = visC.HorizontalSlider("#000", "#FFF", "#FFF", "#FFF", 250, 15, 250, HEIGHT-100)
cv.add_sprite(slider1)

cv.add_button_and_sprite(visC.Rect("#aaa", "#aaa", 100, 50, 10, 10), "button1")

cv.start_text_input()
### CODE END

# for sprite in cv.get_sprites_with_tag("dot"):
#     sprite.delay(30)
#     sprite.change_pos(200, 100, 30)


def onKeyPress(event):
    cv.update_keyboard_input(event.keysym)
    
    ### CODE START - handle key presses
    keyCodeText.change_text('You pressed %s\n' % event.keysym)
    keyCodeText2.change_text(cv.get_text_input())
    ### CODE END

def get_mouse_coords(event):
    clickX = event.x
    clickY = event.y

    signals = cv.update_mouse_click(clickX, clickY)
    ### CODE START - handle mouse click
    if len(signals) > 0:
        if signals[0] == "button1":
            print("yay")
    ### CODE END


def update():
    ### CODE START - general update stuff

    ### CODE END

    cv.update()

    # Schedule the next frame
    canvas.after(int(1000/FPS), update)  # ~30 FPS

root.bind('<KeyPress>', onKeyPress)
root.bind('<Button-1>', get_mouse_coords)

update()
root.mainloop()