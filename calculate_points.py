def calculate_points(position):
    # 1st=14, 2nd=11, 3rd=9, 4th=7, 5th=5, 6th=3, 7th+=1
    points_table = {1: 14, 2: 11, 3: 9, 4: 7, 5: 5, 6: 3}
    if position >= 7:
        return 1
    return points_table.get(position, 0)
