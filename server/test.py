from manim import *
import numpy as np

class LinearProgrammingViz(Scene):
    def construct(self):
        # Title
        title = Text("Linear Programming Visualization", font_size=40)
        subtitle = Text("Maximizing an Objective Function", font_size=24)
        subtitle.next_to(title, DOWN)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Create axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=7,
            y_length=7,
            axis_config={"include_tip": True, "include_numbers": True},
        ).add_coordinates()
        
        axes_labels = axes.get_axis_labels(x_label="x_1", y_label="x_2")
        
        self.play(Create(axes), Write(axes_labels))
        self.wait(1)
        
        # Define LP problem:
        # Maximize: z = 3x₁ + 2x₂
        # Subject to:
        # 2x₁ + x₂ ≤ 8  (Constraint 1)
        # x₁ + 2x₂ ≤ 10 (Constraint 2)
        # x₁ ≥ 0, x₂ ≥ 0

        problem = VGroup(
            MathTex(r"\text{Maximize: } z = 3x_1 + 2x_2"),
            MathTex(r"\text{Subject to:}"),
            MathTex(r"2x_1 + x_2 \leq 8"),
            MathTex(r"x_1 + 2x_2 \leq 10"),
            MathTex(r"x_1, x_2 \geq 0")
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        problem.scale(0.6)
        problem.to_edge(UP + RIGHT)
        
        self.play(Write(problem))
        self.wait(2)
        
        # Constraint 1: 2x₁ + x₂ ≤ 8 => x₂ ≤ 8 - 2x₁
        constraint1_line = axes.plot(
            lambda x: 8 - 2*x,
            x_range=[0, 4],
            color=BLUE
        )
        constraint1_label = MathTex(r"2x_1 + x_2 = 8", color=BLUE).scale(0.6)
        constraint1_label.next_to(axes.c2p(2, 4), UR, buff=0.2)
        
        self.play(Create(constraint1_line), Write(constraint1_label))
        self.wait(1)
        
        # Constraint 2: x₁ + 2x₂ ≤ 10 => x₂ ≤ 5 - 0.5x₁
        constraint2_line = axes.plot(
            lambda x: 5 - 0.5*x,
            x_range=[0, 10],
            color=GREEN
        )
        constraint2_label = MathTex(r"x_1 + 2x_2 = 10", color=GREEN).scale(0.6)
        constraint2_label.next_to(axes.c2p(4, 3), UL, buff=0.2)
        
        self.play(Create(constraint2_line), Write(constraint2_label))
        self.wait(1)
        
        # Create feasible region
        # Find intersection points
        # Origin: (0, 0)
        # x₂-intercept of C1: (0, 8)
        # x₁-intercept of C1: (4, 0)
        # Intersection of C1 and C2: 2x₁ + x₂ = 8 and x₁ + 2x₂ = 10
        # Solving: x₁ = 2, x₂ = 4
        # x₂-intercept of C2: (0, 5)
        
        vertices = [
            axes.c2p(0, 0),
            axes.c2p(4, 0),
            axes.c2p(2, 4),
            axes.c2p(0, 5)
        ]
        
        feasible_region = Polygon(
            *vertices,
            fill_opacity=0.3,
            fill_color=YELLOW,
            stroke_width=0
        )
        
        region_label = Text("Feasible Region", color=YELLOW, font_size=24)
        region_label.move_to(axes.c2p(1.5, 2.5))
        
        self.play(FadeIn(feasible_region))
        self.play(Write(region_label))
        self.wait(2)
        
        # Mark corner points
        corner_points = [
            (0, 0, "O(0,0)"),
            (4, 0, "A(4,0)"),
            (2, 4, "B(2,4)"),
            (0, 5, "C(0,5)")
        ]
        
        dots = VGroup()
        labels = VGroup()
        
        for x, y, label_text in corner_points:
            dot = Dot(axes.c2p(x, y), color=RED, radius=0.08)
            label = Text(label_text, font_size=20, color=RED)
            label.next_to(axes.c2p(x, y), DR, buff=0.1)
            dots.add(dot)
            labels.add(label)
        
        self.play(LaggedStart(*[Create(dot) for dot in dots], lag_ratio=0.3))
        self.play(LaggedStart(*[Write(label) for label in labels], lag_ratio=0.3))
        self.wait(1)
        
        # Animate objective function
        obj_text = Text("Objective Function: z = 3x₁ + 2x₂", 
        font_size=28, color=ORANGE).to_edge(DOWN)
        self.play(Write(obj_text))
        self.wait(1)
        
        # Show objective function lines for different z values
        # 3x₁ + 2x₂ = z => x₂ = z/2 - 1.5x₁
        
        z_values = [0, 6, 12, 14]
        obj_lines = []
        
        for z in z_values:
            if z == 0:
                continue
            line = axes.plot(
                lambda x, z_val=z: z_val/2 - 1.5*x,
                x_range=[0, min(10, z/1.5)],  # Fixed: use z instead of z_val
                color=ORANGE,
                stroke_width=3
            )
            obj_lines.append(line)
        
        # Animate objective function sliding
        current_z = ValueTracker(0)
        
        obj_line = always_redraw(
            lambda: axes.plot(
                lambda x: current_z.get_value()/2 - 1.5*x,
                x_range=[0, min(10, max(0.1, current_z.get_value()/1.5))],
                color=ORANGE,
                stroke_width=4
            )
        )
        
        z_label = always_redraw(
            lambda: MathTex(f"z = {current_z.get_value():.1f}", color=ORANGE)
            .scale(0.7)
            .next_to(axes.c2p(0.5, current_z.get_value()/2 - 0.75), UP, buff=0.1)
        )
        
        self.add(obj_line, z_label)
        self.play(current_z.animate.set_value(14), run_time=4, rate_func=smooth)
        self.wait(1)
        
        # Highlight optimal solution
        optimal_dot = Dot(axes.c2p(2, 4), color=YELLOW, radius=0.15)
        optimal_label = Text("Optimal: B(2,4)\nz = 14", 
        font_size=24, color=YELLOW)
        optimal_label.next_to(axes.c2p(2, 4), UR, buff=0.3)
        
        self.play(
            Create(optimal_dot),
            Write(optimal_label),
            Flash(axes.c2p(2, 4), color=YELLOW, flash_radius=0.5)
        )
        self.wait(2)
        
        # Calculate z values for all vertices
        z_values_calc = VGroup(
            Text("z at O(0,0) = 0", font_size=20),
            Text("z at A(4,0) = 12", font_size=20),
            Text("z at B(2,4) = 14 ✓", font_size=20, color=YELLOW),
            Text("z at C(0,5) = 10", font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        z_values_calc.to_edge(LEFT + DOWN)
        
        self.play(Write(z_values_calc))
        self.wait(3)
        
        # Final message
        conclusion = Text("The optimal solution is at vertex B(2,4)\nwith maximum value z = 14",
        font_size=28, color=YELLOW)
        conclusion.move_to(ORIGIN)
        
        self.play(
            FadeOut(VGroup(axes, axes_labels, constraint1_line, constraint1_label,
                constraint2_line, constraint2_label, feasible_region,
                region_label, dots, labels, obj_line, z_label,
                optimal_dot, optimal_label, obj_text, z_values_calc, problem))
        )
        self.play(Write(conclusion))
        self.wait(3)


class DynamicConstraints(Scene):
    """Shows how changing constraints affects the feasible region"""
    def construct(self):
        title = Text("Dynamic Constraint Changes", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP).scale(0.7))
        
        # Create axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": True},
        )
        axes_labels = axes.get_axis_labels(x_label="x_1", y_label="x_2")
        
        self.play(Create(axes), Write(axes_labels))
        
        # Animate changing constraint: 2x₁ + x₂ ≤ b
        b_tracker = ValueTracker(8)
        
        constraint_line = always_redraw(
            lambda: axes.plot(
                lambda x: b_tracker.get_value() - 2*x,
                x_range=[0, b_tracker.get_value()/2],
                color=BLUE,
                stroke_width=4
            )
        )
        
        # Fixed constraint: x₁ + 2x₂ ≤ 10
        constraint2_line = axes.plot(
            lambda x: 5 - 0.5*x,
            x_range=[0, 10],
            color=GREEN
        )
        
        b_label = always_redraw(
            lambda: MathTex(f"2x_1 + x_2 \\leq {b_tracker.get_value():.0f}", 
            color=BLUE)
            .scale(0.7)
            .to_corner(UR)
        )
        
        self.play(Create(constraint_line), Create(constraint2_line))
        self.add(b_label)
        self.wait(1)
        
        # Animate b changing from 8 to 12 to 6
        self.play(b_tracker.animate.set_value(12), run_time=2)
        self.wait(1)
        self.play(b_tracker.animate.set_value(6), run_time=2)
        self.wait(1)
        self.play(b_tracker.animate.set_value(8), run_time=2)
        self.wait(2)