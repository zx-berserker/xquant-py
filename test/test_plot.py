from bokeh.plotting import figure, show, output_notebook
from bokeh.models import HoverTool

# 给定的数列
def bokeh_show(xnumbers:list, ynumbers:list):
    # numbers = [7, 17, 37, 47, 67, 97, 107, 127, 137, 157, 167, 197, 
            #    227, 257, 277, 307, 317, 337, 347, 367, 397, 457, 467, 487]

    # 创建一个 bokeh 图表对象
    p = figure(
    title="Scatter Plot of Points where x = y",
    x_axis_label='x',
    y_axis_label='y',
    width=700, 
    height=700,
    tools="pan,wheel_zoom,box_zoom,reset,hover,save"  # 启用的交互工具
)

    # 绘制散点
    p.circle(
    xnumbers, 
    ynumbers, 
    size=10, 
    color="navy", 
    alpha=0.8,
    legend_label="Points (x, x)"
)

    # 绘制 y=x 的参考虚线
    p.line(
    xnumbers, 
    ynumbers, 
    line_dash="dashed", 
    color="gray", 
    alpha=0.5, 
    legend_label="Line y = x"
)

    # 配置悬停提示 (HoverTool)
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
    ("X 坐标", "@x"),
    ("Y 坐标", "@y")
]

    # 设置图表样式
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"  # 点击图例可以隐藏/显示对应图形
    p.grid.grid_line_alpha = 0.3
    show(p)

def find_primes_ending_with_7(limit, target=7):
    """
    计算 limit 以内所有个位数为 7 的质数
    """
    if limit < 7:
        return []
    
    # 1. 初始化筛子，假设所有数都是质数
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False  # 0 和 1 不是质数
    
    # 2. 埃拉托斯特尼筛法核心逻辑
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            # 将 i 的倍数标记为非质数
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
                
    # 3. 提取结果：既是质数，且个位数为 7
    result = [num for num in range(target, limit + 1, 10) if is_prime[num]]
    return result

# 测试：找出 1000 以内个位为 7 的质数
# limit = 1000
# primes_7 = find_primes_ending_with_7(limit)

# print(f"{limit} 以内个位为 7 的质数共有 {len(primes_7)} 个：")
# print(primes_7)

# 在浏览器中显示图表
if __name__ == '__main__':
    # num_list = find_primes_ending_with_7(20000,3)
    # yret_list = []
    # xret_list = []
    # for i in range(1,len(num_list)-1):
    #     yret_list.append(num_list[i]-num_list[i-1])
    #     xret_list.append(i)
    # bokeh_show(xret_list,yret_list)
    num = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999]
    temp = [1,2,3,5]
    ret = []
    for n in num:
        for t in temp:
            y = (n - t) % 6
            if y==0:
                ret.append([n,t,(n - t) / 6])

    print(ret)