# 게임월드 리스트 초기화

world = [[], [],[]] # 객체들의 리스트, 빈 리스트

# 객체를 게임월드에 추가하는 함수
def add_object(o, depth = 0): # 0은 가장 밑에 있는거
    world[depth].append(o)

def add_objects(ol, depth = 0): # 객체'들'을 게임월드에 추가
    world[depth] += ol

def remove_object(o): 
    for layer in world: # 모든 레이어를 순회하면서 객체를 제거
        if o in layer:  # 객체가 해당 레이어에 존재하면 제거
            layer.remove(o)
            return # 제거 후 함수 종료  

    raise ValueError('Cannot delete non existing object')

# 게임 로직
def update():
    for layer in world:
        for o in layer[:]:
            o.update()

# 게임월드 렌더링
def render():
    for layer in world:
        for o in layer:
            o.draw()

# 게임월드에 담겨있는 모든 객체들을 담는 리스트.
# Drawing Layer에 따라사 분류, 필요에 따라 Layer 추가