import json
from pathlib import Path
from datetime import datetime

def reset_topics(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"File {file_path} not found.")
        return

    with open(path, 'r') as f:
        data = json.load(f)

    for topic in data.get('topics', []):
        topic['status'] = 'available'
        # Remove usage keys
        for key in ['selected_at', 'used_at', 'draft_path', 'stats']:
            if key in topic:
                del topic[key]

    data['last_updated'] = datetime.now().isoformat()

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully reset {len(data['topics'])} topics in {file_path}")

if __name__ == "__main__":
    reset_topics('config/topics.json')
