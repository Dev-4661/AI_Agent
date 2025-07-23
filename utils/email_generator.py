import urllib.parse
from typing import Dict, List, Optional

def generate_insights_email(
    company_name: str,
    key_issues: List[str],
    recipient_email: Optional[str] = None,
    sender_name: str = "Your Name",
    sender_company: str = "Your Company",
    sender_contact: str = "Your Contact Number"
) -> str:
    """
    Generate a mailto link for sending company insights via email
    
    Args:
        company_name: Name of the analyzed company
        key_issues: List of identified problems/issues
        recipient_email: Optional recipient email address
        sender_name: Name of the person sending the email
        sender_company: Company of the sender
        sender_contact: Contact number of the sender
    
    Returns:
        Formatted mailto URL with encoded parameters
    """
    
    # Email subject
    subject = f"Strategic Insights & Solutions for {company_name}"
    
    # Email body
    body = f"""Dear Team,

I hope this email finds you well.

I recently conducted a comprehensive analysis of {company_name} using advanced AI-powered business intelligence tools. Based on this analysis, I've identified several key areas where strategic improvements could drive significant value for your organization.

KEY INSIGHTS IDENTIFIED:

"""
    
    # Add numbered issues
    for i, issue in enumerate(key_issues[:3], 1):  # Limit to top 3 issues
        body += f"{i}. {issue}\n\n"
    
    body += f"""PROPOSED SOLUTIONS:

Based on these findings, I would like to propose a strategic consultation to discuss:

• Customized solutions addressing the specific challenges identified
• Implementation roadmap with measurable outcomes
• Best practices from similar industry leaders
• Cost-effective approaches to drive immediate impact

NEXT STEPS:

I believe there's tremendous potential to enhance {company_name}'s operational efficiency and market position. I would welcome the opportunity to discuss these insights in detail and explore how we can collaborate to implement these improvements.

Would you be available for a brief 30-minute consultation call this week to discuss these findings and potential solutions?

Best regards,

{sender_name}
{sender_company}
Contact: {sender_contact}

---
This analysis was generated using AI-powered business intelligence tools for strategic assessment purposes.
"""
    
    # URL encode the parameters
    encoded_subject = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(body)
    
    # Build mailto URL
    mailto_url = f"mailto:{recipient_email or ''}?subject={encoded_subject}&body={encoded_body}"
    
    return mailto_url

def extract_email_from_analysis(analysis_text: str) -> Optional[str]:
    """
    Extract email addresses from the AI analysis text
    
    Args:
        analysis_text: The AI-generated analysis text
    
    Returns:
        First email address found, or None if no email found
    """
    import re
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, analysis_text)
    
    return emails[0] if emails else None

def extract_key_issues_from_analysis(analysis_text: str) -> List[str]:
    """
    Extract key issues/problems from AI analysis text using pattern matching
    
    Args:
        analysis_text: The AI-generated analysis text
    
    Returns:
        List of identified key issues
    """
    import re
    
    # Common patterns that indicate problems or opportunities
    issue_patterns = [
        r"(?:challenge|problem|issue|concern|weakness|gap|limitation|bottleneck|inefficiency)[\s:]+([^.\n]+)",
        r"(?:needs improvement|requires attention|could be enhanced|lacking in|missing)[\s:]+([^.\n]+)",
        r"(?:opportunity to|potential for|could benefit from|should consider)[\s:]+([^.\n]+)",
        r"(?:pain point|critical issue|major concern|significant challenge)[\s:]+([^.\n]+)"
    ]
    
    issues = []
    analysis_lower = analysis_text.lower()
    
    for pattern in issue_patterns:
        matches = re.findall(pattern, analysis_lower, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 10:  # Filter out very short matches
                issues.append(match.strip().capitalize())
    
    # If no specific issues found, look for bullet points or numbered lists
    if not issues:
        # Look for bullet points or numbered items that might indicate issues
        bullet_patterns = [
            r"[•\-\*]\s*([^.\n]+(?:challenge|problem|issue|improve|enhance|lack|need)[^.\n]*)",
            r"\d+\.\s*([^.\n]+(?:challenge|problem|issue|improve|enhance|lack|need)[^.\n]*)"
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, analysis_text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 15:
                    issues.append(match.strip())
    
    # Default issues if none found
    if not issues:
        issues = [
            "Limited digital presence and online visibility",
            "Potential for improved operational efficiency",
            "Opportunities for enhanced customer engagement and retention"
        ]
    
    return issues[:3]  # Return top 3 issues
