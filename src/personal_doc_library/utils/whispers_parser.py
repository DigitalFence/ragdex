"""Parse Whispers message date headers and extract metadata"""

import re
from datetime import datetime
from typing import Dict, Optional


class WhispersParser:
    """Parse Whispers message date headers and extract metadata"""

    # Date header patterns (handle variations)
    DATE_PATTERNS = [
        # Standard: "Friday, June 28, 2002 – 8:00 a.m."
        r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(\w+)\s+(\d{1,2}),\s+(\d{4})\s+[–-]\s+(\d{1,2}):(\d{2})\s+([ap])\.m\.',
        # Multi-day: "Tuesday & Wednesday, October 4 & 5, 2005 – 10:00 a.m."
        r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*&\s*(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(\w+)\s+\d{1,2}\s*&\s*(\d{1,2}),\s+(\d{4})\s+[–-]\s+(\d{1,2}):(\d{2})\s+([ap])\.m\.',
    ]

    # Map month names to numbers
    MONTH_MAP = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    # Known weekdays for validation
    WEEKDAYS = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}

    @classmethod
    def parse_date_header(cls, text: str) -> Optional[Dict[str, str]]:
        """Parse date header from Whispers message

        Returns:
            Dict with keys: date (ISO), time (HH:MM), day_of_week, raw_header, year, month
            or None if no match
        """
        for pattern in cls.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()

                # Extract components based on pattern
                if groups[0] in cls.WEEKDAYS:
                    # Standard pattern
                    day_of_week = groups[0]
                    month_name = groups[1]
                    day = int(groups[2])
                    year = int(groups[3])
                    hour = int(groups[4])
                    minute = int(groups[5])
                    am_pm = groups[6]
                else:
                    # Multi-day pattern (no day_of_week in first group)
                    day_of_week = None
                    month_name = groups[0]
                    day = int(groups[1])
                    year = int(groups[2])
                    hour = int(groups[3])
                    minute = int(groups[4])
                    am_pm = groups[5]

                # Convert to 24-hour format
                if am_pm == 'p' and hour != 12:
                    hour += 12
                elif am_pm == 'a' and hour == 12:
                    hour = 0

                # Format date
                month = cls.MONTH_MAP.get(month_name)
                if month:
                    date_iso = f"{year:04d}-{month:02d}-{day:02d}"
                    time_24h = f"{hour:02d}:{minute:02d}"

                    return {
                        'date': date_iso,
                        'time': time_24h,
                        'day_of_week': day_of_week,
                        'raw_header': match.group(0),
                        'year': year,
                        'month': month
                    }

        return None

    @classmethod
    def extract_author(cls, text: str, date_info: Dict) -> Optional[str]:
        """Extract author from message (usually follows date header)

        Common patterns:
        - "Friday, June 28, 2002 – 8:00 a.m.\nBabuji:"
        - Text after date header often starts with author name
        """
        # Look for text after date header
        raw_header = date_info.get('raw_header')
        if raw_header and raw_header in text:
            # Get text after date header
            after_date = text.split(raw_header, 1)[1]

            # Common author indicators
            # Check for known authors in first 200 chars
            known_authors = ['Babuji', 'Lalaji', 'Chariji']
            for author in known_authors:
                if author in after_date[:200]:
                    return author

            # Look for "Master" reference
            if 'Master' in after_date[:200]:
                # Could be Babuji (most common)
                return 'Babuji'

        return None

    @classmethod
    def detect_source_type(cls, filename: str) -> str:
        """Detect source type from filename"""
        filename_lower = filename.lower()

        if 'whispers' in filename_lower and 'volume' in filename_lower:
            return 'whispers'
        elif any(x in filename_lower for x in ['hfn', 'cnbs', 'collector', 'heartfulness']):
            return 'heartfulness'
        elif 'osho' in filename_lower:
            return 'osho'
        elif any(x in filename_lower for x in ['yoga', 'sutras', 'patanjali']):
            return 'yoga_sutras'
        else:
            return 'general'

    @classmethod
    def extract_volume(cls, filename: str) -> Optional[int]:
        """Extract volume number from Whispers filename"""
        match = re.search(r'volume[_\s-]*(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
