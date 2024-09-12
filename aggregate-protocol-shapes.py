import os
import sys
import rdflib


def find_shapes_files(root_folder):
    """Find all 'shapes.ttl' files in the direct subfolders of the given folder."""
    shapes_files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Only look in direct subfolders, skip deeper subdirectories
        if dirpath == root_folder:
            for dirname in dirnames:
                subfolder = os.path.join(dirpath, dirname)
                for filename in os.listdir(subfolder):
                    if filename == "shapes.ttl":
                        shapes_files.append(os.path.join(subfolder, filename))
            break  # Stop further os.walk recursion
    return shapes_files


def aggregate_rdf_triples(shapes_files):
    """Aggregate RDF triples from all shapes.ttl files into one RDF graph."""
    aggregated_graph = rdflib.Graph()

    for shapes_file in shapes_files:
        try:
            print(f"Parsing {shapes_file}...")
            aggregated_graph.parse(shapes_file, format="turtle")
        except Exception as e:
            print(f"Error parsing {shapes_file}: {e}")

    return aggregated_graph


def save_aggregated_graph(graph, output_file):
    """Save the aggregated RDF graph into a single shapes.ttl file."""
    with open(output_file, "w") as f:
        f.write(graph.serialize(format="turtle"))


def main():
    if len(sys.argv) != 2:
        print("Usage: python aggregate_shapes.py <target_folder>")
        sys.exit(1)

    root_folder = sys.argv[1]

    if not os.path.isdir(root_folder):
        print(f"Error: {root_folder} is not a valid directory.")
        sys.exit(1)

    shapes_files = find_shapes_files(root_folder)

    if not shapes_files:
        print("No shapes.ttl files found.")
        return

    aggregated_graph = aggregate_rdf_triples(shapes_files)

    output_file = os.path.join(root_folder, "shapes.ttl")
    save_aggregated_graph(aggregated_graph, output_file)

    print(f"Aggregated shapes.ttl saved to {output_file}")


if __name__ == "__main__":
    main()
