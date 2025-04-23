from Blend import Blend
from DrawRect import DrawRect


def paint_tree(layout_object, display_list):
    if layout_object.should_paint():
        cmds = layout_object.paint()
    for child in layout_object.children:
        paint_tree(child, cmds)
    
    if layout_object.should_paint():
        cmds = layout_object.paint_effects(cmds)
    display_list.extend(cmds)

def paint_visual_effects(node, cmds, rect):
    opacity = float(node.style.get("opacity", "1.0"))
    blend_mode = node.style.get("mix-blend-mode")
    if node.style.get("overflow" "visible") == "clip":
        if not blend_mode:
            blend_mode = "source-over"
        border_radius = float(node.style.get("border-radius", "0px")[:-2])
        cmds.append(Blend(1.0, "destination-in", [DrawRect(rect, border_radius, "white")]))
    return [Blend(opacity, blend_mode, cmds)]