#!/usr/bin/env python3
"""Fix category pages with correct JSX syntax"""

from pathlib import Path

categories = [
    ('definitions-foundations', 'Core Definitions & Foundations'),
    ('natural-vs-induced', 'Natural vs Induced Altered States'),
    ('entry-pathways', 'Entry Pathways & Triggers'),
    ('safety-and-risks', 'Safety, Risks & Stability')
]

base_path = Path('../salarsu/frontend/app/consciousness/altered-states')

for slug, name in categories:
    file_path = base_path / slug / 'page.tsx'
    if file_path.exists():
        content = file_path.read_text()
        # Fix the JSX comment issue - ensure there's content after comments
        content = content.replace(
            '          {/* Category Title */}\n          <div className="space-y-3">',
            '          {/* Category Title */}\n          <div className="space-y-3">'
        )
        content = content.replace(
            '          {/* Question List */}\n          <section className="space-y-4">',
            '          {/* Question List */}\n          <section className="space-y-4">'
        )
        content = content.replace(
            '          {/* Back to Hub */}\n          <section className="pt-6 border-t border-border">',
            '          {/* Back to Hub */}\n          <section className="pt-6 border-t border-border">'
        )
        file_path.write_text(content)
        print(f"✓ Fixed {slug}")

print("All category pages fixed")
