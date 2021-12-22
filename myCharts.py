from pyecharts.charts import Bar, Graph, Line, Grid
from pyecharts import options as opts
from pyecharts.faker import Faker

value = {}
f1 = open("./data/attribute.txt", "r")
data = f1.read().split("\n")
f1.close()
for i in data: value[i.split()[0]] = i.split()[1]

edges = {}
f1 = open("./data/relation.txt", "r")
data = f1.read().split("\n")
f1.close()
for i in data:
    u = i.split()[0]
    v = i.split()[1]
    if u in edges:
        edges[u].append(v)
    else:
        edges[u] = [v]

SI = {}
f1 = open("./data/nodeDisplay.txt", "r")
data = f1.read().split("\n")[:-1]
f1.close()
for i in data:
    SI[i.split()[0]] = i.split()[1]

labels = {}
f1 = open("./data/nodeLabel.txt", "r")
data = f1.read().split("\n")[:-1]
f1.close()
for i in data: labels[i.split()[0]] = i.split()[1]

f1 = open("./data/nodeVector.txt", "r")
data = f1.read().split("\n")[:-1]
f1.close()


def origin_provenance_with_SI() -> Graph:
    p = 0
    used = {}
    nodes = []
    links = []
    for i in range(16):
        for j in range(16):
            u = data[p]
            if int(u) == 0 or u not in edges:
                p += 1
                continue
            if u not in used:
                nodes.append({"name": u, "value": value[u], "symbolSize": float(SI[u])})
                used[u] = 1
            vs = edges[u]
            for v in vs:
                if v not in used:
                    nodes.append({"name": v, "value": value[v], "symbolSize": float(SI[v])})
                    used[v] = 1
                links.append({"source": u, "target": v})
            p += 1
    A = (
        Graph(init_opts=opts.InitOpts(width="900px", height="600px"))
            .add(
            "",
            nodes=nodes,
            links=links,
            is_rotate_label=True,
            linestyle_opts=opts.LineStyleOpts(color="source", curve=0.3),
            label_opts=opts.LabelOpts(position="right"),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="原始溯源图模型"),
        )
    )
    return A


def provenance_with_label() -> Graph:
    p = 0
    tot = 0

    nodes = []
    links = []
    category = []

    used = {}
    label_used = {}

    for i in range(16):
        for j in range(16):
            u = data[p]
            if int(u) == 0 or u not in edges:
                p += 1
                continue

            if u not in used:
                if labels[u] not in label_used:
                    category.append({"name": "用户{0}".format(tot)})
                    label_used[labels[u]] = tot
                    tot += 1
                nodes.append(
                    {"name": u, "value": value[u], "symbol_size": float(SI[u]), "category": label_used[labels[u]]})
                used[u] = 1

            vs = edges[u]
            for v in vs:
                if v not in used:
                    if labels[v] not in label_used:
                        category.append({"name": "用户{0}".format(tot)})
                        label_used[labels[v]] = tot
                        tot += 1
                    nodes.append(
                        {"name": v, "value": value[v], "symbol_size": float(SI[v]), "category": label_used[labels[v]]})
                    used[v] = 1
                links.append({"source": u, "target": v})
            p += 1

    B = (
        Graph(init_opts=opts.InitOpts(width="900px", height="600px"))
            .add(
            "",
            nodes=nodes,
            links=links,
            categories=category,
            is_rotate_label=True,
            linestyle_opts=opts.LineStyleOpts(color="source", curve=0.3),
            label_opts=opts.LabelOpts(position="right"),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="标签化溯源图模型"),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_left="2%", pos_top="20%"
            ),
        )
    )
    return B


def provenance_with_center_node() -> Graph:
    p = 0

    nodes = []
    links = []
    category = [{"name": "用户0"}, {"name": "用户1"}, {"name": "用户2"}, {"name": "用户3"},
                {"name": "用户4"}, {"name": "用户5"}, {"name": "用户6"}, {"name": "用户7"},
                {"name": "用户8"}, {"name": "用户9"}, {"name": "用户10"}, {"name": "用户11"},
                {"name": "用户12"}, {"name": "用户13"}, {"name": "用户14"}, {"name": "用户15"},
                ]

    used = {}

    for i in range(16):
        for j in range(16):
            u = data[p]
            if int(u) == 0:
                p += 1
                continue
            if u not in used:
                nodes.append({"name": u, "value": value[u], "symbol_size": float(SI[u]), "category": i})
                used[u] = 1
            p += 1

    p = 0
    for i in range(16):
        for j in range(16):
            u = data[p]
            if int(u) == 0 or u not in edges:
                p += 1
                continue
            vs = edges[u]
            for v in vs:
                if v not in used: continue
                links.append({"source": u, "target": v})
            p += 1

    C = (
        Graph(init_opts=opts.InitOpts(width="900px", height="600px"))
            .add(
            "",
            nodes=nodes,
            links=links,
            categories=category,
            layout="circular",
            is_rotate_label=True,
            linestyle_opts=opts.LineStyleOpts(color="source", curve=0.3),
            label_opts=opts.LabelOpts(position="right"),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="中心化溯源图模型"),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_left="2%", pos_top="20%"
            ),
        )
    )
    return C


def provenance_to_vector() -> Graph:
    p = 0

    nodes = []
    links = []
    category = [{"name": "用户0"}, {"name": "用户1"}, {"name": "用户2"}, {"name": "用户3"},
                {"name": "用户4"}, {"name": "用户5"}, {"name": "用户6"}, {"name": "用户7"},
                {"name": "用户8"}, {"name": "用户9"}, {"name": "用户10"}, {"name": "用户11"},
                {"name": "用户12"}, {"name": "用户13"}, {"name": "用户14"}, {"name": "用户15"},
                ]

    used = {}

    for i in range(16):
        x = data[p]
        if int(x) == 0: continue
        if x not in used:
            nodes.append(
                {"x": 50, "y": 40 * (i + 1), "name": x, "value": value[x], "symbol_size": float(SI[x]), "category": i})
            used[x] = 1
        u = x
        for j in range(15):
            p += 1
            v = data[p]
            if int(v) == 0: continue
            if v not in used:
                nodes.append(
                    {"x": 50 * (j + 2), "y": 40 * (i + 1), "name": v, "value": value[v], "symbol_size": float(SI[v]),
                     "category": i})
                used[v] = 1
            links.append({"source": u, "target": v})
            u = v
        p += 1

    D = (
        Graph(init_opts=opts.InitOpts(width="900px", height="600px"))
            .add(
            "",
            nodes=nodes,
            links=links,
            categories=category,
            layout="none",
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="向量模型"),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_left="2%", pos_top="20%"
            ),
        )
    )
    return D


def loss_log() -> Line:
    x_data = [i + 1 for i in range(100)]
    y_data = []

    f1 = open("./data/log.txt", "r")
    data = f1.read().split("\n")
    for i in data: y_data.append(i)
    f1.close()
    y_data = y_data[:100]

    E = (
        Line(init_opts=opts.InitOpts(width="900px", height="600px"))
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
            series_name="loss",
            y_axis=y_data,
            symbol="emptyCircle",
            is_symbol_show=True,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="CNN训练过程记录", subtitle="损失值记录"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
    )
    return E


def train_result(normal, intrusion) -> Grid:
    F = (
        Bar()
            .add_xaxis(['正常', '异常'])
            .add_yaxis("测试集", [normal, intrusion])
            #.add_yaxis("商家B", Faker.values())
            .set_global_opts(
            title_opts=opts.TitleOpts(title="检测结果", subtitle="CNN"),
            brush_opts=opts.BrushOpts(),
        )
    )
    return F
