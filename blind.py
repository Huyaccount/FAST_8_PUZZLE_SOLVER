import pygame
import sys
import random
from collections import deque
import time

GRADIENT_TOP_COLOR = (20, 0, 40)
GRADIENT_BOTTOM_COLOR = (10, 0, 20)
PRIMARY = (255, 0, 200)
PRIMARY_DARK = (180, 0, 140)
PRIMARY_CLICK = (140, 0, 100)
ACCENT_COLOR = (0, 220, 255)
SIDEBAR_BG = (25, 20, 30)
TEXT_PRIMARY = (230, 230, 240)
TEXT_SECONDARY = (170, 170, 180)
TEXT_PLACEHOLDER = (100, 100, 110)
BUTTON_SHADOW_COLOR = (5, 0, 10)
ERROR_COLOR = (255, 20, 20)
WARNING_COLOR = (255, 180, 0)
NUMBER_TILE_COLORS = {
    1: (0, 255, 100), 2: (255, 255, 0), 3: (255, 120, 0), 4: (0, 180, 255),
    5: (180, 0, 255), 6: (255, 0, 100), 7: (100, 255, 200), 8: (200, 200, 200)
}
SOLVED_BORDER_COLOR = (50, 255, 50)
SOLVED_BORDER_WIDTH = 2
TILE_BG_DEFAULT = (40, 30, 50)
SHAKE_BORDER_COLOR = ACCENT_COLOR
SIDEBAR_ITEM_BG = (35, 30, 45)
SIDEBAR_ITEM_HOVER_BG = (55, 50, 70)
SIDEBAR_ITEM_SELECTED_BG = PRIMARY

PATH_LIST_WIDTH = 260
PATH_LIST_MARGIN_X = 15
PATH_LIST_MARGIN_Y = 15
PATH_LIST_AREA_WIDTH = PATH_LIST_WIDTH + PATH_LIST_MARGIN_X * 2
PATH_LIST_ITEM_HEIGHT = 38
PATH_LIST_PADDING = 8
PATH_LIST_MAX_VISIBLE_STEPS = 8
PUZZLE_AREA_HORIZONTAL_PADDING_RATIO = 0.03

SHAKE_DURATION = 150
SHAKE_MAGNITUDE = 0
FLASH_INTERVAL = 60
DEFAULT_ANIM_SPEED_BLIND = 350
MIN_ANIM_SPEED_BLIND = 20
MAX_ANIM_SPEED_BLIND = 1200
SLIDER_TRACK_H_BLIND = 10
SLIDER_HANDLE_W_BLIND = 10
SLIDER_HANDLE_H_BLIND = 28
SLIDER_HANDLE_RADIUS = 3

TARGET_GOAL_STATES = {(1,2,3,4,5,6,7,8,9), (1,4,7,2,5,8,3,6,9), (1,2,3,8,9,4,7,6,5)}
TARGET_GOAL_LIST = list(TARGET_GOAL_STATES)

WIDTH, HEIGHT = 0,0

def draw_gradient_background(surface, top_color, bottom_color):
    height = surface.get_height(); width = surface.get_width(); rect_strip = pygame.Rect(0,0,width,1)
    for y in range(height):
        r,g,b = [top_color[i] + (bottom_color[i]-top_color[i])*y/height for i in range(3)]
        rect_strip.top = y; pygame.draw.rect(surface, (int(r),int(g),int(b)), rect_strip)

def truncate_text(text, font, max_width, ellipsis="..."):
    if not text or font.size(text)[0] <= max_width: return text
    truncated = ""
    for char in text:
        if font.size(truncated + char + ellipsis)[0] > max_width: break
        truncated += char
    return truncated + ellipsis

def render_text_wrapped(text, font, color, max_width, surf, start_x, start_y, line_spacing=5, center_x=False, rect_center_in=None):
    words = text.split(' '); lines = []; current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width: current_line = test_line
        else:
            if current_line: lines.append(current_line.strip())
            current_line = word + " "
            if font.size(current_line)[0] > max_width: lines.append(truncate_text(word,font,max_width)); current_line=""
    if current_line: lines.append(current_line.strip())
    y_off = 0
    total_height = 0
    for i, ln_txt in enumerate(lines):
        if not ln_txt: continue
        ln_surf = font.render(ln_txt, True, color)
        ln_r = ln_surf.get_rect(centerx=rect_center_in.centerx, top=start_y+y_off) if center_x and rect_center_in else ln_surf.get_rect(left=start_x, top=start_y+y_off)
        surf.blit(ln_surf, ln_r)
        current_line_height = font.get_height()
        y_off += current_line_height
        total_height += current_line_height
        if i < len(lines) -1 :
            y_off += line_spacing
            total_height += line_spacing
    return total_height

def get_inversions(st): st_nb=[x for x in st if x!=9]; inv=0; L=len(st_nb); [(inv:=inv+1) for i in range(L) for j in range(i+1,L) if st_nb[i]>st_nb[j]]; return inv
def is_solvable(st): return (9 in st and len(st)==9) and get_inversions(st)%2==0
def apply_move(st, mv_dir):
    s=list(st);
    try: bi=s.index(9)
    except ValueError: return None
    r,c=divmod(bi,3); dr,dc={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}.get(mv_dir[0].upper(),(0,0))
    if dr==0 and dc==0 and mv_dir[0].upper() not in ['U','D','L','R']: return None
    nr,nc=r+dr,c+dc
    if 0<=nr<3 and 0<=nc<3: ni=nr*3+nc; s[bi],s[ni]=s[ni],s[bi]; return tuple(s)
    return None
def generate_specific_solvable_states(num_sts, max_rev_depth=10, req_start_val=1):
    gen_sts=set(); att=0; max_att=num_sts*200
    while len(gen_sts)<num_sts and att<max_att:
        att+=1; curr_st=random.choice(TARGET_GOAL_LIST); depth=random.randint(max(1,max_rev_depth//2),max_rev_depth); tmp_st=curr_st
        mvs=['Up','Down','Left','Right']; valid_seq=True
        for _ in range(depth):
            poss_next_sts={m:apply_move(tmp_st,m) for m in mvs if apply_move(tmp_st,m) is not None}
            if not poss_next_sts: valid_seq=False; break
            tmp_st=random.choice(list(poss_next_sts.values()))
        if not valid_seq: continue
        if tmp_st[0]==req_start_val and is_solvable(tmp_st): gen_sts.add(tmp_st)
    if len(gen_sts)<num_sts: return list(gen_sts)[:num_sts] if gen_sts else [(1,2,3,4,5,9,7,8,6)]
    return list(gen_sts)[:num_sts]

class AnimatedTile:
    def __init__(self, val, x, y, s):
        self.value=val; self.size=s; self.inner_size=int(s*0.92); self.rect=pygame.Rect(x,y,s,s)
        self.inner_rect=pygame.Rect(x+(s-self.inner_size)//2,y+(s-self.inner_size)//2,self.inner_size,self.inner_size)
        self.cx,self.cy,self.tx,self.ty = float(x),float(y),float(x),float(y)
        self.speed=0.28; self.is_shaking=False; self.shake_start=0; self.shake_dur=SHAKE_DURATION; self.shake_mag=SHAKE_MAGNITUDE
        self.orig_x,self.orig_y = float(x),float(y); self.radius = max(5,int(self.inner_size*0.08))
    def set_target(self,x,y):
        if not self.is_shaking: self.tx,self.ty=float(x),float(y); self.orig_x,self.orig_y=self.cx,self.cy
    def shake(self):
        if not self.is_shaking: self.is_shaking=True; self.shake_start=pygame.time.get_ticks()
    def update(self):
        now=pygame.time.get_ticks()
        if self.is_shaking:
            el_sh = now-self.shake_start
            if el_sh>=self.shake_dur: self.is_shaking=False
        else:
            dx,dy = self.tx-self.cx, self.ty-self.cy
            if abs(dx)>0.5 or abs(dy)>0.5: self.cx+=dx*self.speed; self.cy+=dy*self.speed
            else: self.cx,self.cy=self.tx,self.ty
        self.rect.x,self.rect.y=int(self.cx),int(self.cy); self.inner_rect.center=self.rect.center
    def draw(self, surf, font_s, is_final_goal=False):
        if self.value == 9:
            if self.is_shaking:
                now = pygame.time.get_ticks()
                flash_color = SHAKE_BORDER_COLOR if (now // FLASH_INTERVAL) % 2 == 0 else tuple(max(0, c-80) for c in SHAKE_BORDER_COLOR)
                pygame.draw.rect(surf, flash_color, self.rect.inflate(-self.size*0.06,-self.size*0.06),border_radius=self.radius,width=3)
            return
        bg_c = NUMBER_TILE_COLORS.get(self.value, TILE_BG_DEFAULT); pygame.draw.rect(surf,bg_c,self.inner_rect,border_radius=self.radius)
        txt_s = font_s.render(str(self.value),True, (0,0,0) if self.value in [2,8] else TEXT_PRIMARY); surf.blit(txt_s,txt_s.get_rect(center=self.inner_rect.center))
        if is_final_goal: pygame.draw.rect(surf,SOLVED_BORDER_COLOR,self.inner_rect,border_radius=self.radius,width=SOLVED_BORDER_WIDTH)
    def is_at_target(self): return not self.is_shaking and abs(self.cx-self.tx)<0.5 and abs(self.cy-self.ty)<0.5

class Button:
    def __init__(self,x,y,w,h,txt,col=PRIMARY,hcol=PRIMARY_DARK,shcol=BUTTON_SHADOW_COLOR, clk_col=PRIMARY_CLICK, radius=8):
        self.rect=pygame.Rect(x,y,w,h);self.text=txt;self.base_color=col;self.hover_color=hcol;self.shadow_color=shcol
        self.click_color = clk_col
        self.is_hovered=False;self.radius=radius;self.sh_offset=3
        self.is_pressed = False
    def draw(self,surf,font_s):
        curr_c = self.base_color
        if self.is_pressed: curr_c = self.click_color
        elif self.is_hovered: curr_c = self.hover_color
        
        sh_r=self.rect.move(self.sh_offset,self.sh_offset)
        pygame.draw.rect(surf,self.shadow_color,sh_r,border_radius=self.radius)
        pygame.draw.rect(surf,curr_c,self.rect,border_radius=self.radius)
        txt_s=font_s.render(self.text,True,TEXT_PRIMARY)
        surf.blit(txt_s,txt_s.get_rect(center=self.rect.center))
    def check_hover(self,mpos): self.is_hovered=self.rect.collidepoint(mpos)
    def handle_event(self,event,mpos):
        clicked_this_frame = False
        self.check_hover(mpos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered: self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.is_hovered: clicked_this_frame = True
            self.is_pressed = False
        return clicked_this_frame

class SpeedSlider:
    def __init__(self, handle_width, handle_height, track_color, handle_color, min_val, max_val, initial_val):
        self.min_value = min_val; self.max_value = max_val; self.current_value = initial_val
        self.track_rect = pygame.Rect(0,0,0,0); self.handle_rect = pygame.Rect(0,0, handle_width, handle_height)
        self.slider_min_x = 0; self.slider_max_x = 0; self.slider_range_x = 0
        self.track_color = track_color; self.handle_color = handle_color
        self.handle_hover_color = tuple(min(255, c+30) for c in handle_color)
        self.is_dragging = False; self.active = True; self.handle_radius = SLIDER_HANDLE_RADIUS

    def update_layout(self, x_track_start, y_center, track_width):
        track_h = SLIDER_TRACK_H_BLIND
        self.track_rect = pygame.Rect(x_track_start, y_center - track_h // 2, track_width, track_h)
        self.slider_min_x = self.track_rect.left # Handle aligns with edge
        self.slider_max_x = self.track_rect.right - self.handle_rect.width # Handle aligns with edge
        self.slider_range_x = self.slider_max_x - self.slider_min_x
        if self.slider_range_x <= 0: self.slider_range_x = 1
        self._update_handle_pos_from_value()

    def _update_handle_pos_from_value(self):
        if not self.track_rect.height: return
        percentage = (self.current_value - self.min_value) / (self.max_value - self.min_value) if self.max_value != self.min_value else 0.5
        percentage = max(0, min(1, percentage))
        handle_x = self.slider_min_x + percentage * self.slider_range_x
        self.handle_rect.left = int(handle_x)
        self.handle_rect.centery = self.track_rect.centery


    def _update_value_from_handle_pos(self):
        percentage = (self.handle_rect.left - self.slider_min_x) / self.slider_range_x if self.slider_range_x else 0
        self.current_value = self.min_value + percentage * (self.max_value - self.min_value)
        self.current_value = max(self.min_value, min(self.max_value, self.current_value))

    def handle_event(self, event, mouse_pos, time_per_move_ref_list):
        if not self.active: return False
        changed_val = False
        is_handle_hovered = self.handle_rect.collidepoint(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_handle_hovered or self.track_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                if self.track_rect.collidepoint(mouse_pos) and not is_handle_hovered:
                    self.handle_rect.left = max(self.slider_min_x, min(mouse_pos[0] - self.handle_rect.width // 2, self.slider_max_x))
                self._update_value_from_handle_pos(); time_per_move_ref_list[0] = int(self.current_value); changed_val = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging: self.is_dragging = False; changed_val = True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.handle_rect.left = max(self.slider_min_x, min(mouse_pos[0] - self.handle_rect.width // 2, self.slider_max_x))
            self._update_value_from_handle_pos(); time_per_move_ref_list[0] = int(self.current_value); changed_val = True
        return changed_val

    def draw(self, screen_surf, font_s, mouse_pos):
        if not self.active or not self.track_rect.height: return
        pygame.draw.rect(screen_surf, self.track_color, self.track_rect, border_radius=self.track_rect.height//2)
        
        current_handle_color = self.handle_color
        if self.handle_rect.collidepoint(mouse_pos) or self.is_dragging:
            current_handle_color = self.handle_hover_color
        pygame.draw.rect(screen_surf, current_handle_color, self.handle_rect, border_radius=self.handle_radius)
        
        speed_text = f"{int(self.current_value)}ms"; text_surf = font_s.render(speed_text,True,TEXT_SECONDARY)
        text_r = text_surf.get_rect(centerx=self.track_rect.centerx, bottom=self.track_rect.top-10); screen_surf.blit(text_surf,text_r)
        
        fast_lbl_s = font_s.render("Nhanh",True,ACCENT_COLOR); slow_lbl_s = font_s.render("Chậm",True,ACCENT_COLOR)
        screen_surf.blit(fast_lbl_s, fast_lbl_s.get_rect(midright=(self.track_rect.left-15, self.track_rect.centery)))
        screen_surf.blit(slow_lbl_s, slow_lbl_s.get_rect(midleft=(self.track_rect.right+15, self.track_rect.centery)))
    def get_value(self): return int(self.current_value)

def find_common_path(init_beliefs, targets_set):
    if not init_beliefs: return None
    init_b_tuple = tuple(sorted(init_beliefs))
    if all(st in targets_set for st in init_b_tuple): return []
    q = deque([(init_b_tuple, [])]); visited = {init_b_tuple}
    mvs = ['Up','Down','Left','Right']; max_iter=250000; it=0
    while q:
        it+=1;
        if it>max_iter: return None
        curr_b_tuple, curr_path = q.popleft()
        for mv in mvs:
            next_b_list = [apply_move(st,mv) or st for st in curr_b_tuple]
            next_b_tuple_unsorted = [s for s in next_b_list if s is not None]
            if len(next_b_tuple_unsorted) != len(curr_b_tuple):
                 continue
            next_b_tuple = tuple(sorted(next_b_tuple_unsorted))

            if next_b_tuple not in visited:
                if all(st in targets_set for st in next_b_tuple): return curr_path + [mv]
                visited.add(next_b_tuple); q.append((next_b_tuple, curr_path+[mv]))
    return None

def run_blind_search():
    global WIDTH, HEIGHT; local_W, local_H = WIDTH, HEIGHT
    if not pygame.get_init(): pygame.init(); pygame.font.init()
    try:
        screen_surf = pygame.display.get_surface()
        if screen_surf is None: screen_surf = pygame.display.set_mode((local_W,local_H), pygame.FULLSCREEN if pygame.display.Info().current_w==local_W else 0)
        else: local_W,local_H = screen_surf.get_size()
        pygame.display.set_caption("Blind Search - 8 Puzzle")
    except pygame.error: local_W,local_H=1280,720; screen_surf = pygame.display.set_mode((local_W,local_H))

    clock = pygame.time.Clock()
    vn_fonts = ["Bahnschrift","Arial","Segoe UI","Calibri","Roboto"]
    font_name_sel = pygame.font.get_default_font(); sys_f_list = pygame.font.get_fonts()
    for f_n in vn_fonts:
        if f_n.lower().replace(" ","") in [s.lower().replace(" ","") for s in sys_f_list]: font_name_sel=f_n; break
    try:
        font_ui = pygame.font.SysFont(font_name_sel, 22, bold=False)
        title_f = pygame.font.SysFont(font_name_sel, 48, bold=True)
        puzzle_f_small = pygame.font.SysFont(font_name_sel, 32, bold=True)
        puzzle_f_large = pygame.font.SysFont(font_name_sel, 50, bold=True)
        move_info_f = pygame.font.SysFont(font_name_sel, 28, bold=True)
        path_list_font = pygame.font.SysFont(font_name_sel, 20)
    except Exception:
        font_ui=pygame.font.Font(None,24); title_f=pygame.font.Font(None,48); puzzle_f_small=pygame.font.Font(None,32);
        puzzle_f_large=pygame.font.Font(None,50); move_info_f=pygame.font.Font(None,30); path_list_font=pygame.font.Font(None,22)

    gui_state="generating"; init_sts_list=[]; common_path_res=None; all_anim_puzzles=[]; curr_anim_st_tuples=[]
    curr_mv_idx=0;
    time_per_move_wrapper = [DEFAULT_ANIM_SPEED_BLIND]
    last_anim_upd=0
    status_msg_display="Searching for solvable configurations..."
    num_init_sts=2; gen_max_depth=10; max_retries_val=4; retry_c=0

    btn_w, btn_h = 150, 45
    btn_margin_bottom = 25; btn_margin_controls_area = 20

    back_btn = Button(0,0, btn_w,btn_h,"To Menu")
    auto_mode_blind = True
    auto_btn_blind = Button(0,0, btn_w,btn_h, "Auto: ON")
    reset_btn_blind = Button(0,0, btn_w,btn_h, "Reset All")
    next_btn_blind = Button(0,0, btn_w, btn_h, "Next Step")

    speed_slider_blind = SpeedSlider(SLIDER_HANDLE_W_BLIND, SLIDER_HANDLE_H_BLIND, tuple(max(0,c-20) for c in SIDEBAR_BG), ACCENT_COLOR, MIN_ANIM_SPEED_BLIND, MAX_ANIM_SPEED_BLIND, DEFAULT_ANIM_SPEED_BLIND)
    slider_active_in_blind = False

    gen_ok=False
    anim_puz_grid_s = 0
    puzzles_start_x = 0
    puzzles_start_y = 0
    puz_space = 0

    TOP_MARGIN = 50
    PUZZLE_AREA_HORIZONTAL_PADDING_PX = local_W * PUZZLE_AREA_HORIZONTAL_PADDING_RATIO
    BOTTOM_CONTROLS_AREA_HEIGHT = btn_h + btn_margin_bottom + btn_margin_controls_area + move_info_f.get_height() + 20

    status_msg_y_pos = TOP_MARGIN + title_f.get_height() + 25
    status_text_height = 0
    puzzle_area_top_y_calc = 0
    puzzle_area_bottom_y_calc = 0
    available_puzzle_area_h_calc = 0
    temp_surf_for_calc = pygame.Surface((1,1))

    while common_path_res is None and retry_c < max_retries_val:
        retry_c+=1;
        draw_gradient_background(screen_surf, GRADIENT_TOP_COLOR, GRADIENT_BOTTOM_COLOR)
        title_s = title_f.render("BLIND SEARCH MODE", True, ACCENT_COLOR)
        screen_surf.blit(title_s, title_s.get_rect(centerx=local_W//2, y=TOP_MARGIN))
        search_msg_txt = f"Generating States... (Attempt {retry_c})"
        render_text_wrapped(search_msg_txt, font_ui, TEXT_SECONDARY, local_W*0.7, screen_surf,0,status_msg_y_pos,line_spacing=6,center_x=True,rect_center_in=screen_surf.get_rect())
        pygame.display.flip(); pygame.time.delay(150); pygame.event.pump()

        init_sts_list = generate_specific_solvable_states(num_init_sts,gen_max_depth,1)
        if not init_sts_list: status_msg_display="Error: Failed to generate initial states."; gui_state="no_path"; gen_ok=False; break
        gen_ok=True; common_path_res = find_common_path(init_sts_list,TARGET_GOAL_STATES)

    status_text_height = render_text_wrapped(status_msg_display,font_ui,TEXT_SECONDARY,local_W*0.8,temp_surf_for_calc,0,0,line_spacing=6,center_x=True,rect_center_in=screen_surf.get_rect())

    if common_path_res is not None:
        gui_state="animating";
        slider_active_in_blind = True
        curr_anim_st_tuples=list(init_sts_list); num_p=len(init_sts_list);

        effective_puzzle_area_width = local_W - (PATH_LIST_AREA_WIDTH if num_p > 0 else 0) - PUZZLE_AREA_HORIZONTAL_PADDING_PX * 2
        slider_total_height_needed = SLIDER_HANDLE_H_BLIND + 60 # more space for labels

        puzzle_area_top_y_calc = TOP_MARGIN + title_f.get_height() + status_text_height + 20 + slider_total_height_needed
        puzzle_area_bottom_y_calc = local_H - BOTTOM_CONTROLS_AREA_HEIGHT
        available_puzzle_area_h_calc = puzzle_area_bottom_y_calc - puzzle_area_top_y_calc
        available_puzzle_area_h_calc = max(180, available_puzzle_area_h_calc)

        max_t_s,min_t_s = 130, 35

        tile_s_based_on_width = (effective_puzzle_area_width / num_p if num_p > 0 else effective_puzzle_area_width) * 0.8 / 3
        tile_s_based_on_height = available_puzzle_area_h_calc * 0.85 / 3
        anim_t_s = min(tile_s_based_on_width, tile_s_based_on_height)
        anim_t_s = max(min_t_s, min(anim_t_s, max_t_s)); anim_t_s = max(1, int(anim_t_s))

        anim_puz_grid_s = anim_t_s*3
        puz_space = anim_t_s * 0.35
        total_puzzles_width_val = num_p * anim_puz_grid_s + max(0, num_p-1) * puz_space

        puzzles_start_x_base = PUZZLE_AREA_HORIZONTAL_PADDING_PX
        puzzles_start_x = puzzles_start_x_base + (effective_puzzle_area_width - total_puzzles_width_val) / 2

        puzzles_start_y = puzzle_area_top_y_calc + (available_puzzle_area_h_calc - anim_puz_grid_s) / 2
        puzzles_start_y = max(puzzle_area_top_y_calc, puzzles_start_y)

        all_anim_puzzles = []
        for i,init_st_val in enumerate(init_sts_list):
            anim_sx=puzzles_start_x+i*(anim_puz_grid_s+puz_space); anim_sy=puzzles_start_y
            puz_ts=[AnimatedTile(val,anim_sx+c*anim_t_s,anim_sy+r_tile*anim_t_s,anim_t_s) for idx,val in enumerate(init_st_val) for r_tile,c in [divmod(idx,3)]]
            all_anim_puzzles.append(puz_ts)

        slider_track_w_val = local_W * 0.4
        slider_center_x_area = (local_W - (PATH_LIST_AREA_WIDTH if common_path_res else 0)) / 2 + (PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res else 0)
        slider_track_x_start = slider_center_x_area - slider_track_w_val / 2
        slider_y_center_val = TOP_MARGIN + title_f.get_height() + status_text_height + 35 + SLIDER_HANDLE_H_BLIND // 2
        speed_slider_blind.update_layout(slider_track_x_start, slider_y_center_val, slider_track_w_val)

        last_anim_upd=pygame.time.get_ticks()
    elif not gen_ok: slider_active_in_blind = False
    else: status_msg_display=f"No common path found after {max_retries_val} attempts."; gui_state="no_path"; slider_active_in_blind = False

    running_loop=True
    all_tiles_settled_current_frame = True

    while running_loop:
        mpos=pygame.mouse.get_pos()
        for evt in pygame.event.get():
            if evt.type==pygame.QUIT: running_loop=False
            elif evt.type==pygame.KEYDOWN and evt.key==pygame.K_ESCAPE: running_loop=False
            
            if back_btn.handle_event(evt,mpos): running_loop=False

            if slider_active_in_blind:
                speed_slider_blind.handle_event(evt, mpos, time_per_move_wrapper)

            if gui_state in ["animating", "finished"] and common_path_res:
                if auto_btn_blind.handle_event(evt,mpos):
                    auto_mode_blind = not auto_mode_blind
                    auto_btn_blind.text = "Auto: ON" if auto_mode_blind else "Auto: OFF"
                    if auto_mode_blind: last_anim_upd = pygame.time.get_ticks()
                elif reset_btn_blind.handle_event(evt,mpos):
                    curr_mv_idx = 0; last_anim_upd = pygame.time.get_ticks(); curr_anim_st_tuples=list(init_sts_list)
                    if all_anim_puzzles and init_sts_list and anim_puz_grid_s > 0 and len(all_anim_puzzles) > 0 and len(all_anim_puzzles[0]) > 0:
                         anim_t_s_val=all_anim_puzzles[0][0].size
                         for i, p_tiles in enumerate(all_anim_puzzles):
                            target_st_val = init_sts_list[i]; val_pos_map={v:idx_v for idx_v,v in enumerate(target_st_val)}
                            anim_sx=puzzles_start_x+i*(anim_puz_grid_s+puz_space); anim_sy=puzzles_start_y
                            for t_o in p_tiles:
                                if t_o.value in val_pos_map: new_i_val=val_pos_map[t_o.value]; r_t,c_t=divmod(new_i_val,3); t_o.set_target(anim_sx+c_t*anim_t_s_val,anim_sy+r_t*anim_t_s_val)
                elif next_btn_blind.handle_event(evt,mpos) and not auto_mode_blind and curr_mv_idx < len(common_path_res):
                    current_all_ready = True
                    if all_anim_puzzles:
                        for p_ts_list_check in all_anim_puzzles:
                            if not all(t.is_at_target() for t in p_ts_list_check if not t.is_shaking) or \
                               any(t.value == 9 and t.is_shaking for t in p_ts_list_check):
                                current_all_ready = False
                                break
                    
                    if current_all_ready:
                        mv_apply=common_path_res[curr_mv_idx]; upd_indices=[]
                        for i,curr_p_st in enumerate(curr_anim_st_tuples):
                            next_s=apply_move(curr_p_st,mv_apply)
                            if next_s: curr_anim_st_tuples[i]=next_s; upd_indices.append(i)
                            else:
                                bl_t=None
                                if i < len(all_anim_puzzles):
                                    bl_t = next((t for t in all_anim_puzzles[i] if t.value==9),None)
                                if bl_t: bl_t.shake()
                        if upd_indices and all_anim_puzzles and anim_puz_grid_s > 0 and len(all_anim_puzzles) > 0 and len(all_anim_puzzles[0]) > 0:
                            anim_t_s_val=all_anim_puzzles[0][0].size
                            for p_idx in upd_indices:
                                if p_idx < len(all_anim_puzzles) and p_idx < len(curr_anim_st_tuples):
                                    anim_sx_val=puzzles_start_x+p_idx*(anim_puz_grid_s+puz_space); anim_sy_val=puzzles_start_y
                                    ts_to_upd=all_anim_puzzles[p_idx]; target_s_val=curr_anim_st_tuples[p_idx]
                                    val_pos_map={v:i_v for i_v,v in enumerate(target_s_val)}
                                    for t_o in ts_to_upd:
                                        if t_o.value in val_pos_map: new_i_val=val_pos_map[t_o.value]; r_t,c_t=divmod(new_i_val,3); t_o.set_target(anim_sx_val+c_t*anim_t_s_val,anim_sy_val+r_t*anim_t_s_val)
                        
                        curr_mv_idx+=1
                        last_anim_upd=pygame.time.get_ticks()

        all_tiles_settled_current_frame = True
        if gui_state in ["animating", "finished"] and all_anim_puzzles:
            for i,p_tiles_list in enumerate(all_anim_puzzles):
                for t_obj in p_tiles_list:
                    t_obj.update()
                    if not t_obj.is_at_target() and not t_obj.is_shaking:
                        all_tiles_settled_current_frame = False
        elif not all_anim_puzzles and gui_state in ["animating", "finished"]:
            all_tiles_settled_current_frame = True

        if gui_state == "animating" and common_path_res and curr_mv_idx < len(common_path_res):
            if auto_mode_blind and all_tiles_settled_current_frame and \
               (pygame.time.get_ticks() - last_anim_upd >= time_per_move_wrapper[0]):
                mv_apply = common_path_res[curr_mv_idx]
                upd_indices = []
                for i, curr_p_st_tuple in enumerate(curr_anim_st_tuples):
                    next_s = apply_move(curr_p_st_tuple, mv_apply)
                    if next_s:
                        curr_anim_st_tuples[i] = next_s
                        upd_indices.append(i)
                    else:
                        blank_tile_to_shake = None
                        if i < len(all_anim_puzzles):
                             blank_tile_to_shake = next((t for t in all_anim_puzzles[i] if t.value == 9), None)
                        if blank_tile_to_shake:
                            blank_tile_to_shake.shake()

                if upd_indices and all_anim_puzzles and anim_puz_grid_s > 0 and len(all_anim_puzzles) > 0 and len(all_anim_puzzles[0]) > 0:
                    anim_t_s_val = all_anim_puzzles[0][0].size
                    for p_idx in upd_indices:
                        if p_idx < len(all_anim_puzzles) and p_idx < len(curr_anim_st_tuples):
                            anim_sx_val = puzzles_start_x + p_idx * (anim_puz_grid_s + puz_space)
                            anim_sy_val = puzzles_start_y
                            tiles_to_update = all_anim_puzzles[p_idx]
                            target_state_val = curr_anim_st_tuples[p_idx]
                            value_pos_map = {v: idx_v for idx_v, v in enumerate(target_state_val)}
                            for t_obj in tiles_to_update:
                                if t_obj.value in value_pos_map:
                                    new_idx_val = value_pos_map[t_obj.value]
                                    r_t, c_t = divmod(new_idx_val, 3)
                                    t_obj.set_target(anim_sx_val + c_t * anim_t_s_val, anim_sy_val + r_t * anim_t_s_val)
                
                curr_mv_idx += 1
                last_anim_upd = pygame.time.get_ticks()

        draw_gradient_background(screen_surf, GRADIENT_TOP_COLOR, GRADIENT_BOTTOM_COLOR)
        title_txt="BLIND SEARCH RESULT" if gui_state!="generating" else "BLIND SEARCH MODE"
        title_s=title_f.render(title_txt,True,ACCENT_COLOR)
        title_rect = title_s.get_rect(centerx=local_W//2,y=TOP_MARGIN)
        screen_surf.blit(title_s,title_rect)

        current_bottom_of_text = title_rect.bottom + 25
        status_text_height_render = render_text_wrapped(status_msg_display,font_ui,TEXT_SECONDARY,local_W*0.8,screen_surf,0,current_bottom_of_text,line_spacing=6,center_x=True,rect_center_in=screen_surf.get_rect())
        current_bottom_of_text += status_text_height_render

        back_btn.rect.topleft = (20, 20) # Top-left corner
        back_btn.draw(screen_surf,font_ui)

        if gui_state=="no_path":
            if gen_ok and init_sts_list:
                available_height_for_no_path_grid = local_H - current_bottom_of_text - (btn_h + btn_margin_bottom + 40)
                available_height_for_no_path_grid = max(180, available_height_for_no_path_grid)
                grid_cols_val=min(len(init_sts_list),2);
                grid_rows_val=(len(init_sts_list)+grid_cols_val-1)//grid_cols_val

                puz_w_per_col_no_path = (local_W * 0.65) / grid_cols_val
                puz_h_per_row_no_path = available_height_for_no_path_grid / grid_rows_val
                tile_s_val = min(puz_w_per_col_no_path * 0.8, puz_h_per_row_no_path * 0.8) / 3
                tile_s_val = max(35, min(tile_s_val, 110))
                tile_s_val = int(tile_s_val)

                actual_puzzle_grid_width = tile_s_val * 3
                actual_puzzle_grid_height = tile_s_val * 3

                h_spacing_between_puzzles = tile_s_val * 0.8
                total_preview_grid_width = grid_cols_val * actual_puzzle_grid_width + max(0, grid_cols_val-1) * h_spacing_between_puzzles
                total_preview_grid_height = grid_rows_val * actual_puzzle_grid_height + max(0, grid_rows_val-1) * (h_spacing_between_puzzles / 2)

                start_x_grid_val = (local_W - total_preview_grid_width) / 2
                start_y_grid_val = current_bottom_of_text + 25 + (available_height_for_no_path_grid - total_preview_grid_height) / 2
                start_y_grid_val = max(current_bottom_of_text + 25, start_y_grid_val)

                for i,init_st in enumerate(init_sts_list):
                    r_idx,c_idx=divmod(i,grid_cols_val)
                    px = start_x_grid_val + c_idx*(actual_puzzle_grid_width + h_spacing_between_puzzles)
                    py = start_y_grid_val + r_idx*(actual_puzzle_grid_height + h_spacing_between_puzzles / 2)
                    for idx,val_t in enumerate(init_st):
                        r_tile,c_tile=divmod(idx,3); xt,yt=px+c_tile*tile_s_val,py+r_tile*tile_s_val
                        if val_t==9: continue
                        pad_val=max(1,int(tile_s_val*0.02)); inner_s_val=tile_s_val-2*pad_val
                        rect_t_val=pygame.Rect(xt+pad_val,yt+pad_val,inner_s_val,inner_s_val)
                        bg_color_val=NUMBER_TILE_COLORS.get(val_t,TILE_BG_DEFAULT)
                        pygame.draw.rect(screen_surf,bg_color_val,rect_t_val,border_radius=max(3,int(inner_s_val*0.08)))
                        txt_color = (0,0,0) if val_t in [2,8] else TEXT_PRIMARY
                        screen_surf.blit(puzzle_f_small.render(str(val_t),True,txt_color),puzzle_f_small.render(str(val_t),True,txt_color).get_rect(center=rect_t_val.center))

        elif gui_state in ["animating","finished"]:
            slider_y_center_pos = current_bottom_of_text + 30 + SLIDER_HANDLE_H_BLIND // 2
            if slider_active_in_blind :
                effective_path_list_width = PATH_LIST_AREA_WIDTH if common_path_res else 0
                slider_w_area = local_W - effective_path_list_width - PUZZLE_AREA_HORIZONTAL_PADDING_PX * 2
                slider_track_w_val = min(slider_w_area * 0.6, local_W * 0.4)

                slider_x_base = PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res and num_p > 0 else 0
                slider_track_x_start = slider_x_base + (slider_w_area - slider_track_w_val) / 2
                if not common_path_res or num_p == 0:
                    slider_track_x_start = (local_W - slider_track_w_val) / 2
                
                speed_slider_blind.update_layout(slider_track_x_start, slider_y_center_pos, slider_track_w_val)
                speed_slider_blind.draw(screen_surf, font_ui, mpos)

            if all_anim_puzzles:
                for i,p_tiles_list_draw in enumerate(all_anim_puzzles):
                    p_st = curr_anim_st_tuples[i] if i < len(curr_anim_st_tuples) else None
                    is_this_p_goal = (gui_state=="finished" or (gui_state=="animating" and common_path_res and curr_mv_idx==len(common_path_res))) and \
                                     (p_st and p_st in TARGET_GOAL_STATES)
                    for t_obj_draw in p_tiles_list_draw:
                        is_t_final_pos=False
                        if is_this_p_goal and p_st:
                            try: curr_idx_t=list(p_st).index(t_obj_draw.value)
                            except ValueError: curr_idx_t=-1
                            if curr_idx_t!=-1 and t_obj_draw.value!=9 and p_st[curr_idx_t]==t_obj_draw.value: is_t_final_pos=True
                        t_obj_draw.draw(screen_surf,puzzle_f_large,is_t_final_pos)

            path_list_rect = None
            if common_path_res:
                path_list_effective_y_start = TOP_MARGIN
                path_list_total_h = local_H - path_list_effective_y_start - PATH_LIST_MARGIN_Y
                path_list_rect = pygame.Rect(local_W - PATH_LIST_AREA_WIDTH + PATH_LIST_MARGIN_X, path_list_effective_y_start, PATH_LIST_WIDTH, path_list_total_h)
                
                path_list_inner_rect = path_list_rect.inflate(-PATH_LIST_PADDING*2, -PATH_LIST_PADDING*2)
                pygame.draw.rect(screen_surf, SIDEBAR_BG, path_list_rect, border_radius=10)
                
                path_title_s = font_ui.render("MOVE SEQUENCE", True, ACCENT_COLOR)
                path_title_r = path_title_s.get_rect(centerx=path_list_rect.centerx, top=path_list_rect.top + PATH_LIST_PADDING + 5)
                screen_surf.blit(path_title_s, path_title_r)

                path_item_y = path_title_r.bottom + 15
                num_before = (PATH_LIST_MAX_VISIBLE_STEPS -1) // 2
                start_display_idx_path = max(0, curr_mv_idx - num_before)
                if curr_mv_idx == len(common_path_res) and len(common_path_res) > 0:
                    start_display_idx_path = max(0, curr_mv_idx -1 - num_before)
                
                end_display_idx_path = min(len(common_path_res), start_display_idx_path + PATH_LIST_MAX_VISIBLE_STEPS)
                if end_display_idx_path - start_display_idx_path < PATH_LIST_MAX_VISIBLE_STEPS:
                    start_display_idx_path = max(0, end_display_idx_path - PATH_LIST_MAX_VISIBLE_STEPS)

                for i in range(start_display_idx_path, end_display_idx_path):
                    if path_item_y + PATH_LIST_ITEM_HEIGHT > path_list_rect.bottom - PATH_LIST_PADDING: break
                    move_str = f"S{i+1}: {common_path_res[i]}"
                    item_r = pygame.Rect(path_list_inner_rect.x, path_item_y, path_list_inner_rect.width, PATH_LIST_ITEM_HEIGHT - PATH_LIST_PADDING // 2)
                    
                    is_current_highlight = (i == curr_mv_idx)
                    if curr_mv_idx == len(common_path_res) and i == len(common_path_res) -1 : is_current_highlight = True
                    
                    item_bg_c = SIDEBAR_ITEM_SELECTED_BG if is_current_highlight else SIDEBAR_ITEM_BG
                    pygame.draw.rect(screen_surf, item_bg_c, item_r, border_radius=5)
                    move_text_surf = path_list_font.render(truncate_text(move_str, path_list_font, item_r.width - 15), True, TEXT_PRIMARY)
                    screen_surf.blit(move_text_surf, move_text_surf.get_rect(midleft=(item_r.left + 10, item_r.centery)))
                    path_item_y += PATH_LIST_ITEM_HEIGHT

            control_btn_y_pos = local_H - btn_margin_bottom - btn_h
            control_btn_spacing = 15

            all_control_buttons = [auto_btn_blind, next_btn_blind, reset_btn_blind]
            total_control_btns_width_current = sum(b.rect.width for b in all_control_buttons) + max(0, len(all_control_buttons)-1) * control_btn_spacing
            
            control_area_w = local_W - (PATH_LIST_AREA_WIDTH if common_path_res else 0) - PUZZLE_AREA_HORIZONTAL_PADDING_PX * 2
            control_btns_start_x_pos = (PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res else 0) + (control_area_w - total_control_btns_width_current) / 2
            control_btns_start_x_pos = max(PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res else 20, control_btns_start_x_pos)

            current_x_btn = control_btns_start_x_pos
            for btn in all_control_buttons:
                btn.rect.topleft = (current_x_btn, control_btn_y_pos)
                btn.draw(screen_surf, font_ui)
                current_x_btn += btn.rect.width + control_btn_spacing

            move_text_y_final_pos = control_btn_y_pos - move_info_f.get_height() - 10
            move_text_center_x_pos = control_btns_start_x_pos + total_control_btns_width_current / 2

            if common_path_res:
                mv_txt_disp=""; final_step_comp=(gui_state=="finished" or (gui_state=="animating" and curr_mv_idx==len(common_path_res)))
                all_puz_goal = all(st in TARGET_GOAL_STATES for st in curr_anim_st_tuples)

                if curr_mv_idx < len(common_path_res):
                    mv_txt_disp=f"Step {curr_mv_idx+1}/{len(common_path_res)}: {common_path_res[curr_mv_idx]}"
                elif final_step_comp and all_puz_goal: mv_txt_disp=f"TARGET REACHED! ({len(common_path_res)} Steps)"
                elif final_step_comp: mv_txt_disp="Finished (End state error)"
                if mv_txt_disp:
                    txt_c_mv=ERROR_COLOR if "error" in mv_txt_disp.lower() else (SOLVED_BORDER_COLOR if (final_step_comp and all_puz_goal) else TEXT_PRIMARY)
                    mv_s=move_info_f.render(mv_txt_disp,True,txt_c_mv)
                    screen_surf.blit(mv_s,mv_s.get_rect(center=(move_text_center_x_pos,move_text_y_final_pos)))

            if gui_state=="animating" and common_path_res and curr_mv_idx==len(common_path_res) and all_tiles_settled_current_frame:
                if not any(t.is_shaking for p_ts_list in all_anim_puzzles for t in p_ts_list):
                    if all_puz_goal: gui_state="finished"; status_msg_display=f"All states reached target!"
                    else: gui_state="finished"; status_msg_display=f"Completed (Some states might not be exact targets!)"
        
        pygame.display.flip(); clock.tick(60)

if __name__=="__main__":
    pygame.init(); pygame.font.init();
    try:
        s_info = pygame.display.Info()
        WIDTH, HEIGHT = s_info.current_w, s_info.current_h
    except pygame.error:
        WIDTH, HEIGHT = 1280, 720
    run_blind_search()
    pygame.quit(); sys.exit()