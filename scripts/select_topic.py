#!/usr/bin/env python3
import json
import random
import sys
from datetime import datetime
from pathlib import Path

def select_next_topic(topics_file='config/topics.json'):
    """Select an available topic with weighted randomness."""
    
    topics_path = Path(topics_file)
    
    if not topics_path.exists():
        print(f"❌ Error: {topics_file} not found")
        sys.exit(1)
    
    with open(topics_path, 'r') as f:
        data = json.load(f)
    
    # Filter available topics
    available = [t for t in data['topics'] if t['status'] == 'available']
    
    if not available:
        print("❌ No available topics. Add more to topics.json")
        sys.exit(1)
    
    print(f"📚 Found {len(available)} available topics")
    
    # Get recently used categories to avoid repetition
    used_topics = sorted(
        [t for t in data['topics'] if t.get('status') == 'used'],
        key=lambda x: x.get('used_at', ''),
        reverse=True
    )[:3]
    
    used_categories = [t['category'] for t in used_topics]
    
    # Weight selection: prefer advanced, avoid recently used categories
    weights = []
    for t in available:
        weight = 1.0
        
        # Prefer advanced topics
        if t['difficulty'] == 'advanced':
            weight *= 1.5
        
        # Penalize recently used categories
        if t['category'] in used_categories:
            weight *= 0.5
        
        weights.append(weight)
    
    # Select topic
    topic = random.choices(available, weights=weights, k=1)[0]
    
    print(f"\n✅ Selected: {topic['title']}")
    print(f"   Category: {topic['category']}")
    print(f"   Difficulty: {topic['difficulty']}")
    
    # Mark as in_progress
    topic['status'] = 'in_progress'
    topic['selected_at'] = datetime.now().isoformat()
    
    # Update topics.json
    data['last_updated'] = datetime.now().isoformat()
    
    with open(topics_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Save selected topic for next script
    with open('.selected_topic.json', 'w') as f:
        json.dump(topic, f, indent=2)
    
    return topic

if __name__ == "__main__":
    topic = select_next_topic()
    print(f"\n💾 Topic saved to .selected_topic.json")