def create_mouse_get_pos(scale_ratio, offset_x, offset_y):
    """创建带有缩放参数的鼠标位置获取函数"""
    def mouse_get_pos():
        mouse_pos = pygame.mouse.get_pos()
        scaled_x = (mouse_pos[0] - offset_x) / scale_ratio
        scaled_y = (mouse_pos[1] - offset_y) / scale_ratio
        return scaled_x, scaled_y
    return mouse_get_pos

# 在绘制函数中
def draw_to_real_screen(physical_screen, virtual_canvas):
    phys_h = physical_screen.get_height()
    phys_w = physical_screen.get_width()
    virt_h = virtual_canvas.get_height()
    virt_w = virtual_canvas.get_width()
    scale_ratio = min(phys_h/virt_h, phys_w/virt_w)  # 修正了比例计算
    
    # 计算缩放后的尺寸和偏移
    scale_w = int(virt_w * scale_ratio)
    scale_h = int(virt_h * scale_ratio)
    offset_x = (phys_w - scale_w) // 2
    offset_y = (phys_h - scale_h) // 2
    
    # 创建带参数的鼠标位置函数
    global mouse_get_pos
    mouse_get_pos = create_mouse_get_pos(scale_ratio, offset_x, offset_y)
    
    # 继续绘制逻辑...
    canvas = pygame.transform.scale(virtual_canvas, (scale_w, scale_h))
    physical_screen.fill((0, 0, 0))  # 使用元组而不是Colors.BLACK
    physical_screen.blit(canvas, (offset_x, offset_y))

# 其他地方调用鼠标位置函数时保持不变
current_mouse = mouse_get_pos()