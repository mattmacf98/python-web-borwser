def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

def tree_to_list(tree_node, list):
    list.append(tree_node)
    for child in tree_node.children:
        tree_to_list(child, list)
    return list