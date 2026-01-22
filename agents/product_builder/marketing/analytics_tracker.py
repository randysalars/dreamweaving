"""
Analytics Tracker
Track product performance and user engagement metrics.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    # Product events
    PRODUCT_CREATED = "product_created"
    PRODUCT_PUBLISHED = "product_published"
    PRODUCT_VIEWED = "product_viewed"
    
    # Sales events
    SALE_STARTED = "sale_started"
    SALE_COMPLETED = "sale_completed"
    SALE_ABANDONED = "sale_abandoned"
    REFUND_REQUESTED = "refund_requested"
    
    # Engagement events
    CHAPTER_STARTED = "chapter_started"
    CHAPTER_COMPLETED = "chapter_completed"
    VIDEO_PLAYED = "video_played"
    AUDIO_PLAYED = "audio_played"
    PDF_DOWNLOADED = "pdf_downloaded"
    
    # Marketing events
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    LANDING_PAGE_VIEWED = "landing_page_viewed"


@dataclass
class AnalyticsEvent:
    """Single analytics event."""
    event_type: EventType
    product_id: str
    timestamp: str = ""
    user_id: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class ProductMetrics:
    """Aggregated metrics for a product."""
    product_id: str
    product_title: str
    
    # Revenue
    total_sales: int = 0
    total_revenue: float = 0.0
    refunds: int = 0
    net_revenue: float = 0.0
    
    # Engagement
    total_views: int = 0
    unique_buyers: int = 0
    completion_rate: float = 0.0
    avg_progress: float = 0.0
    
    # Marketing
    email_open_rate: float = 0.0
    landing_page_conversion: float = 0.0
    
    # Time metrics
    first_sale_date: str = ""
    last_sale_date: str = ""


class AnalyticsTracker:
    """
    Tracks product performance and engagement.
    
    Provides:
    - Event logging
    - Metric aggregation
    - Performance dashboards
    - Export capabilities
    """
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("./analytics_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "events.jsonl"
    
    def track(self, event: AnalyticsEvent):
        """Track a single event."""
        event_data = {
            "event_type": event.event_type.value,
            "product_id": event.product_id,
            "timestamp": event.timestamp,
            "user_id": event.user_id,
            "metadata": event.metadata
        }
        
        # Append to events file
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(event_data) + "\n")
        
        logger.debug(f"Tracked: {event.event_type.value} for {event.product_id}")
    
    def track_product_created(self, product_id: str, product_title: str, metadata: Dict = None):
        """Track product creation."""
        self.track(AnalyticsEvent(
            event_type=EventType.PRODUCT_CREATED,
            product_id=product_id,
            metadata={"title": product_title, **(metadata or {})}
        ))
    
    def track_sale(self, product_id: str, user_id: str, amount: float, currency: str = "USD"):
        """Track a sale."""
        self.track(AnalyticsEvent(
            event_type=EventType.SALE_COMPLETED,
            product_id=product_id,
            user_id=user_id,
            metadata={"amount": amount, "currency": currency}
        ))
    
    def track_engagement(self, product_id: str, user_id: str, event_type: EventType, chapter_id: str = ""):
        """Track content engagement."""
        self.track(AnalyticsEvent(
            event_type=event_type,
            product_id=product_id,
            user_id=user_id,
            metadata={"chapter_id": chapter_id}
        ))
    
    def get_events(self, product_id: str = None, event_type: EventType = None) -> List[Dict]:
        """Get filtered events."""
        events = []
        
        if not self.events_file.exists():
            return events
        
        with open(self.events_file, 'r') as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    
                    if product_id and event.get("product_id") != product_id:
                        continue
                    if event_type and event.get("event_type") != event_type.value:
                        continue
                    
                    events.append(event)
        
        return events
    
    def get_product_metrics(self, product_id: str, product_title: str = "") -> ProductMetrics:
        """Calculate aggregated metrics for a product."""
        events = self.get_events(product_id=product_id)
        
        metrics = ProductMetrics(
            product_id=product_id,
            product_title=product_title
        )
        
        sales = [e for e in events if e.get("event_type") == EventType.SALE_COMPLETED.value]
        views = [e for e in events if e.get("event_type") == EventType.PRODUCT_VIEWED.value]
        refunds = [e for e in events if e.get("event_type") == EventType.REFUND_REQUESTED.value]
        
        # Revenue metrics
        metrics.total_sales = len(sales)
        metrics.total_revenue = sum(s.get("metadata", {}).get("amount", 0) for s in sales)
        metrics.refunds = len(refunds)
        refund_amount = sum(r.get("metadata", {}).get("amount", 0) for r in refunds)
        metrics.net_revenue = metrics.total_revenue - refund_amount
        
        # Engagement metrics
        metrics.total_views = len(views)
        unique_buyers = set(s.get("user_id") for s in sales if s.get("user_id"))
        metrics.unique_buyers = len(unique_buyers)
        
        # Dates
        if sales:
            metrics.first_sale_date = min(s.get("timestamp", "") for s in sales)
            metrics.last_sale_date = max(s.get("timestamp", "") for s in sales)
        
        return metrics
    
    def generate_dashboard(self, product_id: str, product_title: str) -> str:
        """Generate a markdown dashboard for a product."""
        metrics = self.get_product_metrics(product_id, product_title)
        
        dashboard = f"""# Analytics Dashboard: {product_title}

## 💰 Revenue

| Metric | Value |
|--------|-------|
| Total Sales | {metrics.total_sales} |
| Total Revenue | ${metrics.total_revenue:,.2f} |
| Refunds | {metrics.refunds} |
| Net Revenue | ${metrics.net_revenue:,.2f} |

## 📊 Engagement

| Metric | Value |
|--------|-------|
| Total Views | {metrics.total_views} |
| Unique Buyers | {metrics.unique_buyers} |
| Completion Rate | {metrics.completion_rate:.1%} |
| Avg Progress | {metrics.avg_progress:.1%} |

## 📅 Timeline

- **First Sale:** {metrics.first_sale_date or 'N/A'}
- **Last Sale:** {metrics.last_sale_date or 'N/A'}

## 📈 Conversion Funnel

```
Views → Sales Conversion: {(metrics.total_sales / metrics.total_views * 100) if metrics.total_views > 0 else 0:.1f}%
```

---
*Generated: {datetime.utcnow().isoformat()}*
"""
        
        return dashboard
    
    def export_dashboard(self, product_id: str, product_title: str, output_path: Path) -> str:
        """Export dashboard to file."""
        dashboard = self.generate_dashboard(product_id, product_title)
        output_path.write_text(dashboard)
        logger.info(f"✅ Dashboard exported: {output_path}")
        return str(output_path)
    
    def export_csv(self, product_id: str = None, output_path: Path = None) -> str:
        """Export events to CSV."""
        import csv
        
        events = self.get_events(product_id=product_id)
        output_path = output_path or self.data_dir / "events_export.csv"
        
        if not events:
            logger.warning("No events to export")
            return ""
        
        fieldnames = ["timestamp", "event_type", "product_id", "user_id"]
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                writer.writerow({
                    "timestamp": event.get("timestamp", ""),
                    "event_type": event.get("event_type", ""),
                    "product_id": event.get("product_id", ""),
                    "user_id": event.get("user_id", "")
                })
        
        logger.info(f"✅ CSV exported: {output_path}")
        return str(output_path)
