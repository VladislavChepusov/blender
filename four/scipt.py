import bpy
from random import *


# Количество участков местности (должно быть> 50)
subdiv = 54
# Общая длина и ширина местности
size = 70

# Максимальная высота любой вершины
height_max = 40

# Вычислить вершины и грани ландшафта (Построение поверхности)
def create_landscape():
    verts = []
    faces = []

    #Список склонности каждой вершины к типу земли (Land_T)
    land_tend = []

    start_loc = -(size / 2.0)
    face_size = size/ float(subdiv - 1)

    # Пройдитесь по рядам и столбцам квадратной плоскости
     # и создаем их вершины
    for row in range(subdiv):    # Строка в x-направлении
        x = start_loc + row * face_size
        for col in range(subdiv):  # Столбец в направлении y
            y = start_loc + col * face_size 

            # Необходимо вычислить высоту и Land_T вершин по
             # наблюдение за высотой окружающих вершин
            height_average = 0
            curr_land_t = Land_T.Plain

            # Использовать высоту предыдущей строки
            if row > 0:
                vert_below = verts[col + subdiv * (row - 1)]
                land_below = land_tend[col + subdiv * (row - 1)]
                # Использовать высоту предыдущей вершины в текущем цикле ребер
                if col > 0:
                    vert_prev = verts[(col - 1) + subdiv * row]
                    land_prev = land_tend[(col - 1) + subdiv * row]
                    height_average = (vert_prev[2] + vert_below[2]) / 2.0
                    z, curr_land_t = height_gen(height_average, land_below, land_prev)
                    
                    # Create a face, using indices of vertices
                    vertInd1 = (col - 1) + subdiv * row
                    vertInd2 = col + subdiv * row
                    vertInd3 = (col - 1) + subdiv * (row - 1)
                    vertInd4 = col + subdiv * (row - 1)
                    face_new = (vertInd2, vertInd1, vertInd3, vertInd4)
                    faces.append(face_new)

                # Первая вершина каждой строки
                else:
                    height_average = vert_below[2]
                    z, curr_land_t = height_gen(height_average, land_below, 0)

    
            else:
                if col > 0:
                    vert_prev = verts[col - 1]
                    land_prev = land_tend[col - 1]
                    height_average = vert_prev[2]
                    z, curr_land_t = height_gen(height_average, 0, land_prev)
                # Первая вершина
                else:
                    # Случайная начальная средняя высота простого типа
                    height_average = uniform(0, plain_height_max)
                    z, curr_land_t = height_gen(height_average, Land_T.Plain, 0)
                      
            verts.append((x,y,z))
            land_tend.append(curr_land_t)
        
    return verts, faces

# Вычисляет случайную высоту на основе средней высоты 
#  типа земли окружающих ее вершин
def height_gen(height_avg, land_below, land_prev):
    height = height_avg 
   # Определяет склонность типа земли (гора, холм, равнина)
     # текущей вершины на основе окружающих типов земель
    type_change = 0
    if land_below <= 0 and land_prev <= 0:  # Default Case
        type_change = Land_T.Plain
    elif land_below <= 0:  
        type_change = land_prev
    elif land_prev <= 0:  
        type_change = land_below
    else:
        # Выбор случайным образом между двумя типами земель
        type_change = choice([land_below, land_prev])
# Текущий тип земли на основе height_avg
    curr_land = Land_T.Plain
    if height >= mountain_height_min:
        curr_land = Land_T.Mountain
    elif height >= hill_height_min:
        curr_land = Land_T.Hill
   # Рассчитать высоту
    if type_change == Land_T.Mountain:  # Горный тип
        if curr_land == Land_T.Mountain:
            height += uniform(-1,1) * mountain_height_bias
            # Случайным образом решаем, изменяется ли land_t при создании горы
            if hill_chance >= random():
                type_change = Land_T.Hill
            elif plain_chance >= random():
                type_change = Land_T.Plain
        elif curr_land == Land_T.Hill:
            height += uniform(-0.10, 1) * hill_height_bias
        else:
            # Увеличение высоты от равнины является средним для отклонения высоты равнины и холма
            height += random() * (plain_height_bias + hill_height_bias) / 2.0
    elif type_change == Land_T.Hill:  # Тип холма
        if curr_land == Land_T.Mountain:
            height -= uniform(-0.10, 1) * mountain_height_bias
        elif curr_land == Land_T.Hill:
            height += uniform(-1,1) * hill_height_bias
            # Случайным образом решить, изменяется ли land_t при создании холма
            if mountain_chance >= random():
                type_change = Land_T.Mountain
            elif plain_chance >= random():
                type_change = Land_T.Plain
        else:
            # Увеличение высоты от равнины является средним для отклонения высоты равнины и холма
            height += random() * (plain_height_bias + hill_height_bias) / 2.0
    else:  
        if curr_land == Land_T.Mountain:
            height -= uniform(-0.10, 1) * mountain_height_bias
        elif curr_land == Land_T.Hill:
            height += uniform(-1,1) * hill_height_bias
        else:
            height += uniform(-1,1) * plain_height_bias

            if height >= plain_height_max:
                height -= 2* random() * plain_height_bias

            if mountain_chance >= random():
                type_change = Land_T.Mountain
            elif hill_chance >= random():
                type_change = Land_T.Hill
    # Высота зажима до максимальной и минимальной высоты
    if height > height_max:
        height = height_max
    elif height < 0:
        height = 0
    return height, type_change




def main():
    verts, faces = create_landscape()
    edges = []
    # Создать новую поверхность
    mesh = bpy.data.meshes.new("Landscape_Data")
    mesh.from_pydata(verts, edges, faces)
    # Обновить геометрию меша после добавления материала.
    mesh.update()
    object = bpy.data.objects.new("Landscape", mesh)  
    object.data = mesh 
    # Привязать поверхность к сцене
    scene = bpy.context.scene  
    #scene.objects.link(object)  
    scene.collection.objects.link(object)
    #object.select = True 




# Минимальная высота для считывания горы / холма
mountain_height_min = height_max * (6/10.0)
hill_height_min = height_max * (2/10.0)


# Максимальная высота равнины (должна быть меньше высоты холма)
plain_height_max = height_max * (1/80.0)


# Вероятность добавления / вычитания смещения гор / холмов
mountain_chance = 0.025
hill_chance =  0.050
plain_chance = 0.750



# Максимальный прыжок по высоте от одной вершины к другой
# (Для хороших результатов: равнина <холм <гора и меньше для более высокого подразделения)
mountain_height_bias = height_max * (1/40.0)
hill_height_bias = height_max * (1/60.0)
plain_height_bias = plain_height_max * (1/1.0)



#КЛАСС КОЛ-ВА ОБЬЕКТОВ
class Land_T:
    Mountain = 0
    Hill = 3
    Plain = 2

if __name__ == "__main__":
    main()