from manim import *
import json
import sys
import os

# Parse command line arguments for input file
input_file = None
for i, arg in enumerate(sys.argv):
    if arg == "--input_file" and i + 1 < len(sys.argv):
        input_file = sys.argv[i + 1]
        break

input_data = {}
if input_file and os.path.exists(input_file):
    try:
        with open(input_file, 'r') as f:
            input_data = json.load(f)
        print(f"Loaded input data from {input_file}")
        print(f"Data: {input_data}")
    except Exception as e:
        print(f"Error loading input file: {e}")
else:
    print(f"No input file provided or file not found: {input_file}")


class LinearProgrammingFull(Scene):
    def construct(self):
        # Get data from input or use defaults
        objective = input_data.get('objective', '3x1 + 2x2')
        constraints = input_data.get('constraints', ['2x1 + x2 <= 8', 'x1 + 2x2 <= 10'])
        
        # Title
        title = Text("Linear Programming Problem", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        
        # Axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=7,
            y_length=7,
            axis_config={"include_tip": True}
        )
        labels = axes.get_axis_labels(x_label="x_1", y_label="x_2")
        self.play(Create(axes), Write(labels))
        self.wait(1)
        
        # Constraints
        c1 = axes.plot(lambda x: 8 - 2*x, x_range=[0, 4], color=BLUE)
        c2 = axes.plot(lambda x: 5 - 0.5*x, x_range=[0, 10], color=GREEN)
        
        c1_label = MathTex("2x_1 + x_2 = 8", color=BLUE)
        c1_label.next_to(axes.c2p(2, 4), UR)
        c2_label = MathTex("x_1 + 2x_2 = 10", color=GREEN)
        c2_label.next_to(axes.c2p(4, 3), UL)
        
        self.play(Create(c1), Create(c2))
        self.play(Write(c1_label), Write(c2_label))
        self.wait(1)
        
        # Feasible Region
        region = Polygon(
            axes.c2p(0, 0),
            axes.c2p(4, 0),
            axes.c2p(2, 4),
            axes.c2p(0, 5),
            fill_color=YELLOW,
            fill_opacity=0.4,
            stroke_width=0
        )
        region_label = Text("Feasible Region", font_size=24, color=YELLOW)
        region_label.move_to(axes.c2p(1.5, 2.5))
        
        self.play(FadeIn(region), Write(region_label))
        self.wait(1)
        
        # Corner Points
        points = [(0, 0), (4, 0), (2, 4), (0, 5)]
        labels_text = ["O(0,0)", "A(4,0)", "B(2,4)", "C(0,5)"]
        dots = VGroup(*[Dot(axes.c2p(x, y), color=RED, radius=0.08) for x, y in points])
        points_labels = VGroup(*[
            Text(t, font_size=20, color=RED).next_to(axes.c2p(x, y), DR, buff=0.1)
            for (x, y), t in zip(points, labels_text)
        ])
        
        self.play(LaggedStart(*[Create(d) for d in dots], lag_ratio=0.3))
        self.play(LaggedStart(*[Write(l) for l in points_labels], lag_ratio=0.3))
        self.wait(1)
        
        # Sliding Objective Function
        z = ValueTracker(0)
        obj_line = always_redraw(
            lambda: axes.plot(
                lambda x: z.get_value()/2 - 1.5*x,
                x_range=[0, 5],
                color=ORANGE,
                stroke_width=3
            )
        )
        z_label = always_redraw(
            lambda: MathTex(f"z = {z.get_value():.1f}", color=ORANGE)
            .scale(0.7)
            .next_to(axes.c2p(0.5, z.get_value()/2 - 0.75), UP, buff=0.1)
        )
        
        self.add(obj_line, z_label)
        self.play(z.animate.set_value(14), run_time=4)
        self.wait(1)
        
        # Highlight Optimal Solution
        optimal_dot = Dot(axes.c2p(2, 4), color=YELLOW, radius=0.15)
        optimal_label = Text("Optimal: B(2,4)\nz = 14", font_size=24, color=YELLOW)
        optimal_label.next_to(optimal_dot, UR, buff=0.2)
        
        self.play(Create(optimal_dot), Write(optimal_label))
        self.wait(2)


class TransportationProblem(Scene):
    def construct(self):
        # Get data from input or use defaults
        supply = input_data.get('supply', [20, 30, 25])
        demand = input_data.get('demand', [15, 25, 35])
        costs = input_data.get('costs', [[8, 6, 10], [9, 12, 13], [14, 9, 16]])
        
        # Title
        title = Text("Transportation Problem", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.7).to_edge(UP))
        
        # Create supply nodes (sources)
        sources = VGroup()
        for i, s in enumerate(supply):
            circle = Circle(radius=0.5, color=BLUE, fill_opacity=0.3)
            label = Text(f"S{i+1}\n{s}", font_size=20)
            label.move_to(circle.get_center())
            source = VGroup(circle, label)
            source.move_to(LEFT * 4 + UP * (2 - i * 2))
            sources.add(source)
        
        # Create demand nodes (destinations)
        destinations = VGroup()
        for i, d in enumerate(demand):
            circle = Circle(radius=0.5, color=GREEN, fill_opacity=0.3)
            label = Text(f"D{i+1}\n{d}", font_size=20)
            label.move_to(circle.get_center())
            dest = VGroup(circle, label)
            dest.move_to(RIGHT * 4 + UP * (2 - i * 2))
            destinations.add(dest)
        
        self.play(LaggedStart(*[Create(s) for s in sources], lag_ratio=0.2))
        self.play(LaggedStart(*[Create(d) for d in destinations], lag_ratio=0.2))
        self.wait(1)
        
        # Draw connections with costs
        connections = VGroup()
        cost_labels = VGroup()
        
        for i, source in enumerate(sources):
            for j, dest in enumerate(destinations):
                line = Line(
                    source.get_right(),
                    dest.get_left(),
                    color=GRAY,
                    stroke_width=1
                )
                cost_label = Text(str(costs[i][j]), font_size=16, color=YELLOW)
                cost_label.move_to(line.get_center())
                cost_label.add_background_rectangle(color=BLACK, opacity=0.7)
                
                connections.add(line)
                cost_labels.add(cost_label)
        
        self.play(Create(connections), run_time=2)
        self.play(Write(cost_labels), run_time=1)
        self.wait(1)
        
        # Show optimal solution (example - highlight certain paths)
        optimal_paths = [
            (0, 0, 15), (0, 1, 5),
            (1, 1, 20), (1, 2, 10),
            (2, 2, 25)
        ]
        
        solution_text = Text("Optimal Solution", font_size=30, color=YELLOW)
        solution_text.to_edge(DOWN)
        self.play(Write(solution_text))
        
        for src, dst, amount in optimal_paths:
            line = Line(
                sources[src].get_right(),
                destinations[dst].get_left(),
                color=YELLOW,
                stroke_width=4
            )
            flow_label = Text(str(amount), font_size=20, color=RED)
            flow_label.move_to(line.get_center())
            flow_label.shift(UP * 0.3)
            
            self.play(Create(line), Write(flow_label), run_time=0.5)
        
        self.wait(2)


class TravellingSalesmanProblem(Scene):
    def construct(self):
        # Get data from input or use defaults
        cities = input_data.get('cities', ['A', 'B', 'C', 'D'])
        distances = input_data.get('distances', [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        
        # Title
        title = Text("Travelling Salesman Problem", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.7).to_edge(UP))
        
        # Create city nodes in a circle
        n_cities = len(cities)
        radius = 2.5
        city_nodes = VGroup()
        
        for i, city in enumerate(cities):
            angle = i * TAU / n_cities - PI/2
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            circle = Circle(radius=0.4, color=BLUE, fill_opacity=0.5)
            circle.move_to([x, y, 0])
            label = Text(city, font_size=28)
            label.move_to(circle.get_center())
            
            city_node = VGroup(circle, label)
            city_nodes.add(city_node)
        
        self.play(LaggedStart(*[Create(c) for c in city_nodes], lag_ratio=0.2))
        self.wait(1)
        
        # Draw all possible edges with distances
        edges = VGroup()
        for i in range(n_cities):
            for j in range(i + 1, n_cities):
                line = Line(
                    city_nodes[i].get_center(),
                    city_nodes[j].get_center(),
                    color=GRAY,
                    stroke_width=1,
                    stroke_opacity=0.3
                )
                dist_label = Text(str(distances[i][j]), font_size=12, color=WHITE)
                dist_label.move_to(line.get_center())
                dist_label.add_background_rectangle(color=BLACK, opacity=0.5)
                
                edges.add(VGroup(line, dist_label))
        
        self.play(Create(edges), run_time=2)
        self.wait(1)
        
        # Show optimal tour (example solution)
        optimal_tour = [0, 1, 3, 2, 0]  # A -> B -> D -> C -> A
        tour_edges = VGroup()
        total_distance = 0
        
        solution_text = Text("Optimal Tour", font_size=30, color=YELLOW)
        solution_text.to_edge(DOWN)
        self.play(Write(solution_text))
        
        for i in range(len(optimal_tour) - 1):
            start = optimal_tour[i]
            end = optimal_tour[i + 1]
            
            arrow = Arrow(
                city_nodes[start].get_center(),
                city_nodes[end].get_center(),
                color=YELLOW,
                stroke_width=6,
                buff=0.4,
                max_tip_length_to_length_ratio=0.15
            )
            
            dist = distances[start][end]
            total_distance += dist
            
            self.play(Create(arrow), run_time=0.8)
        
        # Show total distance
        total_text = Text(f"Total Distance: {total_distance}", font_size=26, color=GREEN)
        total_text.next_to(solution_text, UP, buff=0.3)
        self.play(Write(total_text))
        
        self.wait(2)