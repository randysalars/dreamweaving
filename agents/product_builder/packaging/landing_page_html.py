"""
Landing Page HTML Generator.

Transforms landing page JSON content into a beautiful, responsive HTML page
with modern styling (glassmorphism, gradients, professional typography).
"""

import logging
from pathlib import Path
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)


class LandingPageHTMLGenerator:
    """Generates styled HTML landing pages from JSON content."""
    
    def __init__(self):
        self.css = self._get_premium_css()
    
    def generate(self, content: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate HTML landing page from content dictionary.
        
        Args:
            content: Landing page content (from LandingPageAgent)
            output_path: Where to save the HTML file
            
        Returns:
            Path to generated HTML file
        """
        logger.info("🎨 Generating Premium Landing Page HTML...")
        
        html = self._build_html(content)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)
        
        logger.info(f"✅ Landing page generated: {output_path}")
        return output_path
    
    def _build_html(self, content: Dict) -> str:
        """Build complete HTML document."""
        hero = content.get('hero', {})
        pain = content.get('pain_agitation', {})
        solution = content.get('solution', {})
        proof = content.get('social_proof', {})
        bonuses = content.get('bonuses', [])
        risk = content.get('risk_reversal', {})
        urgency = content.get('urgency', {})
        faq = content.get('faq', [])
        about = content.get('about', {})
        footer = content.get('footer_cta', {})
        
        title = content.get('page_title', 'Premium Product')
        meta_desc = content.get('meta_description', '')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>{self.css}</style>
</head>
<body>
    {self._hero_section(hero)}
    {self._pain_section(pain)}
    {self._solution_section(solution)}
    {self._social_proof_section(proof)}
    {self._bonuses_section(bonuses)}
    {self._risk_reversal_section(risk)}
    {self._faq_section(faq)}
    {self._about_section(about)}
    {self._footer_cta_section(footer)}
    {self._urgency_bar(urgency)}
    {self._love_offering_popup(content)}
</body>
</html>'''
    
    def _hero_section(self, hero: Dict) -> str:
        if not hero:
            return ""
        return f'''
    <section class="hero">
        <div class="container">
            <p class="hook">{hero.get('hook', '')}</p>
            <h1 class="headline">{hero.get('headline', '')}</h1>
            <p class="subheadline">{hero.get('subheadline', '')}</p>
            <div class="cta-group">
                <a href="#pricing" class="btn btn-primary">{hero.get('cta_primary', 'Get Access')}</a>
                {f'<a href="#features" class="btn btn-secondary">{hero.get("cta_secondary")}</a>' if hero.get('cta_secondary') else ''}
            </div>
        </div>
    </section>'''
    
    def _pain_section(self, pain: Dict) -> str:
        if not pain:
            return ""
        pain_points_html = "\n".join([f'<li>{p}</li>' for p in pain.get('pain_points', [])])
        return f'''
    <section class="pain">
        <div class="container">
            <p class="opener">{pain.get('opener', '')}</p>
            <ul class="pain-points">{pain_points_html}</ul>
            <p class="agitation">{pain.get('agitation', '')}</p>
            <p class="bridge">{pain.get('bridge', '')}</p>
        </div>
    </section>'''
    
    def _solution_section(self, solution: Dict) -> str:
        if not solution:
            return ""
        features_html = ""
        for f in solution.get('features', []):
            features_html += f'''
            <div class="feature-card">
                <span class="feature-icon">{f.get('icon', '✨')}</span>
                <h3>{f.get('title', '')}</h3>
                <p>{f.get('description', '')}</p>
            </div>'''
        return f'''
    <section id="features" class="solution">
        <div class="container">
            <p class="intro">{solution.get('intro', 'Introducing...')}</p>
            <h2 class="product-name">{solution.get('product_name', '')}</h2>
            <div class="features-grid">{features_html}</div>
            <p class="differentiator">{solution.get('differentiator', '')}</p>
        </div>
    </section>'''
    
    def _social_proof_section(self, proof: Dict) -> str:
        if not proof:
            return ""
        stats_html = ""
        for s in proof.get('stats', []):
            stats_html += f'''
            <div class="stat">
                <span class="stat-number">{s.get('number', '')}</span>
                <span class="stat-label">{s.get('label', '')}</span>
            </div>'''
        
        testimonials_html = ""
        for t in proof.get('testimonials', []):
            stars = "⭐" * t.get('rating', 5)
            testimonials_html += f'''
            <div class="testimonial-card">
                <div class="stars">{stars}</div>
                <blockquote>"{t.get('quote', '')}"</blockquote>
                <cite>— {t.get('author', '')} <span class="role">{t.get('role', '')}</span></cite>
            </div>'''
        
        return f'''
    <section class="social-proof">
        <div class="container">
            <h2>Trusted by Thousands</h2>
            <div class="stats-grid">{stats_html}</div>
            <div class="testimonials-grid">{testimonials_html}</div>
        </div>
    </section>'''
    
    def _bonuses_section(self, bonuses: list) -> str:
        if not bonuses:
            return ""
        bonuses_html = ""
        for b in bonuses:
            bonuses_html += f'''
            <div class="bonus-card">
                <span class="bonus-badge">FREE BONUS</span>
                <h3>{b.get('title', '')}</h3>
                <p>{b.get('description', '')}</p>
                <p class="bonus-value">Value: <span>${b.get('value', '0')}</span></p>
            </div>'''
        return f'''
    <section class="bonuses">
        <div class="container">
            <h2>🎁 But Wait, There's More...</h2>
            <p class="bonuses-intro">Order today and get these exclusive bonuses FREE:</p>
            <div class="bonuses-grid">{bonuses_html}</div>
        </div>
    </section>'''
    
    def _risk_reversal_section(self, risk: Dict) -> str:
        if not risk:
            return ""
        return f'''
    <section class="guarantee">
        <div class="container">
            <div class="guarantee-card">
                <span class="guarantee-badge">{risk.get('badge_text', '100% Risk-Free')}</span>
                <h2>{risk.get('guarantee_type', '30-Day Money-Back Guarantee')}</h2>
                <p>{risk.get('guarantee_copy', '')}</p>
            </div>
        </div>
    </section>'''
    
    def _faq_section(self, faq: list) -> str:
        if not faq:
            return ""
        faq_html = ""
        for item in faq:
            faq_html += f'''
            <div class="faq-item">
                <h3 class="faq-question">{item.get('question', '')}</h3>
                <p class="faq-answer">{item.get('answer', '')}</p>
            </div>'''
        return f'''
    <section class="faq">
        <div class="container">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-list">{faq_html}</div>
        </div>
    </section>'''
    
    def _about_section(self, about: Dict) -> str:
        if not about:
            return ""
        creds = "".join([f'<span class="credential">{c}</span>' for c in about.get('credentials', [])])
        return f'''
    <section class="about">
        <div class="container">
            <h2>Meet Your Guide</h2>
            <div class="about-content">
                <div class="about-text">
                    <h3>{about.get('name', '')}</h3>
                    <p>{about.get('bio', '')}</p>
                    <div class="credentials">{creds}</div>
                </div>
            </div>
        </div>
    </section>'''
    
    def _footer_cta_section(self, footer: Dict) -> str:
        if not footer:
            return ""
        return f'''
    <section id="pricing" class="footer-cta">
        <div class="container">
            <h2>{footer.get('headline', 'Ready to Get Started?')}</h2>
            {f'<p class="footer-sub">{footer.get("subheadline")}</p>' if footer.get('subheadline') else ''}
            <a href="#" class="btn btn-primary btn-large">{footer.get('cta_text', 'Get Instant Access')}</a>
        </div>
    </section>
    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2026 All rights reserved. | <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>
        </div>
    </footer>'''
    
    def _urgency_bar(self, urgency: Dict) -> str:
        if not urgency:
            return ""
        return f'''
    <div class="urgency-bar">
        <p>⚡ {urgency.get('message', '')}</p>
    </div>'''
    
    def _love_offering_popup(self, content: Dict) -> str:
        """
        Generate love offering popup - allows users to get product free or pay what they can.
        Randy's philosophy: everyone deserves access to education regardless of ability to pay.
        """
        price = content.get('price', content.get('footer_cta', {}).get('price', '47'))
        product_name = content.get('product_title', content.get('page_title', 'this product'))
        
        return f'''
    <!-- Love Offering Popup -->
    <div id="love-offering-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 9999; justify-content: center; align-items: center; backdrop-filter: blur(4px);">
        <div style="background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); padding: 48px; border-radius: 24px; max-width: 520px; margin: 20px; text-align: center; position: relative; box-shadow: 0 25px 80px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);">
            <button onclick="closeLoveOffering()" style="position: absolute; top: 16px; right: 16px; background: rgba(255,255,255,0.1); border: none; font-size: 20px; cursor: pointer; color: #94a3b8; width: 36px; height: 36px; border-radius: 50%; transition: all 0.2s;">×</button>
            
            <div style="font-size: 56px; margin-bottom: 24px;">💝</div>
            
            <h2 style="color: #f1f5f9; margin-bottom: 16px; font-size: 1.75rem; font-weight: 700;">Wait! You Can Have This Free</h2>
            
            <p style="color: #94a3b8; margin-bottom: 28px; line-height: 1.8; font-size: 1.05rem;">
                I believe everyone deserves access to this knowledge. If ${price} is a barrier right now, 
                <strong style="color: #22d3ee;">take it for free</strong>. Pay what feels right—or nothing at all.
            </p>
            
            <div style="display: flex; flex-direction: column; gap: 16px;">
                <a href="#" style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 18px 36px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 1.15rem; box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4); transition: all 0.2s;">
                    🎁 Get It Free (No Strings)
                </a>
                
                <p style="color: #64748b; font-size: 0.9rem; margin: 8px 0;">— or give a love offering —</p>
                
                <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
                    <a href="#" style="background: rgba(255,255,255,0.05); color: #f1f5f9; padding: 14px 24px; border-radius: 10px; text-decoration: none; font-weight: 600; border: 1px solid rgba(255,255,255,0.15); transition: all 0.2s;">
                        $5 Blessing
                    </a>
                    <a href="#" style="background: rgba(255,255,255,0.05); color: #f1f5f9; padding: 14px 24px; border-radius: 10px; text-decoration: none; font-weight: 600; border: 1px solid rgba(255,255,255,0.15); transition: all 0.2s;">
                        $15 Support
                    </a>
                    <a href="#" style="background: rgba(255,255,255,0.05); color: #f1f5f9; padding: 14px 24px; border-radius: 10px; text-decoration: none; font-weight: 600; border: 1px solid rgba(255,255,255,0.15); transition: all 0.2s;">
                        $27 Gratitude
                    </a>
                </div>
                
                <a href="#pricing" onclick="closeLoveOffering()" style="color: #64748b; font-size: 0.9rem; margin-top: 12px; text-decoration: none;">
                    No thanks, I'll pay full price →
                </a>
            </div>
            
            <p style="color: #475569; font-size: 0.8rem; margin-top: 24px;">
                Your love offering helps keep this work free for others. Thank you. 🙏
            </p>
        </div>
    </div>
    
    <script>
        // Love Offering Popup - triggers on exit intent or after delay
        let lovePopupShown = false;
        
        function showLoveOffering() {{
            if (!lovePopupShown) {{
                document.getElementById('love-offering-overlay').style.display = 'flex';
                lovePopupShown = true;
            }}
        }}
        
        function closeLoveOffering() {{
            document.getElementById('love-offering-overlay').style.display = 'none';
        }}
        
        // Exit intent detection (mouse leaves viewport at top)
        document.addEventListener('mouseout', function(e) {{
            if (e.clientY < 10 && !lovePopupShown) {{
                showLoveOffering();
            }}
        }});
        
        // Backup: show after 45 seconds if still on page
        setTimeout(function() {{
            showLoveOffering();
        }}, 45000);
        
        // Close on escape key
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeLoveOffering();
            }}
        }});
        
        // Close on overlay click (but not popup content)
        document.getElementById('love-offering-overlay').addEventListener('click', function(e) {{
            if (e.target === this) {{
                closeLoveOffering();
            }}
        }});
    </script>'''
    
    def _get_premium_css(self) -> str:
        """Premium CSS with glassmorphism and modern design."""
        return '''
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #ec4899;
    --background: #0f0f23;
    --surface: rgba(255, 255, 255, 0.05);
    --surface-hover: rgba(255, 255, 255, 0.1);
    --text: #e2e8f0;
    --text-muted: #94a3b8;
    --accent: #22d3ee;
    --gradient: linear-gradient(135deg, var(--primary), var(--secondary));
    --glass: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.15);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--background);
    color: var(--text);
    line-height: 1.7;
    overflow-x: hidden;
}

.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 24px;
}

section {
    padding: 100px 0;
}

h1, h2, h3 { font-weight: 700; line-height: 1.2; }
h1 { font-size: clamp(2.5rem, 5vw, 4rem); }
h2 { font-size: clamp(2rem, 4vw, 3rem); margin-bottom: 1.5rem; text-align: center; }
h3 { font-size: 1.25rem; margin-bottom: 0.5rem; }

/* Buttons */
.btn {
    display: inline-block;
    padding: 16px 32px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    text-decoration: none;
    transition: all 0.3s ease;
    cursor: pointer;
    border: none;
}
.btn-primary {
    background: var(--gradient);
    color: white;
    box-shadow: 0 4px 24px rgba(99, 102, 241, 0.4);
}
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.5);
}
.btn-secondary {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--glass-border);
}
.btn-large { padding: 20px 48px; font-size: 1.125rem; }

/* Hero */
.hero {
    min-height: 90vh;
    display: flex;
    align-items: center;
    text-align: center;
    background: radial-gradient(ellipse at top, rgba(99, 102, 241, 0.15), transparent 50%);
}
.hook {
    font-size: 1.25rem;
    color: var(--accent);
    margin-bottom: 1rem;
    font-weight: 500;
}
.headline {
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem;
}
.subheadline {
    font-size: 1.25rem;
    color: var(--text-muted);
    max-width: 600px;
    margin: 0 auto 2rem;
}
.cta-group {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
}

/* Pain Section */
.pain {
    background: rgba(239, 68, 68, 0.05);
    text-align: center;
}
.opener { font-size: 1.5rem; font-weight: 600; margin-bottom: 2rem; }
.pain-points {
    list-style: none;
    max-width: 600px;
    margin: 0 auto 2rem;
}
.pain-points li {
    padding: 1rem;
    margin-bottom: 1rem;
    background: var(--glass);
    border-radius: 12px;
    border-left: 4px solid #ef4444;
}
.agitation { font-size: 1.25rem; font-style: italic; color: var(--text-muted); margin-bottom: 1rem; }
.bridge { font-size: 1.5rem; font-weight: 600; color: var(--accent); }

/* Solution/Features */
.solution { text-align: center; }
.intro { font-size: 1.25rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.product-name { margin-bottom: 3rem; }
.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 3rem;
}
.feature-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 32px;
    text-align: left;
    transition: all 0.3s ease;
}
.feature-card:hover {
    background: var(--surface-hover);
    transform: translateY(-4px);
}
.feature-icon { font-size: 2.5rem; margin-bottom: 1rem; display: block; }
.differentiator {
    font-size: 1.125rem;
    font-style: italic;
    color: var(--accent);
    max-width: 700px;
    margin: 0 auto;
}

/* Social Proof */
.social-proof { background: var(--surface); }
.stats-grid {
    display: flex;
    justify-content: center;
    gap: 48px;
    flex-wrap: wrap;
    margin-bottom: 48px;
}
.stat { text-align: center; }
.stat-number { display: block; font-size: 3rem; font-weight: 800; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stat-label { color: var(--text-muted); }
.testimonials-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
}
.testimonial-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 32px;
}
.stars { color: #fbbf24; margin-bottom: 1rem; }
blockquote { font-size: 1.125rem; font-style: italic; margin-bottom: 1rem; }
cite { color: var(--text-muted); }
.role { opacity: 0.7; }

/* Bonuses */
.bonuses { text-align: center; }
.bonuses-intro { font-size: 1.25rem; color: var(--text-muted); margin-bottom: 2rem; }
.bonuses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
}
.bonus-card {
    background: linear-gradient(135deg, rgba(34, 211, 238, 0.1), rgba(99, 102, 241, 0.1));
    border: 1px solid var(--accent);
    border-radius: 16px;
    padding: 32px;
    position: relative;
}
.bonus-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--accent);
    color: var(--background);
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
}
.bonus-value { margin-top: 1rem; font-weight: 600; }
.bonus-value span { color: var(--accent); font-size: 1.5rem; text-decoration: line-through; opacity: 0.7; }

/* Guarantee */
.guarantee { text-align: center; }
.guarantee-card {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05));
    border: 2px solid #22c55e;
    border-radius: 24px;
    padding: 48px;
    max-width: 700px;
    margin: 0 auto;
}
.guarantee-badge {
    display: inline-block;
    background: #22c55e;
    color: white;
    padding: 8px 24px;
    border-radius: 20px;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* FAQ */
.faq-list { max-width: 700px; margin: 0 auto; }
.faq-item {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}
.faq-question { color: var(--accent); }
.faq-answer { color: var(--text-muted); margin-top: 0.5rem; }

/* About */
.about { text-align: center; }
.about-text { max-width: 600px; margin: 0 auto; }
.credentials { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 1rem; }
.credential {
    background: var(--surface);
    border: 1px solid var(--glass-border);
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.875rem;
}

/* Footer CTA */
.footer-cta {
    text-align: center;
    background: radial-gradient(ellipse at bottom, rgba(99, 102, 241, 0.2), transparent 70%);
    padding: 120px 0;
}
.footer-sub { font-size: 1.25rem; color: var(--text-muted); margin-bottom: 2rem; }
.site-footer {
    text-align: center;
    padding: 24px;
    border-top: 1px solid var(--glass-border);
}
.site-footer a { color: var(--text-muted); }

/* Urgency Bar */
.urgency-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--gradient);
    color: white;
    text-align: center;
    padding: 12px;
    font-weight: 600;
    z-index: 1000;
}

/* Responsive */
@media (max-width: 768px) {
    section { padding: 60px 0; }
    .stats-grid { gap: 24px; }
    .stat-number { font-size: 2rem; }
}
'''
