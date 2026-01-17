from manim import *
import configparser
import sys
import os
import re
import numpy as np
from scipy.optimize import linprog, linear_sum_assignment
from itertools import permutations

# Parse command line arguments for config file
config_file = None
for i, arg in enumerate(sys.argv):
    if arg == "--config_file" and i + 1 < len(sys.argv):
        config_file = sys.argv[i + 1]
        break

# Load configuration
input_data = {}
if config_file and os.path.exists(config_file):
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        if 'INPUT' in config:
            problem_type = config['INPUT'].get('type', 'standard')
            
            if problem_type == 'standard':
                input_data['objective'] = config['INPUT'].get('objective', '3x1 + 2x2')
                constraints_str = config['INPUT'].get('constraints', '2x1 + x2 <= 8;x1 + 2x2 <= 10')
                input_data['constraints'] = constraints_str.split(';')
            
            elif problem_type == 'transportation':
                supply_str = config['INPUT'].get('supply', '20,30,25')
                demand_str = config['INPUT'].get('demand', '15,25,35')
                costs_str = config['INPUT'].get('costs', '8,6,10;9,12,13;14,9,16')
                
                input_data['supply'] = list(map(int, supply_str.split(',')))
                input_data['demand'] = list(map(int, demand_str.split(',')))
                input_data['costs'] = [list(map(int, row.split(','))) for row in costs_str.split(';')]
            
            elif problem_type == 'tsp':
                cities_str = config['INPUT'].get('cities', 'A,B,C,D')
                distances_str = config['INPUT'].get('distances', '0,10,15,20;10,0,35,25;15,35,0,30;20,25,30,0')
                
                input_data['cities'] = cities_str.split(',')
                input_data['distances'] = [list(map(int, row.split(','))) for row in distances_str.split(';')]
        
        print(f"Loaded config data from {config_file}")
        print(f"Data: {input_data}")
    except Exception as e:
        print(f"Error loading config file: {e}")
else:
    print(f"No config file provided or file not found: {config_file}")


def parse_objective(obj_str):
    """Parse objective like '3x1 + 2x2' -> coefficients [3, 2]"""
    coeffs = []
    terms = re.findall(r'([+-]?\s*\d*\.?\d*)\s*x(\d+)', obj_str)
    max_var = max(int(t[1]) for t in terms) if terms else 2
    
    coeffs = [0.0] * max_var
    for coef, var_num in terms:
        coef = coef.replace(' ', '')
        if coef in ['', '+']:
            coef = 1.0
        elif coef == '-':
            coef = -1.0
        else:
            coef = float(coef)
        coeffs[int(var_num) - 1] = coef
    
    return coeffs


def parse_constraint(constraint_str):
    """Parse constraint like '2x1 + x2 <= 8' -> (coeffs, rhs, type)"""
    # Find inequality
    if '<=' in constraint_str:
        lhs, rhs = constraint_str.split('<=')
        ineq_type = '<='
    elif '>=' in constraint_str:
        lhs, rhs = constraint_str.split('>=')
        ineq_type = '>='
    elif '=' in constraint_str:
        lhs, rhs = constraint_str.split('=')
        ineq_type = '='
    else:
        return None
    
    # Parse LHS
    terms = re.findall(r'([+-]?\s*\d*\.?\d*)\s*x(\d+)', lhs)
    max_var = max(int(t[1]) for t in terms) if terms else 2
    
    coeffs = [0.0] * max_var
    for coef, var_num in terms:
        coef = coef.replace(' ', '')
        if coef in ['', '+']:
            coef = 1.0
        elif coef == '-':
            coef = -1.0
        else:
            coef = float(coef)
        coeffs[int(var_num) - 1] = coef
    
    return (coeffs, float(rhs.strip()), ineq_type)


def solve_lp(objective, constraints):
    """Solve LP using scipy and return corner points and optimal solution"""
    obj_coeffs = parse_objective(objective)
    parsed_constraints = [parse_constraint(c) for c in constraints]
    
    # For graphical solution, find intersection points
    points = [(0, 0)]
    
    # Add axis intersections
    for coeffs, rhs, _ in parsed_constraints:
        if coeffs[0] != 0:
            points.append((rhs/coeffs[0], 0))
        if coeffs[1] != 0:
            points.append((0, rhs/coeffs[1]))
    
    # Find constraint intersections (for 2 variables)
    for i in range(len(parsed_constraints)):
        for j in range(i+1, len(parsed_constraints)):
            c1, r1, _ = parsed_constraints[i]
            c2, r2, _ = parsed_constraints[j]
            
            # Solve system: c1[0]*x + c1[1]*y = r1, c2[0]*x + c2[1]*y = r2
            det = c1[0]*c2[1] - c1[1]*c2[0]
            if abs(det) > 1e-10:
                x = (r1*c2[1] - r2*c1[1]) / det
                y = (c1[0]*r2 - c2[0]*r1) / det
                if x >= -0.01 and y >= -0.01:  # Feasible region
                    points.append((max(0, x), max(0, y)))
    
    # Filter feasible points
    feasible_points = []
    for x, y in points:
        is_feasible = True
        for coeffs, rhs, ineq in parsed_constraints:
            val = coeffs[0]*x + coeffs[1]*y
            if ineq == '<=' and val > rhs + 0.01:
                is_feasible = False
            elif ineq == '>=' and val < rhs - 0.01:
                is_feasible = False
        if is_feasible:
            feasible_points.append((round(x, 2), round(y, 2)))
    
    # Remove duplicates
    feasible_points = list(set(feasible_points))
    
    # Find optimal
    optimal_point = None
    optimal_value = float('-inf')
    for x, y in feasible_points:
        z = obj_coeffs[0]*x + obj_coeffs[1]*y
        if z > optimal_value:
            optimal_value = z
            optimal_point = (x, y)
    
    return feasible_points, optimal_point, optimal_value, obj_coeffs, parsed_constraints


def solve_transportation(supply, demand, costs):
    """Solve transportation problem using Vogel's Approximation Method"""
    m, n = len(supply), len(demand)
    supply_left = supply.copy()
    demand_left = demand.copy()
    allocation = [[0 for _ in range(n)] for _ in range(m)]
    
    while sum(supply_left) > 0 and sum(demand_left) > 0:
        # Calculate penalties for rows
        row_penalties = []
        for i in range(m):
            if supply_left[i] > 0:
                available = [costs[i][j] for j in range(n) if demand_left[j] > 0]
                if len(available) >= 2:
                    available.sort()
                    row_penalties.append((available[1] - available[0], i, 'row'))
                elif len(available) == 1:
                    row_penalties.append((0, i, 'row'))
        
        # Calculate penalties for columns
        col_penalties = []
        for j in range(n):
            if demand_left[j] > 0:
                available = [costs[i][j] for i in range(m) if supply_left[i] > 0]
                if len(available) >= 2:
                    available.sort()
                    col_penalties.append((available[1] - available[0], j, 'col'))
                elif len(available) == 1:
                    col_penalties.append((0, j, 'col'))
        
        if not row_penalties and not col_penalties:
            break
        
        # Choose maximum penalty
        all_penalties = row_penalties + col_penalties
        max_penalty = max(all_penalties, key=lambda x: x[0])
        
        if max_penalty[2] == 'row':
            i = max_penalty[1]
            # Find minimum cost in this row
            min_cost = float('inf')
            best_j = -1
            for j in range(n):
                if demand_left[j] > 0 and costs[i][j] < min_cost:
                    min_cost = costs[i][j]
                    best_j = j
            j = best_j
        else:
            j = max_penalty[1]
            # Find minimum cost in this column
            min_cost = float('inf')
            best_i = -1
            for i in range(m):
                if supply_left[i] > 0 and costs[i][j] < min_cost:
                    min_cost = costs[i][j]
                    best_i = i
            i = best_i
        
        # Allocate
        amount = min(supply_left[i], demand_left[j])
        allocation[i][j] = amount
        supply_left[i] -= amount
        demand_left[j] -= amount
    
    # Calculate total cost
    total_cost = sum(allocation[i][j] * costs[i][j] for i in range(m) for j in range(n))
    
    # Create allocation list
    allocations = []
    for i in range(m):
        for j in range(n):
            if allocation[i][j] > 0:
                allocations.append((i, j, allocation[i][j]))
    
    return allocations, total_cost


def solve_tsp(distances):
    """Solve TSP using brute force for small instances or greedy for larger ones"""
    n = len(distances)
    
    # For small instances (n <= 10), use brute force
    if n <= 10:
        min_distance = float('inf')
        best_tour = None
        
        # Try all permutations
        for perm in permutations(range(1, n)):
            tour = [0] + list(perm) + [0]
            distance = sum(distances[tour[i]][tour[i+1]] for i in range(n))
            
            if distance < min_distance:
                min_distance = distance
                best_tour = tour
        
        return best_tour, min_distance
    
    # For larger instances, use nearest neighbor heuristic
    else:
        visited = [0]
        current = 0
        total_distance = 0
        
        while len(visited) < n:
            nearest = None
            nearest_dist = float('inf')
            for i in range(n):
                if i not in visited and distances[current][i] < nearest_dist:
                    nearest = i
                    nearest_dist = distances[current][i]
            
            visited.append(nearest)
            total_distance += nearest_dist
            current = nearest
        
        visited.append(0)
        total_distance += distances[current][0]
        
        return visited, total_distance


class LinearProgrammingFull(Scene):
    def construct(self):
        # Get data from input or use defaults
        objective = input_data.get('objective', '3x1 + 2x2')
        constraints = input_data.get('constraints', ['2x1 + x2 <= 8', 'x1 + 2x2 <= 10'])
        
        # Solve the LP
        feasible_points, optimal_point, optimal_value, obj_coeffs, parsed_constraints = solve_lp(objective, constraints)
        
        # Title
        title = Text("Linear Programming Problem", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # Show objective and constraints
        obj_text = MathTex(f"\\text{{Maximize: }} {objective.replace('x1', 'x_1').replace('x2', 'x_2')}", font_size=28)
        obj_text.next_to(title, DOWN)
        self.play(Write(obj_text))
        
        const_text = VGroup(*[
            MathTex(c.replace('x1', 'x_1').replace('x2', 'x_2'), font_size=24)
            for c in constraints
        ]).arrange(DOWN, aligned_edge=LEFT)
        const_text.next_to(obj_text, DOWN)
        self.play(Write(const_text))
        self.wait(2)
        self.play(FadeOut(obj_text), FadeOut(const_text))
        
        # Axes
        max_val = max(max(p[0] for p in feasible_points), max(p[1] for p in feasible_points))
        axis_max = int(max_val * 1.3) + 1
        
        axes = Axes(
            x_range=[0, axis_max, max(1, axis_max//10)],
            y_range=[0, axis_max, max(1, axis_max//10)],
            x_length=7,
            y_length=7,
            axis_config={"include_tip": True}
        )
        labels = axes.get_axis_labels(x_label="x_1", y_label="x_2")
        self.play(Create(axes), Write(labels))
        self.wait(1)
        
        # Draw constraints
        constraint_lines = VGroup()
        constraint_labels = VGroup()
        colors = [BLUE, GREEN, RED, PURPLE, ORANGE]
        
        for i, (coeffs, rhs, ineq) in enumerate(parsed_constraints):
            color = colors[i % len(colors)]
            
            # Create line equation
            if abs(coeffs[1]) > 1e-10:
                line_func = lambda x, c=coeffs, r=rhs: (r - c[0]*x) / c[1]
                x_range = [0, min(axis_max, rhs/coeffs[0] if abs(coeffs[0]) > 1e-10 else axis_max)]
                line = axes.plot(line_func, x_range=x_range, color=color)
            else:
                # Vertical line
                x_val = rhs / coeffs[0]
                line = Line(axes.c2p(x_val, 0), axes.c2p(x_val, axis_max), color=color)
            
            # Label
            label_str = f"{coeffs[0]:.0f}x_1 + {coeffs[1]:.0f}x_2 {ineq} {rhs:.0f}"
            label_str = label_str.replace("+ -", "- ").replace("1.0x", "x").replace(".0x", "x").replace(".0 ", " ")
            label = MathTex(label_str, color=color, font_size=20)
            
            # Position label
            mid_x = x_range[1]/2 if abs(coeffs[1]) > 1e-10 else x_val
            mid_y = line_func(mid_x) if abs(coeffs[1]) > 1e-10 else axis_max/2
            label.next_to(axes.c2p(mid_x, mid_y), UR, buff=0.1)
            
            constraint_lines.add(line)
            constraint_labels.add(label)
        
        self.play(Create(constraint_lines))
        self.play(Write(constraint_labels))
        self.wait(1)
        
        # Feasible Region
        if len(feasible_points) > 2:
            # Sort points to form polygon
            center = np.mean(feasible_points, axis=0)
            sorted_points = sorted(feasible_points, 
            key=lambda p: np.arctan2(p[1]-center[1], p[0]-center[0]))
            
            region = Polygon(
                *[axes.c2p(x, y) for x, y in sorted_points],
                fill_color=YELLOW,
                fill_opacity=0.3,
                stroke_width=0
            )
            region_label = Text("Feasible Region", font_size=24, color=YELLOW)
            region_label.move_to(axes.c2p(center[0], center[1]))
            
            self.play(FadeIn(region), Write(region_label))
            self.wait(1)
        
        # Corner Points
        dots = VGroup(*[Dot(axes.c2p(x, y), color=RED, radius=0.08) for x, y in feasible_points])
        point_labels = VGroup(*[
            Text(f"({x:.1f},{y:.1f})", font_size=16, color=RED).next_to(axes.c2p(x, y), DR, buff=0.1)
            for x, y in feasible_points
        ])
        
        self.play(LaggedStart(*[Create(d) for d in dots], lag_ratio=0.2))
        self.play(LaggedStart(*[Write(l) for l in point_labels], lag_ratio=0.2))
        self.wait(1)
        
        # Sliding Objective Function
        z = ValueTracker(0)
        
        if abs(obj_coeffs[1]) > 1e-10:
            obj_line = always_redraw(
                lambda: axes.plot(
                    lambda x: (z.get_value() - obj_coeffs[0]*x) / obj_coeffs[1],
                    x_range=[0, axis_max],
                    color=ORANGE,
                    stroke_width=3
                )
            )
            z_label = always_redraw(
                lambda: MathTex(f"z = {z.get_value():.1f}", color=ORANGE)
                .scale(0.7)
                .to_edge(UP)
            )
        else:
            obj_line = always_redraw(
                lambda: Line(
                    axes.c2p(z.get_value()/obj_coeffs[0], 0),
                    axes.c2p(z.get_value()/obj_coeffs[0], axis_max),
                    color=ORANGE,
                    stroke_width=3
                )
            )
            z_label = always_redraw(
                lambda: MathTex(f"z = {z.get_value():.1f}", color=ORANGE)
                .scale(0.7)
                .to_edge(UP)
            )
        
        self.add(obj_line, z_label)
        self.play(z.animate.set_value(optimal_value), run_time=4)
        self.wait(1)
        
        # Highlight Optimal Solution
        optimal_dot = Dot(axes.c2p(optimal_point[0], optimal_point[1]), color=YELLOW, radius=0.15)
        optimal_label = Text(
            f"Optimal: ({optimal_point[0]:.1f},{optimal_point[1]:.1f})\nz = {optimal_value:.1f}", 
            font_size=24, 
            color=YELLOW
        )
        optimal_label.next_to(optimal_dot, UR, buff=0.2)
        
        self.play(Create(optimal_dot), Write(optimal_label))
        self.wait(2)


class TransportationProblem(Scene):
    def construct(self):
        # Get data from input or use defaults
        supply = input_data.get('supply', [20, 30, 25])
        demand = input_data.get('demand', [15, 25, 35])
        costs = input_data.get('costs', [[8, 6, 10], [9, 12, 13], [14, 9, 16]])
        
        # Solve the transportation problem
        allocations, total_cost = solve_transportation(supply, demand, costs)
        
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
        
        # Show optimal solution
        solution_text = Text(f"Optimal Solution (Cost: {total_cost})", font_size=28, color=YELLOW)
        solution_text.to_edge(DOWN)
        self.play(Write(solution_text))
        
        for src, dst, amount in allocations:
            line = Line(
                sources[src].get_right(),
                destinations[dst].get_left(),
                color=YELLOW,
                stroke_width=4
            )
            flow_label = Text(str(amount), font_size=20, color=RED)
            flow_label.move_to(line.get_center())
            flow_label.shift(UP * 0.3)
            flow_label.add_background_rectangle(color=BLACK, opacity=0.8)
            
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
        
        # Simple greedy solution for demonstration
        visited = [0]
        current = 0
        total_distance = 0
        
        while len(visited) < n_cities:
            nearest = None
            nearest_dist = float('inf')
            for i in range(n_cities):
                if i not in visited and distances[current][i] < nearest_dist:
                    nearest = i
                    nearest_dist = distances[current][i]
            visited.append(nearest)
            total_distance += nearest_dist
            current = nearest
        
        visited.append(0)
        total_distance += distances[current][0]
        
        solution_text = Text("Greedy Tour", font_size=30, color=YELLOW)
        solution_text.to_edge(DOWN)
        self.play(Write(solution_text))
        
        for i in range(len(visited) - 1):
            start = visited[i]
            end = visited[i + 1]
            
            arrow = Arrow(
                city_nodes[start].get_center(),
                city_nodes[end].get_center(),
                color=YELLOW,
                stroke_width=6,
                buff=0.4,
                max_tip_length_to_length_ratio=0.15
            )
            
            self.play(Create(arrow), run_time=0.8)
        
        # Show total distance
        total_text = Text(f"Total Distance: {total_distance}", font_size=26, color=GREEN)
        total_text.next_to(solution_text, UP, buff=0.3)
        self.play(Write(total_text))
        
        self.wait(2)