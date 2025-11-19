def test_pygame_import():
    import pygame
    assert pygame.get_sdl_version() is not None

def test_gui_module_exists():
    # non esegue la GUI, importa solo il file per sintassi
    import importlib.util, os
    path = os.path.join("src","gui","main_gui.py")
    spec = importlib.util.spec_from_file_location("main_gui", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "draw_universe")
