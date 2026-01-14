#!/usr/bin/env python3
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_selected_topic():
    """Load the topic selected by select_topic.py"""
    topic_file = Path('.selected_topic.json')
    
    if not topic_file.exists():
        print("❌ No selected topic found. Run select_topic.py first.")
        sys.exit(1)
    
    with open(topic_file, 'r') as f:
        return json.load(f)

def load_prompt_template():
    """Load and return the prompt template"""
    template_path = Path('config/prompt_template.txt')
    
    if not template_path.exists():
        print("❌ Prompt template not found")
        sys.exit(1)
    
    with open(template_path, 'r') as f:
        return f.read()

def generate_draft(topic):
    """Generate blog draft using Anthropic API"""
    
    # Initialize Anthropic client
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    # Load and format prompt
    template = load_prompt_template()
    prompt = template.format(
        title=topic['title'],
        category=topic['category'],
        keywords=', '.join(topic['keywords'])
    )
    
    print(f"\n🤖 Generating draft for: {topic['title']}")
    print(f"📊 Estimated tokens: ~8000")
    print(f"⏱️  This will take 30-60 seconds...\n")
    
    try:
        # Call Anthropic API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            temperature=0.7,  # Slightly creative but focused
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        draft_content = message.content[0].text
        
        # Calculate stats
        word_count = len(draft_content.split())
        char_count = len(draft_content)
        
        print(f"✅ Draft generated!")
        print(f"   Words: {word_count}")
        print(f"   Characters: {char_count:,}")
        print(f"   Tokens used: ~{message.usage.input_tokens + message.usage.output_tokens}")
        
        return draft_content, message.usage
        
    except Exception as e:
        print(f"❌ Error generating draft: {e}")
        sys.exit(1)

def save_draft(topic, content, usage):
    """Save draft and metadata to appropriate directory"""
    
    # Create draft directory
    date_str = datetime.now().strftime('%Y-%m-%d')
    draft_dir = Path(f"drafts/{date_str}-{topic['id']}")
    draft_dir.mkdir(parents=True, exist_ok=True)
    
    # Save draft content
    draft_file = draft_dir / 'draft.md'
    with open(draft_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n💾 Draft saved to: {draft_file}")
    
    # Create metadata
    metadata = {
        'topic_id': topic['id'],
        'title': topic['title'],
        'category': topic['category'],
        'difficulty': topic['difficulty'],
        'keywords': topic['keywords'],
        'generated_at': datetime.now().isoformat(),
        'word_count': len(content.split()),
        'char_count': len(content),
        'model_used': 'claude-3-5-sonnet-20241022',
        'tokens_input': usage.input_tokens,
        'tokens_output': usage.output_tokens,
        'status': 'draft'
    }
    
    metadata_file = draft_dir / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📋 Metadata saved to: {metadata_file}")
    
    return draft_dir

def update_topic_status(topic, draft_dir):
    """Mark topic as used in topics.json"""
    
    topics_path = Path('config/topics.json')
    
    with open(topics_path, 'r') as f:
        data = json.load(f)
    
    # Find and update topic
    for t in data['topics']:
        if t['id'] == topic['id']:
            t['status'] = 'used'
            t['used_at'] = datetime.now().isoformat()
            t['draft_path'] = str(draft_dir)
            break
    
    data['last_updated'] = datetime.now().isoformat()
    
    with open(topics_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Topic marked as 'used' in topics.json")

def main():
    print("=" * 60)
    print("  FLUTTER BLOG DRAFT GENERATOR")
    print("=" * 60)
    
    # Load selected topic
    topic = load_selected_topic()
    
    # Generate draft
    content, usage = generate_draft(topic)
    
    # Save draft and metadata
    draft_dir = save_draft(topic, content, usage)
    
    # Update topic status
    update_topic_status(topic, draft_dir)
    
    # Clean up temp file
    Path('.selected_topic.json').unlink()
    
    print("\n" + "=" * 60)
    print("  ✅ GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"1. Review draft at: {draft_dir}/draft.md")
    print(f"2. Edit and personalize the content")
    print(f"3. Test code examples")
    print(f"4. Publish to Medium when ready")
    print()

if __name__ == "__main__":
    main()