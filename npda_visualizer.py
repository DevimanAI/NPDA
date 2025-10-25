from automata.pda.npda import NPDA, PDAStack, PDAConfiguration
import sys
from collections import defaultdict

# Define your NPDA here
# Example (this will be replaced with actual NPDA definition from file):
# npda = NPDA(
#     states={'q0', 'q1', 'q2'},
#     input_symbols={'a', 'b', 'c'},
#     stack_symbols={'Z0', 'A', 'B'},
#     transitions={
#         ('q0', 'a', 'Z0'): {('q0', ('A', 'Z0'))},
#         ('q0', 'a', 'A'): {('q0', ('A', 'A'))},
#         ('q0', 'b', 'A'): {('q1', ('lambda',))},
#         ('q1', 'b', 'A'): {('q1', ('lambda',))},
#         ('q1', 'c', 'Z0'): {('q2', ('Z0',))}
#     },
#     initial_state='q0',
#     initial_stack_symbol='Z0',
#     final_states={'q2'},
#     acceptance_mode='final_state'
# )

# Function to read NPDA definition from a file
def read_npda_from_file(file_path):
    npda_def = {}
    transitions_list = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key == 'Transitions':
                    # This is the start of the transitions section
                    continue
                npda_def[key] = value
            else:
                # Assume lines without ':' are part of the transitions list
                transitions_list.append(line)

    # Parse states
    states = set(npda_def.get('states', '').split(',')) if npda_def.get('states') else set()

    # Parse input symbols
    input_symbols = set(npda_def.get('input_symbols', '').split(',')) if npda_def.get('input_symbols') else set()

    # Parse stack symbols
    stack_symbols = set(npda_def.get('stack_symbols', '').split(',')) if npda_def.get('stack_symbols') else set()

    # Parse initial state
    initial_state = npda_def.get('initial_state')

    # Parse initial stack symbol
    initial_stack_symbol = npda_def.get('initial_stack_symbol')

    # Parse final states
    final_states = set(npda_def.get('final_states', '').split(',')) if npda_def.get('final_states') else set()

    # Parse acceptance mode
    acceptance_mode = npda_def.get('acceptance_mode', 'final_state')
    if acceptance_mode not in ['empty_stack', 'final_state']:
        raise ValueError("Acceptance mode must be 'empty_stack' or 'final_state'")

    # Parse transitions
    transitions = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    for transition_str in transitions_list:
        parts = transition_str.split('->')
        if len(parts) != 2:
            raise ValueError(f"Invalid transition format: {transition_str}. Expected 'current_state,input_symbol,stack_top -> next_state,stack_push'")

        left_side = [p.strip() for p in parts[0].split(',')]
        right_side = [p.strip() for p in parts[1].split(',')]

        if len(left_side) != 3:
            raise ValueError(f"Invalid left side of transition: {parts[0]}. Expected 'current_state,input_symbol,stack_top'")
        current_state, input_symbol_raw, stack_top_raw = left_side

        if len(right_side) < 1:
            raise ValueError(f"Invalid right side of transition: {parts[1]}. Expected 'next_state,stack_push'")
        next_state = right_side[0]
        stack_push = tuple(s for s in right_side[1:] if s != 'lambda')

        # Convert 'lambda' to None for automata-lib compatibility
        input_symbol = None if input_symbol_raw == 'lambda' else input_symbol_raw
        stack_top = None if stack_top_raw == 'lambda' else stack_top_raw

        if input_symbol is None:
            input_symbols.add('') # Add empty string to input symbols if it's a lambda transition
            input_symbol = ''
        if stack_top is None:
            stack_top = '' # Use empty string for lambda stack_top if automata-lib expects it

        transitions[current_state][input_symbol][stack_top].add((next_state, stack_push))

    # Convert defaultdicts to regular dicts
    transitions = {state: {input_sym: {stack_sym: transitions[state][input_sym][stack_sym] for stack_sym in transitions[state][input_sym]} for input_sym in transitions[state]} for state in transitions}

    # Debug print statements
    print("Debug: States:", states)
    print("Debug: Input Symbols:", input_symbols)
    print("Debug: Stack Symbols:", stack_symbols)
    print("Debug: Transitions:", transitions)
    print("Debug: Initial State:", initial_state)
    print("Debug: Initial Stack Symbol:", initial_stack_symbol)
    print("Debug: Final States:", final_states)
    print("Debug: Acceptance Mode:", acceptance_mode)

    # Create NPDA object
    npda = NPDA(
        states=states,
        input_symbols=input_symbols,
        stack_symbols=stack_symbols,
        transitions=transitions,
        initial_state=initial_state,
        initial_stack_symbol=initial_stack_symbol,
        final_states=final_states,
        acceptance_mode=acceptance_mode
    )

    return npda

# Function to visualize NPDA execution
def visualize_npda_execution(npda, input_string, dot_file_name):
    """Generates a DOT file for visualizing the NPDA's execution as a tree, showing all possible paths."""
    # Store configurations as PDAConfiguration objects
    all_step_configs_raw = []  # List of frozensets of PDAConfiguration for each step
    # Store transitions as (from_cfg_hash, to_cfg_hash, label)
    all_transitions = set()

    print(f"\n--- Visualizing NPDA execution for input: '{input_string}' ---\n")
    try:
        # Get the initial configurations
        initial_config_sets_generator = npda.read_input_stepwise(input_string)
        
        # The first item from the generator is the initial configuration set
        current_config_set = next(initial_config_sets_generator, frozenset())
        if not current_config_set:
            print("No initial configurations found.")
            return

        all_step_configs_raw.append(current_config_set)

        # Collect all configurations for all steps first
        for next_config_set in initial_config_sets_generator:
            if not next_config_set:
                break
            all_step_configs_raw.append(next_config_set)

        # Now, iterate through steps to find explicit transitions
        for step_index in range(len(all_step_configs_raw) - 1):
            current_step_configs = all_step_configs_raw[step_index]
            next_step_configs = all_step_configs_raw[step_index + 1]

            for from_cfg in current_step_configs:
                # Determine the input symbol to be consumed
                input_symbol_to_consume = from_cfg.remaining_input[0] if from_cfg.remaining_input else ''
                stack_top_symbol = from_cfg.stack.top()

                # Check for transitions with the input symbol
                if from_cfg.state in npda.transitions and \
                   input_symbol_to_consume in npda.transitions[from_cfg.state] and \
                   stack_top_symbol in npda.transitions[from_cfg.state][input_symbol_to_consume]:

                    for to_state, stack_push_tuple in npda.transitions[from_cfg.state][input_symbol_to_consume][stack_top_symbol]:
                        # Simulate the stack operation
                        new_stack_list = list(from_cfg.stack.stack)
                        if stack_top_symbol is not None:
                            new_stack_list.pop() # Pop the top symbol
                        for s in reversed(stack_push_tuple):
                            if s != 'lambda': # Only push non-lambda symbols
                                new_stack_list.append(s)
                        new_stack = PDAStack(tuple(new_stack_list))
                        
                        # Create the hypothetical next configuration
                        hypothetical_next_cfg = PDAConfiguration(
                            to_state,
                            from_cfg.remaining_input[1:], # Consume one input symbol
                            new_stack
                        )

                        # Check if this hypothetical_next_cfg is actually in the next_step_configs
                        if hypothetical_next_cfg in next_step_configs:
                            label = f"{input_symbol_to_consume},{stack_top_symbol}/{''.join(stack_push_tuple) if stack_push_tuple else 'ε'}"
                            all_transitions.add((hash(from_cfg), hash(hypothetical_next_cfg), label))
                
                # Check for epsilon transitions (without consuming input)
                if from_cfg.state in npda.transitions and \
                   '' in npda.transitions[from_cfg.state] and \
                   stack_top_symbol in npda.transitions[from_cfg.state]['']:

                    for to_state, stack_push_tuple in npda.transitions[from_cfg.state][''][stack_top_symbol]:
                        # Simulate the stack operation
                        new_stack_list = list(from_cfg.stack.stack)
                        if stack_top_symbol is not None:
                            new_stack_list.pop() # Pop the top symbol
                        for s in reversed(stack_push_tuple):
                            if s != 'lambda': # Only push non-lambda symbols
                                new_stack_list.append(s)
                        new_stack = PDAStack(tuple(new_stack_list))
                        
                        # Create the hypothetical next configuration (remaining_input is unchanged)
                        hypothetical_next_cfg = PDAConfiguration(
                            to_state,
                            from_cfg.remaining_input,
                            new_stack
                        )

                        # Check if this hypothetical_next_cfg is actually in the next_step_configs
                        if hypothetical_next_cfg in next_step_configs:
                            label = f"ε,{stack_top_symbol}/{''.join(stack_push_tuple) if stack_push_tuple else 'ε'}"
                            all_transitions.add((hash(from_cfg), hash(hypothetical_next_cfg), label))

        if not all_step_configs_raw:
            print("No execution path to visualize.")
            return

        if npda.accepts_input(input_string):
            print(f"\nInput '{input_string}' is ACCEPTED by the NPDA.")
        else:
            print(f"\nInput '{input_string}' is REJECTED by the NPDA.")

    except Exception as e:
        print(f"\nError during NPDA execution: {e}")
        return # Exit if there's an error during execution tracing

    # Generate DOT file for visualization
    dot_content = ["digraph NPDA_Execution {", "    rankdir=LR;", "    node [shape=\"box\"];"]

    # Create nodes for all configurations
    node_map = {} # Map PDAConfiguration hash to unique node ID
    node_counter = 0

    for step_index, configs_at_step in enumerate(all_step_configs_raw):
        for cfg in configs_at_step:
            cfg_hash = hash(cfg)
            if cfg_hash not in node_map:
                node_id = f"node_{node_counter}"
                node_map[cfg_hash] = node_id
                node_counter += 1
                
                label = f"({cfg.state}, {''.join(cfg.stack.stack)}, {''.join(cfg.remaining_input)})"
                fillcolor = "lightgreen" if step_index == 0 else "lightblue"
                dot_content.append(f"    {node_id} [label=\"{label}\", style=\"filled\", fillcolor=\"{fillcolor}\"];")

    # Add edges
    for from_cfg_hash, to_cfg_hash, label in all_transitions:
        from_node_id = node_map.get(from_cfg_hash)
        to_node_id = node_map.get(to_cfg_hash)
        if from_node_id and to_node_id:
            dot_content.append(f"    {from_node_id} -> {to_node_id} [label=\"{label}\", color=\"red\", penwidth=\"2\"];")

    dot_content.append("}")

    # Write DOT file
    print(f"Attempting to write DOT file: {dot_file_name}")
    with open(dot_file_name, "w", encoding="utf-8") as f:
        f.write('\n'.join(dot_content))

    print("DOT file generated: npda_execution.dot")
    print("To render as PNG, run: dot -Tpng npda_execution.dot -o npda_execution.png")


def visualize_npda_definition(npda, dot_file_name):
    """Generates a DOT file for visualizing the NPDA's definition."""
    dot_content = ["digraph NPDA_Definition {", "    rankdir=LR;"]

    # Add start node
    dot_content.append("    __start0__ [label=\"\", shape=\"none\", width=\"0\", height=\"0\"];")
    dot_content.append(f"    __start0__ -> {npda.initial_state};")

    # Add states
    for state in npda.states:
        shape = "doublecircle" if state in npda.final_states else "circle"
        dot_content.append(f"    {state} [shape=\"{shape}\"];")

    # Add transitions
    for from_state, input_transitions in npda.transitions.items():
        for input_symbol, stack_transitions in input_transitions.items():
            for stack_top, to_configs in stack_transitions.items():
                for to_state, stack_push_tuple in to_configs:
                    input_sym_label = input_symbol if input_symbol != '' else 'ε'
                    stack_top_label = stack_top if stack_top != '' else 'ε'
                    stack_push_label = ''.join(stack_push_tuple) if stack_push_tuple else 'ε'
                    label = f"{input_sym_label},{stack_top_label}/{stack_push_label}"
                    dot_content.append(f"    {from_state} -> {to_state} [label=\"{label}\"];")

    dot_content.append("}")

    # Write DOT file
    print(f"Attempting to write DOT file: {dot_file_name}")
    with open(dot_file_name, "w", encoding="utf-8") as f:
        f.write('\n'.join(dot_content))

    print("DOT file generated: npda_definition_diagram.dot")
    print("To render as PNG, run: dot -Tpng npda_definition_diagram.dot -o npda_definition_diagram.png")


def render_dot_to_png(dot_file_path, png_file_path):
    try:
        import subprocess
        subprocess.run(['dot', '-Tpng', dot_file_path, '-o', png_file_path], check=True)
        print(f"Successfully converted '{dot_file_path}' to '{png_file_path}'")
    except FileNotFoundError:
        print("Error: 'dot' command not found. Please ensure Graphviz is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting DOT to PNG: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python npda_visualizer.py <npda_definition_file> <input_string>")
        sys.exit(1)

    npda_definition_file = sys.argv[1]
    input_string = sys.argv[2]

    try:
        npda = read_npda_from_file(npda_definition_file)
        print("Successfully loaded NPDA from", npda_definition_file)
    except Exception as e:
        print(f"Error loading or validating NPDA: {e}")
        sys.exit(1)

    dot_file_name_execution = "npda_execution.dot"
    png_file_name_execution = "npda_execution.png"
    dot_file_name_definition = "npda_definition_diagram.dot"
    png_file_name_definition = "npda_definition_diagram.png"

    visualize_npda_execution(npda, input_string, dot_file_name_execution)
    render_dot_to_png(dot_file_name_execution, png_file_name_execution)

    visualize_npda_definition(npda, dot_file_name_definition)
    render_dot_to_png(dot_file_name_definition, png_file_name_definition)