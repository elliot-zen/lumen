from lumen_notes_platform.contracts import NoteTreeNode


def test_note_tree_node_defaults_children_to_empty_tuple():
    node = NoteTreeNode(name="ES", path="ES", node_type="folder")
    assert node.children == ()
