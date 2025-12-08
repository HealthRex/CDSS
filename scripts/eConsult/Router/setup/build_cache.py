import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))


import json
import os
import hashlib
from datetime import datetime
from utils.config import Config

class TemplateCache:
    def __init__(self):
        self.cfg = Config()
        self.templates = {}
        self.specialty_conditions = {}
        self.cache_metadata = {}
        
    def load_and_merge_templates(self):
        """Load all templates from the templates directory"""
        print("📚 Loading templates...")
        all_templates = []
        
        for file in os.listdir(self.cfg.templates_dir):
            if file.endswith(".json"):
                file_path = Path(self.cfg.templates_dir) / file
                with open(file_path, "r") as f:
                    try:
                        data = json.load(f)
                        
                        # Handle files that contain a list instead of a dict
                        if isinstance(data, list) and len(data) > 0:
                            data = data[0]
                        
                        if isinstance(data, dict):
                            # Add filename reference
                            data['_source_file'] = file
                            all_templates.append(data)
                            
                            # Build specialty mapping
                            specialty = data.get("specialty", "")
                            condition = data.get("template_name", file.replace(".json", ""))
                            if specialty not in self.specialty_conditions:
                                self.specialty_conditions[specialty] = []
                            self.specialty_conditions[specialty].append(condition)
                            
                    except Exception as e:
                        print(f"⚠️ Error loading {file}: {e}")
        
        print(f"✅ Loaded {len(all_templates)} templates")
        return all_templates
    
    def save_merged_templates(self, templates):
        """Save merged templates to a single file"""
        output_path = self.cfg.data_dir / "templates_combined.json"
        
        with open(output_path, "w") as f:
            json.dump(templates, f, indent=2)
        
        print(f"💾 Saved merged templates to {output_path}")
        return output_path
    
    def create_cache_structure(self, templates):
        """Create the cache structure for API calls"""
        # Build templates text (limiting to 178 as in the original code)
        templates_text_list = []
        
        for template in templates[:178]:
            text = f"""
Specialty: {template.get("specialty", "")}
Condition: {template.get("template_name", "")}
Required Info: {template.get('required', '')}
Diagnostics: {template.get('diagnostics', '')}
Clinical Pearls: {template.get('clinical_pearls', '')}
"""
            templates_text_list.append(text)
        
        templates_text = "\n\n".join(templates_text_list)
        
        # Create specialty-condition mapping text
        specialty_mapping_text = ""
        for specialty, conditions in self.specialty_conditions.items():
            specialty_mapping_text += f"\n{specialty}: {', '.join(conditions[:10])}..."
        
        # Generate content hash for version tracking
        content_hash = hashlib.md5(templates_text.encode()).hexdigest()[:8]
        
        # Create cache metadata
        self.cache_metadata = {
            "content_hash": content_hash,
            "template_count": len(templates),
            "cached_template_count": min(178, len(templates)),
            "specialty_count": len(self.specialty_conditions),
            "created_at": datetime.now().isoformat(),
            "api_endpoint": self.cfg.securegpt_url,
            "model": self.cfg.llm_model
        }
        
        return templates_text, specialty_mapping_text, self.cache_metadata
    
    def save_cache_files(self, templates_text, specialty_mapping_text):
        """Save cache files for reference"""
        # Save the cacheable content
        cache_content_path = self.cfg.results_dir / "cache_content.txt"
        with open(cache_content_path, "w") as f:
            f.write("=== TEMPLATES ===\n")
            f.write(templates_text)
            f.write("\n\n=== SPECIALTY MAPPINGS ===\n")
            f.write(specialty_mapping_text)
        
        # Save metadata
        metadata_path = self.cfg.results_dir / "cache_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(self.cache_metadata, f, indent=2)
        
        # Save specialty-condition mapping
        mapping_path = self.cfg.results_dir / "specialty_condition_mapping.json"
        with open(mapping_path, "w") as f:
            json.dump(self.specialty_conditions, f, indent=2)
        
        print(f"📁 Saved cache content to {cache_content_path}")
        print(f"📁 Saved metadata to {metadata_path}")
        print(f"📁 Saved specialty mapping to {mapping_path}")

def main():
    # Initialize cache manager
    cache = TemplateCache()
    
    # Load and merge templates
    templates = cache.load_and_merge_templates()
    
    if not templates:
        print("⚠️ No templates found!")
        return
    
    # Save merged templates
    cache.save_merged_templates(templates)
    
    # Create cache structure
    templates_text, specialty_mapping, metadata = cache.create_cache_structure(templates)
    
    # Save cache files
    cache.save_cache_files(templates_text, specialty_mapping)
    
    # Print summary
    print(f"\n📊 Cache Summary:")
    print(f"  - Content hash: {metadata['content_hash']}")
    print(f"  - Total templates: {metadata['template_count']}")
    print(f"  - Cached templates: {metadata['cached_template_count']}")
    print(f"  - Specialties: {metadata['specialty_count']}")
    print(f"  - Model: {metadata['model']}")
    
    print("\n✅ Cache preparation complete!")
    print("\n💡 Next steps:")
    print("  1. Use the merged templates file for batch processing")
    print("  2. Reference the cache_metadata.json for version tracking")
    print("  3. Use specialty_condition_mapping.json for routing logic")

if __name__ == "__main__":
    main()
