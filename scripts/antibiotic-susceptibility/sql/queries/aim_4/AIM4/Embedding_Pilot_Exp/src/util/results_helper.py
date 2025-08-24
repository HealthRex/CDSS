import os
import json


def save_results(results, output_path):
    with open(output_path, 'w') as f:
        for res in results:
            f.write(json.dumps(res) + '\n')

def load_results(output_path):
    if not os.path.exists(output_path):
        return [], set()
    results = []
    processed_indices = set()
    with open(output_path, 'r') as f:
        for line in f:
            if line.strip():
                res = json.loads(line)
                results.append(res)
                # Support both list-of-dict and dict style outputs
                if isinstance(res, list):
                    for d in res:
                        if 'index' in d and 'error' not in d:
                            processed_indices.add(d['index'])
                elif isinstance(res, dict) and 'index' in res:
                    processed_indices.add(res['index'])
    return results, processed_indices
