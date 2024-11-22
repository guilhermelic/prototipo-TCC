import math

# Calcula o centroide dos pontos
def calculate_centroid(points):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    centroid = (sum(x_coords) / len(points), sum(y_coords) / len(points))
    return centroid

# Calcula o ângulo do ponto em relação ao centroide
def angle_from_centroid(centroid, point):
    return math.atan2(point[1] - centroid[1], point[0] - centroid[0])

# Ordena os pontos em sentido anti-horário a partir do centroide
def order_points(points):
    centroid = calculate_centroid(points)
    sorted_points = sorted(points, key=lambda point: angle_from_centroid(centroid, point))
    return sorted_points


# Teste
def main():
    points = [(367, 270), (408, 263), (368, 259), (407, 274)]
    ordered_points = order_points(points)
    print(ordered_points)

if __name__ == "__main__":
    main()